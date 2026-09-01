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

HOST=os.environ["CPANEL_HOST"];USER=os.environ["CPANEL_USER"];TOKEN=os.environ["CPANEL_TOKEN"]
THEME_ROOT=os.environ["THEME_ROOT"].strip("/");HEALTHY=os.environ.get("HEALTHY_HOME_SHA","")
CTX=ssl._create_unverified_context();BASE="https://gramiss.ir"
EXPECTED_PRODUCT_SHA="70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3"
EXPECTED_PRODUCT_CAT_SHA="75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4"
BASE_IDS=[453,459,460,463,464,467,468,471,472,482,483,487,488,492,493]
TITLE16="شست‌وشوی تیشرت چاپی؛ محافظت از چاپ در شستن، خشک‌کردن و اتوکشی"
TITLE17="راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت، افت پارچه، فاق و قد"
META16="شست‌وشوی تیشرت چاپی؛ محافظت از چاپ و پارچه"
DESC16="برای شست‌وشوی تیشرت چاپی، اول لیبل و نوع چاپ را بررسی کنید؛ سپس شستن، خشک‌کردن و اتوکشی را طوری مدیریت کنید که تماس و حرارت اضافه به چاپ وارد نشود."
META17="راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت و افت پارچه"
DESC17="برای خرید شلوار پارچه‌ای مردانه، فیت، فاق، ران، دمپا، قد و افت واقعی پارچه را بررسی کنید و اندازه‌ها را با یک شلوار مرجع مقایسه کنید."


def safe_url(url):
    p=urllib.parse.urlsplit(url);path=urllib.parse.quote(urllib.parse.unquote(p.path),safe="/%:@");query=urllib.parse.quote(urllib.parse.unquote(p.query),safe="=&%:@,+")
    return urllib.parse.urlunsplit((p.scheme,p.netloc,path,query,p.fragment))

def call(fn,params,post=False):
    url=f"https://{HOST}:2083/execute/Fileman/{fn}";enc=urllib.parse.urlencode(params).encode();last=None
    for n in range(1,5):
        try:
            req=urllib.request.Request(url if post else url+"?"+enc.decode(),data=enc if post else None,method="POST" if post else "GET");req.add_header("Authorization",f"cpanel {USER}:{TOKEN}")
            if post:req.add_header("Content-Type","application/x-www-form-urlencoded")
            with urllib.request.urlopen(req,context=CTX,timeout=90) as r:out=json.loads(r.read().decode("utf-8","replace"))
            result=out.get("result") if isinstance(out.get("result"),dict) else out
            if not isinstance(result,dict) or result.get("status")!=1:raise RuntimeError(str(result))
            return result.get("data")
        except Exception as exc:
            last=exc;print("API_RETRY",fn,n,exc)
            if n<4:time.sleep(n*2)
    raise last

def read_theme(rel):
    d,n=rel.rsplit("/",1) if "/" in rel else ("",rel);data=call("get_file_content",{"dir":THEME_ROOT if not d else THEME_ROOT+"/"+d,"file":n,"from_charset":"_DETECT_","to_charset":"utf-8"})
    if isinstance(data,dict):
        for k in ("content","file_content","data"):
            if isinstance(data.get(k),str):return data[k]
    return data if isinstance(data,str) else ""

def save_public(name,content):return call("save_file_content",{"dir":"public_html","file":name,"content":content,"from_charset":"UTF-8","to_charset":"UTF-8","fallback":"0"},True)

def get(url,timeout=180):
    url=safe_url(url);last=None
    for n in range(1,5):
        req=urllib.request.Request(url,headers={"User-Agent":"GramissWave1617/1.0","Cache-Control":"no-cache","Pragma":"no-cache"})
        try:
            with urllib.request.urlopen(req,context=CTX,timeout=timeout) as r:return r.status,r.read(),r.geturl(),dict(r.headers)
        except urllib.error.HTTPError as exc:return exc.code,exc.read(),exc.geturl(),dict(exc.headers)
        except Exception as exc:
            last=exc;print("HTTP_RETRY",n,url,exc)
            if n<4:time.sleep(n*2)
    raise last

def hval(text,pattern):
    m=re.search(pattern,text,re.I|re.S);return re.sub(r"\s+"," ",m.group(1)).strip() if m else ""

def head(raw):
    t=raw.decode("utf-8","replace").split("</head>",1)[0];return {"title":hval(t,r"<title[^>]*>(.*?)</title>"),"description":hval(t,r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']*)"),"canonical":hval(t,r"<link[^>]+rel=[\"']canonical[\"'][^>]+href=[\"']([^\"']+)"),"robots":hval(t,r"<meta[^>]+name=[\"']robots[\"'][^>]+content=[\"']([^\"']+)")}

