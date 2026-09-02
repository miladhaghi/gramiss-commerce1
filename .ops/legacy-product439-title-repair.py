import hashlib,json,os,ssl,time,urllib.parse,urllib.request
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');HEALTHY=os.environ.get('HEALTHY_HOME_SHA','');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir'
PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3';CAT_SHA='75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PROTECTED={'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7','template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d','assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0','assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
ID=439;CURRENT='کتونی سبک ونس D&amp;G';EXPECTED='کتونی سبک ونس D&G'
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
def get(u):
 r=urllib.request.Request(u,headers={'User-Agent':'GramissProduct439TitleRepair/1.1','Cache-Control':'no-cache','Pragma':'no-cache'});return urllib.request.urlopen(r,context=CTX,timeout=180).read()
def hashes():return {p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED}
def sm(path):
 import re,html
 b=get(BASE+'/'+path+'?t='+str(int(time.time()))).decode('utf-8','replace');urls=sorted(html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>',b,re.I));return len(urls),hashlib.sha256('\n'.join(urls).encode()).hexdigest()
def call(mode):
 name='gramiss-p439-title-'+mode+'-'+hashlib.sha256((mode+str(time.time())).encode()).hexdigest()[:12]+'.php'
 php=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);global $wpdb;$id=439;$current='''+json.dumps(CURRENT,ensure_ascii=False)+r''';$expected='''+json.dumps(EXPECTED,ensure_ascii=False)+r''';$mode='''+json.dumps(mode)+r''';$p=get_post($id);$wc=wc_get_product($id);$o=['ok'=>true,'errors'=>[],'before'=>null,'after'=>null];if(!$p||!$wc){$o['errors'][]='missing';}else{$cats=wp_get_post_terms($id,'product_cat',['fields'=>'names']);$robots=get_post_meta($id,'rank_math_robots',true);$vars=[];if($wc->is_type('variable'))foreach($wc->get_children() as $vid){$v=wc_get_product($vid);if($v)$vars[]=['id'=>(int)$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price()];}$o['before']=['title'=>$p->post_title,'excerpt'=>$p->post_excerpt,'status'=>$p->post_status,'cats'=>$cats,'robots'=>$robots,'vars'=>$vars];if($p->post_status!=='publish')$o['errors'][]='status';if(trim((string)$p->post_excerpt)!=='')$o['errors'][]='excerpt';if(!in_array('کتونی',$cats,true))$o['errors'][]='family';if(is_array($robots)&&in_array('noindex',$robots,true))$o['errors'][]='noindex';foreach($vars as $v){if(trim((string)$v['sku'])==='')$o['errors'][]='sku:'.$v['id'];if(trim((string)$v['price'])==='')$o['errors'][]='price:'.$v['id'];}if($mode==='apply'&&$p->post_title!==$current)$o['errors'][]='unexpected-current-title';if($mode==='rollback'&&$p->post_title!==$expected)$o['errors'][]='unexpected-repair-title';if(empty($o['errors'])){$to=$mode==='apply'?$expected:$current;$r=$wpdb->update($wpdb->posts,['post_title'=>$to],['ID'=>$id],['%s'],['%d']);if($r===false)$o['errors'][]='db-update';clean_post_cache($id);wp_cache_flush();do_action('litespeed_purge_all');do_action('rank_math/sitemap/flush_cache');}$q=get_post($id);if($q)$o['after']=['title'=>$q->post_title,'excerpt'=>$q->post_excerpt];}$o['ok']=empty($o['errors']);echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
 save(name,php);d=json.loads(get(BASE+'/'+name+'?t='+str(int(time.time()))).decode('utf-8','replace'));print('WP',mode,json.dumps(d,ensure_ascii=False,separators=(',',':')));return d
pre=hashes();print('PROTECTED_PRE',json.dumps(pre,sort_keys=True));
if pre!=PROTECTED or (HEALTHY and pre['front-page.php']!=HEALTHY):raise SystemExit('protected drift')
ps=sm('product-sitemap.xml');cs=sm('product_cat-sitemap.xml');print('SITEMAP_PRE',ps,cs)
if ps!=(47,PRODUCT_SHA) or cs!=(20,CAT_SHA):raise SystemExit('sitemap drift')
applied=False
try:
 d=call('apply');
 if not d.get('ok') or (d.get('after') or {}).get('title')!=EXPECTED or (d.get('after') or {}).get('excerpt')!='':raise RuntimeError('repair '+str(d))
 applied=True
 ps2=sm('product-sitemap.xml');cs2=sm('product_cat-sitemap.xml');post=hashes();print('SITEMAP_POST',ps2,cs2);print('PROTECTED_POST',json.dumps(post,sort_keys=True))
 if ps2!=ps or cs2!=cs or post!=pre:raise RuntimeError('post-guard drift')
 print('PASS PRODUCT 439 TITLE REPAIR')
except Exception as e:
 print('FAIL',repr(e))
 if applied:
  try:print('ROLLBACK',json.dumps(call('rollback'),ensure_ascii=False,separators=(',',':')))
  except Exception as rb:print('ROLLBACK_FAIL',repr(rb))
 raise
