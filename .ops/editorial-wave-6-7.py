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
 req=urllib.request.Request(u,headers={'User-Agent':'GramissEditorialWave67/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
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
ps0,pl0=sitemap('product-sitemap.xml');pl0=sorted(pl0);psha=hashlib.sha256('\n'.join(pl0).encode()).hexdigest();print('PRODUCT_SITEMAP_PRE',ps0,len(pl0),psha)
if ps0!=200:raise SystemExit('ABORT product sitemap')
commerce={'linen':BASE+'/product-category/shirt/linen-shirt/','pants':BASE+'/product-category/pants/','tshirt':BASE+'/product-category/tshirt/','sneakers':BASE+'/product-category/sneakers/'}
for k,u in commerce.items():
 s,r,f,_=get(u+'?t='+str(int(time.time())),120);h=head(r);print('COMMERCE_PRE',k,s,f,json.dumps(h,ensure_ascii=False,separators=(',',':')))
 if s!=200 or 'noindex' in h.get('robots','').lower() or norm(h.get('canonical',''))!=norm(u):raise SystemExit('ABORT commerce '+k)
nonce=hashlib.sha256((str(time.time())+pre['front-page.php']).encode()).hexdigest()[:14];name='gramiss-editorial-wave-6-7-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$slug6=sanitize_title('استایل با پیراهن لینن مردانه');$slug7=sanitize_title('با شلوار بگ مردانه چی بپوشیم');$a3=get_post(460);$a4=get_post(463);$a5=get_post(464);$a6x=get_page_by_path($slug6,OBJECT,'post');$a7x=get_page_by_path($slug7,OBJECT,'post');$fit=get_term_by('slug','fit-size-guide','category');$fabric=get_term_by('slug','fabric-care','category');$style=get_term_by('slug','style-guide','category');$buy=get_term_by('slug','buying-guide','category');$published=(int)wp_count_posts('post')->publish;
$linen=get_term_by('slug','linen-shirt','product_cat');$pants=get_term_by('slug','pants','product_cat');$tshirt=get_term_by('slug','tshirt','product_cat');$sneakers=get_term_by('slug','sneakers','product_cat');
if(!$a3||!$a4||!$a5||$a3->post_status!=='publish'||$a4->post_status!=='publish'||$a5->post_status!=='publish'||$a6x||$a7x||!$fit||!$fabric||!$style||!$buy||!$linen||!$pants||!$tshirt||!$sneakers||$published!==5||(int)$fit->count!==3||(int)$fabric->count!==2||(int)$style->count!==0){http_response_code(409);echo wp_json_encode(['error'=>'baseline drift','published'=>$published,'a6'=>$a6x?$a6x->ID:null,'a7'=>$a7x?$a7x->ID:null,'fit'=>$fit?$fit->count:null,'fabric'=>$fabric?$fabric->count:null,'style'=>$style?$style->count:null],JSON_UNESCAPED_UNICODE);exit;}
if(strpos($a4->post_content,'data-g1-cluster-wave="67-linen"')!==false||strpos($a3->post_content,'data-g1-cluster-wave="67-bag"')!==false){http_response_code(409);echo wp_json_encode(['error'=>'wave67 marker exists']);exit;}
$lu=get_term_link($linen);$pu=get_term_link($pants);$tu=get_term_link($tshirt);$su=get_term_link($sneakers);foreach([$lu,$pu,$tu,$su] as $x){if(is_wp_error($x)){http_response_code(409);echo wp_json_encode(['error'=>'commerce term url']);exit;}}
$content6=<<<'HTML'
<p>استایل با پیراهن لینن مردانه زمانی بهتر نتیجه می‌دهد که به‌جای دنبال‌کردن یک فرمول ثابت، سه چیز را کنار هم ببینی: حجم خود پیراهن، فرم شلوار و وزن بصری کفش. لینن می‌تواند از یک استایل کاملاً روزمره تا اسمارت‌کژوال حرکت کند، اما همان پیراهن با شلوار و کفش متفاوت حس کاملاً دیگری می‌سازد.</p>
<p>یک نکته هم درباره خود پارچه مهم است: نام «لینن» به‌تنهایی ترکیب دقیق الیاف را مشخص نمی‌کند. اگر این موضوع برایت مهم است، ابتدا <a href="A4_URL">راهنمای شناخت پارچه لینن</a> را ببین و مشخصات همان لباس را بررسی کن.</p>
<h2>از فیت پیراهن شروع کن، نه از رنگ</h2>
<p>قبل از ست‌کردن رنگ‌ها، ببین پیراهن چقدر آزاد است، سرشانه کجا قرار می‌گیرد و قد لباس تا چه نقطه‌ای می‌رسد. پیراهنی که رها و بلند است با یک شلوار پرحجم، سیلوئت کاملاً آزاد می‌سازد؛ مدل جمع‌وجورتر کنار شلوار راسته یا پارچه‌ای می‌تواند مرتب‌تر دیده شود.</p>
<p>هدف این نیست که همیشه یکی از دو بخش جذب باشد. هم ترکیب آزاد با آزاد و هم آزاد با جمع‌وجور می‌تواند درست کار کند؛ تفاوت در این است که آگاهانه بدانیم کدام حجم قرار است نقطه اصلی استایل باشد.</p>
<h2>پیراهن لینن با شلوار پارچه‌ای</h2>
<p>شلوار پارچه‌ای با خطوط ساده می‌تواند با بافت طبیعی لینن تعادل خوبی بسازد. اگر پیراهن آزاد است، شلواری با افت تمیز و دمپای کنترل‌شده ظاهر مرتب‌تری ایجاد می‌کند. اگر شلوار هم بگ یا فول‌بگ است، قد پیراهن را طوری انتخاب کن که کل استایل فقط به یک حجم بزرگ و بدون مرز تبدیل نشود.</p>
<p>رنگ‌های خنثی مثل کرم، طوسی، سرمه‌ای و قهوه‌ای فقط مثال‌های کم‌ریسک برای شروع‌اند؛ قانون اجباری نیستند. مهم‌تر از نام رنگ، میزان تضاد و تکرار آن در کفش و اکسسوری است.</p>
<h2>پیراهن لینن با جین</h2>
<p>جین می‌تواند ظاهر طبیعی لینن را روزمره‌تر کند. جین آبی روشن در کنار پیراهن‌های روشن حس سبک‌تری می‌دهد و جین تیره می‌تواند تضاد بیشتری بسازد. اگر جین زاپ‌دار یا پرجزئیات است، ساده نگه‌داشتن بقیه اجزا کمک می‌کند بافت‌ها با هم رقابت نکنند.</p>
<p>در جین‌های بگ، به محل قرارگیری دمپا روی کفش توجه کن. قد شلوار و حجم کفش می‌تواند بیشتر از رنگ پیراهن روی نتیجه نهایی اثر بگذارد.</p>
<h2>پیراهن را باز بپوشیم یا بسته؟</h2>
<p>پوشیدن پیراهن لینن باز روی تیشرت، یک لایه سبک برای استایل روزمره می‌سازد. در این حالت بهتر است طول تیشرت و پیراهن را کنار هم ببینی؛ اگر هر دو خیلی بلند باشند، لایه‌ها ممکن است فرم پایین‌تنه را پنهان کنند. تیشرت کوتاه‌تر یا هم‌قد با نسبت کنترل‌شده معمولاً خواناتر است.</p>
<p>برای دیدن گزینه‌های فعلی بالاتنه می‌توانی <a href="TSHIRT_URL">دسته تیشرت‌های Gramiss</a> را بررسی کنی و قبل از انتخاب، قد و عرض واقعی هر مدل را ببینی.</p>
<h2>پیراهن داخل شلوار یا بیرون؟</h2>
<p>اگر پیراهن کوتاه و لبه آن برای پوشیدن بیرون طراحی شده، بیرون گذاشتن آن ظاهر راحت‌تری می‌سازد. داخل‌زدن کامل پیراهن، خط کمر و نسبت پاها را واضح‌تر می‌کند و می‌تواند استایل را مرتب‌تر نشان دهد. نیمه‌داخل‌زدن هم یک انتخاب است، اما باید عمدی و تمیز باشد تا شبیه به‌هم‌ریختگی اتفاقی دیده نشود.</p>
<p>فاق شلوار در این تصمیم مهم است؛ یک پیراهن داخل شلوار فاق‌بلند نسبت متفاوتی از همان پیراهن با شلوار فاق پایین می‌سازد.</p>
<h2>آستین کوتاه یا آستین بلند تاخورده؟</h2>
<p>آستین کوتاه به‌طور طبیعی ظاهر ساده‌تر و تابستانی‌تری دارد. در مدل آستین بلند، بالا زدن آستین می‌تواند حجم اطراف مچ را کم کند و استایل را غیررسمی‌تر کند. تا را خیلی ضخیم نکن؛ چند لایه سنگین پارچه روی ساعد می‌تواند ظاهر طبیعی و سبک پیراهن را از بین ببرد.</p>
<p>اگر پیراهن ساختارمندتر است، مرتب نگه‌داشتن خط یقه و سرآستین اهمیت بیشتری پیدا می‌کند.</p>
<h2>چه کفشی با پیراهن لینن مردانه هماهنگ می‌شود؟</h2>
<p>برای استایل روزمره، کتانی ساده با حجم متوسط انتخاب قابل‌انعطافی است. برای ظاهر مرتب‌تر، کفش‌های کم‌جزئیات مثل لوفر یا مدل‌های چرمی ساده می‌توانند مناسب باشند. انتخاب نهایی به شلوار وابسته است؛ کفش را فقط با رنگ پیراهن ست نکن.</p>
<p>اگر شلوار دمپای باز دارد، کفش خیلی کم‌حجم ممکن است زیر آن کمتر دیده شود. اگر شلوار راسته یا کوتاه‌تر است، همان کفش می‌تواند حضور کافی داشته باشد. <a href="SNEAKERS_URL">کتونی‌های فعلی Gramiss</a> را می‌توانی در کنار شلواری که می‌خواهی بپوشی مقایسه کنی.</p>
<h2>چطور رنگ‌ها را بدون شلوغی ترکیب کنیم؟</h2>
<p>یک روش ساده این است که یک رنگ اصلی، یک رنگ پشتیبان و حداکثر یک نقطه تأکید داشته باشی. برای مثال پیراهن آبی با شلوار کرم و کفش خنثی، یا پیراهن قهوه‌ای با شلوار طوسی و کفش تیره. این‌ها نسخه قطعی نیستند؛ فقط نشان می‌دهند چطور می‌توان تعداد رنگ‌های فعال را کنترل کرد.</p>
<p>اگر پیراهن بافت واضح دارد، لازم نیست همزمان چند طرح بزرگ دیگر وارد استایل شود. بافت خود لینن می‌تواند نقش جزئیات بصری را بازی کند.</p>
<h2>استایل مونوکروم با لینن</h2>
<p>مونوکروم الزاماً به معنی یک رنگ کاملاً یکسان نیست. می‌توانی چند تون نزدیک از یک خانواده را کنار هم قرار بدهی و تفاوت را از طریق بافت ایجاد کنی. لینن در این حالت مفید است چون سطح پارچه حتی در رنگ‌های نزدیک، عمق بصری ایجاد می‌کند.</p>
<p>برای جلوگیری از تخت‌شدن استایل، کفش یا کمربند می‌تواند کمی تیره‌تر یا روشن‌تر از بقیه ترکیب باشد.</p>
<h2>اکسسوری‌ها را چقدر وارد استایل کنیم؟</h2>
<p>اگر پیراهن و شلوار هر دو بافت یا حجم مشخصی دارند، اکسسوری‌های ساده معمولاً کافی‌اند. ساعت، عینک یا یک کیف مینیمال می‌تواند استایل را کامل کند بدون اینکه تمرکز از لباس‌ها برداشته شود. اگر از گردنبند استفاده می‌کنی، بازبودن یقه و طول زنجیر را با هم ببین.</p>
<p>قانون «کمتر همیشه بهتر است» وجود ندارد؛ معیار این است که هر آیتم دلیل بصری داشته باشد.</p>
<h2>اشتباهات رایج در استایل پیراهن لینن</h2>
<ul><li>انتخاب شلوار و کفش فقط بر اساس رنگ پیراهن و نادیده‌گرفتن حجم آن‌ها.</li><li>فرض اینکه همه پیراهن‌های لینن فیت و رفتار یکسان دارند.</li><li>پوشیدن چند لایه بلند روی هم بدون مشخص‌بودن خط کمر یا فرم پایین‌تنه.</li><li>استفاده از کفش بسیار ظریف زیر دمپای خیلی حجیم بدون توجه به نسبت‌ها.</li><li>اتوکردن بیش از حد برای حذف تمام بافت طبیعی پارچه.</li><li>اعتماد به نام «لینن» بدون بررسی ترکیب الیاف و دستور مراقبت.</li></ul>
<h2>سه فرمول ساده برای شروع</h2>
<ul><li><strong>روزمره:</strong> پیراهن لینن باز + تیشرت ساده + جین یا شلوار آزاد کنترل‌شده + کتانی ساده.</li><li><strong>مینیمال:</strong> پیراهن بسته + شلوار پارچه‌ای ساده + دو یا سه تون نزدیک + کفش کم‌جزئیات.</li><li><strong>اسمارت‌کژوال:</strong> پیراهن با یقه مرتب + شلوار با افت تمیز + کفش چرمی ساده یا لوفر.</li></ul>
<p>برای انتخاب خود پیراهن، <a href="LINEN_URL">مدل‌های فعلی پیراهن لینن Gramiss</a> را ببین. اگر بعد از پوشیدن می‌خواهی فرم و بافت لباس را بهتر حفظ کنی، <a href="A5_URL">راهنمای شست‌وشو و اتوکشی پیراهن لینن</a> را هم داشته باش.</p>
<p><strong>جمع‌بندی:</strong> استایل لینن بیشتر از یک ترکیب رنگ، مسئله نسبت‌هاست. فیت پیراهن، حجم شلوار و وزن بصری کفش را با هم ببین؛ بعد رنگ و اکسسوری را روی این پایه اضافه کن.</p>
HTML;
$content7=<<<'HTML'
<p>اگر می‌پرسی «با شلوار بگ مردانه چی بپوشیم؟» پاسخ کوتاه این است: هر چیزی که نسبت حجم، قد و کفش را آگاهانه کنترل کند. شلوار بگ فضای زیادی در پایین‌تنه می‌سازد، اما این به معنی آن نیست که بالاتنه حتماً باید جذب یا حتماً باید اورسایز باشد. هر دو مسیر می‌توانند درست باشند؛ فقط نتیجه بصری متفاوتی می‌سازند.</p>
<p>اگر هنوز بین بگ، نیم‌بگ و فول‌بگ تفاوت را دقیق نمی‌دانی، اول <a href="A3_URL">راهنمای تفاوت این سه فیت</a> را ببین. وقتی حجم واقعی شلوار مشخص شد، انتخاب تیشرت و کفش بسیار ساده‌تر می‌شود.</p>
<h2>اول حجم واقعی شلوار را مشخص کن</h2>
<p>اسم «بگ» روی لیبل کافی نیست. عرض ران، دمپا، فاق و قد شلوار تعیین می‌کنند پایین‌تنه چقدر حجم دارد. دو شلوار با یک اسم ممکن است یکی نزدیک نیم‌بگ و دیگری نزدیک فول‌بگ دیده شود. عکس تنخور و اندازه‌های واقعی را قبل از ساختن استایل بررسی کن.</p>
<p>هرچه دمپا بازتر و قد بلندتر باشد، حضور کفش و طول بالاتنه اهمیت بیشتری پیدا می‌کند.</p>
<h2>تیشرت باکسی با شلوار بگ</h2>
<p>تیشرت باکسی به‌خاطر عرض بیشتر و قد کنترل‌شده می‌تواند کنار شلوار بگ یک سیلوئت آزاد ولی تفکیک‌شده بسازد. نکته کلیدی قد تیشرت است؛ اگر هم تیشرت بسیار بلند باشد و هم شلوار پرحجم، مرز بین بالاتنه و پایین‌تنه کمتر دیده می‌شود.</p>
<p>برای مدل‌های موجود، <a href="TSHIRT_URL">دسته تیشرت‌های Gramiss</a> را می‌توانی از نظر قد و عرض واقعی مقایسه کنی.</p>
<h2>آیا تیشرت فیت با شلوار بگ اشتباه است؟</h2>
<p>نه. تیشرت جمع‌وجورتر تضاد بیشتری با حجم شلوار ایجاد می‌کند و می‌تواند انتخاب عمدی باشد. در مقابل تیشرت آزاد یا باکسی حجم را در کل استایل پخش می‌کند. هیچ‌کدام ذاتاً بهتر نیستند؛ انتخاب به تصویری که می‌خواهی بسازی بستگی دارد.</p>
<p>به‌جای قانون ثابت، در آینه یا عکس تمام‌قد ببین نقطه بیشترین حجم کجاست و آیا وزن بصری بالا و پایین لباس با هم ارتباط دارند.</p>
<h2>تیشرت گرافیکی یا ساده؟</h2>
<p>اگر شلوار زاپ، جیب کارگو یا شست‌وشوی پرجزئیات دارد، تیشرت ساده اجازه می‌دهد تمرکز روی پایین‌تنه بماند. اگر شلوار ساده است، چاپ یا گرافیک تیشرت می‌تواند نقطه اصلی بالاتنه شود. استفاده همزمان از چند جزئیات بزرگ ممکن است استایل را شلوغ کند، اما این هم انتخاب طراحی است نه ممنوعیت.</p>
<p>رنگ چاپ را در کنار رنگ کفش یا اکسسوری ببین تا اجزای استایل از هم جدا به نظر نرسند.</p>
<h2>پیراهن با شلوار بگ</h2>
<p>پیراهن آزاد می‌تواند با شلوار بگ استایل رها و لایه‌ای بسازد. اگر پیراهن را باز روی تیشرت می‌پوشی، طول هر دو لایه را کنترل کن. پیراهن کوتاه‌تر یا مدلی که لبه آن نزدیک خط کمر می‌ایستد معمولاً فرم شلوار را واضح‌تر نشان می‌دهد.</p>
<p>برای ظاهر مرتب‌تر می‌توانی از پیراهن با ساختار بیشتر و شلوار بگ پارچه‌ای با افت تمیز استفاده کنی؛ لازم نیست شلوار بگ فقط به استریت‌ویر محدود شود.</p>
<h2>هودی و سویشرت با بگ</h2>
<p>در فصل سرد، هودی یا سویشرت حجیم می‌تواند حجم را در بالاتنه هم تکرار کند. اگر هر دو بخش خیلی بلند باشند، استایل کشیده و سنگین می‌شود؛ کوتاه‌تر بودن یکی از لایه‌ها می‌تواند مرزها را واضح‌تر کند. ضخامت کفش نیز در این ترکیب مهم‌تر می‌شود.</p>
<p>در لایه‌پوشی، بهتر است از پهلو هم استایل را ببینی؛ حجم واقعی فقط در نمای روبه‌رو مشخص نمی‌شود.</p>
<h2>با شلوار بگ چه کفشی بپوشیم؟</h2>
<p>کفش باید با عرض دمپا و میزان شکست شلوار هماهنگ باشد. کتانی با حجم متوسط معمولاً زیر دمپای باز حضور کافی دارد. کفش خیلی باریک ممکن است زیر شلوار فول‌بگ کمتر دیده شود، در حالی که کفش بسیار حجیم می‌تواند دمپا را بالا نگه دارد و فرم شلوار را تغییر دهد.</p>
<p>برای مقایسه می‌توانی <a href="SNEAKERS_URL">کتونی‌های فعلی Gramiss</a> را کنار عکس و اندازه دمپای شلوار بررسی کنی.</p>
<h2>قد شلوار و شکست روی کفش</h2>
<p>یک شکست نرم روی رویه کفش می‌تواند فرم بگ را طبیعی نگه دارد. اگر پارچه در چند لایه متراکم روی زمین جمع شود، هم ظاهر اصلی الگو پنهان می‌شود و هم لبه شلوار سریع‌تر ساییده می‌شود. از طرف دیگر، کوتاهی زیاد ممکن است حجم پایین شلوار را قطع کند.</p>
<p>بهترین روش این است که قد را با همان کفشی بسنجی که بیشتر قرار است با شلوار بپوشی.</p>
<h2>جین بگ و شلوار بگ پارچه‌ای یک استایل ندارند</h2>
<p>جین ساختارمندتر معمولاً خطوط حجم را واضح نگه می‌دارد، در حالی که پارچه ریزشی حرکت بیشتری دارد و نرم‌تر روی کفش می‌افتد. برای همین یک تیشرت و یک کفش ثابت کنار این دو شلوار نتیجه متفاوتی می‌دهد.</p>
<p>در <a href="PANTS_URL">دسته شلوارهای Gramiss</a> مدل‌های جین و پارچه‌ای را از نظر افت، دمپا و قد جداگانه مقایسه کن.</p>
<h2>ترکیب رنگ با شلوار بگ</h2>
<p>اگر تازه با این فیت کار می‌کنی، رنگ‌های خنثی در یکی از بخش‌ها تصمیم را ساده‌تر می‌کنند. شلوار آبی با تیشرت سفید یا خاکستری، شلوار ذغالی با کرم یا مشکی و شلوار روشن با بالاتنه تیره مثال‌هایی برای فهم تضادند، نه فرمول‌های اجباری.</p>
<p>اگر می‌خواهی ظاهر یکپارچه‌تر باشد، تون‌های نزدیک انتخاب کن؛ اگر می‌خواهی خط کمر و حجم شلوار واضح‌تر شود، تضاد رنگی بالاتنه و پایین‌تنه را بیشتر کن.</p>
<h2>استایل مونوکروم با شلوار بگ</h2>
<p>در مونوکروم، تفاوت بافت‌ها کمک می‌کند حجم‌ها از هم جدا شوند. مثلاً جین، تیشرت پنبه‌ای و کفش چرمی یا مش با وجود نزدیک‌بودن رنگ‌ها سطوح متفاوتی می‌سازند. لازم نیست تمام قطعات دقیقاً یک کد رنگ داشته باشند.</p>
<p>می‌توانی کفش را کمی روشن‌تر یا تیره‌تر بگیری تا پایین استایل یک نقطه پایان مشخص داشته باشد.</p>
<h2>اکسسوری در استایل بگ</h2>
<p>کلاه، کیف دوشی، زنجیر یا کمربند می‌توانند جهت استایل را عوض کنند. اگر تیشرت گرافیکی و شلوار پرجزئیات داری، اکسسوری‌های ساده‌تر معمولاً خواناترند. اگر لباس‌ها مینیمال‌اند، یک اکسسوری مشخص می‌تواند نقطه تأکید باشد.</p>
<p>مقیاس اکسسوری را هم با حجم لباس‌ها بسنج؛ یک کیف بسیار کوچک کنار سیلوئت خیلی حجیم حس متفاوتی از یک کیف متوسط ایجاد می‌کند.</p>
<h2>اشتباهات رایج در استایل شلوار بگ</h2>
<ul><li>بزرگ‌تر خریدن سایز کمر برای ساختن حجم به‌جای انتخاب الگوی بگ واقعی.</li><li>نادیده‌گرفتن قد شلوار و تنظیم‌نکردن آن با کفش اصلی.</li><li>فرض اینکه بالاتنه حتماً باید جذب یا حتماً باید اورسایز باشد.</li><li>تمرکز روی رنگ و نادیده‌گرفتن حجم تیشرت و کفش.</li><li>پوشاندن کامل خط کمر با چند لایه بسیار بلند بدون قصد طراحی.</li><li>انتخاب کفش فقط از روی ترند بدون دیدن عرض دمپا.</li></ul>
<h2>چهار فرمول سریع برای شروع</h2>
<ul><li><strong>مینیمال:</strong> بگ ساده + تیشرت باکسی بدون چاپ + کتانی کم‌جزئیات.</li><li><strong>استریت:</strong> جین بگ + تیشرت گرافیکی + کتانی با حجم متوسط + اکسسوری محدود.</li><li><strong>کنتراست حجم:</strong> بگ پرحجم + تیشرت جمع‌وجورتر + کفش متناسب با دمپا.</li><li><strong>اسمارت‌کژوال:</strong> بگ پارچه‌ای ریزشی + پیراهن ساده + کفش کم‌جزئیات با فرم تمیز.</li></ul>
<p><strong>جمع‌بندی:</strong> جواب «با شلوار بگ مردانه چی بپوشیم؟» به یک نوع تیشرت یا کفش محدود نیست. حجم شلوار، قد بالاتنه و اندازه کفش را مثل سه جزء یک سیستم ببین؛ وقتی این نسبت‌ها درست باشند، رنگ و جزئیات را می‌توان آزادانه‌تر انتخاب کرد.</p>
HTML;
$content6=str_replace(['A4_URL','A5_URL','LINEN_URL','TSHIRT_URL','SNEAKERS_URL'],[esc_url(get_permalink($a4)),esc_url(get_permalink($a5)),esc_url($lu),esc_url($tu),esc_url($su)],$content6);$content7=str_replace(['A3_URL','TSHIRT_URL','SNEAKERS_URL','PANTS_URL'],[esc_url(get_permalink($a3)),esc_url($tu),esc_url($su),esc_url($pu)],$content7);
$a6=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'استایل با پیراهن لینن مردانه؛ شلوار، کفش و ترکیب رنگ','post_name'=>$slug6,'post_excerpt'=>'برای استایل با پیراهن لینن مردانه، فیت پیراهن، حجم شلوار و وزن بصری کفش را کنار هم ببینید و بعد رنگ و اکسسوری را انتخاب کنید.','post_content'=>$content6,'post_category'=>[(int)$style->term_id],'post_author'=>1]),true);if(is_wp_error($a6)){http_response_code(500);echo wp_json_encode(['error'=>'a6 insert','message'=>$a6->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a7=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'با شلوار بگ مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و قد شلوار','post_name'=>$slug7,'post_excerpt'=>'شلوار بگ مردانه را با تیشرت، پیراهن و کفش بر اساس حجم، قد و عرض دمپا ست کنید؛ بدون قانون ثابت درباره جذب یا اورسایز بودن بالاتنه.','post_content'=>$content7,'post_category'=>[(int)$style->term_id],'post_author'=>1]),true);if(is_wp_error($a7)){wp_delete_post($a6,true);http_response_code(500);echo wp_json_encode(['error'=>'a7 insert','message'=>$a7->get_error_message()],JSON_UNESCAPED_UNICODE);exit;}
$a6u=get_permalink($a6);$a7u=get_permalink($a7);$meta=[$a6=>['rank_math_title'=>'استایل با پیراهن لینن مردانه؛ شلوار و کفش مناسب','rank_math_description'=>'استایل با پیراهن لینن مردانه را با انتخاب درست حجم شلوار، کفش و ترکیب رنگ بسازید؛ از روزمره تا اسمارت‌کژوال با مثال‌های کاربردی.','rank_math_focus_keyword'=>'استایل با پیراهن لینن مردانه'],$a7=>['rank_math_title'=>'با شلوار بگ مردانه چی بپوشیم؟ راهنمای استایل','rank_math_description'=>'با شلوار بگ مردانه چی بپوشیم؟ تیشرت، پیراهن و کفش را بر اساس حجم، قد شلوار و عرض دمپا انتخاب کنید و استایل متعادل‌تری بسازید.','rank_math_focus_keyword'=>'با شلوار بگ مردانه چی بپوشیم']];foreach($meta as $id=>$mm){foreach($mm as $k=>$v)update_post_meta($id,$k,$v);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}
$b4='<div data-g1-cluster-wave="67-linen"><h2>بعد از شناخت لینن، سراغ استایل برو</h2><p>برای تبدیل شناخت پارچه به یک ترکیب واقعی، <a href="'.esc_url($a6u).'">راهنمای استایل با پیراهن لینن مردانه</a> را ببین؛ شلوار، کفش و نسبت حجم‌ها را مرحله‌به‌مرحله بررسی کرده‌ایم.</p></div>';$r4=wp_update_post(wp_slash(['ID'=>$a4->ID,'post_content'=>$a4->post_content."\n".$b4]),true);
$b3='<div data-g1-cluster-wave="67-bag"><h2>بعد از انتخاب فیت، استایل شلوار بگ را کامل کن</h2><p>اگر بگ، نیم‌بگ یا فول‌بگ مناسب خودت را شناختی، <a href="'.esc_url($a7u).'">راهنمای استایل شلوار بگ مردانه</a> را ببین تا تیشرت، پیراهن، کفش و قد شلوار را کنار هم تنظیم کنی.</p></div>';$r3=wp_update_post(wp_slash(['ID'=>$a3->ID,'post_content'=>$a3->post_content."\n".$b3]),true);if(is_wp_error($r4)||is_wp_error($r3)){wp_delete_post($a7,true);wp_delete_post($a6,true);http_response_code(500);echo wp_json_encode(['error'=>'bridge update']);exit;}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'published'=>(int)wp_count_posts('post')->publish,'style'=>['count'=>(int)get_term($style->term_id)->count,'url'=>get_term_link($style)],'fit'=>['count'=>(int)get_term($fit->term_id)->count,'url'=>get_term_link($fit)],'fabric'=>['count'=>(int)get_term($fabric->term_id)->count,'url'=>get_term_link($fabric)],'a3'=>get_permalink($a3),'a4'=>get_permalink($a4),'a6'=>['id'=>(int)$a6,'url'=>$a6u,'focus'=>get_post_meta($a6,'rank_math_focus_keyword',true)],'a7'=>['id'=>(int)$a7,'url'=>$a7u,'focus'=>get_post_meta($a7,'rank_math_focus_keyword',true)],'blog'=>get_permalink(22)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save(name,php);s,b,_,_=get(BASE+'/'+name+'?t='+str(int(time.time())),240);txt=b.decode('utf-8','replace');print('WRITE',s,txt)
if s!=200:raise SystemExit('wave67 write failed')
d=json.loads(txt);a6=d['a6']['url'];a7=d['a7']['url'];style=d['style']['url'];fit=d['fit']['url'];fabric=d['fabric']['url'];errors=[]
if d.get('published')!=7:errors.append('published not 7')
if d['style']['count']!=2 or d['fit']['count']!=3 or d['fabric']['count']!=2:errors.append('editorial category counts drift')
if d['a6']['focus']!='استایل با پیراهن لینن مردانه' or d['a7']['focus']!='با شلوار بگ مردانه چی بپوشیم':errors.append('focus keyword mismatch')
pages={}
for label,u,frag in [('A6',a6,'استایل با پیراهن لینن مردانه'),('A7',a7,'با شلوار بگ مردانه چی بپوشیم')]:
 st,r,f,_=get(u+'?t='+str(int(time.time())),150);h=head(r);body=r.decode('utf-8','replace');pages[label]=(body,h);print('LIVE_'+label,st,f,json.dumps(h,ensure_ascii=False,separators=(',',':')),'LEN',len(body),'H2',body.count('<h2>'),'BLOGPOSTING',('BlogPosting' in body))
 if st!=200 or 'g1-editorial-single' not in body or frag not in body:errors.append(label+' render failed')
 if norm(h.get('canonical',''))!=norm(u):errors.append(label+' canonical')
 rob=h.get('robots','').lower()
 if 'noindex' in rob or 'index' not in rob or 'follow' not in rob:errors.append(label+' indexability')
 if 'BlogPosting' not in body or re.search(r'"@type"\s*:\s*"Product"',body,re.I):errors.append(label+' schema')
 if body.count('<h2>')<10:errors.append(label+' thin structure')
