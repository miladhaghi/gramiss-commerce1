<?php
/** WooCommerce integration. @package Gramiss */
defined( 'ABSPATH' ) || exit;

function gramiss_woocommerce_setup(): void {
    remove_action( 'woocommerce_before_main_content', 'woocommerce_output_content_wrapper', 10 );
    remove_action( 'woocommerce_after_main_content', 'woocommerce_output_content_wrapper_end', 10 );
    remove_action( 'woocommerce_sidebar', 'woocommerce_get_sidebar', 10 );
}
add_action( 'after_setup_theme', 'gramiss_woocommerce_setup' );

function gramiss_wc_wrapper_start(): void { echo '<main id="primary" class="content-area">'; }
add_action( 'woocommerce_before_main_content', 'gramiss_wc_wrapper_start', 10 );

function gramiss_wc_wrapper_end(): void { echo '</main>'; }
add_action( 'woocommerce_after_main_content', 'gramiss_wc_wrapper_end', 10 );

add_filter( 'loop_shop_columns', static fn(): int => 4 );
add_filter( 'loop_shop_per_page', static fn(): int => 12 );

function gramiss_cart_fragments( array $fragments ): array {
    ob_start();
    ?><span class="header-count gramiss-cart-count"><?php echo esc_html( gramiss_cart_count() ); ?></span><?php
    $fragments['.gramiss-cart-count'] = ob_get_clean();
    return $fragments;
}
add_filter( 'woocommerce_add_to_cart_fragments', 'gramiss_cart_fragments' );
