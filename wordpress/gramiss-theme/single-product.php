<?php
/** Single product page. @package Gramiss */
defined( 'ABSPATH' ) || exit;
get_header();
?>
<main id="primary" class="g1-product-page">
    <?php if ( function_exists( 'woocommerce_breadcrumb' ) ) { woocommerce_breadcrumb(); } ?>
    <?php while ( have_posts() ) : the_post(); ?>
        <?php wc_get_template_part( 'content', 'single-product' ); ?>
        <section class="g1-trust-rail" aria-label="مزایای خرید از Gramiss">
            <div class="g1-trust-item"><strong>انتخاب دقیق‌تر</strong><span>اطلاعات واقعی درباره جنس، سایز و کاربرد</span></div>
            <div class="g1-trust-item"><strong>ارسال به سراسر ایران</strong><span>پیگیری سفارش از حساب کاربری</span></div>
            <div class="g1-trust-item"><strong>پشتیبانی قبل از خرید</strong><span>برای انتخاب بهتر، نه فروش بیشتر</span></div>
        </section>
    <?php endwhile; ?>
</main>
<?php get_footer(); ?>
