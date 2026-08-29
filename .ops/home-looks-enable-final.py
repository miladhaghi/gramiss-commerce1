import hashlib, json, os, re, ssl, time, urllib.error, urllib.parse, urllib.request

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']
root=os.environ['THEME_ROOT'].strip('/'); healthy=os.environ.get('HEALTHY_HOME_SHA','')
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime())

def call(fn,params,post=False):
    url=f'https://{host}:2083/execute/Fileman/{fn}'; data=urllib.parse.urlencode(params).encode(); last=None
    for attempt in range(1,5):
        try:
            req=urllib.request.Request(url if post else url+'?'+data.decode(),data=data if post else None,method='POST' if post else 'GET')
            req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as r: obj=json.loads(r.read().decode('utf-8','replace'))
            result=obj.get('result') if isinstance(obj.get('result'),dict) else obj
            if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last=exc; print(f'Attempt {attempt}/4 {fn}: {exc}')
            if attempt<4: time.sleep(attempt*2)
    raise last

def read_file(directory,name):
    data=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for key in ('content','file_content','data'):
            if isinstance(data.get(key),str): return data[key]
    if isinstance(data,str): return data
    raise RuntimeError('Cannot read '+directory+'/'+name)

def save_file(directory,name,content):
    return call('save_file_content',{'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def read_theme(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=root if not parent else root+'/'+parent
    return read_file(directory,name)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None

def get(url,follow=True,timeout=90):
    req=urllib.request.Request(url,headers={'User-Agent':'GramissSEOMigration/1.2','Cache-Control':'no-cache','Pragma':'no-cache'})
    handlers=[urllib.request.HTTPSHandler(context=ctx)]
    if not follow: handlers.insert(0,NoRedirect())
    opener=urllib.request.build_opener(*handlers)
    try:
        with opener.open(req,timeout=timeout) as r: return r.status,r.read(),r.geturl(),dict(r.headers)
    except urllib.error.HTTPError as e: return e.code,e.read(),url,dict(e.headers)

def header_value(headers,name):
    name=name.lower()
    for k,v in headers.items():
        if k.lower()==name: return v
    return ''

front=read_theme('front-page.php'); front_sha=hashlib.sha256(front.encode()).hexdigest(); print('LIVE_HOME_SHA',front_sha)
if healthy and front_sha!=healthy: raise SystemExit('ABORT: Home baseline mismatch; no changes')
ht_before=read_file('public_html','.htaccess'); ht_sha=hashlib.sha256(ht_before.encode()).hexdigest()
save_file('public_html','.htaccess.bak-seo-url-v1-'+stamp,ht_before); print('BACKUP_HTACCESS',len(ht_before),ht_sha)
redirect_dir='public_html/wp-content/mu-plugins'; redirect_name='gramiss-seo-query-redirects.php'; old_redirect_plugin=None
try: old_redirect_plugin=read_file(redirect_dir,redirect_name)
except Exception: pass
nonce=hashlib.sha256((stamp+front_sha).encode()).hexdigest()[:18]

# Phase 1: snapshot the exact legacy slugs, install a permanent query->ID redirect map, and flip only the permalink option.
phase1=f'gramiss-seo-phase1-{nonce}.php'
php1=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
if(!function_exists('wc_get_product')){http_response_code(500);echo wp_json_encode(['error'=>'WooCommerce unavailable']);exit;}
$old=(string)get_option('permalink_structure');if($old!==''){http_response_code(409);echo wp_json_encode(['error'=>'audited permalink baseline changed','current'=>$old]);exit;}
$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);$pmap=[];foreach($ids as $id){$s=(string)get_post_field('post_name',$id);if($s!=='')$pmap[$s]=(int)$id;}
$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>true]);$cmap=[];if(!is_wp_error($terms)){foreach($terms as $t)$cmap[$t->slug]=(int)$t->term_id;}
wp_mkdir_p(WP_CONTENT_DIR.'/mu-plugins');$plugin=WP_CONTENT_DIR.'/mu-plugins/gramiss-seo-query-redirects.php';$backup='';if(file_exists($plugin)){$backup=$plugin.'.bak-'.gmdate('Ymd-His');@copy($plugin,$backup);}
$pe=var_export($pmap,true);$ce=var_export($cmap,true);
$code="<?php\n/** Plugin Name: Gramiss Legacy SEO Query Redirects */\nif(!defined('ABSPATH'))exit;\nadd_action('template_redirect',function(){\n if(is_admin())return;\n \$pmap={$pe};\n \$cmap={$ce};\n if(count(\$_GET)===1&&isset(\$_GET['product'])){\$s=sanitize_title(wp_unslash(\$_GET['product']));if(isset(\$pmap[\$s])){\$u=get_permalink((int)\$pmap[\$s]);if(\$u){wp_safe_redirect(\$u,301,'Gramiss SEO Migration');exit;}}}\n if(count(\$_GET)===1&&isset(\$_GET['product_cat'])){\$s=sanitize_title(wp_unslash(\$_GET['product_cat']));if(isset(\$cmap[\$s])){\$u=get_term_link((int)\$cmap[\$s],'product_cat');if(!is_wp_error(\$u)){wp_safe_redirect(\$u,301,'Gramiss SEO Migration');exit;}}}\n},0);\n";
if(file_put_contents($plugin,$code)===false){http_response_code(500);echo wp_json_encode(['error'=>'redirect plugin write failed']);exit;}
$manifest=['created_at'=>gmdate('c'),'old_permalink_structure'=>$old,'old_rewrite_rules'=>get_option('rewrite_rules'),'woocommerce_permalinks'=>get_option('woocommerce_permalinks'),'product_map'=>$pmap,'category_map'=>$cmap,'redirect_plugin_backup'=>$backup];
$mp=WP_CONTENT_DIR.'/gramiss-seo-url-migration-v1-'.gmdate('Ymd-His').'.json';file_put_contents($mp,wp_json_encode($manifest,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT));
update_option('permalink_structure','/%postname%/');delete_option('rewrite_rules');
echo wp_json_encode(['ok'=>true,'new_structure'=>(string)get_option('permalink_structure'),'products'=>count($pmap),'categories'=>count($cmap),'manifest'=>$mp,'plugin_backup'=>$backup],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save_file('public_html',phase1,php1); st,b,_,_=get('https://gramiss.ir/'+phase1+'?t='+str(int(time.time())),True,180); print('PHASE1',st,b.decode('utf-8','replace')[:1800])
if st!=200: raise SystemExit('ABORT: phase1 failed')
p1=json.loads(b.decode('utf-8','replace'))

# WordPress marker was empty at baseline. Install only the standard root front-controller block; preserve LiteSpeed and everything outside the marker byte-for-byte.
wp_block='''# BEGIN WordPress\n<IfModule mod_rewrite.c>\nRewriteEngine On\nRewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]\nRewriteBase /\nRewriteRule ^index\\.php$ - [L]\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule . /index.php [L]\n</IfModule>\n# END WordPress'''
pattern=re.compile(r'# BEGIN WordPress.*?# END WordPress',re.S)
if not pattern.search(ht_before):
    save_file('public_html','.htaccess',ht_before); raise SystemExit('ABORT: WordPress htaccess marker missing')
ht_patched=pattern.sub(wp_block,ht_before,count=1); save_file('public_html','.htaccess',ht_patched)
if read_file('public_html','.htaccess')!=ht_patched:
    save_file('public_html','.htaccess',ht_before); raise SystemExit('ABORT: htaccess exact write mismatch')
print('HTACCESS_PATCHED',len(ht_patched),hashlib.sha256(ht_patched.encode()).hexdigest())

# Phase 2: new WordPress bootstrap sees pretty permalinks from startup, so WooCommerce registers product/taxonomy rewrites correctly.
phase2=f'gramiss-seo-phase2-{nonce}.php'
php2=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
if((string)get_option('permalink_structure')!=='/%postname%/'){http_response_code(409);echo wp_json_encode(['error'=>'phase2 permalink option missing']);exit;}
global $wp_rewrite;$wp_rewrite->flush_rules(false);if(function_exists('do_action'))do_action('litespeed_purge_all');
$ids=[49,62,68,97,222,296,392,403];$samples=[];foreach($ids as $id){if(get_post_status($id)==='publish')$samples[]=['type'=>'product','id'=>$id,'url'=>get_permalink($id)];}
foreach(['tshirt','pants','shirt','sneakers','hat','graphic-tshirt','long-sleeve-shirt'] as $slug){$t=get_term_by('slug',$slug,'product_cat');if($t)$samples[]=['type'=>'category','id'=>(int)$t->term_id,'slug'=>$slug,'url'=>get_term_link($t)];}
$pages=[];foreach(['shop'=>'woocommerce_shop_page_id','cart'=>'woocommerce_cart_page_id','checkout'=>'woocommerce_checkout_page_id','account'=>'woocommerce_myaccount_page_id'] as $k=>$opt){$id=(int)get_option($opt);$pages[$k]=['id'=>$id,'url'=>$id?get_permalink($id):''];}
echo wp_json_encode(['ok'=>true,'structure'=>(string)get_option('permalink_structure'),'rewrite_rule_count'=>count((array)get_option('rewrite_rules',[])),'samples'=>$samples,'pages'=>$pages],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save_file('public_html',phase2,php2); st,b,_,_=get('https://gramiss.ir/'+phase2+'?t='+str(int(time.time())),True,180); print('PHASE2',st,b.decode('utf-8','replace')[:5000])
if st!=200: phase2_data={}; errors=['phase2 failed']
else: phase2_data=json.loads(b.decode('utf-8','replace')); errors=[]

ht_after=read_file('public_html','.htaccess')
if not re.search(r'RewriteEngine\s+On',ht_after,re.I) or 'RewriteRule . /index.php [L]' not in ht_after: errors.append('front controller rewrite block missing')
if phase2_data.get('structure')!='/%postname%/': errors.append('permalink option mismatch')
if phase2_data.get('rewrite_rule_count',0)<10: errors.append('rewrite rule set unexpectedly small')
for s in phase2_data.get('samples',[]):
    url=s.get('url',''); print('FRESH_URL',s.get('type'),s.get('id'),url)
    if '?' in url or not url.startswith('https://gramiss.ir/'): errors.append('non-pretty generated URL '+str(s))
    st2,body2,final2,_=get(url,True,90); print('PRETTY_TEST',s.get('type'),s.get('id'),st2,final2,len(body2))
    if st2!=200: errors.append(f"pretty route failed {s.get('type')} {s.get('id')} status={st2}")

slug_map={49:'کلاه-فیت-کپ-آبی',97:'تیشرت-باکسی-سنگشور',392:'تیشرت-باکس-طرح-مسیح',403:'کتونی-طرح-ونس-سرمه-ای'}
for idv,slug in slug_map.items():
    old='https://gramiss.ir/?product='+urllib.parse.quote(slug,safe='-'); st2,_,_,hdr=get(old,False,60); loc=header_value(hdr,'location'); print('LEGACY_PRODUCT',idv,st2,loc)
    if st2!=301 or '/product/' not in loc: errors.append(f'legacy product redirect failed {idv}: {st2} {loc}')
for slug in ['tshirt','pants','shirt','sneakers','hat','graphic-tshirt']:
    old='https://gramiss.ir/?product_cat='+urllib.parse.quote(slug,safe='-'); st2,_,_,hdr=get(old,False,60); loc=header_value(hdr,'location'); print('LEGACY_CATEGORY',slug,st2,loc)
    if st2!=301 or '/product-category/' not in loc: errors.append(f'legacy category redirect failed {slug}: {st2} {loc}')

for k,row in phase2_data.get('pages',{}).items():
    url=row.get('url',''); st2,body2,final2,_=get(url,True,90); print('SYSTEM_PAGE',k,st2,final2,len(body2))
    if st2==404: errors.append('system page 404 '+k)

if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=front_sha: errors.append('Home changed unexpectedly')
for path in ['robots.txt','sitemap_index.xml','wp-sitemap.xml']:
    st2,body2,final2,_=get('https://gramiss.ir/'+path,True,60); print('SEO_ENDPOINT',path,st2,final2,len(body2))

if errors:
    print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False))
    rb=f'gramiss-seo-rollback-{nonce}.php'
    rbphp=r'''<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);update_option('permalink_structure','');delete_option('rewrite_rules');$p=WP_CONTENT_DIR.'/mu-plugins/gramiss-seo-query-redirects.php';@unlink($p);if(function_exists('do_action'))do_action('litespeed_purge_all');echo 'ROLLED_BACK';'''
    save_file('public_html',rb,rbphp); rst,rbody,_,_=get('https://gramiss.ir/'+rb+'?t='+str(int(time.time())),True,120); print('ROLLBACK_APP',rst,rbody[:120])
    if old_redirect_plugin is not None: save_file(redirect_dir,redirect_name,old_redirect_plugin)
    save_file('public_html','.htaccess',ht_before); print('ROLLBACK_HTACCESS',hashlib.sha256(read_file('public_html','.htaccess').encode()).hexdigest()==ht_sha)
    raise SystemExit('ROLLED BACK: '+'; '.join(errors))

print('PASS SEO URL MIGRATION V1 TWO-PHASE')
print('PUBLISHED_PRODUCTS',p1.get('products'),'ACTIVE_CATEGORIES',p1.get('categories'),'REWRITE_RULES',phase2_data.get('rewrite_rule_count'))
print('NO PRODUCT NAMES/SLUGS/PRICES/STOCK/ATTRIBUTES/CATEGORIES/CONTENT CHANGED')
