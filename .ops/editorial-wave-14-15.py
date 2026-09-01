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

EXPECTED_IDS = [453, 459, 460, 463, 464, 467, 468, 471, 472, 482, 483, 487, 488]
TITLE_14 = "شلوار کارگو مردانه چیست و چه تفاوتی با شلوار بگ دارد؟"
TITLE_15 = "راهنمای انتخاب سایز کلاه فیت کپ؛ اندازه‌گیری دور سر بدون حدس"
FOCUS_14 = "شلوار کارگو مردانه چیست"
FOCUS_15 = "انتخاب سایز کلاه فیت کپ"
META_TITLE_14 = "شلوار کارگو مردانه چیست؟ تفاوت کارگو و بگ"
META_TITLE_15 = "انتخاب سایز کلاه فیت کپ؛ اندازه‌گیری دور سر"
META_DESCRIPTION_14 = "شلوار کارگو مردانه را از روی ساختار، جیب‌ها و فیت بشناسید و تفاوت آن با شلوار بگ و راسته را برای انتخاب دقیق‌تر در خرید آنلاین بررسی کنید."
META_DESCRIPTION_15 = "برای انتخاب سایز کلاه فیت کپ، دور سر را درست اندازه بگیرید و عدد را با جدول همان مدل مقایسه کنید؛ بدون تکیه بر جدول‌های تبدیل عمومی."


def call(function, params, post=False):
    url = f"https://{host}:2083/execute/Fileman/{function}"
    data = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 5):
        try:
            req = urllib.request.Request(url if post else url + "?" + data.decode(), data=data if post else None, method="POST" if post else "GET")
            req.add_header("Authorization", f"cpanel {user}:{token}")
            if post:
                req.add_header("Content-Type", "application/x-www-form-urlencoded")
            with urllib.request.urlopen(req, context=ctx, timeout=90) as response:
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
    data = call("get_file_content", {"dir": root if not path else root + "/" + path, "file": name, "from_charset": "_DETECT_", "to_charset": "utf-8"})
    if isinstance(data, dict):
        for key in ("content", "file_content", "data"):
            if isinstance(data.get(key), str):
                return data[key]
    return data if isinstance(data, str) else ""


def save_public(name, content):
    return call("save_file_content", {"dir": "public_html", "file": name, "content": content, "from_charset": "UTF-8", "to_charset": "UTF-8", "fallback": "0"}, True)


def get(url, timeout=180):
    last = None
    for attempt in range(1, 5):
        req = urllib.request.Request(url, headers={"User-Agent": "GramissEditorialWave1415/1.0", "Cache-Control": "no-cache", "Pragma": "no-cache"})
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
                return response.status, response.read(), response.geturl(), dict(response.headers)
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), exc.geturl(), dict(exc.headers)
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
        "description": html_value(text, r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']*)"),
        "canonical": html_value(text, r"<link[^>]+rel=[\"']canonical[\"'][^>]+href=[\"']([^\"']+)"),
        "robots": html_value(text, r"<meta[^>]+name=[\"']robots[\"'][^>]+content=[\"']([^\"']+)"),
    }


def norm(url):
    return urllib.parse.unquote(url).split("?", 1)[0].rstrip("/") + "/"


def sitemap(path):
    status, raw, _, _ = get(BASE + "/" + path + "?t=" + str(int(time.time())), 120)
    return status, [value.replace("&amp;", "&") for value in re.findall(r"<loc>(.*?)</loc>", raw.decode("utf-8", "replace"), re.I)]


protected = ["front-page.php", "template-parts/home-looks.php", "assets/css/home-looks.css", "assets/js/home-looks.js"]
protected_pre = {path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in protected}
print("PROTECTED_PRE", json.dumps(protected_pre, ensure_ascii=False, sort_keys=True))
if healthy and protected_pre["front-page.php"] != healthy:
    raise SystemExit("ABORT Home mismatch")

product_status_pre, product_urls_pre = sitemap("product-sitemap.xml")
product_urls_pre = sorted(product_urls_pre)
product_sha_pre = hashlib.sha256("\n".join(product_urls_pre).encode()).hexdigest()
product_cat_status_pre, product_cat_urls_pre = sitemap("product_cat-sitemap.xml")
product_cat_urls_pre = sorted(product_cat_urls_pre)
product_cat_sha_pre = hashlib.sha256("\n".join(product_cat_urls_pre).encode()).hexdigest()
print("PRODUCT_SITEMAP_PRE", product_status_pre, len(product_urls_pre), product_sha_pre)
print("PRODUCT_CAT_SITEMAP_PRE", product_cat_status_pre, len(product_cat_urls_pre), product_cat_sha_pre)
if product_status_pre != 200 or len(product_urls_pre) != 47 or product_sha_pre != "70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3":
    raise SystemExit("ABORT Product Sitemap drift")
if product_cat_status_pre != 200:
    raise SystemExit("ABORT Product Category Sitemap unavailable")

