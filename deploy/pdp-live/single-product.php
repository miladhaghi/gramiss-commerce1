<?php
/**
 * Gramiss single product page.
 *
 * Separates the purchase row from tabs, upsells and related products so
 * lower content can never collide with the product summary.
 *
 * @package Gramiss
 */
defined( 'ABSPATH' ) || exit;
get_header();
?>
<main id="primary" class="g1-product-page">
    <?php if ( function_exists( 'woocommerce_breadcrumb' ) ) { woocommerce_breadcrumb(); } ?>

    <?php while ( have_posts() ) : the_post(); ?>
        <?php
        do_action( 'woocommerce_before_single_product' );

        if ( post_password_required() ) {
            echo get_the_password_form(); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
            continue;
        }

        global $product;
        ?>

        <div id="product-<?php the_ID(); ?>" <?php wc_product_class( 'g1-pdp-product', $product ); ?>>
            <section class="g1-pdp-main" aria-label="اطلاعات و خرید محصول">
                <div class="g1-pdp-gallery-col">
                    <?php do_action( 'woocommerce_before_single_product_summary' ); ?>
                </div>

                <div class="summary entry-summary g1-pdp-summary">
                    <?php do_action( 'woocommerce_single_product_summary' ); ?>
                </div>
            </section>

            <div class="g1-pdp-after">
                <?php do_action( 'woocommerce_after_single_product_summary' ); ?>
            </div>
        </div>

        <?php do_action( 'woocommerce_after_single_product' ); ?>

        <section class="g1-trust-rail" aria-label="مزایای خرید از Gramiss">
            <div class="g1-trust-item"><strong>انتخاب دقیق‌تر</strong><span>اطلاعات واقعی درباره جنس، سایز و کاربرد</span></div>
            <div class="g1-trust-item"><strong>ارسال به سراسر ایران</strong><span>پیگیری سفارش از حساب کاربری</span></div>
            <div class="g1-trust-item"><strong>پشتیبانی قبل از خرید</strong><span>برای انتخاب بهتر، نه فروش بیشتر</span></div>
        </section>
    <?php endwhile; ?>
</main>
<?php get_footer(); ?>
