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

    add_image_size( 'gramiss-hero', 1200, 1400, false );
    add_image_size( 'gramiss-product-card', 720, 900, false );
    add_image_size( 'gramiss-category', 900, 900, false );

    register_nav_menus(
        array(
            'primary' => __( 'منوی اصلی', 'gramiss' ),
            'footer'  => __( 'منوی فوتر', 'gramiss' ),
        )
    );
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
        array( 'jquery' ),
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

    wp_localize_script(
        'gramiss-v1',
        'gramissV1',
        array(
            'ajaxUrl' => admin_url( 'admin-ajax.php' ),
            'homeUrl' => home_url( '/' ),
            'shopUrl' => function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' ),
        )
    );
}
add_action( 'wp_enqueue_scripts', 'gramiss_assets' );

function gramiss_body_classes( array $classes ): array {
    $classes[] = 'gramiss-rtl';
    $classes[] = 'gramiss-v1';
    $classes[] = 'gramiss-next-staging';

    if ( class_exists( 'WooCommerce' ) ) {
        $classes[] = 'gramiss-woocommerce-active';
    }

    return $classes;
}
add_filter( 'body_class', 'gramiss_body_classes' );

function gramiss_cart_count(): int {
    return function_exists( 'WC' ) && WC()->cart ? (int) WC()->cart->get_cart_contents_count() : 0;
}

function gramiss_cart_count_fragment( array $fragments ): array {
    ob_start();
    ?>
    <span class="header-count gramiss-cart-count"><?php echo esc_html( gramiss_cart_count() ); ?></span>
    <?php
    $fragments['span.gramiss-cart-count'] = ob_get_clean();
    return $fragments;
}
add_filter( 'woocommerce_add_to_cart_fragments', 'gramiss_cart_count_fragment' );

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

    return is_array( $products ) ? $products : array();
}

function gramiss_home_hero_product(): ?WC_Product {
    $products = gramiss_featured_products( 1 );
    return ! empty( $products ) && $products[0] instanceof WC_Product ? $products[0] : null;
}

function gramiss_home_hero_image(): string {
    $custom = get_theme_mod( 'gramiss_hero_image' );
    if ( $custom ) {
        return esc_url( $custom );
    }

    $product = gramiss_home_hero_product();
    if ( $product ) {
        $image = wp_get_attachment_image_url( $product->get_image_id(), 'gramiss-hero' );
        if ( $image ) {
            return esc_url( $image );
        }
    }

    return '';
}

/**
 * Return real WooCommerce categories and fill missing slots with launch categories.
 *
 * @return array<int,array<string,string>>
 */
function gramiss_home_categories( int $limit = 5 ): array {
    $results  = array();
    $fallback = array(
        array( 'name' => 'کلاه', 'en' => 'CAPS', 'slug' => 'caps', 'description' => 'جزئی کوچک با اثر بزرگ', 'mark' => 'C' ),
        array( 'name' => 'کیف', 'en' => 'BAGS', 'slug' => 'bags', 'description' => 'فرم کاربردی برای هر روز', 'mark' => 'B' ),
        array( 'name' => 'جوراب', 'en' => 'SOCKS', 'slug' => 'socks', 'description' => 'جزئیات ساده، انتخاب دقیق', 'mark' => 'S' ),
        array( 'name' => 'تیشرت', 'en' => 'T-SHIRTS', 'slug' => 't-shirts', 'description' => 'پایه‌ای برای ترکیب‌های بی‌نهایت', 'mark' => 'T' ),
        array( 'name' => 'کتونی', 'en' => 'SNEAKERS', 'slug' => 'sneakers', 'description' => 'حرکت، راحتی و استایل', 'mark' => 'SN' ),
    );

    if ( taxonomy_exists( 'product_cat' ) ) {
        $terms = get_terms(
            array(
                'taxonomy'   => 'product_cat',
                'hide_empty' => true,
                'number'     => $limit,
                'orderby'    => 'count',
                'order'      => 'DESC',
            )
        );

        if ( ! is_wp_error( $terms ) ) {
            foreach ( $terms as $term ) {
                $thumbnail_id = (int) get_term_meta( $term->term_id, 'thumbnail_id', true );
                $image        = $thumbnail_id ? wp_get_attachment_image_url( $thumbnail_id, 'gramiss-category' ) : '';
                $url          = get_term_link( $term );

                $results[] = array(
                    'name'        => $term->name,
                    'en'          => strtoupper( (string) $term->slug ),
                    'slug'        => (string) $term->slug,
                    'description' => $term->description ? wp_strip_all_tags( $term->description ) : __( 'انتخاب‌های دقیق برای استایل روزمره', 'gramiss' ),
                    'mark'        => strtoupper( substr( (string) $term->slug, 0, 2 ) ),
                    'image'       => $image ? (string) $image : '',
                    'url'         => is_wp_error( $url ) ? '' : (string) $url,
                );
            }
        }
    }

    $shop_url = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
    foreach ( $fallback as $item ) {
        if ( count( $results ) >= $limit ) {
            break;
        }

        $already_used = array_filter(
            $results,
            static fn( array $category ): bool => $category['slug'] === $item['slug'] || $category['name'] === $item['name']
        );
        if ( $already_used ) {
            continue;
        }

        $item['image'] = '';
        $item['url']   = add_query_arg( 'product_cat', $item['slug'], $shop_url );
        $results[]     = $item;
    }

    return array_slice( $results, 0, $limit );
}

function gramiss_customize_register( WP_Customize_Manager $wp_customize ): void {
    $wp_customize->add_section(
        'gramiss_home',
        array(
            'title'    => __( 'تنظیمات صفحه اصلی Gramiss', 'gramiss' ),
            'priority' => 30,
        )
    );

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
