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
TARGET_IDS = [35, 32, 217, 59, 57, 56, 66, 68, 41]
RELATED_TERM_IDS = [21, 25, 27, 22, 55]
ARTICLE_IDS = [492, 502, 497, 487, 463, 464, 467, 503, 482, 483, 471]
EXPECTED_NAMES = {
    35: 'کارگو',
    32: 'پارچه‌ای',
    217: 'پارچه سیلک',
    59: 'پیراهن لینن',
    57: 'پیراهن آستین بلند',
    56: 'پیراهن آستین کوتاه',
    66: 'کتونی روزمره',
    68: 'پیاده‌روی',
    41: 'یقه‌دار',
}
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
            req = urllib.request.Request(
                url if post else url + '?' + encoded.decode(),
                data=encoded if post else None,
                method='POST' if post else 'GET',
            )
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
    data = api('get_file_content', {
        'dir': ROOT if not directory else ROOT + '/' + directory,
        'file': name,
        'from_charset': '_DETECT_',
        'to_charset': 'utf-8',
    })
    if isinstance(data, dict):
        for key in ('content', 'file_content', 'data'):
            if isinstance(data.get(key), str):
                return data[key]
    return data if isinstance(data, str) else ''


def save_public(name, content):
    return api('save_file_content', {
        'dir': 'public_html', 'file': name, 'content': content,
        'from_charset': 'UTF-8', 'to_charset': 'UTF-8', 'fallback': '0',
    }, True)


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((
        p.scheme, p.netloc,
        urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@'),
        urllib.parse.quote(urllib.parse.unquote(p.query), safe='=&%:@,+'),
        p.fragment,
    ))


def get(url, timeout=180):
    url = safe_url(url)
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'GramissCategoryMoneyPageWave3/1.0',
                'Cache-Control': 'no-cache', 'Pragma': 'no-cache',
            })
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
    tm = re.search(r'<title[^>]*>(.*?)</title>', head, re.I | re.S)
    out = {'title': strip_markup(tm.group(1)) if tm else '', 'description': '', 'robots': '', 'canonical': ''}
    for tag in re.findall(r'<meta\b[^>]*>', head, re.I | re.S):
        name = attr(tag, 'name').lower()
        if name == 'description':
            out['description'] = attr(tag, 'content')
        elif name == 'robots':
            out['robots'] = attr(tag, 'content')
    for tag in re.findall(r'<link\b[^>]*>', head, re.I | re.S):
        if 'canonical' in attr(tag, 'rel').lower().split():
            out['canonical'] = norm(attr(tag, 'href'))
            break
    return out


def inspect(url):
    status, raw, final = get(url + ('&' if '?' in url else '?') + 'g1cw3=' + str(int(time.time() * 1000)), 180)
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
    status, raw, _ = get(BASE + '/' + path + '?g1cw3=' + str(int(time.time() * 1000)), 150)
    urls = sorted(html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>', raw.decode('utf-8', 'replace'), re.I))
    return status, urls, hashlib.sha256('\n'.join(urls).encode()).hexdigest()


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
    print('SAFETY', label, json.dumps({
        'php': php_sha, 'css': css_sha, 'protected': protected,
        'product': [ps, len(pu), ph], 'product_cat': [cs, len(cu), ch], 'errors': errors,
    }, sort_keys=True))
    if errors:
        raise RuntimeError('; '.join(errors))


def wp_state():
    ids = TARGET_IDS + RELATED_TERM_IDS
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave3-state-' + nonce + '.php'
    php = '''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false); require __DIR__ . '/wp-load.php'; @unlink(__FILE__);
$term_ids=%s; $article_ids=%s; $terms=[]; $articles=[];
foreach($term_ids as $id){$t=get_term((int)$id,'product_cat');if(!$t||is_wp_error($t))continue;$u=get_term_link($t);$terms[(string)$id]=['id'=>(int)$t->term_id,'name'=>$t->name,'description'=>$t->description,'url'=>is_wp_error($u)?'':$u,'count'=>(int)$t->count];}
foreach($article_ids as $id){$p=get_post((int)$id);if(!$p)continue;$articles[(string)$id]=['title'=>$p->post_title,'url'=>get_permalink($p)];}
echo wp_json_encode(['terms'=>$terms,'articles'=>$articles],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>''' % (json.dumps(ids), json.dumps(ARTICLE_IDS))
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 180)
    if status != 200:
        raise RuntimeError('wp state HTTP ' + str(status))
    return json.loads(raw.decode('utf-8', 'replace'))