commerce = {
    "pants": BASE + "/product-category/pants/",
    "cargo": BASE + "/product-category/pants/cargo-pants/",
    "hat": BASE + "/product-category/hat/",
    "fitted": BASE + "/product-category/hat/fitted-cap/",
}
for label, url in commerce.items():
    status, raw, final, _ = get(url + "?t=" + str(int(time.time())), 120)
    metadata = head(raw)
    print("COMMERCE_PRE", label, status, final, json.dumps(metadata, ensure_ascii=False))
    robots = metadata.get("robots", "").lower()
    if status != 200 or "noindex" in robots or "index" not in robots or norm(metadata.get("canonical", "")) != norm(url):
        raise SystemExit("ABORT commerce archive " + label)
if not {norm(url) for url in commerce.values()}.issubset({norm(url) for url in product_cat_urls_pre}):
    raise SystemExit("ABORT commerce archive missing from Product Category Sitemap")

nonce = hashlib.sha256((str(time.time()) + protected_pre["front-page.php"]).encode()).hexdigest()[:14]
probe_name = "gramiss-editorial-wave-14-15-" + nonce + ".php"

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
483=>'راهنمای خرید کتانی مردانه برای استفاده روزمره؛ سایز، رویه و زیره',
487=>'راهنمای انتخاب سایز پیراهن مردانه؛ سرشانه، سینه، قد و آستین',
488=>'تمیز کردن کتانی سفید بدون آسیب؛ راهنمای رویه، بند و خشک‌کردن'];
$posts=[];$baseline_errors=[];
foreach($expected as $id=>$title){$p=get_post($id);$posts[$id]=$p;if(!$p||$p->post_status!=='publish'||$p->post_title!==$title)$baseline_errors[]='post '.$id;}
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');
$pants=get_term_by('slug','pants','product_cat');$cargo=get_term_by('slug','cargo-pants','product_cat');$hat=get_term_by('slug','hat','product_cat');$fitted=get_term_by('slug','fitted-cap','product_cat');
$slug14=sanitize_title('شلوار کارگو مردانه چیست');$slug15=sanitize_title('انتخاب سایز کلاه فیت کپ');
$old14=get_page_by_path($slug14,OBJECT,'post');$old15=get_page_by_path($slug15,OBJECT,'post');$published=(int)wp_count_posts('post')->publish;
if(!$fit||!$fabric||!$style||!$buy||!$pants||!$cargo||!$hat||!$fitted)$baseline_errors[]='missing taxonomy';
if($published!==13)$baseline_errors[]='published='.$published;
if((int)$fit->count!==5||(int)$fabric->count!==3||(int)$style->count!==2||(int)$buy->count!==3)$baseline_errors[]='editorial counts';
if($old14||$old15)$baseline_errors[]='target slug exists';
if(strpos($posts[460]->post_content,'data-g1-wave="1415-cargo-from-03"')!==false)$baseline_errors[]='marker 03 exists';
if(strpos($posts[472]->post_content,'data-g1-wave="1415-cargo-from-09"')!==false)$baseline_errors[]='marker 09 exists';
if($baseline_errors){http_response_code(409);echo wp_json_encode(['error'=>'baseline drift','details'=>$baseline_errors,'published'=>$published],JSON_UNESCAPED_UNICODE);exit;}
$pu=get_term_link($pants);$cu=get_term_link($cargo);$hu=get_term_link($hat);$fu=get_term_link($fitted);foreach([$pu,$cu,$hu,$fu] as $url){if(is_wp_error($url)){http_response_code(409);echo wp_json_encode(['error'=>'commerce URL']);exit;}}
$a3u=get_permalink($posts[460]);$a9u=get_permalink($posts[472]);$a12u=get_permalink($posts[487]);
$originals=[460=>$posts[460]->post_content,472=>$posts[472]->post_content];$original_hashes=[];foreach($originals as $id=>$content)$original_hashes[$id]=hash('sha256',$content);

