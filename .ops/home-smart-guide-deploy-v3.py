#!/usr/bin/env python3
import importlib.util
import json
import re
import time
from pathlib import Path

base = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_live_helpers', base)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

EXPECTED_HOME = '0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7'
EXPECTED_CSS = 'b65f5a02acf53f6e0b9e772507879bd13bd33235017b3d5b0348dc0be2f0de7f'
PROTECTED = {
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}

NEW_BLOCK = r'''<section class="g1-section g1-reveal" id="smart-guide">
        <?php
        $smart_pick_product = static function ( array $candidates ) {
            if ( ! function_exists( 'wc_get_products' ) || ! taxonomy_exists( 'product_cat' ) ) {
                return null;
            }
            foreach ( $candidates as $candidate ) {
                $term = get_term_by( 'slug', sanitize_title( $candidate ), 'product_cat' );
                if ( ! $term ) {
                    $term = get_term_by( 'name', $candidate, 'product_cat' );
                }
                if ( ! $term || is_wp_error( $term ) ) {
                    continue;
                }
                $products = wc_get_products(
                    array(
                        'status'   => 'publish',
                        'limit'    => 8,
                        'category' => array( $term->slug ),
                        'orderby'  => 'date',
                        'order'    => 'DESC',
                    )
                );
                foreach ( $products as $product ) {
                    if ( $product instanceof WC_Product && $product->get_image_id() ) {
                        return $product;
                    }
                }
            }
            return null;
        };

        $smart_cards = array(
            array( 'class' => 'is-cap', 'label' => 'کلاه', 'product' => $smart_pick_product( array( 'caps', 'cap', 'hats', 'hat', 'کلاه' ) ) ),
            array( 'class' => 'is-tee', 'label' => 'تیشرت', 'product' => $smart_pick_product( array( 't-shirts', 't-shirt', 'tshirt', 'تی‌شرت', 'تیشرت' ) ) ),
            array( 'class' => 'is-bag', 'label' => 'کیف', 'product' => $smart_pick_product( array( 'bags', 'bag', 'کیف' ) ) ),
            array( 'class' => 'is-pants', 'label' => 'شلوار', 'product' => $smart_pick_product( array( 'pants', 'trousers', 'شلوار' ) ) ),
            array( 'class' => 'is-sneaker', 'label' => 'کتونی', 'product' => $smart_pick_product( array( 'sneakers', 'sneaker', 'shoes', 'کتونی', 'کفش' ) ) ),
        );
        ?>
        <div class="g1-smart g1-smart-v3">
            <div class="g1-smart-copy">
                <small>GRAMISS / SMART GUIDE</small>
                <h2><span>فروشنده‌ای آرام،</span><span>دقیق و بی‌قضاوت.</span></h2>
                <p>چند سؤال کوتاه درباره استایل، کاربرد و بودجه؛<br>بعد فقط گزینه‌هایی که واقعاً به تو می‌خورند.</p>
                <div class="g1-smart-features" aria-label="ویژگی‌های Smart Guide">
                    <span><b>01</b><em>شناخت نیاز</em></span>
                    <span><b>02</b><em>مقایسه شفاف</em></span>
                    <span><b>03</b><em>پیشنهاد قابل توضیح</em></span>
                </div>
                <div class="g1-smart-actions">
                    <a class="g1-smart-cta" href="<?php echo esc_url( $shop_url ); ?>">شروع انتخاب <i>↗</i></a>
                    <button class="g1-smart-how" type="button" aria-label="Smart Guide چطور تصمیم می‌گیرد؟">Smart Guide چطور تصمیم می‌گیرد؟</button>
                </div>
            </div>

            <div class="g1-smart-visual" aria-hidden="true">
                <div class="g1-smart-product-cloud">
                    <?php foreach ( $smart_cards as $card ) : ?>
                        <div class="g1-smart-product-card <?php echo esc_attr( $card['class'] ); ?>">
                            <div class="g1-smart-product-art">
                                <?php if ( $card['product'] instanceof WC_Product ) : ?>
                                    <?php echo wp_kses_post( wp_get_attachment_image( $card['product']->get_image_id(), 'gramiss-product-card', false, array( 'loading' => 'lazy', 'decoding' => 'async', 'fetchpriority' => 'low', 'alt' => '' ) ) ); ?>
                                <?php else : ?>
                                    <span class="g1-smart-product-fallback"><?php echo esc_html( $card['label'] ); ?></span>
                                <?php endif; ?>
                            </div>
                            <span class="g1-smart-skeleton"><i></i><i></i></span>
                        </div>
                    <?php endforeach; ?>
                </div>

                <div class="g1-smart-map">
                    <span class="g1-smart-ring is-outer"></span>
                    <span class="g1-smart-ring is-mid"></span>
                    <span class="g1-smart-ring is-inner"></span>
                    <span class="g1-smart-axis is-horizontal"></span>
                    <span class="g1-smart-axis is-vertical"></span>

                    <span class="g1-smart-node is-style">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5a3 3 0 1 1 4.8 2.4L12 9v2m0 0L4 16.5V19h16v-2.5L12 11Z"/></svg>
                        <b>استایل</b>
                    </span>
                    <span class="g1-smart-node is-budget">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h14a2 2 0 0 1 2 2v9H4V7Zm0 3h16m-4 3h2"/></svg>
                        <b>بودجه</b>
                    </span>
                    <span class="g1-smart-node is-fit">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4 5 5.5 2.5 9l3 2L7 9v11h10V9l1.5 2 3-2L19 5.5 16 4c-.8 1.3-2.2 2-4 2S8.8 5.3 8 4Z"/></svg>
                        <b>فیت</b>
                    </span>
                    <span class="g1-smart-node is-use">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8h14v11H5V8Zm4 0V6h6v2m-10 5h14"/></svg>
                        <b>کاربرد</b>
                    </span>
                    <span class="g1-smart-core">G</span>
                </div>

                <div class="g1-smart-stats">
                    <span><b>۱۲</b><em>گزینه بررسی شد</em></span>
                    <span><b>۳</b><em>انتخاب مناسب</em></span>
                </div>
            </div>
        </div>
    </section>

    '''

