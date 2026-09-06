<?php
/**
 * Plugin Name: Gramiss SMS
 * Description: اتصال سبک و اختصاصی WooCommerce به قالب‌های خدماتی SMS.ir برای سفارش‌های Gramiss.
 * Version: 0.1.0
 * Author: Gramiss
 * Requires Plugins: woocommerce
 * Text Domain: gramiss-sms
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

add_action( 'before_woocommerce_init', static function () {
    if ( class_exists( '\\Automattic\\WooCommerce\\Utilities\\FeaturesUtil' ) ) {
        \Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility( 'custom_order_tables', __FILE__, true );
    }
} );

final class Gramiss_SMS_V1 {
    private const OPTION_KEY = 'gramiss_sms_v1_settings';
    private const API_URL    = 'https://api.sms.ir/v1/send/verify';
    private const META_SENT  = '_gramiss_sms_registration_sent_at';
    private const META_ID    = '_gramiss_sms_registration_message_id';

    public static function boot(): void {
        $self = new self();

        add_action( 'admin_menu', array( $self, 'admin_menu' ), 30 );
        add_action( 'admin_init', array( $self, 'register_settings' ) );

        add_action( 'woocommerce_checkout_order_created', array( $self, 'maybe_send_registration_sms' ), 30, 1 );
        add_action( 'woocommerce_store_api_checkout_order_processed', array( $self, 'maybe_send_registration_sms' ), 30, 1 );

        add_filter( 'woocommerce_order_actions', array( $self, 'add_order_action' ), 20, 2 );
        add_action( 'woocommerce_order_action_gramiss_sms_registration', array( $self, 'manual_order_action' ), 10, 1 );
    }

    private function settings(): array {
        return wp_parse_args(
            get_option( self::OPTION_KEY, array() ),
            array(
                'api_key'        => '',
                'template_id'    => '761339',
                'parameter_name' => 'ORDER_NUMBER',
                'gateway_id'     => '',
                'auto_enabled'   => '0',
            )
        );
    }

    public function admin_menu(): void {
        add_submenu_page(
            'woocommerce',
            'Gramiss SMS',
            'Gramiss SMS',
            'manage_woocommerce',
            'gramiss-sms',
            array( $this, 'render_settings_page' )
        );
    }

    public function register_settings(): void {
        register_setting(
            'gramiss_sms_v1_group',
            self::OPTION_KEY,
            array( $this, 'sanitize_settings' )
        );
    }

    public function sanitize_settings( $input ): array {
        $old   = $this->settings();
        $input = is_array( $input ) ? $input : array();

        $api_key = isset( $input['api_key'] ) ? trim( (string) $input['api_key'] ) : '';
        if ( '' === $api_key ) {
            $api_key = (string) $old['api_key'];
        }

        $parameter = isset( $input['parameter_name'] ) ? strtoupper( (string) $input['parameter_name'] ) : 'ORDER_NUMBER';
        $parameter = preg_replace( '/[^A-Z0-9_]/', '', $parameter );
        if ( '' === $parameter ) {
            $parameter = 'ORDER_NUMBER';
        }

        return array(
            'api_key'        => sanitize_text_field( $api_key ),
            'template_id'    => (string) absint( $input['template_id'] ?? 761339 ),
            'parameter_name' => sanitize_text_field( $parameter ),
            'gateway_id'     => sanitize_text_field( $input['gateway_id'] ?? '' ),
            'auto_enabled'   => empty( $input['auto_enabled'] ) ? '0' : '1',
        );
    }

    private function gateway_choices(): array {
        $choices = array();
        if ( function_exists( 'WC' ) && WC() && WC()->payment_gateways() ) {
            foreach ( WC()->payment_gateways()->payment_gateways() as $id => $gateway ) {
                $title = method_exists( $gateway, 'get_title' ) ? $gateway->get_title() : $id;
                $choices[ (string) $id ] = wp_strip_all_tags( (string) $title );
            }
        }
        return $choices;
    }

    public function render_settings_page(): void {
        if ( ! current_user_can( 'manage_woocommerce' ) ) {
            return;
        }

        $settings = $this->settings();
        $gateways = $this->gateway_choices();
        ?>
        <div class="wrap" dir="rtl">
            <h1>Gramiss SMS</h1>
            <p>ارسال پیامک خدماتی سفارش از طریق قالب تأییدشده SMS.ir. کلید API فقط در دیتابیس وردپرس ذخیره می‌شود و در سورس/GitHub قرار نمی‌گیرد.</p>

            <?php settings_errors(); ?>

            <form method="post" action="options.php" style="max-width:760px;background:#fff;padding:24px;border:1px solid #dcdcde;border-radius:12px;">
                <?php settings_fields( 'gramiss_sms_v1_group' ); ?>
                <table class="form-table" role="presentation">
                    <tr>
                        <th scope="row"><label for="gramiss-sms-api">API Key SMS.ir</label></th>
                        <td>
                            <input id="gramiss-sms-api" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[api_key]" type="password" value="" class="regular-text" autocomplete="new-password" placeholder="<?php echo $settings['api_key'] ? 'کلید ذخیره شده — برای حفظ آن خالی بگذارید' : 'کلید کامل API را وارد کنید'; ?>">
                            <p class="description">کلید را در چت یا GitHub قرار ندهید. برای تعویض کلید، مقدار جدید را اینجا وارد کنید.</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="gramiss-sms-template">شناسه قالب</label></th>
                        <td>
                            <input id="gramiss-sms-template" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[template_id]" type="number" min="1" value="<?php echo esc_attr( $settings['template_id'] ); ?>" class="regular-text">
                            <p class="description">قالب «ثبت سفارش Gramiss»؛ مقدار فعلی از قالب تأییدشده: 761339</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="gramiss-sms-param">نام متغیر شماره سفارش</label></th>
                        <td>
                            <input id="gramiss-sms-param" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[parameter_name]" type="text" value="<?php echo esc_attr( $settings['parameter_name'] ); ?>" class="regular-text" dir="ltr">
                            <p class="description">برای قالب #ORDER_NUMBER# مقدار باید ORDER_NUMBER باشد؛ بدون علامت #.</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="gramiss-sms-gateway">درگاه هدف</label></th>
                        <td>
                            <select id="gramiss-sms-gateway" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[gateway_id]" style="min-width:360px;max-width:100%;">
                                <option value="">— انتخاب کنید —</option>
                                <?php foreach ( $gateways as $id => $title ) : ?>
                                    <option value="<?php echo esc_attr( $id ); ?>" <?php selected( $settings['gateway_id'], $id ); ?>><?php echo esc_html( $title . ' [' . $id . ']' ); ?></option>
                                <?php endforeach; ?>
                            </select>
                            <p class="description">درگاه «کارت‌به‌کارت — Gramiss» را انتخاب کنید. ارسال خودکار فقط برای این درگاه اجرا می‌شود.</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">ارسال خودکار</th>
                        <td>
                            <label><input name="<?php echo esc_attr( self::OPTION_KEY ); ?>[auto_enabled]" type="checkbox" value="1" <?php checked( $settings['auto_enabled'], '1' ); ?>> بعد از ثبت سفارش کارت‌به‌کارت، قالب ثبت سفارش برای مشتری ارسال شود.</label>
                            <p class="description">پیشنهاد: ابتدا سفارش 513 را با «سفارش اعمال → ارسال/ارسال مجدد پیامک ثبت سفارش Gramiss» تست کنید؛ سپس این گزینه را روشن کنید.</p>
                        </td>
                    </tr>
                </table>
                <?php submit_button( 'ذخیره تنظیمات Gramiss SMS' ); ?>
            </form>
        </div>
        <?php
    }

    public function add_order_action( array $actions, $order = null ): array {
        $actions['gramiss_sms_registration'] = 'ارسال/ارسال مجدد پیامک ثبت سفارش Gramiss';
        return $actions;
    }

    public function manual_order_action( $order ): void {
        if ( ! $order instanceof WC_Order ) {
            return;
        }

        $result = $this->send_registration_sms( $order, true );
        if ( is_wp_error( $result ) ) {
            $order->add_order_note( 'Gramiss SMS — ارسال دستی ناموفق: ' . $result->get_error_message() );
            return;
        }

        $order->add_order_note( 'Gramiss SMS — پیامک ثبت سفارش به‌صورت دستی ارسال شد. شناسه پیام: ' . ( $result['message_id'] ?: 'نامشخص' ) );
    }

    public function maybe_send_registration_sms( $order ): void {
        if ( is_numeric( $order ) ) {
            $order = wc_get_order( (int) $order );
        }
        if ( ! $order instanceof WC_Order ) {
            return;
        }

        $settings = $this->settings();
        if ( '1' !== (string) $settings['auto_enabled'] ) {
            return;
        }
        if ( '' === (string) $settings['gateway_id'] || $order->get_payment_method() !== (string) $settings['gateway_id'] ) {
            return;
        }
        if ( $order->get_meta( self::META_SENT, true ) ) {
            return;
        }

        $result = $this->send_registration_sms( $order, false );
        if ( is_wp_error( $result ) ) {
            $order->add_order_note( 'Gramiss SMS — ارسال خودکار ناموفق: ' . $result->get_error_message() );
            return;
        }

        $order->add_order_note( 'Gramiss SMS — پیامک ثبت سفارش خودکار ارسال شد. شناسه پیام: ' . ( $result['message_id'] ?: 'نامشخص' ) );
    }

    private function send_registration_sms( WC_Order $order, bool $force = false ) {
        $settings = $this->settings();

        if ( ! $force && $order->get_meta( self::META_SENT, true ) ) {
            return new WP_Error( 'gramiss_sms_duplicate', 'این پیامک قبلاً برای سفارش ارسال شده است.' );
        }

        $api_key     = trim( (string) $settings['api_key'] );
        $template_id = absint( $settings['template_id'] );
        $param_name  = trim( (string) $settings['parameter_name'] );
        $mobile      = $this->normalize_mobile( (string) $order->get_billing_phone() );

        if ( '' === $api_key ) {
            return new WP_Error( 'gramiss_sms_api_key', 'API Key در تنظیمات Gramiss SMS وارد نشده است.' );
        }
        if ( ! $template_id ) {
            return new WP_Error( 'gramiss_sms_template', 'شناسه قالب معتبر نیست.' );
        }
        if ( '' === $param_name ) {
            return new WP_Error( 'gramiss_sms_parameter', 'نام متغیر قالب مشخص نشده است.' );
        }
        if ( ! $mobile ) {
            return new WP_Error( 'gramiss_sms_mobile', 'شماره موبایل مشتری معتبر نیست.' );
        }

        $payload = array(
            'mobile'     => $mobile,
            'templateId' => $template_id,
            'parameters' => array(
                array(
                    'name'  => $param_name,
                    'value' => (string) $order->get_order_number(),
                ),
            ),
        );

        $response = wp_remote_post(
            self::API_URL,
            array(
                'timeout'     => 20,
                'redirection' => 0,
                'headers'     => array(
                    'Accept'       => 'application/json',
                    'Content-Type' => 'application/json',
                    'X-API-KEY'    => $api_key,
                ),
                'body'        => wp_json_encode( $payload ),
                'data_format' => 'body',
            )
        );

        if ( is_wp_error( $response ) ) {
            $this->log( 'error', 'HTTP error while sending order SMS', array( 'order_id' => $order->get_id(), 'error' => $response->get_error_message() ) );
            return new WP_Error( 'gramiss_sms_http', 'ارتباط با SMS.ir برقرار نشد: ' . $response->get_error_message() );
        }

        $code = (int) wp_remote_retrieve_response_code( $response );
        $body = (string) wp_remote_retrieve_body( $response );
        $json = json_decode( $body, true );
        $json = is_array( $json ) ? $json : array();

        $status     = isset( $json['status'] ) ? (int) $json['status'] : null;
        $message    = isset( $json['message'] ) ? sanitize_text_field( (string) $json['message'] ) : '';
        $message_id = isset( $json['data']['messageId'] ) ? sanitize_text_field( (string) $json['data']['messageId'] ) : '';

        if ( $code < 200 || $code >= 300 || ( null !== $status && 1 !== $status ) ) {
            $safe_message = $message ?: 'پاسخ ناموفق از SMS.ir';
            $this->log( 'error', 'SMS.ir rejected order SMS', array( 'order_id' => $order->get_id(), 'http_code' => $code, 'status' => $status, 'message' => $safe_message ) );
            return new WP_Error( 'gramiss_sms_rejected', $safe_message );
        }

        $order->update_meta_data( self::META_SENT, current_time( 'mysql', true ) );
        $order->update_meta_data( self::META_ID, $message_id );
        $order->save();

        $this->log( 'info', 'Order registration SMS sent', array( 'order_id' => $order->get_id(), 'message_id' => $message_id, 'template_id' => $template_id ) );

        return array(
            'message_id' => $message_id,
            'status'     => $status,
            'http_code'  => $code,
        );
    }

    private function normalize_mobile( string $raw ): string {
        $fa = array( '۰','۱','۲','۳','۴','۵','۶','۷','۸','۹','٠','١','٢','٣','٤','٥','٦','٧','٨','٩' );
        $en = array( '0','1','2','3','4','5','6','7','8','9','0','1','2','3','4','5','6','7','8','9' );
        $mobile = str_replace( $fa, $en, $raw );
        $mobile = preg_replace( '/\D+/', '', $mobile );

        if ( 0 === strpos( $mobile, '0098' ) ) {
            $mobile = '0' . substr( $mobile, 4 );
        } elseif ( 0 === strpos( $mobile, '98' ) && 12 === strlen( $mobile ) ) {
            $mobile = '0' . substr( $mobile, 2 );
        } elseif ( 10 === strlen( $mobile ) && '9' === substr( $mobile, 0, 1 ) ) {
            $mobile = '0' . $mobile;
        }

        return preg_match( '/^09\d{9}$/', $mobile ) ? $mobile : '';
    }

    private function log( string $level, string $message, array $context = array() ): void {
        if ( function_exists( 'wc_get_logger' ) ) {
            wc_get_logger()->log( $level, $message, array_merge( array( 'source' => 'gramiss-sms' ), $context ) );
        }
    }
}

add_action( 'plugins_loaded', static function () {
    if ( class_exists( 'WooCommerce' ) ) {
        Gramiss_SMS_V1::boot();
    }
}, 20 );