def link(url, label):
    return '<a href="' + html.escape(url, quote=True) + '">' + label + '</a>'


def build_copy(state):
    t = state['terms']
    a = state['articles']
    tu = lambda i: t[str(i)]['url']
    au = lambda i: a[str(i)]['url']
    copy = {}
    copy[35] = (
        '<h2>خرید شلوار کارگو مردانه؛ فیت، جیب‌ها و تناسب استایل</h2>'
        '<p>در دسته شلوار کارگو مردانه Gramiss مدل‌های موجود را بر اساس فرم شلوار، حجم ران و دمپا، قد و جای‌گذاری جیب‌ها مقایسه کنید. نام «کارگو» به‌تنهایی فیت را مشخص نمی‌کند؛ دو مدل کارگو می‌توانند از نظر حجم و افت کاملاً متفاوت باشند، پس اندازه‌ها و تصاویر همان محصول را مبنا قرار دهید.</p>'
        '<p>' + link(au(492), 'تفاوت شلوار کارگو و شلوار بگ') + ' مرز بین نوع طراحی و فیت را روشن می‌کند و ' + link(au(502), 'راهنمای استایل با شلوار کارگو') + ' برای انتخاب تیشرت و کفش کمک می‌کند.</p>'
        '<h3>قبل از انتخاب مدل</h3><ul><li>کمر، فاق، ران، دمپا و قد اعلام‌شده را بررسی کنید.</li><li>جیب‌ها و جزئیات دوخت را از تصاویر همان محصول ببینید.</li><li>برای فیت آزاد، فقط به انتخاب سایز بزرگ‌تر تکیه نکنید.</li></ul>'
        '<p>' + link(tu(21), 'مشاهده همه شلوارهای مردانه') + '</p>'
    )
    copy[32] = (
        '<h2>خرید شلوار پارچه‌ای مردانه؛ فیت، افت و اندازه واقعی</h2>'
        '<p>برای انتخاب شلوار پارچه‌ای مردانه بهتر است هم‌زمان به فیت و رفتار ظاهری پارچه توجه کنید. در مدل‌های Gramiss اندازه واقعی کمر، فاق، ران، دمپا و قد را با شلواری که تن‌خورش را می‌پسندید مقایسه کنید و درباره جنس یا کشسانی فقط به مشخصاتی تکیه کنید که برای همان محصول اعلام شده است.</p>'
        '<p>' + link(au(497), 'راهنمای خرید شلوار پارچه‌ای مردانه') + ' معیارهای فیت، افت پارچه، فاق و قد را مرحله‌به‌مرحله جمع‌بندی می‌کند. برای دیدن گزینه‌های دیگر نیز ' + link(tu(21), 'دسته همه شلوارهای مردانه') + ' را بررسی کنید.</p>'
        '<h3>چک‌لیست خرید</h3><ul><li>اندازه‌های واقعی را با شلوار مرجع خود مقایسه کنید.</li><li>افت و حجم شلوار را در نمای کامل محصول ببینید.</li><li>ترکیب الیاف و دستور مراقبت را فقط از اطلاعات همان مدل نتیجه بگیرید.</li></ul>'
    )
    copy[217] = (
        '<h2>خرید پیراهن پارچه سیلک؛ انتخاب فیت و مشخصات واقعی محصول</h2>'
        '<p>«پارچه سیلک» در این صفحه نام دسته محصولات Gramiss است و به‌تنهایی اثبات نمی‌کند که ترکیب الیاف هر پیراهن، ابریشم طبیعی یا درصد مشخصی از یک الیاف خاص باشد. برای خرید، ترکیب الیاف، بافت، شیوه نگهداری و هر ویژگی فنی را فقط از مشخصات یا برچسب مراقبت همان محصول بررسی کنید.</p>'
        '<p>برای اینکه ظاهر پارچه باعث انتخاب سایز اشتباه نشود، ' + link(au(487), 'راهنمای انتخاب سایز پیراهن مردانه') + ' را ببینید. همچنین می‌توانید ' + link(tu(55), 'پیراهن‌های اسپرت') + ' یا ' + link(tu(25), 'همه پیراهن‌های مردانه') + ' را برای مقایسه مدل‌ها بررسی کنید.</p>'
        '<h3>هنگام مقایسه مدل‌ها</h3><ul><li>سرشانه، عرض سینه، قد و آستین را مستقل از نام سایز بررسی کنید.</li><li>درخشندگی یا ظاهر عکس را معادل ترکیب الیاف خاص ندانید.</li><li>دستور شست‌وشو و اتوکشی همان محصول را بر توصیه عمومی مقدم بدانید.</li></ul>'
    )
    copy[59] = (
        '<h2>خرید پیراهن لینن مردانه؛ فیت، ترکیب پارچه و نگهداری</h2>'
        '<p>در بازار پوشاک، واژه «لینن» ممکن است برای لینن خالص، ترکیبی یا حتی ظاهر نزدیک به لینن به‌کار رود؛ بنابراین نام دسته به‌تنهایی برای تعیین ترکیب الیاف کافی نیست. در هر پیراهن Gramiss مشخصات همان محصول و برچسب مراقبت را مرجع قرار دهید و سپس فیت، رنگ و کاربرد موردنظر را مقایسه کنید.</p>'
        '<p>برای شناخت بهتر پارچه، ' + link(au(463), 'راهنمای پارچه لینن') + ' را بخوانید؛ برای مراقبت ' + link(au(464), 'راهنمای شست‌وشوی پیراهن لینن') + ' و برای ترکیب لباس ' + link(au(467), 'راهنمای استایل با پیراهن لینن') + ' در دسترس است.</p>'
        '<h3>قبل از خرید</h3><ul><li>ترکیب الیاف و دستور مراقبت همان مدل را بررسی کنید.</li><li>قد، سرشانه و عرض سینه را با پیراهن مرجع مقایسه کنید.</li><li>میزان چروک یا آب‌رفت را بدون اطلاعات محصول به‌صورت عدد ثابت فرض نکنید.</li></ul><p>' + link(tu(25), 'مشاهده همه پیراهن‌های مردانه') + '</p>'
    )
    copy[57] = (
        '<h2>خرید پیراهن آستین بلند مردانه؛ اندازه و قواره قبل از رنگ</h2>'
        '<p>در پیراهن آستین بلند، محل سرشانه و طول آستین در کنار عرض سینه و قد کلی لباس روی تن‌خور اثر می‌گذارند. برای انتخاب آنلاین مدل‌های Gramiss نام سایز را نقطه شروع بدانید، نه نتیجه نهایی؛ اندازه‌های اعلام‌شده را با یک پیراهن مرجع که روی بدن شما مناسب است مقایسه کنید.</p>'
        '<p>' + link(au(487), 'راهنمای انتخاب سایز پیراهن مردانه') + ' روش اندازه‌گیری سرشانه، سینه، قد و آستین را توضیح می‌دهد. برای مقایسه فرم‌های روزمره نیز ' + link(tu(55), 'دسته پیراهن اسپرت') + ' و ' + link(tu(25), 'همه پیراهن‌های مردانه') + ' را ببینید.</p>'
        '<h3>چک‌لیست سریع</h3><ul><li>طول آستین را در کنار عرض سرشانه بررسی کنید.</li><li>قد پیراهن را متناسب با نحوه پوشیدن داخل یا بیرون شلوار بسنجید.</li><li>جنس و دستور نگهداری را از مشخصات همان محصول بخوانید.</li></ul>'
    )
    copy[56] = (
        '<h2>خرید پیراهن آستین کوتاه مردانه؛ فیت، قد و ترکیب لباس</h2>'
        '<p>پیراهن آستین کوتاه می‌تواند با قواره‌های متفاوت عرضه شود و فقط کوتاه بودن آستین درباره تن‌خور کلی آن چیزی نمی‌گوید. در مدل‌های موجود Gramiss سرشانه، عرض سینه، قد لباس و حجم آستین را کنار هم بررسی کنید تا پیراهن با فرم شلوار و استایل موردنظر هماهنگ‌تر باشد.</p>'
        '<p>برای اندازه‌گیری دقیق‌تر از ' + link(au(487), 'راهنمای انتخاب سایز پیراهن مردانه') + ' استفاده کنید و برای ایده‌های ترکیب لباس، ' + link(au(503), 'راهنمای استایل پیراهن آستین کوتاه') + ' را ببینید. ' + link(tu(25), 'همه پیراهن‌های مردانه') + ' نیز برای مقایسه مدل‌های دیگر در دسترس است.</p>'
        '<h3>قبل از انتخاب</h3><ul><li>سرشانه و سینه را با پیراهن مرجع مقایسه کنید.</li><li>قد لباس را مستقل از عرض آن بررسی کنید.</li><li>رنگ، بافت و جزئیات را از تصاویر و مشخصات همان مدل نتیجه بگیرید.</li></ul>'
    )
    copy[66] = (
        '<h2>خرید کتونی روزمره مردانه؛ سایز، رویه و زیره را مقایسه کنید</h2>'
        '<p>برای کتونی روزمره، ظاهر تنها یکی از معیارهاست. در مدل‌های Gramiss طول پا و جدول سایز همان محصول را در کنار ساختار رویه، زیره، نوع بسته‌شدن و اطلاعات فنی اعلام‌شده بررسی کنید. تجربه راحتی بین افراد متفاوت است، بنابراین از روی عکس یا نام مدل درباره راحتی قطعی نتیجه نگیرید.</p>'
        '<p>' + link(au(482), 'راهنمای انتخاب سایز کتانی مردانه') + ' روش اندازه‌گیری پا برای خرید آنلاین را توضیح می‌دهد و ' + link(au(483), 'راهنمای خرید کتانی روزمره') + ' معیارهای رویه و زیره را برای مقایسه منظم‌تر جمع‌بندی می‌کند.</p>'
        '<h3>قبل از خرید</h3><ul><li>هر دو پا را اندازه بگیرید و جدول همان مدل را مرجع قرار دهید.</li><li>جنس رویه و زیره را فقط از مشخصات محصول برداشت کنید.</li><li>کاربری ادعاشده هر مدل را با نیاز واقعی خود تطبیق دهید.</li></ul><p>' + link(tu(27), 'مشاهده همه کتونی‌های مردانه') + '</p>'
    )
    copy[68] = (
        '<h2>خرید کتونی پیاده‌روی مردانه؛ اندازه و مشخصات را بدون حدس بررسی کنید</h2>'
        '<p>در انتخاب کتونی برای پیاده‌روی، سایز و مشخصات واقعی هر مدل مهم‌تر از برچسب کلی دسته هستند. Gramiss درباره حمایت پزشکی، اصلاح فرم پا یا مناسب‌بودن برای شرایط جسمی خاص بدون مشخصات معتبر ادعایی نمی‌کند؛ اگر نیاز تخصصی دارید، ارزیابی حرفه‌ای جداگانه لازم است.</p>'
        '<p>برای خرید آنلاین، ابتدا ' + link(au(482), 'راهنمای انتخاب سایز کتانی مردانه') + ' را برای اندازه‌گیری پا ببینید. ' + link(au(483), 'راهنمای خرید کتانی روزمره') + ' نیز چارچوبی عمومی برای مقایسه رویه، زیره و ساختار کفش ارائه می‌کند، بدون اینکه جای مشخصات همان محصول را بگیرد.</p>'
        '<h3>در صفحه هر مدل بررسی کنید</h3><ul><li>جدول سایز و طول پای پیشنهادی همان محصول.</li><li>مواد و ساختار اعلام‌شده برای رویه و زیره.</li><li>محدوده استفاده‌ای که فروشنده برای همان مدل مشخص کرده است.</li></ul><p>' + link(tu(27), 'مشاهده همه کتونی‌های مردانه') + '</p>'
    )
    copy[41] = (
        '<h2>خرید تیشرت یقه‌دار مردانه؛ فیت و مشخصات هر مدل را جداگانه ببینید</h2>'
        '<p>دسته تیشرت یقه‌دار Gramiss در حال حاضر مجموعه محدودی دارد و ویژگی یک محصول نباید به همه مدل‌های آینده این دسته تعمیم داده شود. برای هر گزینه، فیت، اندازه واقعی، نوع یقه، پارچه، دوخت و دستور نگهداری را از صفحه همان محصول بررسی کنید.</p>'
        '<p>' + link(au(471), 'راهنمای خرید تیشرت مردانه') + ' یک چک‌لیست عمومی برای مقایسه فیت، جنس، یقه و دوخت ارائه می‌کند. برای مقایسه با فرم‌های دیگر نیز ' + link(tu(22), 'همه تیشرت‌های مردانه') + ' را ببینید.</p>'
        '<h3>پیش از سفارش</h3><ul><li>عرض سینه، سرشانه و قد را با لباس مرجع خود مقایسه کنید.</li><li>فرم یقه و جزئیات دوخت را در تصاویر همان محصول بررسی کنید.</li><li>مشخصات مدل فعلی را به محصولات دیگر این دسته تعمیم ندهید.</li></ul>'
    )
    return copy


