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
 r=urllib.request.Request(u,headers={'User-Agent':'GramissRankMathBootstrapAudit/1.0','Cache-Control':'no-cache'});
 with urllib.request.urlopen(r,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
f=read_theme('front-page.php');sha=hashlib.sha256(f.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-rm-bootstrap-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$rm=function_exists('rank_math')?rank_math():null;$reg=$rm?$rm->registration:null;$out=['rank_math_function'=>function_exists('rank_math'),'version'=>defined('RANK_MATH_VERSION')?RANK_MATH_VERSION:'','registration_exists'=>(bool)$reg,'registration_class'=>$reg?get_class($reg):'','registration_invalid'=>$reg?(bool)$reg->invalid:null,'manager_exists'=>$rm?isset($rm->manager):false,'frontend_exists'=>$rm?isset($rm->frontend):false,'rewrite_exists'=>$rm?isset($rm->rewrite):false,'settings_exists'=>$rm?isset($rm->settings):false,'plugin_links_filter'=>has_filter('plugin_action_links_'.plugin_basename(RANK_MATH_FILE)),'loaded_action'=>did_action('rank_math/loaded'),'plugins_loaded'=>did_action('plugins_loaded')];if($reg){$r=new ReflectionObject($reg);$props=[];foreach($r->getProperties() as $p){$n=$p->getName();if(in_array($n,['invalid','registered','is_registered','message','error','status'],true)){try{$p->setAccessible(true);$v=$p->getValue($reg);if(is_scalar($v)||$v===null)$props[$n]=$v;}catch(Throwable $e){}}}$out['registration_selected_props']=$props;}echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save(name,php);s,b,u=get('https://gramiss.ir/'+name+'?t='+st);print('BOOTSTRAP',s,u,b.decode('utf-8','replace'))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY BOOTSTRAP AUDIT')