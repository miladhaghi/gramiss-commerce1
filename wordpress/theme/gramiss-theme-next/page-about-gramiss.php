<?php
/**
 * Template Name: Gramiss About V1
 * Description: صفحه درباره Gramiss.
 */
defined( 'ABSPATH' ) || exit;
get_header();
$shop_url    = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$support_url = home_url( '/contact/' );
?>
<!-- GRAMISS ABOUT V1 START -->
<main id="primary" class="g-info-page g-about-page" dir="rtl">
    <section class="g-info-hero" aria-labelledby="g-about-title">
        <div class="g-info-shell g-info-hero-grid">
            <div class="g-info-hero-copy">
                <span class="g-info-kicker">GRAMISS / ABOUT</span>
                <h1 id="g-about-title">کمتر حدس بزن؛<br>بهتر انتخاب کن.</h1>
                <p>Gramiss برای خرید پوشاکی ساخته شده که تصمیم‌گیری در آن ساده‌تر، شفاف‌تر و آگاهانه‌تر باشد؛ از خود محصول تا راهنمای انتخاب و استایل.</p>
                <div class="g-info-actions">
                    <a class="g-info-btn g-info-btn-dark" href="<?php echo esc_url( $shop_url ); ?>">مشاهده فروشگاه <span aria-hidden="true">↗</span></a>
                    <a class="g-info-btn g-info-btn-light" href="<?php echo esc_url( $support_url ); ?>">پشتیبانی و تماس</a>
                </div>
            </div>
            <div class="g-about-orbit" aria-hidden="true">
                <div class="g-about-orbit-ring ring-1"></div>
                <div class="g-about-orbit-ring ring-2"></div>
                <div class="g-about-orbit-ring ring-3"></div>
                <div class="g-about-orbit-core">G</div>
                <span class="g-about-orbit-label label-a">انتخاب</span>
                <span class="g-about-orbit-label label-b">کیفیت</span>
                <span class="g-about-orbit-label label-c">استایل</span>
            </div>
        </div>
    </section>

    <section class="g-info-section">
        <div class="g-info-shell g-about-intro">
            <span class="g-info-index">01</span>
            <div>
                <span class="g-info-kicker">WHAT GRAMISS IS</span>
                <h2>فقط یک ویترین محصول نیست.</h2>
            </div>
            <p>هدف Gramiss این است که قبل از خرید، اطلاعاتی که واقعاً به تصمیم کمک می‌کند در دسترس باشد: فیت، کاربرد، جنس، نگهداری، ترکیب استایل و تفاوت گزینه‌ها. محصول باید دیده شود، اما انتخاب باید فهمیده شود.</p>
        </div>
    </section>

    <section class="g-info-section g-info-section-soft">
        <div class="g-info-shell">
            <div class="g-info-section-head">
                <div><span class="g-info-kicker">OUR PRINCIPLES</span><h2>سه اصل ساده.</h2></div>
                <p>چیزی که تجربه Gramiss را از فروشگاه‌های شلوغ و فشارمحور جدا می‌کند.</p>
            </div>
            <div class="g-info-card-grid g-info-card-grid-3">
                <article class="g-info-card"><span>01</span><h3>انتخاب آگاهانه</h3><p>اطلاعات کاربردی قبل از خرید، نه توضیحات طولانی و بی‌اثر.</p></article>
                <article class="g-info-card"><span>02</span><h3>محصول واقعی</h3><p>جزئیات محصول، موجودی و مشخصات باید تا جای ممکن دقیق و قابل اتکا باشند.</p></article>
                <article class="g-info-card"><span>03</span><h3>بدون فشار</h3><p>مسیر خرید کوتاه و روشن باشد و کاربر برای تصمیم‌گیری تحت فشار قرار نگیرد.</p></article>
            </div>
        </div>
    </section>

    <section class="g-info-section">
        <div class="g-info-shell g-about-smart">
            <div class="g-about-smart-copy">
                <span class="g-info-kicker">GRAMISS SMART GUIDE</span>
                <h2>راهنما، قبل از فروش.</h2>
                <p>Smart Guide قرار است با چند سؤال درباره نیاز، کاربرد، بودجه، فرم و سلیقه، گزینه‌های مناسب‌تر را محدود کند. نقش آن کمک به تصمیم است؛ نه جایگزین‌کردن انتخاب کاربر.</p>
                <a class="g-info-text-link" href="<?php echo esc_url( home_url( '/#smart-guide' ) ); ?>">دیدن Smart Guide <span aria-hidden="true">↗</span></a>
            </div>
            <div class="g-about-smart-stat" aria-label="اصول Smart Guide">
                <div><strong>01</strong><span>شناخت نیاز</span></div>
                <div><strong>02</strong><span>مقایسه شفاف</span></div>
                <div><strong>03</strong><span>پیشنهاد قابل توضیح</span></div>
            </div>
        </div>
    </section>

    <section class="g-info-cta">
        <div class="g-info-shell g-info-cta-inner">
            <div><span class="g-info-kicker">NEXT</span><h2>از چیزی که واقعاً نیاز داری شروع کن.</h2></div>
            <a class="g-info-btn g-info-btn-dark" href="<?php echo esc_url( $shop_url ); ?>">ورود به فروشگاه <span aria-hidden="true">↗</span></a>
        </div>
    </section>
</main>
<!-- GRAMISS ABOUT V1 END -->
<?php get_footer(); ?>
