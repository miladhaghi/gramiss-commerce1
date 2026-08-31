import hashlib,json,os,ssl,time,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}')
 if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
 q=o.get('result') if isinstance(o.get('result'),dict) else o
 if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
 return q.get('data')
def read(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
front=read('front-page.php');sha=hashlib.sha256(front.encode()).hexdigest();print('HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('Home mismatch')
n='gramiss-blog-indexability-'+hashlib.sha256((str(time.time())+sha).encode()).hexdigest()[:12]+'.php'
php=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$m=get_post_meta(22);$rm=[];foreach($m as $k=>$v)if(strpos($k,'rank_math')===0)$rm[$k]=$v;$titles=get_option('rank-math-options-titles',[]);$picked=[];foreach((array)$titles as $k=>$v)if(preg_match('/home|homepage|robots|archive|post/i',$k))$picked[$k]=$v;$general=get_option('rank-math-options-general',[]);$gp=[];foreach((array)$general as $k=>$v)if(preg_match('/robot|link|strip|breadcrumb/i',$k))$gp[$k]=$v;echo wp_json_encode(['page22'=>['title'=>get_the_title(22),'status'=>get_post_status(22),'meta'=>$rm],'published_posts'=>(int)wp_count_posts('post')->publish,'titles'=>$picked,'general'=>$gp,'reading'=>['show_on_front'=>get_option('show_on_front'),'page_on_front'=>get_option('page_on_front'),'page_for_posts'=>get_option('page_for_posts')]],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save(n,php);r=urllib.request.Request('https://gramiss.ir/'+n+'?t='+str(int(time.time())),headers={'User-Agent':'GramissBlogIndexAudit/1.0','Cache-Control':'no-cache'});data=urllib.request.urlopen(r,context=ctx,timeout=120).read().decode('utf-8','replace');print(data);print('END BLOG INDEXABILITY AUDIT')