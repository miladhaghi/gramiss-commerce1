import hashlib,json,os,ssl,time,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}');
 if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
 q=o.get('result') if isinstance(o.get('result'),dict) else o
 if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
 return q.get('data')
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'});return d.get('content','') if isinstance(d,dict) else d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u):
 r=urllib.request.Request(u,headers={'User-Agent':'GramissBlogMetaAudit/1.0','Cache-Control':'no-cache'});
 with urllib.request.urlopen(r,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
sha=hashlib.sha256(read_theme('front-page.php').encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
name='gramiss-blog-meta-audit-'+hashlib.sha256((str(time.time())+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$id=(int)get_option('page_for_posts');$keys=['rank_math_title','rank_math_description','rank_math_robots','rank_math_advanced_robots','rank_math_canonical_url','_gramiss_auto_noindex_empty_blog'];$meta=[];foreach($keys as $k)$meta[$k]=get_post_meta($id,$k,true);$p=get_post($id);$count=wp_count_posts('post');echo wp_json_encode(['id'=>$id,'title'=>$p?$p->post_title:null,'slug'=>$p?$p->post_name:null,'url'=>get_permalink($id),'status'=>$p?$p->post_status:null,'meta'=>$meta,'published'=>(int)($count->publish??0),'page_in_sitemap'=>class_exists('RankMath\\Sitemap\\Cache')],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save(name,php);s,b,f=get('https://gramiss.ir/'+name+'?t='+str(int(time.time())));print('AUDIT',s,b.decode('utf-8','replace'));print('HOME_SHA_AFTER',hashlib.sha256(read_theme('front-page.php').encode()).hexdigest())
