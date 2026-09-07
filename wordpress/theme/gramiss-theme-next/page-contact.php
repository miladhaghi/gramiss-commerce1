<?php
/**
 * Template Name: Gramiss Support V1
 * Description: صفحه پشتیبانی و تماس Gramiss.
 */
defined( 'ABSPATH' ) || exit;
get_header();
$info  = function_exists( 'gramiss_site_info_v1' ) ? gramiss_site_info_v1() : array( 'phone' => '', 'email' => '', 'hours' => '' );
$phone = trim( (string) ( $info['phone'] ?? '' ) );
$email = trim( (string) ( $info['email'] ?? '' ) );
$hours = trim( (string) ( $info['hours'] ?? '' ) );
$tel   = preg_replace( '/[^0-9+]/', '', $phone );
?>
<!-- GRAMISS SUPPORT V1 START -->
<main id="primary" class="g-info-page g-support-page" dir="rtl">
    <section class="g-info-hero g-support-hero" aria-labelledby="g-support-title">
        <div class="g-info-shell g-info-hero-grid">
            <div class="g-info-hero-copy">
                <span class="g-info-kicker">GRAMISS / SUPPORT</span>
                <h1 id="g-support-title">کمکت می‌کنیم،<br>قبل و بعد از خرید.</h1>
                <p>برای سؤال درباره سفارش، پرداخت، ارسال، پیگیری یا مغایرت محصول، مسیر پشتیبانی Gramiss همین‌جاست.</p>
            </div>
            <div class="g-support-status" aria-label="مسیر پشتیبانی">
                <div><span>01</span><strong>موضوع را مشخص کن</strong><small>سفارش، پرداخت، ارسال یا محصول</small></div>
                <div><span>02</span><strong>با ما تماس بگیر</strong><small>شماره سفارش را آماده داشته باش</small></div>
                <div><span>03</span><strong>پیگیری روشن</strong><small>نتیجه را شفاف اعلام می‌کنیم</small></div>
            </div>
        </div>
    </section>

    <section class="g-info-section">
        <div class="g-info-shell">
            <div class="g-info-section-head">
                <div><span class="g-info-kicker">SUPPORT ROUTES</span><h2>برای چه چیزی می‌تونی با ما تماس بگیری؟</h2></div>
                <p>برای سریع‌تر شدن بررسی، اگر سفارش ثبت کرده‌ای شماره سفارش را همراهت داشته باش.</p>
            </div>
            <div class="g-info-card-grid g-info-card-grid-3">
                <article class="g-info-card"><span>01</span><h3>سفارش و پرداخت</h3><p>ثبت سفارش، پرداخت کارت‌به‌کارت، رسید پرداخت و وضعیت تأیید سفارش.</p></article>
                <article class="g-info-card"><span>02</span><h3>ارسال و پیگیری</h3><p>وضعیت آماده‌سازی، ارسال سفارش و دریافت اطلاعات پیگیری.</p></article>
                <article class="g-info-card"><span>03</span><h3>محصول و مغایرت</h3><p>سؤال درباره محصول، سایز، مشخصات یا گزارش مغایرت پس از دریافت.</p></article>
            </div>
        </div>
    </section>

    <section class="g-support-contact-wrap">
        <div class="g-info-shell g-support-contact">
            <div class="g-support-contact-head">
                <span class="g-info-kicker">CONTACT GRAMISS</span>
                <h2>راه‌های ارتباط</h2>
                <p>اطلاعات زیر، اطلاعات رسمی پشتیبانی Gramiss است.</p>
            </div>
            <div class="g-support-contact-list">
                <?php if ( $phone ) : ?>
                    <a class="g-support-contact-row" href="tel:<?php echo esc_attr( $tel ); ?>"><span>شماره پشتیبانی</span><strong dir="ltr"><?php echo esc_html( $phone ); ?></strong><em aria-hidden="true">↗</em></a>
                <?php endif; ?>
                <?php if ( $email ) : ?>
                    <a class="g-support-contact-row" href="mailto:<?php echo esc_attr( $email ); ?>"><span>ایمیل پشتیبانی</span><strong dir="ltr"><?php echo esc_html( $email ); ?></strong><em aria-hidden="true">↗</em></a>
                <?php endif; ?>
                <?php if ( $hours ) : ?>
                    <div class="g-support-contact-row"><span>ساعات پاسخ‌گویی</span><strong><?php echo esc_html( $hours ); ?></strong><em aria-hidden="true">—</em></div>
                <?php endif; ?>

                <?php if ( ! $phone && ! $email && ! $hours ) : ?>
                    <div class="g-support-empty">
                        <strong>اطلاعات تماس در حال تکمیل است.</strong>
                        <p>اطلاعات رسمی پشتیبانی به‌زودی در همین صفحه قرار می‌گیرد.</p>
                        <?php if ( current_user_can( 'manage_options' ) ) : ?>
                            <a href="<?php echo esc_url( admin_url( 'options-general.php?page=gramiss-site-info' ) ); ?>">ورود اطلاعات تماس در مدیریت وردپرس</a>
                        <?php endif; ?>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </section>

    <section class="g-info-section g-info-section-soft">
        <div class="g-info-shell">
            <div class="g-info-section-head">
                <div><span class="g-info-kicker">QUICK ANSWERS</span><h2>پاسخ‌های سریع.</h2></div>
            </div>
            <div class="g-support-faq">
                <details><summary>سفارشم ثبت شده؛ مرحله بعد چیست؟</summary><p>اگر روش پرداخت کارت‌به‌کارت را انتخاب کرده‌ای، سفارش تا ثبت و بررسی پرداخت در وضعیت انتظار می‌ماند. برای پیگیری، شماره سفارش را اعلام کن.</p></details>
                <details><summary>برای پیگیری سفارش چه اطلاعاتی لازم است؟</summary><p>شماره سفارش و شماره موبایلی که هنگام خرید ثبت کرده‌ای، سریع‌ترین راه برای پیدا کردن سفارش است.</p></details>
                <details><summary>اگر مشخصات محصول با چیزی که دریافت کردم متفاوت بود چه کنم؟</summary><p>قبل از استفاده از محصول با پشتیبانی تماس بگیر و شماره سفارش و توضیح مغایرت را اعلام کن تا بررسی شود.</p></details>
                <details><summary>برای سؤال قبل از خرید هم می‌توانم تماس بگیرم؟</summary><p>بله. اگر درباره سایز، مشخصات یا انتخاب محصول سؤال داری، پشتیبانی برای راهنمایی قبل از خرید هم در دسترس است.</p></details>
            </div>
        </div>
    </section>
</main>
<!-- GRAMISS SUPPORT V1 END -->
<?php get_footer(); ?>
