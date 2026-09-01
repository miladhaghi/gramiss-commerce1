import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

HOST = os.environ["CPANEL_HOST"]
USER = os.environ["CPANEL_USER"]
TOKEN = os.environ["CPANEL_TOKEN"]
ROOT = os.environ["THEME_ROOT"].strip("/")
HEALTHY = os.environ.get("HEALTHY_HOME_SHA", "")
CTX = ssl._create_unverified_context()
BASE = "https://gramiss.ir"

PRODUCT_SHA = "70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3"
PCAT_SHA = "75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4"
TITLE18 = "با شلوار کارگو مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و حجم لباس"
TITLE19 = "پیراهن آستین کوتاه مردانه را با چی بپوشیم؟ شلوار، کفش و لایه‌بندی"
META18 = "با شلوار کارگو مردانه چی بپوشیم؟ راهنمای استایل"
DESC18 = "برای استایل با شلوار کارگو مردانه، تیشرت، پیراهن، کتانی و حجم بالاتنه را بر اساس فیت و دمپای همان شلوار هماهنگ کنید؛ با فرمول‌های کاربردی و بدون قانون‌های خشک."
META19 = "پیراهن آستین کوتاه مردانه با چی بپوشیم؟ راهنمای استایل"
DESC19 = "پیراهن آستین کوتاه مردانه را با جین، شلوار پارچه‌ای، کتانی و لایه‌بندی درست ست کنید؛ انتخاب فیت، قد پیراهن و حجم شلوار را مرحله‌به‌مرحله بررسی کنید."
FOCUS18 = "با شلوار کارگو مردانه چی بپوشیم"
FOCUS19 = "پیراهن آستین کوتاه مردانه با چی بپوشیم"
SLUG18 = "با-شلوار-کارگو-مردانه-چی-بپوشیم"
SLUG19 = "استایل-پیراهن-آستین-کوتاه-مردانه"
EXPECTED_IDS = [453,459,460,463,464,467,468,471,472,482,483,487,488,492,493,496,497]
PROTECTED = {
    "front-page.php": "0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7",
    "template-parts/home-looks.php": "3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d",
    "assets/css/home-looks.css": "98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0",
    "assets/js/home-looks.js": "6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2",
}


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((
        p.scheme,
        p.netloc,
        urllib.parse.quote(urllib.parse.unquote(p.path), safe="/%:@"),
        urllib.parse.quote(urllib.parse.unquote(p.query), safe="=&%:@,+"),
        p.fragment,
    ))


def api(function, params, post=False):
    url = f"https://{HOST}:2083/execute/Fileman/{function}"
    encoded = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 5):
        try:
            req = urllib.request.Request(
                url if post else url + "?" + encoded.decode(),
                data=encoded if post else None,
                method="POST" if post else "GET",
            )
            req.add_header("Authorization", f"cpanel {USER}:{TOKEN}")
            if post:
                req.add_header("Content-Type", "application/x-www-form-urlencoded")
            with urllib.request.urlopen(req, context=CTX, timeout=90) as response:
                payload = json.loads(response.read().decode("utf-8", "replace"))
            result = payload.get("result") if isinstance(payload.get("result"), dict) else payload
            if not isinstance(result, dict) or result.get("status") != 1:
                raise RuntimeError(str(result))
            return result.get("data")
        except Exception as exc:
            last = exc
            print("API_RETRY", function, attempt, exc)
            if attempt < 4:
                time.sleep(attempt * 2)
    raise last


def read_theme(relative):
    directory, name = relative.rsplit("/", 1) if "/" in relative else ("", relative)
    data = api("get_file_content", {
        "dir": ROOT if not directory else ROOT + "/" + directory,
        "file": name,
        "from_charset": "_DETECT_",
        "to_charset": "utf-8",
    })
    if isinstance(data, dict):
        for key in ("content", "file_content", "data"):
            if isinstance(data.get(key), str):
                return data[key]
    return data if isinstance(data, str) else ""


def save_public(name, content):
    return api("save_file_content", {
        "dir": "public_html",
        "file": name,
        "content": content,
        "from_charset": "UTF-8",
        "to_charset": "UTF-8",
        "fallback": "0",
    }, True)


