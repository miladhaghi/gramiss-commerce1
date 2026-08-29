import hashlib, json, os, ssl, time, urllib.parse, urllib.request

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

def read_theme(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=root if not parent else root+'/'+parent
    return read_file(directory,name)

def public_get(url,timeout=150):
    req=urllib.request.Request(url,headers={'User-Agent':'GramissSEOURLDryRun/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req,context=ctx,timeout=timeout) as r: return r.status,r.read(),r.geturl(),dict(r.headers)

front=read_theme('front-page.php'); front_sha=hashlib.sha256(front.encode()).hexdigest(); print('LIVE_HOME_SHA',front_sha)
if healthy and front_sha!=healthy: raise SystemExit('ABORT: Home baseline mismatch; no production mutations performed')
try:
    ht=read_file('public_html','.htaccess')
    print('HTACCESS',json.dumps({'exists':True,'bytes':len(ht.encode()),'sha256':hashlib.sha256(ht.encode()).hexdigest(),'has_wp_block':'# BEGIN WordPress' in ht,'has_rewrite_engine':'RewriteEngine On' in ht},separators=(',',':')))
except Exception as exc:
    print('HTACCESS',json.dumps({'exists':False,'error':str(exc)[:180]},separators=(',',':')))

nonce=hashlib.sha256((stamp+front_sha).encode()).hexdigest()[:18]; probe=f'gramiss-seo-url-plan-{nonce}.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false); require __DIR__ . '/wp-load.php'; @unlink(__FILE__);
if (!function_exists('wc_get_product')) { http_response_code(500); echo json_encode(['error'=>'WooCommerce unavailable']); exit; }
function g1_clean($u){return esc_url_raw($u);}
function g1_pretty_product($slug){return user_trailingslashit(home_url('/product/'.$slug));}
function g1_pretty_cat($slug){return user_trailingslashit(home_url('/product-category/'.$slug));}
$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);
$products=[];$seen=[];$titleGroups=[];$flags=[];
foreach($ids as $id){$p=wc_get_product($id);if(!$p)continue;$slug=(string)get_post_field('post_name',$id);$name=$p->get_name();$old=get_permalink($id);$new=g1_pretty_product($slug);$cats=wp_get_post_terms($id,'product_cat',['fields'=>'names']);
$row=['id'=>(int)$id,'name'=>$name,'slug'=>$slug,'old_url'=>g1_clean($old),'proposed_url'=>g1_clean($new),'categories'=>array_values($cats)];$products[]=$row;
$key=mb_strtolower(trim(preg_replace('/\s+/u',' ',$name)));$titleGroups[$key][]=(int)$id;if(isset($seen[$new]))$flags[]=['type'=>'product_url_collision','ids'=>[$seen[$new],(int)$id],'url'=>$new];else$seen[$new]=(int)$id;
if($slug===''||preg_match('/-\d+$/',$slug))$flags[]=['type'=>'product_slug_review','id'=>(int)$id,'slug'=>$slug,'reason'=>$slug===''?'empty':'numeric-suffix'];
}
foreach($titleGroups as $name=>$group){if(count($group)>1)$flags[]=['type'=>'duplicate_product_title','ids'=>$group,'name'=>$name];}
$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>true]);$categories=[];$cseen=[];if(!is_wp_error($terms)){foreach($terms as $t){$old=get_term_link($t);$new=g1_pretty_cat($t->slug);$row=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'parent'=>(int)$t->parent,'old_url'=>g1_clean($old),'proposed_url'=>g1_clean($new)];$categories[]=$row;if(isset($cseen[$new]))$flags[]=['type'=>'category_url_collision','ids'=>[$cseen[$new],(int)$t->term_id],'url'=>$new];else$cseen[$new]=(int)$t->term_id;if(preg_match('/%[0-9a-f]{2}/i',$t->slug))$flags[]=['type'=>'category_slug_language_review','id'=>(int)$t->term_id,'slug'=>$t->slug];}}
$contract=['wp_post_permalink'=>'/%postname%/','product_base'=>'product','product_pattern'=>'/product/{existing-product-slug}/','category_base'=>'product-category','category_pattern'=>'/product-category/{existing-category-slug}/','slug_policy'=>'preserve existing published slugs during first migration; fix verified bad slugs only in later isolated redirect-backed batch','redirect_policy'=>'301 exact old query URL to mapped pretty canonical; no chains; keep redirects long-term','canonical_policy'=>'self-referencing pretty canonical after migration','draft_policy'=>'exclude drafts','facet_policy'=>'do not create indexable filter/sort/search utility URLs'];
$out=['generated_at'=>gmdate('c'),'server_software'=>$_SERVER['SERVER_SOFTWARE']??'','home_url'=>home_url('/'),'current'=>['permalink_structure'=>(string)get_option('permalink_structure'),'woocommerce_permalinks'=>get_option('woocommerce_permalinks'),'using_permalinks'=>isset($GLOBALS['wp_rewrite'])?$GLOBALS['wp_rewrite']->using_permalinks():null],'contract'=>$contract,'summary'=>['published_products'=>count($products),'active_categories'=>count($categories),'product_collisions'=>count(array_filter($flags,fn($x)=>$x['type']==='product_url_collision')),'category_collisions'=>count(array_filter($flags,fn($x)=>$x['type']==='category_url_collision')),'review_flags'=>count($flags)],'products'=>$products,'categories'=>$categories,'flags'=>$flags];
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
call('save_file_content',{'dir':'public_html','file':probe,'content':php,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
status,body,final,headers=public_get('https://gramiss.ir/'+probe+'?t='+str(int(time.time())),180)
print('PROBE_STATUS',status,'BYTES',len(body),'FINAL',final,'SERVER_HEADER',headers.get('Server',''))
if status!=200: raise SystemExit('ABORT: probe failed; no changes performed')
data=json.loads(body.decode('utf-8','replace'))
print('=== GRAMISS SEO URL MIGRATION DRY RUN V1 ===')
for key in ('server_software','home_url','current','contract','summary','flags'):
    print(key.upper(),json.dumps(data.get(key),ensure_ascii=False,separators=(',',':')))
for row in data.get('products',[]): print('PRODUCT_MAP',json.dumps(row,ensure_ascii=False,separators=(',',':')))
for row in data.get('categories',[]): print('CATEGORY_MAP',json.dumps(row,ensure_ascii=False,separators=(',',':')))
print('=== END DRY RUN; NO OPTIONS, SLUGS, PRODUCTS, TAXONOMIES OR REDIRECTS CHANGED ===')
