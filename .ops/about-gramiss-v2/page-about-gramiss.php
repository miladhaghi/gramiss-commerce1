<?php
/**
 * Gramiss About page — premium editorial redesign.
 * Slug: /about-gramiss/
 * Marker: GRAMISS_ABOUT_V2
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

wp_enqueue_style(
    'gramiss-about-v2',
    get_stylesheet_directory_uri() . '/assets/css/about-gramiss-v2.css',
    array(),
    '2.1.0'
);

get_header();

$shop_url = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
if ( ! $shop_url ) {
    $shop_url = home_url( '/shop/' );
}
$contact_url = home_url( '/contact/' );
$smart_url   = home_url( '/smart-guide/' );
?>

<main id="primary" class="gabout" data-gramiss-about="v2" dir="rtl">
    <!-- GRAMISS_ABOUT_V2 -->

    <section class="gabout-hero" aria-labelledby="gabout-title">
        <div class="gabout-shell gabout-hero__grid">
            <div class="gabout-hero__copy">
                <p class="gabout-eyebrow">درباره گرامیس</p>
                <h1 id="gabout-title">کمتر حدس بزن،<br>بهتر انتخاب کن.</h1>
                <p class="gabout-lead">
                    Gramiss برای خرید پوشاکی ساخته شده که تصمیم‌گیری در آن ساده‌تر، شفاف‌تر و آگاهانه‌تر باشد؛
                    از خود محصول تا راهنمای انتخاب و استایل.
                </p>
                <div class="gabout-actions">
                    <a class="gabout-btn gabout-btn--dark" href="<?php echo esc_url( $shop_url ); ?>">
                        <span>مشاهده فروشگاه</span><span class="gabout-arrow" aria-hidden="true">↗</span>
                    </a>
                    <a class="gabout-btn gabout-btn--light" href="<?php echo esc_url( $contact_url ); ?>">پشتیبانی و تماس</a>
                </div>
            </div>

            <div class="gabout-hero__visual" aria-hidden="true">
                <div class="gabout-visual__arch"></div>
                <div class="gabout-rack">
                    <span class="gabout-rack__bar"></span>
                    <span class="gabout-rack__leg gabout-rack__leg--a"></span>
                    <span class="gabout-rack__leg gabout-rack__leg--b"></span>
                    <span class="gabout-garment gabout-garment--dark"></span>
                    <span class="gabout-garment gabout-garment--light"></span>
                </div>
                <div class="gabout-orbit gabout-orbit--one"></div>
                <div class="gabout-orbit gabout-orbit--two"></div>
                <div class="gabout-gmark">G</div>
                <p class="gabout-manifesto">BETTER<br>CHOICES<br>A BRIGHTER<br>YOU</p>
                <div class="gabout-visual__tags">
                    <span>استایل</span><span>کیفیت</span><span>اعتماد</span>
                </div>
            </div>
        </div>
    </section>

    <section class="gabout-story">
        <div class="gabout-shell gabout-story__grid">
            <div class="gabout-story__title">
                <p class="gabout-eyebrow gabout-eyebrow--en">WHAT GRAMISS IS</p>
                <h2>فقط یک ویترین<br>محصول نیست.</h2>
            </div>
            <div class="gabout-story__body">
                <p>
                    هدف Gramiss این است که قبل از خرید، اطلاعاتی که واقعاً به تصمیم کمک می‌کند در دسترس باشد:
                    فیت، کاربرد، جنس، نگهداری، ترکیب استایل و تفاوت گزینه‌ها. محصول باید دیده شود، اما انتخاب باید فهمیده شود.
                </p>
                <div class="gabout-story__note"><span></span> انتخاب آگاهانه، استایل بهتر</div>
            </div>
        </div>
    </section>

    <section class="gabout-principles" aria-labelledby="gabout-principles-title">
        <div class="gabout-shell">
            <div class="gabout-sectionhead">
                <div>
                    <p class="gabout-eyebrow gabout-eyebrow--en">OUR PRINCIPLES</p>
                    <h2 id="gabout-principles-title">سه اصل ساده.</h2>
                </div>
                <p>چیزی که تجربه Gramiss را از فروشگاه‌های شلوغ و فشارمحور جدا می‌کند.</p>
            </div>

            <div class="gabout-cards">
                <article class="gabout-card">
                    <div class="gabout-card__top"><span class="gabout-icon">◌</span><span class="gabout-index">01</span></div>
                    <h3>انتخاب آگاهانه</h3>
                    <p>اطلاعات کاربردی قبل از خرید، به توضیحات طولانی و مبهم پایان می‌دهد.</p>
                </article>
                <article class="gabout-card">
                    <div class="gabout-card__top"><span class="gabout-icon">□</span><span class="gabout-index">02</span></div>
                    <h3>محصول واقعی</h3>
                    <p>جزئیات محصول، موجودی و مشخصات باید تا جای ممکن دقیق و قابل اتکا باشند.</p>
                </article>
                <article class="gabout-card">
                    <div class="gabout-card__top"><span class="gabout-icon">○</span><span class="gabout-index">03</span></div>
                    <h3>بدون فشار</h3>
                    <p>مسیر خرید کوتاه و روشن باشد و کاربر برای تصمیم‌گیری تحت فشار قرار نگیرد.</p>
                </article>
            </div>
        </div>
    </section>

    <section class="gabout-guide" aria-labelledby="gabout-guide-title">
        <div class="gabout-shell gabout-guide__grid">
            <div class="gabout-guide__copy">
                <p class="gabout-eyebrow gabout-eyebrow--en">GRAMISS SMART GUIDE</p>
                <h2 id="gabout-guide-title">راهنما، قبل از فروش.</h2>
                <p>
                    Smart Guide قرار است با چند سؤال درباره نیاز، بودجه، فرم و سلیقه، گزینه‌های مناسب‌تر را محدود کند.
                    نقش آن کمک به تصمیم است؛ نه جایگزین کردن انتخاب کاربر.
                </p>
                <a class="gabout-textlink" href="<?php echo esc_url( $smart_url ); ?>">دیدن Smart Guide <span aria-hidden="true">↗</span></a>
            </div>

            <div class="gabout-guide__panel">
                <article class="gabout-step">
                    <span class="gabout-step__icon">⌕</span>
                    <div><h3>شناخت نیاز</h3><p>نیاز و موقعیت خود را بهتر بشناسید.</p></div>
                    <span class="gabout-index">01</span>
                </article>
                <article class="gabout-step">
                    <span class="gabout-step__icon">≍</span>
                    <div><h3>مقایسه شفاف</h3><p>گزینه‌ها را با اطلاعات دقیق مقایسه کنید.</p></div>
                    <span class="gabout-index">02</span>
                </article>
                <article class="gabout-step">
                    <span class="gabout-step__icon">☆</span>
                    <div><h3>پیشنهاد قابل توضیح</h3><p>پیشنهادهایی که منطق و دلیل دارند.</p></div>
                    <span class="gabout-index">03</span>
                </article>
            </div>
        </div>
    </section>

    <section class="gabout-cta">
        <div class="gabout-shell gabout-cta__inner">
            <div class="gabout-cta__copy">
                <p class="gabout-eyebrow gabout-eyebrow--en">NEXT</p>
                <h2>از چیزی که واقعاً نیاز داری شروع کن.</h2>
                <a class="gabout-btn gabout-btn--dark" href="<?php echo esc_url( $shop_url ); ?>">
                    <span>ورود به فروشگاه</span><span class="gabout-arrow" aria-hidden="true">↗</span>
                </a>
            </div>
            <div class="gabout-cta__art" aria-hidden="true">
                <div class="gabout-block gabout-block--one"></div>
                <div class="gabout-block gabout-block--two"></div>
                <div class="gabout-fold"></div>
                <p>GOOD<br>CLOTHES<br>BRIGHTER<br>DAYS</p>
            </div>
        </div>
    </section>
</main>

<?php get_footer();
