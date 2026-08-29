import hashlib, html, json, os, re, ssl, time, urllib.error, urllib.parse, urllib.request

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']; root=os.environ['THEME_ROOT'].strip('/'); healthy=os.environ.get('HEALTHY_HOME_SHA',''); ctx=ssl._create_unverified_context()

def call(fn,params,post=False):
    url=f'https://{host}:2083/execute/Fileman/{fn}'; data=urllib.parse.urlencode(params).encode(); last=None
    for attempt in range(1,5):
        try:
            req=urllib.request.Request(url if post else url+'?'+data.decode(),data=data if post else None,method='POST' if post else 'GET'); req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as r: obj=json.loads(r.read().decode('utf-8','replace'))
            result=obj.get('result') if isinstance(obj.get('result'),dict) else obj
            if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last=exc; print('CPANEL_RETRY',attempt,fn,str(exc)[:180]); time.sleep(attempt if attempt<4 else 0)
    raise last

def read_theme(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=root if not parent else root+'/'+parent
    d=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str): return d[k]
    if isinstance(d,str): return d
    raise RuntimeError('Cannot read '+rel)

def save_public(name,content): return call('save_file_content',{'dir':'public_html','file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def get(url,timeout=90):
    req=urllib.request.Request(url,headers={'User-Agent':'GramissSEOFrontendAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    try:
        with urllib.request.urlopen(req,context=ctx,timeout=timeout) as r:return r.status,r.read(),r.geturl(),dict(r.headers)
    except urllib.error.HTTPError as e:return e.code,e.read(),url,dict(e.headers)

def head_info(raw):
    txt=raw.decode('utf-8','replace'); m=re.search(r'<head\b[^>]*>(.*?)</head>',txt,re.I|re.S); head=m.group(1) if m else txt[:40000]
    def attr_meta(name):
        pats=[rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']*)',rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']{re.escape(name)}["\']']
        for p in pats:
            mm=re.search(p,head,re.I)
            if mm:return html.unescape(mm.group(1)).strip()
        return ''
    cm=re.search(r'<link[^>]+rel=["\'][^"\']*canonical[^"\']*["\'][^>]+href=["\']([^"\']+)',head,re.I) or re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*canonical',head,re.I)
    robots=attr_meta('robots'); desc=attr_meta('description')
    return {'canonical':html.unescape(cm.group(1)).strip() if cm else '','robots':robots,'description_len':len(desc),'og_tags':len(re.findall(r'<meta[^>]+property=["\']og:',head,re.I)),'twitter_tags':len(re.findall(r'<meta[^>]+(?:name|property)=["\']twitter:',head,re.I)),'rank_math_marker':('rank math' in head.lower()),'wp_head_bytes':len(head)}

front=read_theme('front-page.php'); fsha=hashlib.sha256(front.encode()).hexdigest(); print('LIVE_HOME_SHA',fsha)
if healthy and fsha!=healthy: raise SystemExit('ABORT Home mismatch')
header=read_theme('header.php'); funcs=read_theme('functions.php')
print('THEME_HEAD_CHECK',json.dumps({'header_has_wp_head':bool(re.search(r'wp_head\s*\(',header)),'header_wp_head_count':len(re.findall(r'wp_head\s*\(',header)),'functions_mentions_rank_math':bool(re.search(r'rank[_ -]?math',funcs,re.I)),'functions_removes_wp_head':bool(re.search(r'remove_(?:action|all_actions)\s*\(\s*["\']wp_head',funcs,re.I)),'functions_disables_sitemaps':bool(re.search(r'wp_sitemaps|sitemap',funcs,re.I))},separators=(',',':')))

stamp=str(int(time.time())); probe='gramiss-rankmath-diag-'+hashlib.sha256((stamp+fsha).encode()).hexdigest()[:16]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
global $wp_filter;
function g1_callbacks($hook){global $wp_filter;$out=[];if(empty($wp_filter[$hook]))return $out;foreach($wp_filter[$hook]->callbacks as $pri=>$rows){foreach($rows as $r){$f=$r['function'];if(is_string($f))$n=$f;elseif(is_array($f)){$a=$f[0];$n=(is_object($a)?get_class($a):(string)$a).'::'.$f[1];}elseif($f instanceof Closure)$n='Closure';else $n=gettype($f);if(stripos($n,'rank')!==false||stripos($n,'seo')!==false)$out[]=['priority'=>(int)$pri,'callback'=>$n];}}return $out;}
$rules=(array)get_option('rewrite_rules',[]);$s=[];foreach($rules as $k=>$v){if(stripos($k,'sitemap')!==false||stripos($v,'sitemap')!==false)$s[$k]=$v;}
$out=['rank_math_loaded'=>defined('RANK_MATH_VERSION'),'rank_math_version'=>defined('RANK_MATH_VERSION')?RANK_MATH_VERSION:'','modules'=>get_option('rank_math_modules'),'sitemap_rewrite_rules'=>$s,'sitemap_rule_count'=>count($s),'wp_head_rank_callbacks'=>g1_callbacks('wp_head'),'template_redirect_rank_callbacks'=>g1_callbacks('template_redirect'),'init_rank_callbacks'=>g1_callbacks('init'),'core_sitemap_enabled'=>function_exists('wp_sitemaps_get_server'),'core_sitemap_provider_posts'=>null];
if(function_exists('wp_sitemaps_get_server')){$server=wp_sitemaps_get_server();$out['core_sitemap_provider_posts']=(bool)$server->registry->get_provider('posts');}
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save_public(probe,php); st,b,final,_=get('https://gramiss.ir/'+probe+'?t='+stamp,120); print('PROBE_STATUS',st,final,len(b)); print('RANK_RUNTIME',b.decode('utf-8','replace')[:12000])

checks=[('home','https://gramiss.ir/'),('product','https://gramiss.ir/product/'+urllib.parse.quote('تیشرت-باکس-طرح-مسیح',safe='-')+'/'),('category','https://gramiss.ir/product-category/tshirt/'),('search','https://gramiss.ir/?'+urllib.parse.urlencode({'s':'تیشرت'})),('cart','https://gramiss.ir/cart/'),('account','https://gramiss.ir/my-account/')]
for label,url in checks:
    s,raw,f,h=get(url,90); print('HEAD_CHECK',label,json.dumps({'requested':url,'status':s,'final':f,**head_info(raw)},ensure_ascii=False,separators=(',',':')))
for path in ['sitemap_index.xml','wp-sitemap.xml','robots.txt']:
    s,raw,f,h=get('https://gramiss.ir/'+path,90); print('ENDPOINT_CHECK',path,s,f,len(raw),raw[:180].decode('utf-8','replace').replace('\n',' '))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=fsha: raise SystemExit('ABORT Home changed')
print('END READ-ONLY RANK MATH / INDEXATION DIAGNOSTIC')
