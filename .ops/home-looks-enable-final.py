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
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'});
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u):
 r=urllib.request.Request(u,headers={'User-Agent':'GramissRankMathCacheAudit/1.0','Cache-Control':'no-cache'});
 with urllib.request.urlopen(r,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
f=read_theme('front-page.php');sha=hashlib.sha256(f.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-rm-cache-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function g1_method($class,$method){$m=new ReflectionMethod($class,$method);$f=$m->getFileName();$ls=file($f,FILE_IGNORE_NEW_LINES);$out=[];for($i=max(1,$m->getStartLine()-5);$i<=min(count($ls),$m->getEndLine()+5);$i++)$out[]=['line'=>$i,'text'=>$ls[$i-1]];return ['class'=>$class,'method'=>$method,'file'=>$f,'source'=>$out];}
$out=['classes'=>[],'hooks'=>[],'cache_option'=>get_option('rank_math_sitemap_cache_files')];foreach(['RankMath\\Sitemap\\Cache','RankMath\\Sitemap\\Sitemap','RankMath\\Sitemap\\Router'] as $c){if(class_exists($c)){$r=new ReflectionClass($c);$ms=[];foreach($r->getMethods() as $m)$ms[]=$m->getName();$out['classes'][$c]=['file'=>$r->getFileName(),'methods'=>$ms];foreach(['invalidate_storage','invalidate_cache','purge','clear_cache','flush_cache','remove_storage','clear'] as $mn){if($r->hasMethod($mn))$out['classes'][$c]['detail_'.$mn]=g1_method($c,$mn);}}}
$path=defined('RANK_MATH_PATH')?RANK_MATH_PATH:'';$hits=[];if($path){$it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path,FilesystemIterator::SKIP_DOTS));foreach($it as $fi){if(!$fi->isFile()||$fi->getExtension()!=='php')continue;$c=@file_get_contents($fi->getPathname());if($c===false)continue;if(strpos($c,'rank_math_sitemap_cache_files')!==false||strpos($c,'flush_cache')!==false||strpos($c,'invalidate_storage')!==false){$lines=preg_split('/\R/',$c);foreach($lines as $i=>$line){if(strpos($line,'rank_math_sitemap_cache_files')!==false||strpos($line,'flush_cache')!==false||strpos($line,'invalidate_storage')!==false)$hits[]=['file'=>$fi->getPathname(),'line'=>$i+1,'text'=>trim($line)];}}}}$out['source_hits']=$hits;
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,u=get('https://gramiss.ir/'+name+'?t='+st);print('CACHE_AUDIT',s,u,b.decode('utf-8','replace'))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY CACHE AUDIT')
