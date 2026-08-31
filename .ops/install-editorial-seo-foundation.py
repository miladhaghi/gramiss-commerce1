import hashlib,json,os,ssl,time,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
PLUGIN='''<?php
/**
 * Plugin Name: Gramiss Editorial SEO Foundation
 * Description: Keeps the magazine indexable only when it has published editorial content.
 * Version: 1.0.0
 */
defined('ABSPATH') || exit;
function gramiss_editorial_robots_exact($robots,$wanted){if(!is_array($robots))return false;$a=array_values(array_unique(array_map('strval',$robots)));$b=$wanted;sort($a);sort($b);return $a===$b;}
function gramiss_editorial_published_count(){global $wpdb;return (int)$wpdb->get_var("SELECT COUNT(ID) FROM {$wpdb->posts} WHERE post_type='post' AND post_status='publish'");}
function gramiss_editorial_invalidate_page_sitemap(){if(class_exists('RankMath\\Sitemap\\Cache')){\\RankMath\\Sitemap\\Cache::invalidate_storage('page');}}
function gramiss_editorial_sync_blog_indexability(){
    $page_id=(int)get_option('page_for_posts');if($page_id<1)return;
    $published=gramiss_editorial_published_count();$robots=get_post_meta($page_id,'rank_math_robots',true);$flag=(string)get_post_meta($page_id,'_gramiss_auto_noindex_empty_blog',true);$changed=false;
    if($flag!=='1'){
        if($published===0 && gramiss_editorial_robots_exact($robots,['noindex','follow'])){update_post_meta($page_id,'_gramiss_auto_noindex_empty_blog','1');$flag='1';}
        else{return;}
    }
    if($published>0){
        if($robots===''||$robots===[]){return;}
        if(gramiss_editorial_robots_exact($robots,['noindex','follow'])){delete_post_meta($page_id,'rank_math_robots');$changed=true;}
        else{delete_post_meta($page_id,'_gramiss_auto_noindex_empty_blog');return;}
    }else{
        if(gramiss_editorial_robots_exact($robots,['noindex','follow']))return;
        if($robots===''||$robots===[]){update_post_meta($page_id,'rank_math_robots',['noindex','follow']);$changed=true;}
        else{delete_post_meta($page_id,'_gramiss_auto_noindex_empty_blog');return;}
    }
    if($changed)gramiss_editorial_invalidate_page_sitemap();
}
add_action('wp',function(){if(is_home())gramiss_editorial_sync_blog_indexability();},1);
add_action('transition_post_status',function($new,$old,$post){if($post instanceof WP_Post && $post->post_type==='post' && $new!==$old)gramiss_editorial_sync_blog_indexability();},99,3);
add_action('deleted_post',function($post_id,$post){if($post instanceof WP_Post && $post->post_type==='post')gramiss_editorial_sync_blog_indexability();},99,2);
'''
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
  except Exception as exc:last=exc;print('ATTEMPT',attempt,fn,str(exc));time.sleep(attempt*2 if attempt<4 else 0)
 raise last
def read_file(directory,file):
 try:d=call('get_file_content',{'dir':directory,'file':file,'from_charset':'_DETECT_','to_charset':'utf-8'})
 except Exception:return None
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else None
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);return read_file(root if not p else root+'/'+p,n) or ''
def write_file(directory,file,content):return call('save_file_content',{'dir':directory,'file':file,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u):
 r=urllib.request.Request(u,headers={'User-Agent':'GramissEditorialSEOInstall/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});
 with urllib.request.urlopen(r,context=ctx,timeout=180) as z:return z.status,z.read(),z.geturl()
home_sha=hashlib.sha256(read_theme('front-page.php').encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch')
dir='public_html/wp-content/mu-plugins';file='gramiss-editorial-seo-foundation.php';old=read_file(dir,file);expected_sha=hashlib.sha256(PLUGIN.encode()).hexdigest();
if old is not None and old!='' and hashlib.sha256(old.encode()).hexdigest()!=expected_sha:raise SystemExit('ABORT existing editorial SEO plugin drift')
write_file(dir,file,PLUGIN);readback=read_file(dir,file) or ''
if hashlib.sha256(readback.encode()).hexdigest()!=expected_sha:raise SystemExit('plugin exact write verify failed')
# Load blog while zero posts; plugin claims the existing empty-blog noindex state and marks it managed.
s,b,f=get('https://gramiss.ir/%D9%88%D8%A8%D9%84%D8%A7%DA%AF/?t='+str(int(time.time())));print('BLOG_LOAD',s,f,'BYTES',len(b))
if s!=200:raise SystemExit('blog load failed')
# DB verify through self deleting helper
nonce=hashlib.sha256((str(time.time())+expected_sha).encode()).hexdigest()[:14];helper='gramiss-editorial-seo-verify-'+nonce+'.php';php=r'''<?php header('Content-Type:application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$id=(int)get_option('page_for_posts');$c=wp_count_posts('post');echo wp_json_encode(['page'=>$id,'robots'=>get_post_meta($id,'rank_math_robots',true),'flag'=>get_post_meta($id,'_gramiss_auto_noindex_empty_blog',true),'published'=>(int)($c->publish??0),'plugin'=>file_exists(WPMU_PLUGIN_DIR.'/gramiss-editorial-seo-foundation.php'),'sha'=>file_exists(WPMU_PLUGIN_DIR.'/gramiss-editorial-seo-foundation.php')?hash_file('sha256',WPMU_PLUGIN_DIR.'/gramiss-editorial-seo-foundation.php'):null],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);''';write_file('public_html',helper,php);vs,vb,vf=get('https://gramiss.ir/'+helper+'?t='+str(int(time.time())));print('STATE',vs,vb.decode('utf-8','replace'));state=json.loads(vb.decode('utf-8','replace'))
if vs!=200 or state.get('published')!=0 or state.get('flag')!='1' or sorted(state.get('robots') or [])!=['follow','noindex'] or state.get('sha')!=expected_sha:raise SystemExit('editorial SEO state verify failed')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:raise SystemExit('Home changed')
print('PASS EDITORIAL SEO FOUNDATION INSTALLED',expected_sha);print('HOME SHA PRESERVED',home_sha)
