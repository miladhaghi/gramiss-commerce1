<?php
/**
 * Site header.
 *
 * @package Gramiss
 */
defined( 'ABSPATH' ) || exit;

$shop_url      = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$wishlist_page = get_page_by_path( 'wishlist' );
$compare_page  = get_page_by_path( 'compare' );
$wishlist_url  = $wishlist_page ? get_permalink( $wishlist_page ) : add_query_arg( 'gramiss_page', 'wishlist', home_url( '/' ) );
$compare_url   = $compare_page ? get_permalink( $compare_page ) : add_query_arg( 'gramiss_page', 'compare', home_url( '/' ) );
$release_css   = get_template_directory_uri() . '/assets/css/gramiss-release.css';
$release_ver   = gramiss_asset_version( '/assets/css/gramiss-release.css', (string) wp_get_theme()->get( 'Version' ) );
$is_shop_view  = function_exists( 'is_shop' ) && ( is_shop() || is_product_taxonomy() || is_post_type_archive( 'product' ) );
$is_home_view  = is_front_page();
$shop_css      = get_template_directory_uri() . '/assets/css/shop.css';
$shop_css_ver  = gramiss_asset_version( '/assets/css/shop.css', (string) wp_get_theme()->get( 'Version' ) );
$home_header_css = get_template_directory_uri() . '/assets/css/home-floating-header.css';
$home_header_css_ver = gramiss_asset_version( '/assets/css/home-floating-header.css', '20260820-1' );
$home_header_js = get_template_directory_uri() . '/assets/js/home-floating-header.js';
$home_header_js_ver = gramiss_asset_version( '/assets/js/home-floating-header.js', '20260820-1' );
?><!doctype html>
<html <?php language_attributes(); ?> dir="rtl">
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="theme-color" content="#101319">
    <?php wp_head(); ?>
    <link rel="stylesheet" id="gramiss-release-css" href="<?php echo esc_url( add_query_arg( 'ver', $release_ver, $release_css ) ); ?>" media="all">
    <?php if ( $is_home_view ) : ?>
        <link rel="stylesheet" id="gramiss-home-floating-header-css" href="<?php echo esc_url( add_query_arg( 'ver', $home_header_css_ver, $home_header_css ) ); ?>" media="all">
        <script id="gramiss-home-floating-header-js" defer src="<?php echo esc_url( add_query_arg( 'ver', $home_header_js_ver, $home_header_js ) ); ?>"></script>
    <?php endif; ?>
    <?php if ( $is_shop_view ) : ?>
        <link rel="stylesheet" id="gramiss-shop-css" href="<?php echo esc_url( add_query_arg( 'ver', $shop_css_ver, $shop_css ) ); ?>" media="all">
    <?php endif; ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<a class="screen-reader-text" href="#primary">پرش به محتوای اصلی</a>
<?php if ( ! $is_home_view ) : ?>
<div class="g1-announcement">
    <span>انتخاب بهتر، خرید مطمئن‌تر</span>
    <span aria-hidden="true">/</span>
    <span>ارسال به سراسر ایران</span>
</div>
<?php endif; ?>