def get(url, timeout=180):
    url = safe_url(url)
    last = None
    for attempt in range(1, 5):
        req = urllib.request.Request(url, headers={
            "User-Agent": "GramissWave1819/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        })
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as response:
                return response.status, response.read(), response.geturl()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), exc.geturl()
        except Exception as exc:
            last = exc
            print("HTTP_RETRY", attempt, url, exc)
            if attempt < 4:
                time.sleep(attempt * 2)
    raise last


def value(text, pattern):
    match = re.search(pattern, text, re.I | re.S)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def meta(raw):
    text = raw.decode("utf-8", "replace").split("</head>", 1)[0]
    return {
        "title": value(text, r"<title[^>]*>(.*?)</title>"),
        "description": value(text, r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']*)"),
        "canonical": value(text, r"<link[^>]+rel=[\"']canonical[\"'][^>]+href=[\"']([^\"']+)"),
        "robots": value(text, r"<meta[^>]+name=[\"']robots[\"'][^>]+content=[\"']([^\"']+)"),
    }


def norm(url):
    return urllib.parse.unquote(url).split("?", 1)[0].rstrip("/") + "/"


def sitemap(path):
    status, raw, _ = get(BASE + "/" + path + "?t=" + str(int(time.time())), 120)
    urls = [x.replace("&amp;", "&") for x in re.findall(r"<loc>(.*?)</loc>", raw.decode("utf-8", "replace"), re.I)]
    return status, urls


def run_public_php(name, php_text, timeout=240):
    save_public(name, php_text)
    status, raw, final = get(BASE + "/" + name + "?t=" + str(int(time.time())), timeout)
    text = raw.decode("utf-8", "replace")
    try:
        payload = json.loads(text)
    except Exception:
        payload = {"raw": text[:1000]}
    return status, payload, final


# Immutable preflight.
protected_pre = {path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in PROTECTED}
print("PROTECTED_PRE", json.dumps(protected_pre, ensure_ascii=False, sort_keys=True))
for path, expected in PROTECTED.items():
    if protected_pre.get(path) != expected:
        raise SystemExit("ABORT protected drift " + path)
if HEALTHY and protected_pre["front-page.php"] != HEALTHY:
    raise SystemExit("ABORT Home drift")

ps, product_urls_pre = sitemap("product-sitemap.xml")
pcs, pcat_urls_pre = sitemap("product_cat-sitemap.xml")
product_urls_pre = sorted(product_urls_pre)
pcat_urls_pre = sorted(pcat_urls_pre)
product_sha_pre = hashlib.sha256("\n".join(product_urls_pre).encode()).hexdigest()
pcat_sha_pre = hashlib.sha256("\n".join(pcat_urls_pre).encode()).hexdigest()
print("COMMERCE_SITEMAPS_PRE", ps, len(product_urls_pre), product_sha_pre, pcs, len(pcat_urls_pre), pcat_sha_pre)
if ps != 200 or len(product_urls_pre) != 47 or product_sha_pre != PRODUCT_SHA:
    raise SystemExit("ABORT product sitemap drift")
if pcs != 200 or len(pcat_urls_pre) != 20 or pcat_sha_pre != PCAT_SHA:
    raise SystemExit("ABORT product category sitemap drift")

commerce = {
    "cargo": BASE + "/product-category/pants/cargo-pants/",
    "tshirt": BASE + "/product-category/tshirt/",
    "sneakers": BASE + "/product-category/sneakers/",
    "shirt": BASE + "/product-category/shirt/",
    "shortshirt": BASE + "/product-category/shirt/short-sleeve-shirt/",
    "pants": BASE + "/product-category/pants/",
}
for label, url in commerce.items():
    status, raw, final = get(url + "?t=" + str(int(time.time())), 150)
    metadata = meta(raw)
    robots = metadata.get("robots", "").lower()
    print("COMMERCE", label, status, final, metadata)
    if status != 200 or "noindex" in robots or "index" not in robots or norm(metadata.get("canonical", "")) != norm(url):
        raise SystemExit("ABORT commerce archive " + label)
if not {norm(x) for x in commerce.values()}.issubset({norm(x) for x in pcat_urls_pre}):
    raise SystemExit("ABORT commerce target missing from product category sitemap")

nonce = hashlib.sha256((str(time.time()) + protected_pre["front-page.php"]).encode()).hexdigest()[:14]
probe_name = "gramiss-wave-18-19-" + nonce + ".php"

# The WordPress mutation is transactional at the application level: source-post originals
# are saved in a non-autoloaded option until public verification finishes.
php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false); require __DIR__.'/wp-load.php'; @unlink(__FILE__);
$expected=[453,459,460,463,464,467,468,471,472,482,483,487,488,492,493,496,497];
$posts=[];$errors=[];foreach($expected as $id){$posts[$id]=get_post($id);if(!$posts[$id]||$posts[$id]->post_status!=='publish')$errors[]='post '.$id;}
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');
$cargo=get_term_by('slug','cargo-pants','product_cat');$tshirt=get_term_by('slug','tshirt','product_cat');$sneakers=get_term_by('slug','sneakers','product_cat');$shirt=get_term_by('slug','shirt','product_cat');$short=get_term_by('slug','short-sleeve-shirt','product_cat');$pants=get_term_by('slug','pants','product_cat');
$slug18='با-شلوار-کارگو-مردانه-چی-بپوشیم';$slug19='استایل-پیراهن-آستین-کوتاه-مردانه';
if((int)wp_count_posts('post')->publish!==17)$errors[]='published';
if(!$fit||!$fabric||!$style||!$buy||!$cargo||!$tshirt||!$sneakers||!$shirt||!$short||!$pants)$errors[]='taxonomy';
if($fit&&(int)$fit->count!==7)$errors[]='fit';if($fabric&&(int)$fabric->count!==4)$errors[]='fabric';if($style&&(int)$style->count!==2)$errors[]='style';if($buy&&(int)$buy->count!==4)$errors[]='buy';
if(get_page_by_path($slug18,OBJECT,'post')||get_page_by_path($slug19,OBJECT,'post'))$errors[]='target slug exists';
$markers=[468=>'1819-cargo-style-from-07',492=>'1819-cargo-style-from-14',467=>'1819-shortshirt-style-from-06',487=>'1819-shortshirt-style-from-12'];foreach($markers as $id=>$m){if(strpos($posts[$id]->post_content,$m)!==false)$errors[]='marker '.$id;}
if($errors){http_response_code(409);echo wp_json_encode(['error'=>'baseline drift','details'=>$errors],JSON_UNESCAPED_UNICODE);exit;}

$cu=get_term_link($cargo);$tu=get_term_link($tshirt);$su=get_term_link($sneakers);$shu=get_term_link($shirt);$ssu=get_term_link($short);$pu=get_term_link($pants);
foreach([$cu,$tu,$su,$shu,$ssu,$pu] as $u){if(is_wp_error($u)){http_response_code(409);echo wp_json_encode(['error'=>'commerce url']);exit;}}
$a3=get_permalink($posts[460]);$a6=get_permalink($posts[467]);$a7=get_permalink($posts[468]);$a9=get_permalink($posts[472]);$a11=get_permalink($posts[483]);$a12=get_permalink($posts[487]);$a14=get_permalink($posts[492]);$a17=get_permalink($posts[497]);
$rollback='gramiss_wave1819_rollback_'.wp_generate_password(18,false,false);$snapshot=[];foreach([468,492,467,487] as $id)$snapshot[$id]=$posts[$id]->post_content;
if(!add_option($rollback,$snapshot,'',false)){http_response_code(500);echo wp_json_encode(['error'=>'rollback snapshot']);exit;}
$created=[];
function g1819_meta($id,$title,$desc,$focus){update_post_meta($id,'rank_math_title',$title);update_post_meta($id,'rank_math_description',$desc);update_post_meta($id,'rank_math_focus_keyword',$focus);foreach(['rank_math_robots','rank_math_rich_snippet','rank_math_snippet_article_type'] as $k)delete_post_meta($id,$k);}
function g1819_flush(){global $wpdb;$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_transient_rank_math_sitemap_%' OR option_name LIKE '_transient_timeout_rank_math_sitemap_%'");wp_cache_flush();do_action('litespeed_purge_all');}
function g1819_rollback_local($created,$snapshot,$rollback){foreach($snapshot as $id=>$content)wp_update_post(['ID'=>(int)$id,'post_content'=>$content]);foreach($created as $id)wp_delete_post((int)$id,true);delete_option($rollback);g1819_flush();}

$c18=<<<HTML
<p>برای استایل شلوار کارگو، از تعداد جیب‌ها شروع نکن؛ اول فیت واقعی شلوار، حجم ران و ساق، عرض دمپا و قد آن را ببین. دو شلوار با نام «کارگو» می‌توانند از نظر سیلوئت کاملاً متفاوت باشند و به بالاتنه و کفش متفاوتی نیاز داشته باشند.</p>
<p>اگر هنوز مرز بین ساختار کارگو و فیت بگ برایت روشن نیست، اول <a href="$a14">راهنمای شلوار کارگو و تفاوت آن با بگ</a> را بخوان. این صفحه فقط مالک نیت «چطور کارگو را استایل کنیم» است.</p>
<h2>اول حجم واقعی شلوار کارگو را مشخص کن</h2><p>کارگو می‌تواند راسته، آزاد، بگ یا جمع‌شونده در مچ باشد. به‌جای تکیه بر اسم محصول، کمر، فاق، ران، ساق، دمپا و قد را ببین و بعد تصمیم بگیر بالاتنه چقدر حجم داشته باشد.</p>
<h2>با شلوار کارگو چه تیشرتی بپوشیم؟</h2><p>تیشرت ساده، گرافیکی، باکسی یا رگولار همگی می‌توانند جواب بدهند. معیار بهتر، نسبت عرض و قد تیشرت به حجم شلوار است؛ نه یک قانون ثابت که بالاتنه حتماً تنگ یا حتماً اورسایز باشد.</p>
<h2>تیشرت باکسی با کارگو چه زمانی متعادل می‌شود؟</h2><p>اگر کارگو حجم زیادی دارد، تیشرت باکسی کوتاه‌تر می‌تواند خط کمر و نسبت بالاتنه به پایین‌تنه را واضح‌تر کند. اگر خود شلوار جمع‌وجورتر است، باکسی خیلی عریض ممکن است مرکز ثقل استایل را بالا ببرد؛ نتیجه را با آینه و نمای کامل بررسی کن.</p>
<h2>تیشرت گرافیکی را با جیب‌های کارگو چطور هماهنگ کنیم؟</h2><p>جیب‌های بزرگ خودشان جزئیات بصری ایجاد می‌کنند. وقتی چاپ تیشرت هم شلوغ است، تعداد نقاط کانونی بیشتر می‌شود. این الزاماً اشتباه نیست؛ اما اگر استایل آرام‌تر می‌خواهی، یکی از دو بخش را ساده‌تر نگه دار. مدل‌های موجود در <a href="$tu">دسته تیشرت مردانه</a> را می‌توانی برای مقایسه حجم و طرح ببینی.</p>
<h2>پیراهن با شلوار کارگو؛ باز یا بسته؟</h2><p>پیراهن بسته ظاهر منظم‌تری می‌دهد و پیراهن باز روی تیشرت یک لایه اضافه می‌کند. طول پیراهن مهم است: لایه خیلی بلند روی کارگوی پرحجم می‌تواند بخش میانی استایل را سنگین کند. انتخاب را با قد شلوار و محل قرارگیری جیب‌ها بسنج.</p>
<h2>هودی و سویشرت با کارگو</h2><p>برای هوای خنک، هودی یا سویشرت می‌تواند حجم بالاتنه را به پایین‌تنه نزدیک کند. اما «اورسایز + بگ» تنها فرمول ممکن نیست؛ یک سویشرت جمع‌وجور با کارگوی آزاد هم می‌تواند تضاد کنترل‌شده بسازد.</p>
<h2>با شلوار کارگو چه کفشی بپوشیم؟</h2><p>از دمپا شروع کن. دمپای باز، دمپای جمع‌شده و قدی که روی کفش شکست ایجاد می‌کند، هرکدام رابطه متفاوتی با حجم کفش دارند. کفش را جدا از شلوار انتخاب نکن.</p>
<h2>کتانی کم‌حجم یا حجیم؟</h2><p>هر دو ممکن‌اند. کتانی حجیم می‌تواند وزن بصری پایین استایل را بیشتر کند؛ کتانی ساده‌تر اجازه می‌دهد جیب‌ها و فرم شلوار بیشتر دیده شوند. برای معیارهای کاربردی خرید، <a href="$a11">راهنمای خرید کتانی مردانه روزمره</a> را ببین و سپس مدل‌های <a href="$su">کتانی مردانه Gramiss</a> را با دمپای شلوارت مقایسه کن.</p>
<h2>قد شلوار و شکست روی کفش را جدی بگیر</h2><p>کارگویی که روی کفش جمع می‌شود، سیلوئت متفاوتی از کارگوی کوتاه‌تر یا مچ‌دار دارد. قبل از کوتاه‌کردن یا تا زدن، همان کفشی را بپوش که بیشتر با شلوار استفاده می‌کنی.</p>
<h2>رنگ‌ها را از یک نقطه ثابت شروع کن</h2><p>به‌جای حفظ کردن جدول «رنگ مناسب کارگو»، یک آیتم اصلی را ثابت کن و بقیه را پیرامون آن بساز. کارگوی خاکی، مشکی یا خنثی می‌تواند با طیف‌های زیادی کار کند؛ نور، بافت و شدت رنگ هم روی نتیجه اثر دارند.</p>
<h2>جیب‌های کارگو بخشی از ترکیب بصری‌اند</h2><p>جیب‌های برجسته فقط کاربردی نیستند؛ پهلوهای شلوار را پرتر نشان می‌دهند. اگر جیب‌ها بزرگ یا چندلایه‌اند، جای چاپ، کیف و اکسسوری‌های حجیم را آگاهانه انتخاب کن تا همه جزئیات برای جلب توجه رقابت نکنند.</p>
<h2>کارگو و استایل مونوکروم</h2><p>مونوکروم لزوماً یعنی یک رنگ دقیق نیست. می‌توانی چند تون نزدیک را کنار هم بگذاری و با تفاوت بافت و حجم، عمق ایجاد کنی. جیب‌ها در چنین ترکیبی بدون نیاز به رنگ متضاد هم ساختار ایجاد می‌کنند.</p>
<h2>اکسسوری با کارگو؛ کمتر یا بیشتر؟</h2><p>مقدار اکسسوری به شلوغی خود شلوار و بالاتنه بستگی دارد. کلاه، کیف یا زیور می‌تواند مکمل باشد، اما قانون عددی ثابتی وجود ندارد. قبل از اضافه کردن هر آیتم ببین آیا نقش مشخصی در ترکیب دارد یا فقط یک نقطه کانونی دیگر می‌سازد.</p>
<h2>اشتباه‌های رایج در استایل شلوار کارگو</h2><ul><li>فرض کردن اینکه همه کارگوها یک فیت دارند.</li><li>انتخاب کفش بدون توجه به عرض دمپا و قد شلوار.</li><li>بزرگ‌تر خریدن کمر برای ساختن فیت بگ.</li><li>استفاده از چند جزئیات خیلی شلوغ بدون تصمیم آگاهانه.</li><li>کپی کردن یک فرمول ثابت بدون توجه به تناسب واقعی لباس‌های خودت.</li></ul>
<h2>چهار فرمول ساده برای شروع</h2><ul><li>کارگوی آزاد + تیشرت باکسی ساده + کتانی تمیز.</li><li>کارگوی راسته + تیشرت گرافیکی کنترل‌شده + کتانی کم‌حجم.</li><li>کارگوی تیره + تیشرت روشن + پیراهن باز کوتاه‌تر.</li><li>کارگوی خنثی + بالاتنه هم‌خانواده + یک اکسسوری نقطه‌ای.</li></ul>
<h2>راهنماهای مرتبط</h2><p>برای فهم تفاوت حجم‌ها <a href="$a3">راهنمای بگ، نیم‌بگ و فول‌بگ</a>، برای شناخت خود آیتم <a href="$a14">راهنمای شلوار کارگو</a> و برای انتخاب کفش <a href="$a11">راهنمای خرید کتانی روزمره</a> را بخوان. مدل‌های فعلی <a href="$cu">شلوار کارگو مردانه Gramiss</a> هم نقطه اتصال این راهنما به موجودی واقعی فروشگاه هستند.</p>
HTML;
$c19=<<<HTML
<p>پیراهن آستین کوتاه را فقط با «تابستانی بودن» تعریف نکن. فیت بدن، عرض سرشانه، قد پیراهن، شکل یقه و حجم شلواری که زیر آن می‌پوشی تعیین می‌کنند استایل نهایی جمع‌وجور، رها یا لایه‌ای دیده شود.</p>
<p>اگر هنوز اندازه پیراهن را دقیق نمی‌دانی، اول <a href="$a12">راهنمای انتخاب سایز پیراهن مردانه</a> را بخوان. این صفحه درباره استایل است، نه اندازه‌گیری و نه مراقبت اختصاصی پارچه لینن.</p>
<h2>از فیت و قد پیراهن شروع کن</h2><p>پیراهن کوتاه‌تر و باکسی رفتار متفاوتی از مدل بلند و رگولار دارد. قبل از انتخاب شلوار، ببین لبه پیراهن در کجای بدن می‌ایستد و عرض آن نسبت به شلوار چقدر است.</p>
<h2>پیراهن آستین کوتاه را بسته بپوشیم یا باز؟</h2><p>حالت بسته یک سطح بصری یکپارچه می‌سازد؛ حالت باز، تیشرت زیر را وارد ترکیب می‌کند و دو خط عمودی جدید می‌سازد. هیچ‌کدام ذاتاً رسمی‌تر یا بهتر نیستند؛ جنس، یقه، طرح و بقیه آیتم‌ها هم اثر دارند.</p>
<h2>لایه‌بندی با تیشرت زیر پیراهن</h2><p>اگر پیراهن را باز می‌پوشی، یقه و قد تیشرت زیر را هم جزو استایل حساب کن. تیشرت خیلی بلندتر از پیراهن یا چاپی که با طرح پیراهن رقابت می‌کند می‌تواند نتیجه را شلوغ کند؛ مگر اینکه عمداً همین هدف را داشته باشی.</p>
<h2>پیراهن آستین کوتاه با شلوار جین</h2><p>جین روشن، تیره، راسته یا آزاد هرکدام حس متفاوتی می‌دهند. فیت پیراهن را با فیت جین هماهنگ کن و برای معیارهای خرید خود شلوار، <a href="$a9">راهنمای خرید شلوار جین مردانه</a> را ببین.</p>
<h2>پیراهن آستین کوتاه با شلوار پارچه‌ای</h2><p>این ترکیب فقط مخصوص استایل رسمی نیست. شلوار پارچه‌ای آزاد با پیراهن رها می‌تواند کژوال باشد و مدل ساختارمندتر می‌تواند ظاهر مرتب‌تری بسازد. راهنمای <a href="$a17">خرید شلوار پارچه‌ای مردانه</a> فاق، ران، دمپا و افت پارچه را جداگانه توضیح می‌دهد.</p>
<h2>با شلوار بگ چطور حجم را کنترل کنیم؟</h2><p>اگر شلوار خیلی حجیم است، می‌توانی پیراهن جمع‌وجورتری انتخاب کنی یا آگاهانه حجم بالا و پایین را زیاد نگه داری. به‌جای قانون «یکی حتماً باید فیت باشد»، سیلوئت کامل را ببین.</p>
<h2>داخل شلوار یا بیرون؟</h2><p>طول پیراهن و فرم لبه تعیین‌کننده‌اند. بعضی مدل‌ها برای بیرون ماندن طراحی شده‌اند و بعضی با داخل رفتن ساختار متفاوتی می‌گیرند. اگر مشخصات محصول درباره فرم لبه چیزی نمی‌گوید، از عکس و اندازه واقعی کمک بگیر.</p>
<h2>با پیراهن آستین کوتاه چه کفشی بپوشیم؟</h2><p>کفش را بر اساس میزان کژوال یا مرتب بودن کل ترکیب انتخاب کن. کتانی، لوفر یا مدل‌های ساده چرمی می‌توانند در شرایط متفاوت کار کنند؛ اما این مقاله روی موجودی فعلی Gramiss، یعنی کتانی، تمرکز تجاری دارد.</p>
<h2>کتانی را با حجم شلوار هماهنگ کن</h2><p>وقتی شلوار آزاد و بلند است، حجم کفش در خط پایین استایل اهمیت بیشتری پیدا می‌کند. برای انتخاب کاربرد، رویه و زیره از <a href="$a11">راهنمای خرید کتانی مردانه</a> استفاده کن و مدل‌های <a href="$su">کتانی Gramiss</a> را کنار شلوار اصلی مقایسه کن.</p>
<h2>طرح پیراهن و شلوغی بقیه استایل</h2><p>پیراهن طرح‌دار الزاماً به شلوار ساده نیاز ندارد، اما باید بدانی چند نقطه کانونی می‌سازی. اگر طرح پیراهن پرقدرت است، کفش و اکسسوری ساده‌تر می‌توانند فضا بدهند؛ یا می‌توانی آگاهانه استایل شلوغ‌تری بسازی.</p>
<h2>رنگ را با کمد واقعی خودت انتخاب کن</h2><p>به‌جای نسخه ثابت «فلان رنگ با فلان رنگ»، سه شلواری را که بیشتر می‌پوشی کنار پیراهن بگذار. نور، جنس و شدت رنگ روی هماهنگی اثر دارند. چند ترکیب خنثی نقطه شروع خوبی هستند، نه قانون اجباری.</p>
<h2>آستین و یقه چه اثری روی تناسب دارند؟</h2><p>عرض آستین و اندازه یقه می‌توانند پیراهن را ساختارمند یا رها نشان دهند. این جزئیات را همراه با سرشانه و عرض سینه ببین؛ نه جدا از فیت کلی.</p>
<h2>استایل لینن را با استایل عمومی پیراهن یکی نکن</h2><p>لینن رفتار بافتی و چروک خاص خودش را دارد و مقاله <a href="$a6">استایل با پیراهن لینن مردانه</a> همان نیت تخصصی را پوشش می‌دهد. این صفحه عمداً برای همه پیراهن‌های آستین کوتاه نوشته شده و وارد ادعا درباره ترکیب الیاف نمی‌شود.</p>
<h2>اکسسوری و لایه سوم</h2><p>کلاه، کیف یا یک لایه بیرونی می‌تواند ترکیب را کامل کند، اما باید با یقه و طرح پیراهن رقابت نکند مگر اینکه عمداً استایل پرجزئیات بخواهی. کاربرد واقعی آیتم را هم کنار ظاهر در نظر بگیر.</p>
<h2>اشتباه‌های رایج در استایل پیراهن آستین کوتاه</h2><ul><li>نادیده گرفتن قد پیراهن نسبت به فاق شلوار.</li><li>فرض کردن اینکه آستین کوتاه فقط با شلوار جذب هماهنگ است.</li><li>انتخاب تیشرت زیر بدون توجه به یقه و طول دو لایه.</li><li>کپی کردن قواعد رنگی ثابت بدون دیدن جنس و نور واقعی.</li><li>انتخاب کفش جدا از عرض و قد شلوار.</li></ul>
<h2>چهار فرمول کاربردی برای شروع</h2><ul><li>پیراهن ساده بسته + جین راسته + کتانی تمیز.</li><li>پیراهن باکسی باز + تیشرت ساده + شلوار پارچه‌ای آزاد.</li><li>پیراهن طرح‌دار + شلوار خنثی + کفش کم‌جزئیات.</li><li>پیراهن تک‌رنگ + شلوار هم‌خانواده + یک اکسسوری نقطه‌ای.</li></ul>
<h2>راهنماهای مرتبط</h2><p>برای اندازه <a href="$a12">راهنمای سایز پیراهن</a>، برای لینن <a href="$a6">راهنمای استایل پیراهن لینن</a>، برای جین <a href="$a9">راهنمای خرید شلوار جین</a> و برای کفش <a href="$a11">راهنمای خرید کتانی</a> را بخوان. مدل‌های موجود در <a href="$ssu">پیراهن آستین کوتاه مردانه Gramiss</a> و <a href="$shu">دسته پیراهن مردانه</a> را هم می‌توانی با این معیارها مقایسه کنی.</p>
HTML;

$id18=wp_insert_post(['post_title'=>'با شلوار کارگو مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و حجم لباس','post_name'=>$slug18,'post_content'=>$c18,'post_status'=>'publish','post_type'=>'post','post_category'=>[(int)$style->term_id]],true);
if(is_wp_error($id18)){g1819_rollback_local($created,$snapshot,$rollback);http_response_code(500);echo wp_json_encode(['error'=>'insert18','detail'=>$id18->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}$created[]=(int)$id18;g1819_meta($id18,'با شلوار کارگو مردانه چی بپوشیم؟ راهنمای استایل','برای استایل با شلوار کارگو مردانه، تیشرت، پیراهن، کتانی و حجم بالاتنه را بر اساس فیت و دمپای همان شلوار هماهنگ کنید؛ با فرمول‌های کاربردی و بدون قانون‌های خشک.','با شلوار کارگو مردانه چی بپوشیم');
$id19=wp_insert_post(['post_title'=>'پیراهن آستین کوتاه مردانه را با چی بپوشیم؟ شلوار، کفش و لایه‌بندی','post_name'=>$slug19,'post_content'=>$c19,'post_status'=>'publish','post_type'=>'post','post_category'=>[(int)$style->term_id]],true);
if(is_wp_error($id19)){g1819_rollback_local($created,$snapshot,$rollback);http_response_code(500);echo wp_json_encode(['error'=>'insert19','detail'=>$id19->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}$created[]=(int)$id19;g1819_meta($id19,'پیراهن آستین کوتاه مردانه با چی بپوشیم؟ راهنمای استایل','پیراهن آستین کوتاه مردانه را با جین، شلوار پارچه‌ای، کتانی و لایه‌بندی درست ست کنید؛ انتخاب فیت، قد پیراهن و حجم شلوار را مرحله‌به‌مرحله بررسی کنید.','پیراهن آستین کوتاه مردانه با چی بپوشیم');
$u18=get_permalink($id18);$u19=get_permalink($id19);
$blocks=[
468=>'<div data-g1-wave="1819-cargo-style-from-07"><h2>اگر شلوار شما کارگو است، استایل را دقیق‌تر ادامه بده</h2><p>کارگو می‌تواند بگ باشد، اما جیب‌ها و ساختار خودش یک لایه بصری اضافه می‌کنند. <a href="'.esc_url($u18).'">راهنمای استایل شلوار کارگو مردانه</a> این تفاوت را برای تیشرت و کفش جدا بررسی می‌کند.</p></div>',
492=>'<div data-g1-wave="1819-cargo-style-from-14"><h2>بعد از شناخت کارگو، سراغ استایل آن برو</h2><p>اگر ساختار و فیت کارگو را شناختی، مرحله بعد <a href="'.esc_url($u18).'">انتخاب تیشرت، کفش و حجم مناسب برای استایل کارگو</a> است.</p></div>',
467=>'<div data-g1-wave="1819-shortshirt-style-from-06"><h2>برای پیراهن آستین کوتاه غیرلینن، راهنمای عمومی را ببین</h2><p>این مقاله روی لینن متمرکز است. برای مدل‌های دیگر، <a href="'.esc_url($u19).'">راهنمای استایل پیراهن آستین کوتاه مردانه</a> شلوار، کفش و لایه‌بندی را جدا بررسی می‌کند.</p></div>',
487=>'<div data-g1-wave="1819-shortshirt-style-from-12"><h2>بعد از انتخاب سایز، استایل پیراهن آستین کوتاه را کامل کن</h2><p>وقتی اندازه مرجع مشخص شد، <a href="'.esc_url($u19).'">راهنمای استایل پیراهن آستین کوتاه</a> کمک می‌کند قد پیراهن، شلوار، کفش و لایه زیر را هماهنگ کنی.</p></div>'
];
foreach($blocks as $id=>$block){$r=wp_update_post(['ID'=>$id,'post_content'=>$posts[$id]->post_content."\n".$block],true);if(is_wp_error($r)){g1819_rollback_local($created,$snapshot,$rollback);http_response_code(500);echo wp_json_encode(['error'=>'source update','id'=>$id],JSON_UNESCAPED_UNICODE);exit;}}
g1819_flush();
echo wp_json_encode(['ok'=>true,'rollback_key'=>$rollback,'a18'=>['id'=>(int)$id18,'url'=>$u18],'a19'=>['id'=>(int)$id19,'url'=>$u19],'published'=>(int)wp_count_posts('post')->publish,'style_count'=>(int)get_term_by('slug','style-guide','category')->count],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES); ?>'''

status, mutation, final = run_public_php(probe_name, php, 300)
print("MUTATION", status, final, json.dumps(mutation, ensure_ascii=False))
if status != 200 or not mutation.get("ok"):
    raise SystemExit("FAIL mutation")

rollback_key = mutation["rollback_key"]
id18 = int(mutation["a18"]["id"])
id19 = int(mutation["a19"]["id"])
url18 = mutation["a18"]["url"]
url19 = mutation["a19"]["url"]
created_ids = [id18, id19]
success = False
verification_errors = []


def cleanup_snapshot():
    name = "gramiss-wave-18-19-cleanup-" + nonce + ".php"
    key = json.dumps(rollback_key, ensure_ascii=False)
    script = "<?php header('Content-Type: application/json; charset=utf-8'); define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; @unlink(__FILE__); $k=" + key + "; delete_option($k); echo wp_json_encode(['ok'=>true]); ?>"
    cs, cp, _ = run_public_php(name, script, 180)
    print("CLEANUP", cs, cp)
    if cs != 200 or not cp.get("ok"):
        raise RuntimeError("rollback snapshot cleanup failed")


def rollback():
    name = "gramiss-wave-18-19-rollback-" + nonce + ".php"
    key = json.dumps(rollback_key, ensure_ascii=False)
    ids = "[" + ",".join(str(x) for x in created_ids) + "]"
    script = "<?php header('Content-Type: application/json; charset=utf-8'); define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; @unlink(__FILE__); $k=" + key + "; $ids=" + ids + "; $s=get_option($k,[]); foreach($s as $id=>$content){wp_update_post(['ID'=>(int)$id,'post_content'=>$content]);} foreach($ids as $id){wp_delete_post((int)$id,true);} delete_option($k); global $wpdb; $wpdb->query(\"DELETE FROM {$wpdb->options} WHERE option_name LIKE '_transient_rank_math_sitemap_%' OR option_name LIKE '_transient_timeout_rank_math_sitemap_%'\"); wp_cache_flush(); do_action('litespeed_purge_all'); echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish]); ?>"
    rs, rp, _ = run_public_php(name, script, 240)
    print("ROLLBACK", rs, rp)
    return rs == 200 and rp.get("ok")


try:
    # Public article verification.
    expected_new = {
        id18: (url18, TITLE18, META18, DESC18),
        id19: (url19, TITLE19, META19, DESC19),
    }
    for pid, (url, title, mt, md) in expected_new.items():
        st, raw, final_url = get(url + "?t=" + str(int(time.time())), 180)
        text = raw.decode("utf-8", "replace")
        metadata = meta(raw)
        h2 = len(re.findall(r"<h2\b", text, re.I))
        blogposting = bool(re.search(r'"@type"\s*:\s*"BlogPosting"', text, re.I))
        product_schema = bool(re.search(r'"@type"\s*:\s*"Product"', text, re.I))
        print("NEW_ARTICLE", pid, st, final_url, "H2", h2, metadata, "BLOGPOSTING", blogposting, "PRODUCT", product_schema)
        if st != 200:
            verification_errors.append("http " + str(pid))
        if title not in text:
            verification_errors.append("rendered h1/title " + str(pid))
        if metadata.get("title") != mt or metadata.get("description") != md:
            verification_errors.append("meta " + str(pid))
        if norm(metadata.get("canonical", "")) != norm(url):
            verification_errors.append("canonical " + str(pid))
        robots = metadata.get("robots", "").lower()
        if "noindex" in robots or "index" not in robots:
            verification_errors.append("robots " + str(pid))
        if not blogposting or product_schema:
            verification_errors.append("schema " + str(pid))
        if h2 < 14:
            verification_errors.append("h2 " + str(pid))

    # Source backlinks must be public and unique enough to resolve to the new owner pages.
    source_requirements = {
        468: url18,
        492: url18,
        467: url19,
        487: url19,
    }
    # Reuse canonical URLs from a small WP state probe rather than hardcoding Persian paths.
    state_name = "gramiss-wave-18-19-state-" + nonce + ".php"
    state_php = r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$ids=[467,468,487,492];$u=[];foreach($ids as $id)$u[$id]=get_permalink($id);$style=get_term_by('slug','style-guide','category');$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$buy=get_term_by('slug','buying-guide','category');echo wp_json_encode(['published'=>(int)wp_count_posts('post')->publish,'style'=>(int)$style->count,'fit'=>(int)$fit->count,'fabric'=>(int)$fabric->count,'buy'=>(int)$buy->count,'urls'=>$u,'focus18'=>get_post_meta(%ID18%,'rank_math_focus_keyword',true),'focus19'=>get_post_meta(%ID19%,'rank_math_focus_keyword',true),'cat18'=>wp_get_post_categories(%ID18%,['fields'=>'slugs']),'cat19'=>wp_get_post_categories(%ID19%,['fields'=>'slugs'])],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES); ?>'''.replace("%ID18%", str(id18)).replace("%ID19%", str(id19))
    ss, sp, _ = run_public_php(state_name, state_php, 180)
    print("STATE_POST", ss, sp)
    if ss != 200 or sp.get("published") != 19 or sp.get("style") != 4 or sp.get("fit") != 7 or sp.get("fabric") != 4 or sp.get("buy") != 4:
        verification_errors.append("wp counts")
    if sp.get("focus18") != FOCUS18 or sp.get("focus19") != FOCUS19:
        verification_errors.append("focus")
    if sp.get("cat18") != ["style-guide"] or sp.get("cat19") != ["style-guide"]:
        verification_errors.append("categories")
    for pid, target in source_requirements.items():
        source_url = (sp.get("urls") or {}).get(str(pid)) or (sp.get("urls") or {}).get(pid)
        if not source_url:
            verification_errors.append("source url " + str(pid))
            continue
        st, raw, _ = get(source_url + "?t=" + str(int(time.time())), 150)
        text = raw.decode("utf-8", "replace")
        links = {norm(x) for x in re.findall(r'href=["\']([^"\']+)', text, re.I) if "gramiss.ir" in x}
        print("SOURCE_LINK", pid, st, target, norm(target) in links)
        if st != 200 or norm(target) not in links:
            verification_errors.append("source link " + str(pid))

    # New pages must connect to their intended editorial and commerce clusters.
    new_link_requirements = {
        url18: [commerce["cargo"], commerce["tshirt"], commerce["sneakers"]],
        url19: [commerce["shortshirt"], commerce["shirt"], commerce["sneakers"]],
    }
    for page_url, targets in new_link_requirements.items():
        st, raw, _ = get(page_url + "?t=" + str(int(time.time())), 150)
        text = raw.decode("utf-8", "replace")
        links = {norm(x) for x in re.findall(r'href=["\']([^"\']+)', text, re.I) if "gramiss.ir" in x}
        for target in targets:
            if norm(target) not in links:
                verification_errors.append("new commerce link " + target)

    # Give Rank Math a short convergence window for the post sitemap.
    post_status = 0
    post_urls = []
    for attempt in range(1, 7):
        post_status, post_urls = sitemap("post-sitemap.xml")
        print("POST_SITEMAP_ATTEMPT", attempt, post_status, len(post_urls))
        if post_status == 200 and len(post_urls) == 20 and norm(url18) in {norm(x) for x in post_urls} and norm(url19) in {norm(x) for x in post_urls}:
            break
        time.sleep(attempt * 2)
    cat_status, cat_urls = sitemap("category-sitemap.xml")
    product_status, product_urls_post = sitemap("product-sitemap.xml")
    pcat_status, pcat_urls_post = sitemap("product_cat-sitemap.xml")
    product_urls_post = sorted(product_urls_post)
    pcat_urls_post = sorted(pcat_urls_post)
    product_sha_post = hashlib.sha256("\n".join(product_urls_post).encode()).hexdigest()
    pcat_sha_post = hashlib.sha256("\n".join(pcat_urls_post).encode()).hexdigest()
    print("SITEMAPS_POST", post_status, len(post_urls), cat_status, len(cat_urls), product_status, len(product_urls_post), product_sha_post, pcat_status, len(pcat_urls_post), pcat_sha_post)
    if post_status != 200 or len(post_urls) != 20:
        verification_errors.append("post sitemap")
    if cat_status != 200 or len(cat_urls) != 4:
        verification_errors.append("category sitemap")
    if product_status != 200 or product_urls_post != product_urls_pre or product_sha_post != PRODUCT_SHA:
        verification_errors.append("product sitemap drift")
    if pcat_status != 200 or pcat_urls_post != pcat_urls_pre or pcat_sha_post != PCAT_SHA:
        verification_errors.append("product category sitemap drift")

    protected_post = {path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in PROTECTED}
    print("PROTECTED_POST", json.dumps(protected_post, ensure_ascii=False, sort_keys=True))
    if protected_post != protected_pre:
        verification_errors.append("protected UI drift")

    if verification_errors:
        raise RuntimeError("; ".join(verification_errors))
    cleanup_snapshot()
    success = True
    print("PASS EDITORIAL WAVE 18-19", json.dumps({
        "a18": {"id": id18, "url": url18},
        "a19": {"id": id19, "url": url19},
        "published": 19,
        "style_count": 4,
        "post_sitemap": len(post_urls),
        "product_sha": product_sha_post,
        "product_cat_sha": pcat_sha_post,
        "protected": protected_post,
    }, ensure_ascii=False))
except Exception as exc:
    print("VERIFY_EXCEPTION", repr(exc))
    ok = rollback()
    # Verify the known 17-article baseline after rollback.
    time.sleep(3)
    rs, ru = sitemap("post-sitemap.xml")
    rollback_protected = {path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in PROTECTED}
    print("ROLLBACK_VERIFY", ok, rs, len(ru), rollback_protected == protected_pre)
    if not ok or rs != 200 or len(ru) != 18 or rollback_protected != protected_pre:
        raise SystemExit("CRITICAL rollback verification failed")
    raise SystemExit("ROLLED BACK WAVE 18-19: " + str(exc))
