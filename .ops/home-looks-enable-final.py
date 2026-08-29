import hashlib, json, os, re, ssl, time, urllib.parse, urllib.request

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
    req=urllib.request.Request(url,headers={'User-Agent':'GramissSEOMigration/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    opener=urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx)) if follow else urllib.request.build_opener(NoRedirect(),urllib.request.HTTPSHandler(context=ctx))
    try:
        with opener.open(req,timeout=timeout) as r: return r.status,r.read(),r.geturl(),dict(r.headers)
    except urllib.error.HTTPError as e: return e.code,e.read(),url,dict(e.headers)

front=read_theme('front-page.php'); front_sha=hashlib.sha256(front.encode()).hexdigest(); print('LIVE_HOME_SHA',front_sha)
if healthy and front_sha!=healthy: raise SystemExit('ABORT: Home baseline mismatch; no changes')
ht_before=read_file('public_html','.htaccess'); ht_sha=hashlib.sha256(ht_before.encode()).hexdigest();
save_file('public_html','.htaccess.bak-seo-url-v1-'+stamp,ht_before); print('BACKUP_HTACCESS',len(ht_before),ht_sha)

nonce=hashlib.sha256((stamp+front_sha).encode()).hexdigest()[:18]; probe=f'gramiss-seo-migrate-{nonce}.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false); require __DIR__.'/wp-load.php'; @unlink(__FILE__);
if (!function_exists('wc_get_product')) { http_response_code(500); echo json_encode(['error'=>'WooCommerce unavailable']); exit; }
$old_structure=(string)get_option('permalink_structure');
$wc_permalinks=(array)get_option('woocommerce_permalinks',[]);
if ($old_structure!=='') { http_response_code(409); echo wp_json_encode(['error'=>'permalink_structure changed from audited baseline','current'=>$old_structure]); exit; }
$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);
$pmap=[];foreach($ids as $id){$slug=(string)get_post_field('post_name',$id);if($slug!=='')$pmap[$slug]=(int)$id;}
$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>true]);$cmap=[];if(!is_wp_error($terms)){foreach($terms as $t)$cmap[$t->slug]=(int)$t->term_id;}
wp_mkdir_p(WP_CONTENT_DIR.'/mu-plugins');
$plugin=WP_CONTENT_DIR.'/mu-plugins/gramiss-seo-query-redirects.php';$plugin_backup='';
if(file_exists($plugin)){$plugin_backup=$plugin.'.bak-'''.gmdate('Ymd-His').''' ';$plugin_backup=trim($plugin_backup);@copy($plugin,$plugin_backup);}
$p_export=var_export($pmap,true);$c_export=var_export($cmap,true);
$code="<?php\n/** Plugin Name: Gramiss Legacy SEO Query Redirects */\nif (!defined('ABSPATH')) exit;\nadd_action('template_redirect', function(){\n  if (is_admin()) return;\n  \$pmap={$p_export};\n  \$cmap={$c_export};\n  if (count(\$_GET)===1 && isset(\$_GET['product'])) {\n    \$slug=sanitize_title(wp_unslash(\$_GET['product']));\n    if(isset(\$pmap[\$slug])){\$target=get_permalink((int)\$pmap[\$slug]);if(\$target){wp_safe_redirect(\$target,301,'Gramiss SEO Migration');exit;}}\n  }\n  if (count(\$_GET)===1 && isset(\$_GET['product_cat'])) {\n    \$slug=sanitize_title(wp_unslash(\$_GET['product_cat']));\n    if(isset(\$cmap[\$slug])){\$target=get_term_link((int)\$cmap[\$slug],'product_cat');if(!is_wp_error(\$target)){wp_safe_redirect(\$target,301,'Gramiss SEO Migration');exit;}}\n  }\n},0);\n";
if(file_put_contents($plugin,$code)===false){http_response_code(500);echo wp_json_encode(['error'=>'redirect plugin write failed']);exit;}
$manifest=['created_at'=>gmdate('c'),'old_permalink_structure'=>$old_structure,'woocommerce_permalinks'=>$wc_permalinks,'product_map'=>$pmap,'category_map'=>$cmap,'redirect_plugin'=>$plugin,'redirect_plugin_backup'=>$plugin_backup];
$manifest_path=WP_CONTENT_DIR.'/gramiss-seo-url-migration-v1-'.gmdate('Ymd-His').'.json';file_put_contents($manifest_path,wp_json_encode($manifest,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT));
update_option('permalink_structure','/%postname%/');global $wp_rewrite;$wp_rewrite->set_permalink_structure('/%postname%/');flush_rewrite_rules(true);
$samples=[];foreach(array_slice($ids,0,3) as $id)$samples[]=['type'=>'product','id'=>(int)$id,'url'=>get_permalink($id)];
foreach([97,222,296,392,403] as $id){if(get_post_status($id)==='publish')$samples[]=['type'=>'product','id'=>$id,'url'=>get_permalink($id)];}
foreach(['tshirt','pants','shirt','sneakers','hat'] as $slug){$t=get_term_by('slug',$slug,'product_cat');if($t)$samples[]=['type'=>'category','id'=>(int)$t->term_id,'slug'=>$slug,'url'=>get_term_link($t)];}
$pages=[];foreach(['shop'=>'woocommerce_shop_page_id','cart'=>'woocommerce_cart_page_id','checkout'=>'woocommerce_checkout_page_id','account'=>'woocommerce_myaccount_page_id'] as $k=>$opt){$id=(int)get_option($opt);$pages[$k]=['id'=>$id,'url'=>$id?get_permalink($id):''];}
echo wp_json_encode(['ok'=>true,'old_structure'=>$old_structure,'new_structure'=>(string)get_option('permalink_structure'),'products'=>count($pmap),'categories'=>count($cmap),'manifest'=>$manifest_path,'plugin'=>$plugin,'plugin_backup'=>$plugin_backup,'samples'=>$samples,'pages'=>$pages],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save_file('public_html',probe,php)
status,body,_,_=get('https://gramiss.ir/'+probe+'?t='+str(int(time.time())),True,180); print('MIGRATE_STATUS',status,'BYTES',len(body))
if status!=200: print(body.decode('utf-8','replace')[:1200]); raise SystemExit('ABORT: migration bootstrap failed')
data=json.loads(body.decode('utf-8','replace')); print('MIGRATION',json.dumps(data,ensure_ascii=False,separators=(',',':')))

# Verify generated rewrite rules and route behavior.
ht_after=read_file('public_html','.htaccess'); print('HTACCESS_AFTER',len(ht_after),hashlib.sha256(ht_after.encode()).hexdigest(),'RewriteEngine On' in ht_after)
errors=[]
if data.get('new_structure')!='/%postname%/': errors.append('permalink option mismatch')
if 'RewriteEngine On' not in ht_after or 'index.php' not in ht_after: errors.append('WordPress rewrite rules missing from .htaccess')

# Representative pretty routes must resolve publicly.
for s in data.get('samples',[]):
    url=s.get('url','');
    if not url: errors.append('empty sample URL '+str(s)); continue
    st,b,final,_=get(url+'?g1v='+str(int(time.time())) if '?' not in url else url+'&g1v=1',True,90)
    print('PRETTY_TEST',s.get('type'),s.get('id'),st,final,len(b))
    if st!=200: errors.append(f"pretty route failed {s.get('type')} {s.get('id')} status={st}")

# Exact legacy query redirects: verify several products/categories.
legacy_checks=[('product',49),('product',97),('product',392),('product',403)]
for typ,idv in legacy_checks:
    if typ=='product':
        slug=None
        for row in data.get('samples',[]):
            if row.get('type')=='product' and row.get('id')==idv:
                target=row.get('url'); break
        else:
            target=''
        # Read slug via target-independent WP query using audited IDs from public baseline.
        slug_map={49:'کلاه-فیت-کپ-آبی',97:'تیشرت-باکسی-سنگشور',392:'تیشرت-باکس-طرح-مسیح',403:'کتونی-طرح-ونس-سرمه-ای'}
        old='https://gramiss.ir/?product='+urllib.parse.quote(slug_map[idv],safe='-')
        st,_,_,hdr=get(old,False,60); loc=hdr.get('Location',''); print('LEGACY_REDIRECT',idv,st,loc)
        if st!=301 or '/product/' not in loc: errors.append(f'legacy product redirect failed {idv}: {st} {loc}')

# System pages must not 404 after permalink activation. Checkout may redirect when cart is empty.
for k,row in data.get('pages',{}).items():
    url=row.get('url','');
    if not url: continue
    st,b,final,_=get(url,True,90); print('SYSTEM_PAGE',k,st,final,len(b))
    if st==404: errors.append('system page 404 '+k)

# Home invariant and SEO endpoints (SEO endpoints are diagnostic, not rollback blockers).
front_after=read_theme('front-page.php');
if hashlib.sha256(front_after.encode()).hexdigest()!=front_sha: errors.append('Home changed unexpectedly')
for path in ['robots.txt','sitemap_index.xml','wp-sitemap.xml']:
    st,b,final,_=get('https://gramiss.ir/'+path+'?g1='+str(int(time.time())),True,60); print('SEO_ENDPOINT',path,st,final,len(b))

if errors:
    print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False))
    # Application rollback first.
    rb=f'gramiss-seo-rollback-{nonce}.php'
    rbphp=r'''<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);update_option('permalink_structure','');global $wp_rewrite;$wp_rewrite->set_permalink_structure('');flush_rewrite_rules(true);$p=WP_CONTENT_DIR.'/mu-plugins/gramiss-seo-query-redirects.php';@unlink($p);echo 'ROLLED_BACK';'''
    save_file('public_html',rb,rbphp)
    rst,rbody,_,_=get('https://gramiss.ir/'+rb+'?t='+str(int(time.time())),True,120); print('ROLLBACK_APP',rst,rbody[:100])
    save_file('public_html','.htaccess',ht_before); print('ROLLBACK_HTACCESS_RESTORED',hashlib.sha256(read_file('public_html','.htaccess').encode()).hexdigest()==ht_sha)
    raise SystemExit('ROLLED BACK: '+ '; '.join(errors))

print('PASS SEO URL MIGRATION V1')
print('NO PRODUCT NAMES/SLUGS/PRICES/STOCK/ATTRIBUTES/CATEGORIES/CONTENT CHANGED')
