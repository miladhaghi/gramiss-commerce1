import hashlib,json,os,re,ssl,time,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}')
 if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
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
def get(u):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissCategoryMetadataAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 with urllib.request.urlopen(req,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
def head(raw):
 t=raw.decode('utf-8','replace');h=t.split('</head>',1)[0]
 def one(p):
  m=re.search(p,h,re.I|re.S);return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
 return {'title':one(r'<title[^>]*>(.*?)</title>'),'description':one(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':one(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':one(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
front=read_theme('front-page.php');sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-category-meta-audit-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function pm($id){$o=[];foreach(['rank_math_title','rank_math_description','rank_math_canonical_url','rank_math_robots'] as $k){$v=get_post_meta($id,$k,true);$o[$k]=$v;}return $o;}
function tm($id){$o=[];foreach(['rank_math_title','rank_math_description','rank_math_canonical_url','rank_math_robots'] as $k){$v=get_term_meta($id,$k,true);$o[$k]=$v;}return $o;}
$cats=[];$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>true,'orderby'=>'term_id','order'=>'ASC']);foreach($terms as $t){$parent=$t->parent?get_term($t->parent,'product_cat'):null;$pids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>5,'fields'=>'ids','tax_query'=>[['taxonomy'=>'product_cat','field'=>'term_id','terms'=>$t->term_id]]]);$names=[];foreach($pids as $id)$names[]=['id'=>(int)$id,'name'=>get_the_title($id)];$cats[]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'parent_id'=>(int)$t->parent,'parent_name'=>$parent&&!is_wp_error($parent)?$parent->name:'','url'=>get_term_link($t),'description'=>trim(wp_strip_all_tags($t->description)),'description_len'=>mb_strlen(trim(wp_strip_all_tags($t->description))),'meta'=>tm($t->term_id),'sample_products'=>$names];}
$pages=[];foreach([20,9] as $id){$p=get_post($id);$pages[]=['id'=>$id,'title'=>$p?$p->post_title:'','slug'=>$p?$p->post_name:'','url'=>$p?get_permalink($p):'','excerpt'=>$p?trim(wp_strip_all_tags($p->post_excerpt)):'','content_text'=>$p?trim(wp_strip_all_tags($p->post_content)):'','meta'=>pm($id)];}
$opts=(array)get_option('rank-math-options-titles',[]);$selected=[];foreach(['homepage_title','homepage_description','pt_page_title','pt_page_description','pt_product_title','pt_product_description','tax_product_cat_title','tax_product_cat_description','tax_product_cat_robots'] as $k)$selected[$k]=$opts[$k]??null;
echo wp_json_encode(['rank_math_invalid'=>function_exists('rank_math')?(bool)rank_math()->registration->invalid:null,'pages'=>$pages,'categories'=>$cats,'title_options'=>$selected],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,u=get('https://gramiss.ir/'+name+'?t='+st);print('PROBE',s,u,'BYTES',len(b));data=json.loads(b.decode('utf-8','replace'));print('STATE',json.dumps(data,ensure_ascii=False,separators=(',',':')))
for label,u in [('home','https://gramiss.ir/'),('shop','https://gramiss.ir/shop/')]:
 s,r,f=get(u);print('HEAD',label,json.dumps({'status':s,'url':f,**head(r)},ensure_ascii=False,separators=(',',':')))
for c in data.get('categories',[]):
 s,r,f=get(c['url']);print('CAT_HEAD',c['id'],json.dumps({'name':c['name'],'status':s,'url':f,**head(r)},ensure_ascii=False,separators=(',',':')))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY CATEGORY METADATA AUDIT')
