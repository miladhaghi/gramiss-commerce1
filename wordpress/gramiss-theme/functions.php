<?php
/**
 * Gramiss theme bootstrap.
 *
 * @package Gramiss
 */

defined( 'ABSPATH' ) || exit;

function gramiss_setup(): void {
    load_theme_textdomain( 'gramiss', get_template_directory() . '/languages' );

    add_theme_support( 'title-tag' );
    add_theme_support( 'post-thumbnails' );
    add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );
    add_theme_support( 'woocommerce' );
    add_theme_support( 'wc-product-gallery-zoom' );
    add_theme_support( 'wc-product-gallery-lightbox' );
    add_theme_support( 'wc-product-gallery-slider' );

    register_nav_menus(
        array(
            'primary' => __( 'Primary Menu', 'gramiss' ),
            'footer'  => __( 'Footer Menu', 'gramiss' ),
        )
    );
}
add_action( 'after_setup_theme', 'gramiss_setup' );

function gramiss_assets(): void {
    $theme = wp_get_theme();

    wp_enqueue_style(
        'gramiss-style',
        get_stylesheet_uri(),
        array(),
        $theme->get( 'Version' )
    );
}
add_action( 'wp_enqueue_scripts', 'gramiss_assets' );

function gramiss_body_classes( array $classes ): array {
    $classes[] = 'gramiss-rtl';

    if ( class_exists( 'WooCommerce' ) ) {
        $classes[] = 'gramiss-woocommerce-active';
    }

    return $classes;
}
add_filter( 'body_class', 'gramiss_body_classes' );
