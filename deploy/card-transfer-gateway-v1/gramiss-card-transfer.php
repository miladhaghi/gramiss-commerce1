<?php
/**
 * Plugin Name: Gramiss Card Transfer
 * Description: Temporary branded card-to-card payment gateway for Gramiss WooCommerce orders.
 * Version: 1.0.0
 * Author: Gramiss
 * Text Domain: gramiss-card-transfer
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

define( 'GRAMISS_CARD_TRANSFER_VERSION', '1.0.0' );
define( 'GRAMISS_CARD_TRANSFER_FILE', __FILE__ );
define( 'GRAMISS_CARD_TRANSFER_URL', plugin_dir_url( __FILE__ ) );

register_activation_hook( __FILE__, function () {
    $key = 'woocommerce_gramiss_card_transfer_settings';
    if ( false === get_option( $key, false ) ) {
        add_option( $key, array(
            'enabled'              => 'yes',
            'title'                => 'کارت‌به‌کارت',
            'description'          => 'سفارش ثبت می‌شود؛ سپس شماره کارت مقصد و فرم ثبت رسید نمایش داده خواهد شد.',
            'bank_name'            => '',
            'card_holder'          => '',
            'card_number'          => '',
            'instructions'         => 'پس از واریز، شماره پیگیری یا تصویر رسید را ثبت کنید. سفارش پس از تأیید پرداخت وارد مرحله آماده‌سازی می‌شود.',
        ) );
    }
} );

add_action( 'plugins_loaded', function () {
    if ( ! class_exists( 'WC_Payment_Gateway' ) ) {
        return;
    }

    class WC_Gateway_Gramiss_Card_Transfer extends WC_Payment_Gateway {
        public $bank_name;
        public $card_holder;
        public $card_number;
        public $instructions;

        public function __construct() {
            $this->id                 = 'gramiss_card_transfer';
            $this->icon               = '';
            $this->has_fields         = true;
            $this->method_title       = 'Gramiss — کارت‌به‌کارت';
            $this->method_description = 'درگاه موقت کارت‌به‌کارت با ثبت رسید و تأیید دستی سفارش.';
            $this->supports           = array( 'products' );

            $this->init_form_fields();
            $this->init_settings();

            $this->title        = $this->get_option( 'title', 'کارت‌به‌کارت' );
            $this->description  = $this->get_option( 'description', '' );
            $this->enabled      = $this->get_option( 'enabled', 'yes' );
            $this->bank_name    = trim( (string) $this->get_option( 'bank_name', '' ) );
            $this->card_holder  = trim( (string) $this->get_option( 'card_holder', '' ) );
            $this->card_number  = preg_replace( '/\D+/', '', (string) $this->get_option( 'card_number', '' ) );
            $this->instructions = trim( (string) $this->get_option( 'instructions', '' ) );

            add_action( 'woocommerce_update_options_payment_gateways_' . $this->id, array( $this, 'process_admin_options' ) );
            add_action( 'woocommerce_thankyou_' . $this->id, array( $this, 'thankyou_page' ), 5 );
        }

        public function init_form_fields() {
            $this->form_fields = array(
                'enabled' => array(
                    'title'   => 'فعال‌سازی',
                    'type'    => 'checkbox',
                    'label'   => 'نمایش روش پرداخت کارت‌به‌کارت در تسویه حساب',
                    'default' => 'yes',
                ),
                'title' => array(
                    'title'       => 'عنوان روش پرداخت',
                    'type'        => 'text',
                    'default'     => 'کارت‌به‌کارت',
                    'desc_tip'    => true,
                    'description' => 'عنوانی که مشتری در Checkout می‌بیند.',
                ),
                'description' => array(
                    'title'   => 'توضیح کوتاه در Checkout',
                    'type'    => 'textarea',
                    'default' => 'سفارش ثبت می‌شود؛ سپس شماره کارت مقصد و فرم ثبت رسید نمایش داده خواهد شد.',
                ),
                'bank_name' => array(
                    'title'       => 'نام بانک',
                    'type'        => 'text',
                    'placeholder' => 'مثلاً بانک ملت',
                    'description' => 'در صفحه پرداخت نمایش داده می‌شود.',
                ),
                'card_holder' => array(
                    'title'       => 'نام صاحب کارت',
                    'type'        => 'text',
                    'placeholder' => 'نام و نام خانوادگی',
                    'description' => 'برای تطبیق کارت مقصد.',
                ),
                'card_number' => array(
                    'title'       => 'شماره کارت مقصد',
                    'type'        => 'text',
                    'placeholder' => '16 رقم بدون خط تیره',
                    'description' => 'تا زمانی که این فیلد و نام صاحب کارت تکمیل نشده باشند، روش پرداخت به مشتری نمایش داده نمی‌شود.',
                ),
                'instructions' => array(
                    'title'   => 'راهنمای ثبت رسید',
                    'type'    => 'textarea',
                    'default' => 'پس از واریز، شماره پیگیری یا تصویر رسید را ثبت کنید. سفارش پس از تأیید پرداخت وارد مرحله آماده‌سازی می‌شود.',
                ),
            );
        }

        public function is_available() {
            if ( 'yes' !== $this->enabled || strlen( $this->card_number ) < 16 || '' === $this->card_holder ) {
                return false;
            }
            return parent::is_available();
        }

        public function payment_fields() {
            if ( $this->description ) {
                echo '<p class="gct-checkout-description">' . wp_kses_post( wpautop( $this->description ) ) . '</p>';
            }
            echo '<div class="gct-checkout-note">';
            echo '<span class="gct-checkout-note__mark" aria-hidden="true">↗</span>';
            echo '<div><strong>پرداخت بعد از ثبت سفارش</strong><small>شماره کارت کامل، مبلغ دقیق و فرم ثبت رسید در مرحله بعد نمایش داده می‌شود.</small></div>';
            echo '</div>';
        }

        public function validate_fields() {
            if ( ! $this->is_available() ) {
                wc_add_notice( 'روش کارت‌به‌کارت در حال حاضر در دسترس نیست. لطفاً روش دیگری را انتخاب کنید.', 'error' );
                return false;
            }
            return true;
        }

        public function process_payment( $order_id ) {
            $order = wc_get_order( $order_id );
            if ( ! $order ) {
                return array( 'result' => 'failure' );
            }

            $order->update_status( 'on-hold', 'در انتظار واریز کارت‌به‌کارت و تأیید رسید توسط Gramiss.' );
            $order->update_meta_data( '_gramiss_card_transfer_expected_amount', (string) $order->get_total() );
            $order->save();

            wc_reduce_stock_levels( $order_id );
            if ( WC()->cart ) {
                WC()->cart->empty_cart();
            }

            return array(
                'result'   => 'success',
                'redirect' => $this->get_return_url( $order ),
            );
        }

        private function formatted_card_number() {
            return trim( chunk_split( $this->card_number, 4, ' ' ) );
        }

        public function thankyou_page( $order_id ) {
            $order = wc_get_order( $order_id );
            if ( ! $order || $this->id !== $order->get_payment_method() ) {
                return;
            }

            $submitted = (bool) $order->get_meta( '_gramiss_card_transfer_submitted_at', true );
            $tracking  = (string) $order->get_meta( '_gramiss_card_transfer_tracking_code', true );
            $status    = isset( $_GET['gct_status'] ) ? sanitize_key( wp_unslash( $_GET['gct_status'] ) ) : '';
            $amount    = wp_strip_all_tags( $order->get_formatted_order_total() );
            $nonce     = wp_create_nonce( 'gct_receipt_' . $order_id . '_' . $order->get_order_key() );

            echo '<section class="gct-payment" dir="rtl" data-gct-payment>';
            echo '<div class="gct-payment__eyebrow">GRAMISS / PAYMENT</div>';
            echo '<div class="gct-payment__head"><div><h2>پرداخت سفارش</h2><p>سفارش <bdi>#' . esc_html( $order->get_order_number() ) . '</bdi> ثبت شد و تا تأیید واریز برای شما نگه داشته می‌شود.</p></div><span class="gct-payment__status">در انتظار پرداخت</span></div>';

            if ( 'ok' === $status ) {
                echo '<div class="gct-alert gct-alert--success">رسید شما دریافت شد. بعد از تأیید پرداخت، وضعیت سفارش به‌روزرسانی می‌شود.</div>';
            } elseif ( 'missing' === $status ) {
                echo '<div class="gct-alert gct-alert--error">لطفاً شماره پیگیری یا تصویر رسید را وارد کنید.</div>';
            } elseif ( 'upload' === $status ) {
                echo '<div class="gct-alert gct-alert--error">فایل رسید قابل ثبت نبود. تصویر JPG/PNG/WEBP یا PDF تا ۵ مگابایت ارسال کنید.</div>';
            }

            echo '<div class="gct-amount"><span>مبلغ قابل پرداخت</span><strong>' . esc_html( $amount ) . '</strong></div>';
            echo '<div class="gct-card">';
            echo '<div class="gct-card__top"><span>کارت مقصد</span><span>' . esc_html( $this->bank_name ?: 'بانک مقصد' ) . '</span></div>';
            echo '<div class="gct-card__number" dir="ltr">' . esc_html( $this->formatted_card_number() ) . '</div>';
            echo '<div class="gct-card__bottom"><div><small>به نام</small><strong>' . esc_html( $this->card_holder ) . '</strong></div><button type="button" class="gct-copy" data-copy="' . esc_attr( $this->card_number ) . '"><span>کپی شماره کارت</span><b aria-hidden="true">↗</b></button></div>';
            echo '</div>';

            if ( $this->instructions ) {
                echo '<p class="gct-instructions">' . wp_kses_post( $this->instructions ) . '</p>';
            }

            if ( $submitted ) {
                echo '<div class="gct-submitted"><span class="gct-submitted__check">✓</span><div><strong>رسید برای بررسی ثبت شده</strong><p>' . ( $tracking ? 'شماره پیگیری: <bdi>' . esc_html( $tracking ) . '</bdi>' : 'تصویر رسید دریافت شده است.' ) . '</p></div></div>';
            }

            echo '<form class="gct-receipt" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" method="post" enctype="multipart/form-data">';
            echo '<input type="hidden" name="action" value="gramiss_card_transfer_receipt">';
            echo '<input type="hidden" name="order_id" value="' . esc_attr( $order_id ) . '">';
            echo '<input type="hidden" name="order_key" value="' . esc_attr( $order->get_order_key() ) . '">';
            echo '<input type="hidden" name="gct_nonce" value="' . esc_attr( $nonce ) . '">';
            echo '<div class="gct-receipt__title"><span>پرداخت رو انجام دادی؟</span><small>یکی از دو مورد زیر کافی است.</small></div>';
            echo '<label class="gct-field"><span>شماره پیگیری</span><input type="text" name="tracking_code" inputmode="numeric" autocomplete="off" placeholder="شماره پیگیری تراکنش"></label>';
            echo '<label class="gct-upload"><input type="file" name="receipt" accept="image/jpeg,image/png,image/webp,application/pdf"><span class="gct-upload__icon">＋</span><span><strong>آپلود رسید</strong><small data-gct-file-name>JPG، PNG، WEBP یا PDF تا ۵MB</small></span></label>';
            echo '<button class="gct-submit" type="submit">ارسال برای تأیید پرداخت <span>↗</span></button>';
            echo '<p class="gct-privacy">هیچ اطلاعاتی مثل شماره کارت شما، CVV2 یا رمز پویا دریافت نمی‌شود.</p>';
            echo '</form>';
            echo '</section>';
        }
    }

    add_filter( 'woocommerce_payment_gateways', function ( $gateways ) {
        $gateways[] = 'WC_Gateway_Gramiss_Card_Transfer';
        return $gateways;
    } );
}, 20 );

function gramiss_card_transfer_order_from_request() {
    $order_id  = isset( $_POST['order_id'] ) ? absint( $_POST['order_id'] ) : 0;
    $order_key = isset( $_POST['order_key'] ) ? wc_clean( wp_unslash( $_POST['order_key'] ) ) : '';
    $nonce     = isset( $_POST['gct_nonce'] ) ? sanitize_text_field( wp_unslash( $_POST['gct_nonce'] ) ) : '';
    $order     = $order_id ? wc_get_order( $order_id ) : false;

    if ( ! $order || 'gramiss_card_transfer' !== $order->get_payment_method() || ! hash_equals( (string) $order->get_order_key(), (string) $order_key ) ) {
        return false;
    }
    if ( ! wp_verify_nonce( $nonce, 'gct_receipt_' . $order_id . '_' . $order->get_order_key() ) ) {
        return false;
    }
    return $order;
}

function gramiss_card_transfer_receipt_dir() {
    $upload = wp_upload_dir();
    $dir    = trailingslashit( $upload['basedir'] ) . 'gramiss-receipts';
    if ( ! is_dir( $dir ) ) {
        wp_mkdir_p( $dir );
    }
    $protect = $dir . '/.htaccess';
    if ( ! file_exists( $protect ) ) {
        @file_put_contents( $protect, "Options -Indexes\n<FilesMatch \".*\">\nRequire all denied\n</FilesMatch>\n" );
    }
    return $dir;
}

function gramiss_card_transfer_handle_receipt() {
    if ( ! function_exists( 'wc_get_order' ) ) {
        wp_die( 'WooCommerce unavailable.' );
    }

    $order = gramiss_card_transfer_order_from_request();
    if ( ! $order ) {
        wp_die( 'درخواست نامعتبر است.', 'Gramiss', array( 'response' => 403 ) );
    }

    $tracking = isset( $_POST['tracking_code'] ) ? sanitize_text_field( wp_unslash( $_POST['tracking_code'] ) ) : '';
    $has_file = isset( $_FILES['receipt'] ) && is_array( $_FILES['receipt'] ) && ! empty( $_FILES['receipt']['name'] ) && UPLOAD_ERR_NO_FILE !== (int) $_FILES['receipt']['error'];
    $base     = $order->get_checkout_order_received_url();

    if ( '' === $tracking && ! $has_file ) {
        wp_safe_redirect( add_query_arg( 'gct_status', 'missing', $base ) . '#gramiss-payment' );
        exit;
    }

    $saved_file = '';
    $saved_mime = '';

    if ( $has_file ) {
        $file = $_FILES['receipt'];
        if ( UPLOAD_ERR_OK !== (int) $file['error'] || (int) $file['size'] > 5 * 1024 * 1024 ) {
            wp_safe_redirect( add_query_arg( 'gct_status', 'upload', $base ) );
            exit;
        }

        $allowed = array(
            'jpg|jpeg' => 'image/jpeg',
            'png'      => 'image/png',
            'webp'     => 'image/webp',
            'pdf'      => 'application/pdf',
        );
        $check = wp_check_filetype_and_ext( $file['tmp_name'], $file['name'], $allowed );
        if ( empty( $check['ext'] ) || empty( $check['type'] ) ) {
            wp_safe_redirect( add_query_arg( 'gct_status', 'upload', $base ) );
            exit;
        }

        $dir      = gramiss_card_transfer_receipt_dir();
        $filename = wp_unique_filename( $dir, 'order-' . $order->get_id() . '-' . wp_generate_password( 14, false, false ) . '.' . $check['ext'] );
        $target   = trailingslashit( $dir ) . $filename;
        if ( ! @move_uploaded_file( $file['tmp_name'], $target ) ) {
            wp_safe_redirect( add_query_arg( 'gct_status', 'upload', $base ) );
            exit;
        }
        @chmod( $target, 0640 );
        $saved_file = $filename;
        $saved_mime = $check['type'];
    }

    if ( $tracking ) {
        $order->update_meta_data( '_gramiss_card_transfer_tracking_code', $tracking );
    }
    if ( $saved_file ) {
        $order->update_meta_data( '_gramiss_card_transfer_receipt_file', $saved_file );
        $order->update_meta_data( '_gramiss_card_transfer_receipt_mime', $saved_mime );
    }
    $order->update_meta_data( '_gramiss_card_transfer_submitted_at', current_time( 'mysql' ) );
    $order->add_order_note( 'مشتری اطلاعات کارت‌به‌کارت را برای تأیید ارسال کرد.' . ( $tracking ? ' شماره پیگیری: ' . $tracking : '' ) );
    $order->save();

    wp_safe_redirect( add_query_arg( 'gct_status', 'ok', $base ) . '#gramiss-payment' );
    exit;
}
add_action( 'admin_post_gramiss_card_transfer_receipt', 'gramiss_card_transfer_handle_receipt' );
add_action( 'admin_post_nopriv_gramiss_card_transfer_receipt', 'gramiss_card_transfer_handle_receipt' );

add_action( 'admin_post_gramiss_card_transfer_receipt_file', function () {
    if ( ! current_user_can( 'manage_woocommerce' ) ) {
        wp_die( 'دسترسی غیرمجاز.', 'Gramiss', array( 'response' => 403 ) );
    }
    $order_id = isset( $_GET['order_id'] ) ? absint( $_GET['order_id'] ) : 0;
    $nonce    = isset( $_GET['_wpnonce'] ) ? sanitize_text_field( wp_unslash( $_GET['_wpnonce'] ) ) : '';
    if ( ! $order_id || ! wp_verify_nonce( $nonce, 'gct_admin_receipt_' . $order_id ) ) {
        wp_die( 'درخواست نامعتبر.', 'Gramiss', array( 'response' => 403 ) );
    }
    $order = wc_get_order( $order_id );
    $file  = $order ? basename( (string) $order->get_meta( '_gramiss_card_transfer_receipt_file', true ) ) : '';
    $mime  = $order ? (string) $order->get_meta( '_gramiss_card_transfer_receipt_mime', true ) : '';
    $path  = $file ? trailingslashit( gramiss_card_transfer_receipt_dir() ) . $file : '';
    if ( ! $path || ! is_file( $path ) ) {
        wp_die( 'رسید پیدا نشد.', 'Gramiss', array( 'response' => 404 ) );
    }
    nocache_headers();
    header( 'Content-Type: ' . ( $mime ?: 'application/octet-stream' ) );
    header( 'Content-Disposition: inline; filename="receipt-' . $order_id . '.' . pathinfo( $file, PATHINFO_EXTENSION ) . '"' );
    header( 'Content-Length: ' . filesize( $path ) );
    readfile( $path );
    exit;
} );

add_action( 'woocommerce_admin_order_data_after_billing_address', function ( $order ) {
    if ( ! $order || 'gramiss_card_transfer' !== $order->get_payment_method() ) {
        return;
    }
    $tracking  = (string) $order->get_meta( '_gramiss_card_transfer_tracking_code', true );
    $file      = (string) $order->get_meta( '_gramiss_card_transfer_receipt_file', true );
    $submitted = (string) $order->get_meta( '_gramiss_card_transfer_submitted_at', true );
    echo '<div style="margin-top:14px;padding:12px;border:1px solid #e5e1da;border-radius:10px;background:#faf9f6">';
    echo '<strong>Gramiss — کارت‌به‌کارت</strong>';
    echo '<p style="margin:7px 0 0">وضعیت: ' . ( $submitted ? '<b style="color:#297a4a">رسید ثبت شده</b>' : 'در انتظار رسید' ) . '</p>';
    if ( $tracking ) {
        echo '<p style="margin:5px 0 0">شماره پیگیری: <code>' . esc_html( $tracking ) . '</code></p>';
    }
    if ( $file ) {
        $url = wp_nonce_url( admin_url( 'admin-post.php?action=gramiss_card_transfer_receipt_file&order_id=' . $order->get_id() ), 'gct_admin_receipt_' . $order->get_id() );
        echo '<p style="margin:7px 0 0"><a class="button" target="_blank" rel="noopener" href="' . esc_url( $url ) . '">مشاهده رسید</a></p>';
    }
    echo '</div>';
} );

add_action( 'wp_enqueue_scripts', function () {
    if ( function_exists( 'is_checkout' ) && is_checkout() ) {
        wp_enqueue_style( 'gramiss-card-transfer', GRAMISS_CARD_TRANSFER_URL . 'assets/card-transfer.css', array(), GRAMISS_CARD_TRANSFER_VERSION );
        wp_enqueue_script( 'gramiss-card-transfer', GRAMISS_CARD_TRANSFER_URL . 'assets/card-transfer.js', array(), GRAMISS_CARD_TRANSFER_VERSION, true );
    }
}, 40 );

add_filter( 'plugin_action_links_' . plugin_basename( __FILE__ ), function ( $links ) {
    $url = admin_url( 'admin.php?page=wc-settings&tab=checkout&section=gramiss_card_transfer' );
    array_unshift( $links, '<a href="' . esc_url( $url ) . '">تنظیمات کارت</a>' );
    return $links;
} );
