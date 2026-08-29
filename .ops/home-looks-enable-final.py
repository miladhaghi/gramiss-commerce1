import hashlib,json,os,re,ssl,time,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}');
 if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
 q=o.get('result') if isinstance(o.get('result'),dict) else o
 if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
 return q.get('data')
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'});
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u):
 r=urllib.request.Request(u,headers={'User-Agent':'GramissSitemapAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});
 with urllib.request.urlopen(r,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
f=read_theme('front-page.php');sha=hashlib.sha256(f.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-sitemap-audit-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function g1_meta($id){$o=[];foreach(['rank_math_robots','rank_math_title','rank_math_description','rank_math_canonical_url'] as $k){$v=get_post_meta($id,$k,true);if($v!==''&&$v!==null)$o[$k]=$v;}return $o;}
function g1_term_meta($id){$o=[];foreach(['rank_math_robots','rank_math_title','rank_math_description','rank_math_canonical_url'] as $k){$v=get_term_meta($id,$k,true);if($v!==''&&$v!==null)$o[$k]=$v;}return $o;}
$pages=[];foreach(get_posts(['post_type'=>'page','post_status'=>['publish','draft','private'],'numberposts'=>-1,'orderby'=>'ID','order'=>'ASC']) as $p)$pages[]=['id'=>$p->ID,'status'=>$p->post_status,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>get_permalink($p),'meta'=>g1_meta($p->ID)];
$posts=[];foreach(get_posts(['post_type'=>'post','post_status'=>['publish','draft','private'],'numberposts'=>-1,'orderby'=>'ID','order'=>'ASC']) as $p)$posts[]=['id'=>$p->ID,'status'=>$p->post_status,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>get_permalink($p),'meta'=>g1_meta($p->ID)];
$cats=[];foreach(get_terms(['taxonomy'=>'product_cat','hide_empty'=>false]) as $t)$cats[]=['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>$t->count,'parent'=>$t->parent,'url'=>get_term_link($t),'meta'=>g1_term_meta($t->term_id)];
$blogcats=[];foreach(get_terms(['taxonomy'=>'category','hide_empty'=>false]) as $t)$blogcats[]=['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>$t->count,'url'=>get_term_link($t),'meta'=>g1_term_meta($t->term_id)];
$attrs=[];if(function_exists('wc_get_attribute_taxonomies'))foreach(wc_get_attribute_taxonomies() as $a){$tax=wc_attribute_taxonomy_name($a->attribute_name);$terms=get_terms(['taxonomy'=>$tax,'hide_empty'=>false]);$attrs[]=['id'=>$a->attribute_id,'name'=>$a->attribute_name,'label'=>$a->attribute_label,'taxonomy'=>$tax,'public'=>(bool)$a->attribute_public,'terms'=>is_wp_error($terms)?[]:array_map(fn($t)=>['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>$t->count,'url'=>get_term_link($t),'meta'=>g1_term_meta($t->term_id)],$terms)];}
$sm=(array)get_option('rank_math_options_sitemap',[]);$titles=(array)get_option('rank_math_options_titles',[]);$sel=[];foreach($titles as $k=>$v){if(str_starts_with($k,'tax_product_cat')||str_starts_with($k,'tax_pa_')||str_starts_with($k,'pt_page')||str_starts_with($k,'pt_post')||str_starts_with($k,'pt_product'))$sel[$k]=$v;}
echo wp_json_encode(['registration_skip'=>get_option('rank_math_registration_skip'),'invalid'=>function_exists('rank_math')?(bool)rank_math()->registration->invalid:null,'sitemap_options'=>$sm,'title_selected'=>$sel,'pages'=>$pages,'posts'=>$posts,'product_categories'=>$cats,'blog_categories'=>$blogcats,'attributes'=>$attrs],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,u=get('https://gramiss.ir/'+name+'?t='+st);print('PROBE',s,u,'BYTES',len(b));data=json.loads(b.decode('utf-8','replace'));print('STATE',json.dumps(data,ensure_ascii=False,separators=(',',':')))
s,raw,u=get('https://gramiss.ir/sitemap_index.xml');txt=raw.decode('utf-8','replace');children=re.findall(r'<loc>(.*?)</loc>',txt,re.I);print('INDEX',s,u,json.dumps(children,ensure_ascii=False))
all_urls=[]
for child in children:
 try:
  cs,cr,cu=get(child);ct=cr.decode('utf-8','replace');locs=re.findall(r'<loc>(.*?)</loc>',ct,re.I);all_urls+=locs;print('CHILD',child,'STATUS',cs,'COUNT',len(locs),'URLS',json.dumps(locs,ensure_ascii=False))
 except Exception as e:print('CHILD_ERROR',child,str(e))
print('TOTAL_UNIQUE',len(set(all_urls)))
for needle in ['/cart/','/checkout/','/my-account/','/product-category/','/color/','/57-7cm/','/58-7cm/']:
 print('PRESENCE',needle,sum(1 for x in set(all_urls) if needle in x))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY SITEMAP AUDIT')