def norm(url):return urllib.parse.unquote(url).split("?",1)[0].rstrip("/")+"/"
def sitemap(path):
    st,raw,_,_=get(BASE+"/"+path+"?t="+str(int(time.time())),120);return st,[x.replace("&amp;","&") for x in re.findall(r"<loc>(.*?)</loc>",raw.decode("utf-8","replace"),re.I)]

protected=["front-page.php","template-parts/home-looks.php","assets/css/home-looks.css","assets/js/home-looks.js"]
pre_hash={p:hashlib.sha256(read_theme(p).encode()).hexdigest() for p in protected};print("PROTECTED_PRE",json.dumps(pre_hash,sort_keys=True))
if HEALTHY and pre_hash["front-page.php"]!=HEALTHY:raise SystemExit("ABORT home drift")
pst,pu=sitemap("product-sitemap.xml");pu=sorted(pu);psha=hashlib.sha256("\n".join(pu).encode()).hexdigest();pcst,pcu=sitemap("product_cat-sitemap.xml");pcu=sorted(pcu);pcsha=hashlib.sha256("\n".join(pcu).encode()).hexdigest()
print("PRODUCT_PRE",pst,len(pu),psha);print("PRODUCT_CAT_PRE",pcst,len(pcu),pcsha)
if pst!=200 or len(pu)!=47 or psha!=EXPECTED_PRODUCT_SHA:raise SystemExit("ABORT product sitemap")
if pcst!=200 or len(pcu)!=20 or pcsha!=EXPECTED_PRODUCT_CAT_SHA:raise SystemExit("ABORT product cat sitemap")
commerce={"tshirt":BASE+"/product-category/tshirt/","graphic":BASE+"/product-category/tshirt/graphic-tshirt/","pants":BASE+"/product-category/pants/","fabric":BASE+"/product-category/pants/fabric-pants/"}
for name,url in commerce.items():
    st,raw,final,_=get(url+"?t="+str(int(time.time())),120);m=head(raw);print("COMMERCE",name,st,final,json.dumps(m,ensure_ascii=False))
    if st!=200 or "noindex" in m["robots"].lower() or norm(m["canonical"])!=norm(url):raise SystemExit("ABORT commerce "+name)
