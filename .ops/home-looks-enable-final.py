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

def read_theme(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=root if not parent else root+'/'+parent
    data=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for key in ('content','file_content','data'):
            if isinstance(data.get(key),str): return data[key]
    if isinstance(data,str): return data
    raise RuntimeError('Cannot read '+rel)

def public_get(url,timeout=120):
    req=urllib.request.Request(url,headers={'User-Agent':'GramissSEOInventory/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req,context=ctx,timeout=timeout) as r: return r.status,r.read(),r.geturl()

front=read_theme('front-page.php'); front_sha=hashlib.sha256(front.encode()).hexdigest(); print('LIVE_HOME_SHA',front_sha)
if healthy and front_sha!=healthy: raise SystemExit('ABORT: Home baseline mismatch; no product reads performed')

nonce=hashlib.sha256((stamp+front_sha).encode()).hexdigest()[:18]
probe=f'gramiss-seo-inventory-{nonce}.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
if (!function_exists('wc_get_product')) { http_response_code(500); echo json_encode(['error'=>'WooCommerce unavailable']); exit; }

function g1_meta($id,$keys){$o=[];foreach($keys as $k){$v=get_post_meta($id,$k,true);if($v!==''&&$v!==null)$o[$k]=(string)$v;}return $o;}
function g1_images($p){$ids=[];$f=$p->get_image_id();if($f)$ids[]=$f;foreach($p->get_gallery_image_ids() as $id){if(!in_array($id,$ids,true))$ids[]=$id;}$out=[];foreach($ids as $id){$alt=(string)get_post_meta($id,'_wp_attachment_image_alt',true);$out[]=['id'=>(int)$id,'alt'=>$alt,'alt_empty'=>trim($alt)==='','title'=>get_the_title($id),'url'=>wp_get_attachment_url($id)];}return $out;}
function g1_attrs($p){$out=[];foreach($p->get_attributes() as $a){$name=$a->get_name();$vals=[];if($a->is_taxonomy()){$vals=wc_get_product_terms($p->get_id(),$name,['fields'=>'names']);}else{$vals=$a->get_options();}$out[]=['name'=>$name,'label'=>wc_attribute_label($name),'values'=>array_values($vals),'variation'=>(bool)$a->get_variation(),'visible'=>(bool)$a->get_visible()];}return $out;}

$ids=get_posts(['post_type'=>'product','post_status'=>['publish','draft','pending','private'],'numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);
$products=[];$summary=['products'=>0,'published'=>0,'draft_or_private'=>0,'simple'=>0,'variable'=>0,'other_types'=>0,'variations'=>0,'missing_parent_sku'=>0,'missing_description'=>0,'missing_short_description'=>0,'missing_featured_image'=>0,'image_alt_empty'=>0,'products_with_any_empty_alt'=>0,'products_without_category'=>0,'query_product_urls'=>0,'pretty_product_urls'=>0,'seo_title_missing'=>0,'seo_description_missing'=>0,'seo_canonical_missing'=>0,'variation_missing_sku'=>0,'variation_missing_price'=>0,'variation_out_of_stock'=>0];
$seo_keys=['_yoast_wpseo_title','_yoast_wpseo_metadesc','_yoast_wpseo_canonical','rank_math_title','rank_math_description','rank_math_canonical_url','_seopress_titles_title','_seopress_titles_desc','_seopress_robots_canonical'];
foreach($ids as $id){$p=wc_get_product($id);if(!$p)continue;$summary['products']++;$status=get_post_status($id);if($status==='publish')$summary['published']++;else$summary['draft_or_private']++;$type=$p->get_type();if(isset($summary[$type]))$summary[$type]++;else$summary['other_types']++;
$cats=wp_get_post_terms($id,'product_cat',['fields'=>'all']);$catrows=[];foreach($cats as $c)$catrows[]=['id'=>(int)$c->term_id,'name'=>$c->name,'slug'=>$c->slug];if(!$catrows)$summary['products_without_category']++;
$permalink=get_permalink($id);if(strpos($permalink,'?product=')!==false)$summary['query_product_urls']++;else$summary['pretty_product_urls']++;
$sku=(string)$p->get_sku();if(trim($sku)==='')$summary['missing_parent_sku']++;$desc=(string)$p->get_description();$short=(string)$p->get_short_description();if(trim(wp_strip_all_tags($desc))==='')$summary['missing_description']++;if(trim(wp_strip_all_tags($short))==='')$summary['missing_short_description']++;if(!$p->get_image_id())$summary['missing_featured_image']++;
$images=g1_images($p);$empty=0;foreach($images as $im){if($im['alt_empty']){$empty++;$summary['image_alt_empty']++;}}if($empty)$summary['products_with_any_empty_alt']++;
$seo=g1_meta($id,$seo_keys);$hasTitle=isset($seo['_yoast_wpseo_title'])||isset($seo['rank_math_title'])||isset($seo['_seopress_titles_title']);$hasDesc=isset($seo['_yoast_wpseo_metadesc'])||isset($seo['rank_math_description'])||isset($seo['_seopress_titles_desc']);$hasCan=isset($seo['_yoast_wpseo_canonical'])||isset($seo['rank_math_canonical_url'])||isset($seo['_seopress_robots_canonical']);if(!$hasTitle)$summary['seo_title_missing']++;if(!$hasDesc)$summary['seo_description_missing']++;if(!$hasCan)$summary['seo_canonical_missing']++;
$vars=[];if($p->is_type('variable')){foreach($p->get_children() as $vid){$v=wc_get_product($vid);if(!$v)continue;$summary['variations']++;$vsku=(string)$v->get_sku();$vprice=(string)$v->get_price();if(trim($vsku)==='')$summary['variation_missing_sku']++;if(trim($vprice)==='')$summary['variation_missing_price']++;if(!$v->is_in_stock())$summary['variation_out_of_stock']++;$vars[]=['id'=>(int)$vid,'sku'=>$vsku,'price'=>$vprice,'regular_price'=>(string)$v->get_regular_price(),'sale_price'=>(string)$v->get_sale_price(),'stock_status'=>$v->get_stock_status(),'manage_stock'=>$v->get_manage_stock(),'stock_quantity'=>$v->get_stock_quantity(),'attributes'=>$v->get_attributes()];}}
$products[]=['id'=>(int)$id,'status'=>$status,'name'=>$p->get_name(),'slug'=>get_post_field('post_name',$id),'type'=>$type,'permalink'=>$permalink,'sku'=>$sku,'price'=>(string)$p->get_price(),'regular_price'=>(string)$p->get_regular_price(),'sale_price'=>(string)$p->get_sale_price(),'stock_status'=>$p->get_stock_status(),'manage_stock'=>$p->get_manage_stock(),'stock_quantity'=>$p->get_stock_quantity(),'categories'=>$catrows,'attributes'=>g1_attrs($p),'variation_count'=>count($vars),'variation_issues'=>['missing_sku'=>count(array_filter($vars,fn($x)=>trim($x['sku'])==='')),'missing_price'=>count(array_filter($vars,fn($x)=>trim($x['price'])==='')),'out_of_stock'=>count(array_filter($vars,fn($x)=>$x['stock_status']!=='instock'))],'variations'=>$vars,'description_len'=>mb_strlen(trim(wp_strip_all_tags($desc))),'short_description_len'=>mb_strlen(trim(wp_strip_all_tags($short))),'featured_image_id'=>(int)$p->get_image_id(),'image_count'=>count($images),'empty_alt_count'=>$empty,'images'=>$images,'seo_meta'=>$seo];}
$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>false]);$categories=[];if(!is_wp_error($terms)){foreach($terms as $t)$categories[]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'parent'=>(int)$t->parent,'description_len'=>mb_strlen(trim(wp_strip_all_tags($t->description))),'permalink'=>get_term_link($t)];}
$active=(array)get_option('active_plugins',[]);$seo_plugins=array_values(array_filter($active,function($p){$s=strtolower($p);return strpos($s,'yoast')!==false||strpos($s,'seo')!==false||strpos($s,'rank-math')!==false||strpos($s,'aioseo')!==false;}));
$out=['generated_at'=>gmdate('c'),'site'=>['home_url'=>home_url('/'),'site_url'=>site_url('/'),'blog_public'=>(int)get_option('blog_public'),'permalink_structure'=>(string)get_option('permalink_structure'),'woocommerce_permalinks'=>get_option('woocommerce_permalinks'),'shop_page_id'=>(int)get_option('woocommerce_shop_page_id'),'shop_url'=>function_exists('wc_get_page_permalink')?wc_get_page_permalink('shop'):'','seo_plugins'=>$seo_plugins],'summary'=>$summary,'categories'=>$categories,'products'=>$products];
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
call('save_file_content',{'dir':'public_html','file':probe,'content':php,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
try:
    status,body,final=public_get('https://gramiss.ir/'+probe+'?t='+str(int(time.time())),180)
    print('PROBE_STATUS',status,'BYTES',len(body),'FINAL',final)
    if status!=200: raise RuntimeError('inventory probe non-200')
    data=json.loads(body.decode('utf-8','replace'))
finally:
    # The PHP self-deletes before reading WooCommerce. If HTTP failed before execution, try deleting it via Fileman.
    try: call('delete_files',{'dir':'public_html','files':probe},True)
    except Exception: pass

print('=== GRAMISS PRODUCT INVENTORY V1 ===')
print('SITE',json.dumps(data.get('site',{}),ensure_ascii=False,separators=(',',':')))
print('SUMMARY',json.dumps(data.get('summary',{}),ensure_ascii=False,separators=(',',':')))
print('CATEGORIES',json.dumps(data.get('categories',[]),ensure_ascii=False,separators=(',',':')))
for p in data.get('products',[]):
    compact={k:p.get(k) for k in ['id','status','name','slug','type','permalink','sku','price','regular_price','sale_price','stock_status','manage_stock','stock_quantity','categories','attributes','variation_count','variation_issues','description_len','short_description_len','featured_image_id','image_count','empty_alt_count','seo_meta']}
    print('PRODUCT',json.dumps(compact,ensure_ascii=False,separators=(',',':')))
    if p.get('variation_count'):
        print('VARIATIONS',p.get('id'),json.dumps(p.get('variations',[]),ensure_ascii=False,separators=(',',':')))
    if p.get('empty_alt_count'):
        print('IMAGE_ALT_ISSUES',p.get('id'),json.dumps([i for i in p.get('images',[]) if i.get('alt_empty')],ensure_ascii=False,separators=(',',':')))
print('=== END INVENTORY; NO PRODUCT/OPTION/TAXONOMY MUTATIONS PERFORMED ===')
