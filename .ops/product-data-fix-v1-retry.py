import base64,hashlib,html,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context();baseline_manifest='/home/gramissi/public_html/wp-content/gramiss-product-data-fix-v1-20260831-103126.json';old_plugin_sha='a719f2d27d4d6632b520df9d056dd74458343d36dc333d1f0a9b582ad3a426f1'
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
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def get(u,follow=True,timeout=180):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissProductDataFixRetry/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});hs=[urllib.request.HTTPSHandler(context=ctx)]
 if not follow:hs.insert(0,NoRedirect())
 op=urllib.request.build_opener(*hs)
 try:
  with op.open(req,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def hval(h,n):
 for k,v in h.items():
  if k.lower()==n.lower():return v
 return ''
def one(h,p):
 m=re.search(p,h,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def head_info(raw):
 t=raw.decode('utf-8','replace');h=t.split('</head>',1)[0];return {'title':one(h,r'<title[^>]*>(.*?)</title>'),'description':one(h,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':one(h,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':one(h,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
front=read_theme('front-page.php');home_sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch')
plugin=r'''<?php
/**
 * Plugin Name: Gramiss Product SEO Foundation
 * Description: Product image ALT automation, Google-compatible IRT→IRR Product JSON-LD, and automatic noindex for incomplete published products.
 * Version: 1.1.0
 */
defined('ABSPATH') || exit;
function gramiss_seo_auto_alt_value_key(){return '_gramiss_auto_product_alt_value';}
function gramiss_seo_auto_alt_owner_key(){return '_gramiss_auto_product_alt_product';}
function gramiss_seo_set_product_alt($attachment_id,$text,$product_id){$attachment_id=(int)$attachment_id;$product_id=(int)$product_id;if($attachment_id<1||get_post_type($attachment_id)!=='attachment')return;$text=trim(wp_strip_all_tags((string)$text));if($text==='')return;$current=(string)get_post_meta($attachment_id,'_wp_attachment_image_alt',true);$auto=(string)get_post_meta($attachment_id,gramiss_seo_auto_alt_value_key(),true);$owner=(int)get_post_meta($attachment_id,gramiss_seo_auto_alt_owner_key(),true);if($current===''||($owner===$product_id&&$auto!==''&&$current===$auto)){update_post_meta($attachment_id,'_wp_attachment_image_alt',$text);update_post_meta($attachment_id,gramiss_seo_auto_alt_value_key(),$text);update_post_meta($attachment_id,gramiss_seo_auto_alt_owner_key(),$product_id);return;}if($owner===$product_id&&$auto!==''&&$current!==$auto){delete_post_meta($attachment_id,gramiss_seo_auto_alt_value_key());delete_post_meta($attachment_id,gramiss_seo_auto_alt_owner_key());}}
function gramiss_seo_sync_product_image_alts($product_id){if(!function_exists('wc_get_product'))return;$p=wc_get_product((int)$product_id);if(!$p||$p->is_type('variation'))return;$name=trim(wp_strip_all_tags($p->get_name()));if($name==='')return;gramiss_seo_set_product_alt($p->get_image_id(),$name,$product_id);$n=2;foreach($p->get_gallery_image_ids() as $aid){gramiss_seo_set_product_alt($aid,$name.' - تصویر '.$n,$product_id);$n++;}}
function gramiss_seo_product_incomplete($p){if(!$p||$p->get_status()!=='publish')return false;if($p->is_type('variable')){$children=$p->get_children();if(!$children)return true;$priced=false;foreach($children as $vid){$v=wc_get_product($vid);if($v&&get_post_status($vid)==='publish'&&$v->get_price()!==''){$priced=true;break;}}return !$priced;}return $p->get_price()==='';}
function gramiss_seo_auto_robots_match($r){if(!is_array($r))return false;$r=array_values(array_unique(array_map('strval',$r)));sort($r);$a=['follow','noindex'];sort($a);return $r===$a;}
function gramiss_seo_invalidate_product_sitemap(){if(class_exists('RankMath\\Sitemap\\Cache')){\RankMath\Sitemap\Cache::invalidate_storage('product');}}
function gramiss_seo_sync_product_indexability($product_id){if(!function_exists('wc_get_product'))return;$p=wc_get_product((int)$product_id);if(!$p||$p->is_type('variation'))return;$flag=(string)get_post_meta($product_id,'_gramiss_auto_noindex_incomplete',true);$robots=get_post_meta($product_id,'rank_math_robots',true);$incomplete=gramiss_seo_product_incomplete($p);$changed=false;if($incomplete){if($flag==='1'){if(!gramiss_seo_auto_robots_match($robots))delete_post_meta($product_id,'_gramiss_auto_noindex_incomplete');}elseif($robots===''||$robots===[]){update_post_meta($product_id,'rank_math_robots',['noindex','follow']);update_post_meta($product_id,'_gramiss_auto_noindex_incomplete','1');$changed=true;}}elseif($flag==='1'){if(gramiss_seo_auto_robots_match($robots))delete_post_meta($product_id,'rank_math_robots');delete_post_meta($product_id,'_gramiss_auto_noindex_incomplete');$changed=true;}if($changed)gramiss_seo_invalidate_product_sitemap();}
function gramiss_seo_sync_product_foundation($product_id){gramiss_seo_sync_product_image_alts($product_id);gramiss_seo_sync_product_indexability($product_id);}
add_action('woocommerce_new_product','gramiss_seo_sync_product_foundation',40,1);add_action('woocommerce_update_product','gramiss_seo_sync_product_foundation',40,1);add_action('woocommerce_save_product_variation',function($variation_id){$parent=wp_get_post_parent_id($variation_id);if($parent)gramiss_seo_sync_product_indexability($parent);},99,1);
function gramiss_seo_irt_price_to_irr($value){if(!is_numeric($value))return $value;$number=((float)$value)*10;if(floor($number)===$number)return sprintf('%.0f',$number);return rtrim(rtrim(number_format($number,6,'.',''),'0'),'.');}
function gramiss_seo_normalize_irt_schema(&$node){if(!is_array($node))return;if(isset($node['priceCurrency'])&&strtoupper((string)$node['priceCurrency'])==='IRT'){$node['priceCurrency']='IRR';foreach(['price','lowPrice','highPrice','minPrice','maxPrice'] as $key)if(isset($node[$key]))$node[$key]=gramiss_seo_irt_price_to_irr($node[$key]);}foreach($node as &$value)if(is_array($value))gramiss_seo_normalize_irt_schema($value);unset($value);}
add_filter('rank_math/json_ld',function($data,$jsonld){if(function_exists('is_product')&&is_product())gramiss_seo_normalize_irt_schema($data);return $data;},99,2);
'''
plugin_b64=base64.b64encode(plugin.encode()).decode();plugin_sha=hashlib.sha256(plugin.encode()).hexdigest();nonce=hashlib.sha256((str(time.time())+home_sha).encode()).hexdigest()[:14]
write='gramiss-product-data-retry-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$mp='__MANIFEST__';if(!file_exists($mp)){http_response_code(409);echo wp_json_encode(['error'=>'baseline manifest missing']);exit;}$target=WPMU_PLUGIN_DIR.'/gramiss-product-seo-foundation.php';if(!file_exists($target)||hash_file('sha256',$target)!=='__OLD_SHA__'){http_response_code(409);echo wp_json_encode(['error'=>'baseline plugin drift','sha'=>file_exists($target)?hash_file('sha256',$target):null]);exit;}
$guards=[84=>['title'=>'کلاه فیت کپ مشکی نارنجی NY','slug'=>'%d9%85%d9%84%d8%a7%d9%87-%d9%81%db%8c%d8%aa-%da%a9%d9%be-%d9%85%d8%b4%da%a9%db%8c-%d9%86%d8%a7%d8%b1%d9%86%d8%ac%db%8c-ny'],296=>['title'=>'پیراهن آستین بلند پارچه سیلک','slug'=>'%d9%be%db%8c%d8%b1%d8%a7%d9%87%d9%86-%d8%a2%d8%b3%d8%aa%db%8c%d9%86-%d8%a8%d9%84%d9%86%d8%af-%d9%be%d8%a7%d8%b1%da%86%d9%87-%d9%84%d9%87'],307=>['title'=>'پیراهن آستین بلند پارچه سیلک'],320=>['title'=>'پیراهن آستین بلند پارچه سیلک','slug'=>'%d9%be%db%8c%d8%b1%d8%a7%d9%87%d9%86-%d8%a2%d8%b3%d8%aa%db%8c%d9%86-%d8%a8%d9%84%d9%86%d8%af-%d9%be%d8%a7%d8%b1%da%86%d9%87-%d8%b3%db%8c%d9%84%da%a9-2'],330=>['title'=>'پیراهن لینن آستین کوتاه'],344=>['title'=>'پراهن آستین کوتاه لینن','slug'=>'%d9%be%d8%b1%d8%a7%d9%87%d9%86-%d8%a2%d8%b3%d8%aa%db%8c%d9%86-%da%a9%d9%88%d8%aa%d8%a7%d9%87-%d9%84%db%8c%d9%86%d9%86'],355=>['title'=>'پیراهن آستین بلند ماچایی پارچه سیلک'],359=>['title'=>'شلوار پارچه ای بگ ریزشی'],366=>['title'=>'شلوار پارچه ای بگ ریزشی']];foreach($guards as $id=>$g){$p=get_post($id);if(!$p||$p->post_title!==$g['title']||(isset($g['slug'])&&$p->post_name!==$g['slug'])){http_response_code(409);echo wp_json_encode(['error'=>'baseline product drift','id'=>$id]);exit;}}
if(file_put_contents($target,base64_decode('__PLUGIN__'))===false){http_response_code(500);echo wp_json_encode(['error'=>'plugin write failed']);exit;}
$updates=[84=>['post_name'=>'کلاه-فیت-کپ-مشکی-نارنجی-ny','post_content'=>'کلاه فیت کپ مشکی نارنجی NY جنس کتان گلدوزی درجه یک خارجی اورجینال'],87=>['post_content'=>'کلاه فیت کپ NY مشکی طرح فرشته گل سرخ جنس کتان قابل شست و شو گلدوزی درجه یک اورجینال خارجی'],296=>['post_title'=>'پیراهن آستین بلند پارچه سیلک هلویی و آبی‌طوسی','post_name'=>'پیراهن-آستین-بلند-سیلک-هلویی-آبی-طوسی'],307=>['post_title'=>'پیراهن آستین بلند پارچه سیلک قهوه‌ای و کرم'],320=>['post_title'=>'پیراهن آستین بلند پارچه سیلک گرم‌دار','post_name'=>'پیراهن-آستین-بلند-سیلک-گرم-دار'],330=>['post_title'=>'پیراهن لینن آستین کوتاه سرمه‌ای','post_content'=>'پیراهن آستین کوتاه لینن سرمه‌ای پارچه خنک شست رفته بدون آبرفت\r\nتضمین کیفیت و رنگ پارچه در شست و شو'],344=>['post_title'=>'پیراهن لینن آستین کوتاه آبی','post_name'=>'پیراهن-لینن-آستین-کوتاه-آبی','post_content'=>'پیراهن آستین کوتاه لینن آبی پارچه خنک شست رفته بدون آبرفت\r\nتضمین کیفیت و رنگ پارچه در شست و شو'],359=>['post_title'=>'شلوار پارچه‌ای بگ ریزشی'],366=>['post_title'=>'شلوار پارچه‌ای فول بگ ریزشی']];$redirects=[];foreach($updates as $id=>$u){$old=get_permalink($id);$args=['ID'=>$id]+$u;$r=wp_update_post(wp_slash($args),true);if(is_wp_error($r)){http_response_code(500);echo wp_json_encode(['error'=>'update failed','id'=>$id,'message'=>$r->get_error_message()]);exit;}$new=get_permalink($id);if($old!==$new)$redirects[]=['id'=>$id,'old'=>$old,'new'=>$new];}
$terms=wp_get_post_terms(355,'product_cat',['fields'=>'ids']);$terms=array_values(array_diff($terms,[56]));$terms[]=57;wp_set_post_terms(355,array_values(array_unique(array_map('intval',$terms))),'product_cat',false);foreach([62,68,80,84,87] as $id)wp_remove_object_terms($id,44,'product_cat');
$all=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'fields'=>'ids']);foreach($all as $id){$p=wc_get_product($id);if(!$p)continue;$name=get_the_title($id);$imgs=array_values(array_filter(array_merge([$p->get_image_id()],$p->get_gallery_image_ids())));$n=1;foreach($imgs as $aid){$oldtitle=$name;# For changed titles, allow the exact pre-fix auto ALT from manifest or current title pattern.
$desired=$n===1?$name:$name.' - تصویر '.$n;$current=(string)get_post_meta($aid,'_wp_attachment_image_alt',true);$owner=(int)get_post_meta($aid,'_gramiss_auto_product_alt_product',true);$auto=(string)get_post_meta($aid,'_gramiss_auto_product_alt_value',true);if($current===''||($auto!==''&&$owner===(int)$id&&$current===$auto)||in_array((int)$id,[296,307,320,330,344,359,366],true)){update_post_meta($aid,'_wp_attachment_image_alt',$desired);update_post_meta($aid,'_gramiss_auto_product_alt_value',$desired);update_post_meta($aid,'_gramiss_auto_product_alt_product',$id);}elseif($current===$desired){update_post_meta($aid,'_gramiss_auto_product_alt_value',$desired);update_post_meta($aid,'_gramiss_auto_product_alt_product',$id);}$n++;}}
foreach([62,68] as $id){$robots=get_post_meta($id,'rank_math_robots',true);if($robots===''||$robots===[]){update_post_meta($id,'rank_math_robots',['noindex','follow']);update_post_meta($id,'_gramiss_auto_noindex_incomplete','1');}}
if(class_exists('RankMath\\Sitemap\\Cache'))\RankMath\Sitemap\Cache::invalidate_storage();global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'plugin_sha'=>hash_file('sha256',$target),'redirects'=>$redirects],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''.replace('__MANIFEST__',baseline_manifest).replace('__OLD_SHA__',old_plugin_sha).replace('__PLUGIN__',plugin_b64)
save(write,php);ws,wb,_,_=get('https://gramiss.ir/'+write+'?t='+str(int(time.time())),True,240);print('WRITE',ws,wb.decode('utf-8','replace'))
if ws!=200:raise SystemExit('ABORT retry write failed')
w=json.loads(wb.decode('utf-8','replace'));errors=[];time.sleep(2)
# Compact DB verifier.
vp='gramiss-product-data-retry-verify-'+nonce+'.php';vphp=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$ids=[62,68,80,84,87,296,307,320,330,344,355,359,366];$rows=[];foreach($ids as $id){$p=wc_get_product($id);$terms=wp_get_post_terms($id,'product_cat',['fields'=>'slugs']);$imgs=[];foreach(array_values(array_filter(array_merge([$p->get_image_id()],$p->get_gallery_image_ids()))) as $aid)$imgs[]=['alt'=>get_post_meta($aid,'_wp_attachment_image_alt',true),'auto'=>get_post_meta($aid,'_gramiss_auto_product_alt_value',true),'owner'=>get_post_meta($aid,'_gramiss_auto_product_alt_product',true)];$rows[(string)$id]=['title'=>get_the_title($id),'url'=>get_permalink($id),'terms'=>$terms,'robots'=>get_post_meta($id,'rank_math_robots',true),'flag'=>get_post_meta($id,'_gramiss_auto_noindex_incomplete',true),'price'=>$p->get_price(),'children'=>count($p->get_children()),'images'=>$imgs,'content'=>trim(wp_strip_all_tags($p->get_description()))];}$g=[];foreach(get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'fields'=>'ids']) as $id)$g[get_the_title($id)][]=$id;$dupes=[];foreach($g as $n=>$x)if(count($x)>1)$dupes[]=['name'=>$n,'ids'=>$x];foreach(['snapback-cap','fitted-cap','short-sleeve-shirt','long-sleeve-shirt'] as $s){$t=get_term_by('slug',$s,'product_cat');$counts[$s]=$t?(int)$t->count:null;}$target=WPMU_PLUGIN_DIR.'/gramiss-product-seo-foundation.php';echo wp_json_encode(['rows'=>$rows,'duplicates'=>$dupes,'counts'=>$counts,'plugin_sha'=>hash_file('sha256',$target)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save(vp,vphp);vs,vb,_,_=get('https://gramiss.ir/'+vp+'?t='+str(int(time.time())),True,180);print('DB_VERIFY',vs,vb.decode('utf-8','replace'))
if vs!=200:errors.append('DB verify failed');vd={}
else:vd=json.loads(vb.decode('utf-8','replace'))
exp={'296':'پیراهن آستین بلند پارچه سیلک هلویی و آبی‌طوسی','307':'پیراهن آستین بلند پارچه سیلک قهوه‌ای و کرم','320':'پیراهن آستین بلند پارچه سیلک گرم‌دار','330':'پیراهن لینن آستین کوتاه سرمه‌ای','344':'پیراهن لینن آستین کوتاه آبی','359':'شلوار پارچه‌ای بگ ریزشی','366':'شلوار پارچه‌ای فول بگ ریزشی'}
for i,t in exp.items():
 r=vd.get('rows',{}).get(i,{});
 if r.get('title')!=t:errors.append('title mismatch '+i)
 for n,img in enumerate(r.get('images',[]),1):
  a=t if n==1 else t+' - تصویر '+str(n)
  if img.get('alt')!=a or img.get('auto')!=a or str(img.get('owner'))!=i:errors.append('ALT mismatch '+i+'#'+str(n))
for i in ('62','68'):
 r=vd.get('rows',{}).get(i,{});
 if 'noindex' not in r.get('robots',[]) or r.get('flag')!='1':errors.append('auto noindex failed '+i)
for i in ('62','68','80','84','87'):
 if 'snapback-cap' in vd.get('rows',{}).get(i,{}).get('terms',[]):errors.append('snapback still assigned '+i)
if 'long-sleeve-shirt' not in vd.get('rows',{}).get('355',{}).get('terms',[]) or 'short-sleeve-shirt' in vd.get('rows',{}).get('355',{}).get('terms',[]):errors.append('355 category wrong')
if vd.get('duplicates'):errors.append('duplicate titles remain')
if vd.get('counts',{}).get('snapback-cap')!=0 or vd.get('counts',{}).get('short-sleeve-shirt')!=5 or vd.get('counts',{}).get('long-sleeve-shirt')!=4:errors.append('category counts wrong')
if vd.get('plugin_sha')!=plugin_sha:errors.append('plugin SHA mismatch')
if 'فیت کچ' in vd.get('rows',{}).get('84',{}).get('content','') or 'مشکلی' in vd.get('rows',{}).get('84',{}).get('content',''):errors.append('84 text typo remains')
if 'جس کتان' in vd.get('rows',{}).get('87',{}).get('content',''):errors.append('87 text typo remains')
# Redirects: all old slugs must resolve 301 to new.
for r in w.get('redirects',[]):
 s,_,_,h=get(r['old'],False,90);loc=hval(h,'Location');print('REDIRECT',r['id'],s,'=>',loc)
 if s!=301 or urllib.parse.unquote((loc or '').rstrip('/'))!=urllib.parse.unquote(r['new'].rstrip('/')):errors.append('redirect failed '+str(r['id']))
# Live SEO: canonical required only for indexable products. Rank Math intentionally omits it on noindex pages.
for i in (84,296,307,320,330,344,355,359,366,62,68):
 r=vd.get('rows',{}).get(str(i),{});s,raw,f,_=get(r.get('url'),True,120);h=head_info(raw);print('LIVE',i,s,json.dumps({'url':f,**h},ensure_ascii=False,separators=(',',':')))
 if s!=200:errors.append('live non-200 '+str(i))
 if i in (62,68):
  if 'noindex' not in h['robots'].lower():errors.append('live noindex missing '+str(i))
 else:
  if not h['canonical'] or 'noindex' in h['robots'].lower() or not h['title'].startswith('خرید '):errors.append('live SEO failed '+str(i))
# Sitemap.
ss,sraw,_,_=get('https://gramiss.ir/sitemap_index.xml?t='+str(int(time.time())),True,120);children=re.findall(r'<loc>(.*?)</loc>',sraw.decode('utf-8','replace'),re.I);allurls=[];print('SITEMAP_INDEX',ss,json.dumps(children,ensure_ascii=False))
for child in children:
 cs,cr,_,_=get(child+'?t='+str(int(time.time())),True,120);locs=re.findall(r'<loc>(.*?)</loc>',cr.decode('utf-8','replace'),re.I);allurls+=locs;print('CHILD',child,cs,len(locs))
pu=[u for u in set(allurls) if '/product/' in u];cu=[u for u in set(allurls) if '/product-category/' in u];print('SITEMAP_COUNTS',len(pu),len(cu))
if len(pu)!=46 or len(cu)!=20:errors.append('sitemap counts wrong')
for i in ('62','68'):
 if vd.get('rows',{}).get(i,{}).get('url') in set(allurls):errors.append('incomplete product in sitemap '+i)
if any('/snapback-cap/' in u for u in allurls):errors.append('snapback in sitemap')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:errors.append('Home changed')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));rb='gramiss-product-data-retry-rollback-'+nonce+'.php';mp=json.dumps(baseline_manifest)
 rbphp="<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$m=json_decode(file_get_contents("+mp+"),true);file_put_contents($m['plugin_target'],base64_decode($m['plugin_content_b64']));foreach($m['products'] as $id=>$s){wp_update_post(wp_slash(['ID'=>(int)$id,'post_title'=>$s['title'],'post_name'=>$s['slug'],'post_content'=>$s['content']]));wp_set_post_terms((int)$id,array_map('intval',$s['terms']),'product_cat',false);if($s['robots_exists'])update_post_meta((int)$id,'rank_math_robots',$s['robots']);else delete_post_meta((int)$id,'rank_math_robots');if($s['auto_flag_exists'])update_post_meta((int)$id,'_gramiss_auto_noindex_incomplete',$s['auto_flag']);else delete_post_meta((int)$id,'_gramiss_auto_noindex_incomplete');delete_post_meta((int)$id,'_wp_old_slug');foreach($s['old_slugs'] as $os)add_post_meta((int)$id,'_wp_old_slug',$os,false);}foreach($m['media'] as $aid=>$s){if($s['alt_exists'])update_post_meta((int)$aid,'_wp_attachment_image_alt',$s['alt']);else delete_post_meta((int)$aid,'_wp_attachment_image_alt');}global $wpdb;$wpdb->delete($wpdb->postmeta,['meta_key'=>'_gramiss_auto_product_alt_value']);$wpdb->delete($wpdb->postmeta,['meta_key'=>'_gramiss_auto_product_alt_product']);if(class_exists('RankMath\\Sitemap\\Cache')){\\RankMath\\Sitemap\\Cache::invalidate_storage();}global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo 'ROLLED_BACK';"
 save(rb,rbphp);rs,rr,_,_=get('https://gramiss.ir/'+rb+'?t='+str(int(time.time())),True,240);print('ROLLBACK',rs,rr[:100]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS PRODUCT DATA QA FIXES V1 RETRY')
print('PLUGIN_SHA',plugin_sha,'PRODUCTS_IN_SITEMAP',len(pu),'CATEGORIES_IN_SITEMAP',len(cu))
print('REMAINING_MANUAL_DATA product 62/68 need price+variations; product 210 XL and product 344 L still have missing variation price; SKU generation intentionally untouched')
print('HOME SHA PRESERVED',home_sha)
