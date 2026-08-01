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

    add_image_size( 'gramiss-hero', 1800, 1020, false );
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
    wp_enqueue_style(
        'gramiss-interactive-hero',
        get_template_directory_uri() . '/assets/css/interactive-hero.css',
        array( 'gramiss-v1' ),
        gramiss_asset_version( '/assets/css/interactive-hero.css', $ver )
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
    wp_enqueue_script(
        'gramiss-interactive-hero',
        get_template_directory_uri() . '/assets/js/interactive-hero.js',
        array( 'gramiss-v1' ),
        gramiss_asset_version( '/assets/js/interactive-hero.js', $ver ),
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
 * A canonical shop URL that keeps Gramiss filters intact on plain permalinks.
 *
 * @param array<string,string> $args Optional query arguments.
 */
function gramiss_filterable_shop_url( array $args = array() ): string {
    $url = add_query_arg( 'post_type', 'product', home_url( '/' ) );
    return $args ? add_query_arg( $args, $url ) : $url;
}

/**
 * Launch categories used before matching WooCommerce terms are published.
 *
 * @return array<string,string>
 */
function gramiss_launch_categories(): array {
    return array(
        't-shirts' => 'تیشرت',
        'pants'    => 'شلوار',
        'caps'     => 'کلاه',
        'bags'     => 'کیف',
        'sneakers' => 'کتونی',
        'socks'    => 'جوراب',
        'belts'    => 'کمربند',
        'shirts'   => 'پیراهن',
        'underwear' => 'لباس زیر',
        'keychains' => 'جاکلیدی',
    );
}

/**
 * Resolve a WooCommerce product-category URL using several possible slugs/names.
 * Falls back to a filtered shop URL until the real category exists.
 *
 * @param array<int,string> $candidates Possible slugs or names.
 * @param string            $fallback_slug Query-string fallback.
 */
function gramiss_product_category_url( array $candidates, string $fallback_slug ): string {
    if ( taxonomy_exists( 'product_cat' ) ) {
        foreach ( $candidates as $candidate ) {
            $term = get_term_by( 'slug', sanitize_title( $candidate ), 'product_cat' );
            if ( ! $term ) {
                $term = get_term_by( 'name', $candidate, 'product_cat' );
            }
            if ( $term && ! is_wp_error( $term ) ) {
                $url = get_term_link( $term );
                if ( ! is_wp_error( $url ) ) {
                    return (string) $url;
                }
            }
        }
    }

    return gramiss_filterable_shop_url( array( 'gramiss_category' => $fallback_slug ) );
}

/**
 * Return real WooCommerce categories and fill missing slots with launch categories.
 *
 * @return array<int,array<string,string>>
 */
function gramiss_home_categories( int $limit = 10 ): array {
    $catalog = array(
        array( 'name' => 'تیشرت', 'en' => 'T-SHIRTS', 'slug' => 't-shirts', 'candidates' => array( 't-shirts', 't-shirt', 'tshirt', 'تی‌شرت', 'تیشرت' ) ),
        array( 'name' => 'شلوار', 'en' => 'PANTS', 'slug' => 'pants', 'candidates' => array( 'pants', 'trousers', 'شلوار' ) ),
        array( 'name' => 'کلاه', 'en' => 'CAPS', 'slug' => 'caps', 'candidates' => array( 'caps', 'cap', 'hats', 'hat', 'کلاه' ) ),
        array( 'name' => 'کیف', 'en' => 'BAGS', 'slug' => 'bags', 'candidates' => array( 'bags', 'bag', 'کیف' ) ),
        array( 'name' => 'کتونی', 'en' => 'SNEAKERS', 'slug' => 'sneakers', 'candidates' => array( 'sneakers', 'sneaker', 'shoes', 'کتونی', 'کفش' ) ),
        array( 'name' => 'جوراب', 'en' => 'SOCKS', 'slug' => 'socks', 'candidates' => array( 'socks', 'sock', 'جوراب' ) ),
        array( 'name' => 'کمربند', 'en' => 'BELTS', 'slug' => 'belts', 'candidates' => array( 'belts', 'belt', 'کمربند' ) ),
        array( 'name' => 'پیراهن', 'en' => 'SHIRTS', 'slug' => 'shirts', 'candidates' => array( 'shirts', 'shirt', 'پیراهن' ) ),
        array( 'name' => 'لباس زیر', 'en' => 'UNDERWEAR', 'slug' => 'underwear', 'candidates' => array( 'underwear', 'under-wear', 'لباس-زیر', 'لباس زیر' ) ),
        array( 'name' => 'جاکلیدی', 'en' => 'KEYCHAINS', 'slug' => 'keychains', 'candidates' => array( 'keychains', 'keychain', 'key-chains', 'جاکلیدی' ) ),
    );

    $results = array();
    foreach ( array_slice( $catalog, 0, max( 0, $limit ) ) as $item ) {
        $item['url'] = gramiss_product_category_url( $item['candidates'], $item['slug'] );
        unset( $item['candidates'] );
        $results[] = $item;
    }

    return $results;
}

/**
 * Return the compact outline icon used by the home category directory.
 */
function gramiss_home_category_icon( string $slug ): string {
    $icons = array(
        't-shirts' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4 5 5.5 2.5 9l3 2L7 9v11h10V9l1.5 2 3-2L19 5.5 16 4c-.8 1.3-2.2 2-4 2S8.8 5.3 8 4Z"/></svg>',
        'pants' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3h8l1 16-4 2-1-10-1 10-4-2L8 3Z"/><path d="M8 7h8"/></svg>',
        'caps' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 13c0-4.2 2.7-7 7-7s7 2.8 7 7H5Z"/><path d="M12 6v7M5 13c-2.3 0-3 1.1-3 2 0 1.1 1.7 1.7 4 1.2l6-1.7"/></svg>',
        'bags' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h16l-1 12H5L4 8Z"/><path d="M8 9V7a4 4 0 0 1 8 0v2"/></svg>',
        'sneakers' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 14 2-6 5 5 7 2c2 .6 3 2 2 4H5c-2 0-3-3-1-5Z"/><path d="m8 12 2-2m2 4 1.5-2M4 17h16"/></svg>',
        'socks' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3h7v8c0 2 2 3 3 4 2 2 .5 6-3 6h-2c-2 0-3-1-3-3 0-1 .5-2 1.5-3L8 13V3Z"/><path d="M8 7h7"/></svg>',
        'belts' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9h8v6H3V9Zm10 1h8v4h-8"/><path d="M6 12h3m9-2v4"/></svg>',
        'shirts' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 4-4 2-2 4 4 2v8h12v-8l4-2-2-4-4-2c-.5 1.2-2 2-4 2S8.5 5.2 8 4Z"/><path d="M12 6v14m0-10h.01m0 4h.01"/></svg>',
        'underwear' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16l-1 6c-.5 4-3 7-7 8-4-1-6.5-4-7-8L4 7Z"/><path d="m9 8 3 5 3-5"/></svg>',
        'keychains' => '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="8" r="4"/><path d="m11 11 10 10m-4-4 2-2m-5-1 2-2"/></svg>',
    );

    return $icons[ $slug ] ?? $icons['keychains'];
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
                'label'       => __( 'تصویر Hero تعاملی', 'gramiss' ),
                'description' => __( 'یک تصویر افقی 16:9 با شش گروه کلاه، کیف، جوراب، تیشرت، کتونی و شلوار.', 'gramiss' ),
                'section'     => 'gramiss_home',
            )
        )
    );
}
add_action( 'customize_register', 'gramiss_customize_register' );
