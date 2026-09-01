import hashlib,json,os,ssl,time,urllib.parse,urllib.request
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
  except Exception as exc:last=exc;print('API_RETRY',n+1,exc);time.sleep(2+n*2)
 raise last
def theme(rel):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel);x=api('get_file_content',{'dir':ROOT if not d else ROOT+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(x,dict):
  for k in ('content','file_content','data'):
   if isinstance(x.get(k),str):return x[k]
 return x if isinstance(x,str) else ''
def save(n,c):return api('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
pre={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_PRE',json.dumps(pre,sort_keys=True));
if pre!=PROTECTED:raise SystemExit('protected drift')
if HEALTHY and pre['front-page.php']!=HEALTHY:raise SystemExit('home drift')
nonce=hashlib.sha256((str(time.time())+pre['front-page.php']).encode()).hexdigest()[:12];name='gramiss-family-discovery-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function root_term($t){while($t && (int)$t->parent>0){$t=get_term((int)$t->parent,'product_cat');if(is_wp_error($t))return null;}return $t;}
$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>false]);$roots=[];foreach($terms as $t){if((int)$t->parent===0)$roots[(string)$t->term_id]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count];}
$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);$rows=[];$groups=[];foreach($ids as $id){$p=get_post($id);if(trim((string)$p->post_excerpt)!=='')continue;$wc=wc_get_product($id);if(!$wc)continue;$robots=get_post_meta($id,'rank_math_robots',true);$noindex=is_array($robots)&&in_array('noindex',$robots,true);$vars=[];$blockers=[];if(trim((string)$wc->get_sku())==='')$blockers[]='parent_sku_missing';if($wc->is_type('variable')){foreach($wc->get_children() as $vid){$v=wc_get_product($vid);if(!$v)continue;$vars[]=['id'=>(int)$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price(),'stock_status'=>$v->get_stock_status(),'attributes'=>$v->get_attributes()];if(trim((string)$v->get_sku())==='')$blockers[]='variation_sku_missing:'.$vid;if(trim((string)$v->get_price())==='')$blockers[]='variation_price_missing:'.$vid;}}
$attrs=[];foreach($wc->get_attributes() as $a){$vals=$a->is_taxonomy()?wc_get_product_terms($id,$a->get_name(),['fields'=>'names']):$a->get_options();$attrs[]=['name'=>$a->get_name(),'variation'=>$a->get_variation(),'visible'=>$a->get_visible(),'values'=>$vals];}
$cats=wp_get_post_terms($id,'product_cat');$root_ids=[];$cat_rows=[];foreach($cats as $t){$r=root_term($t);if($r)$root_ids[(string)$r->term_id]=true;$cat_rows[]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'parent'=>(int)$t->parent];}
$row=['id'=>(int)$id,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>get_permalink($id),'type'=>$wc->get_type(),'noindex'=>$noindex,'categories'=>$cat_rows,'root_ids'=>array_map('intval',array_keys($root_ids)),'attributes'=>$attrs,'variations'=>$vars,'blockers'=>$blockers];$rows[]=$row;foreach(array_keys($root_ids) as $rid){if(!isset($groups[$rid]))$groups[$rid]=['root'=>$roots[$rid]??['id'=>(int)$rid],'candidate_ids'=>[],'safe_ids'=>[],'blocked_ids'=>[],'noindex_ids'=>[]];$groups[$rid]['candidate_ids'][]=(int)$id;if($noindex)$groups[$rid]['noindex_ids'][]=(int)$id;$hard=array_values(array_filter($blockers,fn($x)=>strpos($x,'variation_')===0));if(!$noindex&&empty($hard))$groups[$rid]['safe_ids'][]=(int)$id;else$groups[$rid]['blocked_ids'][]=(int)$id;}}
echo wp_json_encode(['published'=>count($ids),'roots'=>array_values($roots),'groups'=>array_values($groups),'rows'=>$rows],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save(name,php);req=urllib.request.Request(BASE+'/'+name+'?t='+str(int(time.time())),headers={'User-Agent':'GramissLegacyFamilyDiscovery/1.0'});raw=urllib.request.urlopen(req,context=CTX,timeout=240).read();d=json.loads(raw.decode('utf-8','replace'))
print('PUBLISHED',d.get('published'));groups=sorted(d.get('groups',[]),key=lambda g:(-len(g.get('safe_ids',[])),str((g.get('root') or {}).get('name',''))));print('FAMILY_SUMMARY',json.dumps(groups,ensure_ascii=False,separators=(',',':')))
byid={r['id']:r for r in d.get('rows',[])}
for g in groups:
 root=g.get('root') or {};safe=g.get('safe_ids',[]);blocked=g.get('blocked_ids',[]);print('FAMILY',json.dumps({'root':root,'safe_count':len(safe),'blocked_count':len(blocked),'noindex_count':len(g.get('noindex_ids',[])),'safe_preview':[byid[i] for i in safe[:8]],'blocked_preview':[{'id':i,'title':byid[i]['title'],'blockers':byid[i]['blockers'],'noindex':byid[i]['noindex']} for i in blocked[:8]]},ensure_ascii=False,separators=(',',':')))
post={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_POST',json.dumps(post,sort_keys=True));
if post!=pre:raise SystemExit('protected changed')
print('PASS LEGACY FAMILY DISCOVERY V1')