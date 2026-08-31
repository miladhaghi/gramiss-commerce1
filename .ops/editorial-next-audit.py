import hashlib,json,os,ssl,time,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();req=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');req.add_header('Authorization',f'cpanel {user}:{token}')
 if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(req,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
 q=o.get('result') if isinstance(o.get('result'),dict) else o
 if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
 return q.get('data')
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
h=hashlib.sha256(read_theme('front-page.php').encode()).hexdigest();print('HOME_SHA',h)
if healthy and h!=healthy:raise SystemExit('ABORT Home mismatch')
name='gramiss-editorial-next-audit-'+str(int(time.time()))+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$cats=[];$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>false]);foreach($terms as $t){$cats[]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'url'=>is_wp_error(get_term_link($t))?'':get_term_link($t)];}
$posts=[];$q=new WP_Query(['post_type'=>'product','post_status'=>'publish','posts_per_page'=>-1,'orderby'=>'ID','order'=>'ASC']);foreach($q->posts as $p){$title=$p->post_title;if(preg_match('/لینن|سیلک|تیشرت|شلوار|پیراهن/u',$title)){$ts=wp_get_post_terms($p->ID,'product_cat');$posts[]=['id'=>(int)$p->ID,'title'=>$title,'url'=>get_permalink($p),'cats'=>array_map(fn($x)=>['name'=>$x->name,'slug'=>$x->slug],$ts),'price'=>get_post_meta($p->ID,'_price',true)];}}
$ecats=[];foreach(get_terms(['taxonomy'=>'category','hide_empty'=>false]) as $t){$ecats[]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'url'=>is_wp_error(get_term_link($t))?'':get_term_link($t),'robots'=>get_term_meta($t->term_id,'rank_math_robots',true)];}
$articles=[];foreach(get_posts(['post_type'=>'post','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC']) as $p){$articles[]=['id'=>(int)$p->ID,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>get_permalink($p),'cats'=>wp_get_post_categories($p->ID,['fields'=>'names'])];}
echo wp_json_encode(['product_categories'=>$cats,'matching_products'=>$posts,'editorial_categories'=>$ecats,'articles'=>$articles],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save(name,php)
req=urllib.request.Request('https://gramiss.ir/'+name+'?t='+str(int(time.time())),headers={'User-Agent':'GramissEditorialNextAudit/1.0'})
with urllib.request.urlopen(req,context=ctx,timeout=180) as z:b=z.read().decode('utf-8','replace');print('AUDIT',z.status,b)
print('PASS EDITORIAL NEXT AUDIT')
