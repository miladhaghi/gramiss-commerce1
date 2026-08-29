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
 r=urllib.request.Request(u,headers={'User-Agent':'GramissRankMathHelperAudit/1.0','Cache-Control':'no-cache'});
 with urllib.request.urlopen(r,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
f=read_theme('front-page.php');sha=hashlib.sha256(f.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-rm-helper-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function g1_method($class,$method){$m=new ReflectionMethod($class,$method);$f=$m->getFileName();$s=$m->getStartLine();$e=$m->getEndLine();$lines=file($f,FILE_IGNORE_NEW_LINES);$chunk=[];for($i=max(1,$s-5);$i<=min(count($lines),$e+5);$i++)$chunk[]=['line'=>$i,'text'=>$lines[$i-1]];return ['class'=>$class,'method'=>$method,'file'=>$f,'start'=>$s,'end'=>$e,'source'=>$chunk];}
$out=['invalid'=>\RankMath\Helper::is_invalid_registration(),'methods'=>[],'options'=>['registration_data'=>get_option('rank_math_registration_data'),'connect_data'=>get_option('rank_math_connect_data'),'wizard_completed'=>get_option('rank_math_wizard_completed'),'installation_date'=>get_option('rank_math_installation_date'),'version'=>get_option('rank_math_version')]];
foreach([['RankMath\\Helper','is_invalid_registration'],['RankMath\\Helper','is_connected'],['RankMath\\Helper','get_registration_data']] as $x){try{$out['methods'][]=g1_method($x[0],$x[1]);}catch(Throwable $e){$out['methods'][]=['class'=>$x[0],'method'=>$x[1],'error'=>$e->getMessage()];}}
$rf=new ReflectionClass('RankMath\\Helper');$file=$rf->getFileName();$lines=file($file,FILE_IGNORE_NEW_LINES);$hits=[];foreach($lines as $i=>$line){if(stripos($line,'registration')!==false||stripos($line,'connect_data')!==false||stripos($line,'is_connected')!==false){$hits[]=['line'=>$i+1,'text'=>$line];}}$out['helper_file']=$file;$out['registration_hits']=$hits;
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,u=get('https://gramiss.ir/'+name+'?t='+st);print('HELPER_AUDIT_STATUS',s,u,'BYTES',len(b));print('HELPER_AUDIT',b.decode('utf-8','replace'))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY HELPER AUDIT')
