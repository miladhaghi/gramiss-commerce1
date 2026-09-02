import base64
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
PHP_SHA = '4f518fdbc1fdf84c2b4efb065af1129345d56fe121b2a67e8ab78a7e9719c21b'
CSS_TARGET = 'assets/css/shop-premium-shell.css'
CSS_SHA = 'b20eba9bedbe2dc0f1115b4b63dd7deff1eaf6cb9dcfb17801d0e803eb8a21e2'
PRODUCT_SHA = '70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'
PCAT_SHA = '75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
TARGET_SLUGS = ['jeans', 'oversized-tshirt', 'graphic-tshirt', 'crewneck-tshirt', 'casual-shirt', 'fitted-cap']
FITTED_PRE = 'کلاه فیت‌کپ AFT با پارچه کتان، فرم مینیمال و قابلیت تنظیم؛ مناسب استایل روزمره.'
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
            req = urllib.request.Request(url, headers={'User-Agent': 'GramissCategoryMoneyPageWave2/1.0', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
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
    status, raw, final = get(url + ('&' if '?' in url else '?') + 'g1cw2=' + str(int(time.time() * 1000)), 180)
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
        'seo_text': strip_markup(seo_html),
        'seo_html': seo_html,
        'seo_pos': text.find('gramiss-category-seo-copy'),
        'products_pos': text.find('<ul class="products'),
        'default_term_description_pos': text.find('class="term-description"'),
        'internal_links': [html.unescape(x) for x in re.findall(r'href=["\']([^"\']+)', seo_html, re.I) if 'gramiss.ir' in x],
    }


def sitemap(path):
    status, raw, _ = get(BASE + '/' + path + '?g1cw2=' + str(int(time.time() * 1000)), 150)
    urls = sorted(html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>', raw.decode('utf-8', 'replace'), re.I))
    return status, urls, hashlib.sha256('\n'.join(urls).encode()).hexdigest()


def purge():
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-content-wave2-purge-' + nonce + '.php'
    php = r'''<?php
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
if (function_exists('wp_cache_flush')) { wp_cache_flush(); }
if (has_action('litespeed_purge_all')) { do_action('litespeed_purge_all'); }
header('Content-Type: text/plain; charset=utf-8'); echo 'PURGED';
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
    php_sha = hashlib.sha256(read_theme(PHP_TARGET).encode()).hexdigest()
    css_sha = hashlib.sha256(read_theme(CSS_TARGET).encode()).hexdigest()
    if php_sha != PHP_SHA:
        errors.append('woocommerce.php drift')
    if css_sha != CSS_SHA:
        errors.append('shop-premium-shell.css drift')
    ps, pu, ph = sitemap('product-sitemap.xml')
    cs, cu, ch = sitemap('product_cat-sitemap.xml')
    if ps != 200 or len(pu) != 47 or ph != PRODUCT_SHA:
        errors.append('product sitemap drift')
    if cs != 200 or len(cu) != 20 or ch != PCAT_SHA:
        errors.append('product_cat sitemap drift')
    print('SAFETY', label, json.dumps({'php': php_sha, 'css': css_sha, 'protected': protected, 'product': [ps, len(pu), ph], 'product_cat': [cs, len(cu), ch], 'errors': errors}, sort_keys=True))
    if errors:
        raise RuntimeError('; '.join(errors))


def wp_state():
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave2-state-' + nonce + '.php'
    php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false); require __DIR__ . '/wp-load.php'; @unlink(__FILE__);
$slugs=['jeans','oversized-tshirt','graphic-tshirt','crewneck-tshirt','casual-shirt','fitted-cap'];
$out=[]; foreach($slugs as $slug){$t=get_term_by('slug',$slug,'product_cat');if(!$t)continue;$u=get_term_link($t);$out[$slug]=['id'=>(int)$t->term_id,'name'=>$t->name,'description'=>$t->description,'url'=>is_wp_error($u)?'':$u,'count'=>(int)$t->count];}
echo wp_json_encode(['terms'=>$out], JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 180)
    if status != 200:
        raise RuntimeError('wp state HTTP ' + str(status))
    return json.loads(raw.decode('utf-8', 'replace'))


def mutate_terms():
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave2-mutate-' + nonce + '.php'
    php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false); require __DIR__ . '/wp-load.php'; @unlink(__FILE__);
function g2u($v){return esc_url($v);} function g2term($slug){$t=get_term_by('slug',$slug,'product_cat');if(!$t)return '';$u=get_term_link($t);return is_wp_error($u)?'':$u;}
$u453=get_permalink(453);$u460=get_permalink(460);$u468=get_permalink(468);$u471=get_permalink(471);$u472=get_permalink(472);$u487=get_permalink(487);$u493=get_permalink(493);$u496=get_permalink(496);$u503=get_permalink(503);
$copy=[];
$copy['jeans']='<h2>خرید شلوار جین مردانه؛ فیت، اندازه و ظاهر</h2><p>در دسته شلوار جین مردانه Gramiss می‌توانید مدل‌های موجود را بر اساس فرم کلی، قد، حجم ران و دمپا و جزئیات ظاهری مقایسه کنید. برای انتخاب آنلاین، نام سایز به‌تنهایی کافی نیست؛ اندازه واقعی کمر، فاق، ران، دمپا و قد را با شلواری که تن‌خورش را می‌پسندید مقایسه کنید.</p><p><a href="'.g2u($u472).'">راهنمای خرید شلوار جین مردانه</a> معیارهای اندازه و رفتار پارچه را دقیق‌تر توضیح می‌دهد. اگر بین فیت‌های آزاد مردد هستید، <a href="'.g2u($u460).'">تفاوت شلوار بگ، نیم‌بگ و فول‌بگ</a> کمک می‌کند حجم موردنظر را بهتر تعریف کنید؛ برای ترکیب بالاتنه و کفش هم <a href="'.g2u($u468).'">راهنمای استایل شلوار بگ</a> را ببینید.</p><h3>در صفحه هر مدل چه چیزهایی را بررسی کنید؟</h3><ul><li>اندازه‌های اعلام‌شده و نسبت آن‌ها با شلوار مرجع خودتان.</li><li>قد شلوار در کنار کفشی که معمولاً می‌پوشید.</li><li>رنگ، شست‌وشوی ظاهری و جزئیات جیب و دوخت در تصاویر همان محصول.</li></ul><p><a href="'.g2u(g2term('pants')).'">مشاهده همه شلوارهای مردانه</a></p>';
$copy['oversized-tshirt']='<h2>خرید تیشرت اورسایز مردانه؛ انتخاب حجم و قد مناسب</h2><p>تیشرت اورسایز فقط یک سایز بزرگ‌تر نیست؛ نتیجه نهایی به عرض لباس، افت سرشانه، قد و حجم آستین بستگی دارد. در این دسته مدل‌های موجود Gramiss را با توجه به همین نسبت‌ها مقایسه کنید و برای رسیدن به فرم دلخواه، اندازه‌های واقعی هر محصول را در اولویت قرار دهید.</p><p>اگر تفاوت فرم‌های آزاد برایتان مبهم است، <a href="'.g2u($u453).'">تفاوت تیشرت باکسی و اورسایز</a> را بخوانید. برای بررسی جنس، دوخت، یقه، چاپ و معیارهای کلی خرید هم <a href="'.g2u($u471).'">راهنمای خرید تیشرت مردانه</a> یک چک‌لیست کاربردی ارائه می‌کند.</p><h3>قبل از انتخاب مدل</h3><ul><li>عرض سینه و محل سرشانه را با فیت موردنظر خود مقایسه کنید.</li><li>قد تیشرت را مستقل از عرض آن بررسی کنید؛ دو مدل آزاد می‌توانند قد کاملاً متفاوتی داشته باشند.</li><li>رنگ و جزئیات پارچه را فقط از مشخصات و تصاویر همان محصول نتیجه بگیرید.</li></ul><p><a href="'.g2u(g2term('tshirt')).'">بازگشت به همه تیشرت‌های مردانه</a></p>';
$copy['graphic-tshirt']='<h2>خرید تیشرت چاپی مردانه؛ طرح، فیت و نگهداری</h2><p>در دسته تیشرت چاپی مردانه Gramiss می‌توانید مدل‌ها را بر اساس طرح چاپ، رنگ زمینه و فرم لباس مقایسه کنید. هنگام خرید، چاپ را جدا از خود تیشرت نبینید؛ فیت، اندازه واقعی، نوع یقه و اطلاعات پارچه‌ای که برای همان محصول درج شده‌اند در تجربه پوشیدن به همان اندازه مهم‌اند.</p><p><a href="'.g2u($u471).'">راهنمای خرید تیشرت مردانه</a> معیارهای مقایسه فیت، پارچه، دوخت و چاپ را جمع‌بندی می‌کند. بعد از خرید نیز نحوه شست‌وشو می‌تواند روی دوام ظاهر چاپ اثر بگذارد؛ در <a href="'.g2u($u496).'">راهنمای شست‌وشوی تیشرت چاپی</a> روش محافظه‌کارانه شستن، خشک‌کردن و اتوکشی توضیح داده شده است.</p><h3>برای مقایسه طرح‌ها</h3><ul><li>محل و ابعاد چاپ را در نمای کامل لباس ببینید.</li><li>فیت را از روی اندازه‌ها انتخاب کنید، نه صرفاً از روی عکس مدل.</li><li>دستور مراقبت همان محصول را بر توصیه‌های عمومی مقدم بدانید.</li></ul><p><a href="'.g2u(g2term('tshirt')).'">مشاهده همه تیشرت‌های مردانه</a></p>';
$copy['crewneck-tshirt']='<h2>خرید تیشرت یقه‌گرد مردانه؛ فیت و اندازه را کنار یقه ببینید</h2><p>یقه‌گرد یکی از فرم‌های رایج تیشرت است، اما انتخاب خوب فقط به شکل یقه محدود نمی‌شود. در مدل‌های موجود Gramiss عرض سینه، سرشانه، قد، طول آستین و فرم کلی لباس را کنار رنگ و جزئیات یقه مقایسه کنید تا انتخاب شما به فیت موردنظر نزدیک‌تر باشد.</p><p>برای خرید آنلاین، اندازه‌های واقعی هر مدل را با یک تیشرت مرجع از کمد خودتان مقایسه کنید. <a href="'.g2u($u471).'">راهنمای خرید تیشرت مردانه</a> توضیح می‌دهد چطور فیت، پارچه، دوخت و یقه را بدون اتکا به نام سایز بررسی کنید. اگر مدل انتخابی فرم آزاد دارد، <a href="'.g2u($u453).'">راهنمای تفاوت باکسی و اورسایز</a> هم برای تشخیص نسبت قد و عرض مفید است.</p><h3>چک‌لیست سریع</h3><ul><li>فرم و ارتفاع یقه در تصاویر محصول.</li><li>قد و عرض واقعی لباس.</li><li>جزئیات دوخت و اطلاعات جنس اعلام‌شده برای همان مدل.</li></ul><p><a href="'.g2u(g2term('tshirt')).'">مشاهده همه تیشرت‌های مردانه</a></p>';
$copy['casual-shirt']='<h2>خرید پیراهن اسپرت مردانه؛ قواره، آستین و ترکیب لباس</h2><p>پیراهن اسپرت مردانه می‌تواند از نظر قواره، طول، آستین و جنس ظاهرهای متفاوتی داشته باشد. در این دسته مدل‌های موجود Gramiss را بر اساس اندازه‌های واقعی و کاربردی که برای استایل خود می‌خواهید مقایسه کنید؛ عنوان «اسپرت» به‌تنهایی درباره فیت یا ترکیب الیاف یک محصول چیزی را قطعی نمی‌کند.</p><p>برای انتخاب سایز، <a href="'.g2u($u487).'">راهنمای انتخاب سایز پیراهن مردانه</a> اندازه‌گیری سرشانه، سینه، قد و آستین را توضیح می‌دهد. اگر مدل آستین کوتاه انتخاب می‌کنید، <a href="'.g2u($u503).'">راهنمای استایل پیراهن آستین کوتاه</a> برای هماهنگی با شلوار و کفش مثال‌های کاربردی دارد.</p><h3>قبل از خرید</h3><ul><li>قواره و طول پیراهن را با روش پوشیدن دلخواهتان مقایسه کنید.</li><li>نوع آستین، یقه و جزئیات دکمه و جیب را در تصاویر همان مدل ببینید.</li><li>ترکیب الیاف و دستور مراقبت را فقط از اطلاعات همان محصول برداشت کنید.</li></ul><p><a href="'.g2u(g2term('shirt')).'">مشاهده همه پیراهن‌های مردانه</a></p>';
$copy['fitted-cap']='<h2>خرید کلاه فیت کپ مردانه؛ اندازه دور سر و فرم کلاه</h2><p>در دسته کلاه فیت کپ مردانه Gramiss می‌توانید مدل‌های موجود را بر اساس فرم تاج، نقاب، رنگ و شیوه قرارگرفتن روی سر مقایسه کنید. برای خرید آنلاین، ظاهر عکس به‌تنهایی معیار دقیقی برای اندازه نیست؛ دور سر و اطلاعات سایز یا تنظیم‌پذیری همان مدل را قبل از انتخاب بررسی کنید.</p><p><a href="'.g2u($u493).'">راهنمای انتخاب سایز کلاه فیت کپ</a> نشان می‌دهد متر را کجا قرار دهید و چطور اندازه دور سر را بدون حدس ثبت کنید. بعد از آن، اندازه به‌دست‌آمده را با اطلاعات همان محصول مقایسه کنید؛ اگر یک مدل ساختار یا سیستم تنظیم متفاوتی دارد، همان مشخصات اولویت دارد.</p><h3>برای مقایسه مدل‌ها</h3><ul><li>فرم تاج و نقاب را در نماهای مختلف ببینید.</li><li>سایز یا محدوده تنظیم‌پذیری را با دور سر خود تطبیق دهید.</li><li>جنس، رنگ و روش نگهداری را فقط بر اساس اطلاعات همان کالا در نظر بگیرید.</li></ul><p><a href="'.g2u(g2term('hat')).'">مشاهده همه کلاه‌های مردانه</a></p>';
$out=[];foreach($copy as $slug=>$description){$t=get_term_by('slug',$slug,'product_cat');if(!$t){$out[$slug]=['error'=>'missing'];continue;}$r=wp_update_term($t->term_id,'product_cat',['description'=>$description]);if(is_wp_error($r)){$out[$slug]=['error'=>$r->get_error_message()];}else{$fresh=get_term($t->term_id,'product_cat');$plain=wp_strip_all_tags($fresh->description);$len=function_exists('mb_strlen')?mb_strlen($plain,'UTF-8'):strlen($plain);$out[$slug]=['id'=>(int)$t->term_id,'chars'=>$len];}}
echo wp_json_encode(['result'=>$out],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 240)
    body = raw.decode('utf-8', 'replace')
    print('MUTATE_TERMS', status, body[:2000])
    if status != 200:
        raise RuntimeError('mutation HTTP ' + str(status))
    payload = json.loads(body)
    for slug in TARGET_SLUGS:
        row = payload.get('result', {}).get(slug, {})
        if row.get('error') or int(row.get('chars', 0)) < 300:
            raise RuntimeError('mutation failed ' + slug + ' ' + json.dumps(row, ensure_ascii=False))


def restore_terms(pre):
    terms = pre.get('terms', {})
    encoded = {slug: base64.b64encode(terms.get(slug, {}).get('description', '').encode('utf-8')).decode('ascii') for slug in TARGET_SLUGS}
    pairs = ','.join("'%s'=>'%s'" % (slug, value) for slug, value in encoded.items())
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave2-restore-' + nonce + '.php'
    php = f'''<?php
header('Content-Type: application/json; charset=utf-8'); define('WP_USE_THEMES', false); require __DIR__ . '/wp-load.php'; @unlink(__FILE__);
$copy=array({pairs});$out=[];foreach($copy as $slug=>$encoded){{$description=base64_decode($encoded,true);if($description===false){{$out[$slug]='decode';continue;}}$t=get_term_by('slug',$slug,'product_cat');if(!$t){{$out[$slug]='missing';continue;}}$r=wp_update_term($t->term_id,'product_cat',['description'=>$description]);$out[$slug]=is_wp_error($r)?$r->get_error_message():'ok';}}echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 180)
    body = raw.decode('utf-8', 'replace')
    print('RESTORE_TERMS', status, body[:1000])
    if status != 200:
        raise RuntimeError('restore HTTP ' + str(status))
    result = json.loads(body)
    errors = [slug + ':' + str(result.get(slug)) for slug in TARGET_SLUGS if result.get(slug) != 'ok']
    if errors:
        raise RuntimeError('restore failed ' + ' | '.join(errors))


safety('PRE')
pre_state = wp_state()
terms = pre_state.get('terms', {})
for slug in TARGET_SLUGS:
    if slug not in terms or not terms[slug].get('url'):
        raise SystemExit('FAIL PRECONDITION missing ' + slug)
for slug in TARGET_SLUGS:
    plain = strip_markup(terms[slug].get('description', ''))
    if slug == 'fitted-cap':
        if plain != FITTED_PRE:
            raise SystemExit('FAIL PRECONDITION fitted-cap drift')
    elif plain:
        raise SystemExit('FAIL PRECONDITION description not empty ' + slug)

pre_pages = {slug: inspect(terms[slug]['url']) for slug in TARGET_SLUGS}
for slug, row in pre_pages.items():
    if row['status'] != 200 or row['h1_count'] != 1 or row['native_count'] != 0 or row['premium_count'] != 1:
        raise SystemExit('FAIL PRECONDITION page H1 ' + slug)
    if row['default_term_description_pos'] >= 0:
        raise SystemExit('FAIL PRECONDITION default description render ' + slug)
    if slug == 'fitted-cap':
        if len(row['seo_text']) < 50 or row['seo_pos'] <= row['products_pos']:
            raise SystemExit('FAIL PRECONDITION fitted renderer')
    elif row['seo_text']:
        raise SystemExit('FAIL PRECONDITION unexpected seo copy ' + slug)
print('PRE_WAVE2', json.dumps({s:{'seo_chars':len(r['seo_text']),'links':len(r['internal_links'])} for s,r in pre_pages.items()}, ensure_ascii=False, sort_keys=True))

try:
    mutate_terms()
    purge()
    time.sleep(2)
    safety('POST')
    post_state = wp_state()
    post_terms = post_state.get('terms', {})
    post_pages = {slug: inspect(post_terms[slug]['url']) for slug in TARGET_SLUGS}
    errors = []
    for slug, after in post_pages.items():
        before = pre_pages[slug]
        if after['status'] != 200 or after['h1_count'] != 1 or after['native_count'] != 0 or after['premium_count'] != 1:
            errors.append(slug + ' H1/HTTP')
        if after['head'] != before['head']:
            errors.append(slug + ' metadata changed')
        if after['default_term_description_pos'] >= 0:
            errors.append(slug + ' default description returned')
        if len(after['seo_text']) < 300 or after['seo_pos'] <= after['products_pos']:
            errors.append(slug + ' copy missing/position')
        if len(after['internal_links']) < 2:
            errors.append(slug + ' internal links thin')
        if len(strip_markup(post_terms.get(slug, {}).get('description', ''))) < 300:
            errors.append(slug + ' stored copy thin')
    print('POST_WAVE2', json.dumps({s:{'seo_chars':len(r['seo_text']),'links':len(r['internal_links']),'h1':r['h1_count']} for s,r in post_pages.items()}, ensure_ascii=False, sort_keys=True))
    if errors:
        raise RuntimeError(' | '.join(errors))
except Exception as exc:
    print('VERIFY_FAIL', repr(exc))
    rollback_errors = []
    try:
        restore_terms(pre_state)
    except Exception as rex:
        rollback_errors.append('terms ' + repr(rex))
    try:
        purge(); time.sleep(2); safety('ROLLBACK')
    except Exception as rex:
        rollback_errors.append('safety ' + repr(rex))
    restored = wp_state().get('terms', {})
    for slug in TARGET_SLUGS:
        if restored.get(slug, {}).get('description', '') != terms.get(slug, {}).get('description', ''):
            rollback_errors.append('description mismatch ' + slug)
    if rollback_errors:
        raise SystemExit('CRITICAL ROLLBACK FAILURE ' + ' | '.join(rollback_errors))
    raise

print('PASS CATEGORY MONEY PAGE CONTENT WAVE 2')
