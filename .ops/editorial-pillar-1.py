import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
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
  except Exception as exc:last=exc;print('API_RETRY',fn,attempt,exc);time.sleep(attempt*2 if attempt<4 else 0)
 raise last
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save_public(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u,follow=True,timeout=180):
 class NR(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,req,fp,code,msg,headers,newurl):return None
 req=urllib.request.Request(u,headers={'User-Agent':'GramissEditorialWave1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});hs=[urllib.request.HTTPSHandler(context=ctx)]
 if not follow:hs.insert(0,NR())
 op=urllib.request.build_opener(*hs)
 try:
  with op.open(req,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def hval(raw,p):
 m=re.search(p,raw,re.I|re.S);return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def head(raw):
 t=raw.decode('utf-8','replace').split('</head>',1)[0];return {'title':hval(t,r'<title[^>]*>(.*?)</title>'),'description':hval(t,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':hval(t,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':hval(t,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
front=read_theme('front-page.php');home_sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch')
for f,m in [('home.php','g1-editorial-index'),('single.php','g1-editorial-single'),('category.php','g1-editorial-category'),('assets/css/editorial-v1.css','GRAMISS_EDITORIAL_V1')]:
 c=read_theme(f)
 if m not in c:raise SystemExit('ABORT editorial foundation missing '+f)
nonce=hashlib.sha256((str(time.time())+home_sha).encode()).hexdigest()[:14];name='gramiss-editorial-pillar-1-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$slug='تیشرت-باکسی-چیست-تفاوت-با-اورسایز';$existing=get_page_by_path($slug,OBJECT,'post');$cat=get_term_by('slug','fit-size-guide','category');$blog=get_post(22);if($existing||!$cat||!$blog||$blog->post_title!=='مجله Gramiss'){http_response_code(409);echo wp_json_encode(['error'=>'baseline drift','existing'=>$existing?$existing->ID:null,'cat'=>$cat?$cat->term_id:null,'blog'=>$blog?$blog->post_title:null],JSON_UNESCAPED_UNICODE);exit;}
$published=(int)wp_count_posts('post')->publish;if($published!==0){http_response_code(409);echo wp_json_encode(['error'=>'unexpected published posts','count'=>$published]);exit;}
$shop=function_exists('wc_get_page_permalink')?wc_get_page_permalink('shop'):home_url('/shop/');$p97=get_permalink(97);$p210=get_permalink(210);$style=get_term_by('slug','style-guide','category');$style_url=$style?get_term_link($style):$shop;$tee_search=add_query_arg(['s'=>'تیشرت','post_type'=>'product'],home_url('/'));
$content=<<<'HTML'
<p>تیشرت باکسی فقط یک تیشرت «گشاد» نیست. تفاوت اصلی آن در نسبت عرض به قد و شکل کلی الگوست: تنه فضای بیشتری دارد، فرم لباس چهارگوش‌تر دیده می‌شود و قد معمولاً کنترل‌شده‌تر از یک تیشرت اورسایز است. همین تفاوت کوچک باعث می‌شود دو تیشرت با سایز اسمی یکسان، روی بدن کاملاً متفاوت دیده شوند.</p>
<p>اگر بین باکسی، اورسایز و فیت معمولی مردد هستی، بهتر است به‌جای اسم مدل یا فقط حرف M و L، چند اندازه واقعی لباس را مقایسه کنی. در این راهنما دقیقاً همین کار را انجام می‌دهیم.</p>

<h2>تیشرت باکسی دقیقاً چیست؟</h2>
<p>در یک تیشرت باکسی، فرم کلی تنه به مستطیل نزدیک‌تر است؛ یعنی عرض سینه و پایین لباس نسبتاً آزاد است و لباس قرار نیست روی خط کمر یا پهلوها جمع شود. سرشانه می‌تواند کمی رها باشد، آستین معمولاً حجم بیشتری دارد و لبه پایین لباس نسبت به عرض آن خیلی کشیده نیست.</p>
<p>نکته مهم این است که «باکسی» یک عدد یا استاندارد جهانی ثابت نیست. هر برند می‌تواند نسبت‌های خودش را داشته باشد. بنابراین ممکن است یک مدل باکسی در یک برند کوتاه‌تر و ساختارمندتر باشد و در برند دیگر نرم‌تر و آزادتر بایستد.</p>

<h2>فرق تیشرت باکسی و اورسایز چیست؟</h2>
<p>هر دو مدل آزادی بیشتری نسبت به تیشرت کلاسیک دارند، اما منطق الگوی آن‌ها یکی نیست. باکسی بیشتر روی <strong>عرض بیشتر در کنار قد کنترل‌شده</strong> تمرکز دارد. اورسایز معمولاً حجم کلی بیشتری ایجاد می‌کند و ممکن است هم عرض، هم قد، هم افت سرشانه و هم طول آستین بیشتر باشد.</p>
<table><thead><tr><th>ویژگی</th><th>باکسی</th><th>اورسایز</th></tr></thead><tbody><tr><td>عرض تنه</td><td>آزاد و چهارگوش</td><td>آزاد تا بسیار آزاد</td></tr><tr><td>قد لباس</td><td>معمولاً کوتاه‌تر و کنترل‌شده‌تر</td><td>اغلب بلندتر یا رها‌تر</td></tr><tr><td>سرشانه</td><td>نرمال تا کمی افتاده</td><td>معمولاً افتاده‌تر</td></tr><tr><td>حس کلی استایل</td><td>آزاد اما مرتب</td><td>رها و حجیم‌تر</td></tr></tbody></table>
<p>پس اگر یک تیشرت معمولی را صرفاً دو سایز بزرگ‌تر بخری، الزاماً باکسی نمی‌شود. احتمال دارد فقط قد و آستین بیش از حد بلند شوند، در حالی که نسبت‌های یک الگوی باکسی از ابتدا برای همین فرم طراحی شده‌اند.</p>

<h2>برای انتخاب سایز تیشرت باکسی چه چیزهایی را اندازه بگیریم؟</h2>
<p>بهترین مرجع، تیشرتی است که همین حالا تنخورش را دوست داری. آن را روی سطح صاف پهن کن و این چهار اندازه را یادداشت کن:</p>
<ul><li><strong>عرض سینه:</strong> فاصله افقی زیر بغل تا زیر بغل.</li><li><strong>قد لباس:</strong> از بالاترین نقطه شانه تا لبه پایین.</li><li><strong>عرض سرشانه:</strong> فاصله دو انتهای درز شانه.</li><li><strong>طول آستین:</strong> مخصوصاً اگر دوست نداری آستین خیلی پایین‌تر از بازو قرار بگیرد.</li></ul>
<p>بعد این اعداد را با جدول اندازه همان محصول مقایسه کن. سایز روی لیبل فقط یک راهنماست؛ دو مدل L می‌توانند چند سانتی‌متر اختلاف واقعی داشته باشند.</p>

<h2>از کجا بفهمیم فیت باکسی روی بدن درست نشسته؟</h2>
<p>سه نشانه ساده کمک می‌کند. اول، پارچه در سینه نباید کشیده شود. دوم، لبه پایین نباید آن‌قدر بلند باشد که نسبت چهارگوش لباس از بین برود. سوم، حجم آستین و تنه باید عمدی به نظر برسد، نه شبیه لباسی که فقط یک یا دو سایز بزرگ‌تر خریده شده است.</p>
<p>اگر قد لباس برای بالاتنه تو بیش از حد بلند است، رفتن به سایز کوچک‌تر همیشه راه‌حل نیست؛ چون ممکن است عرض و سرشانه را خراب کند. در این حالت بهتر است مدل دیگری با قد کوتاه‌تر انتخاب شود.</p>

<h2>باکسی برای چه استایلی مناسب‌تر است؟</h2>
<p>تیشرت باکسی به‌خاطر حجم کنترل‌شده، با شلوارهای راسته، نیم‌بگ، بگ و بعضی مدل‌های پارچه‌ای آزاد خوب کار می‌کند. چیزی که ترکیب را تمیز نگه می‌دارد، تعادل حجم بالاتنه و پایین‌تنه است.</p>
<p>اگر تیشرت خیلی عریض و شلوار هم بسیار حجیم باشد، بهتر است قد تیشرت کنترل‌شده بماند تا استایل سنگین نشود. برعکس، با شلوار راسته می‌توان کمی آزادی بیشتر در تیشرت داشت. در مقاله‌های <a href="STYLE_URL">راهنمای استایل Gramiss</a> این نسبت‌ها را برای ترکیب‌های مختلف جداگانه باز می‌کنیم.</p>

<h2>پارچه چه تغییری در تنخور باکسی ایجاد می‌کند؟</h2>
<p>الگو فقط نیمی از ماجراست. یک پارچه نسبتاً سنگین یا ساختارمند، فرم چهارگوش را واضح‌تر نگه می‌دارد. پارچه نرم و ریزشی همان الگو را روان‌تر و نزدیک‌تر به بدن نشان می‌دهد. سنگشور، نوع بافت، ضخامت و حتی نوع چاپ هم می‌توانند حس نهایی لباس را تغییر دهند.</p>
<p>به همین دلیل، موقع خرید فقط عکس روبه‌رو را نبین. نمای بغل، پشت و افت پارچه روی بدن اطلاعات بیشتری درباره فیت واقعی می‌دهد.</p>

<h2>باکسی ساده یا چاپی؛ کدام انتخاب بهتری است؟</h2>
<p>این انتخاب بیشتر به کمد فعلی تو برمی‌گردد. مدل ساده و خنثی راحت‌تر با چند شلوار و کفش مختلف تکرار می‌شود. مدل چاپی می‌تواند نقطه اصلی استایل باشد و بهتر است بقیه آیتم‌ها رقابت بصری کمتری با آن داشته باشند.</p>
<p>برای دیدن تفاوت تنخور در محصول واقعی، می‌توانی <a href="P97_URL">تیشرت باکسی سنگشور Gramiss</a> و یک مدل ساختارمندتر مثل <a href="P210_URL">تیشرت باکس دو تکه چاپی</a> را کنار هم مقایسه کنی. هدف از این لینک‌ها فروش فوری نیست؛ مقایسه عکس و مشخصات دو مدل کمک می‌کند معنی «فیت» را عملی‌تر ببینی.</p>

<h2>۵ اشتباه رایج هنگام خرید تیشرت باکسی</h2>
<ol><li><strong>انتخاب فقط بر اساس M، L یا XL:</strong> اندازه واقعی لباس مهم‌تر از نام سایز است.</li><li><strong>یکی دانستن باکسی و اورسایز:</strong> هر لباس آزاد، باکسی نیست.</li><li><strong>نادیده گرفتن قد:</strong> چند سانتی‌متر اختلاف قد می‌تواند کل نسبت استایل را عوض کند.</li><li><strong>دیدن فقط عکس محصول روی زمینه سفید:</strong> برای فهم فیت، عکس روی بدن مهم‌تر است.</li><li><strong>بزرگ‌تر خریدن برای رسیدن به فرم باکسی:</strong> اگر الگو باکسی نباشد، فقط همه ابعاد لباس بزرگ‌تر می‌شوند.</li></ol>

<h2>چک‌لیست سریع قبل از خرید</h2>
<ul><li>یک تیشرت خوش‌فیت خودت را اندازه بگیر.</li><li>عرض سینه و قد را با جدول محصول مقایسه کن.</li><li>به افت سرشانه و طول آستین در عکس مدل نگاه کن.</li><li>جنس و میزان ریزش پارچه را بخوان.</li><li>تصمیم بگیر باکسی مرتب می‌خواهی یا حجم نزدیک‌تر به اورسایز.</li><li>بعد سراغ رنگ و چاپ برو.</li></ul>

<h2>جمع‌بندی: کدام را انتخاب کنیم؟</h2>
<p>اگر فرم آزاد می‌خواهی اما دوست داری قد لباس و حجم کلی کنترل‌شده بماند، باکسی معمولاً انتخاب منطقی‌تری است. اگر عمداً دنبال حجم بیشتر، سرشانه افتاده‌تر و ظاهر رها هستی، اورسایز به خواسته‌ات نزدیک‌تر است.</p>
<p>مهم‌تر از اسم مدل، نسبت‌های واقعی لباس با بدن و استایل توست. از این به بعد وقتی عبارت «باکسی» را روی یک محصول می‌بینی، قبل از خرید سه چیز را بررسی کن: <strong>عرض، قد و جنس پارچه</strong>.</p>
<p><a href="TEE_SEARCH_URL">مشاهده تیشرت‌های Gramiss</a> یا بازگشت به <a href="SHOP_URL">فروشگاه Gramiss</a>.</p>
HTML;
$content=str_replace(['STYLE_URL','P97_URL','P210_URL','TEE_SEARCH_URL','SHOP_URL'],[esc_url($style_url),esc_url($p97),esc_url($p210),esc_url($tee_search),esc_url($shop)],$content);
$post_id=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>'تیشرت باکسی چیست؟ تفاوت با اورسایز و راهنمای انتخاب سایز','post_name'=>$slug,'post_excerpt'=>'تیشرت باکسی چه فرقی با اورسایز دارد؟ در این راهنما با فرم باکسی، اندازه‌های مهم، انتخاب سایز و اشتباهات رایج خرید آشنا می‌شویم.','post_content'=>$content,'post_category'=>[(int)$cat->term_id],'post_author'=>1]),true);
if(is_wp_error($post_id)){http_response_code(500);echo wp_json_encode(['error'=>$post_id->get_error_message()]);exit;}
update_post_meta($post_id,'rank_math_title','تیشرت باکسی چیست؟ تفاوت با اورسایز و انتخاب سایز');update_post_meta($post_id,'rank_math_description','تفاوت تیشرت باکسی و اورسایز، روش اندازه‌گیری و انتخاب سایز مناسب و نکات مهم فیت را ساده و کاربردی یاد بگیرید.');update_post_meta($post_id,'rank_math_focus_keyword','تیشرت باکسی چیست');update_post_meta($post_id,'rank_math_robots',['index','follow']);update_post_meta($post_id,'rank_math_rich_snippet','article');update_post_meta($post_id,'rank_math_snippet_article_type','BlogPosting');
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'id'=>$post_id,'url'=>get_permalink($post_id),'cat_url'=>get_term_link($cat),'published'=>(int)wp_count_posts('post')->publish,'words'=>str_word_count(wp_strip_all_tags($content))],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save_public(name,php);s,b,_,_=get('https://gramiss.ir/'+name+'?t='+str(int(time.time())),True,180);print('WRITE',s,b.decode('utf-8','replace'))
if s!=200:raise SystemExit('article write failed')
d=json.loads(b.decode('utf-8','replace'));pid=d['id'];url=d['url'];caturl=d['cat_url'];errors=[]
# Article live output.
ps,praw,pf,_=get(url+'?t='+str(int(time.time())),True,120);ph=head(praw);pbody=praw.decode('utf-8','replace');print('LIVE_POST',ps,pf,json.dumps(ph,ensure_ascii=False,separators=(',',':')),'SINGLE',('g1-editorial-single' in pbody),'H2',pbody.count('<h2>'))
if ps!=200 or 'g1-editorial-single' not in pbody or 'تیشرت باکسی چیست؟' not in pbody or pbody.count('<h2>')<7:errors.append('single article output failed')
if not ph.get('canonical') or 'noindex' in ph.get('robots','').lower() or 'تیشرت باکسی' not in ph.get('title',''):errors.append('article SEO failed')
# Blog must now become indexable with its first substantive post.
bs,braw,bf,_=get('https://gramiss.ir/%D9%88%D8%A8%D9%84%D8%A7%DA%AF/?t='+str(int(time.time())),True,120);bh=head(braw);bb=braw.decode('utf-8','replace');print('LIVE_BLOG',bs,bf,json.dumps(bh,ensure_ascii=False,separators=(',',':')),'CARD_TITLE',('تیشرت باکسی چیست؟' in bb))
if bs!=200 or 'تیشرت باکسی چیست؟' not in bb:errors.append('blog card missing')
if 'noindex' in bh.get('robots','').lower() or not bh.get('canonical'):errors.append('blog remained noindex after first post')
# Category must now be a real indexable archive.
cs,craw,cf,_=get(caturl+'?t='+str(int(time.time())),True,120);ch=head(craw);cb=craw.decode('utf-8','replace');print('LIVE_CATEGORY',cs,cf,json.dumps(ch,ensure_ascii=False,separators=(',',':')),'TEMPLATE',('g1-editorial-category' in cb))
if cs!=200 or 'g1-editorial-category' not in cb or 'تیشرت باکسی چیست؟' not in cb or 'noindex' in ch.get('robots','').lower() or not ch.get('canonical'):errors.append('category archive failed')
# Sitemaps.
for sm in ['sitemap_index.xml','post-sitemap.xml','category-sitemap.xml','product-sitemap.xml','product_cat-sitemap.xml']:
 ss,sraw,sf,_=get('https://gramiss.ir/'+sm+'?t='+str(int(time.time())),True,120);txt=sraw.decode('utf-8','replace');locs=re.findall(r'<loc>(.*?)</loc>',txt,re.I);print('SITEMAP',sm,ss,len(locs),json.dumps(locs[:6],ensure_ascii=False));
 if ss!=200:errors.append(sm+' not 200')
 if sm=='post-sitemap.xml' and url not in locs:errors.append('post absent sitemap')
 if sm=='category-sitemap.xml' and caturl not in locs:errors.append('category absent sitemap')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:errors.append('Home changed')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));rb='gramiss-editorial-pillar-1-rollback-'+nonce+'.php';rphp=f'''<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);wp_delete_post({pid},true);if(class_exists('RankMath\\\\Sitemap\\\\Cache'))\\RankMath\\Sitemap\\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo 'ROLLED_BACK';''';save_public(rb,rphp);rs,rr,_,_=get('https://gramiss.ir/'+rb+'?t='+str(int(time.time())),True,180);print('ROLLBACK',rs,rr[:80]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS EDITORIAL PILLAR 1 PUBLISHED');print('POST_ID',pid,'URL',url);print('HOME SHA PRESERVED',home_sha)