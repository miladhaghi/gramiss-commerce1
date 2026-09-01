import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
from collections import defaultdict
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');HEALTHY=os.environ.get('HEALTHY_HOME_SHA','');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir'
PROTECTED={'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7','template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d','assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0','assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
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
def safe(u):
 p=urllib.parse.urlsplit(u);return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def get(u,timeout=120):
 u=safe(u);last=None
 for n in range(4):
  try:
   r=urllib.request.Request(u,headers={'User-Agent':'GramissLegacyRemediationPlannerV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
   with urllib.request.urlopen(r,context=CTX,timeout=timeout) as z:return z.status,z.read(),z.geturl()
  except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
  except Exception as exc:last=exc;print('HTTP_RETRY',n+1,u,exc);time.sleep(n+1)
 raise last
def val(t,p):
 m=re.search(p,t,re.I|re.S);return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
protected={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_PRE',json.dumps(protected,sort_keys=True))
for p,h in PROTECTED.items():
 if protected[p]!=h:raise SystemExit('ABORT protected drift '+p)
if HEALTHY and protected['front-page.php']!=HEALTHY:raise SystemExit('ABORT healthy home')
nonce=hashlib.sha256((str(time.time())+protected['front-page.php']).encode()).hexdigest()[:14];name='gramiss-legacy-remediation-plan-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function gw($s){$s=trim(wp_strip_all_tags(strip_shortcodes((string)$s)));if($s==='')return 0;$a=preg_split('/\s+/u',$s,-1,PREG_SPLIT_NO_EMPTY);return is_array($a)?count($a):0;}
function clean($s){return trim(preg_replace('/\s+/u',' ',wp_strip_all_tags(strip_shortcodes((string)$s))));}
$o=[];$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);foreach($ids as $id){$p=get_post($id);$wc=wc_get_product($id);if(!$wc)continue;$cats=wp_get_post_terms($id,'product_cat',['fields'=>'all']);$imgs=[];$image_ids=[];$thumb=(int)get_post_thumbnail_id($id);if($thumb)$image_ids[]=$thumb;foreach((array)$wc->get_gallery_image_ids() as $iid)$image_ids[]=(int)$iid;foreach(array_values(array_unique(array_filter($image_ids))) as $iid)$imgs[]=['id'=>$iid,'alt'=>(string)get_post_meta($iid,'_wp_attachment_image_alt',true)];$vars=[];if($wc->is_type('variable')){foreach($wc->get_children() as $vid){$v=wc_get_product($vid);if(!$v)continue;$vars[]=['id'=>(int)$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price(),'stock_status'=>$v->get_stock_status(),'attributes'=>$v->get_attributes()];}}$o[]=['id'=>(int)$id,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>get_permalink($id),'type'=>$wc->get_type(),'sku'=>$wc->get_sku(),'description'=>clean($p->post_content),'description_words'=>gw($p->post_content),'short_description'=>clean($p->post_excerpt),'short_description_words'=>gw($p->post_excerpt),'featured_image'=>$thumb,'images'=>$imgs,'categories'=>array_map(fn($t)=>['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug],$cats),'variations'=>$vars,'robots'=>get_post_meta($id,'rank_math_robots',true),'rank_title'=>(string)get_post_meta($id,'rank_math_title',true),'rank_description'=>(string)get_post_meta($id,'rank_math_description',true)];}echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save(name,php);s,b,f=get(BASE+'/'+name+'?t='+str(int(time.time())),300);print('PROBE',s,f,'BYTES',len(b));
if s!=200:raise SystemExit('probe failed')
rows=json.loads(b.decode('utf-8','replace'));print('PUBLISHED',len(rows))
SAFE=[];AUTH=[];DECISION=[];WARN=[];short_candidates=[]
for p in rows:
 reasons_auth=[];reasons_dec=[];reasons_safe=[];warnings=[]
 if not str(p.get('sku','')).strip():reasons_auth.append('parent_sku_missing')
 for v in p.get('variations',[]):
  if not str(v.get('sku','')).strip():reasons_auth.append('variation_sku_missing:'+str(v['id']))
  if not str(v.get('price','')).strip():reasons_auth.append('variation_price_missing:'+str(v['id']))
 if not p.get('categories'):reasons_dec.append('no_category')
 robots=p.get('robots')
 if isinstance(robots,list) and 'noindex' in robots:reasons_dec.append('published_noindex_review')
 if p.get('description_words',0)==0:reasons_dec.append('description_missing_requires_verified_copy')
 if not p.get('featured_image'):reasons_dec.append('featured_image_missing')
 empty=[x['id'] for x in p.get('images',[]) if not str(x.get('alt','')).strip()]
 if empty:reasons_safe.append('image_alt_missing:'+','.join(map(str,empty)))
 if p.get('short_description_words',0)==0:reasons_safe.append('short_description_missing')
 if p.get('type')=='variable' and not p.get('variations'):reasons_dec.append('variable_without_variations')
 st,raw,final=get(p['url']+'?t='+str(int(time.time())),150);txt=raw.decode('utf-8','replace');head=txt.split('</head>',1)[0];meta=val(head,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)');canon=val(head,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)');rbt=val(head,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')
 if p.get('short_description_words',0)==0:
  source='none';candidate=''
  if meta and len(meta)>=30:source='public_meta_description';candidate=meta
  elif p.get('description'):
   chunks=[x.strip() for x in re.split(r'(?<=[.!؟])\s+|\n+',p['description']) if x.strip()]
   if chunks:source='existing_full_description_first_sentence';candidate=chunks[0][:320].strip()
  short_candidates.append({'id':p['id'],'title':p['title'],'source':source,'candidate':candidate,'candidate_len':len(candidate),'public_meta':meta})
 if st!=200:warnings.append('http_'+str(st))
 if 'noindex' not in rbt.lower() and norm(canon)!=norm(p['url']):warnings.append('canonical_public_mismatch')
 if reasons_safe:SAFE.append({'id':p['id'],'title':p['title'],'issues':reasons_safe})
 if reasons_auth:AUTH.append({'id':p['id'],'title':p['title'],'issues':reasons_auth})
 if reasons_dec:DECISION.append({'id':p['id'],'title':p['title'],'issues':reasons_dec})
 if warnings:WARN.append({'id':p['id'],'title':p['title'],'issues':warnings})
print('QUEUE_SAFE',json.dumps(SAFE,ensure_ascii=False,separators=(',',':')))
print('QUEUE_AUTH_REQUIRED',json.dumps(AUTH,ensure_ascii=False,separators=(',',':')))
print('QUEUE_DECISION_REQUIRED',json.dumps(DECISION,ensure_ascii=False,separators=(',',':')))
print('QUEUE_WARNINGS',json.dumps(WARN,ensure_ascii=False,separators=(',',':')))
print('SHORT_DESCRIPTION_CANDIDATES',json.dumps(short_candidates,ensure_ascii=False,separators=(',',':')))
print('SUMMARY',json.dumps({'safe_products':len(SAFE),'auth_required_products':len(AUTH),'decision_required_products':len(DECISION),'warning_products':len(WARN),'short_description_candidates':len(short_candidates)},sort_keys=True))
post={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_POST',json.dumps(post,sort_keys=True));
if post!=protected:raise SystemExit('ABORT protected changed during planner')
print('PASS LEGACY PRODUCT REMEDIATION PLAN V1')