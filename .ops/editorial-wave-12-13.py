import base64
import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request


host = os.environ["CPANEL_HOST"]
user = os.environ["CPANEL_USER"]
token = os.environ["CPANEL_TOKEN"]
root = os.environ["THEME_ROOT"].strip("/")
healthy = os.environ.get("HEALTHY_HOME_SHA", "")
ctx = ssl._create_unverified_context()
BASE = "https://gramiss.ir"
EXPECTED_IDS = [453, 459, 460, 463, 464, 467, 468, 471, 472, 482, 483]
EXPECTED_TITLES = {
    453: "تیشرت باکسی چیست و چه تفاوتی با اورسایز دارد؟",
    459: "راهنمای انتخاب سایز تیشرت باکسی مردانه؛ اندازه‌گیری و فیت مناسب",
    460: "تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ کدام فیت مناسب شماست؟",
    463: "پارچه لینن چیست؟ راهنمای شناخت، چروک و انتخاب لباس لینن",
    464: "شست‌وشوی پیراهن لینن مردانه؛ راهنمای خشک‌کردن و اتوکشی",
    467: "استایل با پیراهن لینن مردانه؛ شلوار، کفش و ترکیب رنگ",
    468: "با شلوار بگ مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و قد شلوار",
    471: "راهنمای خرید تیشرت مردانه؛ فیت، اندازه، پارچه، دوخت و چاپ",
    472: "راهنمای خرید شلوار جین مردانه؛ فیت، قد، پارچه و جزئیات",
    482: "راهنمای انتخاب سایز کتانی مردانه؛ اندازه‌گیری پا برای خرید آنلاین",
    483: "راهنمای خرید کتانی مردانه برای استفاده روزمره؛ سایز، رویه و زیره",
}
TITLE_12 = "راهنمای انتخاب سایز پیراهن مردانه؛ سرشانه، سینه، قد و آستین"
TITLE_13 = "تمیز کردن کتانی سفید بدون آسیب؛ راهنمای رویه، بند و خشک‌کردن"
FOCUS_12 = "انتخاب سایز پیراهن مردانه"
FOCUS_13 = "تمیز کردن کتانی سفید"
META_TITLE_12 = "انتخاب سایز پیراهن مردانه؛ سرشانه، سینه و آستین"
META_TITLE_13 = "تمیز کردن کتانی سفید بدون آسیب؛ راهنمای مراقبت"
META_DESCRIPTION_12 = (
    "برای انتخاب سایز پیراهن مردانه، عرض سرشانه و سینه، قد لباس و طول آستین "
    "یک پیراهن مرجع را اندازه بگیرید و با اطلاعات همان مدل مقایسه کنید."
)
META_DESCRIPTION_13 = (
    "برای تمیز کردن کتانی سفید، ابتدا جنس و دستور مراقبت را بررسی کنید؛ گرد خشک، "
    "لکه‌گیری کنترل‌شده، بندها و خشک‌کردن را مرحله‌به‌مرحله مدیریت کنید."
)


def call(function, params, post=False):
    url = f"https://{host}:2083/execute/Fileman/{function}"
    data = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 5):
        try:
            request = urllib.request.Request(
                url if post else url + "?" + data.decode(),
                data=data if post else None,
                method="POST" if post else "GET",
            )
            request.add_header("Authorization", f"cpanel {user}:{token}")
            if post:
                request.add_header(
                    "Content-Type", "application/x-www-form-urlencoded"
                )
            with urllib.request.urlopen(request, context=ctx, timeout=90) as response:
                output = json.loads(response.read().decode("utf-8", "replace"))
            result = output.get("result") if isinstance(output.get("result"), dict) else output
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
    path, name = relative.rsplit("/", 1) if "/" in relative else ("", relative)
    data = call(
        "get_file_content",
        {
            "dir": root if not path else root + "/" + path,
            "file": name,
            "from_charset": "_DETECT_",
            "to_charset": "utf-8",
        },
    )
    if isinstance(data, dict):
        for key in ("content", "file_content", "data"):
            if isinstance(data.get(key), str):
                return data[key]
    return data if isinstance(data, str) else ""


def save_public(name, content):
    return call(
        "save_file_content",
        {
            "dir": "public_html",
            "file": name,
            "content": content,
            "from_charset": "UTF-8",
            "to_charset": "UTF-8",
            "fallback": "0",
        },
        True,
    )


def get(url, timeout=180):
    last = None
    for attempt in range(1, 5):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "GramissEditorialWave1213/1.0",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )
        try:
            with urllib.request.urlopen(request, context=ctx, timeout=timeout) as response:
                return (
                    response.status,
                    response.read(),
                    response.geturl(),
                    dict(response.headers),
                )
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), url, dict(exc.headers)
        except Exception as exc:
            last = exc
            print("HTTP_RETRY", attempt, url, exc)
            if attempt < 4:
                time.sleep(attempt * 2)
    raise last


def html_value(text, pattern):
    match = re.search(pattern, text, re.I | re.S)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def head(raw):
    text = raw.decode("utf-8", "replace").split("</head>", 1)[0]
    return {
        "title": html_value(text, r"<title[^>]*>(.*?)</title>"),
        "description": html_value(
            text,
            r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']*)",
        ),
        "canonical": html_value(
            text,
            r"<link[^>]+rel=[\"']canonical[\"'][^>]+href=[\"']([^\"']+)",
        ),
        "robots": html_value(
            text,
            r"<meta[^>]+name=[\"']robots[\"'][^>]+content=[\"']([^\"']+)",
        ),
    }


def norm(url):
    return urllib.parse.unquote(url).split("?", 1)[0].rstrip("/") + "/"


def sitemap(path):
    status, raw, _, _ = get(BASE + "/" + path + "?t=" + str(int(time.time())), 120)
    return status, [
        value.replace("&amp;", "&")
        for value in re.findall(
            r"<loc>(.*?)</loc>", raw.decode("utf-8", "replace"), re.I
        )
    ]


protected = [
    "front-page.php",
    "template-parts/home-looks.php",
    "assets/css/home-looks.css",
    "assets/js/home-looks.js",
]
protected_pre = {
    path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in protected
}
print("PROTECTED_PRE", json.dumps(protected_pre, ensure_ascii=False, sort_keys=True))
if healthy and protected_pre["front-page.php"] != healthy:
    raise SystemExit("ABORT Home mismatch")

product_status_pre, product_urls_pre = sitemap("product-sitemap.xml")
product_urls_pre = sorted(product_urls_pre)
product_sha_pre = hashlib.sha256("\n".join(product_urls_pre).encode()).hexdigest()
print("PRODUCT_SITEMAP_PRE", product_status_pre, len(product_urls_pre), product_sha_pre)
product_cat_status_pre, product_cat_urls_pre = sitemap("product_cat-sitemap.xml")
product_cat_urls_pre = sorted(product_cat_urls_pre)
product_cat_sha_pre = hashlib.sha256("\n".join(product_cat_urls_pre).encode()).hexdigest()
print(
    "PRODUCT_CAT_SITEMAP_PRE",
    product_cat_status_pre,
    len(product_cat_urls_pre),
    product_cat_sha_pre,
)
if product_status_pre != 200 or product_cat_status_pre != 200:
    raise SystemExit("ABORT Product Sitemap unavailable")

