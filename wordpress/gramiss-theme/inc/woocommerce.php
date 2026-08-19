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

function gramiss_shop_product_query( $query ): void {
    if ( ! $query instanceof WP_Query ) {
        return;
    }
    if ( is_admin() || ! ( is_shop() || is_product_taxonomy() ) ) {
        return;
    }

    $tax_query  = (array) $query->get( 'tax_query' );
    $meta_query = (array) $query->get( 'meta_query' );

    $selected_category = '';
    if ( ! empty( $_GET['gramiss_category'] ) ) {
        $selected_category = sanitize_title( wp_unslash( $_GET['gramiss_category'] ) );
    } elseif ( ! empty( $_GET['product_cat'] ) ) {
        $selected_category = sanitize_title( wp_unslash( $_GET['product_cat'] ) );
    }

    if ( $selected_category ) {
        $tax_query[] = array(
            'taxonomy' => 'product_cat',
            'field'    => 'slug',
            'terms'    => $selected_category,
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

/* GRAMISS CART SUCCESS START */
function gramiss_add_to_cart_message_html( $message, $products, $show_qty ) {
    if ( empty( $products ) || ! function_exists( 'wc_get_product' ) ) {
        return $message;
    }

    $titles = array();
    foreach ( (array) $products as $product_id => $qty ) {
        $product = wc_get_product( $product_id );
        if ( ! $product ) {
            continue;
        }

        $title = wp_strip_all_tags( $product->get_name() );
        if ( $show_qty && absint( $qty ) > 1 ) {
            $title = absint( $qty ) . ' × ' . $title;
        }
        $titles[] = $title;
    }

    if ( empty( $titles ) ) {
        return $message;
    }

    $title_text = implode( '، ', $titles );
    $cart_url   = function_exists( 'wc_get_cart_url' ) ? wc_get_cart_url() : '#';

    return sprintf(
        '<div class="gramiss-cart-success" dir="rtl"><span class="gramiss-cart-success__check" aria-hidden="true"><span class="gramiss-cart-success__tick">✓</span></span><span class="gramiss-cart-success__copy"><strong>«%1$s» به سبد خرید شما اضافه شد.</strong><span>محصول با موفقیت به سبد خرید شما افزوده شد.</span></span><a href="%2$s" class="button wc-forward gramiss-cart-success__cta">مشاهده سبد خرید <span class="gramiss-cart-success__arrow" aria-hidden="true">←</span></a></div>',
        esc_html( $title_text ),
        esc_url( $cart_url )
    );
}
add_filter( 'wc_add_to_cart_message_html', 'gramiss_add_to_cart_message_html', 20, 3 );

function gramiss_cart_success_assets(): void {
    if ( ! function_exists( 'is_product' ) || ! is_product() ) {
        return;
    }

    $css = <<<'CSS'
body.single-product .woocommerce-message:has(.gramiss-cart-success){margin:16px auto 18px!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;overflow:visible!important}
body.single-product .woocommerce-message:has(.gramiss-cart-success)::before{display:none!important}
.gramiss-cart-success{position:relative;isolation:isolate;width:100%;min-height:118px;display:flex;flex-direction:row;direction:rtl;align-items:center;gap:24px;padding:22px 26px 22px 28px;border:1px solid rgba(13,16,21,.10);border-radius:20px;background:linear-gradient(105deg,rgba(255,255,255,.97) 0%,rgba(251,249,244,.98) 58%,rgba(248,246,239,.98) 100%);box-shadow:0 18px 46px rgba(13,16,21,.11),0 1px 0 rgba(255,255,255,.9) inset;overflow:hidden;animation:gramiss-success-card-in .48s cubic-bezier(.2,.8,.2,1) both}
.gramiss-cart-success::before{content:"";position:absolute;z-index:-1;top:0;right:0;width:4px;height:100%;background:linear-gradient(180deg,#76d9a8 0%,#2dac72 52%,#55c990 100%)}
.gramiss-cart-success::after{content:"";position:absolute;z-index:-1;right:-34px;top:50%;width:190px;height:190px;border-radius:50%;background:radial-gradient(circle,rgba(73,190,126,.15) 0%,rgba(73,190,126,0) 69%);transform:translateY(-50%);pointer-events:none}
.gramiss-cart-success__check{position:relative;flex:0 0 64px;width:64px;height:64px;border-radius:50%;display:grid;place-items:center;color:#fff;background:linear-gradient(145deg,#66cb95 0%,#2aa76e 100%);box-shadow:0 10px 24px rgba(42,167,110,.28),0 0 0 8px rgba(91,199,143,.08);animation:gramiss-success-check-pop .68s cubic-bezier(.16,1.25,.32,1) .12s both}
.gramiss-cart-success__check::before,.gramiss-cart-success__check::after{position:absolute;color:#d6c56d;line-height:1;text-shadow:0 2px 8px rgba(197,176,68,.22);animation:gramiss-success-sparkle 1.05s ease-out .35s both}
.gramiss-cart-success__check::before{content:"✦";font-size:15px;right:-13px;top:-9px}
.gramiss-cart-success__check::after{content:"✦";font-size:10px;left:-9px;bottom:-3px;animation-delay:.52s}
.gramiss-cart-success__tick{display:block;font:700 33px/1 Arial,sans-serif;transform-origin:center;animation:gramiss-success-tick-in .38s cubic-bezier(.2,1.4,.4,1) .34s both}
.gramiss-cart-success__copy{min-width:0;flex:1 1 auto;display:flex;flex-direction:column;gap:7px;text-align:right}
.gramiss-cart-success__copy strong{display:block;color:#0d1015;font-size:clamp(16px,1.45vw,21px);line-height:1.8;font-weight:850}
.gramiss-cart-success__copy>span{display:block;color:#6f747d;font-size:12px;line-height:1.9}
.woocommerce .gramiss-cart-success__cta.button,.gramiss-cart-success__cta{flex:0 0 auto;min-width:238px;min-height:58px;margin:0!important;padding:0 24px!important;border:0!important;border-radius:999px!important;display:inline-flex!important;align-items:center;justify-content:center;gap:12px;background:linear-gradient(180deg,#161a20 0%,#0b0e12 100%)!important;color:#fff!important;font-size:13px!important;font-weight:800!important;text-decoration:none!important;box-shadow:0 10px 24px rgba(13,16,21,.18);transition:transform .22s ease,box-shadow .22s ease,background .22s ease!important}
.woocommerce .gramiss-cart-success__cta.button:hover,.gramiss-cart-success__cta:hover{background:linear-gradient(180deg,#20252d 0%,#11151a 100%)!important;transform:translateY(-2px)!important;box-shadow:0 14px 30px rgba(13,16,21,.22)}
.gramiss-cart-success__arrow{display:inline-block;font-size:17px;transition:transform .22s ease}.gramiss-cart-success__cta:hover .gramiss-cart-success__arrow{transform:translateX(-4px)}
@keyframes gramiss-success-card-in{0%{opacity:0;transform:translateY(-10px) scale(.986)}100%{opacity:1;transform:translateY(0) scale(1)}}
@keyframes gramiss-success-check-pop{0%{opacity:0;transform:scale(.34) rotate(-18deg)}58%{opacity:1;transform:scale(1.12) rotate(4deg)}78%{transform:scale(.96) rotate(-2deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
@keyframes gramiss-success-tick-in{0%{opacity:0;transform:scale(.35) rotate(-22deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
@keyframes gramiss-success-sparkle{0%{opacity:0;transform:scale(.25) rotate(-20deg)}55%{opacity:1;transform:scale(1.2) rotate(12deg)}100%{opacity:.85;transform:scale(1) rotate(0)}}
@media(max-width:780px){body.single-product .woocommerce-message:has(.gramiss-cart-success){margin:12px auto 16px!important}.gramiss-cart-success{min-height:0;flex-wrap:wrap;gap:14px 16px;padding:18px;border-radius:18px}.gramiss-cart-success__check{flex-basis:52px;width:52px;height:52px;box-shadow:0 8px 20px rgba(42,167,110,.25),0 0 0 6px rgba(91,199,143,.07)}.gramiss-cart-success__tick{font-size:27px}.gramiss-cart-success__copy{flex-basis:calc(100% - 70px)}.gramiss-cart-success__copy strong{font-size:14px;line-height:1.8}.gramiss-cart-success__copy>span{font-size:11px}.woocommerce .gramiss-cart-success__cta.button,.gramiss-cart-success__cta{order:3;flex:1 0 100%;width:100%;min-width:0;min-height:52px;font-size:12px!important}}
@media(prefers-reduced-motion:reduce){.gramiss-cart-success,.gramiss-cart-success__check,.gramiss-cart-success__tick,.gramiss-cart-success__check::before,.gramiss-cart-success__check::after{animation:none!important}}
CSS;

    wp_add_inline_style( 'gramiss-v1', $css );
}
add_action( 'wp_enqueue_scripts', 'gramiss_cart_success_assets', 35 );
/* GRAMISS CART SUCCESS END */
