import hashlib,html,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context();manifest='/home/gramissi/public_html/wp-content/gramiss-product-seo-foundation-v1-20260831-101728.json';expected_plugin_sha='a719f2d27d4d6632b520df9d056dd74458343d36dc333d1f0a9b582ad3a426f1'
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
 req=urllib.request.Request(u,headers={'User-Agent':'GramissProductSEOVerify/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 try:
  with urllib.request.urlopen(req,context=ctx,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
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
def rollback(reason):
 print('VERIFY_ERRORS',json.dumps(reason,ensure_ascii=False));name='gramiss-product-seo-rollback-verify.php';mp=json.dumps(manifest)
 php="<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$m=json_decode(file_get_contents("+mp+"),true);if(!$m){http_response_code(500);echo 'MANIFEST_MISSING';exit;}update_option($m['titles_option_name'],$m['old_titles'],false);foreach($m['attachment_alts'] as $a)update_post_meta((int)$a['attachment_id'],'_wp_attachment_image_alt',$a['old_alt']);if(isset($m['plugin_target'])&&file_exists($m['plugin_target']))@unlink($m['plugin_target']);do_action('litespeed_purge_all');echo 'ROLLED_BACK';"
 save(name,php);s,b,_,_=get('https://gramiss.ir/'+name+'?t='+str(int(time.time())),180);print('ROLLBACK',s,b.decode('utf-8','replace'));raise SystemExit('ROLLED BACK: '+'; '.join(reason))
front=read_theme('front-page.php');sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:rollback(['Home mismatch before verify'])
nonce=hashlib.sha256((str(time.time())+sha).encode()).hexdigest()[:14];probe='gramiss-product-seo-postverify-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$ti=(array)get_option('rank-math-options-titles',[]);$target=WPMU_PLUGIN_DIR.'/gramiss-product-seo-foundation.php';$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'fields'=>'ids','orderby'=>'ID','order'=>'ASC']);$missing=[];$rows=[];$gallery=0;$sku_empty=0;$price_empty=[];foreach($ids as $id){$p=wc_get_product($id);if(!$p)continue;if($p->get_sku()==='')$sku_empty++;if($p->get_price()==='')$price_empty[]=(int)$id;$fid=(int)$p->get_image_id();if($fid&&trim((string)get_post_meta($fid,'_wp_attachment_image_alt',true))==='')$missing[]=$fid;foreach($p->get_gallery_image_ids() as $gid){$gallery++;if(trim((string)get_post_meta($gid,'_wp_attachment_image_alt',true))==='')$missing[]=(int)$gid;}$rows[]=['id'=>(int)$id,'name'=>$p->get_name(),'url'=>get_permalink($id),'price'=>$p->get_price(),'currency'=>get_woocommerce_currency()];}echo wp_json_encode(['rank_math_invalid'=>function_exists('rank_math')?(bool)rank_math()->registration->invalid:null,'products'=>count($rows),'gallery_images'=>$gallery,'missing_alt_ids'=>array_values(array_unique($missing)),'sku_empty'=>$sku_empty,'price_empty_ids'=>$price_empty,'pt_product_title'=>$ti['pt_product_title']??null,'knowledgegraph_type'=>$ti['knowledgegraph_type']??null,'plugin_exists'=>file_exists($target),'plugin_sha256'=>file_exists($target)?hash_file('sha256',$target):null,'rows'=>$rows],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(probe,php);ps,pb,_,_=get('https://gramiss.ir/'+probe+'?t='+str(int(time.time())),180);print('PROBE',ps,'BYTES',len(pb));errors=[]
if ps!=200:rollback(['post-deploy probe failed'])
data=json.loads(pb.decode('utf-8','replace'));print('STATE',json.dumps({k:v for k,v in data.items() if k!='rows'},ensure_ascii=False,separators=(',',':')))
if data.get('rank_math_invalid'):errors.append('Rank Math invalid')
if data.get('pt_product_title')!='خرید %title% %sep% %sitename%':errors.append('product title template mismatch')
if data.get('knowledgegraph_type')!='company':errors.append('knowledgegraph_type mismatch')
if not data.get('plugin_exists') or data.get('plugin_sha256')!=expected_plugin_sha:errors.append('MU plugin mismatch')
if data.get('missing_alt_ids'):errors.append('product images still missing ALT')
rows=data.get('rows',[]);byid={r['id']:r for r in rows};sample_ids=[49,97,222,296,403];sample=[byid[i] for i in sample_ids if i in byid]
if len(sample)<3:sample=rows[:5]
for r in sample:
 s,raw,final,_=get(r['url'],120);h=head_info(raw);sc=schema_info(raw);print('LIVE_PRODUCT',r['id'],json.dumps({'status':s,'final':final,'head':h,'schema':sc,'wc_price':r['price'],'wc_currency':r['currency']},ensure_ascii=False,separators=(',',':')))
 if s!=200:errors.append(f"product {r['id']} non-200")
 if not h['title'].startswith('خرید '):errors.append(f"product {r['id']} title template missing")
 if not h['description']:errors.append(f"product {r['id']} meta description empty")
 if not h['canonical']:errors.append(f"product {r['id']} canonical missing")
 if 'noindex' in h['robots'].lower():errors.append(f"product {r['id']} noindex")
 p=(sc.get('products') or [{}])[0]
 if r.get('price')!='':
  if p.get('currency')!='IRR':errors.append(f"product {r['id']} schema currency {p.get('currency')}")
  try:
   if abs(float(p.get('price'))-float(r['price'])*10)>0.01:errors.append(f"product {r['id']} schema price mismatch")
  except Exception:errors.append(f"product {r['id']} schema price unreadable")
hs,hraw,_,_=get('https://gramiss.ir/',120);hsc=schema_info(hraw);print('HOME_SCHEMA',hs,json.dumps(hsc,ensure_ascii=False,separators=(',',':')))
if hs!=200 or 'Organization' not in hsc.get('types',[]):errors.append('Home Organization schema missing')
ss,sraw,_,_=get('https://gramiss.ir/sitemap_index.xml?t='+str(int(time.time())),120);children=re.findall(r'<loc>(.*?)</loc>',sraw.decode('utf-8','replace'),re.I);print('SITEMAP_INDEX',ss,json.dumps(children,ensure_ascii=False));expected={'https://gramiss.ir/page-sitemap.xml','https://gramiss.ir/product-sitemap.xml','https://gramiss.ir/product_cat-sitemap.xml'}
if ss!=200 or set(children)!=expected:errors.append('sitemap structure changed')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:errors.append('Home changed during verify')
if errors:rollback(errors)
print('PASS PRODUCT SEO FOUNDATION V1 VERIFIED')
print('PRODUCTS',data.get('products'),'GALLERY',data.get('gallery_images'),'SKU_EMPTY',data.get('sku_empty'),'PRICE_EMPTY',json.dumps(data.get('price_empty_ids')))
print('HOME SHA PRESERVED',sha)
