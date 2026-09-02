import hashlib
import html
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

HOST = os.environ['CPANEL_HOST']
USER = os.environ['CPANEL_USER']
TOKEN = os.environ['CPANEL_TOKEN']
ROOT = os.environ['THEME_ROOT'].strip('/')
CTX = ssl._create_unverified_context()
BASE = 'https://gramiss.ir'
PHP_TARGET = 'woocommerce.php'
PHP_SHA = '788789512eee810604b84c426c6c6ece0be4e5eca7f56c6b4cabb5db0d4491f8'
CSS_TARGET = 'assets/css/shop-premium-shell.css'
CSS_SHA = '7f959030695a814fa5df1eb6557f5dc9754ca9f28f5d668180b26c6eae0e7378'
PRODUCT_SHA = '70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'
PCAT_SHA = '75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PHP_MARKER = 'GRAMISS_CATEGORY_SEO_COPY_V1'
CSS_MARKER = 'GRAMISS_CATEGORY_SEO_COPY_CSS_V1'
TARGET_SLUGS = ['tshirt', 'pants', 'shirt', 'sneakers', 'hat']
PROTECTED = {
    'front-page.php': '0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}


def api(fn, params, post=False):
    url = f'https://{HOST}:2083/execute/Fileman/{fn}'
    encoded = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url if post else url + '?' + encoded.decode(), data=encoded if post else None, method='POST' if post else 'GET')
            req.add_header('Authorization', f'cpanel {USER}:{TOKEN}')
            if post:
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, context=CTX, timeout=90) as response:
                payload = json.loads(response.read().decode('utf-8', 'replace'))
            result = payload.get('result') if isinstance(payload.get('result'), dict) else payload
            if not isinstance(result, dict) or result.get('status') != 1:
                raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last = exc
            print('API_RETRY', fn, attempt + 1, exc)
            time.sleep(attempt + 1)
    raise last


def read_theme(rel):
    directory, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    data = api('get_file_content', {'dir': ROOT if not directory else ROOT + '/' + directory, 'file': name, 'from_charset': '_DETECT_', 'to_charset': 'utf-8'})
    if isinstance(data, dict):
        for key in ('content', 'file_content', 'data'):
            if isinstance(data.get(key), str):
                return data[key]
    return data if isinstance(data, str) else ''


def write_theme(rel, content):
    directory, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    return api('save_file_content', {'dir': ROOT if not directory else ROOT + '/' + directory, 'file': name, 'content': content, 'from_charset': 'UTF-8', 'to_charset': 'UTF-8', 'fallback': '0'}, True)


def save_public(name, content):
    return api('save_file_content', {'dir': 'public_html', 'file': name, 'content': content, 'from_charset': 'UTF-8', 'to_charset': 'UTF-8', 'fallback': '0'}, True)


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@'), urllib.parse.quote(urllib.parse.unquote(p.query), safe='=&%:@,+'), p.fragment))


def get(url, timeout=180):
    url = safe_url(url)
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'GramissCategoryMoneyPageWave1/1.0', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as response:
                return response.status, response.read(), response.geturl()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), exc.geturl()
        except Exception as exc:
            last = exc
            print('HTTP_RETRY', attempt + 1, url, exc)
            time.sleep(attempt + 1)
    raise last


def norm(url):
    if not url:
        return ''
    return urllib.parse.unquote(url).split('?', 1)[0].rstrip('/') + '/'


def strip_markup(value):
    value = re.sub(r'<script\b[^>]*>.*?</script>', ' ', value or '', flags=re.I | re.S)
    value = re.sub(r'<style\b[^>]*>.*?</style>', ' ', value, flags=re.I | re.S)
    value = re.sub(r'<[^>]+>', ' ', value)
    return re.sub(r'\s+', ' ', html.unescape(value)).strip()


