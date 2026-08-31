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
 r=urllib.request.Request(u,headers={'User-Agent':'GramissContentSEOAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 try:
  with urllib.request.urlopen(r,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
 except urllib.error.HTTPError as e:return e.code,e.read(),u
front=read_theme('front-page.php');sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch; audit not run')
nonce=hashlib.sha256((str(time.time())+sha).encode()).hexdigest()[:14];name='gramiss-content-seo-audit-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function g_words($s){$s=trim(wp_strip_all_tags(strip_shortcodes((string)$s)));if($s==='')return 0;$x=preg_split('/\s+/u',$s,-1,PREG_SPLIT_NO_EMPTY);return is_array($x)?count($x):0;}
function g_meta($id,$k){return get_post_meta($id,$k,true);}
$o=[];$pf=(int)get_option('page_on_front');$pp=(int)get_option('page_for_posts');$o['wp']=['home'=>home_url('/'),'siteurl'=>site_url('/'),'show_on_front'=>get_option('show_on_front'),'page_on_front'=>$pf,'front_title'=>$pf?get_the_title($pf):null,'page_for_posts'=>$pp,'posts_title'=>$pp?get_the_title($pp):null,'posts_url'=>$pp?get_permalink($pp):null,'permalink_structure'=>get_option('permalink_structure'),'blog_public'=>get_option('blog_public'),'timezone'=>wp_timezone_string()];
$cnt=wp_count_posts('post');$o['counts']=['publish'=>(int)($cnt->publish??0),'draft'=>(int)($cnt->draft??0),'pending'=>(int)($cnt->pending??0),'future'=>(int)($cnt->future??0),'private'=>(int)($cnt->private??0)];
$o['posts']=[];$ids=get_posts(['post_type'=>'post','post_status'=>['publish','draft','pending','future','private'],'numberposts'=>-1,'orderby'=>'date','order'=>'DESC','fields'=>'ids']);foreach($ids as $id){$p=get_post($id);$cats=wp_get_post_terms($id,'category',['fields'=>'all']);$tags=wp_get_post_terms($id,'post_tag',['fields'=>'all']);$o['posts'][]=['id'=>$id,'status'=>$p->post_status,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>$p->post_status==='publish'?get_permalink($id):null,'date'=>$p->post_date,'modified'=>$p->post_modified,'words'=>g_words($p->post_content),'excerpt_words'=>g_words($p->post_excerpt),'featured_image'=>(int)get_post_thumbnail_id($id),'categories'=>array_map(fn($t)=>['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug],$cats),'tags'=>array_map(fn($t)=>['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug],$tags),'seo'=>['title'=>g_meta($id,'rank_math_title'),'description'=>g_meta($id,'rank_math_description'),'focus_keyword'=>g_meta($id,'rank_math_focus_keyword'),'robots'=>g_meta($id,'rank_math_robots')]];}
$o['categories']=[];foreach(get_terms(['taxonomy'=>'category','hide_empty'=>false]) as $t)$o['categories'][]=['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'description'=>$t->description,'url'=>get_term_link($t),'seo'=>['title'=>get_term_meta($t->term_id,'rank_math_title',true),'description'=>get_term_meta($t->term_id,'rank_math_description',true),'robots'=>get_term_meta($t->term_id,'rank_math_robots',true)]];
$o['tags']=[];foreach(get_terms(['taxonomy'=>'post_tag','hide_empty'=>false]) as $t)$o['tags'][]=['id'=>$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'description'=>$t->description];
$o['pages']=[];foreach(get_posts(['post_type'=>'page','post_status'=>['publish','draft'],'numberposts'=>-1,'orderby'=>'menu_order title','order'=>'ASC']) as $p)$o['pages'][]=['id'=>$p->ID,'status'=>$p->post_status,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>$p->post_status==='publish'?get_permalink($p):null,'template'=>get_page_template_slug($p->ID),'words'=>g_words($p->post_content)];
$o['menus']=[];foreach(wp_get_nav_menus() as $m){$items=[];foreach((array)wp_get_nav_menu_items($m->term_id) as $i)$items[]=['title'=>$i->title,'url'=>$i->url,'type'=>$i->type,'object'=>$i->object,'object_id'=>(int)$i->object_id];$o['menus'][]=['id'=>$m->term_id,'name'=>$m->name,'items'=>$items];}
$titles=get_option('rank-math-options-titles',[]);$sel=[];foreach((array)$titles as $k=>$v)if(preg_match('/^(pt_post_|tax_category_|author_|date_|noindex_|disable_author|knowledgegraph)/',$k))$sel[$k]=$v;$o['rank_math_titles']=$sel;$sm=get_option('rank-math-options-sitemap',[]);$o['rank_math_sitemap']=$sm;
$dir=get_stylesheet_directory();$o['theme']=['stylesheet'=>get_stylesheet(),'template'=>get_template(),'dir'=>$dir,'files'=>[]];foreach(['single.php','home.php','archive.php','category.php','index.php','page.php','functions.php','header.php','footer.php'] as $f){$p=$dir.'/'.$f;$o['theme']['files'][$f]=file_exists($p)?['exists'=>true,'bytes'=>filesize($p),'sha256'=>hash_file('sha256',$p)]:['exists'=>false];}
echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save(name,php);s,b,f=get('https://gramiss.ir/'+name+'?t='+str(int(time.time())));print('PROBE',s,f,'BYTES',len(b))
if s!=200:raise SystemExit('audit probe failed')
d=json.loads(b.decode('utf-8','replace'));print('WP',json.dumps(d.get('wp'),ensure_ascii=False,separators=(',',':')));print('COUNTS',json.dumps(d.get('counts'),ensure_ascii=False,separators=(',',':')))
for p in d.get('posts',[]):print('POST',json.dumps(p,ensure_ascii=False,separators=(',',':')))
print('CATEGORIES',json.dumps(d.get('categories'),ensure_ascii=False,separators=(',',':')));print('TAGS',json.dumps(d.get('tags'),ensure_ascii=False,separators=(',',':')));print('PAGES',json.dumps(d.get('pages'),ensure_ascii=False,separators=(',',':')));print('MENUS',json.dumps(d.get('menus'),ensure_ascii=False,separators=(',',':')));print('RANK_MATH_TITLES',json.dumps(d.get('rank_math_titles'),ensure_ascii=False,separators=(',',':')));print('RANK_MATH_SITEMAP',json.dumps(d.get('rank_math_sitemap'),ensure_ascii=False,separators=(',',':')));print('THEME',json.dumps(d.get('theme'),ensure_ascii=False,separators=(',',':')))
for u in ['https://gramiss.ir/sitemap_index.xml','https://gramiss.ir/post-sitemap.xml','https://gramiss.ir/category-sitemap.xml','https://gramiss.ir/robots.txt']:
 ss,bb,ff=get(u+'?t='+str(int(time.time())));txt=bb.decode('utf-8','replace');locs=re.findall(r'<loc>(.*?)</loc>',txt,re.I);print('LIVE_RESOURCE',u,ss,'FINAL',ff,'LOCS',len(locs),'SAMPLE',json.dumps(locs[:8],ensure_ascii=False))
print('END READ ONLY CONTENT SEO AUDIT V1');print('HOME SHA PRESERVED',sha)