$content14=<<<'HTML'
<p>شلوار کارگو مردانه را معمولاً با جیب‌های کناری می‌شناسیم، اما «کارگو» و «بگ» دو مفهوم یکسان نیستند. کارگو بیشتر به ساختار و جزئیات کاربردی شلوار اشاره می‌کند؛ بگ درباره حجم و فیت لباس است. به همین دلیل یک کارگو می‌تواند راسته، آزاد یا بگ باشد و صرفاً گشاد بودن شلوار آن را کارگو نمی‌کند.</p>
<p>اگر برای خرید آنلاین بین کارگو، بگ و مدل‌های راسته مردد هستی، بهتر است سه چیز را جدا بررسی کنی: ساختار جیب‌ها، فیت واقعی و اندازه‌های خود شلوار. این راهنما همین مرزها را روشن می‌کند و برای مشخصات هر مدل، صفحه همان محصول را مرجع نهایی می‌داند.</p>
<h2>شلوار کارگو چیست؟</h2>
<p>در تعریف کاربردی پوشاک، کارگو به شلواری گفته می‌شود که طراحی آن از جیب‌های کاربردی و معمولاً جیب‌های جانبی روی ران یا بخش‌های پایین‌تر پا استفاده می‌کند. تعداد دقیق جیب‌ها یک قانون جهانی نیست؛ بنابراین «شش جیب» می‌تواند یک نام رایج بازار باشد، نه معیاری که هر کارگو الزاماً باید دقیقاً رعایت کند.</p>
<p>در خرید آنلاین بهتر است به جای تکیه بر اسم محصول، تصاویر جلو، بغل و پشت را ببینی و جای جیب‌ها، نوع بسته‌شدن و فرم پاچه را با توضیحات همان مدل تطبیق بدهی.</p>
<h2>آیا هر شلوار شش جیب، کارگو است؟</h2>
<p>در بازار ایران «شش جیب» اغلب برای اشاره به کارگو استفاده می‌شود، اما تعداد جیب به‌تنهایی درباره فیت، جنس یا کاربرد محصول اطلاعات کافی نمی‌دهد. ممکن است دو شلوار هر دو جیب جانبی داشته باشند ولی یکی راسته و دیگری بسیار آزاد باشد. پس اسم «شش جیب» را نقطه شروع بدان، نه نتیجه نهایی.</p>
<h2>تفاوت شلوار کارگو و بگ چیست؟</h2>
<p>بگ یک خانواده فیت است: حجم بیشتری در ران و ساق ایجاد می‌کند و عرض پاچه بخش مهمی از ظاهر آن است. در مقابل، کارگو با جزئیات ساختاری شناخته می‌شود. برای مرور تفاوت بگ، نیم‌بگ و فول‌بگ، <a href="__A3__">راهنمای تفاوت فیت‌های بگ</a> مرجع جداگانه Gramiss است.</p>
<p>بنابراین «کارگو بگ» تناقض نیست؛ یعنی شلواری با جزئیات کارگو که فیت آن هم در خانواده بگ قرار می‌گیرد.</p>
<h2>کارگو بگ یعنی چه؟</h2>
<p>وقتی فروشنده از عبارت کارگو بگ استفاده می‌کند، باید انتظار داشته باشی دو ویژگی مستقل را در صفحه محصول ببینی: جیب‌ها و جزئیات کارگو، و اندازه‌هایی که حجم آزادتر شلوار را نشان می‌دهند. اگر اندازه‌های ران، دمپا، فاق یا قد منتشر شده‌اند، آن‌ها از خود عبارت «بگ» دقیق‌ترند.</p>
<h2>کارگو با شلوار راسته چه تفاوتی دارد؟</h2>
<p>راسته بودن به خط کلی پاچه مربوط است؛ یعنی عرض ساق در طول شلوار تغییر شدید ندارد. کارگو می‌تواند روی همین فیت راسته ساخته شود. پس مقایسه «کارگو یا راسته» همیشه دو گزینه متضاد نیست؛ ممکن است یک محصول هم‌زمان کارگو و راسته باشد.</p>
<h2>جیب‌ها چه اطلاعاتی درباره ساختار شلوار می‌دهند؟</h2>
<p>جای جیب‌های جانبی، حجم آن‌ها، فلپ، دکمه یا زیپ می‌تواند ظاهر شلوار را تغییر دهد. جیب بزرگ روی ران حجم بصری بیشتری ایجاد می‌کند و جیب تخت‌تر ظاهر آرام‌تری دارد. از روی عکس نباید ظرفیت، استحکام یا کاربرد تخصصی جیب را حدس زد؛ فقط چیزی را معیار قرار بده که در تصویر یا مشخصات واقعی محصول دیده می‌شود.</p>
<h2>فیت واقعی کارگو را از چه اندازه‌هایی بخوانیم؟</h2>
<p>برای مقایسه دو مدل، دور یا عرض کمر، فاق، ران، دمپا و قد شلوار مهم‌تر از نام فیت هستند. اگر یک شلوار مرجع داری که روی بدن خوب می‌ایستد، همان را روی سطح صاف اندازه بگیر و عددها را با جدول همان مدل مقایسه کن.</p>
<p>اگر هنوز بین بگ و فیت‌های آزاد تفاوت را دقیق نمی‌دانی، ابتدا مقاله فیت‌های بگ را بخوان و بعد سراغ جزئیات کارگو برو؛ این کار جلوی خرید سایز بزرگ‌تر فقط برای «بگ دیده شدن» را می‌گیرد.</p>
<h2>قد و دمپا در ظاهر کارگو چه نقشی دارند؟</h2>
<p>قد شلوار و عرض دمپا تعیین می‌کنند پایین لباس روی کتانی یا کفش چطور می‌نشیند. مدل‌های جمع‌شونده، کش‌دار یا دمپای آزاد رفتار متفاوتی دارند. بدون اندازه و تصویر واقعی نباید فرض کرد یک کارگو حتماً روی کفش شکست زیاد ایجاد می‌کند.</p>
<h2>پارچه کارگو را از روی عکس حدس نزن</h2>
<p>کارگو می‌تواند با پارچه‌های مختلف ساخته شود و ظاهر مات یا ضخیم در عکس، ترکیب الیاف را ثابت نمی‌کند. اگر جنس یا درصد الیاف روی صفحه محصول نوشته نشده، آن را به عنوان واقعیت ذکر نکن. افت پارچه، ایستایی و حس سطح را هم فقط در حد چیزی که تصویر و توضیح فروشنده نشان می‌دهد ارزیابی کن.</p>
<h2>برای خرید آنلاین شلوار کارگو چه چیزهایی را بررسی کنیم؟</h2>
<ul><li>نام فیت را با اندازه‌های واقعی تطبیق بده.</li><li>جیب‌های جانبی و نوع بسته‌شدن آن‌ها را در چند زاویه ببین.</li><li>فاق، ران، دمپا و قد را با یک شلوار مرجع مقایسه کن.</li><li>جنس را فقط از مشخصات اعلام‌شده بخوان.</li><li>رنگ را در چند تصویر و نور مختلف بررسی کن.</li><li>اگر مدل کارگو جزئیات خاصی مثل بند یا کش دارد، نحوه استفاده آن را از صفحه همان محصول چک کن.</li></ul>
<h2>اشتباه‌های رایج هنگام انتخاب کارگو</h2>
<p>یکی از خطاهای رایج این است که هر شلوار آزاد را کارگو یا هر کارگو را بگ بدانیم. خطای دیگر، بزرگ‌تر خریدن کمر برای ساختن فیت آزاد است؛ در حالی که فیت باید از الگوی خود شلوار بیاید. همچنین بهتر است از روی تعداد جیب‌ها، دوام یا کاربری حرفه‌ای نتیجه‌گیری نکنی.</p>
<h2>اگر بین کارگو و بگ مردد هستی، از کدام شروع کنی؟</h2>
<p>اول مشخص کن مسئله تو «ظاهر و حجم شلوار» است یا «جزئیات کارگو». اگر حجم مهم‌تر است، فیت را با <a href="__A3__">راهنمای بگ، نیم‌بگ و فول‌بگ</a> مشخص کن. اگر به جیب‌ها و فرم کارگو علاقه داری، مدل‌های واقعی <a href="__CARGO__">شلوار کارگو مردانه</a> را ببین و اندازه‌هایشان را مقایسه کن.</p>
<h2>خرید جین و کارگو یک چک‌لیست ندارند</h2>
<p>بخشی از اندازه‌گیری‌ها مشترک است، اما جین و کارگو جزئیات متفاوتی دارند. <a href="__A9__">راهنمای خرید شلوار جین مردانه</a> درباره رفتار دنیم، شست‌وشوی جین و جزئیات مخصوص آن است؛ این مقاله مالک موضوع ساختار کارگو و تفاوت آن با فیت بگ می‌ماند.</p>
<h2>جمع‌بندی</h2>
<p>کارگو را با ساختار و جیب‌هایش بشناس و بگ را با فیت و حجمش. هنگام خرید، اسم محصول را با اندازه واقعی، تصاویر چندزاویه و مشخصات همان مدل تطبیق بده. برای دیدن خانواده کامل‌تر شلوارها می‌توانی <a href="__PANTS__">دسته شلوار مردانه</a> را هم مقایسه کنی.</p>
HTML;
$content14=str_replace(['__A3__','__A9__','__CARGO__','__PANTS__'],[esc_url($a3u),esc_url($a9u),esc_url($cu),esc_url($pu)],$content14);

