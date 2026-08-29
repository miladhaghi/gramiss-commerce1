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
  except Exception as exc:
   last=exc;print(f'Attempt {attempt}/4 {fn}: {exc}');time.sleep(attempt*2 if attempt<4 else 0)
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
def get(u,follow=True,timeout=120):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissRankMathBootstrapFix/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 hs=[urllib.request.HTTPSHandler(context=ctx)]
 if not follow:hs.insert(0,NoRedirect())
 op=urllib.request.build_opener(*hs)
 try:
  with op.open(req,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def hval(h,n):
 n=n.lower()
 for k,v in h.items():
  if k.lower()==n:return v
 return ''
def head_info(raw):
 t=raw.decode('utf-8','replace');head=t.split('</head>',1)[0] if '</head>' in t else t[:80000]
 cans=re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',head,re.I)
 desc=re.findall(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)',head,re.I)
 og=re.findall(r'<meta[^>]+property=["\']og:[^"\']+["\']',head,re.I);tw=re.findall(r'<meta[^>]+name=["\']twitter:[^"\']+["\']',head,re.I)
 return {'canonical_count':len(cans),'canonical':cans[0] if cans else '','description_count':len(desc),'description_len':len(desc[0].strip()) if desc else 0,'og_count':len(og),'twitter_count':len(tw),'rank_math_marker':'Rank Math SEO plugin' in head or 'rank-math' in head.lower(),'jsonld_count':len(re.findall(r'application/ld\+json',head,re.I))}
front=read_theme('front-page.php');front_sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',front_sha)
if healthy and front_sha!=healthy:raise SystemExit('ABORT Home mismatch; no changes')
stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime());nonce=hashlib.sha256((stamp+front_sha).encode()).hexdigest()[:14]
# Phase 1: use Rank Math's own supported registration-skip option; preserve exact prior state.
p1='gramiss-rm-fix1-'+nonce+'.php'
php1=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$sent='__GRAMISS_MISSING__';$old=get_option('rank_math_registration_skip',$sent);$before=function_exists('rank_math')&&rank_math()->registration?(bool)rank_math()->registration->invalid:null;update_option('rank_math_registration_skip',1,false);$manifest=['created_at'=>gmdate('c'),'option'=>'rank_math_registration_skip','old'=>$old,'before_invalid'=>$before,'permalink_structure'=>get_option('permalink_structure')];$mp=WP_CONTENT_DIR.'/gramiss-rankmath-bootstrap-fix-v1-'.gmdate('Ymd-His').'.json';file_put_contents($mp,wp_json_encode($manifest,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT));echo wp_json_encode(['ok'=>true,'old'=>$old,'new'=>get_option('rank_math_registration_skip'),'before_invalid'=>$before,'manifest'=>$mp],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save(p1,php1);s,b,_,_=get('https://gramiss.ir/'+p1+'?t='+str(int(time.time())));print('PHASE1',s,b.decode('utf-8','replace'))
if s!=200:raise SystemExit('ABORT phase1 failed')
p1d=json.loads(b.decode('utf-8','replace'))
# Phase 2: fresh bootstrap must now initialize complete Rank Math runtime, then rebuild rewrites.
p2='gramiss-rm-fix2-'+nonce+'.php'
php2=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$rm=function_exists('rank_math')?rank_math():null;$reg=$rm?$rm->registration:null;global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);if(function_exists('do_action'))do_action('litespeed_purge_all');echo wp_json_encode(['skip'=>get_option('rank_math_registration_skip'),'invalid'=>$reg?(bool)$reg->invalid:null,'manager'=>$rm?isset($rm->manager):false,'rewrite'=>$rm?isset($rm->rewrite):false,'frontend'=>$rm?isset($rm->frontend):false,'settings'=>$rm?isset($rm->settings):false,'modules'=>get_option('rank_math_modules'),'rewrite_rules'=>count((array)get_option('rewrite_rules',[])),'permalink_structure'=>get_option('permalink_structure')],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save(p2,php2);s,b,_,_=get('https://gramiss.ir/'+p2+'?t='+str(int(time.time())));print('PHASE2',s,b.decode('utf-8','replace'))
errors=[]
if s!=200:errors.append('phase2 non-200');p2d={}
else:p2d=json.loads(b.decode('utf-8','replace'))
if p2d.get('invalid') is not False:errors.append('Rank Math registration still invalid')
for k in ('manager','rewrite','frontend','settings'):
 if not p2d.get(k):errors.append('Rank Math runtime missing '+k)
if p2d.get('permalink_structure')!='/%postname%/':errors.append('permalink contract changed')
# Public SEO endpoints and money-page head checks.
urls={'home':'https://gramiss.ir/','shop':'https://gramiss.ir/shop/','product':'https://gramiss.ir/product/%D8%AA%DB%8C%D8%B4%D8%B1%D8%AA-%D8%A8%D8%A7%DA%A9%D8%B3-%D8%B7%D8%B1%D8%AD-%D9%85%D8%B3%DB%8C%D8%AD/','category':'https://gramiss.ir/product-category/tshirt/','cart':'https://gramiss.ir/cart/','account':'https://gramiss.ir/my-account/','search':'https://gramiss.ir/?s=%D8%AA%DB%8C%D8%B4%D8%B1%D8%AA'}
heads={}
for label,u in urls.items():
 st,raw,final,h=get(u,True,120);info=head_info(raw);heads[label]={'status':st,'final':final,**info};print('HEAD',label,json.dumps(heads[label],ensure_ascii=False,separators=(',',':')))
 if label in ('home','shop','product','category','cart','account') and st!=200:errors.append(label+' non-200')
for label in ('product','category'):
 if heads.get(label,{}).get('canonical_count')!=1:errors.append(label+' canonical count != 1')
 if heads.get(label,{}).get('og_count',0)<1:errors.append(label+' missing OG output')
 if heads.get(label,{}).get('jsonld_count',0)<1:errors.append(label+' missing JSON-LD')
# Utility robots should stay noindex.
for label in ('cart','account','search'):
 st,raw,_,_=get(urls[label],True,90);txt=raw.decode('utf-8','replace').lower()
 if 'noindex' not in txt.split('</head>',1)[0]:errors.append(label+' lost noindex')
# Rank Math sitemap must resolve as XML.
st,raw,final,h=get('https://gramiss.ir/sitemap_index.xml',True,120);txt=raw.decode('utf-8','replace');locs=re.findall(r'<loc>(.*?)</loc>',txt,re.I);print('SITEMAP_INDEX',st,final,'BYTES',len(raw),'LOCS',json.dumps(locs,ensure_ascii=False))
if st!=200 or '<sitemapindex' not in txt.lower():errors.append('Rank Math sitemap index unavailable')
# robots must remain reachable.
st_r,raw_r,final_r,_=get('https://gramiss.ir/robots.txt',True,90);print('ROBOTS',st_r,final_r,raw_r.decode('utf-8','replace').replace('\n',' | ')[:1000])
if st_r!=200:errors.append('robots non-200')
# Legacy redirect contract still intact.
old='https://gramiss.ir/?product='+urllib.parse.quote('تیشرت-باکس-طرح-مسیح',safe='-');st_l,_,_,hh=get(old,False,60);loc=hval(hh,'Location');print('LEGACY_REDIRECT',st_l,loc)
if st_l!=301 or '/product/' not in loc:errors.append('legacy redirect contract broken')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=front_sha:errors.append('Home changed')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False))
 rb='gramiss-rm-rollback-'+nonce+'.php';old_json=json.dumps(p1d.get('old'),ensure_ascii=False)
 rbphp="<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$old=json_decode('"+json.dumps(old_json)+"',true);if($old==='__GRAMISS_MISSING__'){delete_option('rank_math_registration_skip');}else{update_option('rank_math_registration_skip',$old,false);}global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);if(function_exists('do_action'))do_action('litespeed_purge_all');echo 'ROLLED_BACK';"
 save(rb,rbphp);rs,rbody,_,_=get('https://gramiss.ir/'+rb+'?t='+str(int(time.time())),True,120);print('ROLLBACK',rs,rbody[:100]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS RANK MATH BOOTSTRAP FIX V1')
print('OPTION rank_math_registration_skip=1 (supported Rank Math skip path)')
print('HOME SHA PRESERVED',front_sha)
