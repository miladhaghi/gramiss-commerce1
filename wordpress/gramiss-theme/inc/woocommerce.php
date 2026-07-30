<?php
/** WooCommerce integration. @package Gramiss */
defined( 'ABSPATH' ) || exit;

function gramiss_woocommerce_setup(): void {
    remove_action( 'woocommerce_before_main_content', 'woocommerce_output_content_wrapper', 10 );
    remove_action( 'woocommerce_after_main_content', 'woocommerce_output_content_wrapper_end', 10 );
    remove_action( 'woocommerce_sidebar', 'woocommerce_get_sidebar', 10 );
}
add_action( 'after_setup_theme', 'gramiss_woocommerce_setup' );

add_filter( 'loop_shop_columns', static fn(): int => 3 );
add_filter( 'loop_shop_per_page', static fn(): int => 9 );

function gramiss_shop_product_query( WC_Query $query ): void {
    if ( is_admin() || ! ( is_shop() || is_product_taxonomy() ) ) {
        return;
    }

    $tax_query  = (array) $query->get( 'tax_query' );
    $meta_query = (array) $query->get( 'meta_query' );

    if ( ! empty( $_GET['product_cat'] ) ) {
        $tax_query[] = array(
            'taxonomy' => 'product_cat',
            'field'    => 'slug',
            'terms'    => sanitize_title( wp_unslash( $_GET['product_cat'] ) ),
        );
    }

    foreach ( array( 'color' => 'pa_color', 'size' => 'pa_size', 'material' => 'pa_material' ) as $key => $taxonomy ) {
        $query_key = 'filter_' . $key;
        if ( taxonomy_exists( $taxonomy ) && ! empty( $_GET[ $query_key ] ) ) {
            $tax_query[] = array(
                'taxonomy' => $taxonomy,
                'field'    => 'slug',
                'terms'    => array_map( 'sanitize_title', (array) wp_unslash( $_GET[ $query_key ] ) ),
                'operator' => 'IN',
            );
        }
    }

    $min_price = isset( $_GET['min_price'] ) && '' !== $_GET['min_price'] ? absint( $_GET['min_price'] ) : null;
    $max_price = isset( $_GET['max_price'] ) && '' !== $_GET['max_price'] ? absint( $_GET['max_price'] ) : null;
    if ( null !== $min_price || null !== $max_price ) {
        $meta_query[] = array(
            'key'     => '_price',
            'value'   => array( null === $min_price ? 0 : $min_price, null === $max_price ? PHP_INT_MAX : $max_price ),
            'compare' => 'BETWEEN',
            'type'    => 'NUMERIC',
        );
    }

    if ( ! empty( $_GET['in_stock'] ) ) {
        $meta_query[] = array( 'key' => '_stock_status', 'value' => 'instock' );
    }

    if ( ! empty( $_GET['on_sale'] ) ) {
        $sale_ids = wc_get_product_ids_on_sale();
        $query->set( 'post__in', empty( $sale_ids ) ? array( 0 ) : $sale_ids );
    }

    $query->set( 'tax_query', $tax_query );
    $query->set( 'meta_query', $meta_query );
}
add_action( 'woocommerce_product_query', 'gramiss_shop_product_query' );

function gramiss_cart_fragments( array $fragments ): array {
    ob_start();
    ?><span class="cart-count gramiss-cart-count"><?php echo esc_html( gramiss_cart_count() ); ?></span><?php
    $fragments['.gramiss-cart-count'] = ob_get_clean();
    return $fragments;
}
add_filter( 'woocommerce_add_to_cart_fragments', 'gramiss_cart_fragments' );
