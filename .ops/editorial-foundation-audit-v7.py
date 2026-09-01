import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']; ROOT=os.environ['THEME_ROOT'].strip('/'); HEALTHY=os.environ.get('HEALTHY_HOME_SHA',''); CTX=ssl._create_unverified_context(); BASE='https://gramiss.ir'
PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'; PCAT_SHA='75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
TITLES={
453:'تیشرت باکسی چیست و چه تفاوتی با اورسایز دارد؟',459:'راهنمای انتخاب سایز تیشرت باکسی مردانه؛ اندازه‌گیری و فیت مناسب',460:'تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ کدام فیت مناسب شماست؟',463:'پارچه لینن چیست؟ راهنمای شناخت، چروک و انتخاب لباس لینن',464:'شست‌وشوی پیراهن لینن مردانه؛ راهنمای خشک‌کردن و اتوکشی',467:'استایل با پیراهن لینن مردانه؛ شلوار، کفش و ترکیب رنگ',468:'با شلوار بگ مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و قد شلوار',471:'راهنمای خرید تیشرت مردانه؛ فیت، اندازه، پارچه، دوخت و چاپ',472:'راهنمای خرید شلوار جین مردانه؛ فیت، قد، پارچه و جزئیات',482:'راهنمای انتخاب سایز کتانی مردانه؛ اندازه‌گیری پا برای خرید آنلاین',483:'راهنمای خرید کتانی مردانه برای استفاده روزمره؛ سایز، رویه و زیره',487:'راهنمای انتخاب سایز پیراهن مردانه؛ سرشانه، سینه، قد و آستین',488:'تمیز کردن کتانی سفید بدون آسیب؛ راهنمای رویه، بند و خشک‌کردن',492:'شلوار کارگو مردانه چیست و چه تفاوتی با شلوار بگ دارد؟',493:'راهنمای انتخاب سایز کلاه فیت کپ؛ اندازه‌گیری دور سر بدون حدس',496:'شست‌وشوی تیشرت چاپی؛ محافظت از چاپ در شستن، خشک‌کردن و اتوکشی',497:'راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت، افت پارچه، فاق و قد',502:'با شلوار کارگو مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و حجم لباس',503:'پیراهن آستین کوتاه مردانه را با چی بپوشیم؟ شلوار، کفش و لایه‌بندی'}
IDS=list(TITLES); COUNTS={'fit-size-guide':7,'fabric-care':4,'style-guide':4,'buying-guide':4}
FOCUS={492:'شلوار کارگو مردانه چیست',493:'انتخاب سایز کلاه فیت کپ',496:'شستشوی تیشرت چاپی',497:'راهنمای خرید شلوار پارچه ای مردانه',502:'با شلوار کارگو مردانه چی بپوشیم',503:'پیراهن آستین کوتاه مردانه با چی بپوشیم'}
META={502:('با شلوار کارگو مردانه چی بپوشیم؟ راهنمای استایل','برای استایل با شلوار کارگو مردانه، تیشرت، پیراهن، کتانی و حجم بالاتنه را بر اساس فیت و دمپای همان شلوار هماهنگ کنید؛ با فرمول‌های کاربردی و بدون قانون‌های خشک.'),503:('پیراهن آستین کوتاه مردانه با چی بپوشیم؟ راهنمای استایل','پیراهن آستین کوتاه مردانه را با جین، شلوار پارچه‌ای، کتانی و لایه‌بندی درست ست کنید؛ انتخاب فیت، قد پیراهن و حجم شلوار را مرحله‌به‌مرحله بررسی کنید.')}
PROTECTED={'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7','template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d','assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0','assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}

def safe(u):
 p=urllib.parse.urlsplit(u); return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def api(fn,params,post=False):
 u=f'https://{HOST}:2083/execute/Fileman/{fn}'; e=urllib.parse.urlencode(params).encode(); last=None
 for n in range(4):
  try:
   r=urllib.request.Request(u if post else u+'?'+e.decode(),data=e if post else None,method='POST' if post else 'GET'); r.add_header('Authorization',f'cpanel {USER}:{TOKEN}');
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=CTX,timeout=90) as x:o=json.loads(x.read().decode('utf-8','replace'))
   z=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(z,dict) or z.get('status')!=1:raise RuntimeError(str(z))
   return z.get('data')
  except Exception as exc:last=exc; print('API_RETRY',fn,n+1,exc); time.sleep(n+1)
 raise last
