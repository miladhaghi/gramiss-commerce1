import base64,hashlib,html,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
TITLE='تیشرت باکسی چیست و چه تفاوتی با اورسایز دارد؟'
SLUG='تیشرت-باکسی-چیست-تفاوت-اورسایز'
SEO_TITLE='تیشرت باکسی چیست؟ تفاوت با اورسایز + راهنمای انتخاب'
SEO_DESC='تفاوت تیشرت باکسی و اورسایز را از نظر قد، عرض، سرشانه و تن‌خور بشناسید و یاد بگیرید برای استایل و فرم بدنتان کدام فیت انتخاب بهتری است.'
EXCERPT='تیشرت باکسی و اورسایز هر دو آزادند، اما فرم و نسبت‌های یکسانی ندارند. در این راهنما تفاوت واقعی این دو فیت و روش انتخاب سایز مناسب را ساده و کاربردی بررسی می‌کنیم.'
FOCUS='تیشرت باکسی چیست'
BODY='''<p>اگر بین تیشرت باکسی و اورسایز مردد شده‌ای، مهم‌ترین نکته این است که این دو اسم فقط دو روش متفاوت برای گفتن «تیشرت گشاد» نیستند. هر دو می‌توانند آزاد و راحت باشند، اما نسبت عرض به قد، محل قرار گرفتن سرشانه و حجم کلی لباس در آن‌ها متفاوت است. همین تفاوت‌ها تعیین می‌کند تیشرت روی بدن جمع‌وجور و چهارگوش دیده شود یا بلندتر و رها‌تر.</p>
<p>در این راهنما بدون پیچیده‌کردن موضوع، اول تعریف هر فیت را روشن می‌کنیم و بعد می‌رسیم به بخش مهم‌تر: چطور بفهمی کدام مدل برای استایل تو مناسب‌تر است و موقع انتخاب سایز باید چه اندازه‌هایی را بررسی کنی.</p>

<h2>تیشرت باکسی چیست؟</h2>
<p>باکسی یا <span dir="ltr">Boxy Fit</span> به فرمی گفته می‌شود که تنه‌ی لباس نسبتاً عریض و چهارگوش است، اما قد لباس لزوماً به همان نسبت بلند نمی‌شود. نتیجه معمولاً یک سیلوئت آزاد، ساختارمند و کمی کوتاه‌تر از چیزی است که از یک تیشرت خیلی گشاد انتظار داریم.</p>
<ul>
<li><strong>عرض تنه بیشتر است:</strong> لباس از پهلوها فضای آزاد بیشتری دارد و به بدن نمی‌چسبد.</li>
<li><strong>قد کنترل‌شده‌تر است:</strong> باکسی معمولاً قرار نیست فقط به دلیل بزرگ‌تر بودن سایز، خیلی پایین‌تر روی بدن بیاید.</li>
<li><strong>آستین و سرشانه آزادترند:</strong> بسته به الگو، سرشانه می‌تواند کمی افتاده باشد و آستین فرم پهن‌تری داشته باشد.</li>
<li><strong>فرم نهایی چهارگوش‌تر است:</strong> یعنی عرض لباس نسبت به قد آن نقش پررنگ‌تری در ظاهر کلی دارد.</li>
</ul>
<p>پس «باکسی» بیشتر درباره‌ی <strong>نسبت‌های الگو و فرم لباس</strong> است، نه صرفاً انتخاب یک سایز بزرگ‌تر.</p>

<h2>تیشرت اورسایز چیست؟</h2>
<p>اورسایز یا <span dir="ltr">Oversized Fit</span> هم از ابتدا با حجم بیشتر طراحی می‌شود، اما معمولاً آزادی آن فقط در عرض تنه خلاصه نمی‌شود. قد، سرشانه و آستین هم می‌توانند بزرگ‌تر و افتاده‌تر باشند تا ظاهر کلی لباس رها‌تر شود.</p>
<p>یک اورسایز درست با «پوشیدن تیشرت معمولی دو سایز بزرگ‌تر» یکی نیست. در مدل طراحی‌شده‌ی اورسایز، نسبت اجزای لباس باید با هم هماهنگ باشد؛ وگرنه یقه، حلقه آستین و قد لباس ممکن است به‌جای استایل آزاد، فقط نامتناسب دیده شوند.</p>

<h2>تفاوت تیشرت باکسی و اورسایز دقیقاً چیست؟</h2>
<h3>۱. نسبت عرض به قد</h3>
<p>واضح‌ترین تفاوت معمولاً همین‌جاست. در باکسی، عرض زیاد است ولی قد کنترل می‌شود؛ به همین دلیل فرم لباس چهارگوش‌تر به نظر می‌رسد. در اورسایز، افزایش حجم می‌تواند هم در عرض و هم در طول دیده شود و لباس پوشش بیشتری روی پایین‌تنه ایجاد کند.</p>

<h3>۲. افت سرشانه</h3>
<p>هر دو مدل ممکن است سرشانه‌ی افتاده داشته باشند، اما در اورسایز این ویژگی معمولاً پررنگ‌تر است. در باکسی هدف اصلی حفظ فرم پهن و متعادل تنه است و میزان افت سرشانه به طراحی همان مدل بستگی دارد.</p>

<h3>۳. فرم آستین</h3>
<p>آستین باکسی اغلب پهن است و می‌تواند تا حوالی میانه بازو یا نزدیک آرنج برسد. در اورسایز، آستین ممکن است هم پهن‌تر و هم بلندتر باشد تا با حجم کلی لباس هماهنگ بماند.</p>

<h3>۴. حجم بصری</h3>
<p>باکسی با وجود آزادی، معمولاً ظاهر جمع‌وجورتری می‌دهد؛ مخصوصاً وقتی با شلوارهای بگ یا نیم‌بگ پوشیده شود. اورسایز حجم بیشتری در بالاتنه می‌سازد و اگر پایین‌تنه هم خیلی حجیم باشد، باید تناسب کل استایل را آگاهانه‌تر تنظیم کرد.</p>

<h2>باکسی بهتر است یا اورسایز؟</h2>
<p>هیچ‌کدام ذاتاً بهتر نیست. انتخاب درست به این بستگی دارد که از لباس چه فرمی می‌خواهی.</p>
<ul>
<li>اگر تیشرت آزاد می‌خواهی اما دوست نداری قد لباس خیلی بلند شود، <strong>باکسی</strong> معمولاً انتخاب مستقیم‌تری است.</li>
<li>اگر ظاهر رها، سرشانه‌ی افتاده‌تر و حجم بیشتر در کل بالاتنه می‌خواهی، <strong>اورسایز</strong> به آن حس نزدیک‌تر است.</li>
<li>اگر شلوار خیلی گشاد می‌پوشی و می‌خواهی بالا و پایین استایل از هم تفکیک شوند، قد کنترل‌شده‌ی باکسی می‌تواند تعادل خوبی بسازد.</li>
<li>اگر لایه‌سازی می‌کنی یا دوست داری تیشرت بخش بیشتری از پایین‌تنه را بپوشاند، اورسایز می‌تواند کاربردی‌تر باشد.</li>
</ul>

<h2>چطور سایز مناسب تیشرت باکسی را انتخاب کنیم؟</h2>
<p>برای فیت‌های آزاد، فقط نگاه‌کردن به برچسب M یا L کافی نیست؛ چون دو برند می‌توانند برای یک سایز اسمی، اندازه‌های کاملاً متفاوتی داشته باشند. مطمئن‌ترین روش این است که اندازه‌های خود محصول را با تیشرتی که تن‌خورش را دوست داری مقایسه کنی.</p>
<ol>
<li><strong>عرض سینه:</strong> تیشرت مرجع را روی سطح صاف بگذار و فاصله‌ی زیر بغل تا زیر بغل را اندازه بگیر.</li>
<li><strong>قد لباس:</strong> از بالاترین نقطه‌ی سرشانه تا لبه‌ی پایین را اندازه بگیر. این عدد در تشخیص باکسی از یک فیت صرفاً بزرگ خیلی مهم است.</li>
<li><strong>عرض سرشانه:</strong> اگر سرشانه‌ی خیلی افتاده دوست نداری، این اندازه را با لباس مرجع مقایسه کن.</li>
<li><strong>طول و پهنای آستین:</strong> مخصوصاً اگر می‌خواهی آستین نزدیک آرنج بایستد، فقط سایز کلی لباس را ملاک قرار نده.</li>
</ol>
<p>اگر بین دو سایز هستی، اول مشخص کن هدفت حفظ فرم باکسی است یا نزدیک‌شدن به ظاهر اورسایز. انتخاب سایز بزرگ‌تر می‌تواند قد و افت سرشانه را هم تغییر دهد و در نهایت شخصیت اصلی مدل را عوض کند.</p>

<h2>اشتباه‌های رایج موقع خرید تیشرت باکسی</h2>
<h3>فقط یک سایز بزرگ‌تر می‌خریم</h3>
<p>تیشرت معمولی بزرگ‌تر الزاماً باکسی نمی‌شود. ممکن است فقط یقه و سرشانه نامتناسب شوند و قد لباس بیش از چیزی که می‌خواهی پایین بیاید.</p>

<h3>قد لباس را نادیده می‌گیریم</h3>
<p>خیلی‌ها فقط دور سینه یا عرض لباس را نگاه می‌کنند، در حالی که بخش مهم شخصیت باکسی از تعادل بین عرض زیاد و قد کنترل‌شده می‌آید.</p>

<h3>فیت را بدون توجه به شلوار انتخاب می‌کنیم</h3>
<p>تیشرت به‌تنهایی دیده نمی‌شود. اگر بیشتر شلوارهای کمدت بگ، فول‌بگ یا پارچه‌ای ریزشی هستند، طول و حجم تیشرت روی تناسب استایل اثر زیادی می‌گذارد.</p>

<h2>تیشرت باکسی را با چه شلواری ست کنیم؟</h2>
<p>برای یک استایل روزمره و خیابانی، باکسی با شلوار نیم‌بگ یا بگ ترکیب ساده‌ای می‌سازد؛ چون بالاتنه آزاد می‌ماند اما قد کوتاه‌تر تیشرت اجازه می‌دهد فرم شلوار هم دیده شود. با شلوار فول‌بگ، بهتر است حجم تیشرت و افت سرشانه را کنترل کنی تا استایل بیش از حد سنگین نشود.</p>
<p>برای ظاهر مینیمال‌تر، شلوار پارچه‌ای آزاد یا راسته‌ی راحت هم گزینه‌ی خوبی است. در نهایت قانون ثابت وجود ندارد؛ هدف این است که یک بخش از استایل بی‌دلیل بخش دیگر را نپوشاند و نسبت‌ها عمدی به نظر برسند.</p>

<h2>پس موقع انتخاب چه چیزی را چک کنیم؟</h2>
<p>به‌جای گیرکردن روی اسم مدل، چهار عدد را ببین: <strong>عرض سینه، قد لباس، سرشانه و آستین</strong>. بعد آن‌ها را با لباسی که همین حالا تن‌خور خوبی روی بدنت دارد مقایسه کن. این کار معمولاً از حدس‌زدن بر اساس اسم فیت یا سایز اسمی دقیق‌تر است.</p>
<p>اگر در Gramiss محصولی با عنوان باکسی می‌بینی، هدف این است که اطلاعات فیت و سایز همان محصول معیار تصمیم باشد، نه اینکه فرض کنیم همه‌ی باکسی‌ها یک اندازه و یک الگو دارند.</p>

<h2>سؤال‌های رایج درباره تیشرت باکسی</h2>
<h3>آیا تیشرت باکسی همان اورسایز است؟</h3>
<p>نه. هر دو آزادند، اما باکسی معمولاً عرض زیاد و قد کنترل‌شده‌تری دارد، در حالی که اورسایز می‌تواند در عرض، قد، سرشانه و آستین همزمان حجم بیشتری داشته باشد.</p>

<h3>آیا برای پوشیدن باکسی باید سایز بزرگ‌تر بخریم؟</h3>
<p>نه لزوماً. اگر محصول از ابتدا با الگوی باکسی طراحی شده باشد، انتخاب سایز باید بر اساس جدول اندازه‌ی همان محصول انجام شود. بزرگ‌تر خریدن ممکن است فیت را به سمت اورسایز ببرد.</p>

<h3>باکسی برای شلوار بگ مناسب است؟</h3>
<p>بله، مخصوصاً وقتی قد تیشرت کنترل‌شده باشد. این ترکیب اجازه می‌دهد حجم شلوار دیده شود و بالاتنه هم آزاد بماند.</p>

<h3>مهم‌ترین اندازه برای تشخیص فیت باکسی چیست؟</h3>
<p>یک عدد به‌تنهایی کافی نیست. نسبت عرض سینه به قد لباس، همراه با عرض سرشانه و فرم آستین، تصویر دقیق‌تری از فیت واقعی می‌دهد.</p>

<h2>جمع‌بندی</h2>
<p>تفاوت باکسی و اورسایز بیشتر از میزان «گشادی» است. باکسی روی عرض و فرم چهارگوش با قد کنترل‌شده تأکید دارد؛ اورسایز معمولاً حجم کلی بیشتری ایجاد می‌کند. برای انتخاب درست، اسم فیت را نقطه‌ی شروع بدان و تصمیم نهایی را با اندازه‌های واقعی لباس بگیر.</p>
<p><a href="/shop/">مشاهده محصولات Gramiss</a>؛ مشخصات هر محصول را جداگانه بررسی کن و فیتی را انتخاب کن که با استایل خودت هماهنگ است.</p>'''

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
  except Exception as exc:last=exc;print(f'Attempt {attempt}/4 {fn}: {exc}');time.sleep(attempt*2 if attempt<4 else 0)
 raise last
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def get(u,follow=True):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissContentWave1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});hs=[urllib.request.HTTPSHandler(context=ctx)]
 if not follow:hs.insert(0,NoRedirect())
 op=urllib.request.build_opener(*hs)
 try:
  with op.open(req,timeout=180) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def one(t,p):
 m=re.search(p,t,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def head(raw):
 t=raw.decode('utf-8','replace');h=t.split('</head>',1)[0];return {'title':one(h,r'<title[^>]*>(.*?)</title>'),'description':one(h,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':one(h,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':one(h,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
def types(raw):
 t=raw.decode('utf-8','replace');out=[]
 for s in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',t,re.I|re.S):
  try:
   d=json.loads(s)
   def walk(x):
    if isinstance(x,dict):
     ty=x.get('@type');out.extend(ty if isinstance(ty,list) else [ty] if ty else []);[walk(v) for v in x.values()]
    elif isinstance(x,list):[walk(v) for v in x]
   walk(d)
  except:pass
 return sorted(set(str(x) for x in out))
home_sha=hashlib.sha256(read_theme('front-page.php').encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch')
vals={k:base64.b64encode(v.encode()).decode() for k,v in {'title':TITLE,'slug':SLUG,'seo_title':SEO_TITLE,'seo_desc':SEO_DESC,'excerpt':EXCERPT,'focus':FOCUS,'body':BODY}.items()};nonce=hashlib.sha256((str(time.time())+home_sha).encode()).hexdigest()[:14];name='gramiss-publish-article01-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function d($s){return base64_decode($s);}$title=d('__TITLE__');$slug=sanitize_title(d('__SLUG__'));$body=d('__BODY__');$excerpt=d('__EXCERPT__');$seo_title=d('__SEO_TITLE__');$seo_desc=d('__SEO_DESC__');$focus=d('__FOCUS__');$marker='wave1-a01';$created=false;
$cat=get_term_by('slug','fit-size-guide','category');if(!$cat||is_wp_error($cat)){http_response_code(409);echo wp_json_encode(['error'=>'fit-size-guide missing']);exit;}
$existing=get_page_by_path($slug,OBJECT,'post');if($existing){if((string)get_post_meta($existing->ID,'_gramiss_content_wave_item',true)!==$marker){http_response_code(409);echo wp_json_encode(['error'=>'slug occupied','id'=>$existing->ID]);exit;}$id=$existing->ID;}else{$admins=get_users(['role__in'=>['administrator','editor'],'number'=>1,'orderby'=>'ID','order'=>'ASC']);$author=$admins?(int)$admins[0]->ID:1;$id=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>$title,'post_name'=>$slug,'post_content'=>$body,'post_excerpt'=>$excerpt,'post_author'=>$author,'post_category'=>[(int)$cat->term_id],'comment_status'=>'closed','ping_status'=>'closed']),true);if(is_wp_error($id)){http_response_code(500);echo wp_json_encode(['error'=>$id->get_error_message()]);exit;}$created=true;update_post_meta($id,'_gramiss_content_wave_item',$marker);update_post_meta($id,'rank_math_title',$seo_title);update_post_meta($id,'rank_math_description',$seo_desc);update_post_meta($id,'rank_math_focus_keyword',$focus);}
if(class_exists('RankMath\\Sitemap\\Cache')){\RankMath\Sitemap\Cache::invalidate_storage('post');\RankMath\Sitemap\Cache::invalidate_storage('category');}do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'id'=>$id,'created'=>$created,'url'=>get_permalink($id),'category'=>get_category_link($cat->term_id),'blog'=>get_permalink((int)get_option('page_for_posts'))],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
for k,v in vals.items():php=php.replace('__'+k.upper()+'__',v)
save(name,php);s,b,f,h=get('https://gramiss.ir/'+name+'?t='+str(int(time.time())));print('PUBLISH',s,b.decode('utf-8','replace'))
if s!=200:raise SystemExit('publish failed')
r=json.loads(b.decode('utf-8','replace'));created=bool(r.get('created'));post_url=r['url'];errors=[]
time.sleep(2)
# Article
s,raw,f,h=get(post_url+'?t='+str(int(time.time())));hi=head(raw);ty=types(raw);text=raw.decode('utf-8','replace');print('ARTICLE',s,f,json.dumps(hi,ensure_ascii=False),'SCHEMA',ty,'H2',len(re.findall(r'<h2\b',text,re.I)))
if s!=200 or SEO_TITLE not in hi['title']:errors.append('article title')
if hi['description']!=SEO_DESC:errors.append('article description')
if not hi['canonical'] or 'noindex' in hi['robots'].lower():errors.append('article index/canonical')
if not ('BlogPosting' in ty or 'Article' in ty):errors.append('article schema')
if len(re.findall(r'<h1\b',text,re.I))!=1 or len(re.findall(r'<h2\b',text,re.I))<6:errors.append('article headings')
# Blog becomes indexable and contains article
blog=r['blog'];s,br,bf,bh=get(blog+'?t='+str(int(time.time())));bhi=head(br);bt=br.decode('utf-8','replace');print('BLOG',s,bf,json.dumps(bhi,ensure_ascii=False),'ARTICLES',len(re.findall(r'<article\b',bt,re.I)))
if s!=200 or 'noindex' in bhi['robots'].lower() or not bhi['canonical'] or TITLE not in bt:errors.append('blog activation')
# Used category becomes indexable
cat=r['category'];s,cr,cf,ch=get(cat+'?t='+str(int(time.time())));chi=head(cr);ct=cr.decode('utf-8','replace');print('CATEGORY',s,cf,json.dumps(chi,ensure_ascii=False),'ARTICLES',len(re.findall(r'<article\b',ct,re.I)))
if s!=200 or 'noindex' in chi['robots'].lower() or not chi['canonical'] or TITLE not in ct:errors.append('category activation')
# Empty categories stay noindex
for u in ['https://gramiss.ir/category/style-guide/','https://gramiss.ir/category/buying-guide/','https://gramiss.ir/category/fabric-care/']:
 es,er,ef,eh=get(u+'?t='+str(int(time.time())));ehi=head(er);print('EMPTY_CATEGORY',u,es,ehi['robots']);
 if es!=200 or 'noindex' not in ehi['robots'].lower():errors.append('empty category '+u)
# Sitemaps
for label,u,needle in [('post','https://gramiss.ir/post-sitemap.xml',post_url),('category','https://gramiss.ir/category-sitemap.xml',cat)]:
 ss,sr,sf,sh=get(u);st=sr.decode('utf-8','replace');locs=re.findall(r'<loc>(.*?)</loc>',st,re.I);print('SITEMAP',label,ss,locs)
 if ss!=200 or not any(needle.rstrip('/')==x.rstrip('/') for x in locs):errors.append(label+' sitemap')
# Product sitemap must stay healthy
ps,pr,pf,ph=get('https://gramiss.ir/product-sitemap.xml');pc=len(re.findall(r'<url>',pr.decode('utf-8','replace'),re.I));print('PRODUCT_SITEMAP',ps,pc)
if ps!=200 or pc<40:errors.append('product sitemap regression')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:errors.append('Home changed')
if errors and created:
 rollback=r'''<?php header('Content-Type:text/plain');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$p=get_page_by_path('__SLUG__',OBJECT,'post');if($p&&(string)get_post_meta($p->ID,'_gramiss_content_wave_item',true)==='wave1-a01')wp_delete_post($p->ID,true);if(class_exists('RankMath\\Sitemap\\Cache')){\RankMath\Sitemap\Cache::invalidate_storage('post');\RankMath\Sitemap\Cache::invalidate_storage('category');}do_action('litespeed_purge_all');echo 'ROLLED_BACK';'''.replace('__SLUG__',urllib.parse.quote(SLUG,safe=''))
 rb='gramiss-rollback-article01-'+nonce+'.php';save(rb,rollback);rs,rr,rf,rh=get('https://gramiss.ir/'+rb);print('ROLLBACK',rs,rr.decode('utf-8','replace'))
if errors:raise SystemExit('VERIFY_ERRORS '+json.dumps(errors,ensure_ascii=False))
print('PASS CONTENT WAVE 1 ARTICLE 01');print('POST',post_url);print('HOME SHA PRESERVED',home_sha)
