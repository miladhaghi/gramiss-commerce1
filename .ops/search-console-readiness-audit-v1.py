import json, os, re, ssl, time, urllib.parse, urllib.request, urllib.error

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']
CTX=ssl._create_unverified_context(); BASE='https://gramiss.ir'

def api(fn, params, post=False):
    url=f'https://{HOST}:2083/execute/Fileman/{fn}'
    data=urllib.parse.urlencode(params).encode()
    req=urllib.request.Request(url if post else url+'?'+data.decode(), data=data if post else None, method='POST' if post else 'GET')
    req.add_header('Authorization', f'cpanel {USER}:{TOKEN}')
    if post: req.add_header('Content-Type','application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, context=CTX, timeout=90) as r: obj=json.loads(r.read().decode('utf-8','replace'))
    q=obj.get('result') if isinstance(obj.get('result'),dict) else obj
    if not isinstance(q,dict) or q.get('status')!=1: raise RuntimeError(str(q))
    return q.get('data')

def save(name, content):
    return api('save_file_content', {'dir':'public_html','file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'}, True)

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'GramissMeasurementReadiness/1.0','Cache-Control':'no-cache'})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=120) as r: return r.status, r.read().decode('utf-8','replace')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8','replace')

nonce=str(int(time.time()))
name='gramiss-measurement-readiness-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__.'/wp-load.php';
@unlink(__FILE__);
global $wpdb;
function safe_key_paths($value,$prefix=''){
  $out=[];
  if(!is_array($value)) return $out;
  foreach($value as $k=>$v){
    $p=$prefix===''?(string)$k:$prefix.'.'.$k;
    if(preg_match('/analytics|search.?console|google|verification|property|site.?url/i',(string)$k)) $out[]=$p;
    if(is_array($v)) $out=array_merge($out,safe_key_paths($v,$p));
  }
  return array_values(array_unique($out));
}
$o=[];
$o['wp_version']=get_bloginfo('version');
$o['site_url']=site_url();
$o['home_url']=home_url();
$o['active_rank_math_plugins']=array_values(array_filter((array)get_option('active_plugins',[]),fn($x)=>stripos($x,'seo-by-rank-math')!==false||stripos($x,'rank-math')!==false));
$o['rank_math_modules']=get_option('rank_math_modules',[]);
$general=get_option('rank-math-options-general',[]);
$titles=get_option('rank-math-options-titles',[]);
$o['rank_math_general_relevant_key_paths']=safe_key_paths($general);
$o['rank_math_titles_relevant_key_paths']=safe_key_paths($titles);
$option_names=$wpdb->get_col("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE 'rank_math%' OR option_name LIKE 'rank-math%' ORDER BY option_name");
$o['rank_math_option_names']=array_values(array_filter($option_names,fn($n)=>preg_match('/analytics|google|console|verification|api/i',$n)));
$o['sensitive_option_presence']=[];
foreach(['rank_math_google_api_code','rank_math_google_oauth_tokens','rank_math_analytics_settings','rank_math_analytics_all_services'] as $n){$v=get_option($n,null);$o['sensitive_option_presence'][$n]=($v!==null && $v!==false && $v!=='' && $v!==[]);}
$tables=$wpdb->get_col("SHOW TABLES LIKE '{$wpdb->prefix}rank_math%'");
$o['rank_math_tables']=[];
foreach($tables as $table){
  if(!preg_match('/analytics|gsc|search/i',$table)) continue;
  $safe=preg_replace('/[^A-Za-z0-9_]/','',$table);
  $cols=$wpdb->get_results("SHOW COLUMNS FROM `$safe`",ARRAY_A);
  $names=array_values(array_map(fn($r)=>$r['Field'],$cols));
  $row_count=(int)$wpdb->get_var("SELECT COUNT(*) FROM `$safe`");
  $date_info=[];
  foreach($names as $c){
    if(preg_match('/date|created|updated|time/i',$c)){
      $sc=preg_replace('/[^A-Za-z0-9_]/','',$c);
      $min=$wpdb->get_var("SELECT MIN(`$sc`) FROM `$safe`");
      $max=$wpdb->get_var("SELECT MAX(`$sc`) FROM `$safe`");
      if($min!==null||$max!==null) $date_info[$c]=['min'=>$min,'max'=>$max];
    }
  }
  $o['rank_math_tables'][]=['table'=>$table,'rows'=>$row_count,'columns'=>$names,'date_ranges'=>$date_info];
}
$cron=_get_cron_array();$hooks=[];
foreach((array)$cron as $ts=>$entries){foreach((array)$entries as $hook=>$details){if(preg_match('/rank.?math|analytics|search.?console|google/i',$hook))$hooks[$hook]=true;}}
$o['relevant_cron_hooks']=array_keys($hooks);
$o['analytics_rows_total']=array_sum(array_map(fn($x)=>(int)$x['rows'],$o['rank_math_tables']));
echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save(name,php)
status,body=get(BASE+'/'+name+'?t='+nonce)
if status!=200: raise SystemExit('FAIL probe HTTP '+str(status))
data=json.loads(body)
status_home,home=get(BASE+'/?measurement-readiness='+nonce)
verification=bool(re.search(r'<meta[^>]+name=["\']google-site-verification["\']',home,re.I))
print('MEASUREMENT_READINESS',json.dumps({
 'probe_http':status,
 'home_http':status_home,
 'rank_math_plugins':data.get('active_rank_math_plugins',[]),
 'rank_math_modules':data.get('rank_math_modules',[]),
 'relevant_config_key_paths':data.get('rank_math_general_relevant_key_paths',[]),
 'relevant_option_names':data.get('rank_math_option_names',[]),
 'sensitive_option_presence':data.get('sensitive_option_presence',{}),
 'analytics_tables':data.get('rank_math_tables',[]),
 'analytics_rows_total':data.get('analytics_rows_total',0),
 'relevant_cron_hooks':data.get('relevant_cron_hooks',[]),
 'google_site_verification_meta_present':verification
},ensure_ascii=False,sort_keys=True))
rows=int(data.get('analytics_rows_total',0) or 0)
if rows>0:
    print('MEASUREMENT_PATH RANK_MATH_IMPORTED_DATA_PRESENT')
else:
    print('MEASUREMENT_PATH NO_IMPORTED_SEARCH_CONSOLE_DATA_DETECTED')
print('PASS SEARCH CONSOLE READINESS AUDIT V1')