def theme(rel):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel); x=api('get_file_content',{'dir':ROOT if not d else ROOT+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(x,dict):
  for k in ('content','file_content','data'):
   if isinstance(x.get(k),str):return x[k]
 return x if isinstance(x,str) else ''
def save(name,text):return api('save_file_content',{'dir':'public_html','file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u,timeout=180):
 u=safe(u); last=None
 for n in range(4):
  try:
   q=urllib.request.Request(u,headers={'User-Agent':'GramissEditorialAuditV7/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});
   with urllib.request.urlopen(q,context=CTX,timeout=timeout) as r:return r.status,r.read(),r.geturl()
  except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
  except Exception as exc:last=exc; print('HTTP_RETRY',n+1,u,exc); time.sleep(n+1)
 raise last
def val(t,p):
 m=re.search(p,t,re.I|re.S); return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def head(raw):
 t=raw.decode('utf-8','replace').split('</head>',1)[0]; return {'title':val(t,r'<title[^>]*>(.*?)</title>'),'description':val(t,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':val(t,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':val(t,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sm(path):
 s,b,_=get(BASE+'/'+path+'?t='+str(int(time.time())),120); return s,[x.replace('&amp;','&') for x in re.findall(r'<loc>(.*?)</loc>',b.decode('utf-8','replace'),re.I)]

errors=[]; protected={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED}; print('PROTECTED',json.dumps(protected,sort_keys=True))
for p,h in PROTECTED.items():
 if protected.get(p)!=h:errors.append('protected '+p)
if HEALTHY and protected['front-page.php']!=HEALTHY:errors.append('healthy home')
nonce=hashlib.sha256((str(time.time())+protected['front-page.php']).encode()).hexdigest()[:14]; probe='gramiss-editorial-foundation-audit-v7-'+nonce+'.php'
php=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$ids=[453,459,460,463,464,467,468,471,472,482,483,487,488,492,493,496,497,502,503];$posts=[];foreach($ids as $id){$p=get_post($id);$posts[]=$p?['id'=>(int)$p->ID,'status'=>$p->post_status,'title'=>$p->post_title,'url'=>get_permalink($p),'cats'=>wp_get_post_categories($p->ID,['fields'=>'slugs']),'focus'=>get_post_meta($p->ID,'rank_math_focus_keyword',true)]:['id'=>$id,'missing'=>true];}$cats=[];foreach(['fit-size-guide','fabric-care','style-guide','buying-guide'] as $slug){$t=get_term_by('slug',$slug,'category');$cats[$slug]=$t?['count'=>(int)$t->count,'url'=>get_term_link($t)]:null;}$blog=get_post(22);echo wp_json_encode(['published'=>(int)wp_count_posts('post')->publish,'posts'=>$posts,'cats'=>$cats,'blog'=>$blog?['title'=>$blog->post_title,'url'=>get_permalink($blog)]:null],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save(probe,php); ss,sraw,_=get(BASE+'/'+probe+'?t='+str(int(time.time())),240)
try:state=json.loads(sraw.decode('utf-8','replace')) if ss==200 else {}
except Exception as exc:state={};errors.append('state json '+str(exc))
print('WP_STATE',ss,state.get('published'))
if ss!=200 or state.get('published')!=19:errors.append('published')
rows={int(x.get('id',0)):x for x in state.get('posts',[]) if isinstance(x,dict)}
for pid in IDS:
 r=rows.get(pid)
 if not r:errors.append('missing '+str(pid));continue
 if r.get('status')!='publish' or r.get('title')!=TITLES[pid] or not r.get('url'):errors.append('post state '+str(pid))
 if pid in FOCUS and r.get('focus')!=FOCUS[pid]:errors.append('focus '+str(pid))
for slug,count in COUNTS.items():
 c=(state.get('cats') or {}).get(slug)
 if not c or c.get('count')!=count:errors.append('cat count '+slug)

urls={pid:rows[pid]['url'] for pid in IDS if pid in rows and rows[pid].get('url')}; article_norms={norm(u):pid for pid,u in urls.items()}; public_links={}
for pid,u in urls.items():
 st,raw,final=get(u+'?t='+str(int(time.time())),180); text=raw.decode('utf-8','replace'); m=head(raw); links={norm(x) for x in re.findall(r'href=["\']([^"\']+)',text,re.I) if 'gramiss.ir' in x}; public_links[pid]=links; h2=len(re.findall(r'<h2\b',text,re.I)); bp=bool(re.search(r'"@type"\s*:\s*"BlogPosting"',text,re.I)); prod=bool(re.search(r'"@type"\s*:\s*"Product"',text,re.I)); print('ARTICLE',pid,st,'H2',h2,'BLOGPOSTING',bp,'PRODUCT',prod)
 if st!=200:errors.append('http '+str(pid))
 if TITLES[pid] not in text:errors.append('title render '+str(pid))
 if norm(m.get('canonical',''))!=norm(u):errors.append('canonical '+str(pid))
 rob=m.get('robots','').lower()
 if 'noindex' in rob or 'index' not in rob:errors.append('robots '+str(pid))
 if not bp or prod:errors.append('schema '+str(pid))
 if h2<8:errors.append('h2 '+str(pid))
 if pid in META and (m.get('title'),m.get('description'))!=META[pid]:errors.append('meta '+str(pid))
 incoming=sum(1 for target in links if target in article_norms and article_norms[target]!=pid)
 if incoming<1:errors.append('no editorial outbound '+str(pid))

required={468:[urls[502]],492:[urls[502]],467:[urls[503]],487:[urls[503]],502:[urls[460],urls[483],urls[492],BASE+'/product-category/pants/cargo-pants/',BASE+'/product-category/tshirt/',BASE+'/product-category/sneakers/'],503:[urls[467],urls[472],urls[483],urls[487],BASE+'/product-category/shirt/',BASE+'/product-category/shirt/short-sleeve-shirt/',BASE+'/product-category/sneakers/']}
for pid,targets in required.items():
 for target in targets:
  if norm(target) not in public_links.get(pid,set()):errors.append(f'link {pid}->{target}')

for slug,c in (state.get('cats') or {}).items():
 if not c or not c.get('url'):continue
 st,raw,_=get(c['url']+'?t='+str(int(time.time())),150); m=head(raw); rob=m.get('robots','').lower(); print('CATEGORY',slug,st,c.get('count'))
 if st!=200 or 'noindex' in rob or 'index' not in rob or norm(m.get('canonical',''))!=norm(c['url']):errors.append('category page '+slug)

blog=(state.get('blog') or {}).get('url',BASE+'/وبلاگ/'); visible=set()
for page in (1,2):
 u=blog if page==1 else blog.rstrip('/')+'/page/2/'; st,raw,final=get(u+'?t='+str(int(time.time())),150); text=raw.decode('utf-8','replace'); print('BLOG_PAGE',page,st,final)
 if st!=200:errors.append('blog '+str(page))
 visible|={norm(x) for x in re.findall(r'href=["\']([^"\']+)',text,re.I) if 'gramiss.ir' in x}
for pid,u in urls.items():
 if norm(u) not in visible:errors.append('blog missing '+str(pid))

post_s,post_u=sm('post-sitemap.xml'); cat_s,cat_u=sm('category-sitemap.xml'); prod_s,prod_u=sm('product-sitemap.xml'); pc_s,pc_u=sm('product_cat-sitemap.xml'); prod_u=sorted(prod_u);pc_u=sorted(pc_u);ph=hashlib.sha256('\n'.join(prod_u).encode()).hexdigest();pch=hashlib.sha256('\n'.join(pc_u).encode()).hexdigest(); print('SITEMAPS',post_s,len(post_u),cat_s,len(cat_u),prod_s,len(prod_u),ph,pc_s,len(pc_u),pch)
if post_s!=200 or len(post_u)!=20:errors.append('post sitemap')
if cat_s!=200 or len(cat_u)!=4:errors.append('category sitemap')
if prod_s!=200 or len(prod_u)!=47 or ph!=PRODUCT_SHA:errors.append('product sitemap')
if pc_s!=200 or len(pc_u)!=20 or pch!=PCAT_SHA:errors.append('product cat sitemap')
pset={norm(x) for x in post_u}
for pid,u in urls.items():
 if norm(u) not in pset:errors.append('post sitemap missing '+str(pid))
print('ERRORS',json.dumps(errors,ensure_ascii=False))
if errors:raise SystemExit('FAIL EDITORIAL FOUNDATION AUDIT V7')
print('PASS EDITORIAL FOUNDATION AUDIT V7')
