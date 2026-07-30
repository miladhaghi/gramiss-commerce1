<?php
/** Front page. @package Gramiss */
defined( 'ABSPATH' ) || exit;
get_header();
$shop_url = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$hero_img = gramiss_home_hero_image();
$featured = gramiss_featured_products( 4 );
$reasons  = array(
    array( '01', 'راهنمای خرید واقعی', 'اطلاعات کاربردی درباره جنس، دوام، قواره و نحوه استفاده؛ درست در کنار محصول.' ),
    array( '02', 'انتخاب بدون فشار', 'مسیر خرید کوتاه و شفاف، بدون فروشندگی تهاجمی و بدون ترس از قضاوت شدن.' ),
    array( '03', 'کیفیت قبل از قیمت', 'تمرکز بر ارزش واقعی محصول و چیزی که بعد از خرید و استفاده برایت باقی می‌ماند.' ),
    array( '04', 'پیشنهاد هوشمند', 'زیرساختی برای پیشنهاد محصول متناسب با نیاز، استایل و موقعیت استفاده تو.' ),
);
$categories = array(
    array( '01', 'کتونی', 'SNEAKERS', 'حرکت، راحتی و استایل روزمره' ),
    array( '02', 'تیشرت', 'T-SHIRTS', 'پایه‌ای ساده برای ترکیب‌های بی‌نهایت' ),
    array( '03', 'کلاه', 'CAPS', 'جزئی کوچک با تأثیری بزرگ' ),
    array( '04', 'کیف', 'BAGS', 'کاربرد روزانه با فرم مینیمال' ),
);
$all_categories = array(
    array( '01', 'کیف', 'BAGS' ), array( '02', 'کلاه', 'CAPS' ), array( '03', 'کتونی', 'SNEAKERS' ), array( '04', 'جوراب', 'SOCKS' ), array( '05', 'تیشرت', 'T-SHIRTS' ), array( '06', 'پیراهن', 'SHIRTS' ), array( '07', 'شلوار', 'TROUSERS' ), array( '08', 'لباس زیر', 'UNDERWEAR' ), array( '09', 'کمربند', 'BELTS' ), array( '10', 'جاکلیدی', 'KEYCHAINS' ),
);
?>
<main id="primary">
<section class="hero home-section" aria-labelledby="hero-title">
    <div class="hero-copy">
        <p class="eyebrow-pill">انتخابی هوشمند برای استایل روزمره</p>
        <h1 id="hero-title">خرید پوشاک،<br>بدون تردید و حدس</h1>
        <p class="hero-description"><bdi dir="ltr">Gramiss</bdi> به تو کمک می‌کند جنس، کیفیت و انتخاب مناسب را قبل از خرید بهتر بفهمی؛ سریع، بی‌قضاوت و دقیق.</p>
        <div class="hero-actions"><a class="button button-primary" href="<?php echo esc_url( $shop_url ); ?>">شروع خرید</a><a class="button button-secondary" href="#journal">راهنمای انتخاب</a></div>
        <div class="hero-proof"><div><strong>۳ دسته اصلی</strong><span>کیف، جوراب، کلاه</span></div><div><strong>تصمیم سریع‌تر</strong><span>راهنمای خرید</span></div><div><strong>خرید مطمئن‌تر</strong><span>تمرکز بر کیفیت</span></div></div>
    </div>
    <div class="hero-visual"><?php if ( $hero_img ) : ?><img src="<?php echo esc_url( $hero_img ); ?>" alt="محصول منتخب Gramiss" fetchpriority="high"><?php else : ?><div class="footer-wordmark">GRAMISS</div><?php endif; ?></div>
</section>

<section class="featured home-section" id="shop">
    <div class="section-heading"><div><p>FEATURED CATEGORIES</p><h2>دسته‌هایی برای شروع استایل</h2></div><a href="<?php echo esc_url( $shop_url ); ?>">مشاهده همه دسته‌ها ←</a></div>
    <div class="featured-grid">
        <?php foreach ( $categories as $index => $category ) : ?>
            <a class="featured-category <?php echo 0 === $index ? 'is-dark' : ''; ?>" href="<?php echo esc_url( $shop_url ); ?>"><span class="card-index"><?php echo esc_html( $category[0] ); ?></span><span class="featured-artwork"><span class="footer-wordmark"><?php echo esc_html( mb_substr( $category[2], 0, 1 ) ); ?></span></span><span class="category-copy"><span class="latin-label" dir="ltr"><?php echo esc_html( $category[2] ); ?></span><strong><?php echo esc_html( $category[1] ); ?></strong><span><?php echo esc_html( $category[3] ); ?></span></span></a>
        <?php endforeach; ?>
    </div>
