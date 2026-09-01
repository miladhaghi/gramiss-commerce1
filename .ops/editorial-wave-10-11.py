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
EXPECTED_IDS = [453, 459, 460, 463, 464, 467, 468, 471, 472]
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
}
TITLE_10 = "راهنمای انتخاب سایز کتانی مردانه؛ اندازه‌گیری پا برای خرید آنلاین"
TITLE_11 = "راهنمای خرید کتانی مردانه برای استفاده روزمره؛ سایز، رویه و زیره"
FOCUS_10 = "انتخاب سایز کتانی مردانه"
FOCUS_11 = "راهنمای خرید کتانی مردانه"
META_TITLE_10 = "انتخاب سایز کتانی مردانه برای خرید آنلاین"
META_TITLE_11 = "راهنمای خرید کتانی مردانه؛ سایز، رویه و زیره"
META_DESCRIPTION_10 = (
    "برای انتخاب سایز کتانی مردانه، طول و عرض هر دو پا را درست اندازه بگیرید "
    "و نتیجه را با جدول همان مدل مقایسه کنید تا خرید آنلاین دقیق‌تری داشته باشید."
)
META_DESCRIPTION_11 = (
    "راهنمای خرید کتانی مردانه برای استفاده روزمره؛ کاربرد، سایز، رویه، آستر، "
    "کفی، زیره و جزئیات ساخت را بدون تکیه بر ادعاهای مبهم مقایسه کنید."
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
                "User-Agent": "GramissEditorialWave1011/1.0",
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
if product_status_pre != 200:
    raise SystemExit("ABORT Product Sitemap unavailable")

commerce = {
    "sneakers": BASE + "/product-category/sneakers/",
    "casual": BASE + "/product-category/sneakers/casual-sneakers/",
    "walking": BASE + "/product-category/sneakers/walking-shoes/",
    "tshirt": BASE + "/product-category/tshirt/",
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

nonce = hashlib.sha256(
    (str(time.time()) + protected_pre["front-page.php"]).encode()
).hexdigest()[:14]
probe_name = "gramiss-editorial-wave-10-11-" + nonce + ".php"

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
472=>'راهنمای خرید شلوار جین مردانه؛ فیت، قد، پارچه و جزئیات'];
$posts=[];$baseline_errors=[];
foreach($expected as $id=>$title){$p=get_post($id);$posts[$id]=$p;if(!$p||$p->post_status!=='publish'||$p->post_title!==$title)$baseline_errors[]='post '.$id;}
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');
$sneakers=get_term_by('slug','sneakers','product_cat');$casual=get_term_by('slug','casual-sneakers','product_cat');$walking=get_term_by('slug','walking-shoes','product_cat');$tshirt=get_term_by('slug','tshirt','product_cat');
$slug10=sanitize_title('انتخاب سایز کتانی مردانه');$slug11=sanitize_title('راهنمای خرید کتانی مردانه روزمره');
$old10=get_page_by_path($slug10,OBJECT,'post');$old11=get_page_by_path($slug11,OBJECT,'post');$published=(int)wp_count_posts('post')->publish;
if(!$fit||!$fabric||!$style||!$buy||!$sneakers||!$casual||!$walking||!$tshirt)$baseline_errors[]='term missing';
if($fit&&(int)$fit->count!==3)$baseline_errors[]='fit count';if($fabric&&(int)$fabric->count!==2)$baseline_errors[]='fabric count';if($style&&(int)$style->count!==2)$baseline_errors[]='style count';if($buy&&(int)$buy->count!==2)$baseline_errors[]='buy count';
if($sneakers&&(int)$sneakers->count<1)$baseline_errors[]='sneakers empty';if($casual&&(int)$casual->count<1)$baseline_errors[]='casual empty';if($walking&&(int)$walking->count<1)$baseline_errors[]='walking empty';
if($published!==9)$baseline_errors[]='published count';if($old10||$old11)$baseline_errors[]='target slug exists';
if($posts[468]&&strpos($posts[468]->post_content,'data-g1-cluster-wave="1011-sneakers"')!==false)$baseline_errors[]='article 7 marker';
if($posts[453]&&strpos($posts[453]->post_content,'data-g1-commerce-bridge="tshirt"')!==false)$baseline_errors[]='article 1 marker';
if($baseline_errors){http_response_code(409);echo wp_json_encode(['error'=>'baseline drift','details'=>$baseline_errors,'published'=>$published,'a10'=>$old10?$old10->ID:null,'a11'=>$old11?$old11->ID:null],JSON_UNESCAPED_UNICODE);exit;}
$su=get_term_link($sneakers);$cu=get_term_link($casual);$wu=get_term_link($walking);$tu=get_term_link($tshirt);foreach([$su,$cu,$wu,$tu] as $url){if(is_wp_error($url)){http_response_code(409);echo wp_json_encode(['error'=>'commerce URL']);exit;}}
$a6u=get_permalink($posts[467]);$a7u=get_permalink($posts[468]);$future11=home_url('/'.$slug11.'/');
$content10=<<<'HTML'
<p>انتخاب سایز کتانی در خرید آنلاین فقط پیدا کردن یک عدد آشنا نیست. ممکن است همیشه یک سایز مشخص بپوشی، اما قالب دو مدل، شکل پنجه، ضخامت آستر یا روشی که فروشنده اندازه را اعلام کرده یکسان نباشد. به همین دلیل، عدد روی جعبه باید نقطه شروع باشد؛ تصمیم نهایی باید از اندازه واقعی پا و جدول همان مدل بیاید.</p>
<p>این راهنما کمک می‌کند طول و عرض پا را با ابزار ساده اندازه بگیری، نتیجه را درست ثبت کنی و قبل از سفارش با اطلاعات صفحه محصول مقایسه کنی. هدف ارائه یک جدول جهانی یا قول فیت قطعی نیست؛ چون جدول و قالب خود محصول از هر قاعده عمومی مهم‌تر است.</p>
<h2>چرا عدد سایزی که همیشه می‌پوشی کافی نیست؟</h2>
<p>یک عدد مشترک لزوماً به معنی فضای داخلی یکسان نیست. طراحی پنجه، فرم پاشنه، ساختار رویه و حتی نوع استفاده می‌تواند حس دو کتانی هم‌سایز را متفاوت کند. اگر صفحه محصول درباره قالب یا جدول اندازه توضیح داده، همان اطلاعات را مبنا قرار بده و تجربه قبلی خودت را فقط برای مقایسه استفاده کن.</p>
<p>در <a href="SNEAKERS_URL">دسته کتانی مردانه</a> ابتدا مدل مناسب را پیدا کن، اما قبل از انتخاب گزینه سایز، اطلاعات همان محصول را جداگانه بخوان. عنوان دسته یا ظاهر عکس جای جدول سایز مدل را نمی‌گیرد.</p>
<h2>برای اندازه‌گیری پا چه چیزهایی لازم است؟</h2>
<p>یک برگ کاغذ بزرگ‌تر از پا، خودکار یا مداد، خط‌کش یا متر و جورابی که معمولاً با همان نوع کتانی می‌پوشی کافی است. سطح باید صاف باشد. کاغذ نرم روی فرش یا نگه داشتن متر در هوا می‌تواند نتیجه را جابه‌جا کند.</p>
<p>عددها را همان لحظه یادداشت کن. تکیه به حافظه یا گرد کردن زودهنگام باعث می‌شود هنگام مقایسه با جدول، جزئیات مفید از بین برود.</p>
<h2>هر دو پا را اندازه بگیر</h2>
<p>دو پا همیشه دقیقاً یک اندازه نیستند. برای هر پا طول و در صورت نیاز عرض را جدا ثبت کن و هنگام انتخاب، پایی را که فضای بیشتری نیاز دارد در نظر بگیر. این کار از حدس‌زدن بر اساس یک پا مطمئن‌تر است.</p>
<p>اگر اندازه‌ها غیرعادی یا نتیجه هر بار بسیار متفاوت بود، دوباره وضعیت ایستادن، محل پاشنه و راستای خط‌کش را بررسی کن؛ هدف این است که اندازه‌گیری قابل تکرار باشد.</p>
<h2>روش اندازه‌گیری طول پا روی کاغذ</h2>
<ol><li>کاغذ را روی سطح صاف بگذار و با جوراب معمولت روی آن بایست.</li><li>وزن را طبیعی بین دو پا تقسیم کن و پا را نچرخان.</li><li>پشت پاشنه و دورترین نقطه جلوی انگشت‌ها را علامت بزن.</li><li>فاصله مستقیم بین دو نقطه را اندازه بگیر و عدد را ثبت کن.</li><li>همین مراحل را برای پای دیگر تکرار کن.</li></ol>
<p>قلم را تا حد ممکن عمودی نگه دار. خواباندن قلم دور پا، طرح را بزرگ‌تر از اندازه واقعی نشان می‌دهد. اگر کسی کنارت هست، علامت‌گذاری توسط نفر دوم معمولاً کنترل وضعیت ایستادن را ساده‌تر می‌کند.</p>
<h2>عرض پا و شکل پنجه را نادیده نگیر</h2>
<p>دو نفر با طول پای مشابه می‌توانند عرض پنجه متفاوتی داشته باشند. اگر جدول محصول فقط طول را اعلام کرده، از روی عکس نمی‌توان با قطعیت درباره فضای داخلی نتیجه گرفت. توضیحات قالب، امکان پرسش از فروشگاه و تجربه یک کتانی مرجع می‌تواند اطلاعات تکمیلی بدهد.</p>
<p>به پهن یا باریک بودن ظاهری زیره به‌تنهایی تکیه نکن؛ نمای بیرونی همیشه فضای قابل استفاده داخل کتانی را نشان نمی‌دهد.</p>
<h2>اندازه پا را چطور با جدول همان مدل مقایسه کنیم؟</h2>
<p>اول واحد جدول را بررسی کن و مطمئن شو عدد مربوط به طول پا است یا طول کفی. این دو یکی نیستند و نباید بدون توضیح فروشنده به جای هم استفاده شوند. سپس عدد ثبت‌شده برای پای بزرگ‌تر را دقیقاً با ردیف‌های همان جدول مقایسه کن.</p>
<p>اگر صفحه محصول جدول ندارد یا نوع اندازه را روشن نکرده، از ساختن تبدیل شخصی و قطعی خودداری کن. قبل از سفارش سؤال بپرس یا مدلی را انتخاب کن که اطلاعات اندازه شفاف‌تری دارد.</p>
<h2>از یک کتانی مرجع کمک بگیر</h2>
<p>کتانی‌ای را انتخاب کن که همین حالا فیتش را دوست داری و کاربردش به خرید جدید نزدیک است. سایز نوشته‌شده، شکل پنجه و حس فضای جلو و پاشنه را یادداشت کن. اگر کفی آن بدون آسیب جدا می‌شود و فروشنده هم طول کفی را اعلام کرده، می‌توانی این دو عدد را مقایسه کنی؛ در غیر این صورت کفی را به زور خارج نکن.</p>
<p>کتانی مرجع یک سرنخ است، نه تضمین. دو مدل با ظاهر شبیه ممکن است قالب متفاوت داشته باشند.</p>
<h2>جوراب و کاربرد را قبل از اندازه‌گیری مشخص کن</h2>
<p>کتانی‌ای که با جوراب نازک روزمره می‌پوشی ممکن است حس متفاوتی از مدلی داشته باشد که برای جوراب ضخیم‌تر در نظر گرفته‌ای. اندازه‌گیری را با ترکیبی انجام بده که واقعاً استفاده می‌کنی و هنگام مقایسه محصول، کاربرد را هم ثابت نگه دار.</p>
<p>برای دیدن مدل‌هایی که با کاربرد روزانه معرفی شده‌اند، <a href="CASUAL_URL">کتانی‌های روزمره</a> را جدا از <a href="WALKING_URL">کفش‌های دسته پیاده‌روی</a> بررسی کن. قرار گرفتن یک محصول در دسته، جای خواندن مشخصات همان مدل را نمی‌گیرد.</p>
<h2>اگر بین دو سایز قرار گرفتی چه کار کنی؟</h2>
<p>یک قانون عمومی مثل «همیشه سایز بزرگ‌تر» برای همه مدل‌ها قابل دفاع نیست. ابتدا توضیح قالب، جدول همان محصول، نوع جوراب و سیاست تعویض را بررسی کن. اگر داده کافی نیست، از فروشگاه درباره اندازه داخلی یا تجربه قالب همان مدل سؤال کن.</p>
<p>همچنین مشکل طول را با عرض اشتباه نگیر. رفتن به عدد بزرگ‌تر شاید طول را زیاد کند، اما لزوماً مسئله فشار کناره پنجه را به شکل درست حل نمی‌کند.</p>
<h2>هنگام تحویل کتانی چه چیزهایی را بررسی کنیم؟</h2>
<p>تا زمانی که از انتخاب مطمئن نشده‌ای، کتانی را روی سطح تمیز و داخل خانه امتحان کن و بسته‌بندی را سالم نگه دار. پاشنه نباید هنگام چند قدم راه رفتن بی‌دلیل از پا جدا شود و انگشت‌ها نباید به شکل آزاردهنده جمع شوند. بندها را با فشار معمول خودت ببند؛ سفت‌کردن افراطی بند نباید راه اصلاح سایز اشتباه باشد.</p>
<p>شرایط تعویض همان فروشگاه را قبل از استفاده بیرون از خانه بخوان. سیاست‌ها ممکن است تغییر کنند و نباید از تجربه فروشگاه دیگری نتیجه گرفت.</p>
<h2>اشتباه‌های رایج در انتخاب سایز کتانی</h2>
<ul><li>سفارش فقط بر اساس عدد کتانی قبلی، بدون دیدن جدول مدل جدید.</li><li>اندازه‌گیری فقط یک پا.</li><li>اندازه‌گیری روی فرش یا در حالت نشسته و ناپایدار.</li><li>یکی گرفتن طول پا با طول کفی.</li><li>نادیده گرفتن عرض پنجه و نوع جوراب.</li><li>استفاده از جدول عمومی اینترنت به جای جدول همان محصول.</li><li>پوشیدن کتانی در فضای بیرون قبل از اطمینان از شرایط تعویض.</li></ul>
<h2>سایز را کنار معیارهای خرید ببین</h2>
<p>سایز درست فقط یکی از بخش‌های تصمیم است. در <a href="A11_URL">راهنمای خرید کتانی مردانه</a> می‌توانی کاربرد، رویه، آستر، کفی، زیره و جزئیات ساخت را هم با یک چک‌لیست ثابت مقایسه کنی.</p>
<p>اگر قرار است کتانی را با شلوار آزاد بپوشی، <a href="A7_URL">راهنمای استایل شلوار بگ مردانه</a> کمک می‌کند حجم کفش و شکست قد شلوار را هم در تصمیم ببینی.</p>
<h2>چک‌لیست نهایی قبل از ثبت سفارش</h2>
<ul><li>هر دو پا را با جوراب واقعی اندازه گرفته‌ام.</li><li>می‌دانم جدول، طول پا را نشان می‌دهد یا طول کفی.</li><li>عدد پای بزرگ‌تر را با جدول همان مدل مقایسه کرده‌ام.</li><li>عرض پنجه و توضیح قالب را بررسی کرده‌ام.</li><li>کاربرد روزمره یا پیاده‌روی را مشخص کرده‌ام.</li><li>شرایط تعویض و روش امتحان‌کردن محصول را خوانده‌ام.</li></ul>
<p>وقتی این اطلاعات کنار هم قرار بگیرند، انتخاب سایز از یک حدس سریع به یک مقایسه قابل توضیح تبدیل می‌شود؛ بدون اینکه درباره قالب محصولی که هنوز امتحان نکرده‌ای ادعای قطعی بسازی.</p>
HTML;
$content10=strtr($content10,['SNEAKERS_URL'=>esc_url($su),'CASUAL_URL'=>esc_url($cu),'WALKING_URL'=>esc_url($wu),'A11_URL'=>esc_url($future11),'A7_URL'=>esc_url($a7u)]);
$a10=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای انتخاب سایز کتانی مردانه؛ اندازه‌گیری پا برای خرید آنلاین','post_name'=>$slug10,'post_excerpt'=>'برای انتخاب سایز کتانی مردانه، هر دو پا را اندازه بگیرید و طول، عرض، جوراب و کاربرد را با جدول دقیق همان مدل مقایسه کنید.','post_content'=>$content10,'post_category'=>[(int)$fit->term_id],'post_author'=>1]),true);
if(is_wp_error($a10)){http_response_code(500);echo wp_json_encode(['error'=>'article 10 insert','message'=>$a10->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a10u=get_permalink($a10);
$content11=<<<'HTML'
<p>برای خرید کتانی مردانه، ظاهر اولین چیزی است که دیده می‌شود اما نباید تنها معیار تصمیم باشد. یک مدل زمانی انتخاب کاربردی‌تری است که نوع استفاده، فیت، اطلاعات رویه و آستر، ساختار کفی و زیره و جزئیات اجرای همان محصول را کنار هم ببینی. عکس خوب مفید است، ولی نمی‌تواند جای مشخصات نوشته‌شده و تجربه پوشیدن را بگیرد.</p>
<p>این راهنما به جای معرفی «بهترین کتانی»، یک روش مقایسه می‌دهد. هرجا اطلاعاتی در صفحه محصول موجود نیست، نتیجه قطعی نمی‌گیریم و از فروشنده سؤال می‌کنیم. موجودی، رنگ، جنس و ویژگی هر مدل هم باید از صفحه زنده همان محصول خوانده شود.</p>
<h2>اول کاربرد واقعی کتانی را مشخص کن</h2>
<p>از خودت بپرس کتانی را بیشتر برای رفت‌وآمد روزانه، زمان طولانی بیرون از خانه، پیاده‌روی برنامه‌ریزی‌شده یا تکمیل یک استایل می‌خواهی. پاسخ این سؤال مشخص می‌کند کدام ویژگی‌ها برایت اولویت دارد و مقایسه مدل‌ها را از یک انتخاب صرفاً تصویری جدا می‌کند.</p>
<p><a href="SNEAKERS_URL">آرشیو کتانی مردانه</a> نقطه شروع خوبی است. بعد می‌توانی <a href="CASUAL_URL">مدل‌های دسته روزمره</a> و <a href="WALKING_URL">مدل‌های دسته پیاده‌روی</a> را ببینی، اما عنوان دسته به‌تنهایی تضمین ویژگی فنی مشخصی نیست؛ توضیحات هر محصول همچنان مرجع اصلی است.</p>
<h2>کتانی روزمره و کفش پیاده‌روی را چطور مقایسه کنیم؟</h2>
<p>مرز این دو عنوان همیشه در فروشگاه‌ها یکسان نیست و یک محصول ممکن است در هر دو دسته قرار بگیرد. به جای تکیه بر برچسب، موارد قابل مشاهده و اعلام‌شده را مقایسه کن: فرم و فیت، نوع بسته‌شدن، توضیح رویه و آستر، اطلاعات کفی، ساختار زیره، وزن اعلام‌شده و کاربردی که سازنده یا فروشنده نوشته است.</p>
<p>اگر ویژگی فنی در صفحه نیامده، از روی عبارت‌هایی مثل «راحت» یا «سبک» یک نتیجه پزشکی، ورزشی یا عملکردی نساز. این واژه‌ها بدون عدد، روش آزمون و مشخصات دقیق برای مقایسه کافی نیستند.</p>
<h2>سایز و قالب را قبل از رنگ بررسی کن</h2>
<p>کتانی‌ای که خوب روی پا نمی‌نشیند، با انتخاب رنگ بهتر جبران نمی‌شود. طول و عرض هر دو پا را ثبت کن و آن را با جدول همان مدل مقایسه کن. عدد سایز قبلی فقط مرجع کمکی است.</p>
<p>مراحل کامل اندازه‌گیری و خطاهای رایج در <a href="A10_URL">راهنمای انتخاب سایز کتانی مردانه</a> آمده است. اگر جدول محصول روشن نیست، پیش از خرید درباره قالب و نوع عدد اعلام‌شده سؤال کن.</p>
<h2>درباره رویه فقط به ظاهر عکس تکیه نکن</h2>
<p>رویه می‌تواند از بخش‌ها و مواد مختلف ساخته شده باشد، اما ترکیب دقیق را فقط وقتی بپذیر که در مشخصات همان محصول نوشته شده باشد. از روی بافت عکس نمی‌توان با اطمینان درصد الیاف، نوع چرم، مقاومت یا قابلیت تنفس را تعیین کرد.</p>
<p>در تصاویر نزدیک، یکنواختی اتصال قطعات، محل تاخوردن رویه، تقارن دو لنگه و تمیزی لبه‌ها را بررسی کن. این مشاهده‌ها برای طرح سؤال خوب‌اند، نه برای صدور تضمین دوام.</p>
<h2>آستر، زبانه و لبه دور مچ چه اطلاعاتی می‌دهند؟</h2>
<p>توضیح آستر و تصویر داخل کفش کمک می‌کند ساختار محصول را بهتر بفهمی. زبانه باید در تصاویر درست قرار گرفته باشد و لبه دور مچ در دو سمت نامتقارن دیده نشود. اگر ضخامت یا جنس این بخش‌ها اعلام نشده، آن را حدس نزن.</p>
<p>همچنین ببین بندها در چه محدوده‌ای امکان تنظیم دارند. بند می‌تواند فیت را تنظیم کند اما راه‌حل یک سایز کاملاً اشتباه نیست.</p>
<h2>کفی را با ادعاهای مبهم نسنج</h2>
<p>جداشدن کفی، جنس، ضخامت یا ویژگی خاص آن باید در مشخصات محصول ذکر شده باشد. از روی یک عکس عمومی نمی‌توان درباره پشتیبانی، جذب فشار یا مناسب‌بودن برای شرایط بدنی نتیجه قطعی گرفت.</p>
<p>اگر نیاز مشخص یا سابقه ناراحتی پا داری، مقاله فروشگاهی جای ارزیابی تخصصی را نمی‌گیرد. برای خرید عمومی، کافی است اطلاعات قابل اثبات محصول را مقایسه و هر ابهام را قبل از سفارش روشن کنی.</p>
<h2>زیره را از چند زاویه ببین</h2>
<p>نمای کناری به ارتفاع و فرم کلی کمک می‌کند و تصویر زیره می‌تواند الگو و بخش‌بندی آن را نشان دهد. اگر فروشنده جنس زیره یا ویژگی مشخصی را اعلام کرده، همان متن را ثبت کن؛ در غیر این صورت از ظاهر، نام ماده یا عملکرد دقیق نساز.</p>
<p>رد چسب بسیار زیاد، فاصله نامتقارن بین رویه و زیره یا تفاوت واضح دو لنگه در تصاویر نزدیک ارزش بررسی بیشتر دارد. با این حال، کیفیت بلندمدت فقط از عکس قابل تضمین نیست.</p>
<h2>انعطاف و وزن را چگونه ارزیابی کنیم؟</h2>
<p>اگر وزن یا توضیح انعطاف در صفحه محصول آمده، مطمئن شو مربوط به کدام سایز و کدام لنگه یا جفت است. مقایسه دو عدد بدون واحد و شرایط یکسان گمراه‌کننده است. اگر عددی وجود ندارد، «سبک» را یک توصیف فروشنده بدان، نه اندازه‌گیری مستقل.</p>
<p>برای استفاده روزمره، تجربه واقعی پس از تحویل اهمیت دارد. محصول را طبق شرایط تعویض، روی سطح تمیز امتحان کن و چند حرکت عادی انجام بده؛ بدون اینکه برای آزمون، کفش را در فضای بیرون استفاده کنی.</p>
<h2>رنگ کتانی را با لباس‌های واقعی کمدت انتخاب کن</h2>
<p>سفید، کرم، سرمه‌ای یا رنگ‌های دیگر زمانی کاربردی‌اند که با شلوارها و بالاتنه‌هایی که واقعاً می‌پوشی هماهنگ باشند. عکس محصول را در نمایشگرهای مختلف ببین، اما انتظار تطابق کامل رنگ بین صفحه و محصول نداشته باش؛ نور عکاسی و تنظیم نمایشگر اثر می‌گذارد.</p>
<p>اگر شلوارهای آزاد بخش اصلی استایلت هستند، <a href="A7_URL">راهنمای پوشیدن شلوار بگ مردانه</a> درباره حجم کتانی و شکست قد شلوار توضیح می‌دهد. برای ترکیب پیراهن لینن با کتانی هم <a href="A6_URL">راهنمای استایل پیراهن لینن</a> مسیر مرتبط‌تری است.</p>
<h2>دوخت، چسب و تقارن را در تصاویر بررسی کن</h2>
<p>تصاویر جلو، پشت، دو طرف و زیره را کنار هم بگذار. فاصله دوخت‌ها، محل اتصال قطعات، فرم پنجه و ارتفاع پشت دو لنگه باید تا حد ممکن هماهنگ باشد. یک عکس دور یا رندر تزئینی برای قضاوت جزئیات کافی نیست.</p>
<p>مشاهده تمیز بودن نمونه تصویری به معنی تضمین تمام موجودی نیست. اگر جزئیاتی برایت مهم است، درباره همان مدل و همان رنگ سؤال مشخص بپرس.</p>
<h2>قیمت را با اطلاعات قابل مقایسه بسنج</h2>
<p>قیمت بالاتر به‌تنهایی کیفیت بیشتر را ثابت نمی‌کند و قیمت پایین‌تر هم لزوماً خرید بهتر نیست. دو یا سه مدل را با معیارهای ثابت مقایسه کن: کاربرد، اندازه، اطلاعات مواد، تصاویر جزئیات، شرایط تعویض و شفافیت توضیحات.</p>
<p>تخفیف یا موجودی ممکن است تغییر کند؛ این مقاله نباید عدد قیمت یا وعده موجودی را ثابت نگه دارد. صفحه زنده محصول مرجع وضعیت خرید است.</p>
<h2>قبل از پرداخت چه سؤال‌هایی بپرسیم؟</h2>
<ul><li>جدول سایز مربوط به طول پا است یا طول کفی؟</li><li>قالب این مدل طبق اطلاعات فروشگاه چگونه توصیف شده است؟</li><li>ترکیب رویه، آستر و زیره دقیقاً کجا اعلام شده؟</li><li>آیا عکس‌های چند زاویه و تصویر داخل یا زیره وجود دارد؟</li><li>شرایط و مهلت تعویض سایز چیست؟</li><li>اگر ویژگی مهمی نوشته نشده، فروشگاه چه پاسخ قابل ثبت و مشخصی می‌دهد؟</li></ul>
<h2>پس از تحویل، کتانی را چطور بررسی کنیم؟</h2>
<p>بسته‌بندی را نگه دار و محصول را ابتدا روی سطح تمیز داخل خانه امتحان کن. دو لنگه را از نظر سایز، رنگ، دوخت و فرم مقایسه کن. با جوراب معمول خودت چند قدم راه برو و بندها را طبیعی ببند.</p>
<p>اگر با توضیحات یا سفارش اختلافی دیدی، قبل از استفاده بیرون از خانه طبق روش اعلام‌شده فروشگاه پیگیری کن. تمیز نگه داشتن زیره در این مرحله، امکان بررسی و تعویض را بهتر حفظ می‌کند.</p>
<h2>اشتباه‌های رایج هنگام خرید کتانی مردانه</h2>
<ul><li>انتخاب فقط با نام برند یا ظاهر عکس اول.</li><li>یکی دانستن عنوان روزمره، پیاده‌روی و ورزشی بدون خواندن مشخصات.</li><li>سفارش بر اساس سایز همیشگی بدون جدول همان مدل.</li><li>حدس جنس و عملکرد رویه یا زیره از روی تصویر.</li><li>نادیده گرفتن لباس‌ها و شلوارهای واقعی کمد.</li><li>امتحان کردن در فضای بیرون پیش از بررسی شرایط تعویض.</li><li>تبدیل عبارت‌های تبلیغاتی به ادعای فنی یا پزشکی.</li></ul>
<h2>چک‌لیست نهایی خرید کتانی</h2>
<ul><li>کاربرد اصلی را مشخص کرده‌ام.</li><li>سایز را با اندازه پا و جدول همان مدل سنجیده‌ام.</li><li>فقط اطلاعات اعلام‌شده درباره رویه، آستر، کفی و زیره را ثبت کرده‌ام.</li><li>تصاویر چند زاویه و جزئیات ساخت را دیده‌ام.</li><li>رنگ را با شلوارها و بالاتنه‌های خودم مقایسه کرده‌ام.</li><li>شرایط تعویض را قبل از پرداخت خوانده‌ام.</li></ul>
<p>یک خرید آگاهانه لزوماً به معنی پیدا کردن مدل «برتر» نیست؛ یعنی می‌توانی توضیح بدهی چرا این مدل برای کاربرد، اندازه و استایل تو انتخاب مناسب‌تری است و کدام بخش‌های تصمیم هنوز به امتحان واقعی وابسته‌اند.</p>
HTML;
$content11=strtr($content11,['SNEAKERS_URL'=>esc_url($su),'CASUAL_URL'=>esc_url($cu),'WALKING_URL'=>esc_url($wu),'A10_URL'=>esc_url($a10u),'A6_URL'=>esc_url($a6u),'A7_URL'=>esc_url($a7u)]);
$a11=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای خرید کتانی مردانه برای استفاده روزمره؛ سایز، رویه و زیره','post_name'=>$slug11,'post_excerpt'=>'برای خرید کتانی مردانه، کاربرد و سایز را کنار اطلاعات واقعی رویه، آستر، کفی، زیره، جزئیات ساخت و شرایط تعویض مقایسه کنید.','post_content'=>$content11,'post_category'=>[(int)$buy->term_id],'post_author'=>1]),true);
if(is_wp_error($a11)){wp_delete_post($a10,true);http_response_code(500);echo wp_json_encode(['error'=>'article 11 insert','message'=>$a11->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a11u=get_permalink($a11);
$updated10=str_replace(esc_url($future11),esc_url($a11u),get_post($a10)->post_content);$r10=wp_update_post(wp_slash(['ID'=>$a10,'post_content'=>$updated10]),true);
$meta=[$a10=>['rank_math_title'=>'انتخاب سایز کتانی مردانه برای خرید آنلاین','rank_math_description'=>'برای انتخاب سایز کتانی مردانه، طول و عرض هر دو پا را درست اندازه بگیرید و نتیجه را با جدول همان مدل مقایسه کنید تا خرید آنلاین دقیق‌تری داشته باشید.','rank_math_focus_keyword'=>'انتخاب سایز کتانی مردانه'],$a11=>['rank_math_title'=>'راهنمای خرید کتانی مردانه؛ سایز، رویه و زیره','rank_math_description'=>'راهنمای خرید کتانی مردانه برای استفاده روزمره؛ کاربرد، سایز، رویه، آستر، کفی، زیره و جزئیات ساخت را بدون تکیه بر ادعاهای مبهم مقایسه کنید.','rank_math_focus_keyword'=>'راهنمای خرید کتانی مردانه']];
foreach($meta as $id=>$values){foreach($values as $key=>$value)update_post_meta($id,$key,$value);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}
$bridge7='<div data-g1-cluster-wave="1011-sneakers"><h2>کتانی را با کاربرد و اندازه واقعی انتخاب کن</h2><p>بعد از مشخص کردن حجم کفش در استایل بگ، <a href="'.esc_url($a11u).'">راهنمای خرید کتانی مردانه</a> را ببین و برای مقایسه دقیق طول و عرض پا از <a href="'.esc_url($a10u).'">راهنمای انتخاب سایز کتانی مردانه</a> استفاده کن.</p></div>';
$bridge1='<div data-g1-commerce-bridge="tshirt"><h2>مدل‌های تیشرت را با فیت موردنظرت مقایسه کن</h2><p>بعد از تشخیص تفاوت باکسی و اورسایز، مدل‌های زنده را در <a href="'.esc_url($tu).'">دسته تیشرت مردانه</a> با اندازه‌های واقعی هر محصول مقایسه کن.</p></div>';
$r7=wp_update_post(wp_slash(['ID'=>$posts[468]->ID,'post_content'=>$posts[468]->post_content."\n".$bridge7]),true);$r1=wp_update_post(wp_slash(['ID'=>$posts[453]->ID,'post_content'=>$posts[453]->post_content."\n".$bridge1]),true);
if(is_wp_error($r10)||is_wp_error($r7)||is_wp_error($r1)){
 wp_delete_post($a11,true);wp_delete_post($a10,true);
 foreach([[468,'data-g1-cluster-wave="1011-sneakers"'],[453,'data-g1-commerce-bridge="tshirt"']] as $item){$p=get_post($item[0]);if($p&&strpos($p->post_content,$item[1])!==false){$pattern=$item[0]===468?'/\s*<div data-g1-cluster-wave="1011-sneakers">.*?<\/div>\s*$/s':'/\s*<div data-g1-commerce-bridge="tshirt">.*?<\/div>\s*$/s';wp_update_post(wp_slash(['ID'=>$p->ID,'post_content'=>preg_replace($pattern,'',$p->post_content,1)]));}}
 http_response_code(500);echo wp_json_encode(['error'=>'content bridge update']);exit;
}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
$live=[];foreach(array_keys($expected) as $id){$p=get_post($id);$live[$id]=['title'=>$p->post_title,'url'=>get_permalink($p)];}
echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'counts'=>['fit'=>(int)get_term($fit->term_id)->count,'fabric'=>(int)get_term($fabric->term_id)->count,'style'=>(int)get_term($style->term_id)->count,'buy'=>(int)get_term($buy->term_id)->count],'categories'=>['fit'=>get_term_link($fit),'fabric'=>get_term_link($fabric),'style'=>get_term_link($style),'buy'=>get_term_link($buy)],'existing'=>$live,'a10'=>['id'=>(int)$a10,'url'=>$a10u,'focus'=>get_post_meta($a10,'rank_math_focus_keyword',true)],'a11'=>['id'=>(int)$a11,'url'=>$a11u,'focus'=>get_post_meta($a11,'rank_math_focus_keyword',true)],'blog'=>get_permalink(22)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''


def rollback(reason):
    print("ROLLBACK_REASON", reason)
    rollback_name = "gramiss-editorial-wave-10-11-rollback-" + nonce + ".php"
    rollback_php = r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
foreach([sanitize_title('انتخاب سایز کتانی مردانه'),sanitize_title('راهنمای خرید کتانی مردانه روزمره')] as $slug){$post=get_page_by_path($slug,OBJECT,'post');if($post)wp_delete_post($post->ID,true);}
foreach([[468,'/\s*<div data-g1-cluster-wave="1011-sneakers">.*?<\/div>\s*$/s'],[453,'/\s*<div data-g1-commerce-bridge="tshirt">.*?<\/div>\s*$/s']] as $item){$post=get_post($item[0]);if($post&&preg_match($item[1],$post->post_content))wp_update_post(wp_slash(['ID'=>$post->ID,'post_content'=>preg_replace($item[1],'',$post->post_content,1)]));}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');echo wp_json_encode(['rolled_back'=>true,'published'=>(int)wp_count_posts('post')->publish,'counts'=>['fit'=>(int)$fit->count,'fabric'=>(int)$fabric->count,'style'=>(int)$style->count,'buy'=>(int)$buy->count]],JSON_UNESCAPED_UNICODE);
?>'''
    save_public(rollback_name, rollback_php)
    status, raw, _, _ = get(
        BASE + "/" + rollback_name + "?t=" + str(int(time.time())), 240
    )
    text = raw.decode("utf-8", "replace")
    print("ROLLBACK", status, text)
    if status != 200:
        raise SystemExit("ROLLBACK REQUEST FAILED after " + reason)
    data = json.loads(text)
    if data.get("published") != 9 or data.get("counts") != {
        "fit": 3,
        "fabric": 2,
        "style": 2,
        "buy": 2,
    }:
        raise SystemExit("ROLLBACK BASELINE FAILED after " + reason)
    product_status, product_urls = sitemap("product-sitemap.xml")
    protected_now = {
        path: hashlib.sha256(read_theme(path).encode()).hexdigest()
        for path in protected
    }
    if (
        product_status != 200
        or sorted(product_urls) != product_urls_pre
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
if state.get("published") != 11:
    errors.append("published post count")
if state.get("counts") != {"fit": 4, "fabric": 2, "style": 2, "buy": 3}:
    errors.append("editorial category counts")
if state.get("a10", {}).get("focus") != FOCUS_10:
    errors.append("Article 10 focus keyword")
if state.get("a11", {}).get("focus") != FOCUS_11:
    errors.append("Article 11 focus keyword")

a10_url = state["a10"]["url"]
a11_url = state["a11"]["url"]
existing_urls = {
    int(post_id): value["url"] for post_id, value in state["existing"].items()
}
all_pages = dict(existing_urls)
all_pages[state["a10"]["id"]] = a10_url
all_pages[state["a11"]["id"]] = a11_url
expected_live_titles = dict(EXPECTED_TITLES)
expected_live_titles[state["a10"]["id"]] = TITLE_10
expected_live_titles[state["a11"]["id"]] = TITLE_11

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
    if status != 200 or expected_live_titles[post_id] not in body:
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
    if h2_count < (10 if post_id in (state["a10"]["id"], state["a11"]["id"]) else 8):
        errors.append("article structure " + str(post_id))
    if post_id in (state["a10"]["id"], state["a11"]["id"]):
        new_bodies[post_id] = (body, metadata)

body10, metadata10 = new_bodies[state["a10"]["id"]]
body11, metadata11 = new_bodies[state["a11"]["id"]]
if metadata10.get("title") != META_TITLE_10 or metadata10.get("description") != META_DESCRIPTION_10:
    errors.append("Article 10 metadata")
if metadata11.get("title") != META_TITLE_11 or metadata11.get("description") != META_DESCRIPTION_11:
    errors.append("Article 11 metadata")
for required in (
    a11_url,
    existing_urls[468],
    commerce["sneakers"],
    commerce["casual"],
    commerce["walking"],
):
    if required not in body10:
        errors.append("Article 10 missing link " + required)
for required in (
    a10_url,
    existing_urls[467],
    existing_urls[468],
    commerce["sneakers"],
    commerce["casual"],
    commerce["walking"],
):
    if required not in body11:
        errors.append("Article 11 missing link " + required)

for label, post_id, marker, targets in (
    (
        "A7",
        468,
        'data-g1-cluster-wave="1011-sneakers"',
        [a10_url, a11_url],
    ),
    (
        "A1",
        453,
        'data-g1-commerce-bridge="tshirt"',
        [commerce["tshirt"]],
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
    "fit": (4, [TITLE_10]),
    "fabric": (2, [EXPECTED_TITLES[463], EXPECTED_TITLES[464]]),
    "style": (2, [EXPECTED_TITLES[467], EXPECTED_TITLES[468]]),
    "buy": (3, [TITLE_11, EXPECTED_TITLES[471], EXPECTED_TITLES[472]]),
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
if not all(title in blog_pages_body for title in expected_live_titles.values()):
    blog_page_2 = state["blog"].rstrip("/") + "/page/2/"
    blog_2_status, blog_2_raw, blog_2_final, _ = get(
        blog_page_2 + "?t=" + str(int(time.time())), 180
    )
    blog_2_body = blog_2_raw.decode("utf-8", "replace")
    print("BLOG_PAGE_2", blog_2_status, blog_2_final)
    if blog_2_status == 200:
        blog_pages_body += "\n" + blog_2_body
if (
    blog_status != 200
    or norm(blog_metadata.get("canonical", "")) != norm(state["blog"])
    or "noindex" in blog_metadata.get("robots", "").lower()
    or TITLE_10 not in blog_body
    or TITLE_11 not in blog_body
    or not all(title in blog_pages_body for title in expected_live_titles.values())
):
    errors.append("blog archive")

post_status, post_urls = sitemap("post-sitemap.xml")
post_normalized = {norm(url) for url in post_urls}
print("POST_SITEMAP", post_status, len(post_urls))
if (
    post_status != 200
    or len(post_urls) != 12
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

protected_post = {
    path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in protected
}
print("PROTECTED_POST", json.dumps(protected_post, ensure_ascii=False, sort_keys=True))
if protected_post != protected_pre:
    errors.append("protected UI changed")

if errors:
    print("VERIFY_ERRORS", json.dumps(errors, ensure_ascii=False))
    rollback("; ".join(errors))

print("PASS EDITORIAL WAVE 10-11")
print("ARTICLE_10", a10_url)
print("ARTICLE_11", a11_url)
print("PRODUCT_SITEMAP_SHA_PRESERVED", product_sha_post)
print("HOME_SHA_PRESERVED", protected_post["front-page.php"])
