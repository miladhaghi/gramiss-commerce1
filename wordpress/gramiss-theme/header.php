<?php
/** Site header. @package Gramiss */
defined( 'ABSPATH' ) || exit;
?><!doctype html>
<html <?php language_attributes(); ?> dir="rtl">
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<header class="site-header" aria-label="ناوبری اصلی">
    <div class="gramiss-container header-inner">
        <div class="header-cluster">
            <button class="menu-toggle" type="button" aria-label="باز کردن منو" aria-controls="gramiss-mobile-panel" aria-expanded="false">☰</button>
            <a class="wordmark" href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="Gramiss، صفحه اصلی">GRAMISS</a>
            <nav class="primary-nav" aria-label="فهرست اصلی">
                <?php wp_nav_menu( array( 'theme_location' => 'primary', 'container' => false, 'fallback_cb' => 'gramiss_primary_fallback' ) ); ?>
            </nav>
        </div>
        <div class="header-actions">
            <button class="search-toggle" type="button" aria-label="جست‌وجو">⌕</button>
            <?php if ( function_exists( 'wc_get_page_permalink' ) ) : ?>
                <a class="icon-link account-link" href="<?php echo esc_url( wc_get_page_permalink( 'myaccount' ) ); ?>" aria-label="حساب کاربری">♙</a>
                <a class="icon-link" href="<?php echo esc_url( wc_get_cart_url() ); ?>" aria-label="سبد خرید">
                    <span aria-hidden="true">♧</span>
                    <span class="header-count gramiss-cart-count"><?php echo esc_html( gramiss_cart_count() ); ?></span>
                </a>
            <?php endif; ?>
        </div>
    </div>
</header>
<div id="gramiss-mobile-panel" class="mobile-panel" aria-hidden="true">
    <button class="mobile-panel-backdrop" type="button" aria-label="بستن منو"></button>
    <div class="mobile-panel-content">
        <div class="mobile-panel-head"><span class="wordmark">GRAMISS</span><button class="menu-close icon-link" type="button" aria-label="بستن">×</button></div>
        <nav aria-label="منوی موبایل"><?php wp_nav_menu( array( 'theme_location' => 'primary', 'container' => false, 'fallback_cb' => 'gramiss_primary_fallback' ) ); ?></nav>
    </div>
</div>
<div class="search-overlay" aria-hidden="true"><div class="search-dialog" role="dialog" aria-modal="true" aria-label="جست‌وجوی محصولات"><?php get_product_search_form(); ?></div></div>
<?php
function gramiss_primary_fallback(): void {
    $shop = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
    echo '<ul><li><a href="' . esc_url( $shop ) . '">Shop</a></li><li><a href="' . esc_url( home_url( '/#collections' ) ) . '">Collections</a></li><li><a href="' . esc_url( home_url( '/#journal' ) ) . '">Journal</a></li><li><a href="' . esc_url( home_url( '/#about' ) ) . '">About</a></li></ul>';
}
