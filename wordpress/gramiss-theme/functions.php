<?php
/**
 * Gramiss theme bootstrap.
 *
 * @package Gramiss
 */
defined( 'ABSPATH' ) || exit;

require_once get_template_directory() . '/inc/woocommerce.php';

function gramiss_setup(): void {
    load_theme_textdomain( 'gramiss', get_template_directory() . '/languages' );
    add_theme_support( 'title-tag' );
    add_theme_support( 'post-thumbnails' );
    add_theme_support( 'responsive-embeds' );
    add_theme_support( 'align-wide' );
    add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );
    add_theme_support( 'custom-logo', array( 'height' => 80, 'width' => 260, 'flex-height' => true, 'flex-width' => true ) );
    add_theme_support( 'woocommerce' );
    add_theme_support( 'wc-product-gallery-zoom' );
    add_theme_support( 'wc-product-gallery-lightbox' );
    add_theme_support( 'wc-product-gallery-slider' );
    register_nav_menus( array( 'primary' => __( 'منوی اصلی', 'gramiss' ), 'footer' => __( 'منوی فوتر', 'gramiss' ) ) );
}
add_action( 'after_setup_theme', 'gramiss_setup' );

function gramiss_asset_version( string $relative_path, string $fallback ): string {
    $path = get_template_directory() . $relative_path;
    return file_exists( $path ) ? (string) filemtime( $path ) : $fallback;
}

function gramiss_assets(): void {
    $theme = wp_get_theme();
    $ver   = (string) $theme->get( 'Version' );

    wp_enqueue_style( 'gramiss-style', get_stylesheet_uri(), array(), $ver );
    wp_enqueue_style(
        'gramiss-theme',
        get_template_directory_uri() . '/assets/css/theme.css',
        array( 'gramiss-style' ),
        gramiss_asset_version( '/assets/css/theme.css', $ver )
    );
    wp_enqueue_style(
        'gramiss-v1',
        get_template_directory_uri() . '/assets/css/gramiss-1.css',
        array( 'gramiss-theme' ),
        gramiss_asset_version( '/assets/css/gramiss-1.css', $ver )
    );

    wp_enqueue_script(
        'gramiss-theme',
        get_template_directory_uri() . '/assets/js/theme.js',
        array(),
        gramiss_asset_version( '/assets/js/theme.js', $ver ),
        true
    );
    wp_enqueue_script(
        'gramiss-v1',
        get_template_directory_uri() . '/assets/js/gramiss-1.js',
        array( 'gramiss-theme' ),
        gramiss_asset_version( '/assets/js/gramiss-1.js', $ver ),
        true
    );
}
add_action( 'wp_enqueue_scripts', 'gramiss_assets' );

function gramiss_body_classes( array $classes ): array {
    $classes[] = 'gramiss-rtl';
    $classes[] = 'gramiss-v1';
    if ( class_exists( 'WooCommerce' ) ) {
        $classes[] = 'gramiss-woocommerce-active';
    }
    return $classes;
}
add_filter( 'body_class', 'gramiss_body_classes' );

function gramiss_cart_count(): int {
    return function_exists( 'WC' ) && WC()->cart ? (int) WC()->cart->get_cart_contents_count() : 0;
}

function gramiss_featured_products( int $limit = 4 ): array {
    if ( ! function_exists( 'wc_get_products' ) ) {
        return array();
    }

    $products = wc_get_products(
        array(
            'status'   => 'publish',
            'limit'    => $limit,
            'featured' => true,
            'orderby'  => 'date',
            'order'    => 'DESC',
        )
    );

    if ( count( $products ) < $limit ) {
        $products = wc_get_products(
            array(
                'status'  => 'publish',
                'limit'   => $limit,
                'orderby' => 'date',
                'order'   => 'DESC',
            )
        );
    }

    return $products;
}

function gramiss_home_hero_image(): string {
    $custom = get_theme_mod( 'gramiss_hero_image' );
    if ( $custom ) {
        return esc_url( $custom );
    }

    if ( function_exists( 'wc_get_products' ) ) {
        $products = wc_get_products( array( 'status' => 'publish', 'limit' => 1, 'featured' => true ) );
        if ( empty( $products ) ) {
            $products = wc_get_products( array( 'status' => 'publish', 'limit' => 1, 'orderby' => 'date', 'order' => 'DESC' ) );
        }
        if ( ! empty( $products ) ) {
            $image = wp_get_attachment_image_url( $products[0]->get_image_id(), 'full' );
            if ( $image ) {
                return esc_url( $image );
            }
        }
    }

    return '';
}

function gramiss_customize_register( WP_Customize_Manager $wp_customize ): void {
    $wp_customize->add_section( 'gramiss_home', array( 'title' => __( 'تنظیمات صفحه اصلی Gramiss', 'gramiss' ), 'priority' => 30 ) );
    $wp_customize->add_setting( 'gramiss_hero_image', array( 'sanitize_callback' => 'esc_url_raw' ) );
    $wp_customize->add_control(
        new WP_Customize_Image_Control(
            $wp_customize,
            'gramiss_hero_image',
            array(
                'label'   => __( 'تصویر اصلی Hero', 'gramiss' ),
                'section' => 'gramiss_home',
            )
        )
    );
}
add_action( 'customize_register', 'gramiss_customize_register' );