if not {norm(x) for x in commerce.values()}.issubset({norm(x) for x in pcu}):raise SystemExit("ABORT commerce sitemap")
nonce=hashlib.sha256((str(time.time())+pre_hash["front-page.php"]).encode()).hexdigest()[:14];probe="gramiss-wave-16-17-"+nonce+".php"
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$ids=[453,459,460,463,464,467,468,471,472,482,483,487,488,492,493];$posts=[];$err=[];foreach($ids as $id){$p=get_post($id);$posts[$id]=$p;if(!$p||$p->post_status!=='publish')$err[]='post '.$id;}
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');$graphic=get_term_by('slug','graphic-tshirt','product_cat');$tshirt=get_term_by('slug','tshirt','product_cat');$fp=get_term_by('slug','fabric-pants','product_cat');$pants=get_term_by('slug','pants','product_cat');
if((int)wp_count_posts('post')->publish!==15)$err[]='published';if(!$fit||!$fabric||!$style||!$buy||!$graphic||!$tshirt||!$fp||!$pants)$err[]='taxonomy';if((int)$fit->count!==7||(int)$fabric->count!==3||(int)$style->count!==2||(int)$buy->count!==3)$err[]='counts';
$slug16=sanitize_title('شستشوی تیشرت چاپی');$slug17=sanitize_title('راهنمای خرید شلوار پارچه ای مردانه');if(get_page_by_path($slug16,OBJECT,'post')||get_page_by_path($slug17,OBJECT,'post'))$err[]='slug exists';
$markers=[453=>'data-g1-wave="1617-tee-care-from-01"',471=>'data-g1-wave="1617-tee-care-from-08"',460=>'data-g1-wave="1617-fabric-pants-from-03"',468=>'data-g1-wave="1617-fabric-pants-from-07"'];foreach($markers as $id=>$m){if(strpos($posts[$id]->post_content,$m)!==false)$err[]='marker '.$id;}
if($err){http_response_code(409);echo wp_json_encode(['error'=>'baseline','details'=>$err],JSON_UNESCAPED_UNICODE);exit;}
$gu=get_term_link($graphic);$tu=get_term_link($tshirt);$fpu=get_term_link($fp);$pu=get_term_link($pants);foreach([$gu,$tu,$fpu,$pu] as $u){if(is_wp_error($u)){http_response_code(409);echo wp_json_encode(['error'=>'term url']);exit;}}
$u1=get_permalink($posts[453]);$u3=get_permalink($posts[460]);$u7=get_permalink($posts[468]);$u8=get_permalink($posts[471]);$u9=get_permalink($posts[472]);$originals=[];foreach([453,471,460,468] as $id)$originals[$id]=$posts[$id]->post_content;
$c16=<<<'HTML'
<p>برای تیشرت چاپی یک نسخه شست‌وشوی ثابت وجود ندارد؛ چون جنس پارچه، روش چاپ و دستور مراقبت هر محصول می‌تواند متفاوت باشد. نقطه شروع امن، لیبل خود لباس و اطلاعاتی است که فروشنده یا تولیدکننده برای همان مدل منتشر کرده است.</p>
<p>هدف این راهنما حفظ هم‌زمان پارچه و چاپ است، نه معرفی یک «ترفند جادویی». وقتی نوع چاپ دقیق را نمی‌دانی، باید تماس مکانیکی، مواد قوی و حرارت اضافه را محافظه‌کارانه مدیریت کنی.</p>
<h2>اول لیبل تیشرت و دستور همان محصول را بخوان</h2><p>دمای آب، امکان ماشین‌شویی، خشک‌کن و اتوکشی را از لیبل شروع کن. اگر دستور محصول با یک توصیه عمومی اینترنتی فرق دارد، دستور همان لباس اولویت دارد. روش چاپ را هم فقط وقتی قطعی بدان که در مشخصات محصول اعلام شده باشد.</p>
<h2>چرا نوع چاپ مهم است؟</h2><p>چاپ‌های مختلف رفتار یکسانی در برابر حرارت، اصطکاک و مواد شوینده ندارند. ظاهر چاپ در عکس برای تشخیص قطعی تکنیک چاپ کافی نیست. بنابراین بدون اطلاعات سازنده، از ادعای «این چاپ حتماً DTF، سیلک یا سابلیمیشن است» پرهیز کن.</p>
<h2>قبل از شست‌وشو چاپ را بررسی کن</h2><p>ترک، بلندشدگی لبه، لکه یا آسیب قبلی را ببین. اگر چاپ از قبل آسیب دیده، شست‌وشوی تهاجمی می‌تواند وضعیت را بدتر کند. لکه را هم قبل از استفاده از هر ماده قوی، با دستور مراقبت همان لباس تطبیق بده.</p>
<h2>پشت‌ورو کردن چه زمانی مفید است؟</h2><p>پشت‌ورو کردن می‌تواند تماس مستقیم سطح چاپ با لباس‌های دیگر و دیواره ماشین را کمتر کند، اما جایگزین دستور لیبل نیست. اگر محصول محدودیت خاصی دارد، همان محدودیت را رعایت کن.</p>
<h2>لباس‌های خشن و یراق‌دار را جدا کن</h2><p>زیپ فلزی، قلاب، سطح زبر یا لباس سنگین می‌تواند اصطکاک بیشتری ایجاد کند. وقتی امکانش هست، تیشرت چاپی را با لباس‌های سبک‌تر و رنگ‌های سازگار بشوی تا هم چاپ و هم رنگ پارچه کمتر در معرض تماس سخت قرار بگیرد.</p>
<h2>دمای آب را حدس نزن</h2><p>یک عدد دمای ثابت برای همه تیشرت‌های چاپی درست نیست. پایین‌ترین دمایی را انتخاب کن که با لیبل، میزان آلودگی و شوینده سازگار است. اگر لیبل اجازه نمی‌دهد، توصیه عمومی اینترنتی نباید جای آن را بگیرد.</p>
<h2>شوینده و لکه‌بر را محافظه‌کارانه انتخاب کن</h2><p>سفیدکننده، لکه‌بر یا شوینده قوی می‌تواند روی بعضی رنگ‌ها یا چاپ‌ها اثر بگذارد. اگر سازگاری محصول مشخص نیست، ماده را مستقیم روی سطح چاپ نریز و قبل از استفاده، دستور لباس و شوینده را بخوان.</p>
<h2>ماشین لباس‌شویی یا شست‌وشوی دستی؟</h2><p>هیچ‌کدام به‌صورت جهانی «بهترین» نیست. اگر لیبل ماشین‌شویی را مجاز می‌داند، برنامه ملایم‌تر و بار سبک‌تر معمولاً تماس مکانیکی را کمتر می‌کند. در شست‌وشوی دستی هم چنگ‌زدن، پیچاندن یا ساییدن مستقیم چاپ می‌تواند مشکل‌ساز باشد.</p>
<h2>چاپ را نساب و نپیچان</h2><p>برای خارج کردن آب، پیچاندن شدید تیشرت یا ساییدن طرح روی خودش را به عادت تبدیل نکن. فشار کنترل‌شده و روش خشک‌کردن مطابق لیبل، ریسک تغییر شکل پارچه و چاپ را کمتر می‌کند.</p>
<h2>خشک‌کردن تیشرت چاپی را چطور مدیریت کنیم؟</h2><p>اول ببین خشک‌کن ماشینی برای همان لباس مجاز است یا نه. اگر درباره تحمل حرارت چاپ مطمئن نیستی، از گرمای شدید و تماس مستقیم با منبع حرارتی دوری کن. هنگام آویزان‌کردن یا پهن‌کردن هم فرم لباس را حفظ کن.</p>
<h2>آفتاب مستقیم همیشه پاسخ نیست</h2><p>نور و گرما می‌تواند روی بعضی رنگ‌ها اثر بگذارد. به جای یک قانون همیشگی، دستور محصول و شرایط پارچه را معیار قرار بده. هدف خشک‌شدن با تهویه مناسب و بدون حرارت تأییدنشده است.</p>
<h2>اتو را مستقیم روی چاپ نگذار</h2><p>اگر لیبل اجازه اتو می‌دهد، تنظیم حرارت را با جنس پارچه هماهنگ کن و از تماس مستقیم صفحه داغ با چاپی که تحملش مشخص نیست خودداری کن. بعضی محصولات ممکن است روش یا محدودیت اختصاصی داشته باشند.</p>
<h2>اگر نوع چاپ را می‌دانیم چه تغییری می‌کند؟</h2><p>وقتی فروشنده روش چاپ و دستور نگهداری آن را مشخص کرده، می‌توانی توصیه دقیق‌تر همان محصول را دنبال کنی. اما این اطلاعات را به تمام تیشرت‌های چاپی تعمیم نده؛ حتی دو محصول ظاهراً مشابه ممکن است ساخت متفاوت داشته باشند.</p>
<h2>اشتباه‌های رایج در شست‌وشوی تیشرت چاپی</h2><ul><li>انتخاب دما از روی یک عدد عمومی بدون دیدن لیبل.</li><li>ریختن مستقیم لکه‌بر یا سفیدکننده روی طرح.</li><li>شستن کنار لباس‌های زبر و یراق‌دار بدون توجه به اصطکاک.</li><li>پیچاندن و ساییدن شدید چاپ.</li><li>استفاده از حرارت مستقیم برای خشک‌کردن یا اتوکشی بدون اجازه محصول.</li><li>فرض کردن روش چاپ فقط از روی ظاهر.</li></ul>
<h2>قبل از خرید، اطلاعات نگهداری را هم بررسی کن</h2><p>اگر هنوز محصول را نخریده‌ای، علاوه بر فیت و پارچه، ببین فروشنده درباره چاپ و مراقبت چه اطلاعاتی داده است. <a href="__A8__">راهنمای خرید تیشرت مردانه</a> معیارهای فیت، دوخت و چاپ را جداگانه توضیح می‌دهد.</p>
<h2>چک‌لیست کوتاه مراقبت</h2><ul><li>لیبل را بخوان.</li><li>نوع چاپ را حدس نزن.</li><li>اصطکاک و فشار را کم کن.</li><li>دما و شوینده را با همان محصول هماهنگ کن.</li><li>خشک‌کن و اتو را فقط در محدوده مجاز استفاده کن.</li><li>برای مدل‌های چاپی موجود، مشخصات <a href="__GRAPHIC__">تیشرت گرافیکی</a> و <a href="__TSHIRT__">دسته تیشرت مردانه</a> را جدا بررسی کن.</li></ul>
HTML;
$c16=str_replace(['__A8__','__GRAPHIC__','__TSHIRT__'],[esc_url($u8),esc_url($gu),esc_url($tu)],$c16);
$c17=<<<'HTML'
<p>«شلوار پارچه‌ای مردانه» فقط شلوار رسمی و اسلیم نیست. در فروشگاه‌های امروزی مدل‌های راسته، نیم‌بگ، بگ و پارچه‌های نرم و ریزش‌دار هم در همین خانواده دیده می‌شوند. برای خرید آنلاین، مهم‌تر از اسم مدل این است که فیت، اندازه و رفتار پارچه را جدا بررسی کنی.</p>
<p>این راهنما معیارهای خرید شلوار پارچه‌ای را برای استایل روزمره و کژوال توضیح می‌دهد و با مقاله جین هم‌پوشانی نمی‌سازد؛ چون دنیم رفتار و جزئیات مخصوص خودش را دارد.</p>
<h2>اول مشخص کن چه فیتی می‌خواهی</h2><p>راسته، نیم‌بگ و بگ فقط برچسب نیستند. حجم ران، فاق، عرض دمپا و قد تعیین می‌کنند شلوار روی بدن چه سیلوئتی بسازد. برای تفاوت فیت‌های آزاد، <a href="__A3__">راهنمای بگ، نیم‌بگ و فول‌بگ</a> را جدا ببین.</p>
<h2>سایز کمر را برای بگ دیده‌شدن بزرگ‌تر نخر</h2><p>اگر مدل واقعاً بگ طراحی شده باشد، آزادی باید در الگوی شلوار دیده شود. بزرگ‌کردن سایز کمر ممکن است فقط جای کمر و فاق را خراب کند. عددهای همان مدل را با شلواری که خوب روی تنت می‌نشیند مقایسه کن.</p>
<h2>از یک شلوار مرجع اندازه بگیر</h2><p>شلوار مرجع را صاف بگذار و کمر، فاق، ران، دمپا و قد را به روشی ثابت اندازه بگیر. سپس فقط با جدول همان مدل مقایسه کن؛ دو برند یا دو الگو می‌توانند با برچسب سایز یکسان، اندازه متفاوت داشته باشند.</p>
<h2>فاق چرا در شلوار پارچه‌ای مهم است؟</h2><p>فاق روی محل نشستن کمر و نسبت حجم بالاتنه شلوار اثر دارد. فاق بلند یا کوتاه به‌خودی‌خود بهتر نیست؛ باید با طراحی مدل و فیتی که می‌خواهی هماهنگ باشد.</p>
<h2>عرض ران را نادیده نگیر</h2><p>در مدل‌های آزاد، ران یکی از اندازه‌های تعیین‌کننده است. اگر فقط کمر و دمپا را ببینی ممکن است حجم واقعی بخش بالایی شلوار را اشتباه تخمین بزنی.</p>
<h2>دمپا ظاهر شلوار را چطور تغییر می‌دهد؟</h2><p>عرض دمپا روی ارتباط شلوار با کفش و میزان حجم پایین استایل اثر می‌گذارد. دمپای باز، راسته یا جمع‌تر هرکدام ظاهر متفاوتی می‌سازند؛ عدد واقعی از عبارت‌های مبهم مثل «آزاد» دقیق‌تر است.</p>
<h2>قد شلوار را با کفشی که واقعاً می‌پوشی بسنج</h2><p>قد مناسب به نوع کفش، عرض دمپا و میزان شکست دلخواه روی کفش بستگی دارد. یک عدد قد برای همه استایل‌ها جواب نمی‌دهد. شلوار مرجع را همراه کفش اصلی خودت ارزیابی کن.</p>
<h2>افت پارچه یعنی چه؟</h2><p>افت یا ریزش به نحوه آویزان‌شدن و حرکت پارچه اشاره دارد. پارچه نرم‌تر ممکن است حجم را روان‌تر نشان دهد و پارچه ساختارمندتر خط واضح‌تری بسازد. اما جنس الیاف، وزن یا کیفیت را فقط از روی عکس حدس نزن.</p>
<h2>پارچه نرم همیشه بهتر نیست</h2><p>انتخاب بین پارچه رها و ساختارمند به مدل و استایل موردنظر بستگی دارد. برای یک شلوار آزاد ممکن است ریزش نرم جذاب باشد، اما مدل دیگری عمداً ساختار بیشتری داشته باشد. مشخصات واقعی محصول را معیار قرار بده.</p>
<h2>ترکیب الیاف را فقط از مشخصات بخوان</h2><p>ظاهر مات، براق، ضخیم یا سبک در تصویر ترکیب الیاف را ثابت نمی‌کند. اگر درصد الیاف یا نام پارچه اعلام نشده، آن را حدس نزن و ادعای کشسانی، چروک‌پذیری یا دوام قطعی نساز.</p>
<h2>کمر کشی، بند یا زیپ چه فرقی در خرید ایجاد می‌کند؟</h2><p>نوع بسته‌شدن روی دامنه تنظیم و حس استفاده اثر دارد. اما مقدار کشسانی یا میزان تنظیم را فقط وقتی قطعی بدان که در مشخصات مدل آمده باشد. تصویر به‌تنهایی اندازه واقعی این دامنه را نشان نمی‌دهد.</p>
<h2>جیب و دوخت را از چند زاویه ببین</h2><p>نمای جلو برای ارزیابی کامل کافی نیست. محل جیب‌ها، خطوط دوخت، پشت شلوار و دمپا را هم ببین. هدف پیدا کردن اطلاعات قابل مشاهده است، نه نتیجه‌گیری درباره کیفیتی که از عکس قابل اثبات نیست.</p>
<h2>شلوار پارچه‌ای را با چه بالاتنه‌ای تصور کنیم؟</h2><p>حجم بالاتنه به درک درست فیت کمک می‌کند. <a href="__A7__">راهنمای استایل با شلوار بگ</a> توضیح می‌دهد که بالاتنه فیت یا باکسی هر دو می‌توانند کار کنند؛ تعادل نهایی به حجم کل استایل بستگی دارد.</p>
<h2>شلوار پارچه‌ای و جین یک معیار خرید ندارند</h2><p>اندازه‌های پایه مشترک‌اند، اما جین موضوعاتی مثل رفتار دنیم، شست‌وشوی جین و جزئیات مخصوص خودش دارد. برای آن دسته، <a href="__A9__">راهنمای خرید شلوار جین مردانه</a> مالک موضوع باقی می‌ماند.</p>
<h2>اشتباه‌های رایج هنگام خرید شلوار پارچه‌ای</h2><ul><li>فرض اینکه همه مدل‌های پارچه‌ای رسمی یا اسلیم‌اند.</li><li>بزرگ‌تر خریدن کمر برای ساختن فیت بگ.</li><li>نادیده گرفتن فاق و ران.</li><li>انتخاب قد بدون درنظرگرفتن کفش.</li><li>حدس جنس، کشسانی یا ضخامت فقط از عکس.</li><li>مقایسه سایز اسمی به جای اندازه واقعی.</li></ul>
<h2>چک‌لیست نهایی خرید</h2><ul><li>فیت موردنظر را مشخص کن.</li><li>کمر، فاق، ران، دمپا و قد را با شلوار مرجع مقایسه کن.</li><li>افت پارچه را از تصاویر چندزاویه و توضیح محصول ارزیابی کن.</li><li>الیاف را فقط از مشخصات اعلام‌شده بخوان.</li><li>نوع کمر، جیب و دمپا را بررسی کن.</li><li>مدل‌های موجود <a href="__FABRIC__">شلوار پارچه‌ای مردانه</a> و <a href="__PANTS__">دسته شلوار مردانه</a> را با همین معیارها مقایسه کن.</li></ul>
HTML;
$c17=str_replace(['__A3__','__A7__','__A9__','__FABRIC__','__PANTS__'],[esc_url($u3),esc_url($u7),esc_url($u9),esc_url($fpu),esc_url($pu)],$c17);
$a16=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'شست‌وشوی تیشرت چاپی؛ محافظت از چاپ در شستن، خشک‌کردن و اتوکشی','post_name'=>$slug16,'post_content'=>$c16,'post_category'=>[(int)$fabric->term_id]]),true);if(is_wp_error($a16)){http_response_code(500);echo wp_json_encode(['error'=>'a16']);exit;}
$a17=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت، افت پارچه، فاق و قد','post_name'=>$slug17,'post_content'=>$c17,'post_category'=>[(int)$buy->term_id]]),true);if(is_wp_error($a17)){wp_delete_post($a16,true);http_response_code(500);echo wp_json_encode(['error'=>'a17']);exit;}
$u16=get_permalink($a16);$u17=get_permalink($a17);
$meta=[$a16=>['rank_math_title'=>'شست‌وشوی تیشرت چاپی؛ محافظت از چاپ و پارچه','rank_math_description'=>'برای شست‌وشوی تیشرت چاپی، اول لیبل و نوع چاپ را بررسی کنید؛ سپس شستن، خشک‌کردن و اتوکشی را طوری مدیریت کنید که تماس و حرارت اضافه به چاپ وارد نشود.','rank_math_focus_keyword'=>'شستشوی تیشرت چاپی'],$a17=>['rank_math_title'=>'راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت و افت پارچه','rank_math_description'=>'برای خرید شلوار پارچه‌ای مردانه، فیت، فاق، ران، دمپا، قد و افت واقعی پارچه را بررسی کنید و اندازه‌ها را با یک شلوار مرجع مقایسه کنید.','rank_math_focus_keyword'=>'راهنمای خرید شلوار پارچه ای مردانه']];foreach($meta as $id=>$vals){foreach($vals as $k=>$v)update_post_meta($id,$k,$v);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}
$bridges=[453=>'<div data-g1-wave="1617-tee-care-from-01"><h2>بعد از انتخاب فیت، از چاپ هم درست مراقبت کن</h2><p>اگر تیشرت انتخابی چاپ دارد، <a href="'.esc_url($u16).'">راهنمای شست‌وشوی تیشرت چاپی</a> کمک می‌کند شستن و حرارت را بدون نسخه عمومی برای همه چاپ‌ها مدیریت کنی.</p></div>',471=>'<div data-g1-wave="1617-tee-care-from-08"><h2>کیفیت خرید با نگهداری درست کامل می‌شود</h2><p>بعد از بررسی چاپ هنگام خرید، <a href="'.esc_url($u16).'">راهنمای مراقبت و شست‌وشوی تیشرت چاپی</a> مرحله استفاده، خشک‌کردن و اتوکشی را پوشش می‌دهد.</p></div>',460=>'<div data-g1-wave="1617-fabric-pants-from-03"><h2>برای شلوار پارچه‌ای، فیت را کنار افت پارچه بخوان</h2><p>بعد از تشخیص بگ و نیم‌بگ، <a href="'.esc_url($u17).'">راهنمای خرید شلوار پارچه‌ای مردانه</a> فاق، ران، دمپا، قد و ریزش پارچه را به معیار خرید تبدیل می‌کند.</p></div>',468=>'<div data-g1-wave="1617-fabric-pants-from-07"><h2>اگر شلوار بگ پارچه‌ای می‌خواهی، اندازه و افت را جدا بررسی کن</h2><p>برای خود محصول، <a href="'.esc_url($u17).'">راهنمای خرید شلوار پارچه‌ای مردانه</a> کمک می‌کند فیت، قد و رفتار پارچه را قبل از خرید مقایسه کنی.</p></div>'];
foreach($bridges as $id=>$block){$r=wp_update_post(wp_slash(['ID'=>$id,'post_content'=>$posts[$id]->post_content."\n".$block]),true);if(is_wp_error($r)){foreach($originals as $oid=>$old)wp_update_post(wp_slash(['ID'=>$oid,'post_content'=>$old]));wp_delete_post($a17,true);wp_delete_post($a16,true);http_response_code(500);echo wp_json_encode(['error'=>'bridge']);exit;}}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'counts'=>['fit'=>(int)get_term($fit->term_id)->count,'fabric'=>(int)get_term($fabric->term_id)->count,'style'=>(int)get_term($style->term_id)->count,'buy'=>(int)get_term($buy->term_id)->count],'a16'=>['id'=>(int)$a16,'url'=>$u16],'a17'=>['id'=>(int)$a17,'url'=>$u17],'originals'=>array_map('base64_encode',$originals)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save_public(probe,php);st,raw,final,_=get(BASE+"/"+probe+"?t="+str(int(time.time())),300);print("PUBLISH",st,final,raw.decode("utf-8","replace"));
if st!=200:raise SystemExit("PUBLISH FAILED")
result=json.loads(raw.decode("utf-8","replace"));a16=result["a16"];a17=result["a17"];errors=[]
if result.get("published")!=17:errors.append("published")
if result.get("counts")!={"fit":7,"fabric":4,"style":2,"buy":4}:errors.append("counts")
def verify(pid,url,title,mt,md,needed):
    st,raw,final,_=get(url+"?t="+str(int(time.time())),180);text=raw.decode("utf-8","replace");m=head(raw);links={norm(x) for x in re.findall(r'href=["\']([^"\']+)',text,re.I) if "gramiss.ir" in x};print("VERIFY",pid,st,final,"H2",text.count("<h2>"),json.dumps(m,ensure_ascii=False))
    if st!=200 or title not in text:errors.append(str(pid)+" render")
    if m["title"]!=mt or m["description"]!=md:errors.append(str(pid)+" meta")
    if norm(m["canonical"])!=norm(url) or "noindex" in m["robots"].lower():errors.append(str(pid)+" index")
    if not re.search(r'"@type"\s*:\s*"BlogPosting"',text,re.I) or re.search(r'"@type"\s*:\s*"Product"',text,re.I):errors.append(str(pid)+" schema")
    for x in needed:
        if norm(x) not in links:errors.append(str(pid)+" link "+norm(x))
