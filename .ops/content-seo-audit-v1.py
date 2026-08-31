import hashlib,json,os,re,ssl,time,urllib.parse,urllib.request
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
 r=urllib.request.Request(u,headers={'User-Agent':'GramissContentSEOAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 with urllib.request.urlopen(r,context=ctx,timeout=180) as z:return z.status,z.read(),z.geturl()
home_sha=hashlib.sha256(read_theme('front-page.php').encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch')
nonce=hashlib.sha256((str(time.time())+home_sha).encode()).hexdigest()[:14];name='gramiss-content-seo-audit-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function g_words($s){$s=trim(wp_strip_all_tags(strip_shortcodes((string)$s)));if($s==='')return 0;$p=preg_split('/\s+/u',$s,-1,PREG_SPLIT_NO_EMPTY);return is_array($p)?count($p):0;}
function g_clean($v){if(is_array($v)){foreach($v as $k=>$x)$v[$k]=g_clean($x);return $v;}if(is_object($v))return g_clean((array)$v);return $v;}
function g_rm_meta_post($id){$keys=['rank_math_title','rank_math_description','rank_math_robots','rank_math_focus_keyword','rank_math_schema_Product','rank_math_schema_Article','rank_math_facebook_title','rank_math_facebook_description'];$o=[];foreach($keys as $k){$v=get_post_meta($id,$k,true);if($v!==''&&$v!==[])$o[$k]=g_clean($v);}return $o;}
function g_rm_meta_term($id){$keys=['rank_math_title','rank_math_description','rank_math_robots','rank_math_focus_keyword'];$o=[];foreach($keys as $k){$v=get_term_meta($id,$k,true);if($v!==''&&$v!==[])$o[$k]=g_clean($v);}return $o;}
function g_links($html){$a=[];if(preg_match_all('/href=["\']([^"\']+)/iu',(string)$html,$m)){foreach($m[1] as $u)$a[]=$u;}return array_values(array_unique($a));}
$counts=wp_count_posts('post');$post_counts=[];foreach(['publish','draft','pending','future','private','trash'] as $s)$post_counts[$s]=(int)($counts->$s??0);
$posts=[];$all=get_posts(['post_type'=>'post','post_status'=>['publish','draft','pending','future','private'],'posts_per_page'=>-1,'orderby'=>'ID','order'=>'ASC']);foreach($all as $p){$thumb=get_post_thumbnail_id($p->ID);$cats=wp_get_post_categories($p->ID,['fields'=>'all']);$tags=wp_get_post_tags($p->ID);$posts[]=['id'=>$p->ID,'status'=>$p->post_status,'title'=>$p->post_title,'slug'=>$p->post_name,'date'=>$p->post_date,'modified'=>$p->post_modified,'url'=>$p->post_status==='publish'?get_permalink($p->ID):'','words'=>g_words($p->post_content),'content_chars'=>mb_strlen(wp_strip_all_tags($p->post_content)),'excerpt_chars'=>mb_strlen(wp_strip_all_tags($p->post_excerpt)),'featured_image'=>$thumb?['id'=>$thumb,'alt'=>(string)get_post_meta($thumb,'_wp_attachment_image_alt',true),'title'=>get_the_title($thumb)]:null,'categories'=>array_map(fn($t)=>['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug],$cats),'tags'=>array_map(fn($t)=>['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug],$tags),'links'=>g_links($p->post_content),'seo'=>g_rm_meta_post($p->ID),'comments'=>$p->comment_status];}
$cats=[];foreach(get_terms(['taxonomy'=>'category','hide_empty'=>false]) as $t)$cats[]=['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>$t->count,'description'=>$t->description,'url'=>get_term_link($t),'seo'=>g_rm_meta_term($t->term_id)];
$tags=[];foreach(get_terms(['taxonomy'=>'post_tag','hide_empty'=>false]) as $t)$tags[]=['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>$t->count,'description'=>$t->description,'seo'=>g_rm_meta_term($t->term_id)];
$pages=[];foreach(get_pages(['sort_column'=>'ID']) as $p)$pages[]=['id'=>$p->ID,'title'=>$p->post_title,'slug'=>$p->post_name,'status'=>$p->post_status,'url'=>get_permalink($p->ID),'words'=>g_words($p->post_content)];
$titles=get_option('rank-math-options-titles',[]);$title_subset=[];if(is_array($titles)){foreach($titles as $k=>$v){if(preg_match('/^(pt_post|tax_category|author|date|homepage|knowledgegraph|separator|social_url)/',$k))$title_subset[$k]=g_clean($v);}}
$sitemap=get_option('rank-math-options-sitemap',[]);
$theme=wp_get_theme();$td=get_template_directory();$files=[];foreach(['front-page.php','home.php','single.php','archive.php','category.php','index.php','search.php','404.php','comments.php','functions.php','header.php','footer.php'] as $f){$path=$td.'/'.$f;if(file_exists($path))$files[$f]=['bytes'=>filesize($path),'sha256'=>hash_file('sha256',$path)];else $files[$f]=null;}
$menus=[];foreach(wp_get_nav_menus() as $m){$items=[];foreach(wp_get_nav_menu_items($m->term_id)?:[] as $i)$items[]=['title'=>$i->title,'url'=>$i->url,'type'=>$i->type,'object'=>$i->object,'object_id'=>(int)$i->object_id];$menus[]=['name'=>$m->name,'slug'=>$m->slug,'items'=>$items];}
$posts_page=(int)get_option('page_for_posts');$front=(int)get_option('page_on_front');
$out=['site'=>['home'=>home_url('/'),'siteurl'=>site_url('/'),'wp_version'=>get_bloginfo('version'),'theme'=>$theme->get('Name'),'theme_version'=>$theme->get('Version'),'show_on_front'=>get_option('show_on_front'),'page_on_front'=>$front,'front_title'=>$front?get_the_title($front):'','page_for_posts'=>$posts_page,'posts_page_title'=>$posts_page?get_the_title($posts_page):'','posts_page_url'=>$posts_page?get_permalink($posts_page):'','permalink_structure'=>get_option('permalink_structure'),'timezone'=>wp_timezone_string()],'counts'=>$post_counts,'posts'=>$posts,'categories'=>$cats,'tags'=>$tags,'pages'=>$pages,'rank_math'=>['titles'=>$title_subset,'sitemap'=>g_clean($sitemap)],'theme_files'=>$files,'menus'=>$menus,'plugins'=>['rank_math'=>defined('RANK_MATH_VERSION')?RANK_MATH_VERSION:null,'woocommerce'=>defined('WC_VERSION')?WC_VERSION:null,'mu_plugins'=>array_keys(get_mu_plugins())]];echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,f=get('https://gramiss.ir/'+name+'?t='+str(int(time.time())));print('PROBE',s,f,'BYTES',len(b))
if s!=200:raise SystemExit(b.decode('utf-8','replace')[:1000])
data=json.loads(b.decode('utf-8','replace'));print('SITE',json.dumps(data['site'],ensure_ascii=False));print('COUNTS',json.dumps(data['counts'],ensure_ascii=False));print('POSTS',json.dumps(data['posts'],ensure_ascii=False));print('CATEGORIES',json.dumps(data['categories'],ensure_ascii=False));print('TAGS',json.dumps(data['tags'],ensure_ascii=False));print('PAGES',json.dumps(data['pages'],ensure_ascii=False));print('RANK_MATH',json.dumps(data['rank_math'],ensure_ascii=False));print('THEME_FILES',json.dumps(data['theme_files'],ensure_ascii=False));print('MENUS',json.dumps(data['menus'],ensure_ascii=False));print('PLUGINS',json.dumps(data['plugins'],ensure_ascii=False))
# live sitemap inventory
s,raw,f=get('https://gramiss.ir/sitemap_index.xml?t='+str(int(time.time())));txt=raw.decode('utf-8','replace');locs=re.findall(r'<loc>(.*?)</loc>',txt,re.I);print('SITEMAP_INDEX',s,locs)
for u in locs:
 try:
  cs,cr,cf=get(u+'?t='+str(int(time.time())));n=len(re.findall(r'<url>',cr.decode('utf-8','replace'),re.I));print('SITEMAP_CHILD',u,cs,n)
 except Exception as e:print('SITEMAP_CHILD_ERROR',u,str(e))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:raise SystemExit('Home changed during read-only audit')
print('PASS READ ONLY CONTENT SEO AUDIT V1');print('HOME SHA PRESERVED',home_sha)
