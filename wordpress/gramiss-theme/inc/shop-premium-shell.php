<?php
/**
 * Premium visual shell for the live WooCommerce shop.
 * Keeps the existing product-card and image dimensions untouched.
 *
 * @package Gramiss
 */
defined( 'ABSPATH' ) || exit;

if ( ! function_exists( 'gramiss_shop_premium_is_catalog' ) ) {
    function gramiss_shop_premium_is_catalog(): bool {
        return function_exists( 'is_shop' ) && (
            is_shop() ||
            ( function_exists( 'is_product_taxonomy' ) && is_product_taxonomy() ) ||
            is_post_type_archive( 'product' ) ||
            ( is_search() && 'product' === get_query_var( 'post_type' ) )
        );
    }
}

if ( ! function_exists( 'gramiss_shop_premium_hero' ) ) {
    function gramiss_shop_premium_hero(): void {
        if ( ! gramiss_shop_premium_is_catalog() ) {
            return;
        }

        $title = 'فروشگاه';
        if ( function_exists( 'is_product_category' ) && is_product_category() ) {
            $term = get_queried_object();
            if ( $term instanceof WP_Term ) {
                $title = $term->name;
            }
        }
        ?>
        <section class="gramiss-shop-premium-hero" aria-labelledby="gramiss-premium-shop-title" dir="rtl">
            <div class="gramiss-shop-premium-hero__copy">
                <span class="gramiss-shop-premium-hero__eyebrow" dir="ltr">GRAMISS / CURATED SHOP</span>
                <h1 id="gramiss-premium-shop-title"><?php echo esc_html( $title ); ?></h1>
                <p>منتخب محصولات باکیفیت برای استایل‌های ماندگار، کاربردی و امروزی.</p>
            </div>
            <div class="gramiss-shop-premium-hero__mark" aria-hidden="true">G</div>
            <div class="gramiss-shop-premium-hero__threads" aria-hidden="true"></div>
        </section>
        <?php
    }
    add_action( 'woocommerce_before_shop_loop', 'gramiss_shop_premium_hero', 1 );
}

if ( ! function_exists( 'gramiss_shop_premium_controls_open' ) ) {
    function gramiss_shop_premium_controls_open(): void {
        if ( gramiss_shop_premium_is_catalog() ) {
            echo '<section class="gramiss-shop-control-shell" aria-label="کنترل‌های فروشگاه">';
        }
    }
    add_action( 'woocommerce_before_shop_loop', 'gramiss_shop_premium_controls_open', 5 );
}

if ( ! function_exists( 'gramiss_shop_premium_filter_trigger' ) ) {
    function gramiss_shop_premium_filter_trigger(): void {
        if ( ! gramiss_shop_premium_is_catalog() ) {
            return;
        }
        ?>
        <button class="gramiss-shop-filter-trigger" type="button" aria-controls="gramiss-shop-filter-drawer" aria-expanded="false">
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 7h10M18 7h2M10 17h10M4 17h2M14 4v6M10 14v6"/></svg>
            <span>فیلترها</span>
        </button>
        <?php
    }
    add_action( 'woocommerce_before_shop_loop', 'gramiss_shop_premium_filter_trigger', 18 );
}

if ( ! function_exists( 'gramiss_shop_premium_controls_close' ) ) {
    function gramiss_shop_premium_controls_close(): void {
        if ( gramiss_shop_premium_is_catalog() ) {
            echo '</section>';
        }
    }
    add_action( 'woocommerce_before_shop_loop', 'gramiss_shop_premium_controls_close', 99 );
}

if ( ! function_exists( 'gramiss_shop_premium_filter_drawer' ) ) {
    function gramiss_shop_premium_filter_drawer(): void {
        if ( ! gramiss_shop_premium_is_catalog() ) {
            return;
        }

        $shop_url  = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/?post_type=product' );
        $min_price = isset( $_GET['min_price'] ) ? absint( $_GET['min_price'] ) : '';
        $max_price = isset( $_GET['max_price'] ) ? absint( $_GET['max_price'] ) : '';
        $orderby   = isset( $_GET['orderby'] ) ? wc_clean( wp_unslash( $_GET['orderby'] ) ) : '';
        ?>
        <div class="gramiss-shop-filter-overlay" aria-hidden="true">
            <aside id="gramiss-shop-filter-drawer" class="gramiss-shop-filter-drawer" role="dialog" aria-modal="true" aria-labelledby="gramiss-shop-filter-title" dir="rtl">
                <div class="gramiss-shop-filter-drawer__head">
                    <div><span dir="ltr">REFINE / SHOP</span><h2 id="gramiss-shop-filter-title">فیلتر محصولات</h2></div>
                    <button type="button" class="gramiss-shop-filter-close" aria-label="بستن فیلترها">×</button>
                </div>
                <form class="gramiss-shop-filter-form" method="get" action="<?php echo esc_url( $shop_url ); ?>">
                    <fieldset>
                        <legend>محدوده قیمت</legend>
                        <div class="gramiss-shop-price-fields">
                            <label><span>از</span><input type="number" min="0" step="10000" name="min_price" value="<?php echo esc_attr( $min_price ); ?>" placeholder="۵۰۰٬۰۰۰"></label>
                            <label><span>تا</span><input type="number" min="0" step="10000" name="max_price" value="<?php echo esc_attr( $max_price ); ?>" placeholder="۵٬۰۰۰٬۰۰۰"></label>
                        </div>
                    </fieldset>
                    <fieldset>
                        <legend>وضعیت محصول</legend>
                        <label class="gramiss-shop-filter-check"><input type="checkbox" name="in_stock" value="1" <?php checked( ! empty( $_GET['in_stock'] ) ); ?>><span>فقط کالاهای موجود</span></label>
                        <label class="gramiss-shop-filter-check"><input type="checkbox" name="on_sale" value="1" <?php checked( ! empty( $_GET['on_sale'] ) ); ?>><span>فقط محصولات تخفیف‌دار</span></label>
                    </fieldset>
                    <?php if ( $orderby ) : ?><input type="hidden" name="orderby" value="<?php echo esc_attr( $orderby ); ?>"><?php endif; ?>
                    <div class="gramiss-shop-filter-actions">
                        <a href="<?php echo esc_url( $shop_url ); ?>">پاک کردن</a>
                        <button type="submit">اعمال فیلترها</button>
                    </div>
                </form>
            </aside>
        </div>
        <?php
    }
    add_action( 'wp_footer', 'gramiss_shop_premium_filter_drawer', 35 );
}