NEW_CSS = r'''/* GRAMISS_HOME_SMART_GUIDE_V3 — mockup-faithful implementation */
#smart-guide .g1-smart-v3{
  position:relative;isolation:isolate;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);min-height:680px;
  border:1px solid rgba(255,255,255,.08);border-radius:42px;overflow:hidden;color:#fff;
  background:
    radial-gradient(ellipse at 15% 45%,rgba(153,133,114,.075) 0%,rgba(153,133,114,.025) 29%,transparent 58%),
    radial-gradient(ellipse at 76% 43%,rgba(68,101,145,.075) 0%,rgba(68,101,145,.028) 31%,transparent 60%),
    linear-gradient(116deg,#242320 0%,#202123 36%,#1b1e22 62%,#151b23 84%,#131820 100%);
  box-shadow:0 30px 74px rgba(13,16,21,.12),inset 0 1px 0 rgba(255,255,255,.035)
}
#smart-guide .g1-smart-v3::before{content:"";position:absolute;z-index:-1;inset:-20%;pointer-events:none;background:radial-gradient(circle at 54% 48%,rgba(111,150,207,.055),transparent 34%);filter:blur(34px)}
#smart-guide .g1-smart-v3::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:inherit;box-shadow:inset 0 0 140px rgba(4,7,12,.16)}

body.gramiss-next-staging #smart-guide .g1-smart-copy{position:relative;z-index:4;padding:64px 64px 60px!important;display:flex!important;flex-direction:column;justify-content:center!important;align-items:flex-start}
#smart-guide .g1-smart-copy small{margin:0 0 25px;font:650 10px/1 Inter,Arial,sans-serif;letter-spacing:.22em;color:#8caee0;direction:ltr}
#smart-guide .g1-smart-copy h2{width:100%;max-width:600px;margin:0 0 25px;font-size:clamp(46px,3.75vw,62px);line-height:1.38;letter-spacing:-.042em;color:#fff}
#smart-guide .g1-smart-copy h2 span{display:block;white-space:nowrap}
#smart-guide .g1-smart-copy p{max-width:570px;margin:0;color:rgba(231,233,237,.62);font-size:14px;line-height:2.05}

#smart-guide .g1-smart-features{width:min(100%,560px);margin:38px 0 40px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));direction:rtl}
#smart-guide .g1-smart-features span{position:relative;display:flex;flex-direction:column;gap:11px;min-width:0;padding-inline:22px;text-align:center}
#smart-guide .g1-smart-features span:first-child{padding-inline-start:0}
#smart-guide .g1-smart-features span:last-child{padding-inline-end:0}
#smart-guide .g1-smart-features span+span{border-inline-start:1px solid rgba(255,255,255,.10)}
#smart-guide .g1-smart-features b{color:#86aadc;font:650 10px/1 Inter,Arial,sans-serif;letter-spacing:.08em}
#smart-guide .g1-smart-features em{color:rgba(248,249,250,.88);font-style:normal;font-size:11px;line-height:1.7;white-space:nowrap}

#smart-guide .g1-smart-actions{display:flex;flex-direction:column;align-items:flex-start;gap:15px}
body.gramiss-next-staging #smart-guide .g1-smart-cta{min-width:256px;min-height:60px;padding:0 30px;border:1px solid rgba(255,255,255,.88);border-radius:999px;display:inline-flex;align-items:center;justify-content:center;gap:32px;background:#f7f6f3;color:#101419;text-decoration:none;font-size:14px;font-weight:750;box-shadow:0 16px 38px rgba(0,0,0,.14);transition:transform .22s ease,box-shadow .22s ease,background .22s ease}
#smart-guide .g1-smart-cta i{font:600 15px/1 Inter,Arial,sans-serif;font-style:normal}
#smart-guide .g1-smart-cta:hover{transform:translateY(-2px);background:#fff;box-shadow:0 20px 44px rgba(0,0,0,.18)}
#smart-guide .g1-smart-how{padding:0 0 5px;border:0;border-bottom:1px solid rgba(141,172,215,.35);background:transparent;color:rgba(225,230,236,.58);font-size:11px;line-height:1.5;cursor:pointer}

body.gramiss-next-staging #smart-guide .g1-smart-visual{position:relative;z-index:2;min-height:680px!important;display:block!important;overflow:hidden;background:transparent!important}
#smart-guide .g1-smart-product-cloud{position:absolute;inset:0;z-index:1;pointer-events:none}
#smart-guide .g1-smart-product-card{position:absolute;width:126px;aspect-ratio:.82;padding:10px;border:1px solid rgba(255,255,255,.065);border-radius:14px;background:linear-gradient(155deg,rgba(255,255,255,.027),rgba(255,255,255,.008));box-shadow:0 18px 40px rgba(0,0,0,.07);opacity:.40;overflow:hidden;backdrop-filter:blur(2px);-webkit-backdrop-filter:blur(2px)}
#smart-guide .g1-smart-product-card.is-cap{left:10%;top:15%;transform:rotate(-5deg)}
#smart-guide .g1-smart-product-card.is-tee{right:12%;top:15%;transform:rotate(5deg)}
#smart-guide .g1-smart-product-card.is-bag{left:9%;bottom:20%;transform:rotate(6deg)}
#smart-guide .g1-smart-product-card.is-sneaker{right:10%;bottom:23%;transform:rotate(7deg)}
#smart-guide .g1-smart-product-card.is-pants{left:51%;bottom:8%;transform:translateX(-50%) rotate(-4deg)}
#smart-guide .g1-smart-product-art{height:78%;display:grid;place-items:center;overflow:hidden}
#smart-guide .g1-smart-product-art img{width:100%;height:100%;object-fit:contain;filter:grayscale(.48) saturate(.52) brightness(.72) contrast(.92);opacity:.82}
#smart-guide .g1-smart-product-fallback{color:rgba(255,255,255,.26);font-size:11px}
#smart-guide .g1-smart-skeleton{height:22%;display:flex;flex-direction:column;gap:5px;justify-content:flex-end;padding:1px 4px 2px}
#smart-guide .g1-smart-skeleton i{display:block;height:4px;border-radius:999px;background:rgba(255,255,255,.075)}
#smart-guide .g1-smart-skeleton i:last-child{width:62%}

#smart-guide .g1-smart-map{position:absolute;z-index:3;left:50%;top:46%;width:350px;height:350px;transform:translate(-50%,-50%);border-radius:50%}
#smart-guide .g1-smart-ring{position:absolute;left:50%;top:50%;border:1px solid rgba(213,224,239,.13);border-radius:50%;transform:translate(-50%,-50%)}
#smart-guide .g1-smart-ring.is-outer{width:100%;height:100%;border-style:dotted;opacity:.58}
#smart-guide .g1-smart-ring.is-mid{width:74%;height:74%;opacity:.86}
#smart-guide .g1-smart-ring.is-inner{width:49%;height:49%;opacity:.9;box-shadow:0 0 0 13px rgba(114,151,206,.018)}
#smart-guide .g1-smart-axis{position:absolute;left:50%;top:50%;background:rgba(218,227,239,.19);transform:translate(-50%,-50%)}
#smart-guide .g1-smart-axis.is-horizontal{width:100%;height:1px}
#smart-guide .g1-smart-axis.is-vertical{width:1px;height:100%}
#smart-guide .g1-smart-axis::before,#smart-guide .g1-smart-axis::after{content:"";position:absolute;width:7px;height:7px;border-radius:50%;background:#c8b9a5;box-shadow:0 0 0 2px rgba(255,255,255,.06)}
#smart-guide .g1-smart-axis.is-horizontal::before{left:-3px;top:-3px}#smart-guide .g1-smart-axis.is-horizontal::after{right:-3px;top:-3px}
#smart-guide .g1-smart-axis.is-vertical::before{top:-3px;left:-3px}#smart-guide .g1-smart-axis.is-vertical::after{bottom:-3px;left:-3px}

#smart-guide .g1-smart-core{position:absolute;z-index:6;left:50%;top:50%;width:112px;height:112px;transform:translate(-50%,-50%);border-radius:50%;display:grid;place-items:center;background:#fafafa;color:#101419;font:800 35px/1 Inter,Arial,sans-serif;box-shadow:0 0 0 1px rgba(255,255,255,.55),0 0 0 12px rgba(126,160,209,.035),0 0 46px rgba(112,149,203,.24)}
#smart-guide .g1-smart-node{position:absolute;z-index:5;width:78px;height:78px;border:1px solid rgba(216,224,235,.22);border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;background:rgba(25,29,35,.78);color:rgba(248,249,250,.83);box-shadow:0 10px 28px rgba(0,0,0,.10);backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px)}
#smart-guide .g1-smart-node svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.45;stroke-linecap:round;stroke-linejoin:round;opacity:.92}
#smart-guide .g1-smart-node b{font-size:10px;font-weight:500;line-height:1}
#smart-guide .g1-smart-node.is-style{left:50%;top:0;transform:translate(-50%,-50%)}
#smart-guide .g1-smart-node.is-use{left:50%;bottom:0;transform:translate(-50%,50%)}
#smart-guide .g1-smart-node.is-budget{left:0;top:50%;transform:translate(-50%,-50%)}
#smart-guide .g1-smart-node.is-fit{right:0;top:50%;transform:translate(50%,-50%)}

#smart-guide .g1-smart-stats{position:absolute;z-index:4;left:8%;bottom:7%;min-width:210px;padding-inline-start:20px;border-inline-start:1px solid rgba(218,225,234,.32);display:flex;flex-direction:column;gap:7px;direction:rtl;text-align:left}
#smart-guide .g1-smart-stats span{display:flex;align-items:baseline;justify-content:flex-end;gap:10px;color:rgba(238,241,245,.72)}
#smart-guide .g1-smart-stats b{color:#82a9df;font:650 25px/1 Inter,Arial,sans-serif;min-width:30px;text-align:center}
#smart-guide .g1-smart-stats em{font-style:normal;font-size:11px;line-height:1.7;white-space:nowrap}

@media(max-width:1100px){
  body.gramiss-next-staging #smart-guide .g1-smart-v3{grid-template-columns:1fr!important}
  body.gramiss-next-staging #smart-guide .g1-smart-copy{padding:58px 48px 48px!important}
  #smart-guide .g1-smart-copy h2{max-width:620px}
  body.gramiss-next-staging #smart-guide .g1-smart-visual{min-height:600px!important}
}
@media(max-width:760px){
  body.gramiss-next-staging #smart-guide .g1-smart-v3{min-height:0!important;border-radius:28px!important}
  body.gramiss-next-staging #smart-guide .g1-smart-copy{padding:44px 24px 38px!important;align-items:stretch}
  #smart-guide .g1-smart-copy small{margin-bottom:18px}
  #smart-guide .g1-smart-copy h2{font-size:clamp(38px,10.5vw,49px);line-height:1.42;margin-bottom:20px}
  #smart-guide .g1-smart-copy h2 span{white-space:normal}
  #smart-guide .g1-smart-copy p{font-size:12.5px;line-height:2}
  #smart-guide .g1-smart-features{margin:28px 0 31px}
  #smart-guide .g1-smart-features span{padding-inline:8px;gap:8px}
  #smart-guide .g1-smart-features span+span{padding-inline-start:10px}
  #smart-guide .g1-smart-features em{font-size:9px;white-space:normal}
  #smart-guide .g1-smart-actions{align-items:stretch}
  body.gramiss-next-staging #smart-guide .g1-smart-cta{width:100%;min-width:0}
  #smart-guide .g1-smart-how{align-self:center}
  body.gramiss-next-staging #smart-guide .g1-smart-visual{min-height:430px!important}
  #smart-guide .g1-smart-map{width:235px;height:235px;top:47%}
  #smart-guide .g1-smart-core{width:86px;height:86px;font-size:28px}
  #smart-guide .g1-smart-node{width:58px;height:58px;gap:3px}
  #smart-guide .g1-smart-node svg{width:15px;height:15px}
  #smart-guide .g1-smart-node b{font-size:8px}
  #smart-guide .g1-smart-product-card{width:78px;padding:6px;border-radius:10px;opacity:.32}
  #smart-guide .g1-smart-product-card.is-cap{left:4%;top:11%}
  #smart-guide .g1-smart-product-card.is-tee{right:5%;top:12%}
  #smart-guide .g1-smart-product-card.is-bag{left:3%;bottom:18%}
  #smart-guide .g1-smart-product-card.is-sneaker{right:4%;bottom:20%}
  #smart-guide .g1-smart-product-card.is-pants{bottom:4%}
  #smart-guide .g1-smart-stats{left:5%;bottom:4%;min-width:150px;padding-inline-start:12px;gap:4px}
  #smart-guide .g1-smart-stats b{font-size:18px}
  #smart-guide .g1-smart-stats em{font-size:9px}
}
'''

