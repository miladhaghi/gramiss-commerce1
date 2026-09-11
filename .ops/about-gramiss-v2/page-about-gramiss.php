<?php
/**
 * Gramiss About page — approved editorial art direction.
 * Slug: /about-gramiss/
 * Marker: GRAMISS_ABOUT_V3
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

wp_enqueue_style(
    'gramiss-about-v3',
    get_stylesheet_directory_uri() . '/assets/css/about-gramiss-v2.css',
    array(),
    '3.1.0'
);

get_header();

$shop_url = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
if ( ! $shop_url ) {
    $shop_url = home_url( '/shop/' );
}
$contact_url = home_url( '/contact/' );
$smart_url   = home_url( '/smart-guide/' );
?>

<main id="primary" class="gabout" data-gramiss-about="v3" dir="rtl">
    <!-- GRAMISS_ABOUT_V3 -->

    <section class="gabout-hero" aria-labelledby="gabout-title">
        <div class="gabout-hero__grid">
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
                <div class="gabout-hero__photo"></div>
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
        <div class="gabout-shell gabout-principles__layout">
            <div class="gabout-sectionhead">
                <div>
                    <p class="gabout-eyebrow gabout-eyebrow--en">OUR PRINCIPLES</p>
                    <h2 id="gabout-principles-title">سه اصل ساده.</h2>
                    <p class="gabout-sectionhead__copy">چیزی که تجربه Gramiss را از فروشگاه‌های شلوغ و فشارمحور جدا می‌کند.</p>
                </div>
            </div>

            <div class="gabout-cards">
                <article class="gabout-card">
                    <div class="gabout-card__top">
                        <span class="gabout-index">01</span>
                        <span class="gabout-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none"><path d="M9.5 4.5A2.5 2.5 0 0 0 7 7c0 .4.1.8.3 1.1A2.8 2.8 0 0 0 6 10.5c0 1 .5 2 1.3 2.5-.2.4-.3.8-.3 1.2A2.8 2.8 0 0 0 9.8 17H11V7a2.5 2.5 0 0 0-1.5-2.5Z"/><path d="M14.5 4.5A2.5 2.5 0 0 1 17 7c0 .4-.1.8-.3 1.1a2.8 2.8 0 0 1 1.3 2.4c0 1-.5 2-1.3 2.5.2.4.3.8.3 1.2a2.8 2.8 0 0 1-2.8 2.8H13V7a2.5 2.5 0 0 1 1.5-2.5Z"/><path d="M11 9H9M13 11h2M11 14H9M13 15h2"/></svg>
                        </span>
                    </div>
                    <h3>انتخاب آگاهانه</h3>
                    <p>اطلاعات کاربردی قبل از خرید، به توضیحات طولانی و مبهم پایان می‌دهد.</p>
                </article>
                <article class="gabout-card">
                    <div class="gabout-card__top">
                        <span class="gabout-index">02</span>
                        <span class="gabout-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none"><path d="m12 3 7 4-7 4-7-4 7-4Z"/><path d="m5 7 7 4 7-4v9l-7 4-7-4V7Z"/><path d="M12 11v9"/></svg>
                        </span>
                    </div>
                    <h3>محصول واقعی</h3>
                    <p>جزئیات محصول، موجودی و مشخصات باید تا جای ممکن دقیق و قابل اتکا باشند.</p>
                </article>
                <article class="gabout-card">
                    <div class="gabout-card__top">
                        <span class="gabout-index">03</span>
                        <span class="gabout-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="3"/><path d="M6 20v-2.5A4.5 4.5 0 0 1 10.5 13h3A4.5 4.5 0 0 1 18 17.5V20"/></svg>
                        </span>
                    </div>
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
                    <span class="gabout-step__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="6"/><path d="m16 16 4 4"/></svg></span>
                    <div><h3>شناخت نیاز</h3><p>نیاز و موقعیت خود را بهتر بشناسید.</p></div>
                    <span class="gabout-index">01</span>
                </article>
                <article class="gabout-step">
                    <span class="gabout-step__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M4 20h16M12 4v16M6 8h12M7 8 4 14h6L7 8Zm10 0-3 6h6l-3-6Z"/></svg></span>
                    <div><h3>مقایسه شفاف</h3><p>گزینه‌ها را با اطلاعات دقیق مقایسه کنید.</p></div>
                    <span class="gabout-index">02</span>
                </article>
                <article class="gabout-step">
                    <span class="gabout-step__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 2.4 4.9 5.4.8-3.9 3.8.9 5.4-4.8-2.6-4.8 2.6.9-5.4-3.9-3.8 5.4-.8L12 3Z"/></svg></span>
                    <div><h3>پیشنهاد قابل توضیح</h3><p>پیشنهادهایی که منطق و دلیل دارند.</p></div>
                    <span class="gabout-index">03</span>
                </article>
            </div>
        </div>
    </section>

    <section class="gabout-cta">
        <div class="gabout-cta__inner">
            <div class="gabout-cta__copy">
                <p class="gabout-eyebrow gabout-eyebrow--en">NEXT</p>
                <h2>از چیزی که واقعاً نیاز داری شروع کن.</h2>
                <a class="gabout-btn gabout-btn--dark" href="<?php echo esc_url( $shop_url ); ?>">
                    <span>ورود به فروشگاه</span><span class="gabout-arrow" aria-hidden="true">↗</span>
                </a>
            </div>
            <div class="gabout-cta__art" aria-hidden="true">
                <div class="gabout-cta__photo"></div>
            </div>
        </div>
    </section>
</main>

<?php get_footer();