</section>

<section class="browse home-section" id="all-categories">
    <div class="browse-heading"><h2>همه دسته‌بندی‌ها</h2><p>از پوشاک اصلی تا جزئیات تکمیل‌کننده استایل</p></div>
    <div class="browse-grid"><?php foreach ( $all_categories as $category ) : ?><a class="browse-card" href="<?php echo esc_url( $shop_url ); ?>"><span class="browse-top" dir="ltr"><span><?php echo esc_html( $category[0] ); ?></span><span>↗</span></span><span class="browse-labels"><strong><?php echo esc_html( $category[1] ); ?></strong><span class="latin-label" dir="ltr"><?php echo esc_html( $category[2] ); ?></span></span></a><?php endforeach; ?></div>
</section>

<section class="products home-section" id="products">
    <div class="section-heading"><div><p>CURATED FOR GRAMISS</p><h2>محصولات منتخب</h2></div><a href="<?php echo esc_url( $shop_url ); ?>">مشاهده همه محصولات ←</a></div>
    <div class="products-grid">
        <?php if ( ! empty( $featured ) ) : foreach ( $featured as $product ) : ?>
            <article class="product-card"><a class="product-media" href="<?php echo esc_url( $product->get_permalink() ); ?>"><?php echo wp_kses_post( $product->get_image( 'woocommerce_thumbnail' ) ); ?></a><a class="product-info" href="<?php echo esc_url( $product->get_permalink() ); ?>"><span class="product-category"><?php echo wp_kses_post( wc_get_product_category_list( $product->get_id(), '، ' ) ); ?></span><strong><?php echo esc_html( $product->get_name() ); ?></strong><b><?php echo wp_kses_post( $product->get_price_html() ); ?></b></a></article>
        <?php endforeach; else : ?><p>پس از افزودن محصولات ووکامرس، محصولات منتخب اینجا نمایش داده می‌شوند.</p><?php endif; ?>
    </div>
</section>

<section class="campaign home-section" id="collections"><div class="campaign-content"><p class="campaign-label">GRAMISS / CAPSULE 01</p><h2><span>کالکشن شهری؛</span><span>کمتر انتخاب کن، بهتر بپوش</span></h2><p class="campaign-description">ترکیبی محدود از آیتم‌های کاربردی برای استایل روزمره؛ انتخاب‌هایی که راحت‌تر با هم هماهنگ می‌شوند.</p><a class="button button-secondary" href="<?php echo esc_url( $shop_url ); ?>">مشاهده کالکشن</a></div></section>

<section class="why home-section"><div class="section-heading"><div><p>WHY GRAMISS</p><h2>چرا Gramiss؟</h2></div></div><div class="reason-grid"><?php foreach ( $reasons as $reason ) : ?><article class="reason-card"><span><?php echo esc_html( $reason[0] ); ?></span><h3><?php echo esc_html( $reason[1] ); ?></h3><p><?php echo esc_html( $reason[2] ); ?></p></article><?php endforeach; ?></div></section>

<section class="journal home-section" id="journal"><div class="section-heading"><div><p>GRAMISS JOURNAL</p><h2>راهنمای انتخاب بهتر</h2></div></div><div class="journal-grid"><article class="journal-card"><small>GUIDE 01</small><h3>چطور کیفیت پارچه را قبل از خرید تشخیص دهیم؟</h3><p>راهنمای کوتاه و کاربردی برای انتخاب آگاهانه‌تر.</p></article><article class="journal-card"><small>GUIDE 02</small><h3>قواره و سایز؛ فرق اصلی کجاست؟</h3><p>اشتباه‌های رایج هنگام انتخاب اندازه.</p></article><article class="journal-card"><small>GUIDE 03</small><h3>کلاه مناسب فرم صورت</h3><p>چند اصل ساده برای انتخاب بهتر.</p></article></div></section>

<section class="newsletter home-section"><div><h2>انتخاب‌های بهتر، مستقیم در ایمیل تو</h2><p>راهنماها، کالکشن‌های تازه و پیشنهادهای Gramiss.</p></div><form action="" method="post"><label class="screen-reader-text" for="gramiss-email">ایمیل</label><input id="gramiss-email" name="email" type="email" placeholder="example@email.com"><button type="submit">عضویت</button></form></section>
</main>
<?php get_footer(); ?>
