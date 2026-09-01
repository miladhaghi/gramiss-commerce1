import hashlib,html,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');HEALTHY=os.environ.get('HEALTHY_HOME_SHA','');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir'
PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3';CAT_SHA='75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PROTECTED={'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7','template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d','assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0','assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
TARGETS={374:{'title':'تیشرت باکسی سنگشور طرح Romance','excerpt':'تیشرت باکسی سنگشور طرح Romance با طراحی چاپی؛ برای این مدل رنگ ذغالی و سایزهای M، L و XL تعریف شده است.'},380:{'title':'تیشرت باکس سنگشور طرح Only God Can...','excerpt':'تیشرت باکس سنگشور طرح Only God Can... با طراحی چاپی؛ برای این مدل رنگ‌های ذغالی و قهوه‌ای و سایزهای M، L و XL تعریف شده است.'},392:{'title':'تیشرت باکس طرح مسیح','excerpt':'تیشرت باکس طرح مسیح با یقه‌گرد و طراحی چاپی؛ برای این مدل رنگ‌های سرمه‌ای و قهوه‌ای و سایزهای M، L و XL تعریف شده است.'}}
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
   r=urllib.request.Request(u,headers={'User-Agent':'GramissLegacyShortDescBatch3/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
   with urllib.request.urlopen(r,context=CTX,timeout=timeout) as z:return z.status,z.read(),z.geturl()
  except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
  except Exception as exc:last=exc;print('HTTP_RETRY',n+1,u,exc);time.sleep(2+n*2)
 raise last
def val(t,p):
 m=re.search(p,t,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sitemap(path):
 s,b,_=get(BASE+'/'+path+'?t='+str(int(time.time())),120);urls=sorted([html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>',b.decode('utf-8','replace'),re.I)]);return s,urls,hashlib.sha256('\n'.join(urls).encode()).hexdigest()
def hashes():return {p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED}
def php(mode,old=None):
 tj=json.dumps({str(k):v for k,v in TARGETS.items()},ensure_ascii=False,separators=(',',':'));oj=json.dumps(old or {},ensure_ascii=False,separators=(',',':'))
 return r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$mode='''+json.dumps(mode)+r''';$targets=json_decode('''+json.dumps(tj)+r''',true);$old=json_decode('''+json.dumps(oj)+r''',true);$o=['ok'=>true,'errors'=>[],'before'=>[],'after'=>[]];foreach($targets as $sid=>$cfg){$id=(int)$sid;$p=get_post($id);$wc=wc_get_product($id);if(!$p||!$wc){$o['errors'][]='missing:'.$id;continue;}$vars=[];if($wc->is_type('variable'))foreach($wc->get_children() as $vid){$v=wc_get_product($vid);if($v)$vars[]=['id'=>(int)$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price(),'stock_status'=>$v->get_stock_status()];}$o['before'][$sid]=['status'=>$p->post_status,'title'=>$p->post_title,'excerpt'=>$p->post_excerpt,'url'=>get_permalink($id),'vars'=>$vars];if($mode==='apply'){if($p->post_status!=='publish')$o['errors'][]='status:'.$id;if($p->post_title!==$cfg['title'])$o['errors'][]='title:'.$id;if(trim((string)$p->post_excerpt)!=='')$o['errors'][]='excerpt:'.$id;foreach($vars as $v){if(trim((string)$v['sku'])==='')$o['errors'][]='sku:'.$v['id'];if(trim((string)$v['price'])==='')$o['errors'][]='price:'.$v['id'];}}}if($mode==='apply'&&empty($o['errors']))foreach($targets as $sid=>$cfg){$r=wp_update_post(['ID'=>(int)$sid,'post_excerpt'=>$cfg['excerpt']],true);if(is_wp_error($r))$o['errors'][]='update:'.$sid;}if($mode==='rollback')foreach($targets as $sid=>$cfg){$r=wp_update_post(['ID'=>(int)$sid,'post_excerpt'=>array_key_exists($sid,$old)?(string)$old[$sid]:''],true);if(is_wp_error($r))$o['errors'][]='rollback:'.$sid;}foreach($targets as $sid=>$cfg){$p=get_post((int)$sid);if($p)$o['after'][$sid]=['excerpt'=>$p->post_excerpt,'url'=>get_permalink((int)$sid)];}if(function_exists('wp_cache_flush'))wp_cache_flush();do_action('litespeed_purge_all');do_action('rank_math/sitemap/flush_cache');$o['ok']=empty($o['errors']);echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
def call(mode,old=None):
 n='gramiss-shortdesc-b3-'+mode+'-'+hashlib.sha256((mode+str(time.time())).encode()).hexdigest()[:12]+'.php';save(n,php(mode,old));s,b,f=get(BASE+'/'+n+'?t='+str(int(time.time())),240);d=json.loads(b.decode('utf-8','replace'));print('WP',mode,s,f,json.dumps(d,ensure_ascii=False,separators=(',',':')));
 if s!=200 or not d.get('ok'):raise RuntimeError(mode+' '+str(d.get('errors')))
 return d
def verify(urls):
 errs=[]
 for pid,cfg in TARGETS.items():
  u=urls[str(pid)];last={}
  for a in range(6):
   st,raw,_=get(u+'?t='+str(int(time.time())));txt=raw.decode('utf-8','replace');h=txt.split('</head>',1)[0];last={'status':st,'desc':val(h,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canon':val(h,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':val(h,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)'),'schema':len(re.findall(r'"@type"\s*:\s*"Product"',txt,re.I))}
   if st==200 and last['desc']==cfg['excerpt'] and norm(last['canon'])==norm(u) and 'index' in last['robots'].lower() and 'noindex' not in last['robots'].lower() and last['schema']==1:break
   time.sleep(3+a*2)
  print('PUBLIC',pid,json.dumps(last,ensure_ascii=False,separators=(',',':')))
  if last.get('status')!=200 or last.get('desc')!=cfg['excerpt'] or norm(last.get('canon',''))!=norm(u) or 'noindex' in last.get('robots','').lower() or 'index' not in last.get('robots','').lower() or last.get('schema')!=1:errs.append(str(pid))
 return errs
pre=hashes();print('PROTECTED_PRE',json.dumps(pre,sort_keys=True));
if pre!=PROTECTED:raise SystemExit('protected drift')
ps,pu,ph=sitemap('product-sitemap.xml');cs,cu,ch=sitemap('product_cat-sitemap.xml');print('SITEMAP_PRE',ps,len(pu),ph,cs,len(cu),ch)
if (ps,len(pu),ph)!=(200,47,PRODUCT_SHA) or (cs,len(cu),ch)!=(200,20,CAT_SHA):raise SystemExit('sitemap drift')
pf=call('preflight');old={k:v['excerpt'] for k,v in pf['before'].items()};urls={k:v['url'] for k,v in pf['before'].items()}
for k,v in old.items():
 if v!='':raise SystemExit('excerpt occupied '+k)
applied=False
try:
 out=call('apply');applied=True
 for k,c in {str(k):v for k,v in TARGETS.items()}.items():
  if out['after'][k]['excerpt']!=c['excerpt']:raise RuntimeError('stored '+k)
 errs=verify(urls);ps2,pu2,ph2=sitemap('product-sitemap.xml');cs2,cu2,ch2=sitemap('product_cat-sitemap.xml');post=hashes();print('SITEMAP_POST',ps2,len(pu2),ph2,cs2,len(cu2),ch2);print('PROTECTED_POST',json.dumps(post,sort_keys=True))
 if pu2!=pu or ph2!=ph or cu2!=cu or ch2!=ch:raise RuntimeError('sitemap changed')
 if post!=pre:raise RuntimeError('protected changed')
 if errs:raise RuntimeError('public '+','.join(errs))
 print('PASS LEGACY SHORT DESCRIPTION BATCH 3')
except Exception as e:
 print('FAIL',repr(e))
 if applied:
  try:print('ROLLBACK',json.dumps(call('rollback',old),ensure_ascii=False,separators=(',',':')))
  except Exception as rb:print('ROLLBACK_FAIL',repr(rb))
 raise