for label,u,marker,target in [('A4',d['a4'],'data-g1-cluster-wave="67-linen"',a6),('A3',d['a3'],'data-g1-cluster-wave="67-bag"',a7)]:
 st,r,f,_=get(u+'?t='+str(int(time.time())),150);body=r.decode('utf-8','replace');print('BRIDGE_'+label,st,marker in body,target in body)
 if st!=200 or marker not in body or target not in body:errors.append(label+' bridge missing')
if commerce['linen'] not in pages['A6'][0] or commerce['tshirt'] not in pages['A6'][0] or commerce['sneakers'] not in pages['A6'][0]:errors.append('A6 commerce links')
if commerce['pants'] not in pages['A7'][0] or commerce['tshirt'] not in pages['A7'][0] or commerce['sneakers'] not in pages['A7'][0]:errors.append('A7 commerce links')
for label,u,need in [('STYLE',style,['استایل با پیراهن لینن','با شلوار بگ مردانه']),('FIT',fit,['تیشرت باکسی','تفاوت شلوار بگ']),('FABRIC',fabric,['پارچه لینن','شست‌وشوی پیراهن لینن'])]:
 st,r,f,_=get(u+'?t='+str(int(time.time())),150);h=head(r);body=r.decode('utf-8','replace');print('CAT_'+label,st,f,json.dumps(h,ensure_ascii=False,separators=(',',':')))
 if st!=200 or not all(x in body for x in need) or 'noindex' in h.get('robots','').lower() or not h.get('canonical'):errors.append(label+' category')
