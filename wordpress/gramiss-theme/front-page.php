<?php
/** Front page. @package Gramiss */
defined( 'ABSPATH' ) || exit;
get_header();

$shop_url = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$hero_img = gramiss_home_hero_image();
$featured = gramiss_featured_products( 4 );
$hero_product = ! empty( $featured ) ? $featured[0] : null;

$categories = array(
    array( '01', 'کلاه', 'CAPS', 'جزئی کوچک با اثر بزرگ', 'C' ),
    array( '02', 'کیف', 'BAGS', 'فرم کاربردی برای هر روز', 'B' ),
    array( '03', 'جوراب', 'SOCKS', 'جزئیات ساده، انتخاب دقیق', 'S' ),
    array( '04', 'تیشرت', 'T-SHIRTS', 'پایه‌ای برای ترکیب‌های بی‌نهایت', 'T' ),
    array( '05', 'کتونی', 'SNEAKERS', 'حرکت، راحتی و استایل', 'SN' ),
);
?>
<main id="primary" class="g1-home">
    <section class="g1-hero" aria-labelledby="g1-hero-title">
        <div class="g1-hero-copy">
            <p class="g1-kicker">GRAMISS / INTELLIGENT COMMERCE</p>
            <h1 id="g1-hero-title">کمتر حدس بزن،<br>بهتر انتخاب کن.</h1>
            <p class="g1-hero-lead">Gramiss فقط محصول نشان نمی‌دهد؛ کمک می‌کند جنس، کیفیت، کاربرد و انتخاب مناسب را قبل از خرید بهتر بفهمی.</p>
            <div class="g1-actions">
                <a class="g1-btn g1-btn-dark" href="<?php echo esc_url( $shop_url ); ?>">شروع خرید</a>
                <a class="g1-btn g1-btn-ghost" href="#smart-guide">راهنمای هوشمند</a>
            </div>
            <div class="g1-proof">
                <div><strong>خرید آگاهانه</strong><span>جنس، کیفیت و کاربرد</span></div>
                <div><strong>بدون فشار</strong><span>مسیر کوتاه و شفاف</span></div>
                <div><strong>برای استایل واقعی</strong><span>نه فقط ترندهای زودگذر</span></div>
            </div>
        </div>
        <div class="g1-hero-media">
            <?php if ( $hero_img ) : ?>
                <img src="<?php echo esc_url( $hero_img ); ?>" alt="محصول منتخب Gramiss" fetchpriority="high">
            <?php else : ?>
                <span class="wordmark" style="font-size:44px">GRAMISS</span>
            <?php endif; ?>
            <div class="g1-floating-card">
                <small>CURATED OBJECT</small>
                <strong><?php echo $hero_product ? esc_html( $hero_product->get_name() ) : 'انتخاب منتخب Gramiss'; ?></strong>
                <span><?php echo $hero_product ? wp_kses_post( $hero_product->get_price_html() ) : 'برای استایل روزمره و انتخاب دقیق‌تر'; ?></span>
            </div>
        </div>
    </section>

    <section class="g1-section g1-reveal" id="collections">
        <div class="g1-section-head">
            <div><small>SHOP BY CATEGORY</small><h2>از چیزی که واقعاً نیاز داری شروع کن.</h2></div>
            <a class="g1-text-link" href="<?php echo esc_url( $shop_url ); ?>">همه دسته‌ها</a>
        </div>
        <div class="g1-category-grid">
            <?php foreach ( $categories as $category ) : ?>
                <a class="g1-category" href="<?php echo esc_url( $shop_url ); ?>">
                    <span class="g1-category-index"><?php echo esc_html( $category[0] ); ?></span>
                    <span class="g1-category-mark"><?php echo esc_html( $category[4] ); ?></span>
                    <div>
                        <span class="g1-category-en"><?php echo esc_html( $category[2] ); ?></span>
                        <h3><?php echo esc_html( $category[1] ); ?></h3>
                        <p><?php echo esc_html( $category[3] ); ?></p>
                    </div>
                </a>
            <?php endforeach; ?>
        </div>
    </section>

    <section class="g1-products g1-reveal" id="products">
        <div class="g1-products-inner">
            <div class="g1-section-head">
                <div><small>GRAMISS SELECTS</small><h2>انتخاب‌های تازه.</h2></div>
                <a class="g1-text-link" href="<?php echo esc_url( $shop_url ); ?>">مشاهده فروشگاه</a>
            </div>
            <div class="g1-product-grid">
                <?php if ( ! empty( $featured ) ) : ?>
                    <?php foreach ( $featured as $product ) : ?>
                        <article class="g1-product-card">
                            <a class="g1-product-media" href="<?php echo esc_url( $product->get_permalink() ); ?>">
                                <?php if ( $product->is_on_sale() ) : ?><span class="g1-product-badge">تخفیف</span><?php endif; ?>
                                <?php echo wp_kses_post( $product->get_image( 'woocommerce_single' ) ); ?>
                            </a>
                            <div class="g1-product-info">
                                <div class="g1-product-meta"><span><?php echo wp_kses_post( wc_get_product_category_list( $product->get_id(), '، ' ) ); ?></span><span><?php echo $product->is_in_stock() ? 'موجود' : 'ناموجود'; ?></span></div>
                                <h3><a href="<?php echo esc_url( $product->get_permalink() ); ?>"><?php echo esc_html( $product->get_name() ); ?></a></h3>
                                <div class="g1-product-price"><?php echo wp_kses_post( $product->get_price_html() ); ?></div>
                            </div>
                        </article>
                    <?php endforeach; ?>
                <?php else : ?>
                    <p>با افزودن محصولات ووکامرس، انتخاب‌های تازه اینجا نمایش داده می‌شوند.</p>
                <?php endif; ?>
            </div>
        </div>
    </section>

    <section class="g1-section g1-reveal" id="smart-guide">
        <div class="g1-smart">
            <div class="g1-smart-copy">
                <small>GRAMISS SMART GUIDE</small>
                <h2>یک فروشنده آرام، دقیق و بی‌قضاوت.</h2>
                <p>راهنمای هوشمند Gramiss قرار است به‌جای شلوغ‌کردن مسیر خرید، چند سؤال درست بپرسد و انتخاب‌ها را به چیزی که واقعاً به کارت می‌آید محدود کند.</p>
                <div class="g1-actions" style="margin-top:18px"><a class="g1-btn g1-btn-ghost" style="color:#fff;border-color:rgba(255,255,255,.3)" href="<?php echo esc_url( $shop_url ); ?>">دیدن انتخاب‌ها</a></div>
            </div>
            <div class="g1-smart-visual" aria-hidden="true"><div class="g1-orbit"></div></div>
        </div>
    </section>

    <section class="g1-section g1-reveal" id="journal">
        <div class="g1-section-head">
            <div><small>GRAMISS JOURNAL</small><h2>قبل از خرید، بهتر بدان.</h2></div>
        </div>
        <div class="g1-editorial-grid">
            <article class="g1-story" data-index="01"><small>MATERIAL GUIDE</small><h3>چطور کیفیت پارچه را قبل از خرید تشخیص دهیم؟</h3><p>چند نشانه ساده برای انتخابی که بعد از شست‌وشو هم ارزشش را حفظ کند.</p></article>
            <article class="g1-story" data-index="02"><small>FIT GUIDE</small><h3>قواره و سایز، یک چیز نیستند.</h3><p>فرق اصلی را بفهم تا انتخاب دقیق‌تری داشته باشی.</p></article>
            <article class="g1-story" data-index="03"><small>STYLE GUIDE</small><h3>جزئیات کوچک، تفاوت بزرگ.</h3><p>کلاه، جوراب و کیف چطور استایل را کامل می‌کنند؟</p></article>
        </div>
    </section>
</main>
<?php get_footer(); ?>
