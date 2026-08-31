import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context();BASE='https://gramiss.ir'
def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();last=None
 for attempt in range(1,5):
  try:
   r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}')
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
   q=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
   return q.get('data')
  except Exception as e:last=e;print('API_RETRY',fn,attempt,e);time.sleep(attempt*2 if attempt<4 else 0)
 raise last
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u,timeout=180):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissEditorialWave89/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 try:
  with urllib.request.urlopen(req,context=ctx,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def hv(t,p):
 m=re.search(p,t,re.I|re.S);return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def head(raw):
 t=raw.decode('utf-8','replace').split('</head>',1)[0];return {'title':hv(t,r'<title[^>]*>(.*?)</title>'),'description':hv(t,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':hv(t,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':hv(t,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sitemap(path):
 s,r,_,_=get(BASE+'/'+path+'?t='+str(int(time.time())),120);return s,[x.replace('&amp;','&') for x in re.findall(r'<loc>(.*?)</loc>',r.decode('utf-8','replace'),re.I)]
protected=['front-page.php','template-parts/home-looks.php','assets/css/home-looks.css','assets/js/home-looks.js'];pre={f:hashlib.sha256(read_theme(f).encode()).hexdigest() for f in protected};print('PROTECTED_PRE',json.dumps(pre,ensure_ascii=False,sort_keys=True))
if healthy and pre['front-page.php']!=healthy:raise SystemExit('ABORT Home mismatch')
ps0,pl0=sitemap('product-sitemap.xml');pl0=sorted(pl0);print('PRODUCT_SITEMAP_PRE',ps0,len(pl0),hashlib.sha256('\n'.join(pl0).encode()).hexdigest())
if ps0!=200:raise SystemExit('ABORT product sitemap')
commerce={'tshirt':BASE+'/product-category/tshirt/','jeans':BASE+'/product-category/pants/jeans/','pants':BASE+'/product-category/pants/'}
for k,u in commerce.items():
 s,r,f,_=get(u+'?t='+str(int(time.time())),120);h=head(r);print('COMMERCE_PRE',k,s,f,json.dumps(h,ensure_ascii=False,separators=(',',':')))
 if s!=200 or 'noindex' in h.get('robots','').lower() or norm(h.get('canonical',''))!=norm(u):raise SystemExit('ABORT commerce '+k)
nonce=hashlib.sha256((str(time.time())+pre['front-page.php']).encode()).hexdigest()[:14];name='gramiss-editorial-wave-8-9-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$slug8=sanitize_title('راهنمای خرید تیشرت مردانه');$slug9=sanitize_title('راهنمای خرید شلوار جین مردانه');$a1=get_post(453);$a2=get_post(459);$a3=get_post(460);$a7=get_post(468);$a8x=get_page_by_path($slug8,OBJECT,'post');$a9x=get_page_by_path($slug9,OBJECT,'post');$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');$published=(int)wp_count_posts('post')->publish;$tshirt=get_term_by('slug','tshirt','product_cat');$jeans=get_term_by('slug','jeans','product_cat');$pants=get_term_by('slug','pants','product_cat');
if(!$a1||!$a2||!$a3||!$a7||$a1->post_status!=='publish'||$a2->post_status!=='publish'||$a3->post_status!=='publish'||$a7->post_status!=='publish'||$a8x||$a9x||!$fit||!$fabric||!$style||!$buy||!$tshirt||!$jeans||!$pants||$published!==7||(int)$fit->count!==3||(int)$fabric->count!==2||(int)$style->count!==2||(int)$buy->count!==0){http_response_code(409);echo wp_json_encode(['error'=>'baseline drift','published'=>$published,'buy'=>$buy?$buy->count:null,'a8'=>$a8x?$a8x->ID:null,'a9'=>$a9x?$a9x->ID:null],JSON_UNESCAPED_UNICODE);exit;}
if(strpos($a2->post_content,'data-g1-cluster-wave="89-tshirt"')!==false||strpos($a3->post_content,'data-g1-cluster-wave="89-jeans"')!==false){http_response_code(409);echo wp_json_encode(['error'=>'wave89 marker exists']);exit;}
$tu=get_term_link($tshirt);$ju=get_term_link($jeans);$pu=get_term_link($pants);foreach([$tu,$ju,$pu] as $x){if(is_wp_error($x)){http_response_code(409);echo wp_json_encode(['error'=>'commerce url']);exit;}}
$content8=<<<'HTML'
<p>خرید تیشرت مردانه در ظاهر ساده است؛ رنگ و طرح را می‌بینی، سایز را انتخاب می‌کنی و تمام. اما بخش زیادی از رضایت یا نارضایتی بعد از خرید از چیزهایی می‌آید که در عکس اول کمتر دیده می‌شوند: فیت واقعی، قد لباس، فرم یقه، رفتار پارچه، کیفیت چاپ و جزئیات دوخت.</p>
<p>این راهنما یک چک‌لیست برای خرید آگاهانه است، نه فهرستی از ادعاهای کلی مثل «هرچه پارچه ضخیم‌تر باشد بهتر است» یا «قیمت بالاتر یعنی کیفیت بالاتر». کیفیت باید از روی مشخصات و اجرای همان محصول سنجیده شود.</p>
<h2>اول مشخص کن چه نوع تیشرتی می‌خواهی</h2>
<p>قبل از مقایسه محصولات، کاربرد را مشخص کن: تیشرت ساده برای استفاده روزمره، مدل گرافیکی به‌عنوان نقطه اصلی استایل، باکسی برای عرض بیشتر و قد کنترل‌شده یا فیت آزادتر برای سیلوئت رها. وقتی هدف روشن باشد، مقایسه قیمت و جزئیات معنی‌دارتر می‌شود.</p>
<p>اگر تفاوت باکسی و اورسایز برایت مبهم است، <a href="A1_URL">راهنمای تفاوت تیشرت باکسی و اورسایز</a> را قبل از خرید ببین.</p>
<h2>سایز اسمی را با اندازه واقعی اشتباه نگیر</h2>
<p>S، M، L یا XL بین برندها و حتی بین دو مدل یک برند می‌تواند ابعاد متفاوتی داشته باشد. معیار دقیق‌تر، اندازه خود لباس است: عرض سینه، قد، عرض شانه و طول آستین. این اعداد را با تیشرتی که تنخورش را دوست داری مقایسه کن.</p>
<p>برای روش اندازه‌گیری و تصمیم بین دو سایز، <a href="A2_URL">راهنمای انتخاب سایز تیشرت باکسی</a> مراحل دقیق را توضیح می‌دهد.</p>
<h2>فیت را از روی نسبت عرض به قد بخوان</h2>
<p>فقط زیادبودن عرض، تیشرت را باکسی نمی‌کند. اگر همزمان قد زیادی داشته باشد، ممکن است بیشتر شبیه یک تیشرت اورسایز بلند دیده شود. در خرید آنلاین، عرض و قد را کنار هم ببین و محل پایان لباس روی شلوار را تصور کن.</p>
<p>سرشانه و آستین هم مهم‌اند؛ افت شانه می‌تواند حجم بالاتنه را بیشتر کند حتی وقتی عرض سینه دو مدل نزدیک است.</p>
<h2>در مشخصات پارچه دنبال چه چیزی باشیم؟</h2>
<p>اگر ترکیب الیاف، وزن یا گرماژ اعلام شده، از همان اطلاعات استفاده کن. اسم‌هایی مثل «دو نخ»، «پنبه‌ای» یا «سنگشور» در بازار ممکن است توضیح کامل ساختار پارچه نباشند؛ بنابراین از چیزی که در مشخصات نیامده نتیجه قطعی نگیر.</p>
<p>پارچه ساختارمندتر چاپ و فرم باکسی را متفاوت از پارچه نرم و ریزشی نشان می‌دهد. هیچ‌کدام ذاتاً بهتر نیست؛ به فیت موردنظر بستگی دارد.</p>
<h2>گرماژ بالاتر همیشه بهتر است؟</h2>
<p>نه. گرماژ بیشتر معمولاً به معنی وزن بیشتر پارچه در واحد سطح است، اما کیفیت نهایی به نوع الیاف، بافت، تکمیل و دوخت هم وابسته است. تیشرت سبک می‌تواند برای یک کاربرد مناسب باشد و تیشرت سنگین برای کاربرد دیگری.</p>
<p>اگر عدد گرماژ اعلام نشده، از ظاهر عکس نمی‌توان با اطمینان یک عدد حدس زد. بهتر است توضیحات واقعی محصول را مبنا قرار بدهی.</p>
<h2>یقه را چطور ارزیابی کنیم؟</h2>
<p>در عکس‌های نزدیک، اتصال یقه به بدنه، یکنواختی دوخت و فرم ریب را بررسی کن. یقه نباید در همان عکس اولیه موج شدید یا کشیدگی نامتقارن داشته باشد. با این حال دوام یقه بعد از شست‌وشو فقط از عکس قابل پیش‌بینی نیست و به پارچه، دوخت و روش مراقبت وابسته است.</p>
<p>اگر فروشگاه تصویر پشت یا نمای نزدیک دارد، محل اتصال یقه در پشت گردن را هم ببین.</p>
<h2>کیفیت دوخت را از چه جزئیاتی بفهمیم؟</h2>
<ul><li>خط دوخت لبه آستین و پایین لباس تا حد ممکن یکنواخت باشد.</li><li>درزهای پهلو پیچش واضح نداشته باشند.</li><li>نخ‌های رها یا دوخت قطع‌شده در تصاویر نزدیک دیده نشود.</li><li>اتصال آستین و سرشانه در دو طرف متقارن به نظر برسد.</li><li>اگر محصول دو تکه یا پنل‌دار است، محل اتصال قطعات تمیز باشد.</li></ul>
<p>عکس به‌تنهایی همه کیفیت دوخت را نشان نمی‌دهد، اما همین نشانه‌ها برای حذف گزینه‌های ضعیف مفیدند.</p>
<h2>در تیشرت چاپی چه چیزهایی را بررسی کنیم؟</h2>
<p>اول ببین جای چاپ، اندازه و رنگ آن در همه تصاویر یکسان است. لبه‌های گرافیک، هم‌راستایی چاپ با مرکز لباس و اختلاف احتمالی جلو و پشت را بررسی کن. نوع چاپ اگر برای دوام یا حس سطح مهم است باید در مشخصات محصول ذکر شده باشد؛ از روی عکس نمی‌توان با اطمینان تکنیک چاپ را تعیین کرد.</p>
<p>دستور شست‌وشوی محصول برای تیشرت چاپی اهمیت بیشتری دارد، چون حرارت و سایش می‌توانند روی بعضی چاپ‌ها اثر بگذارند.</p>
<h2>رنگ واقعی را چطور بهتر قضاوت کنیم؟</h2>
<p>نمایشگر، نور عکاسی و ویرایش تصویر می‌توانند برداشت ما از رنگ را تغییر دهند. اگر محصول چند عکس دارد، رنگ را در نماهای مختلف مقایسه کن. نام رنگ به‌تنهایی کافی نیست؛ «ذغالی»، «کرم» یا «آبی» می‌توانند طیف گسترده‌ای داشته باشند.</p>
<p>اگر کد رنگ یا توضیح دقیق موجود است، آن را کنار تصاویر قرار بده؛ ولی باز هم نمایشگرهای مختلف می‌توانند اختلاف ایجاد کنند.</p>
<h2>تیشرت را با شلواری که واقعاً می‌پوشی تصور کن</h2>
<p>قد و حجم تیشرت مستقل از پایین‌تنه نیست. با شلوار بگ، یک تیشرت باکسی کوتاه‌تر می‌تواند خط کمر را واضح نگه دارد؛ با شلوار راسته، همان تیشرت نسبت دیگری می‌سازد. قبل از خرید، یکی از شلوارهای پرتکرار خودت را کنار تیشرت مرجع اندازه بگیر.</p>
<p>این کار از خرید بر اساس عکس مدل به‌تنهایی دقیق‌تر است، چون نسبت قد بدن و شلوار خودت را وارد تصمیم می‌کند.</p>
<h2>قیمت را چطور با ارزش واقعی مقایسه کنیم؟</h2>
<p>قیمت را در کنار اطلاعات قابل بررسی ببین: فیت و اندازه، پارچه اعلام‌شده، کیفیت اجرای چاپ، جزئیات دوخت و میزان استفاده‌ای که از لباس خواهی داشت. گران‌تر بودن به‌تنهایی تضمین کیفیت نیست و ارزان‌تر بودن هم لزوماً به معنی انتخاب بد نیست.</p>
<p>دو محصول نزدیک را با یک چک‌لیست ثابت مقایسه کن تا سلیقه لحظه‌ای جای معیارها را نگیرد.</p>
<h2>قبل از خرید آنلاین چه چیزهایی را ثبت کنیم؟</h2>
<ul><li>عرض و قد تیشرت مرجع خودت.</li><li>فیت مطلوب: جمع‌وجور، باکسی یا رها.</li><li>حداکثر و حداقل قدی که با شلوارهای اصلی‌ات مناسب است.</li><li>ترجیح برای پارچه نرم یا ساختارمند.</li><li>ساده یا چاپی بودن.</li><li>دستور شست‌وشویی که واقعاً می‌توانی رعایت کنی.</li></ul>
<h2>اشتباهات رایج هنگام خرید تیشرت</h2>
<ul><li>انتخاب فقط با سایز اسمی.</li><li>خرید چند سایز بزرگ‌تر برای ساختن فیت باکسی.</li><li>فرض کیفیت پارچه فقط از روی ضخامت یا قیمت.</li><li>نادیده‌گرفتن قد لباس.</li><li>حدس نوع چاپ از روی عکس.</li><li>بی‌توجهی به تصاویر پشت و نمای نزدیک دوخت.</li></ul>
<p>برای مقایسه مدل‌های موجود، <a href="TSHIRT_URL">تیشرت‌های فعلی Gramiss</a> را ببین و همین معیارها را روی هر محصول جداگانه اجرا کن.</p>
<p><strong>جمع‌بندی:</strong> خرید تیشرت خوب یعنی تبدیل سلیقه به چند معیار قابل‌اندازه‌گیری. اول فیت و اندازه، بعد اطلاعات پارچه و اجرا، و در نهایت طرح و قیمت را مقایسه کن.</p>
HTML;
$content9=<<<'HTML'
<p>در خرید شلوار جین مردانه، ظاهر شست‌وشو و رنگ اولین چیزهایی هستند که دیده می‌شوند، اما تصمیم خوب بیشتر به فیت، کمر، فاق، عرض ران، دمپا و قد وابسته است. اگر این اندازه‌ها با چیزی که می‌خواهی هماهنگ نباشند، حتی جین با رنگ و جزئیات جذاب هم احتمالاً کمتر پوشیده می‌شود.</p>
<p>این راهنما کمک می‌کند قبل از خرید اینترنتی شلوار جین، مدل را از روی اندازه واقعی بخوانی و تفاوت بین «سایز درست» و «حجم دلخواه» را حفظ کنی.</p>
<h2>اول فیت شلوار را مشخص کن</h2>
<p>راسته، بگ، نیم‌بگ، فول‌بگ، بالنی و کارگو فقط اسم نیستند؛ هرکدام حجم را در نقاط متفاوتی توزیع می‌کنند. قبل از خرید تصمیم بگیر چه مقدار آزادی در ران و ساق می‌خواهی و دمپا قرار است چطور روی کفش قرار بگیرد.</p>
<p>اگر تمرکزت روی مدل‌های آزاد است، <a href="A3_URL">تفاوت بگ، نیم‌بگ و فول‌بگ</a> را اول بخوان تا اسم فیت‌ها را با حجم واقعی اشتباه نگیری.</p>
<h2>برای بگ شدن، سایز کمر را بزرگ‌تر نخر</h2>
<p>حجم بگ باید از الگوی شلوار بیاید، نه از انتخاب کمر اشتباه. اگر یک شلوار معمولی را چند سایز بزرگ‌تر بگیری، کمر و فاق هم جابه‌جا می‌شوند و ممکن است نتیجه فقط نامتناسب باشد. اول سایز کمر مناسب را پیدا کن و بعد فیت طراحی‌شده شلوار را انتخاب کن.</p>
<p>این تفکیک یکی از مهم‌ترین نکات خرید آنلاین شلوارهای آزاد است.</p>
<h2>چه اندازه‌هایی را از شلوار مرجع بگیریم؟</h2>
<ul><li><strong>کمر:</strong> روی سطح صاف و بدون کشیدن پارچه.</li><li><strong>فاق جلو:</strong> برای فهم محل قرارگیری کمر و فضای بالای شلوار.</li><li><strong>عرض ران:</strong> برای مقایسه حجم بخش بالایی پا.</li><li><strong>عرض دمپا:</strong> برای فهم نحوه افت روی کفش.</li><li><strong>قد کلی یا داخل پا:</strong> بسته به روشی که جدول محصول استفاده می‌کند.</li></ul>
<p>مهم است روش اندازه‌گیری فروشگاه را با روش خودت یکی کنی؛ دو عدد با تعریف متفاوت قابل مقایسه نیستند.</p>
<h2>فاق شلوار چرا مهم است؟</h2>
<p>فاق تعیین می‌کند کمر شلوار روی بدن در چه ارتفاعی قرار بگیرد و روی نسبت بالاتنه و پا اثر دارد. در شلوار بگ، فاق همچنین روی فضای بخش بالایی و افت پارچه مؤثر است. فقط دور کمر را نبین؛ دو شلوار با کمر یکسان و فاق متفاوت می‌توانند کاملاً متفاوت بایستند.</p>
<h2>دنیم خشک و دنیم نرم چه تفاوتی در ظاهر دارند؟</h2>
<p>دنیم ساختارمندتر خطوط شلوار و حجم دمپا را واضح‌تر نگه می‌دارد. دنیم نرم‌تر یا ریزشی بیشتر با حرکت بدن همراه می‌شود و شکست‌های متفاوتی روی کفش می‌سازد. هیچ‌کدام ذاتاً باکیفیت‌تر نیستند؛ این رفتار باید با فیتی که می‌خواهی هماهنگ باشد.</p>
<p>اگر ترکیب الیاف یا وزن پارچه اعلام شده، از آن به‌عنوان اطلاعات واقعی استفاده کن. از روی عکس نمی‌توان درصد پنبه یا کشسانی را با دقت تعیین کرد.</p>
<h2>کشش پارچه را از حدس جدا کن</h2>
<p>برخی جین‌ها کشسان‌اند و بعضی تقریباً بدون کشش. این تفاوت روی احساس کمر، زانو و ران اثر دارد. اگر درصد الیاف کشسان در مشخصات نیامده، فقط بر اساس ظاهر پارچه نتیجه قطعی نگیر. اندازه فعلی محصول و توضیحات فروشنده مبنای مطمئن‌تری هستند.</p>
<h2>قد شلوار را با کفش اصلی بسنج</h2>
<p>شلوار جین روی کتانی حجیم و کفش کم‌حجم یکسان نمی‌ایستد. قبل از خرید مشخص کن بیشتر با چه کفشی آن را می‌پوشی. در مدل‌های بگ، یک شکست نرم روی رویه کفش می‌تواند حجم را حفظ کند؛ تجمع چند لایه پارچه روی زمین هم ظاهر الگو را پنهان می‌کند و هم لبه را در معرض سایش قرار می‌دهد.</p>
<p>برای ایده‌های دقیق‌تر درباره تیشرت و کفش، <a href="A7_URL">راهنمای استایل شلوار بگ مردانه</a> را ببین.</p>
<h2>رنگ و شست‌وشوی جین را چطور انتخاب کنیم؟</h2>
<p>آبی روشن، آبی تیره، ذغالی و شست‌وشوهای افکت‌دار هرکدام کنتراست متفاوتی با بالاتنه می‌سازند. اگر می‌خواهی شلوار کاربرد بیشتری داشته باشد، به لباس‌ها و کفش‌های موجود کمدت نگاه کن و ببین کدام تون بیشتر با آن‌ها کار می‌کند.</p>
<p>افکت شست‌وشو بخشی از طراحی است؛ آن را با ساییدگی ناخواسته اشتباه نگیر. تصاویر چند زاویه کمک می‌کنند الگوی رنگ را بهتر ببینی.</p>
<h2>زاپ و جزئیات تزئینی را بررسی کن</h2>
<p>در جین زاپ‌دار، محل زاپ نسبت به زانو و نحوه تقویت لبه‌ها مهم است. جزئیات زیاد می‌توانند نقطه اصلی استایل شوند، بنابراین اگر استفاده روزمره و ترکیب‌پذیری برایت اولویت دارد، میزان جزئیات را با لباس‌های دیگر خودت بسنج.</p>
<p>دوخت تزئینی، پنل‌های دو تکه و جیب‌های کارگو نیز روی وزن بصری شلوار اثر می‌گذارند.</p>
<h2>جیب‌ها و درزها چه اطلاعاتی می‌دهند؟</h2>
<p>تقارن جیب‌ها، یکنواختی درز پهلو و تمیزی اتصال کمر از چیزهایی هستند که در عکس پشت و کنار قابل بررسی‌اند. پیچش شدید درز یا دوخت نامنظم می‌تواند نشانه‌ای برای بررسی بیشتر باشد. البته دوام واقعی فقط از عکس قابل تضمین نیست.</p>
<h2>شلوار جین را با بالاتنه واقعی خودت مقایسه کن</h2>
<p>اگر بیشتر تیشرت‌های باکسی می‌پوشی، قد و فاق شلوار را طوری بررسی کن که نسبت موردنظرت ساخته شود. اگر پیراهن بلند یا لایه‌های اورسایز می‌پوشی، حجم پایین‌تنه ممکن است نیاز به کنترل متفاوتی داشته باشد.</p>
<p>خرید شلوار جدا از کمد فعلی معمولاً باعث می‌شود بعداً برای ست‌کردن آن مجبور به خرید چند آیتم دیگر شوی.</p>
<h2>قیمت جین را با چه معیارهایی بسنجیم؟</h2>
<p>قیمت را کنار اطلاعات قابل بررسی بگذار: فیت، اندازه‌ها، نوع پارچه اعلام‌شده، تمیزی دوخت، جزئیات طراحی و میزان استفاده‌ای که از شلوار انتظار داری. برند یا قیمت به‌تنهایی جای بررسی محصول را نمی‌گیرد.</p>
<h2>اشتباهات رایج در خرید شلوار جین مردانه</h2>
<ul><li>انتخاب سایز کمر بزرگ‌تر برای ساختن فیت بگ.</li><li>نادیده‌گرفتن فاق و تمرکز فقط روی کمر.</li><li>مقایسه دو شلوار فقط از روی اسم فیت.</li><li>خرید قد بدون درنظرگرفتن کفش اصلی.</li><li>حدس کشسانی یا ترکیب الیاف از روی عکس.</li><li>انتخاب رنگ جدا از لباس‌های موجود کمد.</li></ul>
<h2>چک‌لیست نهایی قبل از خرید</h2>
<ul><li>فیت موردنظر را مشخص کرده‌ای.</li><li>کمر، ران، دمپا، فاق و قد را با شلوار مرجع مقایسه کرده‌ای.</li><li>می‌دانی پارچه ساختارمندتر می‌خواهی یا نرم‌تر.</li><li>کفش اصلی استایل را در نظر گرفته‌ای.</li><li>جزئیات زاپ، جیب و دوخت را در چند نما دیده‌ای.</li><li>دستور مراقبت و اطلاعات محصول را خوانده‌ای.</li></ul>
<p>برای مقایسه مدل‌های فعلی، <a href="JEANS_URL">شلوارهای جین Gramiss</a> را ببین. اگر می‌خواهی بین همه فیت‌ها و جنس‌های پایین‌تنه حرکت کنی، <a href="PANTS_URL">دسته کامل شلوارهای Gramiss</a> نقطه شروع گسترده‌تری است.</p>
<p><strong>جمع‌بندی:</strong> خرید جین موفق از اندازه‌های واقعی شروع می‌شود. کمر مناسب را از حجم دلخواه جدا کن، فاق و قد را کنار دمپا ببین و بعد رنگ، جزئیات و قیمت را وارد تصمیم کن.</p>
HTML;
$content8=str_replace(['A1_URL','A2_URL','TSHIRT_URL'],[esc_url(get_permalink($a1)),esc_url(get_permalink($a2)),esc_url($tu)],$content8);$content9=str_replace(['A3_URL','A7_URL','JEANS_URL','PANTS_URL'],[esc_url(get_permalink($a3)),esc_url(get_permalink($a7)),esc_url($ju),esc_url($pu)],$content9);
$a8=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای خرید تیشرت مردانه؛ فیت، اندازه، پارچه، دوخت و چاپ','post_name'=>$slug8,'post_excerpt'=>'برای خرید تیشرت مردانه، فیت و اندازه واقعی لباس را با پارچه، یقه، دوخت و چاپ کنار هم بررسی کنید و فقط به سایز اسمی یا قیمت تکیه نکنید.','post_content'=>$content8,'post_category'=>[(int)$buy->term_id],'post_author'=>1]),true);if(is_wp_error($a8)){http_response_code(500);echo wp_json_encode(['error'=>'a8 insert','message'=>$a8->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a9=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'راهنمای خرید شلوار جین مردانه؛ فیت، قد، پارچه و جزئیات','post_name'=>$slug9,'post_excerpt'=>'در خرید شلوار جین مردانه، کمر مناسب را از حجم فیت جدا کنید و فاق، ران، دمپا، قد، پارچه و جزئیات را با شلوار مرجع مقایسه کنید.','post_content'=>$content9,'post_category'=>[(int)$buy->term_id],'post_author'=>1]),true);if(is_wp_error($a9)){wp_delete_post($a8,true);http_response_code(500);echo wp_json_encode(['error'=>'a9 insert','message'=>$a9->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a8u=get_permalink($a8);$a9u=get_permalink($a9);$meta=[$a8=>['rank_math_title'=>'راهنمای خرید تیشرت مردانه؛ فیت، جنس و دوخت','rank_math_description'=>'راهنمای خرید تیشرت مردانه؛ فیت، اندازه واقعی، پارچه، یقه، دوخت و چاپ را بررسی کنید و قبل از خرید آنلاین با یک چک‌لیست ثابت مقایسه کنید.','rank_math_focus_keyword'=>'راهنمای خرید تیشرت مردانه'],$a9=>['rank_math_title'=>'راهنمای خرید شلوار جین مردانه؛ فیت و اندازه','rank_math_description'=>'راهنمای خرید شلوار جین مردانه؛ فیت، کمر، فاق، ران، دمپا، قد و رفتار پارچه را بررسی کنید و شلوار مناسب‌تری برای استایل خود انتخاب کنید.','rank_math_focus_keyword'=>'راهنمای خرید شلوار جین مردانه']];foreach($meta as $id=>$mm){foreach($mm as $k=>$v)update_post_meta($id,$k,$v);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}
$b2='<div data-g1-cluster-wave="89-tshirt"><h2>قبل از خرید، معیارهای تیشرت را یک‌جا بررسی کن</h2><p>بعد از تعیین سایز، <a href="'.esc_url($a8u).'">راهنمای خرید تیشرت مردانه</a> را ببین تا پارچه، یقه، دوخت و چاپ را هم با یک چک‌لیست ثابت مقایسه کنی.</p></div>';$r2=wp_update_post(wp_slash(['ID'=>$a2->ID,'post_content'=>$a2->post_content."\n".$b2]),true);
$b3='<div data-g1-cluster-wave="89-jeans"><h2>برای خرید جین، فیت را با جزئیات محصول ترکیب کن</h2><p>بعد از شناخت بگ، نیم‌بگ و فول‌بگ، <a href="'.esc_url($a9u).'">راهنمای خرید شلوار جین مردانه</a> را ببین تا کمر، فاق، قد، پارچه و جزئیات را هم وارد تصمیم کنی.</p></div>';$r3=wp_update_post(wp_slash(['ID'=>$a3->ID,'post_content'=>$a3->post_content."\n".$b3]),true);if(is_wp_error($r2)||is_wp_error($r3)){wp_delete_post($a9,true);wp_delete_post($a8,true);http_response_code(500);echo wp_json_encode(['error'=>'bridge update']);exit;}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'buy'=>['count'=>(int)get_term($buy->term_id)->count,'url'=>get_term_link($buy)],'fit'=>['count'=>(int)get_term($fit->term_id)->count,'url'=>get_term_link($fit)],'fabric'=>['count'=>(int)get_term($fabric->term_id)->count,'url'=>get_term_link($fabric)],'style'=>['count'=>(int)get_term($style->term_id)->count,'url'=>get_term_link($style)],'a2'=>get_permalink($a2),'a3'=>get_permalink($a3),'a8'=>['id'=>(int)$a8,'url'=>$a8u,'focus'=>get_post_meta($a8,'rank_math_focus_keyword',true)],'a9'=>['id'=>(int)$a9,'url'=>$a9u,'focus'=>get_post_meta($a9,'rank_math_focus_keyword',true)],'blog'=>get_permalink(22)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save(name,php);s,b,_,_=get(BASE+'/'+name+'?t='+str(int(time.time())),240);txt=b.decode('utf-8','replace');print('WRITE',s,txt)
if s!=200:raise SystemExit('wave89 write failed')
d=json.loads(txt);a8=d['a8']['url'];a9=d['a9']['url'];buy=d['buy']['url'];errors=[]
if d.get('published')!=9 or d['buy']['count']!=2 or d['fit']['count']!=3 or d['fabric']['count']!=2 or d['style']['count']!=2:errors.append('post/category counts drift')
if d['a8']['focus']!='راهنمای خرید تیشرت مردانه' or d['a9']['focus']!='راهنمای خرید شلوار جین مردانه':errors.append('focus keyword mismatch')
pages={}
for label,u,frag in [('A8',a8,'راهنمای خرید تیشرت مردانه'),('A9',a9,'راهنمای خرید شلوار جین مردانه')]:
 st,r,f,_=get(u+'?t='+str(int(time.time())),150);h=head(r);body=r.decode('utf-8','replace');pages[label]=(body,h);print('LIVE_'+label,st,f,json.dumps(h,ensure_ascii=False,separators=(',',':')),'LEN',len(body),'H2',body.count('<h2>'),'BLOGPOSTING',('BlogPosting' in body))
 if st!=200 or 'g1-editorial-single' not in body or frag not in body:errors.append(label+' render')
 if norm(h.get('canonical',''))!=norm(u):errors.append(label+' canonical')
 rob=h.get('robots','').lower()
 if 'noindex' in rob or 'index' not in rob or 'follow' not in rob:errors.append(label+' indexability')
 if 'BlogPosting' not in body or re.search(r'"@type"\s*:\s*"Product"',body,re.I):errors.append(label+' schema')
 if body.count('<h2>')<10:errors.append(label+' structure')
for label,u,marker,target in [('A2',d['a2'],'data-g1-cluster-wave="89-tshirt"',a8),('A3',d['a3'],'data-g1-cluster-wave="89-jeans"',a9)]:
 st,r,f,_=get(u+'?t='+str(int(time.time())),150);body=r.decode('utf-8','replace');print('BRIDGE_'+label,st,marker in body,target in body)
 if st!=200 or marker not in body or target not in body:errors.append(label+' bridge')
if commerce['tshirt'] not in pages['A8'][0]:errors.append('A8 commerce link')
if commerce['jeans'] not in pages['A9'][0] or commerce['pants'] not in pages['A9'][0]:errors.append('A9 commerce links')
for label,u,need in [('BUY',buy,['راهنمای خرید تیشرت مردانه','راهنمای خرید شلوار جین مردانه']),('STYLE',d['style']['url'],['استایل با پیراهن لینن','با شلوار بگ مردانه']),('FIT',d['fit']['url'],['تیشرت باکسی','تفاوت شلوار بگ']),('FABRIC',d['fabric']['url'],['پارچه لینن','شست‌وشوی پیراهن لینن'])]:
 st,r,f,_=get(u+'?t='+str(int(time.time())),150);h=head(r);body=r.decode('utf-8','replace');print('CAT_'+label,st,f,json.dumps(h,ensure_ascii=False,separators=(',',':')))
 if st!=200 or not all(x in body for x in need) or 'noindex' in h.get('robots','').lower() or not h.get('canonical'):errors.append(label+' category')
st,r,f,_=get(d['blog']+'?t='+str(int(time.time())),150);body=r.decode('utf-8','replace');print('BLOG',st,f,'A8',('راهنمای خرید تیشرت مردانه' in body),'A9',('راهنمای خرید شلوار جین مردانه' in body))
if st!=200 or 'راهنمای خرید تیشرت مردانه' not in body or 'راهنمای خرید شلوار جین مردانه' not in body:errors.append('blog cards')
ss,posts=sitemap('post-sitemap.xml');pn={norm(x) for x in posts};print('POST_SITEMAP',ss,len(posts))
if ss!=200 or norm(a8) not in pn or norm(a9) not in pn:errors.append('post sitemap')
ss,cats=sitemap('category-sitemap.xml');cn={norm(x) for x in cats};print('CATEGORY_SITEMAP',ss,len(cats),json.dumps(cats,ensure_ascii=False))
if ss!=200 or not all(norm(x) in cn for x in (buy,d['style']['url'],d['fit']['url'],d['fabric']['url'])):errors.append('category sitemap')
ps1,pl1=sitemap('product-sitemap.xml');pl1=sorted(pl1);print('PRODUCT_SITEMAP_POST',ps1,len(pl1),hashlib.sha256('\n'.join(pl1).encode()).hexdigest())
if ps1!=200 or pl1!=pl0:errors.append('product sitemap changed')
post={f:hashlib.sha256(read_theme(f).encode()).hexdigest() for f in protected};print('PROTECTED_POST',json.dumps(post,ensure_ascii=False,sort_keys=True))
if post!=pre:errors.append('protected UI changed')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));rb='gramiss-editorial-wave-8-9-rollback-'+nonce+'.php';rollback=r'''<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);foreach([sanitize_title('راهنمای خرید تیشرت مردانه'),sanitize_title('راهنمای خرید شلوار جین مردانه')] as $s){$p=get_page_by_path($s,OBJECT,'post');if($p)wp_delete_post($p->ID,true);}foreach([[459,'89-tshirt'],[460,'89-jeans']] as $x){$p=get_post($x[0]);if($p&&strpos($p->post_content,'data-g1-cluster-wave="'.$x[1].'"')!==false){$pat='/\s*<div data-g1-cluster-wave="'.preg_quote($x[1],'/').'">.*?<\/div>\s*$/s';$c=preg_replace($pat,'',$p->post_content,1);wp_update_post(wp_slash(['ID'=>$p->ID,'post_content'=>$c]));}}if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo 'ROLLED_BACK';?>''';save(rb,rollback);rs,rr,_,_=get(BASE+'/'+rb+'?t='+str(int(time.time())),180);print('ROLLBACK',rs,rr[:100]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS EDITORIAL WAVE 8-9');print('ARTICLE_08',a8);print('ARTICLE_09',a9);print('BUY_CATEGORY',buy);print('HOME_SHA_PRESERVED',post['front-page.php'])