front = mod.read('front-page.php')
css = mod.read('assets/css/gramiss-1.css')
print('PRE_HOME_SHA', mod.sha(front))
print('PRE_CSS_SHA', mod.sha(css))
if mod.sha(front) != EXPECTED_HOME:
    raise SystemExit('REFUSE: Home changed since V2')
if mod.sha(css) != EXPECTED_CSS:
    raise SystemExit('REFUSE: CSS changed since V2')
for path, expected in PROTECTED.items():
    actual = mod.sha(mod.read(path))
    print('PROTECTED_PRE', path, actual)
    if actual != expected:
        raise SystemExit('REFUSE: protected drift ' + path)

home_start = front.find('<section class="g1-section g1-reveal" id="smart-guide">')
home_end = front.find('<section class="g1-section g1-reveal" id="journal">', home_start)
if home_start < 0 or home_end < 0:
    raise SystemExit('REFUSE: Smart Guide/JOURNAL anchors missing')
old_prefix = front[:home_start]
old_suffix = front[home_end:]
new_front = old_prefix + NEW_BLOCK + old_suffix

css_start = css.find('/* GRAMISS_HOME_SMART_GUIDE_V2')
css_end = css.find('.g1-editorial-grid{', css_start)
if css_start < 0 or css_end < 0:
    raise SystemExit('REFUSE: V2 CSS block missing')
