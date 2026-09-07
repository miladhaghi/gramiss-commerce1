<?php
/**
 * Plugin Name: Gramiss Site Info
 * Description: اطلاعات تماس و پشتیبانی عمومی Gramiss برای صفحات سایت و سرویس‌های فروشگاهی.
 * Version: 0.1.0
 * Author: Gramiss
 */

defined( 'ABSPATH' ) || exit;

final class Gramiss_Site_Info_V1 {
    public const OPTION_KEY = 'gramiss_site_info_v1';

    public static function boot(): void {
        $self = new self();
        add_action( 'admin_menu', array( $self, 'admin_menu' ) );
        add_action( 'admin_init', array( $self, 'register_settings' ) );
    }

    public static function get(): array {
        return wp_parse_args(
            get_option( self::OPTION_KEY, array() ),
            array(
                'phone' => '',
                'email' => '',
                'hours' => '',
            )
        );
    }

    public function admin_menu(): void {
        add_options_page(
            'اطلاعات Gramiss',
            'اطلاعات Gramiss',
            'manage_options',
            'gramiss-site-info',
            array( $this, 'render_page' )
        );
    }

    public function register_settings(): void {
        register_setting(
            'gramiss_site_info_group',
            self::OPTION_KEY,
            array( $this, 'sanitize' )
        );
    }

    public function sanitize( $input ): array {
        $input = is_array( $input ) ? $input : array();
        $phone = isset( $input['phone'] ) ? trim( (string) $input['phone'] ) : '';
        $phone = preg_replace( '/[^0-9+()\-\s]/u', '', $phone );

        return array(
            'phone' => sanitize_text_field( $phone ),
            'email' => sanitize_email( $input['email'] ?? '' ),
            'hours' => sanitize_text_field( $input['hours'] ?? '' ),
        );
    }

    public function render_page(): void {
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }
        $info = self::get();
        ?>
        <div class="wrap" dir="rtl" style="max-width:900px">
            <h1>اطلاعات عمومی Gramiss</h1>
            <p>این اطلاعات در صفحه «پشتیبانی و تماس» نمایش داده می‌شود و برای معرفی فروشگاه در سرویس‌هایی مثل ترب قابل استفاده است.</p>
            <?php settings_errors(); ?>
            <form method="post" action="options.php" style="background:#fff;border:1px solid #dcdcde;border-radius:14px;padding:24px;margin-top:20px">
                <?php settings_fields( 'gramiss_site_info_group' ); ?>
                <table class="form-table" role="presentation">
                    <tr>
                        <th scope="row"><label for="gramiss-info-phone">شماره پشتیبانی</label></th>
                        <td><input id="gramiss-info-phone" class="regular-text" dir="ltr" type="text" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[phone]" value="<?php echo esc_attr( $info['phone'] ); ?>" placeholder="09xxxxxxxxx"></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="gramiss-info-email">ایمیل پشتیبانی</label></th>
                        <td><input id="gramiss-info-email" class="regular-text" dir="ltr" type="email" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[email]" value="<?php echo esc_attr( $info['email'] ); ?>" placeholder="support@example.com"></td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="gramiss-info-hours">ساعات پاسخ‌گویی</label></th>
                        <td><input id="gramiss-info-hours" class="regular-text" type="text" name="<?php echo esc_attr( self::OPTION_KEY ); ?>[hours]" value="<?php echo esc_attr( $info['hours'] ); ?>" placeholder="مثلاً شنبه تا پنج‌شنبه، ۱۰ تا ۲۰"></td>
                    </tr>
                </table>
                <?php submit_button( 'ذخیره اطلاعات Gramiss' ); ?>
            </form>
        </div>
        <?php
    }
}

Gramiss_Site_Info_V1::boot();

function gramiss_site_info_v1(): array {
    return Gramiss_Site_Info_V1::get();
}