commerce = {
    "shirt": BASE + "/product-category/shirt/",
    "short_shirt": BASE + "/product-category/shirt/short-sleeve-shirt/",
    "long_shirt": BASE + "/product-category/shirt/long-sleeve-shirt/",
    "sneakers": BASE + "/product-category/sneakers/",
    "casual": BASE + "/product-category/sneakers/casual-sneakers/",
}
for label, url in commerce.items():
    status, raw, final, _ = get(url + "?t=" + str(int(time.time())), 120)
    metadata = head(raw)
    print(
        "COMMERCE_PRE",
        label,
        status,
        final,
        json.dumps(metadata, ensure_ascii=False, separators=(",", ":")),
    )
    robots = metadata.get("robots", "").lower()
    if (
        status != 200
        or "noindex" in robots
        or "index" not in robots
        or norm(metadata.get("canonical", "")) != norm(url)
    ):
        raise SystemExit("ABORT commerce archive " + label)
if not {norm(url) for url in commerce.values()}.issubset(
    {norm(url) for url in product_cat_urls_pre}
):
    raise SystemExit("ABORT commerce archive missing from Product Category Sitemap")

nonce = hashlib.sha256(
    (str(time.time()) + protected_pre["front-page.php"]).encode()
).hexdigest()[:14]
probe_name = "gramiss-editorial-wave-12-13-" + nonce + ".php"

