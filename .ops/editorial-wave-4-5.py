import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']
root=os.environ['THEME_ROOT'].strip('/'); healthy=os.environ.get('HEALTHY_HOME_SHA','')
ctx=ssl._create_unverified_context(); BASE='https://gramiss.ir'

def call(fn,p,post=False):
    u=f'https://{host}:2083/execute/Fileman/{fn}'; d=urllib.parse.urlencode(p).encode(); last=None
    for attempt in range(1,5):
        try:
            req=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET')
            req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
            q=o.get('result') if isinstance(o.get('result'),dict) else o
            if not isinstance(q,dict) or q.get('status')!=1: raise RuntimeError(str(q))
            return q.get('data')
        except Exception as exc:
            last=exc; print('API_RETRY',fn,attempt,exc)
            if attempt<4:time.sleep(attempt*2)
    raise last

def read_theme(rel):
    p,n=rel.rsplit('/',1) if '/' in rel else ('',rel)
    d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str):return d[k]
    return d if isinstance(d,str) else ''

def save_public(n,c):
    return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def get(u,follow=True,timeout=180):
    class NR(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl):return None
    req=urllib.request.Request(u,headers={'User-Agent':'GramissEditorialWave45/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    hs=[urllib.request.HTTPSHandler(context=ctx)]
    if not follow:hs.insert(0,NR())
    op=urllib.request.build_opener(*hs)
    try:
        with op.open(req,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
    except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)

def hval(raw,p):
    m=re.search(p,raw,re.I|re.S); return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def head(raw):
    t=raw.decode('utf-8','replace').split('</head>',1)[0]
    return {'title':hval(t,r'<title[^>]*>(.*?)</title>'),'description':hval(t,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':hval(t,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':hval(t,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
def norm_url(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sitemap_locs(path):
    s,raw,_,_=get(BASE+'/'+path+'?t='+str(int(time.time())),True,120); txt=raw.decode('utf-8','replace')
    return s,[re.sub(r'&amp;','&',x) for x in re.findall(r'<loc>(.*?)</loc>',txt,re.I)]

protected=['front-page.php','template-parts/home-looks.php','assets/css/home-looks.css','assets/js/home-looks.js']
pre_hash={f:hashlib.sha256(read_theme(f).encode()).hexdigest() for f in protected}
print('PROTECTED_PRE',json.dumps(pre_hash,ensure_ascii=False,sort_keys=True))
if healthy and pre_hash['front-page.php']!=healthy:raise SystemExit('ABORT Home mismatch')
for f,m in [('home.php','g1-editorial-index'),('single.php','g1-editorial-single'),('category.php','g1-editorial-category'),('assets/css/editorial-v1.css','GRAMISS_EDITORIAL_V1')]:
    if m not in read_theme(f):raise SystemExit('ABORT editorial foundation missing '+f)

ps0,product_locs_before=sitemap_locs('product-sitemap.xml')
if ps0!=200:raise SystemExit('ABORT product sitemap preflight')
product_locs_before=sorted(product_locs_before); product_sha=hashlib.sha256('\n'.join(product_locs_before).encode()).hexdigest()
print('PRODUCT_SITEMAP_PRE',len(product_locs_before),product_sha)

linen_cat=BASE+'/product-category/shirt/linen-shirt/'
ls,lraw,lf,_=get(linen_cat+'?t='+str(int(time.time())),True,120); lh=head(lraw)
print('LINEN_COMMERCE_PRE',ls,lf,json.dumps(lh,ensure_ascii=False,separators=(',',':')))
if ls!=200 or 'noindex' in lh.get('robots','').lower() or norm_url(lh.get('canonical',''))!=norm_url(linen_cat):raise SystemExit('ABORT linen commerce category not safely indexable')

nonce=hashlib.sha256((str(time.time())+pre_hash['front-page.php']).encode()).hexdigest()[:14]; name='gramiss-editorial-wave-4-5-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$slug4=sanitize_title('پارچه لینن چیست');$slug5=sanitize_title('شستشوی پیراهن لینن مردانه');
$a1=get_post(453);$a2=get_post(459);$a3=get_post(460);$a4x=get_page_by_path($slug4,OBJECT,'post');$a5x=get_page_by_path($slug5,OBJECT,'post');
$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');$blog=get_post(22);$linen=get_term_by('slug','linen-shirt','product_cat');$published=(int)wp_count_posts('post')->publish;
if(!$a1||!$a2||!$a3||$a1->post_status!=='publish'||$a2->post_status!=='publish'||$a3->post_status!=='publish'||$a4x||$a5x||!$fit||!$fabric||!$style||!$buy||!$blog||!$linen||$published!==3||(int)$fit->count!==3||(int)$fabric->count!==0){http_response_code(409);echo wp_json_encode(['error'=>'baseline drift','published'=>$published,'a1'=>$a1?$a1->ID:null,'a2'=>$a2?$a2->ID:null,'a3'=>$a3?$a3->ID:null,'a4'=>$a4x?$a4x->ID:null,'a5'=>$a5x?$a5x->ID:null,'fit'=>$fit?[$fit->term_id,$fit->count]:null,'fabric'=>$fabric?[$fabric->term_id,$fabric->count]:null],JSON_UNESCAPED_UNICODE);exit;}
if(strpos($a2->post_content,'data-g1-cluster-wave="45"')!==false){http_response_code(409);echo wp_json_encode(['error'=>'article2 wave45 marker exists']);exit;}
$linen_url=get_term_link($linen);if(is_wp_error($linen_url)){http_response_code(409);echo wp_json_encode(['error'=>'linen category url']);exit;}

$content4=<<<'HTML'
<p>لینن یکی از قدیمی‌ترین نام‌ها در دنیای پارچه است، اما در خرید لباس امروز یک نکته مهم وجود دارد: دیدن کلمه «لینن» روی نام یک محصول به‌تنهایی برای فهمیدن ترکیب دقیق الیاف کافی نیست. در تعریف نساجی، linen به پارچه‌ای گفته می‌شود که از الیاف گیاه فلکس یا کتان ساخته شده است؛ در بازار پوشاک اما ممکن است محصولی با ظاهر و بافت لیننی، ترکیبی از چند الیاف باشد. برای همین هنگام خرید، ترکیب الیاف و برچسب مراقبت لباس مرجع دقیق‌تری از اسم تجاری هستند.</p>
<p>در این راهنما می‌خواهیم بدون اغراق تبلیغاتی بررسی کنیم پارچه لینن چیست، چرا ظاهر طبیعی و چروک‌پذیر دارد، لینن خالص و ترکیبی چه تفاوتی دارند و هنگام انتخاب یا نگهداری لباس لینن باید به چه چیزهایی توجه کرد.</p>
<h2>پارچه لینن چیست؟</h2>
<p>لینن در معنای فنی پارچه‌ای است که از الیاف فلکس ساخته می‌شود. ساختار این الیاف باعث می‌شود پارچه بتواند حس خشک‌تر و خنک‌تری نسبت به بسیاری از پارچه‌های نرم و پرزدار داشته باشد و ظاهر آن معمولاً کاملاً صیقلی و بی‌نقص نیست. همین بافت طبیعی بخشی از هویت بصری لینن محسوب می‌شود.</p>
<p>با این حال، در فروشگاه‌ها واژه «لینن» گاهی برای پارچه‌های ترکیبی یا پارچه‌هایی با بافت لیننی هم استفاده می‌شود. اگر درصد الیاف برای تصمیم تو مهم است، باید ترکیب درج‌شده روی لیبل یا مشخصات همان محصول را بررسی کنی.</p>
<h2>لینن خالص و لینن ترکیبی چه تفاوتی دارند؟</h2>
<p>وقتی پارچه فقط از الیاف فلکس ساخته شده باشد، می‌توان آن را لینن خالص دانست. در پارچه‌های ترکیبی، فلکس ممکن است کنار پنبه، ویسکوز یا الیاف دیگر قرار بگیرد. ترکیب الیاف می‌تواند روی نرمی، میزان چروک، افت پارچه، زمان خشک‌شدن و حتی دستور شست‌وشو اثر بگذارد.</p>
<p>این تفاوت به معنی بهتر یا بدتر بودن مطلق یکی از آن‌ها نیست. ممکن است یک ترکیب برای ایستایی خاص لباس مناسب‌تر باشد و ترکیب دیگری حس طبیعی‌تر لینن را برجسته‌تر کند. معیار بهتر، کاربرد لباس و مشخصات واقعی همان محصول است.</p>
<h2>چرا لینن برای هوای گرم محبوب است؟</h2>
<p>لباس‌های لیننی معمولاً به‌خاطر بافت نسبتاً باز، توانایی جذب رطوبت و حس سبک و خشک پارچه در پوشش‌های هوای گرم محبوب‌اند. البته تجربه واقعی به وزن پارچه، تراکم بافت، الگوی لباس و ترکیب الیاف بستگی دارد؛ بنابراین صرف کلمه «لینن» تضمین نمی‌کند همه لباس‌های این گروه عملکرد یکسانی داشته باشند.</p>
<p>در یک پیراهن مردانه، آزادی الگو و فاصله پارچه از بدن هم می‌تواند به اندازه جنس پارچه روی حس خنکی اثر بگذارد. بهتر است جنس و فیت را در کنار هم ببینی.</p>
<h2>چرا پارچه لینن چروک می‌شود؟</h2>
<p>چروک‌پذیری لینن ویژگی شناخته‌شده این خانواده پارچه است. الیاف آن کشسانی زیادی ندارند و پس از خم‌شدن یا فشرده‌شدن، سریع‌تر خط تا را نشان می‌دهند. به همین دلیل نشستن طولانی، جمع‌کردن آستین یا قرارگرفتن زیر کمربند می‌تواند روی سطح لباس رد ایجاد کند.</p>
<p>این موضوع الزاماً نشانه کیفیت پایین نیست. در استایل‌های غیررسمی، مقدار کنترل‌شده‌ای از چروک حتی بخشی از ظاهر طبیعی لباس است. اگر ظاهر اتوکشیده‌تر می‌خواهی، باید به ترکیب الیاف، وزن پارچه و روش نگهداری توجه بیشتری داشته باشی.</p>
<h2>آیا لینن آب می‌رود؟</h2>
<p>نمی‌توان برای همه لباس‌های لینن یک درصد ثابت آب‌رفت اعلام کرد. تغییر ابعاد به ترکیب الیاف، پیش‌شست‌وشوی پارچه، تکمیل کارخانه، دمای آب، خشک‌کن و ساخت خود لباس وابسته است. بعضی محصولات قبل از دوخت یا فروش فرایندهایی را طی می‌کنند که رفتار آن‌ها بعد از شست‌وشو را تغییر می‌دهد.</p>
<p>برای همین به‌جای اضافه‌کردن یک «سایز اطمینان» بر اساس حدس، جدول اندازه همان محصول و دستور مراقبت آن را مبنا قرار بده. اگر سازنده درباره تغییر ابعاد توضیح مشخصی داده، همان اطلاعات از قانون‌های عمومی معتبرتر است.</p>
<h2>لینن نرم بهتر است یا ساختارمند؟</h2>
<p>این سؤال پاسخ واحد ندارد. لینن نرم‌تر و ریزشی برای پیراهنی که قرار است آزادتر روی بدن بیفتد حس متفاوتی ایجاد می‌کند؛ پارچه ساختارمندتر خطوط یقه، سرشانه و بدنه را واضح‌تر نگه می‌دارد. شست‌وشو و استفاده مکرر نیز می‌تواند حس دست بعضی پارچه‌های لیننی را تغییر دهد.</p>
<p>هنگام خرید آنلاین فقط به عکس نزدیک بافت نگاه نکن. نمای تمام‌قد، نحوه افت آستین و حرکت پایین لباس اطلاعات بیشتری درباره رفتار واقعی پارچه می‌دهد.</p>
<h2>برای خرید پیراهن لینن چه چیزهایی را بررسی کنیم؟</h2>
<ul><li><strong>ترکیب الیاف:</strong> اگر درج شده، مشخص می‌کند با لینن خالص یا یک ترکیب روبه‌رو هستی.</li><li><strong>وزن و شفافیت:</strong> پارچه‌های سبک ممکن است در نور شدید شفاف‌تر دیده شوند.</li><li><strong>افت پارچه:</strong> از عکس تنخور و نمای کنار قابل تشخیص‌تر است.</li><li><strong>اندازه واقعی لباس:</strong> عرض سینه، سرشانه و قد را با یک پیراهن مرجع مقایسه کن.</li><li><strong>دستور مراقبت:</strong> قبل از خرید ببین شست‌وشو یا اتوکشی خاصی لازم دارد یا نه.</li><li><strong>نوع استفاده:</strong> یک پیراهن بسیار رها و سبک با یک مدل ساختارمند برای موقعیت‌های متفاوتی مناسب است.</li></ul>
<h2>رنگ و بافت لینن چه اثری روی ظاهر لباس دارد؟</h2>
<p>سطح لینن معمولاً کاملاً یکنواخت نیست و همین موضوع می‌تواند در رنگ‌های روشن، سایه‌های ریز و بافت را بیشتر نشان دهد. در رنگ‌های تیره، خطوط چروک یا برق ناشی از فشار ممکن است متفاوت دیده شوند. این تفاوت‌ها را بهتر است بخشی از جنس پارچه بدانیم، نه چیزی که در همه رنگ‌ها یکسان رفتار می‌کند.</p>
<p>اگر قصد خرید داری، تصاویر محصول را در چند نما ببین. در Gramiss می‌توانی <a href="LINEN_URL">مدل‌های فعلی پیراهن لینن</a> را کنار هم ببینی و بعد مشخصات هر محصول را جداگانه بررسی کنی.</p>
<h2>شست‌وشو چطور روی ظاهر لینن اثر می‌گذارد؟</h2>
<p>حرارت زیاد، دور خشک‌کن بالا و فشردن شدید پارچه می‌تواند چروک را بیشتر کند و در بعضی لباس‌ها روی ابعاد یا حس دست اثر بگذارد. رویکرد محافظه‌کارانه این است که اول برچسب مراقبت همان لباس را بخوانی و اگر اجازه داده شده، از چرخه ملایم، شوینده ملایم و خشک‌کردن با فشار مکانیکی کمتر استفاده کنی.</p>
<p>برای مراحل دقیق‌تر، <a href="A5_URL">راهنمای شست‌وشوی پیراهن لینن، خشک‌کردن و اتوکشی</a> را بخوان.</p>
<h2>اتو کردن لینن؛ کاملاً صاف یا طبیعی؟</h2>
<p>اگر ظاهر رسمی‌تر می‌خواهی، اتوکشی وقتی پارچه کمی رطوبت دارد معمولاً ساده‌تر است؛ اما دمای مجاز اتو باید از برچسب لباس خوانده شود، چون ترکیب الیاف می‌تواند محدودیت را تغییر دهد. برای استایل روزمره لازم نیست همه خطوط طبیعی پارچه را حذف کنی.</p>
<p>هدف این نیست که لینن شبیه یک پارچه مصنوعی کاملاً صاف شود؛ هدف این است که چروک‌های نامرتب کنترل شوند و فرم یقه، سجاف و آستین تمیز بماند.</p>
<h2>اشتباهات رایج درباره پارچه لینن</h2>
<ul><li>فرض اینکه هر محصول با نام لینن حتماً صددرصد فلکس است.</li><li>درنظرگرفتن یک درصد ثابت برای آب‌رفت همه لباس‌ها.</li><li>بزرگ‌تر خریدن سایز فقط به‌خاطر ترس از آب‌رفت بدون بررسی اطلاعات محصول.</li><li>استفاده از حرارت یا خشک‌کن شدید بدون خواندن لیبل مراقبت.</li><li>تصور اینکه هر چروکی نشانه کیفیت پایین پارچه است.</li><li>مقایسه دو پیراهن فقط از روی نام پارچه و نادیده‌گرفتن وزن، الگو و ترکیب الیاف.</li></ul>
<h2>چک‌لیست سریع قبل از انتخاب لباس لینن</h2>
<ul><li>ترکیب الیاف را در مشخصات یا برچسب پیدا کن.</li><li>فیت و اندازه واقعی لباس را جدا از نام پارچه بسنج.</li><li>میزان ریزش و ساختار پارچه را از تصاویر تنخور بررسی کن.</li><li>برای رنگ‌های روشن به شفافیت احتمالی توجه کن.</li><li>دستور شست‌وشو و اتوکشی همان لباس را مبنا قرار بده.</li><li>چروک طبیعی را بخشی از تصمیم استایل در نظر بگیر.</li></ul>
<p><strong>جمع‌بندی:</strong> شناخت لینن با یک برچسب تمام نمی‌شود. ترکیب الیاف، وزن، بافت، الگوی لباس و دستور مراقبت با هم مشخص می‌کنند یک پیراهن لیننی چطور روی بدن می‌ایستد و بعد از استفاده چگونه نگهداری می‌شود.</p>
HTML;

$content5=<<<'HTML'
<p>شست‌وشوی پیراهن لینن زمانی ساده می‌شود که یک اصل را جدی بگیری: برچسب مراقبت همان لباس از هر راهنمای عمومی مهم‌تر است. دلیلش هم روشن است؛ همه پارچه‌هایی که در بازار «لینن» نامیده می‌شوند ترکیب، وزن و تکمیل یکسانی ندارند و ممکن است بخشی از الیاف آن‌ها از جنس دیگری باشد.</p>
<p>در این راهنما روش محافظه‌کارانه مراقبت از پیراهن لینن را مرور می‌کنیم؛ از آماده‌سازی و شست‌وشو تا خشک‌کردن، اتوکشی، کنترل چروک و نگهداری. اگر ابتدا می‌خواهی جنس را بهتر بشناسی، <a href="A4_URL">راهنمای «پارچه لینن چیست؟»</a> نقطه شروع مناسب‌تری است.</p>
<h2>قبل از شست‌وشو، لیبل لباس را بخوان</h2>
<p>اولین مرحله این است که نمادهای شست‌وشو، دمای مجاز، امکان اتوکشی و محدودیت خشک‌کن را بررسی کنی. اگر لباس ترکیبی باشد، ممکن است حساس‌ترین الیاف موجود در پارچه تعیین‌کننده روش مراقبت باشند. بنابراین یک روش ثابت برای همه پیراهن‌های لیننی وجود ندارد.</p>
<p>اگر برچسب فقط شست‌وشوی دستی یا خشکشویی را مجاز می‌داند، توصیه عمومی ماشین لباسشویی نباید جای آن را بگیرد.</p>
<h2>پیراهن را قبل از قرار دادن در ماشین آماده کن</h2>
<ul><li>جیب‌ها را خالی کن و اجسام تیز یا سنگین را بیرون بیاور.</li><li>اگر روی لباس لکه مشخصی هست، آن را قبل از شست‌وشوی کامل بررسی کن.</li><li>لباس‌های روشن و تیره را بر اساس احتمال رنگ‌دهی جدا کن.</li><li>برای کاهش اصطکاک، ماشین را بیش از ظرفیت پر نکن.</li><li>اگر سازنده توصیه کرده، پیراهن را پشت‌ورو کن تا سایش سطحی کمتر شود.</li></ul>
<p>این آماده‌سازی ساده باعث می‌شود فشار مکانیکی روی یقه، دکمه‌ها و سطح پارچه کمتر شود.</p>
<h2>شست‌وشوی دستی بهتر است یا ماشین؟</h2>
<p>هیچ‌کدام ذاتاً برای همه لباس‌ها بهتر نیست. اگر لیبل ماشین را مجاز بداند، چرخه ملایم با بار سبک می‌تواند انتخاب عملی باشد. در شست‌وشوی دستی نیز نباید پارچه را با پیچاندن شدید آبگیری کرد، چون این کار فشار زیادی روی بافت و درزها وارد می‌کند.</p>
<p>در هر دو روش، تماس خشن و طولانی با پارچه را کم کن و بعد از پایان شست‌وشو لباس را مدت زیادی خیس و مچاله رها نکن.</p>
<h2>دمای آب را چطور انتخاب کنیم؟</h2>
<p>دمای دقیق را از لیبل بخوان. برای بسیاری از لباس‌های لیننی، آب خنک یا ولرم و چرخه ملایم انتخاب محافظه‌کارانه‌تری نسبت به آب بسیار گرم است. حرارت بیشتر می‌تواند روی بعضی رنگ‌ها، تکمیل پارچه یا ابعاد لباس اثر بگذارد.</p>
<p>به‌جای حفظ‌کردن یک عدد ثابت، محدودیت درج‌شده روی همان لباس را سقف تصمیم خود قرار بده.</p>
<h2>چه شوینده‌ای برای لینن مناسب‌تر است؟</h2>
<p>شوینده ملایم و مقدار متناسب با حجم لباس معمولاً انتخاب امن‌تری است. شوینده بیش از حد می‌تواند به‌سختی از میان بافت خارج شود و باقی‌مانده آن حس پارچه را تغییر دهد. سفیدکننده‌های قوی نیز ممکن است برای بعضی رنگ‌ها یا ترکیبات پارچه مناسب نباشند؛ فقط زمانی استفاده کن که برچسب و دستور محصول اجازه می‌دهد.</p>
<p>برای لکه‌ها هم ابتدا از روش‌های ملایم‌تر و آزمون روی بخش کم‌دید لباس شروع کن، نه از مواد قوی و ناشناخته.</p>
<h2>دور خشک‌کن ماشین چرا مهم است؟</h2>
<p>هرچه دور آبگیری بالاتر باشد، پارچه بیشتر به دیواره دیگ فشرده می‌شود و چروک عمیق‌تری می‌تواند شکل بگیرد. اگر لیبل اجازه می‌دهد، دور پایین‌تر و خارج‌کردن لباس بلافاصله پس از پایان چرخه معمولاً به کنترل چروک کمک می‌کند.</p>
<p>وقتی پیراهن را بیرون می‌آوری، آن را با تکان ملایم باز کن و درزها، یقه و سجاف را با دست مرتب کن؛ این کار قبل از خشک‌شدن بسیار مؤثرتر از تلاش برای بازکردن چروک‌های خشک است.</p>
<h2>بهترین روش خشک‌کردن پیراهن لینن چیست؟</h2>
<p>اگر برچسب اجازه می‌دهد، خشک‌کردن طبیعی در سایه و جریان هوا روشی کم‌فشار است. پیراهن را در فرم طبیعی خودش قرار بده و از پیچاندن شدید برای خارج‌کردن آب خودداری کن. برای بعضی لباس‌ها آویزان‌کردن مناسب است و برای بعضی بافت‌های سنگین‌تر، خشک‌کردن روی سطح صاف می‌تواند از کشیدگی جلوگیری کند.</p>
<p>نور مستقیم و حرارت شدید ممکن است روی بعضی رنگ‌ها یا تکمیل پارچه اثر بگذارد؛ بنابراین باز هم دستور همان محصول اولویت دارد.</p>
<h2>آیا می‌توان پیراهن لینن را در خشک‌کن انداخت؟</h2>
<p>فقط اگر برچسب لباس آن را مجاز کرده باشد. خشک‌کن با حرارت بالا و زمان طولانی می‌تواند چروک را تثبیت کند یا در برخی پارچه‌ها تغییر ابعاد ایجاد کند. اگر استفاده از خشک‌کن مجاز است، تنظیمات کم‌حرارت و زمان کوتاه‌تر معمولاً محافظه‌کارانه‌ترند.</p>
<p>بیرون‌آوردن لباس در حالی که هنوز کمی رطوبت دارد می‌تواند اتوکشی را ساده‌تر کند؛ البته این کار هم باید با محدودیت‌های لیبل هماهنگ باشد.</p>
<h2>اتوکشی لینن را چه زمانی انجام دهیم؟</h2>
<p>لینن اغلب زمانی که کمی نم دارد راحت‌تر صاف می‌شود. لباس را پشت‌ورو یا از روی یک پارچه محافظ اتو کن اگر سطح یا رنگ آن حساس به برق افتادن است. درجه حرارت اتو را از علامت روی لیبل انتخاب کن، مخصوصاً اگر پارچه ترکیبی است.</p>
<p>یقه، سرشانه، سجاف جلو و سرآستین‌ها را قبل از بخش‌های بزرگ مرتب کن تا فرم اصلی پیراهن حفظ شود. لازم نیست هر خط طبیعی پارچه را کاملاً محو کنی.</p>
<h2>چطور چروک پیراهن لینن را کمتر کنیم؟</h2>
<ul><li>ماشین را بیش از حد پر نکن.</li><li>چرخه و دور آبگیری را مطابق لیبل و تا حد ممکن ملایم انتخاب کن.</li><li>لباس را بلافاصله پس از پایان شست‌وشو خارج کن.</li><li>قبل از خشک‌شدن یقه، آستین و سجاف را با دست صاف کن.</li><li>پیراهن خشک را فشرده داخل کمد قرار نده.</li><li>برای سفر، لباس را تا حد ممکن بدون فشار زیاد بسته‌بندی کن.</li></ul>
<h2>اگر نگران آب‌رفت هستیم چه کنیم؟</h2>
<p>قبل از اولین شست‌وشو، اگر اندازه لباس برایت حساس است می‌توانی عرض سینه و قد را روی سطح صاف ثبت کنی. بعد دقیقاً بر اساس لیبل بشوی و دوباره اندازه بگیر. این روش اطلاعات واقعی درباره همان لباس به تو می‌دهد، در حالی که درصدهای عمومی اینترنتی ممکن است برای ترکیب و تکمیل محصول تو صدق نکنند.</p>
<p>در زمان خرید هم بهتر است سایز را بر اساس جدول واقعی محصول انتخاب کنی، نه با فرض اینکه «حتماً بعداً چند سانتی‌متر کوچک می‌شود».</p>
<h2>لکه روی لینن را چطور مدیریت کنیم؟</h2>
<p>لکه را هرچه زودتر بررسی کن، اما پارچه را با برس زبر یا مالش شدید نساب. نوع لکه تعیین می‌کند چه پاک‌کننده‌ای مناسب است و بعضی مواد می‌توانند رنگ پارچه را تغییر دهند. اگر لکه حساس یا لباس ارزشمند است، روش تأییدشده سازنده یا خدمات تخصصی انتخاب مطمئن‌تری است.</p>
<p>هیچ محلول خانگی را بدون آزمون روی قسمت پنهان لباس به کل سطح نزن.</p>
<h2>نگهداری پیراهن لینن در کمد</h2>
<p>لباس باید کاملاً خشک باشد. پیراهن را با فضای کافی نگه دار تا زیر فشار لباس‌های دیگر چروک عمیق نگیرد. اگر روی چوب‌لباسی قرار می‌دهی، فرم شانه چوب‌لباسی با عرض شانه لباس هماهنگ باشد تا برجستگی نامعمول ایجاد نشود.</p>
<p>برای نگهداری طولانی، محیط خشک و دارای گردش هوا بهتر از بسته‌بندی مرطوب و فشرده است.</p>
<h2>اشتباهات رایج در شست‌وشوی پیراهن لینن</h2>
<ul><li>نادیده‌گرفتن لیبل و استفاده از یک نسخه ثابت برای همه لباس‌های لیننی.</li><li>آبگیری با پیچاندن شدید پارچه.</li><li>پرکردن بیش از حد ماشین و افزایش اصطکاک.</li><li>رهاکردن لباس خیس و مچاله داخل ماشین.</li><li>استفاده خودکار از حرارت زیاد برای سریع‌تر خشک‌شدن.</li><li>خرید سایز بزرگ‌تر فقط بر اساس یک درصد فرضی آب‌رفت.</li></ul>
<h2>چک‌لیست کوتاه مراقبت</h2>
<ul><li>لیبل را قبل از اولین شست‌وشو بخوان.</li><li>رنگ‌های مشکوک به رنگ‌دهی را جدا کن.</li><li>از فشار مکانیکی و حرارت غیرضروری کم کن.</li><li>لباس را سریع از ماشین خارج و در فرم طبیعی مرتب کن.</li><li>در صورت مجاز بودن، در سایه و جریان هوا خشک کن.</li><li>دمای اتو و خشک‌کن را از لیبل همان محصول تعیین کن.</li></ul>
<p>اگر به‌دنبال مدل‌های فعلی هستی، صفحه <a href="LINEN_URL">پیراهن‌های لینن Gramiss</a> را ببین و دستور مراقبت هر محصول را جداگانه بررسی کن.</p>
<p><strong>جمع‌بندی:</strong> مراقبت خوب از لینن بیشتر از آنکه به یک ترفند خاص وابسته باشد، به کاهش فشار و حرارت غیرضروری و پیروی از اطلاعات همان لباس وابسته است. وقتی ترکیب الیاف و برچسب مراقبت را مبنا قرار بدهی، تصمیم درباره شست‌وشو، خشک‌کردن و اتوکشی دقیق‌تر می‌شود.</p>
HTML;

$content4=str_replace(['LINEN_URL','A5_URL'],[esc_url($linen_url),'__A5__'],$content4);$content5=str_replace(['A4_URL','LINEN_URL'],['__A4__',esc_url($linen_url)],$content5);
$a4=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'پارچه لینن چیست؟ راهنمای شناخت، چروک و انتخاب لباس لینن','post_name'=>$slug4,'post_excerpt'=>'پارچه لینن را از نظر بافت، ترکیب الیاف، چروک‌پذیری و مراقبت بشناسید و هنگام انتخاب لباس لینن به مشخصات واقعی همان محصول توجه کنید.','post_content'=>$content4,'post_category'=>[(int)$fabric->term_id],'post_author'=>1]),true);
if(is_wp_error($a4)){http_response_code(500);echo wp_json_encode(['error'=>'article4 insert','message'=>$a4->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a4_url=get_permalink($a4);$content5=str_replace('__A4__',esc_url($a4_url),$content5);
$a5=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'شست‌وشوی پیراهن لینن مردانه؛ راهنمای خشک‌کردن و اتوکشی','post_name'=>$slug5,'post_excerpt'=>'برای شست‌وشوی پیراهن لینن، برچسب مراقبت را مبنا قرار دهید و با کاهش فشار و حرارت غیرضروری، چروک و تغییر ناخواسته پارچه را بهتر کنترل کنید.','post_content'=>$content5,'post_category'=>[(int)$fabric->term_id],'post_author'=>1]),true);
if(is_wp_error($a5)){wp_delete_post($a4,true);http_response_code(500);echo wp_json_encode(['error'=>'article5 insert','message'=>$a5->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a5_url=get_permalink($a5);$c4=get_post_field('post_content',$a4);$c4=str_replace('__A5__',esc_url($a5_url),$c4);$r4=wp_update_post(wp_slash(['ID'=>$a4,'post_content'=>$c4]),true);if(is_wp_error($r4)){wp_delete_post($a5,true);wp_delete_post($a4,true);http_response_code(500);echo wp_json_encode(['error'=>'article4 reciprocal update']);exit;}
$meta=[$a4=>['rank_math_title'=>'پارچه لینن چیست؟ ویژگی‌ها، چروک و شست‌وشو','rank_math_description'=>'پارچه لینن چیست، چرا چروک می‌شود و هنگام خرید یا شست‌وشوی لباس لینن باید به چه چیزهایی توجه کرد؟ تفاوت لینن خالص و ترکیبی را هم بشناسید.','rank_math_focus_keyword'=>'پارچه لینن چیست'],$a5=>['rank_math_title'=>'شست‌وشوی پیراهن لینن؛ خشک‌کردن و اتوکشی','rank_math_description'=>'برای شست‌وشوی پیراهن لینن، دما، دور ماشین، خشک‌کردن و اتوکشی را چطور انتخاب کنیم؟ راهنمای مراقبت بدون حدس درباره آب‌رفت لباس.','rank_math_focus_keyword'=>'شستشوی پیراهن لینن']];
foreach($meta as $id=>$mm){foreach($mm as $k=>$v)update_post_meta($id,$k,$v);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}
$bridge='<div data-g1-cluster-wave="45"><h2>پارچه و شست‌وشو را هم در انتخاب سایز در نظر بگیر</h2><p>اگر می‌خواهی قبل از خرید رفتار پارچه را بهتر بفهمی، <a href="'.esc_url($a4_url).'">راهنمای شناخت پارچه لینن</a> را ببین. برای نگهداری و جلوگیری از تصمیم‌های حدسی درباره آب‌رفت هم <a href="'.esc_url($a5_url).'">راهنمای شست‌وشوی پیراهن لینن</a> را بخوان.</p></div>';
$u2=wp_update_post(wp_slash(['ID'=>$a2->ID,'post_content'=>$a2->post_content."\n".$bridge]),true);if(is_wp_error($u2)){wp_delete_post($a5,true);wp_delete_post($a4,true);http_response_code(500);echo wp_json_encode(['error'=>'article2 bridge update']);exit;}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'fabric'=>['id'=>(int)$fabric->term_id,'count'=>(int)get_term($fabric->term_id)->count,'url'=>get_term_link($fabric)],'fit'=>['count'=>(int)get_term($fit->term_id)->count,'url'=>get_term_link($fit)],'blog'=>get_permalink(22),'linen'=>$linen_url,'a2'=>get_permalink($a2),'a4'=>['id'=>(int)$a4,'url'=>get_permalink($a4),'focus'=>get_post_meta($a4,'rank_math_focus_keyword',true)],'a5'=>['id'=>(int)$a5,'url'=>get_permalink($a5),'focus'=>get_post_meta($a5,'rank_math_focus_keyword',true)]],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''

save_public(name,php); s,b,_,_=get(BASE+'/'+name+'?t='+str(int(time.time())),True,240); txt=b.decode('utf-8','replace'); print('WRITE',s,txt)
if s!=200:raise SystemExit('article 04/05 write failed')
d=json.loads(txt); a2=d['a2'];a4=d['a4']['url'];a5=d['a5']['url'];fabric=d['fabric']['url'];fit=d['fit']['url'];blog=d['blog'];errors=[]
if d.get('published')!=5:errors.append('published count not 5')
if d['fabric'].get('count')!=2:errors.append('fabric category count not 2')
if d['fit'].get('count')!=3:errors.append('fit category count changed')
if d['a4'].get('focus')!='پارچه لینن چیست':errors.append('A4 focus mismatch')
if d['a5'].get('focus')!='شستشوی پیراهن لینن':errors.append('A5 focus mismatch')

pages={}
for label,url,frag in [('A4',a4,'پارچه لینن چیست'),('A5',a5,'شست‌وشوی پیراهن لینن')]:
    st,raw,final,_=get(url+'?t='+str(int(time.time())),True,150); h=head(raw); body=raw.decode('utf-8','replace'); pages[label]=(st,h,body,final)
    print('LIVE_'+label,st,final,json.dumps(h,ensure_ascii=False,separators=(',',':')),'LEN',len(body),'H2',body.count('<h2>'),'BLOGPOSTING',('BlogPosting' in body))
    if st!=200:errors.append(label+' not 200');continue
    if 'g1-editorial-single' not in body:errors.append(label+' editorial template missing')
    if frag not in body:errors.append(label+' title missing')
    if not h.get('canonical') or norm_url(h['canonical'])!=norm_url(url):errors.append(label+' canonical mismatch')
    rob=h.get('robots','').lower()
    if 'noindex' in rob or 'index' not in rob or 'follow' not in rob:errors.append(label+' index/follow failed')
    if 'BlogPosting' not in body:errors.append(label+' BlogPosting missing')
    if re.search(r'"@type"\s*:\s*"Product"',body,re.I):errors.append(label+' accidental Product schema')
    if body.count('<h2>')<10:errors.append(label+' H2 structure thin')
if a5 not in pages.get('A4',(0,{},''))[2]:errors.append('A4->A5 link missing')
if a4 not in pages.get('A5',(0,{},''))[2]:errors.append('A5->A4 link missing')
if linen_cat not in pages.get('A4',(0,{},''))[2] or linen_cat not in pages.get('A5',(0,{},''))[2]:errors.append('linen commerce link missing')

s2,r2,f2,_=get(a2+'?t='+str(int(time.time())),True,150);b2=r2.decode('utf-8','replace');print('LIVE_A2_BRIDGE',s2,f2,'A4',a4 in b2,'A5',a5 in b2)
if s2!=200 or a4 not in b2 or a5 not in b2 or 'data-g1-cluster-wave="45"' not in b2:errors.append('A2 cross-cluster bridge missing')

bs,braw,bf,_=get(blog+'?t='+str(int(time.time())),True,150);bh=head(braw);bb=braw.decode('utf-8','replace');print('LIVE_BLOG',bs,bf,json.dumps(bh,ensure_ascii=False,separators=(',',':')))
if bs!=200 or not all(x in bb for x in ('تیشرت باکسی','انتخاب سایز تیشرت باکسی','تفاوت شلوار بگ','پارچه لینن چیست','شست‌وشوی پیراهن لینن')):errors.append('blog archive incomplete')
if 'noindex' in bh.get('robots','').lower() or not bh.get('canonical'):errors.append('blog indexability failed')

for label,url,need in [('FABRIC',fabric,['پارچه لینن چیست','شست‌وشوی پیراهن لینن']),('FIT',fit,['تیشرت باکسی','تفاوت شلوار بگ'])]:
    cs,craw,cf,_=get(url+'?t='+str(int(time.time())),True,150);ch=head(craw);cb=craw.decode('utf-8','replace');print('LIVE_CAT_'+label,cs,cf,json.dumps(ch,ensure_ascii=False,separators=(',',':')))
    if cs!=200 or not all(x in cb for x in need):errors.append(label+' category content failed')
    if 'noindex' in ch.get('robots','').lower() or not ch.get('canonical'):errors.append(label+' category indexability failed')
for slug in ('style-guide','buying-guide'):
    es,eraw,ef,_=get(BASE+'/category/'+slug+'/?t='+str(int(time.time())),True,120);eh=head(eraw);print('EMPTY_CATEGORY',slug,es,ef,json.dumps(eh,ensure_ascii=False,separators=(',',':')))
    if es!=200 or 'noindex' not in eh.get('robots','').lower():errors.append(slug+' should remain noindex')

ss,post_locs=sitemap_locs('post-sitemap.xml');print('POST_SITEMAP',ss,len(post_locs),json.dumps(post_locs,ensure_ascii=False));pn={norm_url(x) for x in post_locs}
if ss!=200 or not all(norm_url(x) in pn for x in (a4,a5)):errors.append('post sitemap missing new article')
ss,cat_locs=sitemap_locs('category-sitemap.xml');print('CATEGORY_SITEMAP',ss,len(cat_locs),json.dumps(cat_locs,ensure_ascii=False));cn={norm_url(x) for x in cat_locs}
if ss!=200 or norm_url(fabric) not in cn or norm_url(fit) not in cn:errors.append('category sitemap missing active category')
for slug in ('style-guide','buying-guide'):
    if any('/category/'+slug+'/' in x for x in cat_locs):errors.append(slug+' unexpectedly in category sitemap')
ps1,product_locs_after=sitemap_locs('product-sitemap.xml');product_locs_after=sorted(product_locs_after);print('PRODUCT_SITEMAP_POST',ps1,len(product_locs_after),hashlib.sha256('\n'.join(product_locs_after).encode()).hexdigest())
if ps1!=200 or product_locs_after!=product_locs_before:errors.append('product sitemap changed')
post_hash={f:hashlib.sha256(read_theme(f).encode()).hexdigest() for f in protected};print('PROTECTED_POST',json.dumps(post_hash,ensure_ascii=False,sort_keys=True))
if post_hash!=pre_hash:errors.append('protected UI files changed')

if errors:
    print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));rb='gramiss-editorial-wave-4-5-rollback-'+nonce+'.php'
    rollback=r'''<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);foreach([sanitize_title('پارچه لینن چیست'),sanitize_title('شستشوی پیراهن لینن مردانه')] as $s){$p=get_page_by_path($s,OBJECT,'post');if($p)wp_delete_post($p->ID,true);}$a2=get_post(459);if($a2&&strpos($a2->post_content,'data-g1-cluster-wave="45"')!==false){$c=preg_replace('/\s*<div data-g1-cluster-wave="45">.*?<\/div>\s*$/s','',$a2->post_content,1);wp_update_post(wp_slash(['ID'=>$a2->ID,'post_content'=>$c]));}if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo 'ROLLED_BACK';?>'''
    save_public(rb,rollback);rs,rr,_,_=get(BASE+'/'+rb+'?t='+str(int(time.time())),True,180);print('ROLLBACK',rs,rr[:100]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS EDITORIAL WAVE 4-5');print('ARTICLE_04',a4);print('ARTICLE_05',a5);print('FABRIC_CATEGORY',fabric);print('LINEN_COMMERCE',linen_cat);print('HOME_SHA_PRESERVED',post_hash['front-page.php'])