def attr(tag, name):
    m = re.search(r'\b' + re.escape(name) + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return html.unescape(m.group(1)).strip() if m else ''


def parse_head(raw):
    text = raw.decode('utf-8', 'replace')
    head = text.split('</head>', 1)[0]
    title_m = re.search(r'<title[^>]*>(.*?)</title>', head, re.I | re.S)
    title = strip_markup(title_m.group(1)) if title_m else ''
    description = ''
    robots = ''
    canonical = ''
    for tag in re.findall(r'<meta\b[^>]*>', head, re.I | re.S):
        name = attr(tag, 'name').lower()
        if name == 'description':
            description = attr(tag, 'content')
        elif name == 'robots':
            robots = attr(tag, 'content')
    for tag in re.findall(r'<link\b[^>]*>', head, re.I | re.S):
        if 'canonical' in attr(tag, 'rel').lower().split():
            canonical = attr(tag, 'href')
            break
    return {'title': title, 'description': description, 'robots': robots, 'canonical': norm(canonical)}


def inspect(url):
    status, raw, final = get(url + ('&' if '?' in url else '?') + 'g1cw1=' + str(int(time.time() * 1000)), 180)
    text = raw.decode('utf-8', 'replace')
    h1_tags = re.findall(r'<h1\b[^>]*>.*?</h1>', text, re.I | re.S)
    native = [x for x in h1_tags if re.search(r'class=["\'][^"\']*\bpage-title\b', x, re.I)]
    premium = [x for x in h1_tags if re.search(r'id=["\']gramiss-premium-shop-title["\']', x, re.I)]
    seo_match = re.search(r'<section\b[^>]*class=["\'][^"\']*\bgramiss-category-seo-copy\b[^"\']*["\'][^>]*>(.*?)</section>', text, re.I | re.S)
    seo_html = seo_match.group(1) if seo_match else ''
    return {
        'status': status,
        'final': norm(final),
        'head': parse_head(raw),
        'h1_count': len(h1_tags),
        'native_count': len(native),
        'premium_count': len(premium),
        'seo_copy_count': len(re.findall(r'gramiss-category-seo-copy', text, re.I)),
        'seo_text': strip_markup(seo_html),
        'seo_html': seo_html,
        'hero_pos': text.find('gramiss-shop-premium-hero'),
        'products_pos': text.find('<ul class="products'),
        'seo_pos': text.find('gramiss-category-seo-copy'),
        'default_term_description_pos': text.find('class="term-description"'),
    }


def sitemap(path):
    status, raw, _ = get(BASE + '/' + path + '?g1cw1=' + str(int(time.time() * 1000)), 150)
    urls = sorted(html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>', raw.decode('utf-8', 'replace'), re.I))
    return status, urls, hashlib.sha256('\n'.join(urls).encode()).hexdigest()


def purge():
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-content-wave1-purge-' + nonce + '.php'
    php = r'''<?php
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
if (function_exists('wp_cache_flush')) { wp_cache_flush(); }
if (has_action('litespeed_purge_all')) { do_action('litespeed_purge_all'); }
header('Content-Type: text/plain; charset=utf-8');
echo 'PURGED';
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 120)
    print('PURGE', status, raw.decode('utf-8', 'replace')[:120])
    if status != 200 or b'PURGED' not in raw:
        raise RuntimeError('cache purge failed')


def safety(label):
    errors = []
    protected = {path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in PROTECTED}
    for path, expected in PROTECTED.items():
        if protected.get(path) != expected:
            errors.append('protected drift ' + path)
    ps, pu, ph = sitemap('product-sitemap.xml')
    cs, cu, ch = sitemap('product_cat-sitemap.xml')
    if ps != 200 or len(pu) != 47 or ph != PRODUCT_SHA:
        errors.append('product sitemap drift')
    if cs != 200 or len(cu) != 20 or ch != PCAT_SHA:
        errors.append('product_cat sitemap drift')
    print('SAFETY', label, json.dumps({'protected': protected, 'product': [ps, len(pu), ph], 'product_cat': [cs, len(cu), ch], 'errors': errors}, sort_keys=True))
    if errors:
        raise RuntimeError('; '.join(errors))
    return cu


def wp_state():
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave1-state-' + nonce + '.php'
    php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$slugs=['tshirt','pants','shirt','sneakers','hat','fitted-cap'];
$out=[];
foreach($slugs as $slug){$t=get_term_by('slug',$slug,'product_cat');if(!$t)continue;$u=get_term_link($t);$out[$slug]=['id'=>(int)$t->term_id,'name'=>$t->name,'description'=>$t->description,'url'=>is_wp_error($u)?'':$u,'count'=>(int)$t->count];}
echo wp_json_encode(['terms'=>$out], JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 180)
    if status != 200:
        raise RuntimeError('wp state HTTP ' + str(status))
    return json.loads(raw.decode('utf-8', 'replace'))


def mutate_terms():
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave1-mutate-' + nonce + '.php'
    php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
function g1u($v){return esc_url($v);}
function g1term($slug){$t=get_term_by('slug',$slug,'product_cat');if(!$t)return '';$u=get_term_link($t);return is_wp_error($u)?'':$u;}
$u471=get_permalink(471);$u453=get_permalink(453);$u459=get_permalink(459);$u460=get_permalink(460);$u463=get_permalink(463);$u464=get_permalink(464);$u467=get_permalink(467);$u468=get_permalink(468);$u472=get_permalink(472);$u482=get_permalink(482);$u483=get_permalink(483);$u487=get_permalink(487);$u488=get_permalink(488);$u493=get_permalink(493);$u497=get_permalink(497);$u503=get_permalink(503);
$copy=[];
$copy['tshirt']='<h2>خرید تیشرت مردانه؛ انتخاب فیت، مدل و جزئیات</h2><p>در دسته تیشرت مردانه Gramiss می‌توانید مدل‌های موجود را بر اساس فرم لباس و جزئیات ظاهری مقایسه کنید. برای رسیدن سریع‌تر به گزینه مناسب، دسته‌های <a href="'.g1u(g1term('graphic-tshirt')).'">تیشرت چاپی</a>، <a href="'.g1u(g1term('oversized-tshirt')).'">تیشرت اورسایز</a>، <a href="'.g1u(g1term('crewneck-tshirt')).'">تیشرت یقه‌گرد</a> و <a href="'.g1u(g1term('polo-tshirt')).'">تیشرت یقه‌دار</a> را جداگانه ببینید.</p><p>برای خرید تیشرت فقط به برچسب سایز تکیه نکنید؛ اندازه واقعی لباس، قد، عرض سینه، سرشانه، نوع فیت و اطلاعات پارچه یا چاپی که در صفحه محصول اعلام شده مهم‌تر است. <a href="'.g1u($u471).'">راهنمای خرید تیشرت مردانه</a> معیارهای اصلی مقایسه را یک‌جا توضیح می‌دهد. اگر بین فرم‌های آزاد مردد هستید، <a href="'.g1u($u453).'">تفاوت تیشرت باکسی و اورسایز</a> و <a href="'.g1u($u459).'">راهنمای انتخاب سایز تیشرت باکسی</a> مسیر دقیق‌تری برای انتخاب می‌دهند.</p><h3>قبل از انتخاب چه چیزهایی را مقایسه کنید؟</h3><ul><li>قد و عرض لباس نسبت به فیتی که می‌خواهید.</li><li>فرم یقه، آستین و سرشانه در عکس‌ها و مشخصات محصول.</li><li>رنگ، طرح چاپ و اطلاعات جنس پارچه فقط بر اساس مشخصات همان محصول.</li><li>جدول سایز و اندازه‌های واقعی به‌جای حدس از روی نام سایز.</li></ul>';
$copy['pants']='<h2>خرید شلوار مردانه بر اساس فیت و کاربرد</h2><p>دسته شلوار مردانه Gramiss برای مقایسه مدل‌های موجود از نظر فرم، قد و حجم طراحی شده است. می‌توانید مستقیماً سراغ <a href="'.g1u(g1term('jeans')).'">شلوار جین</a>، <a href="'.g1u(g1term('fabric-pants')).'">شلوار پارچه‌ای</a> یا <a href="'.g1u(g1term('cargo-pants')).'">شلوار کارگو</a> بروید و گزینه‌ها را در همان خانواده بررسی کنید.</p><p>در انتخاب شلوار، نام فیت به‌تنهایی کافی نیست. اندازه کمر، فاق، ران، عرض دمپا و قد شلوار تعیین می‌کند یک مدل در عمل چطور روی بدن و روی کفش می‌ایستد. برای جین، <a href="'.g1u($u472).'">راهنمای خرید شلوار جین مردانه</a> و برای مدل‌های پارچه‌ای، <a href="'.g1u($u497).'">راهنمای خرید شلوار پارچه‌ای مردانه</a> معیارهای مقایسه را مرحله‌به‌مرحله توضیح می‌دهند. اگر درباره حجم فیت‌ها مطمئن نیستید، <a href="'.g1u($u460).'">تفاوت شلوار بگ، نیم‌بگ و فول‌بگ</a> را ببینید.</p><h3>برای انتخاب بهتر</h3><ul><li>اندازه واقعی کمر و ران را با شلواری که تن‌خورش را دوست دارید مقایسه کنید.</li><li>قد شلوار را همراه کفشی که معمولاً می‌پوشید در نظر بگیرید.</li><li>برای ساخت استایل، حجم شلوار و بالاتنه را با هم ببینید؛ <a href="'.g1u($u468).'">راهنمای استایل شلوار بگ</a> چند ترکیب کاربردی دارد.</li></ul>';
$copy['shirt']='<h2>خرید پیراهن مردانه؛ انتخاب قواره، آستین و کاربرد</h2><p>در دسته پیراهن مردانه Gramiss می‌توانید مدل‌های موجود را بین <a href="'.g1u(g1term('casual-shirt')).'">پیراهن اسپرت</a>، <a href="'.g1u(g1term('short-sleeve-shirt')).'">آستین کوتاه</a>، <a href="'.g1u(g1term('long-sleeve-shirt')).'">آستین بلند</a> و <a href="'.g1u(g1term('linen-shirt')).'">پیراهن لینن</a> مقایسه کنید. نام دسته فقط نقطه شروع است؛ قواره واقعی، سرشانه، دور سینه، قد و آستین را از مشخصات همان محصول بررسی کنید.</p><p>اگر خرید آنلاین انجام می‌دهید، <a href="'.g1u($u487).'">راهنمای انتخاب سایز پیراهن مردانه</a> نشان می‌دهد کدام اندازه‌ها برای مقایسه مهم‌ترند. برای مدل‌هایی که با عنوان لینن عرضه می‌شوند، ترکیب الیاف و دستور مراقبت روی برچسب یا مشخصات همان محصول اولویت دارد؛ <a href="'.g1u($u463).'">راهنمای شناخت پارچه لینن</a> و <a href="'.g1u($u464).'">راهنمای شست‌وشوی پیراهن لینن</a> به شما کمک می‌کنند ادعاهای عمومی را با اطلاعات واقعی لباس اشتباه نگیرید.</p><h3>استایل و انتخاب مدل</h3><p>برای ساخت ترکیب روزمره یا اسمارت‌کژوال، فرم شلوار و کفش را کنار قواره پیراهن ببینید. <a href="'.g1u($u467).'">استایل با پیراهن لینن</a> و <a href="'.g1u($u503).'">استایل با پیراهن آستین کوتاه</a> مثال‌های بیشتری برای هماهنگ‌کردن حجم و رنگ دارند.</p>';
$copy['sneakers']='<h2>خرید کتونی مردانه؛ سایز، کاربرد و جزئیات ساخت</h2><p>در دسته کتونی مردانه Gramiss می‌توانید مدل‌های موجود را برای استفاده روزمره و پیاده‌روی بررسی کنید. ظاهر مهم است، اما برای خرید آنلاین بهتر است طول واقعی پا، قالب مدل و اطلاعات سایز همان محصول را قبل از انتخاب نهایی بررسی کنید. اگر بین دو سایز مردد هستید، <a href="'.g1u($u482).'">راهنمای انتخاب سایز کتانی مردانه</a> روش اندازه‌گیری پا و مقایسه با جدول سایز را توضیح می‌دهد.</p><p>برای مقایسه کتونی‌ها، فقط به نام سبک یا ظاهر رویه اکتفا نکنید. اطلاعات اعلام‌شده درباره رویه، زیره، نحوه بسته‌شدن، سایزهای موجود و کاربرد محصول را کنار هم ببینید. <a href="'.g1u($u483).'">راهنمای خرید کتانی مردانه برای استفاده روزمره</a> یک چک‌لیست ساده برای همین مقایسه دارد.</p><h3>نگهداری بعد از خرید</h3><p>روش تمیزکردن باید با جنس همان کفش سازگار باشد. برای مدل‌های روشن می‌توانید از <a href="'.g1u($u488).'">راهنمای تمیز کردن کتانی سفید</a> شروع کنید، اما همیشه دستور مراقبت محصول را بر توصیه‌های عمومی مقدم بدانید.</p>';
$copy['hat']='<h2>خرید کلاه مردانه؛ انتخاب فرم و اندازه مناسب</h2><p>در دسته کلاه مردانه Gramiss مدل‌های موجود را می‌توانید بر اساس فرم، رنگ و نحوه قرارگرفتن روی سر مقایسه کنید. اگر تمرکز شما روی فرم‌های کپ است، وارد دسته <a href="'.g1u(g1term('fitted-cap')).'">فیت کپ</a> شوید تا مدل‌های همان خانواده را کنار هم ببینید.</p><p>برای خرید آنلاین کلاه، اندازه دور سر مهم‌تر از حدس‌زدن بر اساس ظاهر عکس است. محل قرارگیری متر، میزان آزادی دلخواه و ساختار خود کلاه می‌تواند روی انتخاب اثر بگذارد. <a href="'.g1u($u493).'">راهنمای انتخاب سایز کلاه فیت کپ</a> روش اندازه‌گیری دور سر را قدم‌به‌قدم توضیح می‌دهد.</p><h3>قبل از انتخاب بررسی کنید</h3><ul><li>دور سر و اطلاعات سایز یا تنظیم‌پذیری همان مدل.</li><li>فرم تاج، نقاب و تناسب آن با استایلی که می‌خواهید.</li><li>رنگ و جزئیات محصول در تصاویر واقعی همان کالا.</li><li>جنس و روش نگهداری فقط بر اساس اطلاعات درج‌شده برای همان محصول.</li></ul>';
$result=[];
foreach($copy as $slug=>$description){$t=get_term_by('slug',$slug,'product_cat');if(!$t){$result[$slug]=['error'=>'missing'];continue;}$r=wp_update_term($t->term_id,'product_cat',['description'=>$description]);if(is_wp_error($r)){$result[$slug]=['error'=>$r->get_error_message()];}else{$fresh=get_term($t->term_id,'product_cat');$result[$slug]=['id'=>(int)$t->term_id,'chars'=>mb_strlen(wp_strip_all_tags($fresh->description))];}}
echo wp_json_encode(['result'=>$result],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 240)
    print('MUTATE_TERMS_HTTP', status, raw.decode('utf-8', 'replace')[:2000])
    if status != 200:
        raise RuntimeError('term mutation HTTP ' + str(status))
    payload = json.loads(raw.decode('utf-8', 'replace'))
    for slug in TARGET_SLUGS:
        row = payload.get('result', {}).get(slug, {})
        if row.get('error') or int(row.get('chars', 0)) < 300:
            raise RuntimeError('term mutation failed ' + slug + ' ' + json.dumps(row, ensure_ascii=False))


def restore_terms(pre):
    terms = pre.get('terms', {})
    payload = {slug: terms.get(slug, {}).get('description', '') for slug in TARGET_SLUGS}
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave1-restore-' + nonce + '.php'
    php = "<?php\nheader('Content-Type: application/json; charset=utf-8');\ndefine('WP_USE_THEMES', false);\nrequire __DIR__ . '/wp-load.php';\n@unlink(__FILE__);\n$copy=" + json.dumps(payload, ensure_ascii=False).replace('"', "'") + ";\n$out=[];foreach($copy as $slug=>$description){$t=get_term_by('slug',$slug,'product_cat');if(!$t)continue;$r=wp_update_term($t->term_id,'product_cat',['description'=>$description]);$out[$slug]=is_wp_error($r)?$r->get_error_message():'ok';}\necho wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);\n?>"
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 180)
    print('RESTORE_TERMS', status, raw.decode('utf-8', 'replace')[:1000])
    if status != 200:
        raise RuntimeError('restore terms HTTP ' + str(status))


sitemap_urls = safety('PRE')
pre_state = wp_state()
terms = pre_state.get('terms', {})
for slug in TARGET_SLUGS:
    row = terms.get(slug)
    if not row or not row.get('url'):
        raise SystemExit('FAIL PRECONDITION missing target ' + slug)
    if strip_markup(row.get('description', '')):
        raise SystemExit('FAIL PRECONDITION target description not empty ' + slug)

pre_pages = {slug: inspect(terms[slug]['url']) for slug in TARGET_SLUGS}
for slug, row in pre_pages.items():
    if row['status'] != 200 or row['h1_count'] != 1 or row['native_count'] != 0 or row['premium_count'] != 1:
        raise SystemExit('FAIL PRECONDITION page state ' + slug + ' ' + json.dumps(row, ensure_ascii=False))
    if row['seo_copy_count'] != 0:
        raise SystemExit('FAIL PRECONDITION seo copy already present ' + slug)
print('PRE_PAGES', json.dumps({s:[r['h1_count'],r['seo_copy_count']] for s,r in pre_pages.items()}, ensure_ascii=False, sort_keys=True))

old_php = read_theme(PHP_TARGET)
old_css = read_theme(CSS_TARGET)
old_php_sha = hashlib.sha256(old_php.encode()).hexdigest()
old_css_sha = hashlib.sha256(old_css.encode()).hexdigest()
print('TARGET_PRE', PHP_TARGET, old_php_sha, CSS_TARGET, old_css_sha)
if old_php_sha != PHP_SHA or PHP_MARKER in old_php:
    raise SystemExit('FAIL PHP TARGET DRIFT')
if old_css_sha != CSS_SHA or CSS_MARKER in old_css:
    raise SystemExit('FAIL CSS TARGET DRIFT')
if 'GRAMISS_CATEGORY_SINGLE_H1_V2' not in old_php or old_php.count('get_header();') != 1:
    raise SystemExit('FAIL PHP TARGET MARKERS')

php_patch = r'''/* GRAMISS_CATEGORY_SEO_COPY_V1
 * Keep product discovery first: remove the default taxonomy description above
 * the Gramiss hero and render the same term description after the product grid
 * on page 1 only. This changes presentation, not canonical/indexation logic.
 */
if ( ! function_exists( 'gramiss_category_seo_copy_v1' ) ) {
    function gramiss_category_seo_copy_v1(): void {
        if ( ! function_exists( 'is_product_category' ) || ! is_product_category() || is_paged() ) {
            return;
        }
        $term = get_queried_object();
        if ( ! ( $term instanceof WP_Term ) ) {
            return;
        }
        $description = term_description( $term, 'product_cat' );
        if ( ! trim( wp_strip_all_tags( $description ) ) ) {
            return;
        }
        echo '<section class="gramiss-category-seo-copy" dir="rtl">';
        echo '<div class="gramiss-category-seo-copy__inner">' . wp_kses_post( $description ) . '</div>';
        echo '</section>';
    }
}
if ( function_exists( 'is_product_category' ) && is_product_category() ) {
    remove_action( 'woocommerce_archive_description', 'woocommerce_taxonomy_archive_description', 10 );
    add_action( 'woocommerce_after_shop_loop', 'gramiss_category_seo_copy_v1', 40 );
}

'''
css_patch = r'''
/* GRAMISS_CATEGORY_SEO_COPY_CSS_V1
 * Quiet editorial support below category product grids. Product cards and hero
 * dimensions are intentionally untouched.
 */
body.tax-product_cat .gramiss-category-seo-copy{
  width:min(100% - 48px,1540px);
  margin:38px auto 74px;
  padding:0;
  direction:rtl;
}
body.tax-product_cat .gramiss-category-seo-copy__inner{
  max-width:1060px;
  margin:0 auto;
  padding:28px 0 0;
  border-top:1px solid rgba(17,19,24,.09);
  color:#343434;
  font-size:15px;
  line-height:2;
}
body.tax-product_cat .gramiss-category-seo-copy h2{
  margin:0 0 12px;
  color:#171717;
  font-size:clamp(20px,2vw,27px);
  line-height:1.55;
  font-weight:750;
}
body.tax-product_cat .gramiss-category-seo-copy h3{
  margin:24px 0 8px;
  color:#1f1f1f;
  font-size:17px;
  line-height:1.7;
  font-weight:700;
}
body.tax-product_cat .gramiss-category-seo-copy p{margin:0 0 12px;}
body.tax-product_cat .gramiss-category-seo-copy ul{margin:8px 0 0;padding:0 20px 0 0;}
body.tax-product_cat .gramiss-category-seo-copy li{margin:5px 0;}
body.tax-product_cat .gramiss-category-seo-copy a{
  color:inherit;
  text-decoration:underline;
  text-decoration-thickness:1px;
  text-underline-offset:3px;
}
@media (max-width:760px){
  body.tax-product_cat .gramiss-category-seo-copy{width:min(100% - 28px,1540px);margin:28px auto 54px;}
  body.tax-product_cat .gramiss-category-seo-copy__inner{padding-top:22px;font-size:14px;line-height:1.95;}
}
'''

changed_files = False
changed_terms = False
try:
    new_php = old_php.replace('get_header();', php_patch + 'get_header();', 1)
    new_css = old_css.rstrip() + '\n' + css_patch + '\n'
    write_theme(PHP_TARGET, new_php)
    write_theme(CSS_TARGET, new_css)
    changed_files = True
    print('TARGET_WRITTEN', hashlib.sha256(new_php.encode()).hexdigest(), hashlib.sha256(new_css.encode()).hexdigest())

    mutate_terms()
    changed_terms = True
    purge()
    time.sleep(2)
    safety('POST')

    post_state = wp_state()
    post_terms = post_state.get('terms', {})
    for slug in TARGET_SLUGS:
        if len(strip_markup(post_terms.get(slug, {}).get('description', ''))) < 300:
            raise RuntimeError('stored description too short ' + slug)

    post_pages = {slug: inspect(post_terms[slug]['url']) for slug in TARGET_SLUGS}
    errors = []
    for slug, after in post_pages.items():
        before = pre_pages[slug]
        if after['status'] != 200:
            errors.append(slug + ' HTTP')
        if after['h1_count'] != 1 or after['native_count'] != 0 or after['premium_count'] != 1:
            errors.append(slug + ' H1')
        if after['head'] != before['head']:
            errors.append(slug + ' metadata changed')
        if after['default_term_description_pos'] >= 0:
            errors.append(slug + ' default term description still before hero')
        if after['seo_copy_count'] < 1 or len(after['seo_text']) < 300:
            errors.append(slug + ' SEO copy missing/thin')
        if after['seo_pos'] <= after['products_pos'] or after['products_pos'] < 0:
            errors.append(slug + ' SEO copy not after products')
    fitted = post_terms.get('fitted-cap')
    if not fitted or strip_markup(fitted.get('description', '')) != strip_markup(terms.get('fitted-cap', {}).get('description', '')):
        errors.append('fitted-cap stored description changed')
    if fitted and fitted.get('url'):
        fpage = inspect(fitted['url'])
        if fpage['default_term_description_pos'] >= 0 or fpage['seo_pos'] <= fpage['products_pos'] or strip_markup(terms['fitted-cap']['description']) not in fpage['seo_text']:
            errors.append('fitted-cap relocation failed')
    print('POST_PAGES', json.dumps({s:{'h1':r['h1_count'],'seo_chars':len(r['seo_text']),'hero':r['hero_pos'],'products':r['products_pos'],'seo':r['seo_pos']} for s,r in post_pages.items()}, ensure_ascii=False, sort_keys=True))
    if errors:
        raise RuntimeError(' | '.join(errors))
except Exception as exc:
    print('VERIFY_FAIL', repr(exc))
    rollback_errors = []
    if changed_terms:
        try:
            restore_terms(pre_state)
        except Exception as rex:
            rollback_errors.append('terms ' + repr(rex))
    if changed_files:
        try:
            write_theme(PHP_TARGET, old_php)
            write_theme(CSS_TARGET, old_css)
        except Exception as rex:
            rollback_errors.append('files ' + repr(rex))
    try:
        purge()
        time.sleep(2)
        safety('ROLLBACK')
    except Exception as rex:
        rollback_errors.append('safety ' + repr(rex))
    restored_php = hashlib.sha256(read_theme(PHP_TARGET).encode()).hexdigest()
    restored_css = hashlib.sha256(read_theme(CSS_TARGET).encode()).hexdigest()
    print('ROLLBACK_HASHES', restored_php, restored_css, 'errors', rollback_errors)
    if restored_php != old_php_sha or restored_css != old_css_sha or rollback_errors:
        raise SystemExit('CRITICAL ROLLBACK FAILURE ' + ' | '.join(rollback_errors))
    raise

final_php = hashlib.sha256(read_theme(PHP_TARGET).encode()).hexdigest()
final_css = hashlib.sha256(read_theme(CSS_TARGET).encode()).hexdigest()
print('PASS CATEGORY MONEY PAGE CONTENT WAVE 1', final_php, final_css)