$content15=<<<'HTML'
<p>در کلاه فیت کپ، انتخاب سایز فقط یک جزئیات جانبی نیست. چون مدل‌های پشت‌بسته معمولاً مثل اسنپ‌بک بند تنظیم ندارند، باید دور سر را درست اندازه بگیری و عدد را با جدول همان مدل مقایسه کنی. مهم‌ترین نکته این است که هیچ جدول تبدیل عمومی را جای اطلاعات واقعی محصول ننشانی.</p>
<p>این راهنما به جای اعلام یک جدول ثابت سانتی‌متر به سایز، روش اندازه‌گیری قابل تکرار را توضیح می‌دهد. اگر یک مدل Gramiss اندازه یا جدول مشخصی منتشر کرده باشد، همان اطلاعات برای آن محصول مرجع نهایی است.</p>
<h2>فیت کپ چیست و چرا سایزش حساس‌تر است؟</h2>
<p>فیت کپ یا کلاه کپ پشت‌بسته در حالت معمول سازوکار تنظیم بازِ پشت کلاه را ندارد و با سایز مشخص عرضه می‌شود. همین تفاوت باعث می‌شود عدد دور سر و قالب همان مدل اهمیت بیشتری پیدا کند. نام «فیت کپ» به‌تنهایی درباره عمق تاج، جنس یا فرم لبه اطلاعات کامل نمی‌دهد.</p>
<h2>تفاوت فیت کپ و اسنپ‌بک در انتخاب سایز چیست؟</h2>
<p>اسنپ‌بک معمولاً یک بخش تنظیم در پشت دارد، در حالی که فیت کپ پشت‌بسته است. این تفاوت روی دامنه تنظیم اثر می‌گذارد، اما به این معنی نیست که همه اسنپ‌بک‌ها یا همه فیت‌کپ‌ها یک قالب یکسان دارند. مشخصات همان مدل را مرجع قرار بده.</p>
<h2>برای اندازه‌گیری دور سر چه چیزی لازم است؟</h2>
<p>یک متر پارچه‌ای انعطاف‌پذیر بهترین ابزار است. اگر متر پارچه‌ای نداری، یک نخ یا نوار بدون کشش و یک خط‌کش صاف کافی است. از کش یا بندی که طولش هنگام کشیدن تغییر می‌کند استفاده نکن، چون عدد قابل اعتماد نمی‌دهد.</p>
<h2>دور سر را از کجا اندازه بگیریم؟</h2>
<p>متر را در مسیری قرار بده که انتظار داری نوار داخلی کلاه روی سر بنشیند؛ معمولاً کمی بالاتر از ابرو و بالای گوش‌ها و در امتداد برجسته‌ترین بخش پشت سر. مهم‌تر از یک عدد «استاندارد» این است که متر در تمام مسیر هم‌سطح بماند و پیچ نخورد.</p>
<h2>متر چقدر باید سفت باشد؟</h2>
<p>متر باید با سر تماس داشته باشد اما پوست را فشار ندهد. خیلی شل گرفتن متر عدد را بزرگ‌تر و خیلی سفت گرفتن آن عدد را کوچک‌تر می‌کند. هدف ثبت محیط طبیعی سر در محل نشستن کلاه است، نه شبیه‌سازی فشار کلاه.</p>
<h2>اندازه را فقط یک بار نگیر</h2>
<p>اندازه‌گیری را حداقل دو بار از ابتدا تکرار کن. اگر دو عدد تفاوت دارند، مسیر متر را دوباره بررسی کن و یک اندازه سوم بگیر. ثبات اندازه‌گیری از حفظ کردن یک جدول عمومی مهم‌تر است.</p>
<h2>اگر متر پارچه‌ای نداریم چه کنیم؟</h2>
<p>نخ بدون کشش را دور سر قرار بده، محل رسیدن دو سر نخ را علامت بزن و سپس آن را بدون کشیدن روی خط‌کش یا متر صاف اندازه بگیر. علامت‌گذاری دقیق کمک می‌کند خطای کوچک به تصمیم سایز تبدیل نشود.</p>
<h2>عدد دور سر را چطور با سایز کلاه مقایسه کنیم؟</h2>
<p>بعد از ثبت اندازه، جدول یا راهنمای سایز همان محصول را باز کن. اگر فروشنده اندازه‌ها را بر حسب سانتی‌متر، اینچ یا شماره فیت منتشر کرده، همان تبدیل رسمی مدل را دنبال کن. Gramiss نباید یک جدول عمومی را به همه برندها و قالب‌ها تعمیم دهد.</p>
<h2>چرا جدول تبدیل عمومی می‌تواند گمراه‌کننده باشد؟</h2>
<p>دو کلاه با برچسب یکسان می‌توانند در عمق تاج، نوار داخلی، پارچه و قالب تفاوت داشته باشند. حتی اگر جدول عمومی نزدیک باشد، تضمین نمی‌کند محصول خاص همان تناسب را داشته باشد. جدول همان مدل و سیاست تعویض فروشگاه اطلاعات مهم‌تری هستند.</p>
<h2>اگر بین دو سایز قرار گرفتیم چه کنیم؟</h2>
<p>بدون اطلاعات مدل نمی‌توان نسخه همیشگی «بزرگ‌تر بخر» یا «کوچک‌تر بخر» داد. اول ببین برند یا فروشنده برای بین دو سایز بودن چه توصیه‌ای دارد و آیا اندازه واقعی یا توضیح قالب منتشر شده است. اگر چنین اطلاعاتی نیست، قبل از خرید سؤال کردن کم‌ریسک‌تر از حدس زدن است.</p>
<h2>عمق تاج و فرم کلاه را با دور سر اشتباه نگیر</h2>
<p>دور سر فقط یکی از ابعاد فیت است. ممکن است محیط کلاه مناسب باشد اما عمق تاج یا فرم پنل‌ها با نحوه پوشیدن تو هماهنگ نباشد. تصاویر روی سر، نمای بغل و توضیح مدل می‌توانند در کنار عدد دور سر کمک کنند، اما جای اندازه واقعی را نمی‌گیرند.</p>
<h2>مو و نحوه پوشیدن کلاه چه اثری دارد؟</h2>
<p>اگر حجم مو یا شیوه پوشیدن تو باعث می‌شود کلاه در جای متفاوتی بنشیند، اندازه را در همان شرایطی بگیر که معمولاً کلاه را استفاده می‌کنی. قرار نیست عددی برای همه حالت‌ها ثابت فرض شود؛ هدف شبیه‌کردن شرایط واقعی استفاده است.</p>
<h2>بعد از تحویل کلاه چه چیزهایی را بررسی کنیم؟</h2>
<p>کلاه نباید نقطه فشار آزاردهنده ایجاد کند یا با حرکت معمول سر به‌راحتی جابه‌جا شود. هم‌زمان تاج و نوار داخلی را بررسی کن. اگر محصول طبق راهنمای همان مدل مناسب نیست، به جای کشیدن، خیس‌کردن یا تغییر دادن ساختار کلاه، ابتدا شرایط تعویض فروشگاه را بررسی کن.</p>
<h2>اشتباه‌های رایج در انتخاب سایز فیت کپ</h2>
<ul><li>استفاده از سایز یک برند برای برند یا مدل دیگر بدون مقایسه جدول.</li><li>اندازه‌گیری با متر مورب یا پیچ‌خورده.</li><li>فشار دادن متر برای رسیدن به عدد کوچک‌تر.</li><li>اعتماد کامل به برچسب S/M یا شماره سایز بدون دور سر.</li><li>فرض اینکه فیت کپ مثل اسنپ‌بک بعداً دامنه تنظیم زیادی دارد.</li><li>تغییر دادن کلاه قبل از بررسی امکان تعویض.</li></ul>
<h2>یک اصل مشترک در خرید آنلاین: اندازه واقعی، سپس جدول همان مدل</h2>
<p>این منطق فقط برای کلاه نیست. در <a href="__A12__">راهنمای انتخاب سایز پیراهن مردانه</a> هم ابتدا اندازه واقعی ثبت می‌شود و بعد با اطلاعات همان مدل مقایسه می‌شود. تفاوت در این است که برای فیت کپ، اندازه کلیدی دور سر است و جدول اختصاصی کلاه باید مرجع نهایی باشد.</p>
<h2>چک‌لیست نهایی قبل از خرید فیت کپ</h2>
<ul><li>دور سر را در محل واقعی نشستن کلاه اندازه بگیر.</li><li>اندازه را حداقل دو بار تکرار کن.</li><li>واحد اندازه‌گیری جدول محصول را بررسی کن.</li><li>قالب و عمق تاج را از توضیحات و تصاویر همان مدل ببین.</li><li>اگر بین دو سایز هستی، توصیه همان برند یا فروشنده را پیدا کن.</li><li>شرایط تعویض را قبل از ایجاد هر تغییری در کلاه بخوان.</li></ul>
<h2>مدل‌های فیت کپ را با اطلاعات واقعی خودشان مقایسه کن</h2>
<p>برای مشاهده مدل‌های پشت‌بسته، <a href="__FITTED__">دسته کلاه فیت کپ</a> را ببین. اگر می‌خواهی مدل‌های دیگر کلاه را هم مقایسه کنی، <a href="__HAT__">دسته کلاه مردانه</a> مسیر کامل‌تری است. تصمیم سایز را فقط بر اساس اطلاعاتی بگیر که برای همان محصول منتشر شده است.</p>
HTML;
$content15=str_replace(['__A12__','__FITTED__','__HAT__'],[esc_url($a12u),esc_url($fu),esc_url($hu)],$content15);

