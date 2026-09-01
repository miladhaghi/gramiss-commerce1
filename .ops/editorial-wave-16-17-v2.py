import base64,hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');HEALTHY=os.environ.get('HEALTHY_HOME_SHA','');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir'
PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3';PCAT_SHA='75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
TITLE16='شست‌وشوی تیشرت چاپی؛ محافظت از چاپ در شستن، خشک‌کردن و اتوکشی'; TITLE17='راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت، افت پارچه، فاق و قد'
META16='شست‌وشوی تیشرت چاپی؛ محافظت از چاپ و پارچه'; DESC16='برای شست‌وشوی تیشرت چاپی، اول لیبل و نوع چاپ را بررسی کنید؛ سپس شستن، خشک‌کردن و اتوکشی را طوری مدیریت کنید که تماس و حرارت اضافه به چاپ وارد نشود.'
META17='راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت و افت پارچه'; DESC17='برای خرید شلوار پارچه‌ای مردانه، فیت، فاق، ران، دمپا، قد و افت واقعی پارچه را بررسی کنید و اندازه‌ها را با یک شلوار مرجع مقایسه کنید.'

def safe(url):
 p=urllib.parse.urlsplit(url);return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def api(fn,params,post=False):
 u=f'https://{HOST}:2083/execute/Fileman/{fn}';e=urllib.parse.urlencode(params).encode();last=None
 for n in range(4):
  try:
   r=urllib.request.Request(u if post else u+'?'+e.decode(),data=e if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {USER}:{TOKEN}');
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=CTX,timeout=90) as x:o=json.loads(x.read().decode('utf-8','replace'))
   z=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(z,dict) or z.get('status')!=1:raise RuntimeError(str(z))
   return z.get('data')
  except Exception as exc:last=exc;print('API_RETRY',fn,n+1,exc);time.sleep(n+1)
 raise last
