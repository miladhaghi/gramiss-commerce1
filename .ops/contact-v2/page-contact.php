<?php
/**
 * Gramiss Contact page — compact support experience.
 * Slug: /contact/
 * Marker: GRAMISS_CONTACT_V2
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

wp_enqueue_style(
    'gramiss-contact-v2',
    get_stylesheet_directory_uri() . '/assets/css/contact-v2.css',
    array(),
    '2.0.0'
);

get_header();

$support_email = 'Gramiss.ir@gmail.com';
$support_phone = '__SUPPORT_PHONE__';
$phone_digits  = preg_replace( '/\D+/', '', $support_phone );
$phone_display = $support_phone;

if ( strlen( $phone_digits ) === 11 && strpos( $phone_digits, '09' ) === 0 ) {
    $phone_display = substr( $phone_digits, 0, 4 ) . ' ' . substr( $phone_digits, 4, 3 ) . ' ' . substr( $phone_digits, 7 );
    $phone_href    = '+98' . substr( $phone_digits, 1 );
} else {
    $phone_href = '';
}

$primary_contact_href = $phone_href ? 'tel:' . $phone_href : 'mailto:' . $support_email;
?>

<main id="primary" class="gcontact" data-gramiss-contact="v2" dir="rtl">
    <!-- GRAMISS_CONTACT_V2 -->

    <section class="gcontact-screen gcontact-screen--top" aria-labelledby="gcontact-title">
        <div class="gcontact-shell">
            <div class="gcontact-hero">
                <div class="gcontact-panel" aria-label="راه‌های ارتباط">
                    <p class="gcontact-kicker gcontact-kicker--panel">CONTACT GRAMISS</p>
                    <h2>راه‌های ارتباط با ما</h2>
                    <p class="gcontact-panel__lead">تیم پشتیبانی ما آماده پاسخ‌گویی به سؤال‌های شماست.</p>

                    <div class="gcontact-contactlist">
                        <a class="gcontact-contactrow" href="<?php echo esc_url( $primary_contact_href ); ?>">
                            <span class="gcontact-contactrow__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" fill="none"><path d="M7.5 4.5 10 8l-2 2.2c1.5 3 3.8 5.3 6.8 6.8L17 15l3.5 2.5c.4.3.5.8.3 1.2-.7 1.5-2 2.3-3.8 2.3C10.3 21 3 13.7 3 7c0-1.8.8-3.1 2.3-3.8.4-.2.9-.1 1.2.3Z"/></svg>
                            </span>
                            <span class="gcontact-contactrow__body">
                                <small>شماره پشتیبانی</small>
                                <strong><?php echo esc_html( $phone_display ); ?></strong>
                            </span>
                        </a>

                        <a class="gcontact-contactrow" href="mailto:<?php echo esc_attr( $support_email ); ?>">
                            <span class="gcontact-contactrow__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></svg>
                            </span>
                            <span class="gcontact-contactrow__body">
                                <small>ایمیل پشتیبانی</small>
                                <strong dir="ltr"><?php echo esc_html( $support_email ); ?></strong>
                            </span>
                        </a>

                        <div class="gcontact-contactrow">
                            <span class="gcontact-contactrow__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 2"/></svg>
                            </span>
                            <span class="gcontact-contactrow__body">
                                <small>ساعات پاسخ‌گویی</small>
                                <strong>تمام روزهای هفته، ۱۱ تا ۲۳</strong>
                            </span>
                        </div>
                    </div>

                    <div class="gcontact-response-note">
                        <span aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none"><path d="M4 5h16v11H8l-4 3V5Z"/></svg>
                        </span>
                        معمولاً کمتر از ۲۴ ساعت پاسخ می‌دهیم.
                    </div>
                </div>

                <div class="gcontact-intro">
                    <p class="gcontact-kicker">GRAMISS / SUPPORT</p>
                    <h1 id="gcontact-title">پشتیبانی و تماس،<br>کوتاه و روشن.</h1>
                    <p class="gcontact-intro__lead">برای هر سؤالی درباره سفارش، پرداخت، ارسال یا محصول، ما اینجا هستیم تا به شما کمک کنیم.</p>
                    <div class="gcontact-actions">
                        <a class="gcontact-btn gcontact-btn--dark" href="#gcontact-support-choices">
                            <span>تماس با پشتیبانی</span><span aria-hidden="true">←</span>
                        </a>
                        <a class="gcontact-btn gcontact-btn--light" href="#gcontact-faq">مشاهده سؤالات متداول</a>
                    </div>
                    <p class="gcontact-intro__micro">سریع‌تر به پاسخ برسید یا مستقیم با ما در ارتباط باشید.</p>
                </div>
            </div>

            <div class="gcontact-routes" aria-label="مسیرهای پشتیبانی">
                <article class="gcontact-route">
                    <div class="gcontact-route__top">
                        <span class="gcontact-route__icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none"><rect x="4" y="6" width="16" height="12" rx="2"/><path d="M4 10h16"/></svg>
                        </span>
                        <span class="gcontact-index">01</span>
                    </div>
                    <h3>سفارش و پرداخت</h3>
                    <p>ثبت سفارش، پرداخت کارت‌به‌کارت، رسید پرداخت و وضعیت تأیید سفارش.</p>
                    <a href="#gcontact-faq">مشاهده راهنما <span aria-hidden="true">←</span></a>
                </article>

                <article class="gcontact-route">
                    <div class="gcontact-route__top">
                        <span class="gcontact-route__icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none"><path d="M3 6h11v10H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="2"/><circle cx="18" cy="18" r="2"/></svg>
                        </span>
                        <span class="gcontact-index">02</span>
                    </div>
                    <h3>ارسال و پیگیری</h3>
                    <p>وضعیت آماده‌سازی، ارسال سفارش و دریافت اطلاعات پیگیری.</p>
                    <a href="#gcontact-faq">مشاهده راهنما <span aria-hidden="true">←</span></a>
                </article>

                <article class="gcontact-route">
                    <div class="gcontact-route__top">
                        <span class="gcontact-route__icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none"><path d="m12 3 7 4-7 4-7-4 7-4Z"/><path d="m5 7 7 4 7-4v9l-7 4-7-4V7Z"/><path d="M12 11v9"/></svg>
                        </span>
                        <span class="gcontact-index">03</span>
                    </div>
                    <h3>محصول و مغایرت</h3>
                    <p>سؤال درباره محصول، سایز، مشخصات و موارد مغایرت پس از دریافت.</p>
                    <a href="#gcontact-faq">مشاهده راهنما <span aria-hidden="true">←</span></a>
                </article>
            </div>
        </div>
    </section>

    <section id="gcontact-faq" class="gcontact-screen gcontact-screen--faq" aria-labelledby="gcontact-faq-title">
        <div class="gcontact-shell">
            <div class="gcontact-faqbox">
                <div class="gcontact-faqhead">
                    <div>
                        <p class="gcontact-kicker gcontact-kicker--ltr">QUICK ANSWERS</p>
                        <h2 id="gcontact-faq-title">پاسخ‌های سریع</h2>
                        <p>پرتکرارترین سؤال‌ها را اینجا ببینید.</p>
                    </div>
                    <a href="#gcontact-title">مشاهده همه سؤال‌ها <span aria-hidden="true">←</span></a>
                </div>

                <div class="gcontact-faqlayout">
                    <aside class="gcontact-help">
                        <span class="gcontact-help__icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none"><path d="M4 13v-2a8 8 0 0 1 16 0v2"/><path d="M4 12H2v5h4v-5H4Zm16 0h2v5h-4v-5h2ZM18 19c-1 1-2.5 1.5-4.5 1.5H12"/></svg>
                        </span>
                        <div>
                            <h3>پاسخ مورد نظر خود را پیدا نکردید؟</h3>
                            <p>با تیم پشتیبانی ما در ارتباط باشید. ما اینجا هستیم تا راهنمایی‌تان کنیم.</p>
                        </div>
                        <a class="gcontact-btn gcontact-btn--dark" href="#gcontact-support-choices">
                            <span>تماس با پشتیبانی</span><span aria-hidden="true">←</span>
                        </a>
                    </aside>

                    <div class="gcontact-accordion">
                        <details>
                            <summary><span>سفارشم ثبت شده؛ مرحله بعد چیست؟</span><b aria-hidden="true">+</b></summary>
                            <p>پس از ثبت و تأیید سفارش، فرایند آماده‌سازی شروع می‌شود. برای اطلاع از وضعیت سفارش می‌توانید از حساب کاربری یا پشتیبانی پیگیری کنید.</p>
                        </details>
                        <details>
                            <summary><span>برای پیگیری سفارش چه اطلاعاتی لازم است؟</span><b aria-hidden="true">+</b></summary>
                            <p>شماره سفارش و شماره تماس یا ایمیلی که هنگام خرید ثبت کرده‌اید، بررسی را سریع‌تر می‌کند.</p>
                        </details>
                        <details>
                            <summary><span>اگر مشخصات محصول با چیزی که دریافت کردم متفاوت بود چه کنم؟</span><b aria-hidden="true">+</b></summary>
                            <p>شماره سفارش و توضیح کوتاه همراه با تصویر واضح برای پشتیبانی ارسال کنید تا موضوع بررسی و مسیر بعدی به شما اعلام شود.</p>
                        </details>
                        <details>
                            <summary><span>برای سؤال قبل از خرید هم می‌توانم تماس بگیرم؟</span><b aria-hidden="true">+</b></summary>
                            <p>بله. برای سؤال درباره محصول، سایز، انتخاب یا مقایسه گزینه‌ها می‌توانید پیش از خرید با پشتیبانی در ارتباط باشید.</p>
                        </details>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <div id="gcontact-support-choices" class="gcontact-support-choices" role="dialog" aria-modal="true" aria-labelledby="gcontact-support-choice-title">
        <a class="gcontact-support-choices__backdrop" href="#gcontact-title" aria-label="بستن پنجره تماس"></a>
        <div class="gcontact-support-choices__card">
            <a class="gcontact-support-choices__close" href="#gcontact-title" aria-label="بستن">×</a>
            <p class="gcontact-kicker">CONTACT GRAMISS</p>
            <h2 id="gcontact-support-choice-title">راه تماس را انتخاب کنید</h2>
            <p class="gcontact-support-choices__lead">از یکی از روش‌های زیر مستقیماً با پشتیبانی گرامیس در ارتباط باشید.</p>
            <div class="gcontact-support-choices__links">
                <?php if ( $phone_href ) : ?>
                    <a class="gcontact-support-choice" href="tel:<?php echo esc_attr( $phone_href ); ?>">
                        <span>تماس تلفنی</span>
                        <strong dir="ltr"><?php echo esc_html( $phone_display ); ?></strong>
                    </a>
                <?php endif; ?>
                <a class="gcontact-support-choice" href="mailto:<?php echo esc_attr( $support_email ); ?>">
                    <span>ارسال ایمیل</span>
                    <strong dir="ltr"><?php echo esc_html( $support_email ); ?></strong>
                </a>
            </div>
        </div>
    </div>

    <style>
        .gcontact-support-choices{position:fixed;inset:0;z-index:999999;display:grid;place-items:center;padding:20px;opacity:0;visibility:hidden;pointer-events:none;transition:opacity .2s ease,visibility .2s ease}
        .gcontact-support-choices:target{opacity:1;visibility:visible;pointer-events:auto}
        .gcontact-support-choices__backdrop{position:absolute;inset:0;background:rgba(4,9,14,.62);backdrop-filter:blur(8px)}
        .gcontact-support-choices__card{position:relative;z-index:1;width:min(460px,100%);padding:30px;border-radius:22px;background:#fbfaf7;box-shadow:0 28px 80px rgba(3,8,13,.28);transform:translateY(14px) scale(.985);transition:transform .2s ease;text-align:right}
        .gcontact-support-choices:target .gcontact-support-choices__card{transform:none}
        .gcontact-support-choices__close{position:absolute;left:18px;top:14px;width:36px;height:36px;border-radius:50%;display:grid;place-items:center;background:#f0ece6;border:1px solid rgba(13,16,22,.10);font:400 25px/1 Arial,sans-serif;color:#111!important}
        .gcontact-support-choices__card h2{font-size:28px;line-height:1.35;font-weight:900;color:#0d1016}
        .gcontact-support-choices__lead{margin-top:9px!important;color:#747b84;font-size:13px;line-height:1.8}
        .gcontact-support-choices__links{margin-top:22px;display:grid;gap:10px}
        .gcontact-support-choice{min-height:72px;padding:14px 16px;border:1px solid rgba(13,16,22,.10);border-radius:15px;background:#fff;display:flex;align-items:center;justify-content:space-between;gap:18px;transition:.18s ease}
        .gcontact-support-choice:hover{transform:translateY(-1px);border-color:rgba(49,95,155,.30);box-shadow:0 10px 24px rgba(20,24,30,.06)}
        .gcontact-support-choice span{font-size:14px;font-weight:850;color:#111820}
        .gcontact-support-choice strong{font-size:14px;color:#315f9b;white-space:nowrap;unicode-bidi:isolate}
        @media(max-width:560px){.gcontact-support-choices__card{padding:26px 18px 18px;border-radius:18px}.gcontact-support-choices__card h2{font-size:24px}.gcontact-support-choice{align-items:flex-start;flex-direction:column;gap:5px;min-height:0}.gcontact-support-choice strong{font-size:13px}}
    </style>
</main>

<?php get_footer();
