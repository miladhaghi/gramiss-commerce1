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
 r=urllib.request.Request(u,headers={'User-Agent':'GramissRankMathSourceAudit/1.0','Cache-Control':'no-cache'});
 with urllib.request.urlopen(r,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
f=read_theme('front-page.php');sha=hashlib.sha256(f.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-rm-source-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function g1_snips($file,$needles){$out=[];if(!$file||!is_readable($file))return $out;$lines=file($file,FILE_IGNORE_NEW_LINES);foreach($lines as $i=>$line){foreach($needles as $n){if(stripos($line,$n)!==false){$a=max(0,$i-5);$b=min(count($lines)-1,$i+7);$chunk=[];for($j=$a;$j<=$b;$j++)$chunk[]=['line'=>$j+1,'text'=>$lines[$j]];$out[]=['needle'=>$n,'at'=>$i+1,'context'=>$chunk];break;}}}return $out;}
$rm=function_exists('rank_math')?rank_math():null;$reg=$rm?$rm->registration:null;$out=['php'=>PHP_VERSION,'wp'=>$GLOBALS['wp_version']??'','rank_math_version'=>defined('RANK_MATH_VERSION')?RANK_MATH_VERSION:'','rank_math_file'=>defined('RANK_MATH_FILE')?RANK_MATH_FILE:'','rank_math_path'=>defined('RANK_MATH_PATH')?RANK_MATH_PATH:'','active_plugins'=>get_option('active_plugins',[]),'network_plugins'=>is_multisite()?get_site_option('active_sitewide_plugins',[]):[],'registration_invalid'=>$reg?(bool)$reg->invalid:null,'rank_math_loaded'=>did_action('rank_math/loaded')];
if($reg){$rc=new ReflectionClass($reg);$rf=$rc->getFileName();$out['registration']=['class'=>$rc->getName(),'file'=>$rf,'start'=>$rc->getStartLine(),'end'=>$rc->getEndLine(),'snips'=>g1_snips($rf,['invalid','RANK_MATH_VERSION','version_compare','minimum','requirements','PHP_VERSION','WP_VERSION'])];$props=[];foreach($rc->getProperties() as $p){$n=$p->getName();try{$p->setAccessible(true);$v=$p->getValue($reg);if(is_scalar($v)||$v===null||is_array($v))$props[$n]=$v;}catch(Throwable $e){}}$out['registration_props']=$props;}
if($rm){$rc=new ReflectionClass($rm);$out['main']=['class'=>$rc->getName(),'file'=>$rc->getFileName(),'snips'=>g1_snips($rc->getFileName(),['registration','invalid','return','manager','frontend','rewrite'])];}
$plugin=defined('RANK_MATH_FILE')?RANK_MATH_FILE:'';$out['plugin_main_snips']=g1_snips($plugin,['Registration','invalid','requirements','version_compare','PHP_VERSION','ABSPATH']);
$out['options']=['rank_math_version'=>get_option('rank_math_version'),'rank_math_db_version'=>get_option('rank_math_db_version'),'rank_math_registration_data'=>get_option('rank_math_registration_data'),'rank_math_connect_data'=>get_option('rank_math_connect_data'),'rank_math_modules'=>get_option('rank_math_modules')];
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,u=get('https://gramiss.ir/'+name+'?t='+st);print('SOURCE_AUDIT_STATUS',s,u,'BYTES',len(b));data=json.loads(b.decode('utf-8','replace'));print('SOURCE_AUDIT',json.dumps(data,ensure_ascii=False,separators=(',',':')))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY RANK MATH SOURCE AUDIT')