def mutate_terms(copy):
    payload = base64.b64encode(json.dumps({str(k): v for k, v in copy.items()}, ensure_ascii=False).encode('utf-8')).decode('ascii')
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave3-mutate-' + nonce + '.php'
    php = '''<?php
header('Content-Type: application/json; charset=utf-8'); define('WP_USE_THEMES', false); require __DIR__ . '/wp-load.php'; @unlink(__FILE__);
$raw=base64_decode('%s',true); $copy=$raw===false?null:json_decode($raw,true); $out=[];
if(!is_array($copy)){http_response_code(500);echo wp_json_encode(['error'=>'payload']);exit;}
foreach($copy as $id=>$description){$t=get_term((int)$id,'product_cat');if(!$t||is_wp_error($t)){$out[$id]=['error'=>'missing'];continue;}$r=wp_update_term((int)$id,'product_cat',['description'=>$description]);$fresh=get_term((int)$id,'product_cat');$out[$id]=['error'=>is_wp_error($r)?$r->get_error_message():'','chars'=>$fresh?strlen(wp_strip_all_tags($fresh->description)):0];}
echo wp_json_encode(['result'=>$out],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>''' % payload
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 180)
    body = raw.decode('utf-8', 'replace')
    print('MUTATE_TERMS', status, body[:2000])
    if status != 200:
        raise RuntimeError('mutate HTTP ' + str(status))
    result = json.loads(body).get('result', {})
    for tid in TARGET_IDS:
        row = result.get(str(tid), {})
        if row.get('error') or int(row.get('chars', 0)) < 300:
            raise RuntimeError('term mutation failed ' + str(tid) + ' ' + json.dumps(row, ensure_ascii=False))


