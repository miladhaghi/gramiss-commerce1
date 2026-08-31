import base64,hashlib,html,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();last=None
 for attempt in range(1,5):
  try:
   r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}')
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
   q=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
   return q.get('data')
  except Exception as exc:last=exc;print(f'Attempt {attempt}/4 {fn}: {exc}');time.sleep(attempt*2 if attempt<4 else 0)
 raise last
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u,follow=True,timeout=120):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissProductSEOFoundation/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 op=urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
 try:
  with op.open(req,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def one(h,p):
 m=re.search(p,h,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def head_info(raw):
 t=raw.decode('utf-8','replace');h=t.split('</head>',1)[0]
 return {'title':one(h,r'<title[^>]*>(.*?)</title>'),'description':one(h,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':one(h,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':one(h,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)'),'og_title':one(h,r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)'),'og_description':one(h,r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)')}
def schema_info(raw):
 t=raw.decode('utf-8','replace');blocks=re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',t,re.I|re.S);types=[];products=[]
 def walk(x):
  if isinstance(x,dict):
   ty=x.get('@type')
   if isinstance(ty,str):types.append(ty)
   elif isinstance(ty,list):types.extend(str(v) for v in ty)
   isprod=(ty=='Product') or (isinstance(ty,list) and 'Product' in ty)
   if isprod:
    off=x.get('offers');offers=off if isinstance(off,dict) else (off[0] if isinstance(off,list) and off and isinstance(off[0],dict) else {})
    products.append({'name':x.get('name'),'sku':x.get('sku'),'price':offers.get('price') or offers.get('lowPrice'),'currency':offers.get('priceCurrency'),'availability':offers.get('availability')})
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 for b in blocks:
  try:walk(json.loads(html.unescape(b.strip())))
  except Exception:pass
 return {'types':sorted(set(types)),'products':products[:2],'jsonld_blocks':len(blocks)}
def product_state(u):
 s,b,f,_=get(u,True,120);return {'status':s,'final':f,'head':head_info(b),'schema':schema_info(b)}
front=read_theme('front-page.php');home_sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch; no write')
samples={
 'cap':'https://gramiss.ir/product/%DA%A9%D9%84%D8%A7%D9%87-%D9%81%DB%8C%D8%AA-%DA%A9%D9%BE-%D8%A2%D8%A8%DB%8C/',
 'tee':'https://gramiss.ir/product/%D8%AA%DB%8C%D8%B4%D8%B1%D8%AA-%D8%A8%D8%A7%DA%A9%D8%B3%DB%8C-%D8%B3%D9%86%DA%AF%D8%B4%D9%88%D8%B1/',
 'pants':'https://gramiss.ir/product/%D8%B4%D9%84%D9%88%D8%A7%D8%B1%D8%AC%DB%8C%D9%86-%D9%86%DB%8C%D9%85-%D8%A8%DA%AF-%D8%B3%D8%A7%D8%AF%D9%87/',
 'shirt':'https://gramiss.ir/product/%D9%BE%DB%8C%D8%B1%D8%A7%D9%87%D9%86-%D8%A2%D8%B3%D8%AA%DB%8C%D9%86-%D8%A8%D9%84%D9%86%D8%AF-%D9%BE%D8%A7%D8%B1%DA%86%D9%87-%D9%84%D9%87/',
 'shoe':'https://gramiss.ir/product/%DA%A9%D8%AA%D9%88%D9%86%DB%8C-%D8%B7%D8%B1%D8%AD-%D9%88%D9%86%D8%B3-%D8%B3%D8%B1%D9%85%D9%87-%D8%A7%DB%8C/'
}
before={k:product_state(v) for k,v in samples.items()}
for k,v in before.items():print('BEFORE',k,json.dumps(v,ensure_ascii=False,separators=(',',':')))
plugin=r'''<?php
/**
 * Plugin Name: Gramiss Product SEO Foundation
 * Description: Non-destructive product image ALT defaults and Google-compatible IRT→IRR Product JSON-LD normalization.
 * Version: 1.0.0
 */
defined('ABSPATH') || exit;

function gramiss_seo_set_alt_if_empty($attachment_id,$text){
    $attachment_id=(int)$attachment_id;
    if($attachment_id<1 || get_post_type($attachment_id)!=='attachment') return;
    $current=(string)get_post_meta($attachment_id,'_wp_attachment_image_alt',true);
    if(trim($current)!=='') return;
    $text=trim(wp_strip_all_tags((string)$text));
    if($text!=='') update_post_meta($attachment_id,'_wp_attachment_image_alt',$text);
}
function gramiss_seo_sync_product_image_alts($product_id){
    if(!function_exists('wc_get_product')) return;
    $product=wc_get_product((int)$product_id);
    if(!$product) return;
    $name=trim(wp_strip_all_tags($product->get_name()));
    if($name==='') return;
    gramiss_seo_set_alt_if_empty($product->get_image_id(),$name);
    $n=2;
    foreach($product->get_gallery_image_ids() as $image_id){
        gramiss_seo_set_alt_if_empty($image_id,$name.' - تصویر '.$n);
        $n++;
    }
}
add_action('woocommerce_new_product','gramiss_seo_sync_product_image_alts',30,1);
add_action('woocommerce_update_product','gramiss_seo_sync_product_image_alts',30,1);

function gramiss_seo_irt_price_to_irr($value){
    if(!is_numeric($value)) return $value;
    $number=((float)$value)*10;
    if(floor($number)===$number) return sprintf('%.0f',$number);
    return rtrim(rtrim(number_format($number,6,'.',''),'0'),'.');
}
function gramiss_seo_normalize_irt_schema(&$node){
    if(!is_array($node)) return;
    if(isset($node['priceCurrency']) && strtoupper((string)$node['priceCurrency'])==='IRT'){
        $node['priceCurrency']='IRR';
        foreach(['price','lowPrice','highPrice','minPrice','maxPrice'] as $key){
            if(isset($node[$key])) $node[$key]=gramiss_seo_irt_price_to_irr($node[$key]);
        }
    }
    foreach($node as &$value){if(is_array($value)) gramiss_seo_normalize_irt_schema($value);}unset($value);
}
add_filter('rank_math/json_ld',function($data,$jsonld){
    if(function_exists('is_product') && is_product()) gramiss_seo_normalize_irt_schema($data);
    return $data;
},99,2);
'''
plugin_b64=base64.b64encode(plugin.encode()).decode();plugin_sha=hashlib.sha256(plugin.encode()).hexdigest();stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime());nonce=hashlib.sha256((stamp+home_sha+plugin_sha).encode()).hexdigest()[:14]
probe='gramiss-product-seo-write-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
if(!function_exists('rank_math') || (bool)rank_math()->registration->invalid || !function_exists('wc_get_product')){http_response_code(409);echo wp_json_encode(['error'=>'SEO/Woo runtime unavailable']);exit;}
$target=WPMU_PLUGIN_DIR.'/gramiss-product-seo-foundation.php';if(file_exists($target)){http_response_code(409);echo wp_json_encode(['error'=>'target MU plugin already exists']);exit;}
$ti_name='rank-math-options-titles';$old_ti=(array)get_option($ti_name,[]);$old_title=$old_ti['pt_product_title']??'';$old_kg=$old_ti['knowledgegraph_type']??'';$target_title='خرید %title% %sep% %sitename%';
if(!in_array($old_title,['%title% %sep% %sitename%',$target_title],true)){http_response_code(409);echo wp_json_encode(['error'=>'unexpected product title template','value'=>$old_title]);exit;}
if(!in_array($old_kg,['person','company'],true)){http_response_code(409);echo wp_json_encode(['error'=>'unexpected knowledgegraph_type','value'=>$old_kg]);exit;}
$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'fields'=>'ids']);$usage=[];$plans=[];
foreach($ids as $id){$p=wc_get_product($id);if(!$p)continue;$name=trim(wp_strip_all_tags($p->get_name()));$media=[];$fid=(int)$p->get_image_id();if($fid)$media[]=['id'=>$fid,'alt'=>$name];$n=2;foreach($p->get_gallery_image_ids() as $gid){$media[]=['id'=>(int)$gid,'alt'=>$name.' - تصویر '.$n];$n++;}foreach($media as $m){$usage[$m['id']][]=(int)$id;$plans[]=['product_id'=>(int)$id,'attachment_id'=>$m['id'],'new_alt'=>$m['alt']];}}
$shared=[];foreach($usage as $aid=>$pids){$u=array_values(array_unique($pids));if(count($u)>1)$shared[(string)$aid]=$u;}
$changes=[];$changed_ids=[];foreach($plans as $p){$aid=(int)$p['attachment_id'];if(isset($shared[(string)$aid]))continue;if(isset($changed_ids[$aid]))continue;$old=(string)get_post_meta($aid,'_wp_attachment_image_alt',true);if(trim($old)!=='')continue;$changes[]=['attachment_id'=>$aid,'old_alt'=>$old,'new_alt'=>$p['new_alt']];$changed_ids[$aid]=true;}
$manifest=['created_at'=>gmdate('c'),'titles_option_name'=>$ti_name,'old_titles'=>$old_ti,'plugin_target'=>$target,'attachment_alts'=>$changes];$mp=WP_CONTENT_DIR.'/gramiss-product-seo-foundation-v1-'.gmdate('Ymd-His').'.json';if(file_put_contents($mp,wp_json_encode($manifest,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT))===false){http_response_code(500);echo wp_json_encode(['error'=>'manifest write failed']);exit;}
if(!wp_mkdir_p(WPMU_PLUGIN_DIR)){http_response_code(500);echo wp_json_encode(['error'=>'mu-plugin directory unavailable','manifest'=>$mp]);exit;}
$plugin=base64_decode('__PLUGIN_B64__');if(file_put_contents($target,$plugin)===false){http_response_code(500);echo wp_json_encode(['error'=>'plugin write failed','manifest'=>$mp]);exit;}
$ti=$old_ti;$ti['pt_product_title']=$target_title;$ti['knowledgegraph_type']='company';if(!update_option($ti_name,$ti,false) && get_option($ti_name)!=$ti){@unlink($target);http_response_code(500);echo wp_json_encode(['error'=>'titles update failed','manifest'=>$mp]);exit;}
foreach($changes as $c)update_post_meta((int)$c['attachment_id'],'_wp_attachment_image_alt',$c['new_alt']);do_action('litespeed_purge_all');
echo wp_json_encode(['ok'=>true,'manifest'=>$mp,'products'=>count($ids),'alts_changed'=>count($changes),'shared_skipped'=>$shared,'product_title'=>$ti['pt_product_title'],'knowledgegraph_type'=>$ti['knowledgegraph_type'],'plugin_sha256'=>hash_file('sha256',$target)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''.replace('__PLUGIN_B64__',plugin_b64)
save(probe,php);ws,wb,_,_=get('https://gramiss.ir/'+probe+'?t='+str(int(time.time())),True,180);print('WRITE',ws,wb.decode('utf-8','replace'))
if ws!=200:raise SystemExit('ABORT Product SEO write failed')
write_data=json.loads(wb.decode('utf-8','replace'));manifest=write_data['manifest'];errors=[];time.sleep(2)
# Verify database state, every current product image ALT, and persistent MU plugin.
verify='gramiss-product-seo-verify-'+nonce+'.php'
vphp=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$ti=(array)get_option('rank-math-options-titles',[]);$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'fields'=>'ids']);$missing=[];$gallery=0;$price_empty=[];$sku_empty=0;foreach($ids as $id){$p=wc_get_product($id);if(!$p)continue;if($p->get_sku()==='')$sku_empty++;if($p->get_price()==='')$price_empty[]=(int)$id;$fid=(int)$p->get_image_id();if($fid && trim((string)get_post_meta($fid,'_wp_attachment_image_alt',true))==='')$missing[]=$fid;foreach($p->get_gallery_image_ids() as $gid){$gallery++;if(trim((string)get_post_meta($gid,'_wp_attachment_image_alt',true))==='')$missing[]=(int)$gid;}}$target=WPMU_PLUGIN_DIR.'/gramiss-product-seo-foundation.php';echo wp_json_encode(['products'=>count($ids),'gallery_images'=>$gallery,'missing_alt_ids'=>array_values(array_unique($missing)),'sku_empty'=>$sku_empty,'price_empty_ids'=>$price_empty,'pt_product_title'=>$ti['pt_product_title']??null,'knowledgegraph_type'=>$ti['knowledgegraph_type']??null,'plugin_exists'=>file_exists($target),'plugin_sha256'=>file_exists($target)?hash_file('sha256',$target):null],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(verify,vphp);vs,vb,_,_=get('https://gramiss.ir/'+verify+'?t='+str(int(time.time())),True,180);print('DB_VERIFY',vs,vb.decode('utf-8','replace'))
if vs!=200:errors.append('database verify failed')
else:
 vd=json.loads(vb.decode('utf-8','replace'))
 if vd.get('pt_product_title')!='خرید %title% %sep% %sitename%':errors.append('product title template mismatch')
 if vd.get('knowledgegraph_type')!='company':errors.append('knowledgegraph not company')
 if not vd.get('plugin_exists') or vd.get('plugin_sha256')!=plugin_sha:errors.append('MU plugin mismatch')
 shared=set(str(x) for x in write_data.get('shared_skipped',{}).keys());unexpected=[x for x in vd.get('missing_alt_ids',[]) if str(x) not in shared]
 if unexpected:errors.append('unexpected empty product image alts '+json.dumps(unexpected))
# Verify output: descriptions/canonicals unchanged; titles intentional; Product JSON-LD uses equivalent ISO IRR.
after={k:product_state(v) for k,v in samples.items()}
for k,v in after.items():
 print('AFTER',k,json.dumps(v,ensure_ascii=False,separators=(',',':')));b=before[k]
 if v['status']!=200:errors.append(k+' non-200')
 if not v['head']['title'].startswith('خرید '):errors.append(k+' title template not applied')
 if v['head']['description']!=b['head']['description']:errors.append(k+' description changed')
 if v['head']['canonical']!=b['head']['canonical']:errors.append(k+' canonical changed')
 if 'noindex' in v['head']['robots'].lower():errors.append(k+' became noindex')
 bp=(b['schema'].get('products') or [{}])[0];ap=(v['schema'].get('products') or [{}])[0]
 if bp.get('currency')=='IRT':
  if ap.get('currency')!='IRR':errors.append(k+' schema currency not IRR')
  try:
   if abs(float(ap.get('price'))-float(bp.get('price'))*10)>0.01:errors.append(k+' schema price not equivalent IRR')
  except Exception:errors.append(k+' schema price verify failed')
# Home remains a Company/Organization and protected file stays exact.
hs,hraw,hfinal,_=get('https://gramiss.ir/',True,120);hsi=schema_info(hraw);print('HOME_SCHEMA',hs,json.dumps(hsi,ensure_ascii=False,separators=(',',':')))
if 'Organization' not in hsi.get('types',[]):errors.append('Organization schema missing on Home')
ss,sraw,_,_=get('https://gramiss.ir/sitemap_index.xml?t='+str(int(time.time())),True,120);children=re.findall(r'<loc>(.*?)</loc>',sraw.decode('utf-8','replace'),re.I);print('SITEMAP_INDEX',ss,json.dumps(children,ensure_ascii=False))
expected={'https://gramiss.ir/page-sitemap.xml','https://gramiss.ir/product-sitemap.xml','https://gramiss.ir/product_cat-sitemap.xml'}
if ss!=200 or set(children)!=expected:errors.append('sitemap structure changed')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:errors.append('Home changed')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));rb='gramiss-product-seo-rollback-'+nonce+'.php';mp=json.dumps(manifest)
 rbphp="<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$m=json_decode(file_get_contents("+mp+"),true);update_option($m['titles_option_name'],$m['old_titles'],false);foreach($m['attachment_alts'] as $a)update_post_meta((int)$a['attachment_id'],'_wp_attachment_image_alt',$a['old_alt']);if(isset($m['plugin_target'])&&file_exists($m['plugin_target']))@unlink($m['plugin_target']);do_action('litespeed_purge_all');echo 'ROLLED_BACK';"
 save(rb,rbphp);rs,rr,_,_=get('https://gramiss.ir/'+rb+'?t='+str(int(time.time())),True,180);print('ROLLBACK',rs,rr[:200]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS PRODUCT SEO FOUNDATION V1')
print('ALTS_CHANGED',write_data.get('alts_changed'),'PRODUCTS',write_data.get('products'),'PLUGIN_SHA',plugin_sha)
print('HOME SHA PRESERVED',home_sha)