<header class="site-header<?php echo $is_home_view ? ' site-header--home-float' : ''; ?>" aria-label="ناوبری اصلی">
    <div class="gramiss-container header-inner<?php echo $is_home_view ? ' header-inner--home-float' : ''; ?>">
        <div class="header-cluster">
            <button class="menu-toggle" type="button" aria-label="باز کردن منو" aria-controls="gramiss-mobile-panel" aria-expanded="false">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
            </button>

            <a class="wordmark" href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="Gramiss، صفحه اصلی">GRAMISS</a>

            <nav class="primary-nav" aria-label="فهرست اصلی">
                <?php
                wp_nav_menu(
                    array(
                        'theme_location' => 'primary',
                        'container'      => false,
                        'fallback_cb'    => 'gramiss_primary_fallback',
                    )
                );
                ?>
            </nav>
        </div>

        <form class="g1-header-search" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
            <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
            <label class="screen-reader-text" for="g1-product-search">جست‌وجوی محصول</label>
            <input id="g1-product-search" type="search" name="s" placeholder="جست‌وجوی محصول، استایل یا راهنما" value="<?php echo esc_attr( get_search_query() ); ?>" autocomplete="off">
            <input type="hidden" name="post_type" value="product">
        </form>

        <div class="header-actions">
            <button class="search-toggle" type="button" aria-label="باز کردن جست‌وجو" aria-expanded="false">
                <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
            </button>

            <a class="icon-link" href="<?php echo esc_url( $wishlist_url ); ?>" aria-label="علاقه‌مندی‌ها">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.5 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z"/></svg>
            </a>

            <a class="icon-link" href="<?php echo esc_url( $compare_url ); ?>" aria-label="مقایسه محصولات">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7h12l-3-3M17 17H5l3 3"/></svg>
            </a>

            <?php if ( function_exists( 'wc_get_page_permalink' ) ) : ?>
                <a class="icon-link account-link" href="<?php echo esc_url( wc_get_page_permalink( 'myaccount' ) ); ?>" aria-label="حساب کاربری">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/></svg>
                </a>

                <a class="icon-link" href="<?php echo esc_url( wc_get_cart_url() ); ?>" aria-label="سبد خرید">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 8a3 3 0 0 1 6 0"/></svg>
                    <span class="header-count gramiss-cart-count"><?php echo esc_html( gramiss_cart_count() ); ?></span>
                </a>
            <?php endif; ?>
        </div>
    </div>
</header>

<div id="gramiss-mobile-panel" class="mobile-panel" aria-hidden="true">
    <button class="mobile-panel-backdrop" type="button" aria-label="بستن منو"></button>
    <div class="mobile-panel-content" role="dialog" aria-modal="true" aria-label="منوی Gramiss">
        <div class="mobile-panel-head">
            <span class="wordmark">GRAMISS</span>
            <button class="menu-close icon-link" type="button" aria-label="بستن">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
            </button>
        </div>

        <nav aria-label="منوی موبایل">
            <?php
            wp_nav_menu(
                array(
                    'theme_location' => 'primary',
                    'container'      => false,
                    'fallback_cb'    => 'gramiss_primary_fallback',
                )
            );
            ?>
        </nav>

        <div class="mobile-panel-actions">
            <a class="g1-btn g1-btn-dark" href="<?php echo esc_url( $shop_url ); ?>">ورود به فروشگاه</a>
            <a class="g1-btn g1-btn-ghost" href="<?php echo esc_url( $wishlist_url ); ?>">علاقه‌مندی‌ها</a>
        </div>
    </div>
</div>

<div class="search-overlay" aria-hidden="true">
    <div class="search-dialog" role="dialog" aria-modal="true" aria-label="جست‌وجوی محصولات">
        <div class="search-dialog-head">
            <div>
                <small>SEARCH GRAMISS</small>
                <strong>دنبال چه چیزی می‌گردی؟</strong>
            </div>
            <button class="search-close icon-link" type="button" aria-label="بستن جست‌وجو">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
            </button>
        </div>
        <?php get_product_search_form(); ?>
        <div class="search-dialog-hints">
            <span>کلاه</span><span>کیف</span><span>جوراب</span><span>راهنمای انتخاب</span>
        </div>
    </div>
</div>

<?php
function gramiss_primary_fallback(): void {
    $shop = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
    echo '<ul>';
    echo '<li><a href="' . esc_url( $shop ) . '">Shop</a></li>';
    echo '<li><a href="' . esc_url( home_url( '/#collections' ) ) . '">Collections</a></li>';
    echo '<li><a href="' . esc_url( home_url( '/#journal' ) ) . '">Journal</a></li>';
    echo '<li><a href="' . esc_url( home_url( '/#smart-guide' ) ) . '">Smart Guide</a></li>';
    echo '</ul>';
}