def restore_terms(pre):
    encoded = {
        str(tid): base64.b64encode(pre['terms'][str(tid)].get('description', '').encode('utf-8')).decode('ascii')
        for tid in TARGET_IDS
    }
    payload = base64.b64encode(json.dumps(encoded).encode('utf-8')).decode('ascii')
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave3-restore-' + nonce + '.php'
    php = '''<?php
header('Content-Type: application/json; charset=utf-8'); define('WP_USE_THEMES', false); require __DIR__ . '/wp-load.php'; @unlink(__FILE__);
$raw=base64_decode('%s',true);$map=$raw===false?null:json_decode($raw,true);$out=[];if(!is_array($map)){http_response_code(500);echo 'payload';exit;}
foreach($map as $id=>$encoded){$description=base64_decode($encoded,true);if($description===false){$out[$id]='decode';continue;}$r=wp_update_term((int)$id,'product_cat',['description'=>$description]);$out[$id]=is_wp_error($r)?$r->get_error_message():'ok';}
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>''' % payload
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 180)
    body = raw.decode('utf-8', 'replace')
    print('RESTORE_TERMS', status, body[:1500])
    if status != 200:
        raise RuntimeError('restore HTTP ' + str(status))
    result = json.loads(body)
    errors = [str(tid) + ':' + str(result.get(str(tid))) for tid in TARGET_IDS if result.get(str(tid)) != 'ok']
    if errors:
        raise RuntimeError('restore failed ' + ' | '.join(errors))


