import hashlib,html,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');HEALTHY=os.environ.get('HEALTHY_HOME_SHA','');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir'
PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3';CAT_SHA='75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PROTECTED={'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7','template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d','assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0','assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
EXPECTED={
163:"تیشرت باکسی سنگشور طرح I'm Sorry با یقه‌گرد و طراحی چاپی، در رنگ‌های زرشکی و ذغالی و سایز L ارائه می‌شود.",
167:'تیشرت باکس سنگشور طرح Me vs Me با یقه‌گرد و طراحی چاپی، در سایز L ارائه می‌شود.',
197:'تیشرت کراپ باکس سنگشور طرح HORAE با یقه‌گرد و طراحی چاپی، در رنگ‌های کرم و ذغالی و سایزهای M و L ارائه می‌شود.',
202:'تیشرت باکس سنگشور طرح Greedy با یقه‌گرد و طراحی چاپی، در رنگ‌های قهوه‌ای و ذغالی و سایزهای L و XL ارائه می‌شود.',
215:'تیشرت باکس سنگشور طرح BackHouse با یقه‌گرد و طراحی چاپی، در سایزهای M و L ارائه می‌شود.',
113:'تیشرت باکسی سنگشور دو تکه طرح مسیح با یقه‌گرد و طراحی چاپی، در سایزهای M، L و XL ارائه می‌شود.',
119:'تیشرت باکسی سنگشور طرح closer با یقه‌گرد و طراحی چاپی، در رنگ‌های ذغالی و طوسی و سایزهای M و L ارائه می‌شود.',
150:'تیشرت باکسی سنگشور طرح A.D.F با یقه‌گرد و طراحی چاپی، در رنگ‌های سرمه‌ای و سفید و سایزهای M و L ارائه می‌شود.',
175:'تیشرت باکس طرح Chanyoou با یقه‌گرد و طراحی چاپی، در سایزهای M، L و XL ارائه می‌شود.',
181:'تیشرت سنگشور باکس طرح Warnning با یقه‌گرد و طراحی چاپی، در رنگ‌های سبز و سرمه‌ای و سایزهای M، L و XL ارائه می‌شود.',
374:'تیشرت باکسی سنگشور طرح Romance با طراحی چاپی؛ برای این مدل رنگ ذغالی و سایزهای M، L و XL تعریف شده است.',
380:'تیشرت باکس سنگشور طرح Only God Can... با طراحی چاپی؛ برای این مدل رنگ‌های ذغالی و قهوه‌ای و سایزهای M، L و XL تعریف شده است.',
392:'تیشرت باکس طرح مسیح با یقه‌گرد و طراحی چاپی؛ برای این مدل رنگ‌های سرمه‌ای و قهوه‌ای و سایزهای M، L و XL تعریف شده است.',
222:'شلوار جین نیم‌بگ ساده؛ برای این مدل سایزهای 31، 32، 33، 34، 36 و 38 تعریف شده است.',
231:'شلوار جین بگ زاپ‌دار؛ برای این مدل سایزهای M، L، XL و 2XL تعریف شده است.',
239:'شلوار جین بالنی تینت سبز؛ برای این مدل سایزهای 31، 32، 33، 34 و 36 تعریف شده است.',
248:'شلوار جین بالنی آبی روشن؛ برای این مدل سایزهای 30، 31 و 34 تعریف شده است.',
254:'شلوار جین فول‌بگ آبی روشن؛ برای این مدل سایزهای M، L و XL تعریف شده است.',
260:'شلوار جین بالنی زاپ‌دار؛ برای این مدل سایزهای M، L و 2XL تعریف شده است.',
268:'شلوار بگ افه‌دار ذغالی؛ برای این مدل سایزهای M، L و 2XL تعریف شده است.',
284:'شلوار بگ ذغالی طرح‌دار؛ برای این مدل سایزهای L، XL و 2XL تعریف شده است.',
288:'شلوار جین بگ دو تکه؛ برای این مدل سایزهای M، L، XL و 2XL تعریف شده است.',
293:'شلوار جین کارگو زاپ؛ برای این مدل سایزهای M و XL تعریف شده است.'}
def safe(u):
 p=urllib.parse.urlsplit(u);return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def api(fn,p,post=False):
 u=f'https://{HOST}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();last=None
 for n in range(6):
  try:
   r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=CTX,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
   q=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
   return q.get('data')
  except Exception as exc:last=exc;print('API_RETRY',n+1,exc);time.sleep(2+n*2)
 raise last
def theme(rel):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel);x=api('get_file_content',{'dir':ROOT if not d else ROOT+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(x,dict):
  for k in ('content','file_content','data'):
   if isinstance(x.get(k),str):return x[k]
 return x if isinstance(x,str) else ''
def save(n,c):return api('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u,timeout=150):
 u=safe(u);last=None
 for n in range(5):
  try:
   r=urllib.request.Request(u,headers={'User-Agent':'GramissLegacyRemediationAuditV5/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
   with urllib.request.urlopen(r,context=CTX,timeout=timeout) as z:return z.status,z.read(),z.geturl()
  except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
  except Exception as exc:last=exc;print('HTTP_RETRY',n+1,u,exc);time.sleep(2+n*2)
 raise last
def val(t,p):
 m=re.search(p,t,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sitemap(path):
 s,b,_=get(BASE+'/'+path+'?t='+str(int(time.time())),120);urls=sorted([html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>',b.decode('utf-8','replace'),re.I)]);return s,urls,hashlib.sha256('\n'.join(urls).encode()).hexdigest()
pre={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED',json.dumps(pre,sort_keys=True))
if pre!=PROTECTED:raise SystemExit('protected drift')
if HEALTHY and pre['front-page.php']!=HEALTHY:raise SystemExit('home drift')
ps,pu,ph=sitemap('product-sitemap.xml');cs,cu,ch=sitemap('product_cat-sitemap.xml');print('SITEMAPS',ps,len(pu),ph,cs,len(cu),ch)
if (ps,len(pu),ph)!=(200,47,PRODUCT_SHA):raise SystemExit('product sitemap drift')
if (cs,len(cu),ch)!=(200,20,CAT_SHA):raise SystemExit('cat sitemap drift')
nonce=hashlib.sha256((str(time.time())+pre['front-page.php']).encode()).hexdigest()[:12];name='gramiss-remediation-audit-v5-'+nonce+'.php';ids=','.join(map(str,EXPECTED))
php='''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$wanted=['''+ids+'''];$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);$o=['published'=>count($ids),'empty_excerpt'=>0,'rows'=>[]];foreach($ids as $id){$p=get_post($id);if(trim((string)$p->post_excerpt)==='')$o['empty_excerpt']++;if(in_array((int)$id,$wanted,true))$o['rows'][(string)$id]=['excerpt'=>$p->post_excerpt,'url'=>get_permalink($id)];}echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save(name,php);st,b,_=get(BASE+'/'+name+'?t='+str(int(time.time())),180);d=json.loads(b.decode('utf-8','replace'));print('STATE',json.dumps(d,ensure_ascii=False,separators=(',',':')));errs=[]
if st!=200:errs.append('probe')
if d.get('published')!=48:errs.append('published')
if d.get('empty_excerpt')!=24:errs.append('empty_excerpt')
for pid,exp in EXPECTED.items():
 row=(d.get('rows') or {}).get(str(pid))
 if not row or row.get('excerpt')!=exp:errs.append(f'{pid}:stored');continue
 st2,raw,_=get(row['url']+'?t='+str(int(time.time())),150);txt=raw.decode('utf-8','replace');head=txt.split('</head>',1)[0];desc=val(head,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)');canon=val(head,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)');robots=val(head,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)');schemas=len(re.findall(r'"@type"\s*:\s*"Product"',txt,re.I));print('PRODUCT',pid,st2,desc,canon,robots,schemas)
 if st2!=200:errs.append(f'{pid}:http')
 if desc!=exp:errs.append(f'{pid}:meta')
 if norm(canon)!=norm(row['url']):errs.append(f'{pid}:canon')
 if 'noindex' in robots.lower() or 'index' not in robots.lower():errs.append(f'{pid}:robots')
 if schemas!=1:errs.append(f'{pid}:schema')
post={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_POST',json.dumps(post,sort_keys=True))
if post!=pre:errs.append('protected')
print('ERRORS',json.dumps(errs))
if errs:raise SystemExit(1)
print('PASS LEGACY PRODUCT REMEDIATION AUDIT V5')