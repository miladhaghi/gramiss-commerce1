import hashlib,html,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');HEALTHY=os.environ.get('HEALTHY_HOME_SHA','');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir'
EXPECTED_PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3';EXPECTED_PRODUCT_CAT_SHA='75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PROTECTED={'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7','template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d','assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0','assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
TARGETS={
163:{'title':"تیشرت باکسی سنگشور طرح I'm Sorry",'excerpt':"تیشرت باکسی سنگشور طرح I'm Sorry با یقه‌گرد و طراحی چاپی، در رنگ‌های زرشکی و ذغالی و سایز L ارائه می‌شود."},
167:{'title':'تیشرت باکس سنگشور طرح Me vs Me','excerpt':'تیشرت باکس سنگشور طرح Me vs Me با یقه‌گرد و طراحی چاپی، در سایز L ارائه می‌شود.'},
197:{'title':'تیشرت کراپ باکس سنگشور طرح HORAE','excerpt':'تیشرت کراپ باکس سنگشور طرح HORAE با یقه‌گرد و طراحی چاپی، در رنگ‌های کرم و ذغالی و سایزهای M و L ارائه می‌شود.'},
202:{'title':'تیشرت باکس سنگشور طرح Greedy','excerpt':'تیشرت باکس سنگشور طرح Greedy با یقه‌گرد و طراحی چاپی، در رنگ‌های قهوه‌ای و ذغالی و سایزهای L و XL ارائه می‌شود.'},
215:{'title':'تیشرت باکس سنگشور طرح BackHouse','excerpt':'تیشرت باکس سنگشور طرح BackHouse با یقه‌گرد و طراحی چاپی، در سایزهای M و L ارائه می‌شود.'},
}
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
  except Exception as exc:last=exc;print('API_RETRY',fn,n+1,exc);time.sleep(2+n*2)
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
   r=urllib.request.Request(u,headers={'User-Agent':'GramissLegacyShortDescBatch1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
   with urllib.request.urlopen(r,context=CTX,timeout=timeout) as z:return z.status,z.read(),z.geturl()
  except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
  except Exception as exc:last=exc;print('HTTP_RETRY',n+1,u,exc);time.sleep(2+n*2)
 raise last
def val(t,p):
 m=re.search(p,t,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sitemap(path):
 s,b,_=get(BASE+'/'+path+'?t='+str(int(time.time())),120);return s,sorted([html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>',b.decode('utf-8','replace'),re.I)])
def snap_sitemaps():
 ps,pu=sitemap('product-sitemap.xml');cs,cu=sitemap('product_cat-sitemap.xml');psha=hashlib.sha256('\n'.join(pu).encode()).hexdigest();csha=hashlib.sha256('\n'.join(cu).encode()).hexdigest();return {'product_status':ps,'product_urls':pu,'product_sha':psha,'cat_status':cs,'cat_urls':cu,'cat_sha':csha}
def hashes():return {p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED}
def make_probe(mode,expected_old=None):
 payload=json.dumps({str(k):v for k,v in TARGETS.items()},ensure_ascii=False,separators=(',',':'))
 old=json.dumps(expected_old or {},ensure_ascii=False,separators=(',',':'))
 php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$mode='''+json.dumps(mode)+r''';$targets=json_decode('''+json.dumps(payload)+r''',true);$old=json_decode('''+json.dumps(old)+r''',true);$out=['ok'=>true,'mode'=>$mode,'before'=>[],'after'=>[],'errors'=>[]];
foreach($targets as $sid=>$cfg){$id=(int)$sid;$p=get_post($id);$wc=wc_get_product($id);if(!$p||!$wc){$out['errors'][]="missing:$id";continue;}$vars=[];if($wc->is_type('variable'))foreach($wc->get_children() as $vid){$v=wc_get_product($vid);if($v)$vars[]=['id'=>(int)$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price(),'stock_status'=>$v->get_stock_status()];}$out['before'][$sid]=['status'=>$p->post_status,'title'=>$p->post_title,'excerpt'=>$p->post_excerpt,'url'=>get_permalink($id),'type'=>$wc->get_type(),'vars'=>$vars];
 if($mode==='apply'){
  if($p->post_status!=='publish'){$out['errors'][]="status:$id";continue;}
  if($p->post_title!==$cfg['title']){$out['errors'][]="title:$id";continue;}
  if(trim($p->post_excerpt)!==''){$out['errors'][]="excerpt-not-empty:$id";continue;}
  if($wc->is_type('variable'))foreach($vars as $v){if(trim((string)$v['sku'])==='')$out['errors'][]='sku:'.$v['id'];if(trim((string)$v['price'])==='')$out['errors'][]='price:'.$v['id'];}
 }
}
if($mode==='apply' && empty($out['errors'])){foreach($targets as $sid=>$cfg){$id=(int)$sid;$r=wp_update_post(['ID'=>$id,'post_excerpt'=>$cfg['excerpt']],true);if(is_wp_error($r))$out['errors'][]='update:'.$id.':'.$r->get_error_message();}}
if($mode==='rollback'){foreach($targets as $sid=>$cfg){$id=(int)$sid;$restore=array_key_exists($sid,$old)?(string)$old[$sid]:'';$r=wp_update_post(['ID'=>$id,'post_excerpt'=>$restore],true);if(is_wp_error($r))$out['errors'][]='rollback:'.$id.':'.$r->get_error_message();}}
foreach($targets as $sid=>$cfg){$p=get_post((int)$sid);if($p)$out['after'][$sid]=['title'=>$p->post_title,'excerpt'=>$p->post_excerpt,'url'=>get_permalink((int)$sid)];}
if(function_exists('wp_cache_flush'))wp_cache_flush();do_action('litespeed_purge_all');do_action('rank_math/sitemap/flush_cache');$out['ok']=empty($out['errors']);echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
 return php
def wp_call(mode,expected_old=None):
 nonce=hashlib.sha256((mode+str(time.time())+str(os.getpid())).encode()).hexdigest()[:14];name='gramiss-shortdesc-b1-'+mode+'-'+nonce+'.php';save(name,make_probe(mode,expected_old));s,b,f=get(BASE+'/'+name+'?t='+str(int(time.time())),240);print('WP_CALL',mode,s,f,'BYTES',len(b));
 if s!=200:raise RuntimeError('WP call HTTP '+str(s))
 out=json.loads(b.decode('utf-8','replace'));print('WP_RESULT',json.dumps(out,ensure_ascii=False,separators=(',',':')))
 if not out.get('ok'):raise RuntimeError('WP '+mode+' failed '+str(out.get('errors')))
 return out
def verify_public(pre_urls):
 errors=[]
 for pid,cfg in TARGETS.items():
  u=pre_urls[str(pid)];last=None
  for attempt in range(6):
   st,raw,final=get(u+'?t='+str(int(time.time())));txt=raw.decode('utf-8','replace');head=txt.split('</head>',1)[0];title=val(head,r'<title[^>]*>(.*?)</title>');desc=val(head,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)');canon=val(head,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)');robots=val(head,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)');schemas=len(re.findall(r'"@type"\s*:\s*"Product"',txt,re.I));body_plain=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',txt))).strip();last={'status':st,'title':title,'description':desc,'canonical':canon,'robots':robots,'schema_count':schemas,'excerpt_visible':cfg['excerpt'] in body_plain};
   if st==200 and norm(canon)==norm(u) and 'noindex' not in robots.lower() and 'index' in robots.lower() and schemas==1 and desc==cfg['excerpt']:break
   time.sleep(3+attempt*2)
  print('PUBLIC_VERIFY',pid,json.dumps(last,ensure_ascii=False,separators=(',',':')))
  if last['status']!=200:errors.append(f'{pid}:http')
  if norm(last['canonical'])!=norm(u):errors.append(f'{pid}:canonical')
  if 'noindex' in last['robots'].lower() or 'index' not in last['robots'].lower():errors.append(f'{pid}:robots')
  if last['schema_count']!=1:errors.append(f'{pid}:schema')
  if last['description']!=cfg['excerpt']:errors.append(f'{pid}:meta')
 return errors
pre_hash=hashes();print('PROTECTED_PRE',json.dumps(pre_hash,sort_keys=True));
if pre_hash!=PROTECTED:raise SystemExit('ABORT protected drift')
if HEALTHY and pre_hash['front-page.php']!=HEALTHY:raise SystemExit('ABORT healthy home')
pre_sm=snap_sitemaps();print('SITEMAP_PRE',json.dumps({k:v for k,v in pre_sm.items() if not k.endswith('_urls')},sort_keys=True))
if pre_sm['product_status']!=200 or len(pre_sm['product_urls'])!=47 or pre_sm['product_sha']!=EXPECTED_PRODUCT_SHA:raise SystemExit('ABORT product sitemap baseline')
if pre_sm['cat_status']!=200 or len(pre_sm['cat_urls'])!=20 or pre_sm['cat_sha']!=EXPECTED_PRODUCT_CAT_SHA:raise SystemExit('ABORT product category sitemap baseline')
# Preflight obtains canonical expected URLs and validates all target facts before mutation.
pre=wp_call('preflight');old={sid:data['excerpt'] for sid,data in pre['before'].items()};urls={sid:data['url'] for sid,data in pre['before'].items()};
for sid,x in old.items():
 if x!='':raise SystemExit('ABORT excerpt changed before apply '+sid)
applied=False
try:
 out=wp_call('apply');applied=True
 for sid,cfg in {str(k):v for k,v in TARGETS.items()}.items():
  if out['after'][sid]['excerpt']!=cfg['excerpt']:raise RuntimeError('stored excerpt mismatch '+sid)
 pub_errors=verify_public(urls)
 post_sm=snap_sitemaps();print('SITEMAP_POST',json.dumps({k:v for k,v in post_sm.items() if not k.endswith('_urls')},sort_keys=True))
 if post_sm['product_urls']!=pre_sm['product_urls'] or post_sm['product_sha']!=pre_sm['product_sha']:raise RuntimeError('product sitemap changed')
 if post_sm['cat_urls']!=pre_sm['cat_urls'] or post_sm['cat_sha']!=pre_sm['cat_sha']:raise RuntimeError('product category sitemap changed')
 post_hash=hashes();print('PROTECTED_POST',json.dumps(post_hash,sort_keys=True))
 if post_hash!=pre_hash:raise RuntimeError('protected files changed')
 if pub_errors:raise RuntimeError('public verification '+','.join(pub_errors))
 print('PASS LEGACY SHORT DESCRIPTION BATCH 1')
except Exception as exc:
 print('VERIFY_FAILURE',repr(exc))
 if applied:
  try:
   rb=wp_call('rollback',old);print('ROLLBACK_DONE',json.dumps(rb,ensure_ascii=False,separators=(',',':')))
  except Exception as rb_exc:print('ROLLBACK_FAILURE',repr(rb_exc))
 raise
