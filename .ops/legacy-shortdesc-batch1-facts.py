import hashlib,json,os,ssl,time,urllib.parse,urllib.request
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir';IDS=[163,167,197,202,215]
PROTECTED={'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7','template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d','assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0','assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
def api(fn,p,post=False):
 u=f'https://{HOST}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();last=None
 for n in range(5):
  try:
   r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=CTX,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
   q=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
   return q.get('data')
  except Exception as exc:last=exc;print('RETRY',n+1,exc);time.sleep(2+n)
 raise last
def theme(rel):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel);x=api('get_file_content',{'dir':ROOT if not d else ROOT+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(x,dict):
  for k in ('content','file_content','data'):
   if isinstance(x.get(k),str):return x[k]
 return x if isinstance(x,str) else ''
def save(n,c):return api('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
pre={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_PRE',json.dumps(pre,sort_keys=True));
if pre!=PROTECTED:raise SystemExit('ABORT protected drift')
nonce=hashlib.sha256((str(time.time())+pre['front-page.php']).encode()).hexdigest()[:12];name='gramiss-shortdesc-facts-'+nonce+'.php';ids=','.join(map(str,IDS))
php='''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$ids=['''+ids+'''];$o=[];foreach($ids as $id){$p=get_post($id);$wc=wc_get_product($id);if(!$p||!$wc){$o[]=['id'=>$id,'error'=>'missing'];continue;}$attrs=[];foreach($wc->get_attributes() as $a){$vals=$a->is_taxonomy()?wc_get_product_terms($id,$a->get_name(),['fields'=>'names']):$a->get_options();$attrs[]=['name'=>$a->get_name(),'variation'=>$a->get_variation(),'visible'=>$a->get_visible(),'values'=>$vals];}$vars=[];if($wc->is_type('variable'))foreach($wc->get_children() as $vid){$v=wc_get_product($vid);if($v)$vars[]=['id'=>$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price(),'stock_status'=>$v->get_stock_status(),'attributes'=>$v->get_attributes()];}$cats=wp_get_post_terms($id,'product_cat',['fields'=>'names']);$o[]=['id'=>$id,'status'=>$p->post_status,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>get_permalink($id),'type'=>$wc->get_type(),'parent_sku'=>$wc->get_sku(),'description'=>trim(preg_replace('/\\s+/u',' ',wp_strip_all_tags(strip_shortcodes($p->post_content)))),'short_description'=>trim(preg_replace('/\\s+/u',' ',wp_strip_all_tags(strip_shortcodes($p->post_excerpt)))),'categories'=>$cats,'attributes'=>$attrs,'variations'=>$vars,'robots'=>get_post_meta($id,'rank_math_robots',true)];}echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save(name,php);url=BASE+'/'+name+'?t='+str(int(time.time()));req=urllib.request.Request(url,headers={'User-Agent':'GramissShortDescFacts/1.0'});raw=urllib.request.urlopen(req,context=CTX,timeout=180).read();rows=json.loads(raw.decode('utf-8','replace'));print('BATCH1_FACTS',json.dumps(rows,ensure_ascii=False,separators=(',',':')))
for p in rows:
 if p.get('error'):raise SystemExit('missing '+str(p['id']))
 if p['status']!='publish':raise SystemExit('not published '+str(p['id']))
 if p['short_description']:raise SystemExit('excerpt already filled '+str(p['id']))
 if p['type']=='variable':
  for v in p['variations']:
   if not str(v.get('sku','')).strip():raise SystemExit('variation SKU gap '+str(v['id']))
   if not str(v.get('price','')).strip():raise SystemExit('variation price gap '+str(v['id']))
post={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_POST',json.dumps(post,sort_keys=True));
if post!=pre:raise SystemExit('protected changed')
print('PASS SHORT DESCRIPTION BATCH1 FACTS')