new_css = css[:css_start] + NEW_CSS + '\n\n' + css[css_end:]

stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
front_backup = 'front-page.php.bak-smart-guide-v3-' + stamp
css_backup = 'assets/css/gramiss-1.css.bak-smart-guide-v3-' + stamp
try:
    mod.save(front_backup, front)
    mod.save(css_backup, css)
    mod.save('front-page.php', new_front)
    mod.save('assets/css/gramiss-1.css', new_css)
    mod.flush()

    errors = []
    stored_front = mod.read('front-page.php')
    stored_css = mod.read('assets/css/gramiss-1.css')
    print('POST_HOME_SHA', mod.sha(stored_front))
    print('POST_CSS_SHA', mod.sha(stored_css))
    if not stored_front.startswith(old_prefix):
        errors.append('Home prefix changed')
    if not stored_front.endswith(old_suffix):
        errors.append('Home suffix changed')
    if 'GRAMISS_HOME_SMART_GUIDE_V3' not in stored_css:
        errors.append('V3 CSS marker missing')
    if 'GRAMISS_HOME_SMART_GUIDE_V2' in stored_css:
        errors.append('V2 CSS marker remains')
    for path, expected in PROTECTED.items():
        if mod.sha(mod.read(path)) != expected:
            errors.append('protected changed ' + path)

    status, page = mod.get(mod.BASE + '/?smart-guide-v3=' + str(time.time()), 180)
    print('HOME_HTTP', status, 'BYTES', len(page.encode()))
    if status != 200:
        errors.append('Home HTTP ' + str(status))
    required = [
        'g1-smart-v3', 'GRAMISS / SMART GUIDE', 'فروشنده‌ای آرام،', 'دقیق و بی‌قضاوت.',
        'چند سؤال کوتاه درباره استایل، کاربرد و بودجه؛', 'g1-smart-product-card',
        'گ1-smart-map'.replace('گ1','g1'), '۱۲', '۳', 'g1-looks', 'id="collections"', 'id="products"', 'id="journal"'
    ]
    for marker in required:
        if marker not in page:
            errors.append('render missing ' + marker)
    if len(re.findall(r'<h1\b', page, re.I)) != 1:
        errors.append('Home H1 count changed')
    image_cards = len(re.findall(r'g1-smart-product-card[^>]*>.*?<img\b', page, re.I | re.S))
    print('SMART_PRODUCT_IMAGE_CARDS', image_cards)
    if image_cards < 4:
        errors.append('fewer than 4 real Smart Guide product images')

    print('VERIFY_ERRORS', json.dumps(errors, ensure_ascii=False))
    if errors:
        raise RuntimeError('; '.join(errors))
    print('FRONT_BACKUP', front_backup)
    print('CSS_BACKUP', css_backup)
    print('PASS HOME SMART GUIDE V3 DEPLOY')
except Exception:
    mod.save('front-page.php', front)
    mod.save('assets/css/gramiss-1.css', css)
    mod.flush()
    print('ROLLBACK_HOME_SHA', mod.sha(mod.read('front-page.php')))
    print('ROLLBACK_CSS_SHA', mod.sha(mod.read('assets/css/gramiss-1.css')))
    raise
