<?php
/**
 * Template Name: Gramiss About V2
 * Description: صفحه درباره Gramiss — نسخه پالایش‌شده و هماهنگ با Home.
 */
defined( 'ABSPATH' ) || exit;
get_header();

$shop_url    = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$support_url = home_url( '/contact/' );
$about_v2_css_url = get_stylesheet_directory_uri() . '/assets/css/about-gramiss-v2.css?v=20260907-2';
?>
<link id="gramiss-about-v2-css" rel="stylesheet" href="<?php echo esc_url( $about_v2_css_url ); ?>" media="all">
<!-- GRAMISS ABOUT V2 START -->
<main id="primary" class="g-info-page g-about-page g-about-v2" dir="rtl">
    <section class="gav2-hero" aria-labelledby="gav2-title">
        <div class="gav2-shell gav2-hero-grid">
            <div class="gav2-copy">
                <span class="gav2-kicker">GRAMISS / ABOUT</span>
                <h1 id="gav2-title">کمتر حدس بزن،<br>بهتر انتخاب کن.</h1>
                <p class="gav2-lead">Gramiss برای خرید پوشاکی ساخته شده که تصمیم‌گیری در آن ساده‌تر، شفاف‌تر و آگاهانه‌تر باشد؛ از خود محصول تا راهنمای انتخاب و استایل.</p>
                <div class="gav2-actions">
                    <a class="gav2-btn gav2-btn-dark" href="<?php echo esc_url( $shop_url ); ?>">مشاهده فروشگاه <span aria-hidden="true">↗</span></a>
                    <a class="gav2-btn gav2-btn-light" href="<?php echo esc_url( $support_url ); ?>">پشتیبانی و تماس</a>
                </div>
            </div>

            <div class="gav2-orbit" aria-hidden="true">
                <span class="gav2-ring gav2-ring-a"></span>
                <span class="gav2-ring gav2-ring-b"></span>
                <span class="gav2-ring gav2-ring-c"></span>
                <span class="gav2-orbit-core">G</span>
                <span class="gav2-chip gav2-chip-a">انتخاب</span>
                <span class="gav2-chip gav2-chip-b">کیفیت</span>
                <span class="gav2-chip gav2-chip-c">استایل</span>
            </div>
        </div>
    </section>

    <section class="gav2-section gav2-intro-section">
        <div class="gav2-shell gav2-intro-grid">
            <div class="gav2-intro-copy">
                <span class="gav2-kicker">WHAT GRAMISS IS</span>
                <h2>فقط یک ویترین<br>محصول نیست.</h2>
                <p>هدف Gramiss این است که قبل از خرید، اطلاعاتی که واقعاً به تصمیم کمک می‌کند در دسترس باشد: فیت، کاربرد، جنس، نگهداری، ترکیب استایل و تفاوت گزینه‌ها. محصول باید دیده شود، اما انتخاب باید فهمیده شود.</p>
            </div>

            <div class="gav2-editorial" aria-hidden="true">
                <div class="gav2-editorial-rail"></div>
                <span class="gav2-hanger gav2-hanger-1"></span>
                <span class="gav2-hanger gav2-hanger-2"></span>
                <span class="gav2-hanger gav2-hanger-3"></span>
                <span class="gav2-hanger gav2-hanger-4"></span>
                <div class="gav2-editorial-copy-en">Better<br>Choices.<br>A More<br>You.</div>
                <div class="gav2-editorial-mark">GRAMISS</div>
            </div>
        </div>
    </section>

    <section class="gav2-section gav2-principles">
        <div class="gav2-shell">
            <div class="gav2-section-heading gav2-section-heading-center">
                <span class="gav2-kicker">OUR PRINCIPLES</span>
                <h2>سه اصل ساده.</h2>
                <p>چیزی که تجربه Gramiss را از فروشگاه‌های شلوغ و فشارمحور جدا می‌کند.</p>
            </div>

            <div class="gav2-card-grid">
                <article class="gav2-card">
                    <span class="gav2-card-index">01</span>
                    <span class="gav2-card-icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" role="img"><path d="M9 18h6M10 22h4M8.5 15.5C6.9 14.3 6 12.5 6 10.5A6 6 0 0 1 18 10.5c0 2-.9 3.8-2.5 5-.8.6-1.2 1.2-1.3 2H9.8c-.1-.8-.5-1.4-1.3-2Z"/></svg>
                    </span>
                    <h3>انتخاب آگاهانه</h3>
                    <p>اطلاعات کاربردی قبل از خرید، نه توضیحات طولانی و بی‌اثر.</p>
                </article>

                <article class="gav2-card">
                    <span class="gav2-card-index">02</span>
                    <span class="gav2-card-icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" role="img"><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Zm0 0v9m8-4.5-8 4.5-8-4.5M12 12v9"/></svg>
                    </span>
                    <h3>محصول واقعی</h3>
                    <p>جزئیات محصول، موجودی و مشخصات باید تا جای ممکن دقیق و قابل اتکا باشند.</p>
                </article>

                <article class="gav2-card">
                    <span class="gav2-card-index">03</span>
                    <span class="gav2-card-icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" role="img"><path d="M8 21v-2a4 4 0 0 1 4-4h1M5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm13 10v-2a4 4 0 0 0-4-4h-1m5-4a4 4 0 1 0 0-8"/></svg>
                    </span>
                    <h3>بدون فشار</h3>
                    <p>مسیر خرید کوتاه و روشن باشد و کاربر برای تصمیم‌گیری تحت فشار قرار نگیرد.</p>
                </article>
            </div>
        </div>
    </section>

    <section class="gav2-cta">
        <div class="gav2-shell gav2-cta-inner">
            <div>
                <span class="gav2-kicker">NEXT</span>
                <h2>از چیزی که واقعاً نیاز داری شروع کن.</h2>
                <p>استایل بهتر، با انتخاب‌های آگاهانه‌تر.</p>
            </div>
            <a class="gav2-btn gav2-btn-dark" href="<?php echo esc_url( $shop_url ); ?>">ورود به فروشگاه <span aria-hidden="true">↗</span></a>
        </div>
    </section>

    <section class="gav2-section gav2-smart-section">
        <div class="gav2-shell gav2-smart-grid">
            <div class="gav2-smart-copy">
                <span class="gav2-kicker">GRAMISS SMART GUIDE</span>
                <h2>راهنما، قبل از فروش.</h2>
                <p>Smart Guide قرار است با چند سؤال درباره نیاز، کاربرد، بودجه، فرم و سلیقه، گزینه‌های مناسب‌تر را محدود کند. نقش آن کمک به تصمیم است؛ نه جایگزین‌کردن انتخاب کاربر.</p>
                <a class="gav2-text-link" href="<?php echo esc_url( home_url( '/#smart-guide' ) ); ?>">دیدن Smart Guide <span aria-hidden="true">↗</span></a>
            </div>

            <div class="gav2-smart-panel" aria-label="اصول Smart Guide">
                <div class="gav2-smart-row"><strong>01</strong><span><b>شناخت نیاز</b><small>کمک به پیدا کردن کاربرد و انتخاب مناسب‌تر</small></span><i aria-hidden="true">○</i></div>
                <div class="gav2-smart-row"><strong>02</strong><span><b>مقایسه شفاف</b><small>تفاوت گزینه‌ها را واضح ببینید</small></span><i aria-hidden="true">≋</i></div>
                <div class="gav2-smart-row"><strong>03</strong><span><b>پیشنهاد قابل توضیح</b><small>دلیل هر پیشنهاد را بدانید</small></span><i aria-hidden="true">□</i></div>
            </div>
        </div>
    </section>
</main>
<!-- GRAMISS ABOUT V2 END -->
<?php get_footer(); ?>