def theme(rel):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel);x=api('get_file_content',{'dir':ROOT if not d else ROOT+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(x,dict):
  for k in ('content','file_content','data'):
   if isinstance(x.get(k),str):return x[k]
 return x if isinstance(x,str) else ''
def save(name,text):return api('save_file_content',{'dir':'public_html','file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(url,timeout=180):
 url=safe(url);last=None
 for n in range(4):
  try:
   q=urllib.request.Request(url,headers={'User-Agent':'GramissWave1617V2/1.0','Cache-Control':'no-cache'});
   with urllib.request.urlopen(q,context=CTX,timeout=timeout) as r:return r.status,r.read(),r.geturl()
  except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
  except Exception as exc:last=exc;print('HTTP_RETRY',n+1,url,exc);time.sleep(n+1)
 raise last
def val(t,p):
 m=re.search(p,t,re.I|re.S);return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def meta(raw):
 t=raw.decode('utf-8','replace').split('</head>',1)[0];return {'title':val(t,r'<title[^>]*>(.*?)</title>'),'description':val(t,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':val(t,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':val(t,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sm(path):
 s,b,_=get(BASE+'/'+path+'?t='+str(int(time.time())),120);return s,[x.replace('&amp;','&') for x in re.findall(r'<loc>(.*?)</loc>',b.decode('utf-8','replace'),re.I)]
P=['front-page.php','template-parts/home-looks.php','assets/css/home-looks.css','assets/js/home-looks.js'];pre={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in P};print('PROTECTED_PRE',json.dumps(pre,sort_keys=True));
if HEALTHY and pre['front-page.php']!=HEALTHY:raise SystemExit('HOME DRIFT')
ps,pl=sm('product-sitemap.xml');pl=sorted(pl);ph=hashlib.sha256('\n'.join(pl).encode()).hexdigest();cs,cl=sm('product_cat-sitemap.xml');cl=sorted(cl);ch=hashlib.sha256('\n'.join(cl).encode()).hexdigest();print('SITEMAPS_PRE',ps,len(pl),ph,cs,len(cl),ch)
if ps!=200 or len(pl)!=47 or ph!=PRODUCT_SHA or cs!=200 or len(cl)!=20 or ch!=PCAT_SHA:raise SystemExit('COMMERCE SITEMAP DRIFT')
commerce={'tshirt':BASE+'/product-category/tshirt/','graphic':BASE+'/product-category/tshirt/graphic-tshirt/','pants':BASE+'/product-category/pants/','fabric':BASE+'/product-category/pants/fabric-pants/'}
for k,u in commerce.items():
 s,b,f=get(u+'?t='+str(int(time.time())),120);m=meta(b);print('COMMERCE',k,s,f,m)
 if s!=200 or 'noindex' in m['robots'].lower() or norm(m['canonical'])!=norm(u):raise SystemExit('COMMERCE DRIFT '+k)
nonce=hashlib.sha256((str(time.time())+pre['front-page.php']).encode()).hexdigest()[:14];probe='gramiss-wave-16-17-v2-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$ids=[453,459,460,463,464,467,468,471,472,482,483,487,488,492,493];$p=[];$e=[];foreach($ids as $id){$p[$id]=get_post($id);if(!$p[$id]||$p[$id]->post_status!=='publish')$e[]='post'.$id;}
$fit=get_term_by('slug','fit-size-guide','category');$fab=get_term_by('slug','fabric-care','category');$sty=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');$g=get_term_by('slug','graphic-tshirt','product_cat');$t=get_term_by('slug','tshirt','product_cat');$fp=get_term_by('slug','fabric-pants','product_cat');$pa=get_term_by('slug','pants','product_cat');
if((int)wp_count_posts('post')->publish!==15)$e[]='published';if(!$fit||!$fab||!$sty||!$buy||!$g||!$t||!$fp||!$pa)$e[]='taxonomy';if((int)$fit->count!==7||(int)$fab->count!==3||(int)$sty->count!==2||(int)$buy->count!==3)$e[]='counts';
$s16=sanitize_title('شستشوی تیشرت چاپی');$s17=sanitize_title('راهنمای خرید شلوار پارچه ای مردانه');if(get_page_by_path($s16,OBJECT,'post')||get_page_by_path($s17,OBJECT,'post'))$e[]='slug';$marks=[453=>'1617-tee-care-from-01',471=>'1617-tee-care-from-08',460=>'1617-fabric-pants-from-03',468=>'1617-fabric-pants-from-07'];foreach($marks as $id=>$m)if(strpos($p[$id]->post_content,$m)!==false)$e[]='marker'.$id;if($e){http_response_code(409);echo wp_json_encode(['error'=>'baseline','details'=>$e]);exit;}
$gu=get_term_link($g);$tu=get_term_link($t);$fpu=get_term_link($fp);$pau=get_term_link($pa);$u1=get_permalink($p[453]);$u3=get_permalink($p[460]);$u7=get_permalink($p[468]);$u8=get_permalink($p[471]);$u9=get_permalink($p[472]);$old=[];foreach([453,471,460,468] as $id)$old[$id]=$p[$id]->post_content;
$c16=<<<'HTML'
<p>برای تیشرت چاپی یک نسخه شست‌وشوی ثابت وجود ندارد؛ چون جنس پارچه، روش چاپ و دستور مراقبت هر محصول می‌تواند متفاوت باشد. نقطه شروع امن، لیبل خود لباس و اطلاعاتی است که فروشنده یا تولیدکننده برای همان مدل منتشر کرده است.</p>
<p>هدف این راهنما حفظ هم‌زمان پارچه و چاپ است، نه معرفی یک ترفند جادویی. وقتی نوع چاپ دقیق را نمی‌دانی، تماس مکانیکی، مواد قوی و حرارت اضافه را محافظه‌کارانه مدیریت کن.</p>
<h2>اول لیبل تیشرت و دستور همان محصول را بخوان</h2><p>دمای آب، امکان ماشین‌شویی، خشک‌کن و اتوکشی را از لیبل شروع کن. اگر دستور محصول با توصیه عمومی اینترنتی فرق دارد، دستور همان لباس اولویت دارد.</p>
<h2>چرا نوع چاپ مهم است؟</h2><p>چاپ‌های مختلف رفتار یکسانی در برابر حرارت، اصطکاک و مواد شوینده ندارند. ظاهر چاپ در عکس برای تشخیص قطعی تکنیک چاپ کافی نیست؛ روش چاپ را فقط وقتی قطعی بدان که اعلام شده باشد.</p>
<h2>قبل از شست‌وشو چاپ را بررسی کن</h2><p>ترک، بلندشدگی لبه، لکه یا آسیب قبلی را ببین. اگر چاپ از قبل آسیب دیده، شست‌وشوی تهاجمی می‌تواند وضعیت را بدتر کند.</p>
<h2>پشت‌ورو کردن چه زمانی مفید است؟</h2><p>پشت‌ورو کردن می‌تواند تماس مستقیم سطح چاپ با لباس‌های دیگر را کمتر کند، اما جایگزین دستور لیبل نیست.</p>
<h2>لباس‌های خشن و یراق‌دار را جدا کن</h2><p>زیپ فلزی، قلاب، سطح زبر یا لباس سنگین اصطکاک بیشتری ایجاد می‌کند. وقتی امکانش هست، تیشرت چاپی را با لباس‌های سبک‌تر و رنگ‌های سازگار بشوی.</p>
<h2>دمای آب را حدس نزن</h2><p>یک عدد دمای ثابت برای همه تیشرت‌های چاپی درست نیست. دما را با لیبل، میزان آلودگی و شوینده هماهنگ کن و عدد عمومی اینترنتی را جای دستور محصول نگذار.</p>
<h2>شوینده و لکه‌بر را محافظه‌کارانه انتخاب کن</h2><p>سفیدکننده، لکه‌بر یا شوینده قوی می‌تواند روی بعضی رنگ‌ها یا چاپ‌ها اثر بگذارد. اگر سازگاری مشخص نیست، ماده را مستقیم روی سطح چاپ نریز و دستور محصول را بخوان.</p>
<h2>ماشین لباس‌شویی یا شست‌وشوی دستی؟</h2><p>هیچ‌کدام به‌صورت جهانی بهترین نیست. اگر لیبل ماشین‌شویی را مجاز می‌داند، برنامه‌ای با تماس مکانیکی کمتر منطقی است. در شست‌وشوی دستی هم چنگ‌زدن و ساییدن مستقیم چاپ مناسب نیست.</p>
<h2>چاپ را نساب و نپیچان</h2><p>برای خارج کردن آب، پیچاندن شدید تیشرت یا ساییدن طرح روی خودش را به عادت تبدیل نکن. روش خشک‌کردن مطابق لیبل کمک می‌کند فرم پارچه و چاپ بهتر حفظ شود.</p>
<h2>خشک‌کردن تیشرت چاپی را چطور مدیریت کنیم؟</h2><p>اول ببین خشک‌کن ماشینی برای همان لباس مجاز است یا نه. اگر تحمل حرارت چاپ مشخص نیست، از گرمای شدید و تماس مستقیم با منبع حرارتی دوری کن.</p>
<h2>آفتاب مستقیم همیشه پاسخ نیست</h2><p>نور و گرما می‌تواند روی بعضی رنگ‌ها اثر بگذارد. به جای قانون همیشگی، دستور محصول و شرایط پارچه را معیار قرار بده.</p>
<h2>اتو را مستقیم روی چاپ نگذار</h2><p>اگر لیبل اجازه اتو می‌دهد، حرارت را با جنس پارچه هماهنگ کن و از تماس مستقیم صفحه داغ با چاپی که تحملش مشخص نیست خودداری کن.</p>
<h2>اگر نوع چاپ را می‌دانیم چه تغییری می‌کند؟</h2><p>وقتی فروشنده روش چاپ و دستور نگهداری آن را مشخص کرده، توصیه دقیق‌تر همان محصول را دنبال کن؛ آن را به تمام تیشرت‌های چاپی تعمیم نده.</p>
<h2>اشتباه‌های رایج در شست‌وشوی تیشرت چاپی</h2><ul><li>انتخاب دما از روی یک عدد عمومی.</li><li>ریختن مستقیم لکه‌بر یا سفیدکننده روی طرح.</li><li>شستن کنار لباس‌های زبر بدون توجه به اصطکاک.</li><li>پیچاندن و ساییدن شدید چاپ.</li><li>حرارت مستقیم بدون اجازه محصول.</li><li>حدس روش چاپ فقط از روی ظاهر.</li></ul>
<h2>قبل از خرید، اطلاعات نگهداری را هم بررسی کن</h2><p>اگر هنوز محصول را نخریده‌ای، علاوه بر فیت و پارچه ببین فروشنده درباره چاپ و مراقبت چه اطلاعاتی داده است. <a href="__A8__">راهنمای خرید تیشرت مردانه</a> معیارهای فیت، دوخت و چاپ را جدا توضیح می‌دهد.</p>
<h2>چک‌لیست کوتاه مراقبت</h2><ul><li>لیبل را بخوان.</li><li>نوع چاپ را حدس نزن.</li><li>اصطکاک و فشار را کم کن.</li><li>دما و شوینده را با همان محصول هماهنگ کن.</li><li>خشک‌کن و اتو را فقط در محدوده مجاز استفاده کن.</li><li>مشخصات <a href="__G__">تیشرت گرافیکی</a> و <a href="__T__">دسته تیشرت مردانه</a> را برای هر مدل جدا ببین.</li></ul>
HTML;
$c16=str_replace(['__A8__','__G__','__T__'],[esc_url($u8),esc_url($gu),esc_url($tu)],$c16);
$c17=<<<'HTML'
<p>شلوار پارچه‌ای مردانه فقط شلوار رسمی و اسلیم نیست. مدل‌های راسته، نیم‌بگ، بگ و پارچه‌های نرم و ریزش‌دار هم در این خانواده دیده می‌شوند. برای خرید آنلاین، مهم‌تر از اسم مدل این است که فیت، اندازه و رفتار پارچه را جدا بررسی کنی.</p>
<p>این راهنما معیارهای خرید شلوار پارچه‌ای برای استایل روزمره و کژوال را توضیح می‌دهد و موضوع جین را به راهنمای اختصاصی آن می‌سپارد.</p>
<h2>اول مشخص کن چه فیتی می‌خواهی</h2><p>راسته، نیم‌بگ و بگ فقط برچسب نیستند. حجم ران، فاق، عرض دمپا و قد سیلوئت را می‌سازند. برای تفاوت فیت‌های آزاد، <a href="__A3__">راهنمای بگ، نیم‌بگ و فول‌بگ</a> را ببین.</p>
<h2>سایز کمر را برای بگ دیده‌شدن بزرگ‌تر نخر</h2><p>اگر مدل واقعاً بگ طراحی شده، آزادی باید در الگوی شلوار باشد. بزرگ‌کردن سایز کمر ممکن است فقط جای کمر و فاق را خراب کند.</p>
<h2>از یک شلوار مرجع اندازه بگیر</h2><p>شلوار مرجع را صاف بگذار و کمر، فاق، ران، دمپا و قد را به روشی ثابت اندازه بگیر؛ سپس با جدول همان مدل مقایسه کن.</p>
<h2>فاق چرا در شلوار پارچه‌ای مهم است؟</h2><p>فاق روی محل نشستن کمر و نسبت حجم بخش بالایی اثر دارد. فاق بلند یا کوتاه به‌خودی‌خود بهتر نیست؛ باید با طراحی مدل و فیت موردنظر هماهنگ باشد.</p>
<h2>عرض ران را نادیده نگیر</h2><p>در مدل‌های آزاد، ران یکی از اندازه‌های تعیین‌کننده است. اگر فقط کمر و دمپا را ببینی ممکن است حجم واقعی بخش بالایی را اشتباه تخمین بزنی.</p>
<h2>دمپا ظاهر شلوار را چطور تغییر می‌دهد؟</h2><p>عرض دمپا روی ارتباط شلوار با کفش و میزان حجم پایین استایل اثر می‌گذارد. عدد واقعی از عبارت‌های مبهم مثل آزاد دقیق‌تر است.</p>
<h2>قد شلوار را با کفشی که واقعاً می‌پوشی بسنج</h2><p>قد مناسب به نوع کفش، عرض دمپا و میزان شکست دلخواه بستگی دارد. شلوار مرجع را همراه کفش اصلی خودت ارزیابی کن.</p>
<h2>افت پارچه یعنی چه؟</h2><p>افت یا ریزش به نحوه آویزان‌شدن و حرکت پارچه اشاره دارد. پارچه نرم‌تر ممکن است حجم را روان‌تر نشان دهد و پارچه ساختارمندتر خط واضح‌تری بسازد.</p>
<h2>پارچه نرم همیشه بهتر نیست</h2><p>انتخاب بین پارچه رها و ساختارمند به مدل و استایل موردنظر بستگی دارد. مشخصات واقعی محصول را معیار قرار بده.</p>
<h2>ترکیب الیاف را فقط از مشخصات بخوان</h2><p>ظاهر مات، براق، ضخیم یا سبک در تصویر ترکیب الیاف را ثابت نمی‌کند. اگر درصد الیاف اعلام نشده، کشسانی، چروک‌پذیری یا دوام قطعی را حدس نزن.</p>
<h2>کمر کشی، بند یا زیپ چه فرقی در خرید ایجاد می‌کند؟</h2><p>نوع بسته‌شدن روی دامنه تنظیم و حس استفاده اثر دارد، اما مقدار کشسانی یا تنظیم را فقط وقتی قطعی بدان که در مشخصات آمده باشد.</p>
<h2>جیب و دوخت را از چند زاویه ببین</h2><p>نمای جلو کافی نیست. محل جیب‌ها، خطوط دوخت، پشت شلوار و دمپا را هم ببین و فقط اطلاعات قابل مشاهده را نتیجه‌گیری کن.</p>
<h2>شلوار پارچه‌ای را با چه بالاتنه‌ای تصور کنیم؟</h2><p>حجم بالاتنه به درک درست فیت کمک می‌کند. <a href="__A7__">راهنمای استایل با شلوار بگ</a> نشان می‌دهد بالاتنه فیت یا باکسی هر دو می‌توانند با توجه به حجم کل استایل کار کنند.</p>
<h2>شلوار پارچه‌ای و جین یک معیار خرید ندارند</h2><p>اندازه‌های پایه مشترک‌اند، اما جین موضوعات مخصوص خودش را دارد. <a href="__A9__">راهنمای خرید شلوار جین مردانه</a> مالک آن موضوع باقی می‌ماند.</p>
<h2>اشتباه‌های رایج هنگام خرید شلوار پارچه‌ای</h2><ul><li>فرض اینکه همه مدل‌ها رسمی یا اسلیم‌اند.</li><li>بزرگ‌تر خریدن کمر برای ساختن فیت بگ.</li><li>نادیده گرفتن فاق و ران.</li><li>انتخاب قد بدون کفش.</li><li>حدس جنس یا کشسانی از عکس.</li><li>مقایسه سایز اسمی به جای اندازه واقعی.</li></ul>
<h2>چک‌لیست نهایی خرید</h2><ul><li>فیت موردنظر را مشخص کن.</li><li>کمر، فاق، ران، دمپا و قد را با شلوار مرجع مقایسه کن.</li><li>افت را از تصاویر و توضیح محصول ارزیابی کن.</li><li>الیاف را فقط از مشخصات بخوان.</li><li>نوع کمر، جیب و دمپا را بررسی کن.</li><li>مدل‌های <a href="__FP__">شلوار پارچه‌ای مردانه</a> و <a href="__PA__">دسته شلوار مردانه</a> را با همین معیارها مقایسه کن.</li></ul>
HTML;
$c17=str_replace(['__A3__','__A7__','__A9__','__FP__','__PA__'],[esc_url($u3),esc_url($u7),esc_url($u9),esc_url($fpu),esc_url($pau)],$c17);
$a16=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'شست‌وشوی تیشرت چاپی؛ محافظت از چاپ در شستن، خشک‌کردن و اتوکشی','post_name'=>$s16,'post_content'=>$c16,'post_category'=>[(int)$fab->term_id]]),true);if(is_wp_error($a16)){http_response_code(500);echo wp_json_encode(['error'=>'a16']);exit;}$a17=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت، افت پارچه، فاق و قد','post_name'=>$s17,'post_content'=>$c17,'post_category'=>[(int)$buy->term_id]]),true);if(is_wp_error($a17)){wp_delete_post($a16,true);http_response_code(500);echo wp_json_encode(['error'=>'a17']);exit;}$u16=get_permalink($a16);$u17=get_permalink($a17);
$m=[$a16=>['rank_math_title'=>'شست‌وشوی تیشرت چاپی؛ محافظت از چاپ و پارچه','rank_math_description'=>'برای شست‌وشوی تیشرت چاپی، اول لیبل و نوع چاپ را بررسی کنید؛ سپس شستن، خشک‌کردن و اتوکشی را طوری مدیریت کنید که تماس و حرارت اضافه به چاپ وارد نشود.','rank_math_focus_keyword'=>'شستشوی تیشرت چاپی'],$a17=>['rank_math_title'=>'راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت و افت پارچه','rank_math_description'=>'برای خرید شلوار پارچه‌ای مردانه، فیت، فاق، ران، دمپا، قد و افت واقعی پارچه را بررسی کنید و اندازه‌ها را با یک شلوار مرجع مقایسه کنید.','rank_math_focus_keyword'=>'راهنمای خرید شلوار پارچه ای مردانه']];foreach($m as $id=>$v){foreach($v as $k=>$x)update_post_meta($id,$k,$x);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}
$b=[453=>'<div data-g1-wave="1617-tee-care-from-01"><h2>بعد از انتخاب فیت، از چاپ هم درست مراقبت کن</h2><p>اگر تیشرت چاپ دارد، <a href="'.esc_url($u16).'">راهنمای شست‌وشوی تیشرت چاپی</a> شستن و حرارت را بدون نسخه عمومی برای همه چاپ‌ها توضیح می‌دهد.</p></div>',471=>'<div data-g1-wave="1617-tee-care-from-08"><h2>کیفیت خرید با نگهداری درست کامل می‌شود</h2><p>بعد از بررسی چاپ هنگام خرید، <a href="'.esc_url($u16).'">راهنمای مراقبت و شست‌وشوی تیشرت چاپی</a> مرحله استفاده و نگهداری را پوشش می‌دهد.</p></div>',460=>'<div data-g1-wave="1617-fabric-pants-from-03"><h2>برای شلوار پارچه‌ای، فیت را کنار افت پارچه بخوان</h2><p>بعد از تشخیص بگ و نیم‌بگ، <a href="'.esc_url($u17).'">راهنمای خرید شلوار پارچه‌ای مردانه</a> فاق، ران، دمپا، قد و ریزش پارچه را به معیار خرید تبدیل می‌کند.</p></div>',468=>'<div data-g1-wave="1617-fabric-pants-from-07"><h2>اگر شلوار بگ پارچه‌ای می‌خواهی، اندازه و افت را جدا بررسی کن</h2><p><a href="'.esc_url($u17).'">راهنمای خرید شلوار پارچه‌ای مردانه</a> کمک می‌کند فیت، قد و رفتار پارچه را قبل از خرید مقایسه کنی.</p></div>'];foreach($b as $id=>$block){$r=wp_update_post(wp_slash(['ID'=>$id,'post_content'=>$p[$id]->post_content."\n".$block]),true);if(is_wp_error($r)){foreach($old as $oid=>$c)wp_update_post(wp_slash(['ID'=>$oid,'post_content'=>$c]));wp_delete_post($a17,true);wp_delete_post($a16,true);http_response_code(500);echo wp_json_encode(['error'=>'bridge']);exit;}}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'counts'=>['fit'=>(int)get_term($fit->term_id)->count,'fabric'=>(int)get_term($fab->term_id)->count,'style'=>(int)get_term($sty->term_id)->count,'buy'=>(int)get_term($buy->term_id)->count],'a16'=>['id'=>(int)$a16,'url'=>$u16],'a17'=>['id'=>(int)$a17,'url'=>$u17],'old'=>array_map('base64_encode',$old)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save(probe,php);st,raw,f=get(BASE+'/'+probe+'?t='+str(int(time.time())),300);print('PUBLISH',st,f,raw.decode('utf-8','replace'))
if st!=200:raise SystemExit('PUBLISH FAIL')
r=json.loads(raw.decode('utf-8','replace'));a16=r['a16'];a17=r['a17'];errors=[]
if r.get('published')!=17 or r.get('counts')!={'fit':7,'fabric':4,'style':2,'buy':4}:errors.append('state')
def verify(a,title,mt,md,links):
 s,b,f=get(a['url']+'?t='+str(int(time.time())),180);t=b.decode('utf-8','replace');m=meta(b);href={norm(x) for x in re.findall(r'href=["\']([^"\']+)',t,re.I) if 'gramiss.ir' in x};print('VERIFY',a['id'],s,f,'H2',t.count('<h2>'),json.dumps(m,ensure_ascii=False))
 if s!=200 or title not in t or m['title']!=mt or m['description']!=md or norm(m['canonical'])!=norm(a['url']) or 'noindex' in m['robots'].lower() or not re.search(r'"@type"\s*:\s*"BlogPosting"',t,re.I) or re.search(r'"@type"\s*:\s*"Product"',t,re.I):errors.append('article '+str(a['id']))
 for x in links:
  if norm(x) not in href:errors.append('link '+str(a['id'])+' '+norm(x))
verify(a16,TITLE16,META16,DESC16,[commerce['graphic'],commerce['tshirt'],BASE+'/راهنمای-خرید-تیشرت-مردانه/'])
verify(a17,TITLE17,META17,DESC17,[commerce['fabric'],commerce['pants'],BASE+'/تفاوت-شلوار-بگ-نیم-بگ-فول-بگ/',BASE+'/با-شلوار-بگ-مردانه-چی-بپوشیم/',BASE+'/راهنمای-خرید-شلوار-جین-مردانه/'])
checks=[(453,BASE+'/تیشرت-باکسی-چیست-تفاوت-اورسایز/','1617-tee-care-from-01',a16['url']),(471,BASE+'/راهنمای-خرید-تیشرت-مردانه/','1617-tee-care-from-08',a16['url']),(460,BASE+'/تفاوت-شلوار-بگ-نیم-بگ-فول-بگ/','1617-fabric-pants-from-03',a17['url']),(468,BASE+'/با-شلوار-بگ-مردانه-چی-بپوشیم/','1617-fabric-pants-from-07',a17['url'])]
for pid,u,mk,target in checks:
 s,b,_=get(u+'?t='+str(int(time.time())),150);t=b.decode('utf-8','replace');href={norm(x) for x in re.findall(r'href=["\']([^"\']+)',t,re.I) if 'gramiss.ir' in x}
 if s!=200 or mk not in t or norm(target) not in href:errors.append('bridge '+str(pid))
postst,postu=sm('post-sitemap.xml');catst,catu=sm('category-sitemap.xml');ps2,pl2=sm('product-sitemap.xml');cs2,cl2=sm('product_cat-sitemap.xml');pl2=sorted(pl2);cl2=sorted(cl2);postnorm={norm(x) for x in postu}
if postst!=200 or len(postu)!=18 or norm(a16['url']) not in postnorm or norm(a17['url']) not in postnorm:errors.append('post sitemap')
if catst!=200 or len(catu)!=4:errors.append('category sitemap')
if pl2!=pl or hashlib.sha256('\n'.join(pl2).encode()).hexdigest()!=ph:errors.append('product drift')
if cl2!=cl or hashlib.sha256('\n'.join(cl2).encode()).hexdigest()!=ch:errors.append('product cat drift')
post={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in P};print('PROTECTED_POST',json.dumps(post,sort_keys=True));
if post!=pre:errors.append('protected')
found=set()
for page in (1,2):
 u=BASE+'/وبلاگ/' if page==1 else BASE+'/وبلاگ/page/2/';s,b,_=get(u+'?t='+str(int(time.time())),150);t=b.decode('utf-8','replace');
 if TITLE16 in t:found.add(16)
 if TITLE17 in t:found.add(17)
if found!={16,17}:errors.append('blog')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));snap=base64.b64encode(json.dumps(r.get('old',{})).encode()).decode();rb='gramiss-wave-16-17-v2-rollback-'+nonce+'.php';rbphp=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);foreach([sanitize_title('شستشوی تیشرت چاپی'),sanitize_title('راهنمای خرید شلوار پارچه ای مردانه')] as $s){$p=get_page_by_path($s,OBJECT,'post');if($p)wp_delete_post($p->ID,true);}$x=json_decode(base64_decode('SNAP'),true);foreach($x as $id=>$b){$c=base64_decode($b,true);if($c!==false)wp_update_post(wp_slash(['ID'=>(int)$id,'post_content'=>$c]));}if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();do_action('litespeed_purge_all');echo wp_json_encode(['rolled_back'=>true,'published'=>(int)wp_count_posts('post')->publish]);?>'''.replace('SNAP',snap);save(rb,rbphp);rs,rr,_=get(BASE+'/'+rb+'?t='+str(int(time.time())),240);print('ROLLBACK',rs,rr.decode('utf-8','replace'));raise SystemExit('FAILED AND ROLLED BACK')
print('PASS EDITORIAL WAVE 16-17',json.dumps({'a16':a16,'a17':a17,'post_sitemap':len(postu),'product_sha':ph,'product_cat_sha':ch,'protected':post},ensure_ascii=False,sort_keys=True))
