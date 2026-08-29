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
 r=urllib.request.Request(u,headers={'User-Agent':'GramissRankMathOptionsAudit/1.0','Cache-Control':'no-cache'});
 with urllib.request.urlopen(r,context=ctx,timeout=120) as z:return z.status,z.read(),z.geturl()
f=read_theme('front-page.php');sha=hashlib.sha256(f.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-rm-options-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);global $wpdb;
$names=$wpdb->get_col("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE '%rank%math%' OR option_name LIKE '%rank-math%' ORDER BY option_name");$rows=[];foreach($names as $n){$v=get_option($n);if(in_array($n,['rank_math_registration_data','rank_math_connect_data'],true)){$rows[$n]=['type'=>gettype($v),'present'=>!empty($v)];continue;}$rows[$n]=$v;}
$helpers=[];foreach(['sitemap','titles','general'] as $g){try{$helpers[$g]=\RankMath\Helper::get_settings($g);}catch(Throwable $e){$helpers[$g]=['error'=>$e->getMessage()];}}
$sm=[];foreach((array)($helpers['sitemap']??[]) as $k=>$v){if(str_contains($k,'sitemap')||str_contains($k,'exclude')||str_contains($k,'image'))$sm[$k]=$v;}
$ti=[];foreach((array)($helpers['titles']??[]) as $k=>$v){if(str_starts_with($k,'tax_product_cat')||str_starts_with($k,'tax_pa_')||str_starts_with($k,'pt_page')||str_starts_with($k,'pt_post')||str_starts_with($k,'pt_product')||str_contains($k,'empty_tax'))$ti[$k]=$v;}
echo wp_json_encode(['option_names'=>$names,'options'=>$rows,'helper_sitemap_selected'=>$sm,'helper_titles_selected'=>$ti],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,u=get('https://gramiss.ir/'+name+'?t='+st);print('OPTIONS_AUDIT',s,u,b.decode('utf-8','replace'))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY OPTIONS AUDIT')
