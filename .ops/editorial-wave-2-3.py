import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']
root=os.environ['THEME_ROOT'].strip('/'); healthy=os.environ.get('HEALTHY_HOME_SHA','')
ctx=ssl._create_unverified_context()
BASE='https://gramiss.ir'

def call(fn,p,post=False):
    u=f'https://{host}:2083/execute/Fileman/{fn}'
    d=urllib.parse.urlencode(p).encode()
    last=None
    for attempt in range(1,5):
        try:
            req=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET')
            req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as z:
                o=json.loads(z.read().decode('utf-8','replace'))
            q=o.get('result') if isinstance(o.get('result'),dict) else o
            if not isinstance(q,dict) or q.get('status')!=1: raise RuntimeError(str(q))
            return q.get('data')
        except Exception as exc:
            last=exc; print('API_RETRY',fn,attempt,exc)
            if attempt<4: time.sleep(attempt*2)
    raise last

def read_theme(rel):
    p,n=rel.rsplit('/',1) if '/' in rel else ('',rel)
    d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str): return d[k]
    return d if isinstance(d,str) else ''

def save_public(n,c):
    return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def get(u,follow=True,timeout=180):
    class NR(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl): return None
    req=urllib.request.Request(u,headers={'User-Agent':'GramissEditorialWave23/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    hs=[urllib.request.HTTPSHandler(context=ctx)]
    if not follow: hs.insert(0,NR())
    op=urllib.request.build_opener(*hs)
    try:
        with op.open(req,timeout=timeout) as z: return z.status,z.read(),z.geturl(),dict(z.headers)
    except urllib.error.HTTPError as e:
        return e.code,e.read(),u,dict(e.headers)

def hval(raw,p):
    m=re.search(p,raw,re.I|re.S)
    return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''

def head(raw):
    t=raw.decode('utf-8','replace').split('</head>',1)[0]
    return {
        'title':hval(t,r'<title[^>]*>(.*?)</title>'),
        'description':hval(t,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),
        'canonical':hval(t,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),
        'robots':hval(t,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')
    }

def norm_url(u): return urllib.parse.unquote(u).rstrip('/')+'/'
def sitemap_locs(path):
    s,raw,_,_=get(BASE+'/'+path+'?t='+str(int(time.time())),True,120)
    txt=raw.decode('utf-8','replace')
    return s,[re.sub(r'&amp;','&',x) for x in re.findall(r'<loc>(.*?)</loc>',txt,re.I)]

protected=['front-page.php','template-parts/home-looks.php','assets/css/home-looks.css','assets/js/home-looks.js']
pre_hash={f:hashlib.sha256(read_theme(f).encode()).hexdigest() for f in protected}
print('PROTECTED_PRE',json.dumps(pre_hash,ensure_ascii=False,sort_keys=True))
if healthy and pre_hash['front-page.php']!=healthy: raise SystemExit('ABORT Home mismatch')
for f,m in [('home.php','g1-editorial-index'),('single.php','g1-editorial-single'),('category.php','g1-editorial-category'),('assets/css/editorial-v1.css','GRAMISS_EDITORIAL_V1')]:
    if m not in read_theme(f): raise SystemExit('ABORT editorial foundation missing '+f)

ps0,product_locs_before=sitemap_locs('product-sitemap.xml')
if ps0!=200: raise SystemExit('ABORT product sitemap preflight')
product_locs_before=sorted(product_locs_before)
print('PRODUCT_SITEMAP_PRE',len(product_locs_before),hashlib.sha256('\n'.join(product_locs_before).encode()).hexdigest())

nonce=hashlib.sha256((str(time.time())+pre_hash['front-page.php']).encode()).hexdigest()[:14]
name='gramiss-editorial-wave-2-3-'+nonce+'.php'

php=r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES',false);
require __DIR__.'/wp-load.php';
@unlink(__FILE__);

$slug1='تیشرت-باکسی-چیست-تفاوت-با-اورسایز';
$slug2='انتخاب-سایز-تیشرت-باکسی-مردانه';
$slug3='تفاوت-شلوار-بگ-نیم-بگ-فول-بگ';

$a1=get_page_by_path($slug1,OBJECT,'post');
$a2_existing=get_page_by_path($slug2,OBJECT,'post');
$a3_existing=get_page_by_path($slug3,OBJECT,'post');
$cat=get_term_by('slug','fit-size-guide','category');
$blog=get_post(22);
$published=(int)wp_count_posts('post')->publish;

if(!$a1 || $a1->post_status!=='publish' || $a2_existing || $a3_existing || !$cat || !$blog || $blog->post_title!=='مجله Gramiss' || $published!==1){
    http_response_code(409);
    echo wp_json_encode(['error'=>'baseline drift','a1'=>$a1?[$a1->ID,$a1->post_status]:null,'a2'=>$a2_existing?$a2_existing->ID:null,'a3'=>$a3_existing?$a3_existing->ID:null,'cat'=>$cat?$cat->term_id:null,'blog'=>$blog?$blog->post_title:null,'published'=>$published],JSON_UNESCAPED_UNICODE);
    exit;
}
if(strpos($a1->post_content,'data-g1-cluster-wave="23"')!==false){http_response_code(409);echo wp_json_encode(['error'=>'article 1 cluster marker already exists']);exit;}

$tshirt=get_term_by('slug','tshirt','product_cat');
$pants=get_term_by('slug','pants','product_cat');
if(!$tshirt || !$pants){http_response_code(409);echo wp_json_encode(['error'=>'commerce taxonomy drift','tshirt'=>$tshirt?$tshirt->term_id:null,'pants'=>$pants?$pants->term_id:null]);exit;}
$tshirt_url=get_term_link($tshirt);$pants_url=get_term_link($pants);
if(is_wp_error($tshirt_url) || is_wp_error($pants_url)){http_response_code(409);echo wp_json_encode(['error'=>'commerce category url error']);exit;}
$a1_url=get_permalink($a1);

$content2=<<<'HTML'
<p>برای انتخاب سایز تیشرت باکسی، فقط نگاه‌کردن به حرف S، M یا L کافی نیست. چیزی که در نهایت روی بدن می‌بینی حاصل نسبت چند اندازه به یکدیگر است: عرض سینه، قد لباس، جای سرشانه و طول آستین. به همین دلیل ممکن است دو تیشرت با یک سایز اسمی، یکی دقیقاً همان فرم باکسی دلخواهت را بسازد و دیگری بیش از حد بلند یا تنگ دیده شود.</p>
<p>این راهنما کمک می‌کند قبل از خرید، اندازه‌های مهم را از یک لباس مرجع برداری، جدول سایز محصول را درست بخوانی و بین دو سایز تصمیم منطقی‌تری بگیری. اگر هنوز درباره خود فرم باکسی و فرق آن با اورسایز مطمئن نیستی، ابتدا <a href="A1_URL">راهنمای تیشرت باکسی و تفاوت آن با اورسایز</a> را ببین.</p>
<h2>چرا سایز روی لیبل به‌تنهایی کافی نیست؟</h2>
<p>سایز اسمی یک قرارداد داخلی برای هر برند یا حتی هر مدل است و الزاماً به معنی ابعاد یکسان نیست. الگو، نوع پارچه، میزان افت سرشانه و هدف طراحی می‌توانند باعث شوند دو لباس با برچسب L ابعاد متفاوتی داشته باشند. در تیشرت باکسی این موضوع مهم‌تر است، چون نسبت عرض به قد بخش اصلی ظاهر لباس را می‌سازد.</p>
<p>پس به‌جای این سؤال که «من همیشه L می‌پوشم، همین L را بگیرم؟» بهتر است بپرسی «L این مدل چند سانتی‌متر عرض و قد دارد و نسبتش به تیشرتی که تنخورش را دوست دارم چطور است؟»</p>
<h2>چهار اندازه مهم برای انتخاب سایز تیشرت باکسی</h2>
<ul><li><strong>عرض سینه:</strong> فاصله افقی زیر بغل تا زیر بغل روی لباس پهن‌شده. این اندازه بیشترین اثر را روی آزادی تنه دارد.</li><li><strong>قد لباس:</strong> از بالاترین نقطه شانه تا لبه پایین. در فرم باکسی، قد کنترل‌شده کمک می‌کند لباس فقط «بزرگ» به نظر نرسد.</li><li><strong>عرض سرشانه:</strong> فاصله دو انتهای خط شانه. با این عدد می‌توانی بفهمی سرشانه تقریباً در جای طبیعی می‌ایستد یا افت بیشتری دارد.</li><li><strong>طول آستین:</strong> از درز شانه تا انتهای آستین. وقتی آستین حجیم‌تر است، چند سانتی‌متر اختلاف می‌تواند حس کلی فیت را عوض کند.</li></ul>
<p>هیچ‌کدام از این چهار عدد به‌تنهایی تصمیم نهایی را نمی‌سازد. نسبت آن‌ها به یکدیگر و مقایسه با لباس مرجع مهم‌تر است.</p>
<h2>روش درست اندازه‌گیری یک تیشرت مرجع</h2>
<ol><li>تیشرتی را انتخاب کن که فرم آن را روی بدنت دوست داری؛ ترجیحاً لباسی که چند بار پوشیده و شسته شده و شکل واقعی خودش را پیدا کرده است.</li><li>آن را بدون کشیدن پارچه روی سطح صاف پهن کن و چین‌های بزرگ را با دست مرتب کن.</li><li>عرض سینه را خط مستقیم از زیر یک بغل تا زیر بغل دیگر بگیر.</li><li>قد را از بالاترین نقطه نزدیک یقه روی شانه تا پایین لباس اندازه بگیر.</li><li>عرض شانه و طول آستین را هم با همان روش ثابت ثبت کن.</li><li>اعداد را یادداشت کن و بعد سراغ جدول سایز محصول برو؛ حافظه چشمی برای اختلاف‌های کوچک قابل اتکا نیست.</li></ol>
<p>اگر فروشگاه اندازه لباس را به‌صورت «نیم‌دور» اعلام کرده باشد، عرض سینه همان اندازه تخت است. اگر دور کامل اعلام شده باشد، شیوه مقایسه فرق می‌کند؛ بنابراین عنوان ستون جدول را دقیق بخوان.</p>
<h2>چطور جدول سایز را با لباس مرجع مقایسه کنیم؟</h2>
<p>اول عرض سینه را مقایسه کن، چون معمولاً بیشترین اثر را بر آزادی تنه دارد. بعد قد را ببین تا مشخص شود لبه پایین لباس تقریباً در محدوده‌ای قرار می‌گیرد که می‌خواهی. در مرحله بعد سرشانه و آستین را بررسی کن تا حجم بالاتنه بیش از حد تغییر نکند.</p>
<p>لازم نیست اعداد محصول دقیقاً با لباس مرجع برابر باشند. اگر هدف تو فیت باکسی آزادتر است، ممکن است عرض بیشتر را بخواهی؛ اگر فرم جمع‌وجورتر مدنظر است، شاید عرض نزدیک‌تر و قد کنترل‌شده‌تر مناسب‌تر باشد. نکته این است که اختلاف را آگاهانه انتخاب کنی، نه تصادفی.</p>
<h2>اگر بین دو سایز هستیم کدام را انتخاب کنیم؟</h2>
<p>وقتی دو سایز هر دو قابل پوشیدن‌اند، اولویت را از روی ظاهر موردنظر تعیین کن. اگر آزادی تنه برایت مهم‌تر است، عرض سینه را معیار اول قرار بده. اگر قد لباس روی استایل تو حساس‌تر است، سایزی را انتخاب کن که قدش به لباس مرجع نزدیک‌تر است و بعد مطمئن شو عرض هنوز آزادی لازم را دارد.</p>
<p>همیشه بزرگ‌تر رفتن راه‌حل نیست. در بعضی الگوها با بالا رفتن سایز، هم عرض و هم قد و آستین زیاد می‌شوند و ممکن است فرم باکسی به یک ظاهر صرفاً بزرگ تبدیل شود. برعکس، کوچک‌تر رفتن فقط برای کوتاه‌کردن قد هم می‌تواند عرض و سرشانه را خراب کند.</p>
<h2>فیت باکسی جمع‌وجور و باکسی رها چه فرقی دارند؟</h2>
<p>باکسی جمع‌وجور معمولاً حجم عرضی مشخصی دارد اما قد و افت شانه کنترل‌شده‌تر دیده می‌شود. باکسی رها فضای بیشتری در تنه و آستین ایجاد می‌کند و ممکن است سرشانه افت بیشتری داشته باشد. هیچ‌کدام ذاتاً بهتر نیست؛ انتخاب به استایل و میزان آزادی موردنظر تو برمی‌گردد.</p>
<p>برای مقایسه مدل‌های موجود، بهتر است صفحه <a href="TSHIRT_URL">تیشرت‌های Gramiss</a> را بر اساس اندازه واقعی هر محصول بررسی کنی، نه فقط اسم فیت.</p>
<h2>قد تیشرت را چطور برای استایل خودمان بسنجیم؟</h2>
<p>به‌جای قانون‌های کلی درباره قد یا فرم بدن، نقطه‌ای را روی شلواری که معمولاً می‌پوشی مشخص کن که دوست داری لبه تیشرت نزدیک آن قرار بگیرد. بعد قد لباس مرجع را با آن نقطه تطبیق بده. این روش از توصیه‌های عمومی دقیق‌تر است، چون نسبت بالاتنه، فاق شلوار و نحوه ایستادن لباس را هم در عمل وارد تصمیم می‌کند.</p>
<p>اگر بیشتر شلوارهای فاق‌بلند یا آزاد می‌پوشی، ممکن است قد کنترل‌شده تیشرت ترکیب را متعادل‌تر نشان دهد. اگر شلوار راسته یا فاق پایین‌تر است، همان قد ممکن است حس دیگری ایجاد کند. این‌ها قانون ثابت نیستند؛ معیار، نسبت نهایی لباس‌ها روی خود توست.</p>
<h2>پارچه و شست‌وشو چه اثری روی انتخاب سایز دارند؟</h2>
<p>دو تیشرت با ابعاد یکسان می‌توانند به‌خاطر وزن، بافت و میزان افت پارچه متفاوت دیده شوند. پارچه ساختارمندتر فرم چهارگوش را واضح‌تر نگه می‌دارد و پارچه نرم‌تر بیشتر روی بدن می‌افتد. همچنین تغییر ابعاد بعد از شست‌وشو به جنس الیاف، ساخت پارچه و دستور مراقبت بستگی دارد؛ بنابراین نباید بدون اطلاعات محصول یک درصد ثابت برای آب‌رفت در نظر گرفت.</p>
<p>قبل از خرید، توضیحات محصول و راهنمای شست‌وشو را بخوان. اگر اطلاعات مشخصی درباره تغییر ابعاد وجود ندارد، سایز را بر اساس اندازه فعلی محصول انتخاب کن و از حدس‌زدن میزان آب‌رفت خودداری کن.</p>
<h2>اشتباهات رایج در انتخاب سایز تیشرت باکسی</h2>
<ul><li>انتخاب فقط بر اساس سایزی که در برند دیگری می‌پوشی.</li><li>توجه به عرض سینه و نادیده‌گرفتن قد لباس.</li><li>خرید چند سایز بزرگ‌تر برای ساختن فرم باکسی.</li><li>اندازه‌گیری بدن و مقایسه مستقیم آن با جدولی که اندازه خود لباس را نوشته است.</li><li>کشیدن پارچه هنگام اندازه‌گیری لباس مرجع.</li><li>نادیده‌گرفتن سرشانه و آستین وقتی بین دو سایز تصمیم می‌گیری.</li></ul>
<h2>چک‌لیست سریع قبل از خرید</h2>
<ul><li>یک تیشرت مرجع با تنخور مطلوب داری.</li><li>عرض سینه و قد آن را روی سطح صاف اندازه گرفته‌ای.</li><li>روش اندازه‌گیری جدول محصول را فهمیده‌ای.</li><li>می‌دانی ظاهر جمع‌وجورتر می‌خواهی یا رها‌تر.</li><li>در صورت دو دل بودن بین دو سایز، می‌دانی کدام اندازه برایت اولویت بیشتری دارد.</li><li>اطلاعات پارچه و مراقبت را جدا از حدس‌های عمومی بررسی کرده‌ای.</li></ul>
<h2>انتخاب سایز را با کل استایل ببین</h2>
<p>فیت تیشرت جدا از شلوار و کفش دیده نمی‌شود. اگر پایین‌تنه حجم زیادی دارد، کنترل قد و عرض تیشرت می‌تواند ترکیب را منظم‌تر کند. اگر شلوار جمع‌وجورتر است، آزادی بیشتر بالاتنه ممکن است همان تضادی باشد که می‌خواهی. برای تفاوت حجم شلوارها، <a href="A3_URL">راهنمای بگ، نیم‌بگ و فول‌بگ</a> را بخوان.</p>
<p><strong>جمع‌بندی:</strong> بهترین سایز تیشرت باکسی عددی نیست که از روی عادت انتخاب شود. یک لباس مرجع، چهار اندازه واقعی و مشخص‌کردن ظاهر مطلوب، تصمیم را بسیار قابل‌اعتمادتر می‌کند.</p>
HTML;

$content3=<<<'HTML'
<p>بگ، نیم‌بگ و فول‌بگ سه اسم برای سه سطح متفاوت از حجم و آزادی شلوارند، اما یک نکته مهم را باید از ابتدا در نظر گرفت: این نام‌ها استاندارد عددی واحد و جهانی ندارند. ممکن است چیزی که یک برند «بگ» می‌نامد، از نظر اندازه به «نیم‌بگ» برند دیگری نزدیک باشد. بنابراین اسم فیت نقطه شروع است، نه نتیجه نهایی.</p>
<p>برای انتخاب درست باید علاوه بر عنوان مدل، حجم ران و ساق، عرض دمپا، قد، فاق و رفتار پارچه را ببینی. در این راهنما تفاوت این سه فیت را به زبان کاربردی بررسی می‌کنیم تا بتوانی از روی فرم واقعی شلوار تصمیم بگیری.</p>
<h2>شلوار نیم‌بگ چیست؟</h2>
<p>نیم‌بگ معمولاً بین یک شلوار راسته آزاد و یک بگ پرحجم قرار می‌گیرد. در ران و ساق فضای بیشتری از فیت‌های معمولی دارد، اما حجم آن آن‌قدر زیاد نیست که تمام تمرکز استایل روی پایین‌تنه قرار بگیرد. به همین دلیل برای کسی که می‌خواهد از فیت‌های جذب فاصله بگیرد ولی هنوز با حجم خیلی زیاد راحت نیست، نقطه شروع قابل‌فهمی است.</p>
<p>فرم واقعی نیم‌بگ به الگو و پارچه بستگی دارد؛ پس برای خرید آنلاین به اندازه‌های محصول و عکس تنخور توجه کن، نه فقط واژه «نیم‌بگ».</p>
<h2>شلوار بگ چیست؟</h2>
<p>در فیت بگ، آزادی ران و ساق واضح‌تر است و خط شلوار معمولاً با فاصله بیشتری از پا پایین می‌آید. دمپا می‌تواند باز باشد و بسته به قد شلوار روی کفش کمی شکست ایجاد کند. بگ خوب قرار نیست صرفاً شلواری چند سایز بزرگ‌تر باشد؛ کمر و فاق باید مطابق الگو بنشینند و حجم اضافه از طراحی خود شلوار بیاید.</p>
<p>اگر بالاتنه هم آزاد است، نسبت قد تیشرت یا پیراهن با حجم شلوار اهمیت بیشتری پیدا می‌کند. برای فهم دقیق‌تر فرم بالاتنه می‌توانی <a href="A1_URL">تفاوت تیشرت باکسی و اورسایز</a> را ببینی.</p>
<h2>فول‌بگ چه تفاوتی با بگ دارد؟</h2>
<p>فول‌بگ معمولاً بیشترین حجم را در این طیف دارد. فضای ران، ساق و دمپا برجسته‌تر است و پارچه نقش بزرگی در شکل نهایی آن بازی می‌کند. پارچه ریزشی می‌تواند حجم زیاد را نرم و روان نشان دهد، در حالی که پارچه ساختارمند همان حجم را هندسی‌تر و واضح‌تر نمایش می‌دهد.</p>
<p>فول‌بگ به معنی «هرچه بزرگ‌تر بهتر» نیست. اگر کمر، فاق یا طول شلوار با الگو هماهنگ نباشد، افزایش سایز می‌تواند فقط تناسب را به هم بزند. بهتر است مدل فول‌بگ واقعی را در سایز درست خودش انتخاب کنی.</p>
<h2>مقایسه سریع نیم‌بگ، بگ و فول‌بگ</h2>
<table><thead><tr><th>ویژگی</th><th>نیم‌بگ</th><th>بگ</th><th>فول‌بگ</th></tr></thead><tbody><tr><td>حجم کلی</td><td>متوسط</td><td>زیاد</td><td>بیشترین حجم در این طیف</td></tr><tr><td>فاصله از پا</td><td>آزاد اما کنترل‌شده</td><td>واضح و رها</td><td>بسیار رها و پرحجم</td></tr><tr><td>نقش پارچه</td><td>مهم</td><td>خیلی مهم</td><td>تعیین‌کننده در افت و حجم</td></tr><tr><td>حس استایل</td><td>متعادل‌تر</td><td>آزاد و معاصر</td><td>بیانی‌تر و حجیم‌تر</td></tr></tbody></table>
<p>این جدول برای فهم تفاوت نسبی است، نه تعیین سایز. برای هر محصول باید اندازه واقعی همان مدل را بررسی کنی.</p>
<h2>برای تشخیص فیت واقعی چه اندازه‌هایی را بررسی کنیم؟</h2>
<ul><li><strong>عرض ران:</strong> نشان می‌دهد حجم اصلی شلوار از بالای پا چقدر است.</li><li><strong>عرض دمپا:</strong> روی شکل پایین شلوار و نحوه قرارگرفتن روی کفش اثر مستقیم دارد.</li><li><strong>فاق:</strong> محل قرارگیری کمر و حجم بخش بالایی شلوار را تغییر می‌دهد.</li><li><strong>قد شلوار:</strong> تعیین می‌کند پایین شلوار صاف بایستد، روی کفش بشکند یا بیش از حد جمع شود.</li><li><strong>کمر:</strong> باید مطابق سیستم سایزبندی همان محصول سنجیده شود؛ حجم بگ نباید از انتخاب کمر اشتباه ساخته شود.</li></ul>
<h2>پارچه چرا در شلوارهای آزاد مهم‌تر می‌شود؟</h2>
<p>هرچه حجم الگو بیشتر شود، رفتار پارچه بیشتر دیده می‌شود. یک پارچه سبک و ریزشی ممکن است در حرکت موج ایجاد کند و خطوط شلوار نرم‌تر باشند. پارچه خشک‌تر یا ضخیم‌تر حجم را نگه می‌دارد و سیلوئت مشخص‌تری می‌سازد. بنابراین دو شلوار با عرض ران و دمپای نزدیک می‌توانند به‌دلیل جنس و ساخت پارچه، روی بدن کاملاً متفاوت دیده شوند.</p>
<p>هنگام مقایسه محصولات، عکس تنخور و توضیحات جنس پارچه را کنار اندازه‌ها ببین. فقط از روی عدد دمپا نمی‌توان افت واقعی لباس را پیش‌بینی کرد.</p>
<h2>قد و شکست شلوار روی کفش</h2>
<p>در فیت‌های بگ و فول‌بگ، قد شلوار بخش مهمی از ظاهر است. بعضی ترکیب‌ها با یک شکست ملایم روی کفش تمیزتر دیده می‌شوند و بعضی مدل‌ها عمداً حجم بیشتری نزدیک دمپا دارند. اگر قد بیش از حد باشد، تجمع پارچه می‌تواند شکل اصلی الگو را پنهان کند؛ اگر خیلی کوتاه باشد، شلوار ممکن است آن حس رها را از دست بدهد.</p>
<p>بهترین مرجع، شلواری است که محل قرارگیری دمپای آن را دوست داری. قد آن را روی سطح صاف اندازه بگیر و با جدول محصول مقایسه کن.</p>
<h2>کدام فیت برای استایل من مناسب‌تر است؟</h2>
<p>به‌جای قانون‌های محدودکننده درباره قد یا فرم بدن، از میزان حجمی که در استایل می‌خواهی شروع کن. اگر تغییر آرام از شلوارهای معمولی می‌خواهی، نیم‌بگ معمولاً حجم کنترل‌شده‌تری می‌دهد. اگر پایین‌تنه آزاد و مشخص می‌خواهی، بگ انتخاب واضح‌تری است. اگر هدف اصلی استایل یک سیلوئت پرحجم و رهاست، فول‌بگ همان جهت را پررنگ‌تر می‌کند.</p>
<p>بعد بالاتنه را با آن هماهنگ کن. تیشرت باکسی می‌تواند با هر سه فیت کار کند، اما عرض و قد آن باید در کنار حجم شلوار سنجیده شود. اگر برای تیشرت بین دو سایز مرددی، <a href="A2_URL">راهنمای انتخاب سایز تیشرت باکسی</a> به تصمیم دقیق‌تر کمک می‌کند.</p>
<h2>کفش چه نقشی در انتخاب بگ و فول‌بگ دارد؟</h2>
<p>عرض دمپا و قد شلوار باید با حجمی که کفش در پایین استایل می‌سازد هماهنگ باشد. کفش کم‌حجم ممکن است زیر دمپای خیلی باز کمتر دیده شود، در حالی که یک کتانی حجیم‌تر حضور بیشتری ایجاد می‌کند. این موضوع به معنی درست یا غلط بودن هیچ‌کدام نیست؛ فقط باید از قبل بدانیم چه نسبتی می‌خواهیم.</p>
<p>در خرید آنلاین، به عکس‌های تمام‌قد و نمای کنار توجه کن تا ببینی دمپا کجا و با چه مقدار شکست روی کفش قرار گرفته است.</p>
<h2>اشتباهات رایج هنگام انتخاب شلوار آزاد</h2>
<ul><li>خرید چند سایز بزرگ‌تر از یک شلوار معمولی به امید تبدیل‌شدن آن به بگ.</li><li>تصمیم فقط بر اساس اسم «بگ» یا «فول‌بگ» بدون دیدن اندازه‌ها.</li><li>نادیده‌گرفتن فاق و تمرکز فقط روی دمپا.</li><li>مقایسه دو مدل با پارچه‌های متفاوت فقط از روی یک عدد.</li><li>انتخاب قد بدون درنظرگرفتن کفشی که معمولاً با شلوار پوشیده می‌شود.</li><li>فرض اینکه یک نوع فیت برای همه موقعیت‌ها یا همه استایل‌ها بهترین است.</li></ul>
<h2>چک‌لیست خرید بگ، نیم‌بگ یا فول‌بگ</h2>
<ul><li>سطح حجم موردنظر را مشخص کرده‌ای.</li><li>عرض ران و دمپا را با شلوار مرجع مقایسه کرده‌ای.</li><li>فاق و قد را جداگانه بررسی کرده‌ای.</li><li>رفتار پارچه را از توضیحات و عکس تنخور سنجیده‌ای.</li><li>می‌دانی دمپا قرار است روی چه نوع کفشی بنشیند.</li><li>سایز کمر را برای ایجاد حجم عمداً بزرگ‌تر انتخاب نکرده‌ای.</li></ul>
<p>برای دیدن مدل‌های فعلی می‌توانی صفحه <a href="PANTS_URL">شلوارهای Gramiss</a> را بررسی کنی و اندازه هر مدل را جداگانه با شلوار مرجع خودت مقایسه کنی.</p>
<p><strong>جمع‌بندی:</strong> نیم‌بگ، بگ و فول‌بگ را بهتر است یک طیف حجم ببینی، نه سه استاندارد عددی ثابت. نام فیت جهت کلی را می‌گوید؛ انتخاب واقعی را اندازه‌ها، پارچه، قد و نسبت آن با بقیه استایل مشخص می‌کنند.</p>
HTML;

$content2=str_replace(['A1_URL','A3_URL','TSHIRT_URL'],[esc_url($a1_url),'__A3__',esc_url($tshirt_url)],$content2);
$content3=str_replace(['A1_URL','A2_URL','PANTS_URL'],[esc_url($a1_url),'__A2__',esc_url($pants_url)],$content3);

$a2=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای انتخاب سایز تیشرت باکسی مردانه؛ اندازه‌گیری و فیت مناسب','post_name'=>$slug2,'post_excerpt'=>'برای انتخاب سایز تیشرت باکسی، اندازه‌های واقعی لباس را با یک تیشرت مرجع مقایسه کن و به عرض، قد، سرشانه و آستین توجه داشته باش.','post_content'=>$content2,'post_category'=>[(int)$cat->term_id],'post_author'=>1]),true);
if(is_wp_error($a2)){http_response_code(500);echo wp_json_encode(['error'=>'article2 insert','message'=>$a2->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a2_url=get_permalink($a2);
$content3=str_replace('__A2__',esc_url($a2_url),$content3);
$a3=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ کدام فیت مناسب شماست؟','post_name'=>$slug3,'post_excerpt'=>'تفاوت نیم‌بگ، بگ و فول‌بگ را از روی حجم، اندازه‌های واقعی، افت پارچه و نحوه قرارگرفتن روی کفش مقایسه کن و فیت مناسب‌تری انتخاب کن.','post_content'=>$content3,'post_category'=>[(int)$cat->term_id],'post_author'=>1]),true);
if(is_wp_error($a3)){wp_delete_post($a2,true);http_response_code(500);echo wp_json_encode(['error'=>'article3 insert','message'=>$a3->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a3_url=get_permalink($a3);
$c2=get_post_field('post_content',$a2);$c2=str_replace('__A3__',esc_url($a3_url),$c2);$r2=wp_update_post(wp_slash(['ID'=>$a2,'post_content'=>$c2]),true);
if(is_wp_error($r2)){wp_delete_post($a3,true);wp_delete_post($a2,true);http_response_code(500);echo wp_json_encode(['error'=>'article2 reciprocal link update']);exit;}

$meta=[$a2=>['rank_math_title'=>'راهنمای انتخاب سایز تیشرت باکسی مردانه','rank_math_description'=>'برای انتخاب سایز تیشرت باکسی، عرض سینه، قد، سرشانه و آستین را درست اندازه بگیرید و با جدول سایز مقایسه کنید تا فیت مناسب‌تری پیدا کنید.','rank_math_focus_keyword'=>'انتخاب سایز تیشرت باکسی'],$a3=>['rank_math_title'=>'تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ راهنمای فیت','rank_math_description'=>'تفاوت شلوار بگ، نیم‌بگ و فول‌بگ را از نظر حجم، افت پارچه و استایل بشناسید و ببینید کدام فیت برای ترکیب لباس شما مناسب‌تر است.','rank_math_focus_keyword'=>'تفاوت شلوار بگ نیم بگ و فول بگ']];
foreach($meta as $id=>$mm){foreach($mm as $k=>$v)update_post_meta($id,$k,$v);update_post_meta($id,'rank_math_robots',['index','follow']);update_post_meta($id,'rank_math_rich_snippet','article');update_post_meta($id,'rank_math_snippet_article_type','BlogPosting');}

$cluster='<div data-g1-cluster-wave="23"><h2>راهنماهای بعدی برای انتخاب فیت</h2><p>اگر فرم باکسی را شناختی، قدم بعدی این است که <a href="'.esc_url($a2_url).'">سایز تیشرت باکسی را با اندازه واقعی انتخاب کنی</a>. برای هماهنگ‌کردن حجم پایین‌تنه هم <a href="'.esc_url($a3_url).'">تفاوت شلوار بگ، نیم‌بگ و فول‌بگ</a> را ببین.</p></div>';
$u1=wp_update_post(wp_slash(['ID'=>$a1->ID,'post_content'=>$a1->post_content."\n".$cluster]),true);
if(is_wp_error($u1)){wp_delete_post($a3,true);wp_delete_post($a2,true);http_response_code(500);echo wp_json_encode(['error'=>'article1 reciprocal link update']);exit;}

delete_post_meta(22,'rank_math_robots');
foreach(['style-guide','buying-guide','fit-size-guide','fabric-care'] as $cs){$term=get_term_by('slug',$cs,'category');if($term && (int)$term->count>0)delete_term_meta($term->term_id,'rank_math_robots');}
if(class_exists('RankMath\\Sitemap\\Cache')) \RankMath\Sitemap\Cache::invalidate_storage();
global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
$out=['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'category'=>['id'=>(int)$cat->term_id,'count'=>(int)get_term($cat->term_id)->count,'url'=>get_term_link($cat)],'blog_url'=>get_permalink(22),'a1'=>['id'=>(int)$a1->ID,'url'=>get_permalink($a1->ID)],'a2'=>['id'=>(int)$a2,'url'=>get_permalink($a2),'title'=>get_the_title($a2),'focus'=>get_post_meta($a2,'rank_math_focus_keyword',true),'seo_title'=>get_post_meta($a2,'rank_math_title',true),'seo_desc'=>get_post_meta($a2,'rank_math_description',true),'robots'=>get_post_meta($a2,'rank_math_robots',true),'schema'=>get_post_meta($a2,'rank_math_snippet_article_type',true)],'a3'=>['id'=>(int)$a3,'url'=>get_permalink($a3),'title'=>get_the_title($a3),'focus'=>get_post_meta($a3,'rank_math_focus_keyword',true),'seo_title'=>get_post_meta($a3,'rank_math_title',true),'seo_desc'=>get_post_meta($a3,'rank_math_description',true),'robots'=>get_post_meta($a3,'rank_math_robots',true),'schema'=>get_post_meta($a3,'rank_math_snippet_article_type',true)]];
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''

save_public(name,php)
s,b,_,_=get(BASE+'/'+name+'?t='+str(int(time.time())),True,240)
print('WRITE',s,b.decode('utf-8','replace'))
if s!=200: raise SystemExit('article 02/03 write failed')
d=json.loads(b.decode('utf-8','replace'))
a1=d['a1']['url']; a2=d['a2']['url']; a3=d['a3']['url']; caturl=d['category']['url']; blogurl=d['blog_url']
errors=[]
if d.get('published')!=3: errors.append('published post count is not 3')
for key,focus in [('a2','انتخاب سایز تیشرت باکسی'),('a3','تفاوت شلوار بگ نیم بگ و فول بگ')]:
    row=d[key]
    if row.get('focus')!=focus: errors.append(key+' focus keyword db mismatch')
    if row.get('schema')!='BlogPosting': errors.append(key+' schema db mismatch')
    if 'index' not in row.get('robots',[]) or 'follow' not in row.get('robots',[]): errors.append(key+' robots db mismatch')

pages={}
for label,url,title_frag in [('A1',a1,'تیشرت باکسی'),('A2',a2,'انتخاب سایز تیشرت باکسی'),('A3',a3,'تفاوت شلوار بگ')]:
    st,raw,final,_=get(url+'?t='+str(int(time.time())),True,150)
    h=head(raw); body=raw.decode('utf-8','replace'); pages[label]=(st,h,body,final)
    print('LIVE_'+label,st,final,json.dumps(h,ensure_ascii=False,separators=(',',':')),'LEN',len(body),'H2',body.count('<h2>'),'BLOGPOSTING',('BlogPosting' in body))
    if st!=200: errors.append(label+' not 200'); continue
    if 'g1-editorial-single' not in body: errors.append(label+' editorial template missing')
    if title_frag not in body: errors.append(label+' title/H1 missing')
    if not h.get('canonical') or norm_url(h['canonical'])!=norm_url(url): errors.append(label+' canonical mismatch')
    if 'noindex' in h.get('robots','').lower() or 'index' not in h.get('robots','').lower(): errors.append(label+' not index')
    if 'follow' not in h.get('robots','').lower(): errors.append(label+' not follow')
    if 'BlogPosting' not in body: errors.append(label+' BlogPosting missing')
    if re.search(r'"@type"\s*:\s*"Product"',body,re.I): errors.append(label+' accidental Product schema')
    if label in ('A2','A3') and len(body)<8000: errors.append(label+' content unexpectedly thin')

if a2 not in pages['A1'][2]: errors.append('A1->A2 link missing')
if a3 not in pages['A1'][2]: errors.append('A1->A3 link missing')
for src,dst,label in [('A2',a1,'A2->A1'),('A2',a3,'A2->A3'),('A3',a1,'A3->A1'),('A3',a2,'A3->A2')]:
    if dst not in pages[src][2]: errors.append(label+' link missing')

bs,braw,bf,_=get(blogurl+'?t='+str(int(time.time())),True,150); bh=head(braw); bb=braw.decode('utf-8','replace')
print('LIVE_BLOG',bs,bf,json.dumps(bh,ensure_ascii=False,separators=(',',':')))
if bs!=200 or any(x not in bb for x in ('تیشرت باکسی','انتخاب سایز تیشرت باکسی','تفاوت شلوار بگ')): errors.append('blog cards incomplete')
if 'noindex' in bh.get('robots','').lower() or not bh.get('canonical'): errors.append('blog indexability failed')

cs,craw,cf,_=get(caturl+'?t='+str(int(time.time())),True,150); ch=head(craw); cb=craw.decode('utf-8','replace')
print('LIVE_CATEGORY',cs,cf,json.dumps(ch,ensure_ascii=False,separators=(',',':')))
if cs!=200 or any(x not in cb for x in ('تیشرت باکسی','انتخاب سایز تیشرت باکسی','تفاوت شلوار بگ')): errors.append('fit category incomplete')
if 'noindex' in ch.get('robots','').lower() or not ch.get('canonical'): errors.append('fit category indexability failed')

for slug in ('style-guide','buying-guide','fabric-care'):
    u=BASE+'/category/'+slug+'/'
    es,eraw,ef,_=get(u+'?t='+str(int(time.time())),True,120); eh=head(eraw)
    print('EMPTY_CATEGORY',slug,es,ef,json.dumps(eh,ensure_ascii=False,separators=(',',':')))
    if es!=200 or 'noindex' not in eh.get('robots','').lower(): errors.append(slug+' should remain noindex')

ss,post_locs=sitemap_locs('post-sitemap.xml'); print('POST_SITEMAP',ss,len(post_locs),json.dumps(post_locs,ensure_ascii=False))
post_norm={norm_url(y) for y in post_locs}
if ss!=200 or not all(norm_url(x) in post_norm for x in (a1,a2,a3)): errors.append('post sitemap missing article')
ss,cat_locs=sitemap_locs('category-sitemap.xml'); print('CATEGORY_SITEMAP',ss,len(cat_locs),json.dumps(cat_locs,ensure_ascii=False))
cat_norm={norm_url(y) for y in cat_locs}
if ss!=200 or norm_url(caturl) not in cat_norm: errors.append('category sitemap missing fit category')
for slug in ('style-guide','buying-guide','fabric-care'):
    if any('/category/'+slug+'/' in x for x in cat_locs): errors.append(slug+' unexpectedly in category sitemap')

ps1,product_locs_after=sitemap_locs('product-sitemap.xml'); product_locs_after=sorted(product_locs_after)
print('PRODUCT_SITEMAP_POST',ps1,len(product_locs_after),hashlib.sha256('\n'.join(product_locs_after).encode()).hexdigest())
if ps1!=200 or product_locs_after!=product_locs_before: errors.append('product sitemap changed')
post_hash={f:hashlib.sha256(read_theme(f).encode()).hexdigest() for f in protected}
print('PROTECTED_POST',json.dumps(post_hash,ensure_ascii=False,sort_keys=True))
if post_hash!=pre_hash: errors.append('protected UI files changed')

if errors:
    print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False))
    rb='gramiss-editorial-wave-2-3-rollback-'+nonce+'.php'
    rollback=r'''<?php
define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$slug1='تیشرت-باکسی-چیست-تفاوت-با-اورسایز';$slug2='انتخاب-سایز-تیشرت-باکسی-مردانه';$slug3='تفاوت-شلوار-بگ-نیم-بگ-فول-بگ';
foreach([$slug2,$slug3] as $s){$p=get_page_by_path($s,OBJECT,'post');if($p)wp_delete_post($p->ID,true);}
$a1=get_page_by_path($slug1,OBJECT,'post');
if($a1 && strpos($a1->post_content,'data-g1-cluster-wave="23"')!==false){$c=preg_replace('/\s*<div data-g1-cluster-wave="23">.*?<\/div>\s*$/s','',$a1->post_content,1);wp_update_post(wp_slash(['ID'=>$a1->ID,'post_content'=>$c]));}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo 'ROLLED_BACK';
?>'''
    save_public(rb,rollback)
    rs,rr,_,_=get(BASE+'/'+rb+'?t='+str(int(time.time())),True,180)
    print('ROLLBACK',rs,rr[:100])
    raise SystemExit('ROLLED BACK: '+'; '.join(errors))

print('PASS EDITORIAL WAVE 2-3')
print('ARTICLE_01',a1)
print('ARTICLE_02',a2)
print('ARTICLE_03',a3)
print('CATEGORY',caturl)
print('BLOG',blogurl)
print('PUBLISHED',d['published'])
print('HOME_SHA_PRESERVED',post_hash['front-page.php'])