verify(a16["id"],a16["url"],TITLE16,META16,DESC16,[commerce["graphic"],commerce["tshirt"],BASE+"/راهنمای-خرید-تیشرت-مردانه/"])
verify(a17["id"],a17["url"],TITLE17,META17,DESC17,[commerce["fabric"],commerce["pants"],BASE+"/تفاوت-شلوار-بگ-نیم-بگ-فول-بگ/",BASE+"/با-شلوار-بگ-مردانه-چی-بپوشیم/",BASE+"/راهنمای-خرید-شلوار-جین-مردانه/"])
for pid,url,marker,target in [(453,$u1,'data-g1-wave="1617-tee-care-from-01"',a16["url"]),(471,$u8,'data-g1-wave="1617-tee-care-from-08"',a16["url"]),(460,$u3,'data-g1-wave="1617-fabric-pants-from-03"',a17["url"]),(468,$u7,'data-g1-wave="1617-fabric-pants-from-07"',a17["url"])]:
    pass
'''
# Python cannot execute the PHP tuple loop above after interpolation; bridge verification is performed through public URLs below.
for pid,url,marker,target in [(453,BASE+"/تیشرت-باکسی-چیست-تفاوت-اورسایز/",'data-g1-wave="1617-tee-care-from-01"',a16["url"]),(471,BASE+"/راهنمای-خرید-تیشرت-مردانه/",'data-g1-wave="1617-tee-care-from-08"',a16["url"]),(460,BASE+"/تفاوت-شلوار-بگ-نیم-بگ-فول-بگ/",'data-g1-wave="1617-fabric-pants-from-03"',a17["url"]),(468,BASE+"/با-شلوار-بگ-مردانه-چی-بپوشیم/",'data-g1-wave="1617-fabric-pants-from-07"',a17["url"])]:
    st,rr,_,_=get(url+"?t="+str(int(time.time())),150);text=rr.decode("utf-8","replace");links={norm(x) for x in re.findall(r'href=["\']([^"\']+)',text,re.I) if "gramiss.ir" in x}
    if st!=200 or marker not in text or norm(target) not in links:errors.append("bridge "+str(pid))
postst,postu=sitemap("post-sitemap.xml");catst,catu=sitemap("category-sitemap.xml");pst2,pu2=sitemap("product-sitemap.xml");pcst2,pcu2=sitemap("product_cat-sitemap.xml");pu2=sorted(pu2);pcu2=sorted(pcu2)
if postst!=200 or len(postu)!=18 or norm(a16["url"]) not in {norm(x) for x in postu} or norm(a17["url"]) not in {norm(x) for x in postu}:errors.append("post sitemap")
if catst!=200 or len(catu)!=4:errors.append("cat sitemap")
if pu2!=pu or hashlib.sha256("\n".join(pu2).encode()).hexdigest()!=psha:errors.append("product drift")
if pcu2!=pcu or hashlib.sha256("\n".join(pcu2).encode()).hexdigest()!=pcsha:errors.append("product cat drift")
post_hash={p:hashlib.sha256(read_theme(p).encode()).hexdigest() for p in protected};print("PROTECTED_POST",json.dumps(post_hash,sort_keys=True))
if post_hash!=pre_hash:errors.append("protected drift")
found=set()
for page in (1,2):
    u=BASE+"/وبلاگ/" if page==1 else BASE+"/وبلاگ/page/2/";st,rr,_,_=get(u+"?t="+str(int(time.time())),150);text=rr.decode("utf-8","replace")
    if TITLE16 in text:found.add(16)
    if TITLE17 in text:found.add(17)
if found!={16,17}:errors.append("blog cards")
if errors:
    print("ERRORS",json.dumps(errors,ensure_ascii=False));rb="gramiss-wave-16-17-rollback-"+nonce+".php";snap=base64.b64encode(json.dumps(result.get("originals",{})).encode()).decode();rbphp=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);foreach([sanitize_title('شستشوی تیشرت چاپی'),sanitize_title('راهنمای خرید شلوار پارچه ای مردانه')] as $s){$p=get_page_by_path($s,OBJECT,'post');if($p)wp_delete_post($p->ID,true);}$x=json_decode(base64_decode('SNAP'),true);foreach($x as $id=>$b){$c=base64_decode($b,true);if($c!==false)wp_update_post(wp_slash(['ID'=>(int)$id,'post_content'=>$c]));}if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();do_action('litespeed_purge_all');echo wp_json_encode(['rolled_back'=>true,'published'=>(int)wp_count_posts('post')->publish]);?>'''.replace("SNAP",snap);save_public(rb,rbphp);rst,rraw,_,_=get(BASE+"/"+rb+"?t="+str(int(time.time())),240);print("ROLLBACK",rst,rraw.decode("utf-8","replace"));raise SystemExit("VERIFY FAILED; ROLLED BACK")
print("PASS EDITORIAL WAVE 16-17",json.dumps({"a16":a16,"a17":a17,"post_sitemap":len(postu),"product_sitemap":len(pu2),"product_sha":psha,"product_cat_sitemap":len(pcu2),"product_cat_sha":pcsha,"protected":post_hash},ensure_ascii=False,sort_keys=True))