$a14=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'شلوار کارگو مردانه چیست و چه تفاوتی با شلوار بگ دارد؟','post_name'=>$slug14,'post_content'=>$content14,'post_category'=>[(int)$fit->term_id]]),true);
if(is_wp_error($a14)){http_response_code(500);echo wp_json_encode(['error'=>'create a14','detail'=>$a14->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a15=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای انتخاب سایز کلاه فیت کپ؛ اندازه‌گیری دور سر بدون حدس','post_name'=>$slug15,'post_content'=>$content15,'post_category'=>[(int)$fit->term_id]]),true);
if(is_wp_error($a15)){wp_delete_post($a14,true);http_response_code(500);echo wp_json_encode(['error'=>'create a15','detail'=>$a15->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a14u=get_permalink($a14);$a15u=get_permalink($a15);
$meta=[
$a14=>['rank_math_title'=>'شلوار کارگو مردانه چیست؟ تفاوت کارگو و بگ','rank_math_description'=>'شلوار کارگو مردانه را از روی ساختار، جیب‌ها و فیت بشناسید و تفاوت آن با شلوار بگ و راسته را برای انتخاب دقیق‌تر در خرید آنلاین بررسی کنید.','rank_math_focus_keyword'=>'شلوار کارگو مردانه چیست'],
$a15=>['rank_math_title'=>'انتخاب سایز کلاه فیت کپ؛ اندازه‌گیری دور سر','rank_math_description'=>'برای انتخاب سایز کلاه فیت کپ، دور سر را درست اندازه بگیرید و عدد را با جدول همان مدل مقایسه کنید؛ بدون تکیه بر جدول‌های تبدیل عمومی.','rank_math_focus_keyword'=>'انتخاب سایز کلاه فیت کپ']];
foreach($meta as $id=>$values){foreach($values as $key=>$value)update_post_meta($id,$key,$value);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}
$bridge3='<div data-g1-wave="1415-cargo-from-03"><h2>کارگو را با فیت بگ یکی ندان</h2><p>کارگو نام ساختار و جزئیات شلوار است و بگ نام یک خانواده فیت؛ اگر بین این دو اصطلاح مردد هستی، <a href="'.esc_url($a14u).'">راهنمای شلوار کارگو مردانه و تفاوت آن با بگ</a> این مرز را جدا توضیح می‌دهد.</p></div>';
$bridge9='<div data-g1-wave="1415-cargo-from-09"><h2>برای کارگو، جیب و ساختار را جدا از جین بررسی کن</h2><p>معیارهای کمر، فاق و قد قابل مقایسه‌اند، اما جزئیات کارگو متفاوت است؛ <a href="'.esc_url($a14u).'">راهنمای شلوار کارگو مردانه</a> جیب‌ها، فیت و تفاوت کارگو با بگ را پوشش می‌دهد.</p></div>';
$r3=wp_update_post(wp_slash(['ID'=>460,'post_content'=>$posts[460]->post_content."\n".$bridge3]),true);
$r9=wp_update_post(wp_slash(['ID'=>472,'post_content'=>$posts[472]->post_content."\n".$bridge9]),true);
if(is_wp_error($r3)||is_wp_error($r9)){wp_delete_post($a15,true);wp_delete_post($a14,true);foreach($originals as $id=>$content)wp_update_post(wp_slash(['ID'=>$id,'post_content'=>$content]));http_response_code(500);echo wp_json_encode(['error'=>'content bridge update']);exit;}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'counts'=>['fit'=>(int)get_term($fit->term_id)->count,'fabric'=>(int)get_term($fabric->term_id)->count,'style'=>(int)get_term($style->term_id)->count,'buy'=>(int)get_term($buy->term_id)->count],'a14'=>['id'=>(int)$a14,'url'=>$a14u,'focus'=>get_post_meta($a14,'rank_math_focus_keyword',true)],'a15'=>['id'=>(int)$a15,'url'=>$a15u,'focus'=>get_post_meta($a15,'rank_math_focus_keyword',true)],'blog'=>get_permalink(22),'originals'=>array_map('base64_encode',$originals),'original_hashes'=>$original_hashes],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''

save_public(probe_name, php)
status, raw, final, _ = get(BASE + "/" + probe_name + "?t=" + str(int(time.time())), 300)
print("PUBLISH_PROBE", status, final, raw.decode("utf-8", "replace"))
if status != 200:
    raise SystemExit("PUBLISH FAILED")
result = json.loads(raw.decode("utf-8", "replace"))
if not result.get("ok"):
    raise SystemExit("PUBLISH RESPONSE NOT OK")
a14, a15 = result["a14"], result["a15"]
a14_id, a15_id = int(a14["id"]), int(a15["id"])
a14_url, a15_url = a14["url"], a15["url"]
snapshot_payload = base64.b64encode(json.dumps(result.get("originals", {})).encode()).decode()
errors = []
if int(result.get("published", 0)) != 15:
    errors.append("published count")
if result.get("counts") != {"fit": 7, "fabric": 3, "style": 2, "buy": 3}:
    errors.append("category counts")


def verify_article(pid, url, title, meta_title, meta_desc, required_urls):
    status, raw, final, _ = get(url + "?t=" + str(int(time.time())), 180)
    text = raw.decode("utf-8", "replace")
    metadata = head(raw)
    internal = {norm(x) for x in re.findall(r'href=["\']([^"\']+)', text, re.I) if "gramiss.ir" in x}
    print("ARTICLE_VERIFY", pid, status, final, json.dumps(metadata, ensure_ascii=False), "H2", text.count("<h2>"))
    if status != 200: errors.append(f"{pid} http")
    if title not in text: errors.append(f"{pid} h1/title")
    if metadata.get("title") != meta_title: errors.append(f"{pid} meta title")
    if metadata.get("description") != meta_desc: errors.append(f"{pid} meta desc")
    if norm(metadata.get("canonical", "")) != norm(url): errors.append(f"{pid} canonical")
    robots = metadata.get("robots", "").lower()
    if "noindex" in robots or "index" not in robots: errors.append(f"{pid} robots")
    if not re.search(r'"@type"\s*:\s*"BlogPosting"', text, re.I): errors.append(f"{pid} BlogPosting")
    if re.search(r'"@type"\s*:\s*"Product"', text, re.I): errors.append(f"{pid} Product schema")
    if text.count("<h2>") < 10: errors.append(f"{pid} thin headings")
    for required in required_urls:
        if norm(required) not in internal: errors.append(f"{pid} missing link {required}")

verify_article(a14_id, a14_url, TITLE_14, META_TITLE_14, META_DESCRIPTION_14, [BASE + "/product-category/pants/", BASE + "/product-category/pants/cargo-pants/", BASE + "/تفاوت-شلوار-بگ-نیم-بگ-فول-بگ/", BASE + "/راهنمای-خرید-شلوار-جین-مردانه/"])
verify_article(a15_id, a15_url, TITLE_15, META_TITLE_15, META_DESCRIPTION_15, [BASE + "/product-category/hat/", BASE + "/product-category/hat/fitted-cap/", BASE + "/انتخاب-سایز-پیراهن-مردانه/"])

for pid, marker, url in [(460, 'data-g1-wave="1415-cargo-from-03"', BASE + "/تفاوت-شلوار-بگ-نیم-بگ-فول-بگ/"), (472, 'data-g1-wave="1415-cargo-from-09"', BASE + "/راهنمای-خرید-شلوار-جین-مردانه/")]:
    status, raw, _, _ = get(url + "?t=" + str(int(time.time())), 150)
    text = raw.decode("utf-8", "replace")
    links = {norm(x) for x in re.findall(r'href=["\']([^"\']+)', text, re.I) if "gramiss.ir" in x}
    if status != 200 or marker not in text or norm(a14_url) not in links: errors.append(f"bridge {pid}")

post_status, post_urls = sitemap("post-sitemap.xml")
category_status, category_urls = sitemap("category-sitemap.xml")
product_status_post, product_urls_post = sitemap("product-sitemap.xml")
product_cat_status_post, product_cat_urls_post = sitemap("product_cat-sitemap.xml")
product_urls_post, product_cat_urls_post = sorted(product_urls_post), sorted(product_cat_urls_post)
product_sha_post = hashlib.sha256("\n".join(product_urls_post).encode()).hexdigest()
product_cat_sha_post = hashlib.sha256("\n".join(product_cat_urls_post).encode()).hexdigest()
print("POST_SITEMAP_POST", post_status, len(post_urls))
print("CATEGORY_SITEMAP_POST", category_status, len(category_urls))
print("PRODUCT_SITEMAP_POST", product_status_post, len(product_urls_post), product_sha_post)
print("PRODUCT_CAT_SITEMAP_POST", product_cat_status_post, len(product_cat_urls_post), product_cat_sha_post)
if post_status != 200 or len(post_urls) != 16 or norm(a14_url) not in {norm(x) for x in post_urls} or norm(a15_url) not in {norm(x) for x in post_urls}: errors.append("post sitemap")
if category_status != 200 or len(category_urls) != 4: errors.append("category sitemap")
if product_status_post != 200 or product_urls_post != product_urls_pre or product_sha_post != product_sha_pre: errors.append("product sitemap drift")
if product_cat_status_post != 200 or product_cat_urls_post != product_cat_urls_pre or product_cat_sha_post != product_cat_sha_pre: errors.append("product cat sitemap drift")
protected_post = {path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in protected}
print("PROTECTED_POST", json.dumps(protected_post, ensure_ascii=False, sort_keys=True))
if protected_post != protected_pre: errors.append("protected UI drift")
blog_found = set()
for page_number in (1, 2, 3):
    url = BASE + "/وبلاگ/" if page_number == 1 else BASE + f"/وبلاگ/page/{page_number}/"
    status, raw, final, _ = get(url + "?t=" + str(int(time.time())), 150)
    text = raw.decode("utf-8", "replace")
    if status != 200:
        if page_number <= 2: errors.append(f"blog page {page_number}")
        break
    if TITLE_14 in text: blog_found.add(14)
    if TITLE_15 in text: blog_found.add(15)
    print("BLOG_VERIFY", page_number, status, final, "A14", TITLE_14 in text, "A15", TITLE_15 in text)
if blog_found != {14, 15}: errors.append("blog cards")

if errors:
    print("VERIFY_ERRORS", json.dumps(errors, ensure_ascii=False))
    rollback_name = "gramiss-editorial-wave-14-15-rollback-" + nonce + ".php"
    rollback_php = r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
foreach([sanitize_title('شلوار کارگو مردانه چیست'),sanitize_title('انتخاب سایز کلاه فیت کپ')] as $slug){$post=get_page_by_path($slug,OBJECT,'post');if($post)wp_delete_post($post->ID,true);}
$snap=json_decode(base64_decode('SNAPSHOT_PAYLOAD'),true);if(is_array($snap)&&$snap){foreach($snap as $id=>$encoded){$content=base64_decode($encoded,true);if($content!==false)wp_update_post(wp_slash(['ID'=>(int)$id,'post_content'=>$content]));}}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');echo wp_json_encode(['rolled_back'=>true,'published'=>(int)wp_count_posts('post')->publish,'counts'=>['fit'=>(int)$fit->count,'fabric'=>(int)$fabric->count,'style'=>(int)$style->count,'buy'=>(int)$buy->count]],JSON_UNESCAPED_UNICODE);?>'''.replace("SNAPSHOT_PAYLOAD", snapshot_payload)
    save_public(rollback_name, rollback_php)
    rb_status, rb_raw, _, _ = get(BASE + "/" + rollback_name + "?t=" + str(int(time.time())), 240)
    print("ROLLBACK", rb_status, rb_raw.decode("utf-8", "replace"))
    raise SystemExit("WAVE 14-15 VERIFY FAILED AND ROLLED BACK")

print("PASS EDITORIAL WAVE 14-15", json.dumps({"a14": a14, "a15": a15, "published": result.get("published"), "counts": result.get("counts"), "post_sitemap": len(post_urls), "category_sitemap": len(category_urls), "product_sitemap": len(product_urls_post), "product_sha": product_sha_post, "product_cat_sitemap": len(product_cat_urls_post), "product_cat_sha": product_cat_sha_post, "protected": protected_post}, ensure_ascii=False, sort_keys=True))