php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$expected=[
453=>'تیشرت باکسی چیست و چه تفاوتی با اورسایز دارد؟',
459=>'راهنمای انتخاب سایز تیشرت باکسی مردانه؛ اندازه‌گیری و فیت مناسب',
460=>'تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ کدام فیت مناسب شماست؟',
463=>'پارچه لینن چیست؟ راهنمای شناخت، چروک و انتخاب لباس لینن',
464=>'شست‌وشوی پیراهن لینن مردانه؛ راهنمای خشک‌کردن و اتوکشی',
467=>'استایل با پیراهن لینن مردانه؛ شلوار، کفش و ترکیب رنگ',
468=>'با شلوار بگ مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و قد شلوار',
471=>'راهنمای خرید تیشرت مردانه؛ فیت، اندازه، پارچه، دوخت و چاپ',
472=>'راهنمای خرید شلوار جین مردانه؛ فیت، قد، پارچه و جزئیات',
482=>'راهنمای انتخاب سایز کتانی مردانه؛ اندازه‌گیری پا برای خرید آنلاین',
483=>'راهنمای خرید کتانی مردانه برای استفاده روزمره؛ سایز، رویه و زیره'];
$posts=[];$baseline_errors=[];
foreach($expected as $id=>$title){$p=get_post($id);$posts[$id]=$p;if(!$p||$p->post_status!=='publish'||$p->post_title!==$title)$baseline_errors[]='post '.$id;}
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');
$shirt=get_term_by('slug','shirt','product_cat');$short=get_term_by('slug','short-sleeve-shirt','product_cat');$long=get_term_by('slug','long-sleeve-shirt','product_cat');$sneakers=get_term_by('slug','sneakers','product_cat');$casual=get_term_by('slug','casual-sneakers','product_cat');
$slug12=sanitize_title('انتخاب سایز پیراهن مردانه');$slug13=sanitize_title('تمیز کردن کتانی سفید');
$old12=get_page_by_path($slug12,OBJECT,'post');$old13=get_page_by_path($slug13,OBJECT,'post');$published=(int)wp_count_posts('post')->publish;
if(!$fit||!$fabric||!$style||!$buy||!$shirt||!$short||!$long||!$sneakers||!$casual)$baseline_errors[]='term missing';
if($fit&&(int)$fit->count!==4)$baseline_errors[]='fit count';if($fabric&&(int)$fabric->count!==2)$baseline_errors[]='fabric count';if($style&&(int)$style->count!==2)$baseline_errors[]='style count';if($buy&&(int)$buy->count!==3)$baseline_errors[]='buy count';
if($shirt&&(int)$shirt->count<1)$baseline_errors[]='shirt empty';if($short&&(int)$short->count<1)$baseline_errors[]='short shirt empty';if($long&&(int)$long->count<1)$baseline_errors[]='long shirt empty';if($sneakers&&(int)$sneakers->count<1)$baseline_errors[]='sneakers empty';if($casual&&(int)$casual->count<1)$baseline_errors[]='casual empty';
if($published!==11)$baseline_errors[]='published count';if($old12||$old13)$baseline_errors[]='target slug exists';
foreach([[463,'data-g1-wave="1213-shirt-size-from-04"'],[467,'data-g1-wave="1213-shirt-size-from-06"'],[483,'data-g1-wave="1213-sneaker-care-from-11"']] as $item){if($posts[$item[0]]&&strpos($posts[$item[0]]->post_content,$item[1])!==false)$baseline_errors[]='marker '.$item[0];}
if($baseline_errors){http_response_code(409);echo wp_json_encode(['error'=>'baseline drift','details'=>$baseline_errors,'published'=>$published,'a12'=>$old12?$old12->ID:null,'a13'=>$old13?$old13->ID:null],JSON_UNESCAPED_UNICODE);exit;}
$shu=get_term_link($shirt);$ssu=get_term_link($short);$lsu=get_term_link($long);$su=get_term_link($sneakers);$cu=get_term_link($casual);foreach([$shu,$ssu,$lsu,$su,$cu] as $url){if(is_wp_error($url)){http_response_code(409);echo wp_json_encode(['error'=>'commerce URL']);exit;}}
$a4u=get_permalink($posts[463]);$a5u=get_permalink($posts[464]);$a6u=get_permalink($posts[467]);$a10u=get_permalink($posts[482]);$a11u=get_permalink($posts[483]);
$content12=<<<'HTML'
<p>انتخاب سایز پیراهن مردانه در خرید آنلاین با پیدا کردن یک حرف آشنا مثل M یا L تمام نمی‌شود. همین برچسب می‌تواند در دو مدل، دو الگوی برش یا حتی دو روش اندازه‌گذاری نتیجه متفاوتی داشته باشد. راه مطمئن‌تر این است که پیراهنی با فیت مناسب را به‌عنوان مرجع اندازه بگیری و عددهای آن را با اطلاعات دقیق همان محصولی که می‌خواهی سفارش بدهی مقایسه کنی.</p>
<p>این راهنما روی اندازه خود لباس تمرکز دارد: سرشانه، عرض سینه، قد و آستین. قرار نیست یک جدول عمومی را به همه برندها تعمیم بدهد یا درباره تغییر پارچه بعد از شست‌وشو حدس بزند. صفحه همان مدل و توضیح فروشنده همیشه مرجع نهایی تصمیم است.</p>
<h2>چرا S، M و L به‌تنهایی کافی نیستند؟</h2>
<p>حروف سایز فقط نام یک گزینه‌اند و بدون عددهای همان مدل، فضای واقعی لباس را نشان نمی‌دهند. دو پیراهن با برچسب یکسان ممکن است در سرشانه، سینه، قد یا آستین متفاوت باشند. فیت طراحی‌شده نیز مهم است؛ پیراهنی که آزاد معرفی شده نباید با معیار یک مدل جمع‌وجور سنجیده شود.</p>
<p>در <a href="SHIRT_URL">دسته پیراهن مردانه</a> ابتدا مدل مناسب را پیدا کن، سپس توضیحات و اندازه‌های همان صفحه را بخوان. نام دسته یا ظاهر عکس جای اطلاعات سایز محصول را نمی‌گیرد.</p>
<h2>یک پیراهن مرجع درست انتخاب کن</h2>
<p>پیراهنی را بردار که اکنون روی بدن تو خوب می‌ایستد و کاربردش به خرید جدید نزدیک است. اگر دنبال پیراهن آستین‌بلند روزمره هستی، تیشرت یا پیراهن رسمی بسیار جذب مرجع دقیقی نیست. دکمه‌ها را ببند، لباس را روی سطح صاف پهن کن و بدون کشیدن پارچه، چین‌های بزرگ را با دست مرتب کن.</p>
<p>مدل و حسی را که از پیراهن مرجع دوست داری یادداشت کن: سرشانه درست، آزادی سینه، قد مناسب و طول آستین. این یادداشت هنگام مقایسه دو سایز کمک می‌کند فقط به یک عدد نگاه نکنی.</p>
<h2>برای اندازه‌گیری چه چیزهایی لازم است؟</h2>
<p>یک متر خیاطی سالم، سطح صاف، کاغذ یا یادداشت گوشی و همان پیراهن مرجع کافی است. متر نباید پیچ‌خورده باشد و لباس هم نباید از گوشه میز آویزان شود. هر عدد را همان لحظه با نام دقیقش ثبت کن؛ «عرض سینه» را با «دور سینه» یکی ننویس.</p>
<p>اندازه‌گیری را یک‌بار دیگر تکرار کن. اگر نتیجه جابه‌جا شد، محل شروع و پایان متر را بررسی کن. هدف ساختن عددی قابل تکرار است، نه گرد کردن سریع برای رسیدن به سایز دلخواه.</p>
<h2>عرض سرشانه پیراهن را چطور بگیریم؟</h2>
<p>پشت پیراهن را رو به بالا قرار بده و فاصله مستقیم میان محل اتصال درز آستین به سرشانه در دو طرف را اندازه بگیر. متر باید روی خط طبیعی بالای پشت قرار بگیرد و داخل انحنای یقه نرود. اگر مدل سرشانه افتاده یا ساختار متفاوتی دارد، روش اندازه‌گیری فروشنده را مبنا قرار بده؛ چون جای درز در همه مدل‌ها یکسان نیست.</p>
<p>سرشانه یکی از نخستین نقاطی است که تفاوت فیت دیده می‌شود، اما به‌تنهایی سایز را تعیین نمی‌کند. عدد آن باید کنار عرض سینه، قد و فرم کلی مدل خوانده شود.</p>
<h2>عرض سینه لباس را درست ثبت کن</h2>
<p>پیراهن را دکمه‌بسته و صاف بگذار. عرض سینه معمولاً به‌صورت خط مستقیم از زیر یک حلقه آستین تا زیر حلقه دیگر روی جلوی لباس اندازه گرفته می‌شود. متر را نکش و پارچه را هم برای بیشتر شدن عدد تحت فشار قرار نده.</p>
<p>عرض صاف لباس با دور بدن یکی نیست. اگر جدول محصول «دور سینه» نوشته ولی تو «عرض سینه لباس» را داری، بدون توضیح روشن فروشنده این دو را مستقیماً برابر نگیر. ببین جدول دقیقاً اندازه بدن را می‌گوید یا اندازه خود لباس.</p>
<h2>قد پیراهن را از کجا اندازه بگیریم؟</h2>
<p>قد لباس را مطابق روش اعلام‌شده در صفحه محصول بگیر. یک روش رایج، اندازه‌گیری از بالاترین نقطه سرشانه نزدیک یقه تا پایین لبه لباس است، اما اگر فروشنده نقطه دیگری را تعریف کرده همان روش مقدم است. لبه هلالی یا اختلاف قد جلو و پشت نیز باید در توضیحات مدل در نظر گرفته شود.</p>
<p>قد مناسب به شیوه پوشیدن وابسته است. پیراهنی که بیشتر بیرون شلوار پوشیده می‌شود با مدلی که برای داخل شلوار در نظر گرفته شده یک تفسیر ندارد. عدد مرجع را با کاربرد واقعی خودت مقایسه کن.</p>
<h2>طول آستین‌بلند را چطور مقایسه کنیم؟</h2>
<p>برای اندازه‌گیری آستین روی لباس مرجع، محل شروع متر باید با روش جدول محصول هماهنگ باشد. بعضی جدول‌ها طول آستین را از درز سرشانه تا انتهای سرآستین می‌نویسند و بعضی روش دیگری دارند. مسیر متر را روی آستین صاف نگه دار و سرآستین را بدون کشیدن اندازه بگیر.</p>
<p>در <a href="LONG_URL">پیراهن‌های آستین‌بلند</a> علاوه بر طول، به فرم سرآستین و کاربرد توجه کن. عکس می‌تواند سرنخ بدهد، اما عدد و روش اندازه‌گیری همان مدل برای مقایسه معتبرتر است.</p>
<h2>آستین کوتاه را جداگانه بسنج</h2>
<p>در پیراهن آستین‌کوتاه، طول آستین و عرض دهانه آن روی حس فیت اثر دارند. جای پایان آستین در مدل مرجع را ثبت کن و با داده محصول بسنج. قانون ثابتی که برای همه بازوها و همه برش‌ها یک نقطه پایان تعیین کند قابل اتکا نیست.</p>
<p>مدل‌های <a href="SHORT_URL">پیراهن آستین‌کوتاه</a> را با یک مرجع هم‌نوع مقایسه کن. استفاده از آستین‌بلند تاخورده به‌عنوان تنها مرجع می‌تواند فرم واقعی آستین کوتاه را پنهان کند.</p>
<h2>فیت موردنظر تفسیر عددها را تغییر می‌دهد</h2>
<p>قبل از انتخاب سایز مشخص کن پیراهن را جمع‌وجور، معمولی یا آزاد می‌خواهی و خود محصول با چه فیتی معرفی شده است. بزرگ‌تر گرفتن یک مدل برای ساختن فیت آزاد همیشه نتیجه طراحی‌شده یک پیراهن آزاد را نمی‌دهد؛ سرشانه، حلقه آستین و قد ممکن است هم‌زمان تغییر کنند.</p>
<p>اگر می‌خواهی اثر حجم پیراهن بر ترکیب شلوار و کفش را بهتر ببینی، <a href="A6_URL">راهنمای استایل با پیراهن لینن مردانه</a> نمونه‌ای از خواندن فیت در کل استایل است. آن مقاله مالک intent استایل است؛ این صفحه فقط اندازه‌گیری و مقایسه سایز را توضیح می‌دهد.</p>
<h2>عددهای مرجع را با همان مدل محصول مقایسه کن</h2>
<p>یک جدول ساده برای خودت بساز: نام اندازه، عدد پیراهن مرجع، عدد هر سایز محصول و تفاوت میان آن‌ها. فقط ردیف‌هایی را وارد کن که فروشنده تعریف کرده است. اگر روش اندازه‌گیری جدول مشخص نیست، قبل از نتیجه‌گیری سؤال بپرس.</p>
<ul><li>آیا جدول مربوط به اندازه بدن است یا اندازه لباس؟</li><li>آیا عرض سینه نوشته شده یا دور سینه؟</li><li>قد از کدام نقطه شروع شده است؟</li><li>طول آستین از درز سرشانه محاسبه شده یا مسیر دیگری دارد؟</li><li>فیت مدل چگونه توصیف شده است؟</li></ul>
<p>مقایسه چند عدد کنار هم بهتر از تکیه بر یک ردیف است. ممکن است یک سایز در سینه نزدیک به مرجع باشد اما قد یا آستین آن برای ترجیح تو متفاوت باشد.</p>
<h2>اگر بین دو سایز بودیم چه کنیم؟</h2>
<p>قانون عمومی «همیشه بزرگ‌تر» یا «همیشه کوچک‌تر» برای همه پیراهن‌ها قابل دفاع نیست. اول ببین کدام اندازه برای تو محدودکننده‌تر است، فیت موردنظر چیست و صفحه محصول درباره قالب چه می‌گوید. سپس شرایط تعویض را پیش از پرداخت بخوان.</p>
<p>اگر داده کافی نداری، سؤال دقیق بپرس: اندازه واقعی همان سایز، روش اندازه‌گیری و تفاوت دو گزینه چیست. نبود اطلاعات را با جدول‌های عمومی اینترنتی پر نکن.</p>
<h2>رفتار پارچه را حدس نزن</h2>
<p>نام پارچه به‌تنهایی میزان کشش، افت یا تغییر بعد از شست‌وشو را ثابت نمی‌کند. ترکیب الیاف، بافت، تکمیل پارچه و دستور مراقبت می‌توانند متفاوت باشند. برای شناخت زمینه پارچه می‌توانی <a href="A4_URL">راهنمای پارچه لینن</a> را بخوانی، اما حتی آن اطلاعات هم جای مشخصات همان محصول را نمی‌گیرد.</p>
<p>اگر نگرانی تو تغییر اندازه پس از شست‌وشو است، لیبل و دستور همان لباس مقدم است. <a href="A5_URL">راهنمای شست‌وشوی پیراهن لینن</a> نیز عمداً از اعلام درصد ثابت آب‌رفت خودداری می‌کند؛ چون بدون داده مدل نباید عدد ساخت.</p>
<h2>اشتباه‌های رایج در انتخاب سایز پیراهن</h2>
<ul><li>انتخاب فقط با S، M یا L قبلی.</li><li>مقایسه دور بدن با عرض صاف لباس بدون توجه به تعریف جدول.</li><li>اندازه‌گیری پیراهن روی تخت نرم یا در حالت آویزان.</li><li>کشیدن پارچه و بزرگ‌تر ثبت کردن عدد.</li><li>استفاده از مرجعی با کاربرد و فیت کاملاً متفاوت.</li><li>نادیده گرفتن قد و آستین پس از تطبیق سینه.</li><li>فرض کشسانی یا آب‌رفت بر اساس نام پارچه.</li><li>خرید پیش از خواندن شرایط تعویض.</li></ul>
<h2>چک‌لیست نهایی پیش از خرید آنلاین</h2>
<ul><li>یک پیراهن مرجع هم‌کاربرد و خوش‌فیت انتخاب کرده‌ام.</li><li>سرشانه، عرض سینه، قد و آستین را دوبار اندازه گرفته‌ام.</li><li>می‌دانم جدول محصول اندازه بدن است یا لباس.</li><li>روش اندازه‌گیری فروشنده را با روش خودم یکسان کرده‌ام.</li><li>فیت موردنظر و فیت معرفی‌شده مدل را مقایسه کرده‌ام.</li><li>درباره رفتار پارچه ادعای تأییدنشده نساخته‌ام.</li><li>در صورت ابهام سؤال دقیق پرسیده‌ام.</li><li>شرایط تعویض را پیش از پرداخت خوانده‌ام.</li></ul>
<p>انتخاب دقیق سایز یعنی بتوانی تفاوت پیراهن مرجع و گزینه محصول را با چند عدد مشخص توضیح بدهی. اگر داده یک مدل ناقص است، تصمیم امن‌تر پرسیدن یا انتخاب محصولی با اطلاعات شفاف‌تر است، نه پر کردن فاصله با حدس.</p>
HTML;
$content12=strtr($content12,['SHIRT_URL'=>esc_url($shu),'SHORT_URL'=>esc_url($ssu),'LONG_URL'=>esc_url($lsu),'A4_URL'=>esc_url($a4u),'A5_URL'=>esc_url($a5u),'A6_URL'=>esc_url($a6u)]);
$a12=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای انتخاب سایز پیراهن مردانه؛ سرشانه، سینه، قد و آستین','post_name'=>$slug12,'post_excerpt'=>'برای انتخاب سایز پیراهن مردانه، سرشانه، عرض سینه، قد و آستین یک پیراهن مرجع را اندازه بگیرید و با اطلاعات دقیق همان مدل مقایسه کنید.','post_content'=>$content12,'post_category'=>[(int)$fit->term_id],'post_author'=>1]),true);
if(is_wp_error($a12)){http_response_code(500);echo wp_json_encode(['error'=>'article 12 insert','message'=>$a12->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a12u=get_permalink($a12);
$content13=<<<'HTML'
<p>تمیز کردن کتانی سفید یک نسخه ثابت برای همه کفش‌ها ندارد. رنگ سفید لکه و گرد را زودتر نشان می‌دهد، اما خطر اصلی این است که بدون شناخت رویه، چسب، رنگ، دوخت و دستور مراقبت سراغ یک ترفند عمومی برویم. محلولی که روی یک کفش پارچه‌ای جواب داده ممکن است برای چرم، جیر یا قطعات چسبی مدل دیگر مناسب نباشد.</p>
<p>این راهنما به‌جای وعده «سفید شدن مثل روز اول»، یک فرایند کم‌ریسک می‌دهد: اول دستور سازنده، بعد تشخیص جنس تا حد اطلاعات موجود، پاک کردن گرد خشک، آزمایش در نقطه کم‌دید، لکه‌گیری کنترل‌شده و خشک‌کردن با حفظ فرم. هرجا جنس یا روش مجاز روشن نیست، احتیاط از شدت تمیزکاری مهم‌تر است.</p>
<h2>اول دستور مراقبت همان کتانی را پیدا کن</h2>
<p>صفحه محصول، برچسب داخل کفش، جعبه یا راهنمای سازنده را بررسی کن. اگر روش، شوینده یا محدودیت مشخصی نوشته شده، همان دستور بر توصیه عمومی مقدم است. نبود دستور هم به معنی مجاز بودن سفیدکننده، ماشین لباس‌شویی، آب داغ یا گرمای مستقیم نیست.</p>
<p>اگر هنوز در مرحله انتخاب مدل هستی، <a href="A11_URL">راهنمای خرید کتانی مردانه</a> توضیح می‌دهد چطور اطلاعات رویه، آستر، کفی و زیره را پیش از خرید ثبت کنی. داشتن همین اطلاعات، مراقبت بعدی را قابل‌تصمیم‌تر می‌کند.</p>
<h2>پیش از خیس کردن، جنس و وضعیت کفش را بررسی کن</h2>
<p>فقط وقتی جنس را قطعی بدان که روی محصول یا راهنمای سازنده اعلام شده باشد. ظاهر عکس برای تشخیص دقیق کافی نیست. ممکن است یک کتانی چند متریال داشته باشد: رویه اصلی، پنل تزئینی، لبه زیره، بند و آستر هرکدام رفتار متفاوتی نشان دهند.</p>
<p>ترک، پوسته‌شدن، باز شدن چسب، دوخت آسیب‌دیده یا رنگ‌رفتگی قبلی را یادداشت کن. رطوبت و برس‌کشی می‌توانند آسیب موجود را بیشتر نمایان کنند. در چنین وضعیتی تمیزکاری گسترده را متوقف کن و راهنمای سازنده یا متخصص مناسب را بپرس.</p>
<h2>ابزار را کم و کنترل‌شده انتخاب کن</h2>
<p>برای شروع معمولاً یک برس بسیار نرم یا پارچه خشک، دو پارچه روشن و تمیز، ظرف کوچک و ابزار جدا برای بندها کافی است. هر شوینده فقط وقتی وارد فرایند شود که با جنس اعلام‌شده و دستور مراقبت سازگار باشد. ابزار زبر، پارچه رنگی یا اسفنج ساینده می‌تواند سطح را خط بیندازد یا رنگ منتقل کند.</p>
<p>مواد را مستقیماً و با حجم زیاد روی کفش نریز. مقدار کم و قابل‌کنترل کمک می‌کند واکنش سطح را ببینی و از خیس شدن بی‌دلیل لایه‌های داخلی جلوگیری کنی.</p>
<h2>گرد و خاک خشک را قبل از لکه‌گیری بردار</h2>
<p>بندها را شل کن و کفش را در فضای مناسب نگه دار. با برس نرم یا پارچه خشک، گرد آزاد را آرام از رویه، درزها و لبه زیره بردار. سابیدن خاک خشک همراه با آب می‌تواند آن را به خمیر تبدیل کند و به بافت یا شیارها ببرد.</p>
<p>حرکت را از بخش کم‌کثیف به سمت لکه‌های مشخص انجام بده و ابزار رویه را با ابزار زیره یکی نکن. این جداسازی ساده از انتقال آلودگی تیره به بخش سفید جلوگیری می‌کند.</p>
<h2>بندها و اجزای جداشدنی را مستقل مدیریت کن</h2>
<p>اگر دستور محصول اجازه می‌دهد، بندها را جدا کن تا رویه زیر آن‌ها و خود بند بهتر بررسی شود. روش شست‌وشوی بند باید با جنس و راهنمای آن سازگار باشد؛ همه بندهای سفید از یک الیاف یا رنگ ثابت ساخته نشده‌اند.</p>
<p>کفی را فقط اگر بدون فشار جدا می‌شود و سازنده محدودیتی نگذاشته خارج کن. کفی چسبیده را به زور نکش. قطعات جداشده را پیش از نصب دوباره کامل بررسی و خشک کن تا رطوبت در فضای بسته محبوس نشود.</p>
<h2>هر ماده را اول در نقطه کم‌دید آزمایش کن</h2>
<p>حتی محصولی که برای کفش معرفی شده باید روی بخش کوچک و کم‌دید آزمایش شود. مقدار کم استفاده کن، طبق دستور زمان بده و نتیجه را پس از خشک شدن بررسی کن. تغییر رنگ، زبری، هاله، نرم‌شدن چسب یا انتقال رنگ نشانه توقف است.</p>
<p>چند ماده را با هم ترکیب نکن. واکنش ترکیب‌های خانگی همیشه از ظاهر اولیه قابل پیش‌بینی نیست و قوی‌تر بودن به معنی مناسب‌تر بودن نیست.</p>
<h2>لکه‌گیری محافظه‌کارانه چگونه انجام می‌شود؟</h2>
<p>به‌جای خیس کردن کامل، از کمترین رطوبت و فشار لازم شروع کن. پارچه یا برس سازگار را به ماده مجاز آغشته و اضافه آن را کنترل کن، سپس روی محدوده کوچک کار کن. حرکت شدید و طولانی می‌تواند بافت را پرزدار یا سطح را ناهماهنگ کند.</p>
<p>آلودگی جداشده را با بخش تمیز پارچه بردار تا دوباره روی کفش پخش نشود. اگر لکه با چند حرکت ملایم تغییر نکرد، شدت را خودسرانه بالا نبر؛ دوباره جنس، نوع لکه و دستور محصول را بررسی کن.</p>
<h2>برای رویه پارچه‌ای چه ابهامی وجود دارد؟</h2>
<p>«پارچه‌ای» یک مشخصات کامل نیست. نوع الیاف، بافت، چاپ، لایه داخلی و چسب می‌توانند متفاوت باشند. از همین رو نمی‌توان دما، شوینده یا میزان خیس کردن یکسانی برای همه کتانی‌های پارچه‌ای نوشت.</p>
<p>اگر سازنده روش مشخصی داده، مرحله‌ها را دقیق دنبال کن. در غیر این صورت از لکه‌گیری محدود شروع کن و نتیجه آزمون کم‌دید را ملاک قرار بده. غوطه‌ور کردن کامل فقط به‌خاطر سفید بودن رویه تصمیم امنی نیست.</p>
<h2>چرم، چرم مصنوعی و مواد سنتتیک را یکی فرض نکن</h2>
<p>سطح صاف ممکن است چرم طبیعی، روکش‌دار یا سنتتیک باشد و هرکدام به پاک‌کننده و رطوبت واکنش متفاوتی نشان دهند. تشخیص را از نام محصول یا اطلاعات سازنده بگیر، نه فقط لمس یا عکس. محصول مراقبتی باید صریحاً برای همان جنس مناسب باشد.</p>
<p>اگر سطح ترک‌خورده، پوسته‌شده یا رنگ آن ناپایدار است، برس‌کشی و ماده قوی ریسک بیشتری دارد. در این وضعیت تمیزکاری حرفه‌ای یا راهنمایی سازنده از آزمون‌های پی‌درپی خانگی منطقی‌تر است.</p>
<h2>جیر و نبوک به احتیاط بیشتری نیاز دارند</h2>
<p>جیر و نبوک سطح پرزدار دارند و رطوبت یا مالش نامناسب می‌تواند بافت و رنگ آن‌ها را تغییر دهد. اگر محصول واقعاً از این جنس است، ابزار و روش اختصاصی اعلام‌شده برای همان متریال را دنبال کن. نسخه‌های عمومی کتانی سفید را روی آن اجرا نکن.</p>
<p>وقتی جنس قطعی نیست اما سطح پرزدار به نظر می‌رسد، خیس کردن را متوقف کن و از فروشنده، سازنده یا متخصص سؤال کن. هزینه یک بررسی کوتاه معمولاً از آسیب غیرقابل‌برگشت کمتر است.</p>
<h2>لبه و زیره سفید را جدا از رویه تمیز کن</h2>
<p>زیره و نوار کناری ممکن است ماده متفاوتی از رویه داشته باشند. برای آن‌ها ابزار جدا نگه دار و مراقب باش آلودگی تیره زیره به پارچه یا چرم منتقل نشود. ماده مناسب زیره لزوماً برای رویه مناسب نیست.</p>
<p>درز اتصال رویه و زیره را بیش از حد خیس نکن، به‌خصوص وقتی وضعیت چسب یا ساخت مشخص نیست. هدف پاک کردن کنترل‌شده سطح است، نه رساندن محلول به تمام لایه‌های کفش.</p>
<h2>ماشین لباس‌شویی فقط با اجازه روشن سازنده</h2>
<p>نمی‌توان گفت ماشین همیشه ممنوع یا همیشه مجاز است. اگر سازنده صریحاً شست‌وشوی ماشینی را مجاز دانسته، برنامه، دما، آماده‌سازی و روش خشک‌کردن نوشته‌شده را دقیق اجرا کن. اگر چنین اجازه‌ای وجود ندارد، از فرض گرفتن آن خودداری کن.</p>
<p>چرخش، آب‌گیری، گرما و زمان تماس با آب می‌توانند روی فرم، چسب یا مواد مختلف اثر بگذارند. سفید بودن کفش مجوز انتخاب برنامه قوی‌تر نیست.</p>
<h2>کتانی را چطور با حفظ فرم خشک کنیم؟</h2>
<p>پس از پاک کردن باقی‌مانده ماده مجاز طبق دستور، رطوبت سطحی را با پارچه تمیز و فشار ملایم بگیر. کفش را در فضای دارای جریان هوا و دور از منبع گرمای تأییدنشده قرار بده. شکل پنجه و بدنه را بدون کشش شدید حفظ کن.</p>
<p>نور مستقیم، سشوار، بخاری یا خشک‌کن را ایمن فرض نکن. فقط اگر سازنده روش خاصی را مجاز اعلام کرده همان را انجام بده. بند و کفی را زمانی برگردان که خود کفش و قطعات طبق بررسی کاملاً خشک شده باشند.</p>
<h2>چه زمانی تمیزکاری حرفه‌ای انتخاب بهتری است؟</h2>
<p>لکه ناشناخته، جنس ترکیبی، جیر یا نبوک، چرم آسیب‌دیده، رنگ ناپایدار و بازشدگی چسب از موقعیت‌هایی هستند که ادامه آزمون خانگی می‌تواند ریسک را بیشتر کند. عکس واضح و مشخصات محصول را برای سازنده یا متخصص بفرست و دقیق بگو چه کاری تاکنون انجام شده است.</p>
<p>اگر هدف اصلی تو حل فشار، لقی یا انتخاب اندازه است، تمیزکاری راه‌حل فیت نیست. برای آن موضوع <a href="A10_URL">راهنمای انتخاب سایز کتانی مردانه</a> را جداگانه ببین.</p>
<h2>اشتباه‌های رایج هنگام تمیز کردن کتانی سفید</h2>
<ul><li>شروع با سفیدکننده، آب‌اکسیژنه، جوش‌شیرین یا خمیردندان بدون تأیید سازگاری.</li><li>فرض اینکه همه کتانی‌های سفید یک جنس دارند.</li><li>خیس کردن کامل پیش از پاک کردن گرد خشک.</li><li>استفاده از برس زبر یا پارچه رنگی.</li><li>ترکیب چند ماده برای اثر قوی‌تر.</li><li>ندادن زمان کافی به آزمون نقطه کم‌دید تا خشک شود.</li><li>شستن ماشینی بدون اجازه روشن سازنده.</li><li>استفاده از گرمای مستقیم یا نور شدید بدون دستور معتبر.</li><li>نصب دوباره بند و کفی در حالت نم‌دار.</li></ul>
<h2>چک‌لیست کوتاه مراقبت</h2>
<ul><li>دستور مراقبت همان مدل را پیدا کرده‌ام.</li><li>جنس رویه و قطعات را فقط از اطلاعات معتبر ثبت کرده‌ام.</li><li>آسیب قبلی، چسب و ثبات رنگ را بررسی کرده‌ام.</li><li>گرد خشک را پیش از رطوبت برداشته‌ام.</li><li>بند و اجزای جداشدنی را مستقل مدیریت کرده‌ام.</li><li>ماده سازگار را روی نقطه کم‌دید آزمایش کرده‌ام.</li><li>با رطوبت و فشار کم از محدوده کوچک شروع کرده‌ام.</li><li>خشک‌کردن را با تهویه و بدون گرمای تأییدنشده انجام می‌دهم.</li><li>در صورت ابهام از سازنده یا متخصص کمک می‌گیرم.</li></ul>
<p>برای دیدن مدل‌های موجود می‌توانی <a href="SNEAKERS_URL">دسته کتانی مردانه</a> و <a href="CASUAL_URL">کتانی‌های روزمره</a> را بررسی کنی. صفحه زنده هر محصول مرجع جنس، دستور مراقبت و موجودی است؛ این راهنما هیچ ادعای مدل‌محور را جایگزین آن نمی‌کند.</p>
HTML;
$content13=strtr($content13,['SNEAKERS_URL'=>esc_url($su),'CASUAL_URL'=>esc_url($cu),'A10_URL'=>esc_url($a10u),'A11_URL'=>esc_url($a11u)]);
$a13=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'تمیز کردن کتانی سفید بدون آسیب؛ راهنمای رویه، بند و خشک‌کردن','post_name'=>$slug13,'post_excerpt'=>'برای تمیز کردن کتانی سفید، دستور مراقبت، جنس رویه، گرد خشک، لکه‌گیری کنترل‌شده، بندها و خشک‌کردن کم‌ریسک را مرحله‌به‌مرحله بررسی کنید.','post_content'=>$content13,'post_category'=>[(int)$fabric->term_id],'post_author'=>1]),true);
if(is_wp_error($a13)){wp_delete_post($a12,true);http_response_code(500);echo wp_json_encode(['error'=>'article 13 insert','message'=>$a13->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a13u=get_permalink($a13);
$meta=[$a12=>['rank_math_title'=>'انتخاب سایز پیراهن مردانه؛ سرشانه، سینه و آستین','rank_math_description'=>'برای انتخاب سایز پیراهن مردانه، عرض سرشانه و سینه، قد لباس و طول آستین یک پیراهن مرجع را اندازه بگیرید و با اطلاعات همان مدل مقایسه کنید.','rank_math_focus_keyword'=>'انتخاب سایز پیراهن مردانه'],$a13=>['rank_math_title'=>'تمیز کردن کتانی سفید بدون آسیب؛ راهنمای مراقبت','rank_math_description'=>'برای تمیز کردن کتانی سفید، ابتدا جنس و دستور مراقبت را بررسی کنید؛ گرد خشک، لکه‌گیری کنترل‌شده، بندها و خشک‌کردن را مرحله‌به‌مرحله مدیریت کنید.','rank_math_focus_keyword'=>'تمیز کردن کتانی سفید']];
foreach($meta as $id=>$values){foreach($values as $key=>$value)update_post_meta($id,$key,$value);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}
$originals=[463=>$posts[463]->post_content,467=>$posts[467]->post_content,483=>$posts[483]->post_content];$original_hashes=[];foreach($originals as $id=>$content)$original_hashes[$id]=hash('sha256',$content);
$bridge4='<div data-g1-wave="1213-shirt-size-from-04"><h2>پارچه را کنار اندازه واقعی پیراهن بسنج</h2><p>شناخت پارچه به درک افت و کاربرد لباس کمک می‌کند، اما برای تطبیق سرشانه، سینه، قد و آستین باید <a href="'.esc_url($a12u).'">راهنمای انتخاب سایز پیراهن مردانه</a> و اطلاعات دقیق همان مدل را هم بررسی کنی.</p></div>';
$bridge6='<div data-g1-wave="1213-shirt-size-from-06"><h2>فیت پیراهن را پیش از ساختن استایل اندازه بگیر</h2><p>ترکیب شلوار، کفش و رنگ زمانی دقیق‌تر می‌شود که حجم خود پیراهن را شناخته باشی؛ برای مقایسه سرشانه، سینه، قد و آستین از <a href="'.esc_url($a12u).'">راهنمای انتخاب سایز پیراهن مردانه</a> شروع کن.</p></div>';
$bridge11='<div data-g1-wave="1213-sneaker-care-from-11"><h2>بعد از خرید، روش مراقبت را از جنس واقعی شروع کن</h2><p>اطلاعات رویه، آستر و زیره‌ای که هنگام خرید ثبت کرده‌ای، مبنای تصمیم مراقبتی است؛ <a href="'.esc_url($a13u).'">راهنمای تمیز کردن کتانی سفید</a> مسیر کم‌ریسک لکه‌گیری و خشک‌کردن را مرحله‌به‌مرحله توضیح می‌دهد.</p></div>';
$r4=wp_update_post(wp_slash(['ID'=>$posts[463]->ID,'post_content'=>$originals[463]."\n".$bridge4]),true);$r6=wp_update_post(wp_slash(['ID'=>$posts[467]->ID,'post_content'=>$originals[467]."\n".$bridge6]),true);$r11=wp_update_post(wp_slash(['ID'=>$posts[483]->ID,'post_content'=>$originals[483]."\n".$bridge11]),true);
if(is_wp_error($r4)||is_wp_error($r6)||is_wp_error($r11)){
 wp_delete_post($a13,true);wp_delete_post($a12,true);
 foreach($originals as $id=>$content)wp_update_post(wp_slash(['ID'=>$id,'post_content'=>$content]));
 http_response_code(500);echo wp_json_encode(['error'=>'content bridge update']);exit;
}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
$live=[];foreach(array_keys($expected) as $id){$p=get_post($id);$live[$id]=['title'=>$p->post_title,'url'=>get_permalink($p)];}
echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'counts'=>['fit'=>(int)get_term($fit->term_id)->count,'fabric'=>(int)get_term($fabric->term_id)->count,'style'=>(int)get_term($style->term_id)->count,'buy'=>(int)get_term($buy->term_id)->count],'categories'=>['fit'=>get_term_link($fit),'fabric'=>get_term_link($fabric),'style'=>get_term_link($style),'buy'=>get_term_link($buy)],'existing'=>$live,'a12'=>['id'=>(int)$a12,'url'=>$a12u,'focus'=>get_post_meta($a12,'rank_math_focus_keyword',true)],'a13'=>['id'=>(int)$a13,'url'=>$a13u,'focus'=>get_post_meta($a13,'rank_math_focus_keyword',true)],'blog'=>get_permalink(22),'originals'=>array_map('base64_encode',$originals),'original_hashes'=>$original_hashes],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''


state = {}


def rollback(reason):
    print("ROLLBACK_REASON", reason)
    rollback_name = "gramiss-editorial-wave-12-13-rollback-" + nonce + ".php"
    snapshot_payload = base64.b64encode(
        json.dumps(state.get("originals", {}), separators=(",", ":")).encode()
    ).decode()
    rollback_php = r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
foreach([sanitize_title('انتخاب سایز پیراهن مردانه'),sanitize_title('تمیز کردن کتانی سفید')] as $slug){$post=get_page_by_path($slug,OBJECT,'post');if($post)wp_delete_post($post->ID,true);}
$snap=json_decode(base64_decode('SNAPSHOT_PAYLOAD'),true);$restored=[];
if(is_array($snap)&&$snap){foreach($snap as $id=>$encoded){$content=base64_decode($encoded,true);if($content!==false){wp_update_post(wp_slash(['ID'=>(int)$id,'post_content'=>$content]));$restored[(int)$id]=hash('sha256',$content);}}}
else{foreach([[463,'/\s*<div data-g1-wave="1213-shirt-size-from-04">.*?<\/div>\s*$/s'],[467,'/\s*<div data-g1-wave="1213-shirt-size-from-06">.*?<\/div>\s*$/s'],[483,'/\s*<div data-g1-wave="1213-sneaker-care-from-11">.*?<\/div>\s*$/s']] as $item){$post=get_post($item[0]);if($post&&preg_match($item[1],$post->post_content))wp_update_post(wp_slash(['ID'=>$post->ID,'post_content'=>preg_replace($item[1],'',$post->post_content,1)]));$post=get_post($item[0]);if($post)$restored[$item[0]]=hash('sha256',$post->post_content);}}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');echo wp_json_encode(['rolled_back'=>true,'published'=>(int)wp_count_posts('post')->publish,'counts'=>['fit'=>(int)$fit->count,'fabric'=>(int)$fabric->count,'style'=>(int)$style->count,'buy'=>(int)$buy->count],'restored_hashes'=>$restored],JSON_UNESCAPED_UNICODE);
?>'''.replace("SNAPSHOT_PAYLOAD", snapshot_payload)
    save_public(rollback_name, rollback_php)
    status, raw, _, _ = get(
        BASE + "/" + rollback_name + "?t=" + str(int(time.time())), 240
    )
    text = raw.decode("utf-8", "replace")
    print("ROLLBACK", status, text)
    if status != 200:
        raise SystemExit("ROLLBACK REQUEST FAILED after " + reason)
    data = json.loads(text)
    if data.get("published") != 11 or data.get("counts") != {
        "fit": 4,
        "fabric": 2,
        "style": 2,
        "buy": 3,
    }:
        raise SystemExit("ROLLBACK BASELINE FAILED after " + reason)
    expected_hashes = state.get("original_hashes", {})
    restored_hashes = {str(key): value for key, value in data.get("restored_hashes", {}).items()}
    if expected_hashes and restored_hashes != expected_hashes:
        raise SystemExit("ROLLBACK CONTENT SNAPSHOT FAILED after " + reason)
    product_status, product_urls = sitemap("product-sitemap.xml")
    product_cat_status, product_cat_urls = sitemap("product_cat-sitemap.xml")
    protected_now = {
        path: hashlib.sha256(read_theme(path).encode()).hexdigest()
        for path in protected
    }
    if (
        product_status != 200
        or sorted(product_urls) != product_urls_pre
        or product_cat_status != 200
        or sorted(product_cat_urls) != product_cat_urls_pre
        or protected_now != protected_pre
    ):
        raise SystemExit("ROLLBACK GLOBAL GUARD FAILED after " + reason)
    raise SystemExit("ROLLED BACK: " + reason)


save_public(probe_name, php)
try:
    write_status, write_raw, _, _ = get(
        BASE + "/" + probe_name + "?t=" + str(int(time.time())), 300
    )
except Exception as exc:
    rollback("write request exception: " + str(exc))
write_text = write_raw.decode("utf-8", "replace")
print("WRITE", write_status, write_text)
if write_status != 200:
    rollback("write returned HTTP " + str(write_status))
try:
    state = json.loads(write_text)
except Exception as exc:
    rollback("write JSON failure: " + str(exc))

errors = []
if state.get("published") != 13:
    errors.append("published post count")
if state.get("counts") != {"fit": 5, "fabric": 3, "style": 2, "buy": 3}:
    errors.append("editorial category counts")
if state.get("a12", {}).get("focus") != FOCUS_12:
    errors.append("Article 12 focus keyword")
if state.get("a13", {}).get("focus") != FOCUS_13:
    errors.append("Article 13 focus keyword")

a12_url = state["a12"]["url"]
a13_url = state["a13"]["url"]
existing_urls = {
    int(post_id): value["url"] for post_id, value in state["existing"].items()
}
all_pages = dict(existing_urls)
all_pages[state["a12"]["id"]] = a12_url
all_pages[state["a13"]["id"]] = a13_url
expected_live_titles = dict(EXPECTED_TITLES)
expected_live_titles[state["a12"]["id"]] = TITLE_12
expected_live_titles[state["a13"]["id"]] = TITLE_13

new_bodies = {}
for post_id, url in all_pages.items():
    status, raw, final, _ = get(url + "?t=" + str(int(time.time())), 180)
    metadata = head(raw)
    body = raw.decode("utf-8", "replace")
    h2_count = body.count("<h2>")
    print(
        "ARTICLE",
        post_id,
        status,
        final,
        json.dumps(metadata, ensure_ascii=False, separators=(",", ":")),
        "H2",
        h2_count,
        "BLOGPOSTING",
        "BlogPosting" in body,
    )
    if status != 200 or norm(final) != norm(url) or expected_live_titles[post_id] not in body:
        errors.append("article render " + str(post_id))
    if "g1-editorial-single" not in body:
        errors.append("article template " + str(post_id))
    if norm(metadata.get("canonical", "")) != norm(url):
        errors.append("article canonical " + str(post_id))
    robots = metadata.get("robots", "").lower()
    if "noindex" in robots or "index" not in robots or "follow" not in robots:
        errors.append("article robots " + str(post_id))
    if "BlogPosting" not in body or re.search(r'"@type"\s*:\s*"Product"', body, re.I):
        errors.append("article schema " + str(post_id))
    if h2_count < (10 if post_id in (state["a12"]["id"], state["a13"]["id"]) else 8):
        errors.append("article structure " + str(post_id))
    if post_id in (state["a12"]["id"], state["a13"]["id"]):
        new_bodies[post_id] = (body, metadata)

body12, metadata12 = new_bodies[state["a12"]["id"]]
body13, metadata13 = new_bodies[state["a13"]["id"]]
if metadata12.get("title") != META_TITLE_12 or metadata12.get("description") != META_DESCRIPTION_12:
    errors.append("Article 12 metadata")
if metadata13.get("title") != META_TITLE_13 or metadata13.get("description") != META_DESCRIPTION_13:
    errors.append("Article 13 metadata")
for required in (
    existing_urls[463],
    existing_urls[464],
    existing_urls[467],
    commerce["shirt"],
    commerce["short_shirt"],
    commerce["long_shirt"],
):
    if required not in body12:
        errors.append("Article 12 missing link " + required)
for required in (
    existing_urls[482],
    existing_urls[483],
    commerce["sneakers"],
    commerce["casual"],
):
    if required not in body13:
        errors.append("Article 13 missing link " + required)

for label, post_id, marker, targets in (
    (
        "A4",
        463,
        'data-g1-wave="1213-shirt-size-from-04"',
        [a12_url],
    ),
    (
        "A6",
        467,
        'data-g1-wave="1213-shirt-size-from-06"',
        [a12_url],
    ),
    (
        "A11",
        483,
        'data-g1-wave="1213-sneaker-care-from-11"',
        [a13_url],
    ),
):
    status, raw, _, _ = get(
        existing_urls[post_id] + "?t=" + str(int(time.time())), 180
    )
    body = raw.decode("utf-8", "replace")
    print("BRIDGE", label, status, marker in body)
    if status != 200 or marker not in body or not all(target in body for target in targets):
        errors.append(label + " bridge")

category_expectations = {
    "fit": (5, [TITLE_12, EXPECTED_TITLES[459], EXPECTED_TITLES[482]]),
    "fabric": (3, [TITLE_13, EXPECTED_TITLES[463], EXPECTED_TITLES[464]]),
    "style": (2, [EXPECTED_TITLES[467], EXPECTED_TITLES[468]]),
    "buy": (3, [EXPECTED_TITLES[471], EXPECTED_TITLES[472], EXPECTED_TITLES[483]]),
}
for label, url in state["categories"].items():
    expected_count, expected_titles = category_expectations[label]
    status, raw, final, _ = get(url + "?t=" + str(int(time.time())), 180)
    metadata = head(raw)
    body = raw.decode("utf-8", "replace")
    print("CATEGORY", label, status, final, json.dumps(metadata, ensure_ascii=False))
    robots = metadata.get("robots", "").lower()
    if (
        status != 200
        or norm(metadata.get("canonical", "")) != norm(url)
        or "noindex" in robots
        or "index" not in robots
        or "follow" not in robots
        or not all(title in body for title in expected_titles)
        or state["counts"][label] != expected_count
    ):
        errors.append("category " + label)

blog_status, blog_raw, blog_final, _ = get(
    state["blog"] + "?t=" + str(int(time.time())), 180
)
blog_metadata = head(blog_raw)
blog_body = blog_raw.decode("utf-8", "replace")
print("BLOG", blog_status, blog_final, json.dumps(blog_metadata, ensure_ascii=False))
blog_pages_body = blog_body
for page_number in range(2, 6):
    if all(title in blog_pages_body for title in expected_live_titles.values()):
        break
    blog_page = state["blog"].rstrip("/") + "/page/" + str(page_number) + "/"
    page_status, page_raw, page_final, _ = get(
        blog_page + "?t=" + str(int(time.time())), 180
    )
    print("BLOG_PAGE", page_number, page_status, page_final)
    if page_status != 200:
        break
    blog_pages_body += "\n" + page_raw.decode("utf-8", "replace")
if (
    blog_status != 200
    or norm(blog_metadata.get("canonical", "")) != norm(state["blog"])
    or "noindex" in blog_metadata.get("robots", "").lower()
    or TITLE_12 not in blog_body
    or TITLE_13 not in blog_body
    or not all(title in blog_pages_body for title in expected_live_titles.values())
):
    errors.append("blog archive")

post_status, post_urls = sitemap("post-sitemap.xml")
post_normalized = {norm(url) for url in post_urls}
print("POST_SITEMAP", post_status, len(post_urls))
if (
    post_status != 200
    or len(post_urls) != 14
    or not all(norm(url) in post_normalized for url in all_pages.values())
    or norm(state["blog"]) not in post_normalized
):
    errors.append("Post Sitemap")

category_status, category_urls = sitemap("category-sitemap.xml")
category_normalized = {norm(url) for url in category_urls}
print("CATEGORY_SITEMAP", category_status, len(category_urls))
if (
    category_status != 200
    or len(category_urls) != 4
    or not all(norm(url) in category_normalized for url in state["categories"].values())
):
    errors.append("Category Sitemap")

product_status_post, product_urls_post = sitemap("product-sitemap.xml")
product_urls_post = sorted(product_urls_post)
product_sha_post = hashlib.sha256("\n".join(product_urls_post).encode()).hexdigest()
print("PRODUCT_SITEMAP_POST", product_status_post, len(product_urls_post), product_sha_post)
if product_status_post != 200 or product_urls_post != product_urls_pre:
    errors.append("Product Sitemap changed")

product_cat_status_post, product_cat_urls_post = sitemap("product_cat-sitemap.xml")
product_cat_urls_post = sorted(product_cat_urls_post)
product_cat_sha_post = hashlib.sha256("\n".join(product_cat_urls_post).encode()).hexdigest()
print(
    "PRODUCT_CAT_SITEMAP_POST",
    product_cat_status_post,
    len(product_cat_urls_post),
    product_cat_sha_post,
)
if product_cat_status_post != 200 or product_cat_urls_post != product_cat_urls_pre:
    errors.append("Product Category Sitemap changed")

protected_post = {
    path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in protected
}
print("PROTECTED_POST", json.dumps(protected_post, ensure_ascii=False, sort_keys=True))
if protected_post != protected_pre:
    errors.append("protected UI changed")

if errors:
    print("VERIFY_ERRORS", json.dumps(errors, ensure_ascii=False))
    rollback("; ".join(errors))

print("PASS EDITORIAL WAVE 12-13")
print("ARTICLE_12", a12_url)
print("ARTICLE_13", a13_url)
print("PRODUCT_SITEMAP_SHA_PRESERVED", product_sha_post)
print("PRODUCT_CAT_SITEMAP_SHA_PRESERVED", product_cat_sha_post)
print("HOME_SHA_PRESERVED", protected_post["front-page.php"])
