import hashlib,html,json,os,re,ssl,time,urllib.parse,urllib.request
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
def get(u,timeout=120):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissProductSEOAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 with urllib.request.urlopen(req,context=ctx,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
def one(h,p):
 m=re.search(p,h,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def head_info(raw):
 t=raw.decode('utf-8','replace');h=t.split('</head>',1)[0]
 return {'title':one(h,r'<title[^>]*>(.*?)</title>'),'description':one(h,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':one(h,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':one(h,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)'),'og_title':one(h,r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)'),'og_description':one(h,r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)')}
def schema_info(raw):
 t=raw.decode('utf-8','replace');blocks=re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',t,re.I|re.S);types=[];products=[]
 def walk(x):
  if isinstance(x,dict):
   ty=x.get('@type');
   if isinstance(ty,str):types.append(ty)
   elif isinstance(ty,list):types.extend(str(v) for v in ty)
   isprod=(ty=='Product') or (isinstance(ty,list) and 'Product' in ty)
   if isprod:
    off=x.get('offers');offers=off if isinstance(off,dict) else (off[0] if isinstance(off,list) and off and isinstance(off[0],dict) else {})
    products.append({'name':x.get('name'),'sku':x.get('sku'),'image':x.get('image'),'price':offers.get('price') or offers.get('lowPrice'),'currency':offers.get('priceCurrency'),'availability':offers.get('availability'),'url':x.get('url')})
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 for b in blocks:
  try:walk(json.loads(html.unescape(b.strip())))
  except Exception:pass
 return {'types':sorted(set(types)),'products':products[:2],'jsonld_blocks':len(blocks)}
front=read_theme('front-page.php');sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-product-seo-audit-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
if(!function_exists('wc_get_product')){http_response_code(409);echo wp_json_encode(['error'=>'WooCommerce unavailable']);exit;}
function txtlen($v){return mb_strlen(trim(wp_strip_all_tags((string)$v)));}
function media_row($id){if(!$id)return null;$m=wp_get_attachment_metadata($id);return ['id'=>(int)$id,'alt'=>(string)get_post_meta($id,'_wp_attachment_image_alt',true),'title'=>(string)get_the_title($id),'file'=>basename((string)get_attached_file($id)),'width'=>(int)($m['width']??0),'height'=>(int)($m['height']??0)];}
$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);$rows=[];$stats=['products'=>count($ids),'custom_title'=>0,'custom_description'=>0,'custom_canonical'=>0,'custom_robots'=>0,'short_empty'=>0,'content_empty'=>0,'featured_missing'=>0,'featured_alt_empty'=>0,'gallery_images'=>0,'gallery_alt_empty'=>0,'sku_empty'=>0,'price_empty'=>0];
foreach($ids as $id){$p=wc_get_product($id);if(!$p)continue;$meta=[];foreach(['rank_math_title','rank_math_description','rank_math_canonical_url','rank_math_robots','rank_math_focus_keyword'] as $k)$meta[$k]=get_post_meta($id,$k,true);if($meta['rank_math_title']!=='')$stats['custom_title']++;if($meta['rank_math_description']!=='')$stats['custom_description']++;if($meta['rank_math_canonical_url']!=='')$stats['custom_canonical']++;if($meta['rank_math_robots']!=='')$stats['custom_robots']++;
$short=$p->get_short_description();$full=$p->get_description();if(txtlen($short)===0)$stats['short_empty']++;if(txtlen($full)===0)$stats['content_empty']++;$fid=$p->get_image_id();$f=media_row($fid);if(!$fid)$stats['featured_missing']++;elseif(trim((string)$f['alt'])==='')$stats['featured_alt_empty']++;$gallery=[];foreach($p->get_gallery_image_ids() as $gid){$g=media_row($gid);$gallery[]=$g;$stats['gallery_images']++;if(trim((string)$g['alt'])==='')$stats['gallery_alt_empty']++;}
$sku=$p->get_sku();$price=$p->get_price();if($sku==='')$stats['sku_empty']++;if($price==='')$stats['price_empty']++;$cats=[];foreach(wp_get_post_terms($id,'product_cat') as $t)$cats[]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug];$rows[]=['id'=>(int)$id,'name'=>$p->get_name(),'slug'=>get_post_field('post_name',$id),'url'=>get_permalink($id),'modified'=>get_post_modified_time('c',true,$id),'type'=>$p->get_type(),'sku'=>$sku,'price'=>$price,'stock_status'=>$p->get_stock_status(),'short_len'=>txtlen($short),'content_len'=>txtlen($full),'meta'=>$meta,'categories'=>$cats,'featured'=>$f,'gallery'=>$gallery];}
$opts=(array)get_option('rank-math-options-titles',[]);$selected=[];foreach(['pt_product_title','pt_product_description','pt_product_robots','pt_product_custom_robots','pt_product_default_rich_snippet','pt_product_default_snippet_name','pt_product_default_snippet_desc','pt_product_primary_taxonomy'] as $k)$selected[$k]=$opts[$k]??null;
$general=(array)get_option('rank-math-options-general',[]);$settings=['titles'=>$selected,'remove_shop_snippet_data'=>$general['remove_shop_snippet_data']??null,'wc_remove_generator'=>$general['wc_remove_generator']??null];
echo wp_json_encode(['rank_math_invalid'=>function_exists('rank_math')?(bool)rank_math()->registration->invalid:null,'stats'=>$stats,'settings'=>$settings,'products'=>$rows],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,u,_=get('https://gramiss.ir/'+name+'?t='+st,180);print('PROBE',s,u,'BYTES',len(b));data=json.loads(b.decode('utf-8','replace'));print('RANK_MATH_INVALID',data.get('rank_math_invalid'));print('STATS',json.dumps(data.get('stats',{}),ensure_ascii=False,separators=(',',':')));print('SETTINGS',json.dumps(data.get('settings',{}),ensure_ascii=False,separators=(',',':')))
rows=data.get('products',[])
for r in rows:
 issues=[]
 if not r.get('meta',{}).get('rank_math_title'):issues.append('no_custom_title')
 if not r.get('meta',{}).get('rank_math_description'):issues.append('no_custom_desc')
 if r.get('short_len',0)==0:issues.append('short_empty')
 if r.get('content_len',0)==0:issues.append('content_empty')
 if not r.get('featured'):issues.append('no_featured')
 elif not str(r['featured'].get('alt','')).strip():issues.append('featured_alt_empty')
 if any(not str(g.get('alt','')).strip() for g in r.get('gallery',[])):issues.append('gallery_alt_empty')
 print('PRODUCT',r['id'],json.dumps({'name':r['name'],'url':r['url'],'type':r['type'],'sku':r['sku'],'price':r['price'],'stock':r['stock_status'],'short_len':r['short_len'],'content_len':r['content_len'],'cats':[c['name'] for c in r['categories']],'featured':r['featured'],'gallery_count':len(r['gallery']),'issues':issues},ensure_ascii=False,separators=(',',':')))
# Live head/schema on a balanced sample: first, last, and up to one product per top-level category.
sample=[];seen=set()
for r in rows:
 top=(r.get('categories') or [{}])[0].get('name','')
 if top and top not in seen:sample.append(r);seen.add(top)
if rows:
 for r in (rows[0],rows[-1]):
  if all(x['id']!=r['id'] for x in sample):sample.append(r)
for r in sample[:10]:
 ss,raw,final,_=get(r['url'],120);print('LIVE_PRODUCT',r['id'],json.dumps({'status':ss,'final':final,**head_info(raw),'schema':schema_info(raw)},ensure_ascii=False,separators=(',',':')))
# Sitemap remains intact.
ss,raw,final,_=get('https://gramiss.ir/sitemap_index.xml?t='+str(int(time.time())),120);children=re.findall(r'<loc>(.*?)</loc>',raw.decode('utf-8','replace'),re.I);print('SITEMAP_INDEX',ss,json.dumps(children,ensure_ascii=False))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY PRODUCT SEO AUDIT')
