<?php
/**
 * Gramiss 1.0 front page.
 *
 * @package Gramiss
 */
defined( 'ABSPATH' ) || exit;

get_header();

$shop_url     = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$hero_product = gramiss_home_hero_product();
$hero_img     = gramiss_home_hero_image();
$featured     = gramiss_featured_products( 8 );
$categories   = gramiss_home_categories( 10 );
$hero_objects = array(
    array(
        'class'  => 'is-hat',
        'depth'  => '1.18',
        'number' => '01',
        'label'  => 'کلاه',
        'url'    => gramiss_product_category_url( array( 'caps', 'cap', 'کلاه' ), 'caps' ),
    ),
    array(
        'class'  => 'is-shirt',
        'depth'  => '0.82',
        'number' => '02',
        'label'  => 'تیشرت',
        'url'    => gramiss_product_category_url( array( 't-shirts', 'tshirt', 'تی‌شرت', 'تیشرت' ), 't-shirts' ),
    ),
    array(
        'class'  => 'is-pants',
        'depth'  => '0.96',
        'number' => '03',
        'label'  => 'شلوار',
        'url'    => gramiss_product_category_url( array( 'pants', 'trousers', 'شلوار' ), 'pants' ),
    ),
    array(
        'class'  => 'is-bag',
        'depth'  => '1.12',
        'number' => '04',
        'label'  => 'کیف',
        'url'    => gramiss_product_category_url( array( 'bags', 'bag', 'کیف' ), 'bags' ),
    ),
    array(
        'class'  => 'is-socks',
        'depth'  => '1.24',
        'number' => '05',
        'label'  => 'جوراب',
        'url'    => gramiss_product_category_url( array( 'socks', 'sock', 'جوراب' ), 'socks' ),
    ),
    array(
        'class'  => 'is-sneakers',
        'depth'  => '1.32',
        'number' => '06',
        'label'  => 'کتونی',
        'url'    => gramiss_product_category_url( array( 'sneakers', 'shoes', 'کتونی', 'کفش' ), 'sneakers' ),
    ),
);
?>
<main id="primary" class="g1-home">
    <section class="g1-hero g1-reveal" aria-labelledby="g1-hero-title">
        <div class="g1-hero-copy">
            <p class="g1-kicker">GRAMISS / INTELLIGENT COMMERCE</p>
            <h1 id="g1-hero-title">کمتر حدس بزن،<br>بهتر انتخاب کن.</h1>
            <p class="g1-hero-lead">فروشگاه پوشیدنی‌های مردانه با راهنمایی دقیق درباره جنس، کیفیت، کاربرد و تناسب؛ برای خریدی سریع‌تر، آرام‌تر و مطمئن‌تر.</p>

            <div class="g1-actions">
                <a class="g1-btn g1-btn-dark" href="<?php echo esc_url( $shop_url ); ?>">ورود به فروشگاه</a>
                <a class="g1-btn g1-btn-ghost" href="#smart-guide">راهنمای هوشمند</a>
            </div>

            <div class="g1-proof" aria-label="مزیت‌های Gramiss">
                <div><strong>انتخاب آگاهانه</strong><span>جنس، دوام و کاربرد واقعی</span></div>
                <div><strong>مسیر کوتاه خرید</strong><span>بدون شلوغی و فشار تصمیم</span></div>
                <div><strong>پشتیبانی از استایل</strong><span>پیشنهاد متناسب با نیاز تو</span></div>
            </div>
        </div>

        <div class="g1-hero-media">
            <?php if ( $hero_img ) : ?>
                <div class="g1-interactive-hero" data-g1-interactive-hero style="<?php echo esc_attr( '--hero-image:url("' . esc_url_raw( $hero_img ) . '")' ); ?>">
                    <div class="g1-interactive-stage">
                        <div class="g1-interactive-shadow" aria-hidden="true"></div>
                        <div class="g1-interactive-art">
                            <img class="g1-interactive-base" src="<?php echo esc_url( $hero_img ); ?>" alt="مجموعه معلق Gramiss شامل کلاه، تیشرت، شلوار، کیف، جوراب و کتونی" fetchpriority="high" decoding="async">
                            <span class="g1-interactive-glow" aria-hidden="true"></span>

                            <?php foreach ( $hero_objects as $object ) : ?>
                                <a class="g1-hero-object <?php echo esc_attr( $object['class'] ); ?>" href="<?php echo esc_url( $object['url'] ); ?>" data-depth="<?php echo esc_attr( $object['depth'] ); ?>" aria-label="مشاهده دسته‌بندی <?php echo esc_attr( $object['label'] ); ?>">
                                    <span class="g1-object-visual" aria-hidden="true">
                                        <img class="g1-object-image" src="<?php echo esc_url( $hero_img ); ?>" alt="" decoding="async">
                                    </span>
                                    <span class="g1-object-label" aria-hidden="true">
                                        <small><?php echo esc_html( $object['number'] ); ?></small>
                                        <strong><?php echo esc_html( $object['label'] ); ?></strong>
                                    </span>
                                </a>
                            <?php endforeach; ?>
                        </div>
                        <div class="g1-interaction-hint" aria-hidden="true">با موس نزدیک شو و دسته را انتخاب کن</div>
                    </div>
                </div>
            <?php else : ?>
                <div class="g1-hero-placeholder" aria-hidden="true"><span>G</span><strong>GRAMISS</strong></div>
            <?php endif; ?>
        </div>
    </section>

    <section class="g1-signal-strip" aria-label="ویژگی‌های خدمات Gramiss">
        <div><span>01</span><strong>ارسال به سراسر ایران</strong></div>
        <div><span>02</span><strong>اطلاعات شفاف محصول</strong></div>
        <div><span>03</span><strong>انتخاب بدون قضاوت</strong></div>
        <div><span>04</span><strong>پشتیبانی قبل از خرید</strong></div>
    </section>

    <section class="g1-section g1-reveal" id="collections">
        <div class="g1-section-head">
            <div>
                <small>SHOP BY CATEGORY</small>
                <h2>از چیزی که واقعاً نیاز داری شروع کن.</h2>
            </div>
            <a class="g1-text-link" href="<?php echo esc_url( $shop_url ); ?>">همه دسته‌بندی‌ها</a>
        </div>

        <div class="g1-category-grid">
            <?php foreach ( $categories as $index => $category ) : ?>
                <a class="g1-category" href="<?php echo esc_url( $category['url'] ?: $shop_url ); ?>" aria-label="مشاهده دسته‌بندی <?php echo esc_attr( $category['name'] ); ?>">
                    <div class="g1-category-top">
                        <span class="g1-category-icon"><?php echo gramiss_home_category_icon( $category['slug'] ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></span>
                        <span class="g1-category-index"><?php echo esc_html( str_pad( (string) ( $index + 1 ), 2, '0', STR_PAD_LEFT ) ); ?></span>
                    </div>
                    <div class="g1-category-copy">
                        <span class="g1-category-en"><?php echo esc_html( $category['en'] ); ?></span>
                        <h3><?php echo esc_html( $category['name'] ); ?></h3>
                    </div>
                    <span class="g1-category-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7 17 17 7M8 7h9v9"/></svg></span>
                </a>
            <?php endforeach; ?>
        </div>
    </section>

    <section class="g1-products g1-reveal" id="products">
        <div class="g1-products-inner">
            <div class="g1-section-head">
                <div>
                    <small>GRAMISS SELECTS</small>
                    <h2 id="g1-products-title">انتخاب‌های تازه.</h2>
                </div>
                <a class="g1-text-link" href="<?php echo esc_url( $shop_url ); ?>">مشاهده فروشگاه</a>
            </div>

            <div class="g1-product-carousel<?php echo count( $featured ) < 2 ? ' is-single' : ''; ?>" role="region" aria-roledescription="کاروسل" aria-labelledby="g1-products-title" data-g1-product-carousel>
                <div class="g1-product-grid" role="list" tabindex="0" aria-label="محصولات منتخب Gramiss" data-g1-carousel-track>
                    <?php if ( ! empty( $featured ) ) : ?>
                        <?php foreach ( $featured as $product_index => $product ) : ?>
                            <article class="g1-product-card" role="listitem" data-g1-carousel-card aria-label="محصول <?php echo esc_attr( (string) ( $product_index + 1 ) ); ?> از <?php echo esc_attr( (string) count( $featured ) ); ?>">
                                <a class="g1-product-media" href="<?php echo esc_url( $product->get_permalink() ); ?>">
                                    <?php if ( $product->is_on_sale() ) : ?>
                                        <span class="g1-product-badge">تخفیف</span>
                                    <?php endif; ?>
                                    <?php echo wp_kses_post( $product->get_image( 'gramiss-product-card', array( 'loading' => 'lazy', 'decoding' => 'async' ) ) ); ?>
                                </a>
                                <div class="g1-product-info">
                                    <div class="g1-product-meta">
                                        <span><?php echo wp_kses_post( wc_get_product_category_list( $product->get_id(), '، ' ) ); ?></span>
                                        <span class="<?php echo $product->is_in_stock() ? 'is-in-stock' : 'is-out-of-stock'; ?>"><?php echo $product->is_in_stock() ? 'موجود' : 'ناموجود'; ?></span>
                                    </div>
                                    <h3><a href="<?php echo esc_url( $product->get_permalink() ); ?>"><?php echo esc_html( $product->get_name() ); ?></a></h3>
                                    <div class="g1-product-bottom">
                                        <div class="g1-product-price"><?php echo wp_kses_post( $product->get_price_html() ); ?></div>
                                        <a class="g1-product-arrow" href="<?php echo esc_url( $product->get_permalink() ); ?>" aria-label="مشاهده <?php echo esc_attr( $product->get_name() ); ?>">↗</a>
                                    </div>
                                </div>
                            </article>
                        <?php endforeach; ?>
                    <?php else : ?>
                        <div class="g1-empty-state">
                            <small>PRODUCTS ARE COMING</small>
                            <h3>محصولات واقعی ووکامرس اینجا نمایش داده می‌شوند.</h3>
                            <p>با انتشار اولین محصولات، این بخش به‌صورت خودکار کامل می‌شود.</p>
                        </div>
                    <?php endif; ?>
                </div>
                <?php if ( count( $featured ) > 1 ) : ?>
                    <div class="g1-product-carousel-controls" aria-label="کنترل انتخاب‌های تازه">
                        <button type="button" class="g1-carousel-button" data-g1-carousel-prev aria-label="محصول قبلی">
                            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
                        </button>
                        <p class="g1-carousel-status" aria-live="polite"><span data-g1-carousel-current>01</span><i>/</i><span><?php echo esc_html( str_pad( (string) count( $featured ), 2, '0', STR_PAD_LEFT ) ); ?></span></p>
                        <button type="button" class="g1-carousel-button" data-g1-carousel-next aria-label="محصول بعدی">
                            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>
                        </button>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </section>

    <section class="g1-section g1-reveal" id="smart-guide">
        <div class="g1-smart">
            <div class="g1-smart-copy">
                <small>GRAMISS SMART GUIDE</small>
                <h2>فروشنده‌ای آرام، دقیق و بی‌قضاوت.</h2>
                <p>به‌جای صدها انتخاب پراکنده، چند سؤال درست درباره کاربرد، بودجه، فرم و سلیقه می‌پرسیم تا مسیر خرید به گزینه‌های واقعاً مناسب محدود شود.</p>
                <div class="g1-smart-points">
                    <span>شناخت نیاز</span>
                    <span>مقایسه شفاف</span>
                    <span>پیشنهاد قابل توضیح</span>
                </div>
                <div class="g1-actions">
                    <a class="g1-btn g1-btn-light" href="<?php echo esc_url( $shop_url ); ?>">شروع انتخاب</a>
                </div>
            </div>
            <div class="g1-smart-visual" aria-hidden="true">
                <div class="g1-orbit"><span>G</span></div>
                <p>DECISION / CLARITY / CONFIDENCE</p>
            </div>
        </div>
    </section>

    <section class="g1-section g1-reveal" id="journal">
        <div class="g1-section-head">
            <div>
                <small>GRAMISS JOURNAL</small>
                <h2>قبل از خرید، بهتر بدان.</h2>
            </div>
            <span class="g1-section-note">دانش کاربردی، کوتاه و قابل استفاده</span>
        </div>

        <div class="g1-editorial-grid">
            <article class="g1-story" data-index="01">
                <small>MATERIAL GUIDE</small>
                <h3>چطور کیفیت پارچه را قبل از خرید تشخیص دهیم؟</h3>
                <p>نشانه‌های ساده‌ای که کمک می‌کنند محصولی انتخاب کنی که بعد از استفاده و شست‌وشو ارزشش را حفظ کند.</p>
            </article>
            <article class="g1-story" data-index="02">
                <small>FIT GUIDE</small>
                <h3>قواره و سایز یک چیز نیستند.</h3>
                <p>تفاوت اصلی را بفهم تا انتخاب دقیق‌تری داشته باشی.</p>
            </article>
            <article class="g1-story" data-index="03">
                <small>STYLE GUIDE</small>
                <h3>جزئیات کوچک، تفاوت بزرگ.</h3>
                <p>کلاه، جوراب و کیف چطور استایل را کامل می‌کنند؟</p>
            </article>
        </div>
    </section>
</main>
<?php get_footer(); ?>
