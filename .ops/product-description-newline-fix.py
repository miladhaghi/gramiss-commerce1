import hashlib,html,json,os,re,ssl,time,urllib.parse,urllib.request
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
  except Exception as exc:last=exc;print(f'Attempt {attempt}/4 {fn}: {exc}');time.sleep(attempt*2 if attempt<4 else 0)
 raise last
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u):
 r=urllib.request.Request(u,headers={'User-Agent':'GramissProductDescriptionNewlineFix/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 with urllib.request.urlopen(r,context=ctx,timeout=180) as z:return z.status,z.read(),z.geturl()
def meta_desc(raw):
 h=raw.decode('utf-8','replace').split('</head>',1)[0];m=re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)',h,re.I|re.S);return html.unescape(m.group(1)).strip() if m else ''
home_sha=hashlib.sha256(read_theme('front-page.php').encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch')
nonce=hashlib.sha256((str(time.time())+home_sha).encode()).hexdigest()[:14];name='gramiss-product-newline-fix-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$expected=[330=>'پیراهن لینن آستین کوتاه سرمه‌ای',344=>'پیراهن لینن آستین کوتاه آبی'];$before=[];$changed=[];
foreach($expected as $id=>$title){$p=get_post($id);if(!$p||$p->post_type!=='product'||$p->post_title!==$title){http_response_code(409);echo wp_json_encode(['error'=>'product guard failed','id'=>$id]);exit;}$before[(string)$id]=$p->post_content;$clean=str_replace(["\\r\\n","\\n","\\r"],"\n",$p->post_content);if($clean!==$p->post_content){$r=wp_update_post(wp_slash(['ID'=>$id,'post_content'=>$clean]),true);if(is_wp_error($r)){http_response_code(500);echo wp_json_encode(['error'=>$r->get_error_message(),'id'=>$id]);exit;}$changed[]=$id;}}
$verify=[];foreach($expected as $id=>$title){$p=get_post($id);$verify[(string)$id]=['title'=>$p->post_title,'content'=>$p->post_content,'has_literal'=>strpos($p->post_content,'\\r\\n')!==false||strpos($p->post_content,'\\n')!==false];if($verify[(string)$id]['has_literal']){foreach($before as $rid=>$content)wp_update_post(wp_slash(['ID'=>(int)$rid,'post_content'=>$content]));http_response_code(500);echo wp_json_encode(['error'=>'verify failed','verify'=>$verify],JSON_UNESCAPED_UNICODE);exit;}}
do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'changed'=>$changed,'verify'=>$verify],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,f=get('https://gramiss.ir/'+name+'?t='+str(int(time.time())));print('WRITE',s,b.decode('utf-8','replace'))
if s!=200:raise SystemExit('newline fix failed')
for u in ['https://gramiss.ir/product/%d9%be%db%8c%d8%b1%d8%a7%d9%87%d9%86-%d9%84%db%8c%d9%86%d9%86-%d8%a2%d8%b3%d8%aa%db%8c%d9%86-%da%a9%d9%88%d8%aa%d8%a7%d9%87/','https://gramiss.ir/product/%d9%be%db%8c%d8%b1%d8%a7%d9%87%d9%86-%d9%84%db%8c%d9%86%d9%86-%d8%a2%d8%b3%d8%aa%db%8c%d9%86-%da%a9%d9%88%d8%aa%d8%a7%d9%87-%d8%a2%d8%a8%db%8c/']:
 s,raw,f=get(u+'?t='+str(int(time.time())));d=meta_desc(raw);print('LIVE',s,f,d)
 if s!=200 or 'rnتضمین' in d or '\\r\\n' in d or 'تضمین کیفیت' not in d:raise SystemExit('live description verify failed')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:raise SystemExit('Home changed')
print('PASS PRODUCT DESCRIPTION NEWLINE FIX');print('HOME SHA PRESERVED',home_sha)
