<?php
/**
 * Gramiss PDP v2 — isolated product detail page.
 *
 * This template intentionally avoids WooCommerce's legacy div.product root
 * and FlexSlider gallery so older theme rules cannot collide with the PDP.
 *
 * @package Gramiss
 */
defined( 'ABSPATH' ) || exit;

get_header();
?>
<main id="primary" class="gramiss-pdp-v2" dir="rtl">
    <div class="g2-pdp-shell">
        <?php if ( function_exists( 'woocommerce_breadcrumb' ) ) : ?>
            <div class="g2-pdp-breadcrumb">
                <?php woocommerce_breadcrumb(); ?>
            </div>
        <?php endif; ?>

        <?php while ( have_posts() ) : the_post(); ?>
            <?php
            do_action( 'woocommerce_before_single_product' );

            if ( post_password_required() ) {
                echo get_the_password_form(); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
                continue;
            }

            global $product;
            $product = wc_get_product( get_the_ID() );

            if ( ! $product ) {
                continue;
            }

            $main_image_id = $product->get_image_id();
            $gallery_ids   = $product->get_gallery_image_ids();
            $image_ids     = array_values( array_unique( array_filter( array_merge( array( $main_image_id ), $gallery_ids ) ) ) );

            $fallback      = wc_placeholder_img_src( 'woocommerce_single' );
            $main_src      = $main_image_id ? wp_get_attachment_image_url( $main_image_id, 'woocommerce_single' ) : $fallback;
            $main_full     = $main_image_id ? wp_get_attachment_image_url( $main_image_id, 'full' ) : $fallback;
            $main_srcset   = $main_image_id ? wp_get_attachment_image_srcset( $main_image_id, 'woocommerce_single' ) : '';
            $main_alt      = $main_image_id ? get_post_meta( $main_image_id, '_wp_attachment_image_alt', true ) : get_the_title();
            $main_alt      = $main_alt ? $main_alt : get_the_title();
            $category_list = wc_get_product_category_list( $product->get_id(), '، ' );
            ?>

            <article class="g2-pdp" data-product-id="<?php echo esc_attr( $product->get_id() ); ?>">
                <section class="g2-pdp-top" aria-label="مشاهده و خرید محصول">
                    <div class="g2-pdp-buy">
                        <?php if ( $category_list ) : ?>
                            <div class="g2-pdp-eyebrow"><?php echo wp_kses_post( $category_list ); ?></div>
                        <?php endif; ?>

                        <h1 class="g2-pdp-title"><?php the_title(); ?></h1>

                        <?php if ( wc_review_ratings_enabled() && $product->get_rating_count() > 0 ) : ?>
                            <div class="g2-pdp-rating">
                                <?php echo wp_kses_post( wc_get_rating_html( $product->get_average_rating(), $product->get_rating_count() ) ); ?>
                                <span><?php echo esc_html( $product->get_rating_count() ); ?> نظر</span>
                            </div>
                        <?php endif; ?>

                        <div class="g2-pdp-price"><?php echo wp_kses_post( $product->get_price_html() ); ?></div>

                        <?php if ( has_excerpt() ) : ?>
                            <div class="g2-pdp-excerpt">
                                <?php echo wp_kses_post( apply_filters( 'woocommerce_short_description', get_the_excerpt() ) ); ?>
                            </div>
                        <?php endif; ?>

                        <div class="g2-pdp-cart">
                            <?php woocommerce_template_single_add_to_cart(); ?>
                        </div>

                        <div class="g2-pdp-meta">
                            <?php woocommerce_template_single_meta(); ?>
                        </div>

                        <div class="g2-pdp-promises" aria-label="مزایای خرید">
                            <div><strong>انتخاب دقیق‌تر</strong><span>اطلاعات واضح برای تصمیم بهتر</span></div>
                            <div><strong>ارسال سراسری</strong><span>پیگیری سفارش از حساب کاربری</span></div>
                            <div><strong>پشتیبانی خرید</strong><span>راهنمایی قبل از ثبت سفارش</span></div>
                        </div>
                    </div>

                    <div class="g2-pdp-gallery" aria-label="تصاویر محصول">
                        <div class="g2-pdp-stage">
                            <?php if ( $product->is_on_sale() ) : ?>
                                <span class="g2-pdp-sale">تخفیف</span>
                            <?php endif; ?>
                            <img
                                id="g2-pdp-main-image"
                                class="g2-pdp-main-image"
                                src="<?php echo esc_url( $main_src ); ?>"
                                <?php if ( $main_srcset ) : ?>srcset="<?php echo esc_attr( $main_srcset ); ?>"<?php endif; ?>
                                data-full="<?php echo esc_url( $main_full ); ?>"
                                alt="<?php echo esc_attr( $main_alt ); ?>"
                                loading="eager"
                                decoding="async"
                            />
                        </div>

                        <?php if ( count( $image_ids ) > 1 ) : ?>
                            <div class="g2-pdp-thumbs" role="list" aria-label="انتخاب تصویر">
                                <?php foreach ( $image_ids as $index => $image_id ) : ?>
                                    <?php
                                    $thumb_src    = wp_get_attachment_image_url( $image_id, 'woocommerce_thumbnail' );
                                    $display_src  = wp_get_attachment_image_url( $image_id, 'woocommerce_single' );
                                    $display_full = wp_get_attachment_image_url( $image_id, 'full' );
                                    $display_set  = wp_get_attachment_image_srcset( $image_id, 'woocommerce_single' );
                                    $display_alt  = get_post_meta( $image_id, '_wp_attachment_image_alt', true );
                                    $display_alt  = $display_alt ? $display_alt : get_the_title();
                                    ?>
                                    <button
                                        type="button"
                                        class="g2-pdp-thumb<?php echo 0 === $index ? ' is-active' : ''; ?>"
                                        data-g2-pdp-thumb
                                        data-src="<?php echo esc_url( $display_src ); ?>"
                                        data-full="<?php echo esc_url( $display_full ); ?>"
                                        data-srcset="<?php echo esc_attr( $display_set ); ?>"
                                        data-alt="<?php echo esc_attr( $display_alt ); ?>"
                                        aria-pressed="<?php echo 0 === $index ? 'true' : 'false'; ?>"
                                        role="listitem"
                                    >
                                        <img src="<?php echo esc_url( $thumb_src ); ?>" alt="" loading="lazy" decoding="async" />
                                    </button>
                                <?php endforeach; ?>
                            </div>
                        <?php endif; ?>
                    </div>
                </section>

                <section class="g2-pdp-details" aria-label="اطلاعات کامل محصول">
                    <?php woocommerce_output_product_data_tabs(); ?>
                </section>

                <section class="g2-pdp-related" aria-label="محصولات مرتبط">
                    <?php woocommerce_output_related_products(); ?>
                </section>
            </article>

            <?php do_action( 'woocommerce_after_single_product' ); ?>
        <?php endwhile; ?>
    </div>
</main>

<script>
(function () {
    'use strict';
    var root = document.querySelector('.gramiss-pdp-v2');
    if (!root) return;
    var main = root.querySelector('#g2-pdp-main-image');
    if (!main) return;

    root.addEventListener('click', function (event) {
        var thumb = event.target.closest('[data-g2-pdp-thumb]');
        if (!thumb || !root.contains(thumb)) return;

        var src = thumb.getAttribute('data-src');
        var srcset = thumb.getAttribute('data-srcset');
        var full = thumb.getAttribute('data-full');
        var alt = thumb.getAttribute('data-alt');

        if (src) main.src = src;
        if (srcset) main.srcset = srcset; else main.removeAttribute('srcset');
        if (full) main.setAttribute('data-full', full);
        if (alt) main.alt = alt;

        root.querySelectorAll('[data-g2-pdp-thumb]').forEach(function (button) {
            var active = button === thumb;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
    });
})();
</script>

<?php get_footer(); ?>