st,r,f,_=get(BASE+'/category/buying-guide/?t='+str(int(time.time())),120);hb=head(r);print('EMPTY_BUY',st,f,json.dumps(hb,ensure_ascii=False,separators=(',',':')))
if st!=200 or 'noindex' not in hb.get('robots','').lower():errors.append('buying-guide should noindex')
st,r,f,_=get(d['blog']+'?t='+str(int(time.time())),150);body=r.decode('utf-8','replace');print('BLOG',st,f,'A6',('استایل با پیراهن لینن' in body),'A7',('با شلوار بگ مردانه' in body))
if st!=200 or 'استایل با پیراهن لینن' not in body or 'با شلوار بگ مردانه' not in body:errors.append('blog missing new cards')
ss,posts=sitemap('post-sitemap.xml');pn={norm(x) for x in posts};print('POST_SITEMAP',ss,len(posts))
if ss!=200 or norm(a6) not in pn or norm(a7) not in pn:errors.append('post sitemap')
ss,cats=sitemap('category-sitemap.xml');cn={norm(x) for x in cats};print('CATEGORY_SITEMAP',ss,len(cats),json.dumps(cats,ensure_ascii=False))
if ss!=200 or not all(norm(x) in cn for x in (style,fit,fabric)) or any('/category/buying-guide/' in x for x in cats):errors.append('category sitemap')
ps1,pl1=sitemap('product-sitemap.xml');pl1=sorted(pl1);print('PRODUCT_SITEMAP_POST',ps1,len(pl1),hashlib.sha256('\n'.join(pl1).encode()).hexdigest())
if ps1!=200 or pl1!=pl0:errors.append('product sitemap changed')
post={f:hashlib.sha256(read_theme(f).encode()).hexdigest() for f in protected};print('PROTECTED_POST',json.dumps(post,ensure_ascii=False,sort_keys=True))
if post!=pre:errors.append('protected UI changed')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));rb='gramiss-editorial-wave-6-7-rollback-'+nonce+'.php';rollback=r'''<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);foreach([sanitize_title('استایل با پیراهن لینن مردانه'),sanitize_title('با شلوار بگ مردانه چی بپوشیم')] as $s){$p=get_page_by_path($s,OBJECT,'post');if($p)wp_delete_post($p->ID,true);}foreach([[463,'67-linen'],[460,'67-bag']] as $x){$p=get_post($x[0]);if($p&&strpos($p->post_content,'data-g1-cluster-wave="'.$x[1].'"')!==false){$pat='/\s*<div data-g1-cluster-wave="'.preg_quote($x[1],'/').'">.*?<\/div>\s*$/s';$c=preg_replace($pat,'',$p->post_content,1);wp_update_post(wp_slash(['ID'=>$p->ID,'post_content'=>$c]));}}if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo 'ROLLED_BACK';?>''';save(rb,rollback);rs,rr,_,_=get(BASE+'/'+rb+'?t='+str(int(time.time())),180);print('ROLLBACK',rs,rr[:100]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS EDITORIAL WAVE 6-7');print('ARTICLE_06',a6);print('ARTICLE_07',a7);print('STYLE_CATEGORY',style);print('HOME_SHA_PRESERVED',post['front-page.php'])