def purge():
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-content-wave3-purge-' + nonce + '.php'
    php = '''<?php
define('WP_USE_THEMES', false); require __DIR__ . '/wp-load.php'; @unlink(__FILE__);
if(function_exists('wp_cache_flush')){wp_cache_flush();} if(has_action('litespeed_purge_all')){do_action('litespeed_purge_all');}
header('Content-Type: text/plain; charset=utf-8'); echo 'PURGED';
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 120)
    print('PURGE', status, raw.decode('utf-8', 'replace')[:120])
    if status != 200 or b'PURGED' not in raw:
        raise RuntimeError('cache purge failed')


safety('PRE')
pre_state = wp_state()
terms = pre_state.get('terms', {})
articles = pre_state.get('articles', {})
for tid in TARGET_IDS:
    row = terms.get(str(tid))
    if not row or not row.get('url') or row.get('name') != EXPECTED_NAMES[tid]:
        raise SystemExit('FAIL PRECONDITION term state ' + str(tid))
    if strip_markup(row.get('description', '')):
        raise SystemExit('FAIL PRECONDITION description not empty ' + str(tid))
for aid in ARTICLE_IDS:
    if not articles.get(str(aid), {}).get('url'):
        raise SystemExit('FAIL PRECONDITION article url ' + str(aid))
for tid in RELATED_TERM_IDS:
    if not terms.get(str(tid), {}).get('url'):
        raise SystemExit('FAIL PRECONDITION related term ' + str(tid))

pre_pages = {tid: inspect(terms[str(tid)]['url']) for tid in TARGET_IDS}
for tid, row in pre_pages.items():
    robots = row['head'].get('robots', '').lower()
    if row['status'] != 200 or row['h1_count'] != 1 or row['native_count'] != 0 or row['premium_count'] != 1:
        raise SystemExit('FAIL PRECONDITION page/H1 ' + str(tid))
    if row['head'].get('canonical') != norm(terms[str(tid)]['url']):
        raise SystemExit('FAIL PRECONDITION canonical ' + str(tid))
    if 'noindex' in robots or 'index' not in robots:
        raise SystemExit('FAIL PRECONDITION robots ' + str(tid))
    if not row['head'].get('title') or not row['head'].get('description'):
        raise SystemExit('FAIL PRECONDITION metadata ' + str(tid))
    if row['default_term_description_pos'] >= 0 or row['seo_text'] or row['products_pos'] < 0:
        raise SystemExit('FAIL PRECONDITION render state ' + str(tid))
print('PRE_WAVE3', json.dumps({str(i): {'h1': r['h1_count'], 'seo_chars': len(r['seo_text'])} for i, r in pre_pages.items()}, ensure_ascii=False, sort_keys=True))

copy = build_copy(pre_state)
for tid in TARGET_IDS:
    if tid not in copy or len(strip_markup(copy[tid])) < 300 or copy[tid].count('https://gramiss.ir') < 2:
        raise SystemExit('FAIL COPY BUILD ' + str(tid))

try:
    mutate_terms(copy)
    purge()
    time.sleep(2)
    safety('POST')
    post_state = wp_state()
    post_pages = {tid: inspect(post_state['terms'][str(tid)]['url']) for tid in TARGET_IDS}
    errors = []
    for tid, after in post_pages.items():
        before = pre_pages[tid]
        stored = post_state['terms'][str(tid)].get('description', '')
        if after['status'] != 200 or after['h1_count'] != 1 or after['native_count'] != 0 or after['premium_count'] != 1:
            errors.append(str(tid) + ' H1/HTTP')
        if after['head'] != before['head']:
            errors.append(str(tid) + ' metadata changed')
        if after['default_term_description_pos'] >= 0:
            errors.append(str(tid) + ' default description returned')
        if len(after['seo_text']) < 300 or after['seo_pos'] <= after['products_pos']:
            errors.append(str(tid) + ' copy missing/position')
        if len(after['internal_links']) < 2:
            errors.append(str(tid) + ' internal links thin')
        if len(strip_markup(stored)) < 300:
            errors.append(str(tid) + ' stored copy thin')
        if strip_markup(copy[tid])[:80] not in strip_markup(stored):
            errors.append(str(tid) + ' stored copy mismatch')
    print('POST_WAVE3', json.dumps({str(i): {'seo_chars': len(r['seo_text']), 'links': len(r['internal_links']), 'h1': r['h1_count']} for i, r in post_pages.items()}, ensure_ascii=False, sort_keys=True))
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
    try:
        restored = wp_state().get('terms', {})
        for tid in TARGET_IDS:
            if restored.get(str(tid), {}).get('description', '') != terms[str(tid)].get('description', ''):
                rollback_errors.append('description mismatch ' + str(tid))
    except Exception as rex:
        rollback_errors.append('verify restore ' + repr(rex))
    if rollback_errors:
        raise SystemExit('CRITICAL ROLLBACK FAILURE ' + ' | '.join(rollback_errors))
    raise

print('PASS CATEGORY MONEY PAGE CONTENT WAVE 3')
