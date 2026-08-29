import hashlib,json,os,ssl,time,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,params,post=False):
 url=f'https://{host}:2083/execute/Fileman/{fn}';data=urllib.parse.urlencode(params).encode();req=urllib.request.Request(url if post else url+'?'+data.decode(),data=data if post else None,method='POST' if post else 'GET');req.add_header('Authorization',f'cpanel {user}:{token}');
 if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(req,context=ctx,timeout=90) as r:obj=json.loads(r.read().decode('utf-8','replace'))
 result=obj.get('result') if isinstance(obj.get('result'),dict) else obj
 if not isinstance(result,dict) or result.get('status')!=1:raise RuntimeError(str(result))
 return result.get('data')
def read(directory,name):
 d=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'});return d.get('content') if isinstance(d,dict) and isinstance(d.get('content'),str) else (d if isinstance(d,str) else d.get('file_content',''))
def save(directory,name,content):return call('save_file_content',{'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'GramissRewriteDiagnostic/1.0','Cache-Control':'no-cache'});
 with urllib.request.urlopen(req,context=ctx,timeout=120) as r:return r.status,r.read(),r.geturl()
front=read(root,'front-page.php');fsha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',fsha)
if healthy and fsha!=healthy:raise SystemExit('ABORT Home mismatch')
ht=read('public_html','.htaccess');print('HTACCESS_META',json.dumps({'bytes':len(ht.encode()),'sha256':hashlib.sha256(ht.encode()).hexdigest(),'lines':len(ht.splitlines())},separators=(',',':')))
for i,line in enumerate(ht.splitlines(),1):
 low=line.lower();safe='<REDACTED>' if any(x in low for x in ['password','secret','token','api_key','apikey']) else line
 print(f'HTL {i:03d} {safe}')
stamp=str(int(time.time()));probe='gramiss-rewrite-diagnostic-'+hashlib.sha256((stamp+fsha).encode()).hexdigest()[:16]+'.php'
php=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);require_once ABSPATH.'wp-admin/includes/misc.php';require_once ABSPATH.'wp-admin/includes/file.php';global $wp_rewrite;$path=ABSPATH.'.htaccess';$out=['server'=>$_SERVER['SERVER_SOFTWARE']??'','permalink_structure'=>(string)get_option('permalink_structure'),'using_permalinks'=>$wp_rewrite->using_permalinks(),'htaccess_exists'=>file_exists($path),'htaccess_readable'=>is_readable($path),'htaccess_writable'=>is_writable($path),'htaccess_perms'=>file_exists($path)?substr(sprintf('%o',fileperms($path)),-4):'','home_path'=>function_exists('get_home_path')?get_home_path():'','got_mod_rewrite'=>function_exists('got_mod_rewrite')?got_mod_rewrite():null,'save_mod_rewrite_rules_exists'=>function_exists('save_mod_rewrite_rules'),'flush_rules_hard_default'=>apply_filters('flush_rewrite_rules_hard',true),'product_permalink_sample'=>get_permalink(49),'shop_permalink'=>get_permalink((int)get_option('woocommerce_shop_page_id')),'rewrite_rule_count'=>count((array)get_option('rewrite_rules',[])),'wc_permalinks'=>get_option('woocommerce_permalinks')];echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save('public_html',probe,php);st,b,final=get('https://gramiss.ir/'+probe+'?t='+stamp);print('PROBE',st,final,b.decode('utf-8','replace'))
print('END READ ONLY DIAGNOSTIC; NO SETTINGS OR FILES CHANGED')