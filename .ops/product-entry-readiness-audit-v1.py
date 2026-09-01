import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');HEALTHY=os.environ.get('HEALTHY_HOME_SHA','');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir'
EXPECTED_PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3';EXPECTED_PRODUCT_CAT_SHA='75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PROTECTED={'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7','template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d','assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0','assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
def safe(u):
 p=urllib.parse.urlsplit(u);return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def api(fn,p,post=False):
 u=f'https://{HOST}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();last=None
 for n in range(4):
  try:
   r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=CTX,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
   q=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
   return q.get('data')
  except Exception as exc:last=exc;print('API_RETRY',fn,n+1,exc);time.sleep(n+1)
 raise last
def theme(rel):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel);x=api('get_file_content',{'dir':ROOT if not d else ROOT+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(x,dict):
  for k in ('content','file_content','data'):
   if isinstance(x.get(k),str):return x[k]
 return x if isinstance(x,str) else ''
def save(n,c):return api('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u,timeout=150):
 u=safe(u);last=None
 for n in range(4):
  try:
   r=urllib.request.Request(u,headers={'User-Agent':'GramissProductEntryAuditV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});
   with urllib.request.urlopen(r,context=CTX,timeout=timeout) as z:return z.status,z.read(),z.geturl()
  except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
  except Exception as exc:last=exc;print('HTTP_RETRY',n+1,u,exc);time.sleep(n+1)
 raise last
def val(t,p):
 m=re.search(p,t,re.I|re.S);return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def head(raw):
 t=raw.decode('utf-8','replace').split('</head>',1)[0];return {'title':val(t,r'<title[^>]*>(.*?)</title>'),'description':val(t,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':val(t,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':val(t,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sitemap(path):
 s,b,_=get(BASE+'/'+path+'?t='+str(int(time.time())),120);return s,[x.replace('&amp;','&') for x in re.findall(r'<loc>(.*?)</loc>',b.decode('utf-8','replace'),re.I)]
protected={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED',json.dumps(protected,sort_keys=True))
for p,h in PROTECTED.items():
 if protected[p]!=h:raise SystemExit('ABORT protected drift '+p)
if HEALTHY and protected['front-page.php']!=HEALTHY:raise SystemExit('ABORT healthy home')
ps,purls=sitemap('product-sitemap.xml');pcs,pcurls=sitemap('product_cat-sitemap.xml');purls=sorted(purls);pcurls=sorted(pcurls);psha=hashlib.sha256('\n'.join(purls).encode()).hexdigest();pcsha=hashlib.sha256('\n'.join(pcurls).encode()).hexdigest();print('SITEMAP_BASELINE',ps,len(purls),psha,pcs,len(pcurls),pcsha)
if ps!=200 or len(purls)!=47 or psha!=EXPECTED_PRODUCT_SHA:raise SystemExit('ABORT product sitemap drift')
if pcs!=200 or len(pcurls)!=20 or pcsha!=EXPECTED_PRODUCT_CAT_SHA:raise SystemExit('ABORT product category sitemap drift')
nonce=hashlib.sha256((str(time.time())+protected['front-page.php']).encode()).hexdigest()[:14];name='gramiss-product-entry-readiness-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function gw($s){$s=trim(wp_strip_all_tags(strip_shortcodes((string)$s)));if($s==='')return 0;$a=preg_split('/\s+/u',$s,-1,PREG_SPLIT_NO_EMPTY);return is_array($a)?count($a):0;}
function gm($id,$k){$v=get_post_meta($id,$k,true);return is_array($v)?$v:(string)$v;}
function galt($id){return (string)get_post_meta($id,'_wp_attachment_image_alt',true);}
$o=[];$cnt=wp_count_posts('product');$o['counts']=['publish'=>(int)($cnt->publish??0),'draft'=>(int)($cnt->draft??0),'private'=>(int)($cnt->private??0),'pending'=>(int)($cnt->pending??0)];$o['permalink_structure']=get_option('permalink_structure');$o['woocommerce_permalinks']=get_option('woocommerce_permalinks');
$titles=get_option('rank-math-options-titles',[]);$sel=[];foreach((array)$titles as $k=>$v){if(strpos($k,'pt_product_')===0||strpos($k,'tax_product_cat_')===0)$sel[$k]=$v;}$o['rank_math_product_templates']=$sel;
$o['products']=[];$ids=get_posts(['post_type'=>'product','post_status'=>['publish','draft','private','pending'],'numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);foreach($ids as $id){$p=get_post($id);$wc=wc_get_product($id);if(!$wc)continue;$cats=wp_get_post_terms($id,'product_cat',['fields'=>'all']);$image_ids=[];$thumb=(int)get_post_thumbnail_id($id);if($thumb)$image_ids[]=$thumb;foreach((array)$wc->get_gallery_image_ids() as $iid)$image_ids[]=(int)$iid;$image_ids=array_values(array_unique(array_filter($image_ids)));$images=[];foreach($image_ids as $iid)$images[]=['id'=>$iid,'alt'=>galt($iid),'title'=>get_the_title($iid)];$attrs=[];foreach($wc->get_attributes() as $a){$vals=[];if($a->is_taxonomy()){$vals=wc_get_product_terms($id,$a->get_name(),['fields'=>'names']);}else{$vals=$a->get_options();}$attrs[]=['name'=>$a->get_name(),'taxonomy'=>$a->is_taxonomy(),'variation'=>$a->get_variation(),'visible'=>$a->get_visible(),'values'=>$vals];}$vars=[];if($wc->is_type('variable')){foreach($wc->get_children() as $vid){$v=wc_get_product($vid);if(!$v)continue;$vars[]=['id'=>(int)$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price(),'regular_price'=>$v->get_regular_price(),'sale_price'=>$v->get_sale_price(),'stock_status'=>$v->get_stock_status(),'stock_quantity'=>$v->get_stock_quantity(),'attributes'=>$v->get_attributes()];}}$o['products'][]=['id'=>(int)$id,'status'=>$p->post_status,'title'=>$p->post_title,'slug'=>$p->post_name,'url'=>$p->post_status==='publish'?get_permalink($id):null,'type'=>$wc->get_type(),'sku'=>$wc->get_sku(),'price'=>$wc->get_price(),'regular_price'=>$wc->get_regular_price(),'sale_price'=>$wc->get_sale_price(),'stock_status'=>$wc->get_stock_status(),'stock_quantity'=>$wc->get_stock_quantity(),'manage_stock'=>$wc->get_manage_stock(),'description_words'=>gw($p->post_content),'short_description_words'=>gw($p->post_excerpt),'featured_image'=>$thumb,'images'=>$images,'categories'=>array_map(fn($t)=>['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug],$cats),'attributes'=>$attrs,'variations'=>$vars,'seo'=>['title'=>gm($id,'rank_math_title'),'description'=>gm($id,'rank_math_description'),'canonical'=>gm($id,'rank_math_canonical_url'),'robots'=>gm($id,'rank_math_robots'),'focus'=>gm($id,'rank_math_focus_keyword'),'rich_snippet'=>gm($id,'rank_math_rich_snippet')]];}
$o['categories']=[];foreach(get_terms(['taxonomy'=>'product_cat','hide_empty'=>false]) as $t){$o['categories'][]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'parent'=>(int)$t->parent,'description_words'=>gw($t->description),'url'=>get_term_link($t),'seo'=>['title'=>(string)get_term_meta($t->term_id,'rank_math_title',true),'description'=>(string)get_term_meta($t->term_id,'rank_math_description',true),'robots'=>get_term_meta($t->term_id,'rank_math_robots',true)]];}
echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save(name,php);s,b,f=get(BASE+'/'+name+'?t='+str(int(time.time())),300);print('PROBE',s,f,'BYTES',len(b));
if s!=200:raise SystemExit('audit probe failed')
d=json.loads(b.decode('utf-8','replace'));products=d.get('products',[]);published=[p for p in products if p.get('status')=='publish'];drafts=[p for p in products if p.get('status')!='publish'];print('WP_COUNTS',json.dumps(d.get('counts'),ensure_ascii=False),'PERMALINK',d.get('permalink_structure'));print('RANK_MATH_PRODUCT_TEMPLATES',json.dumps(d.get('rank_math_product_templates'),ensure_ascii=False,separators=(',',':')))
summary={'published':len(published),'nonpublic':len(drafts),'missing_parent_sku':0,'missing_description':0,'missing_short_description':0,'missing_featured_image':0,'products_with_empty_alt':0,'empty_alt_images':0,'missing_seo_title':0,'missing_seo_description':0,'explicit_canonical':0,'variable_products':0,'variations':0,'variation_sku_missing':0,'variation_price_missing':0,'out_of_stock_variations':0,'no_category':0,'public_http_bad':0,'public_canonical_bad':0,'public_noindex':0,'public_product_schema_missing':0,'public_duplicate_product_schema':0,'sitemap_published_mismatch':0}
flags=[]
for p in published:
 if not p.get('sku'):summary['missing_parent_sku']+=1
 if p.get('description_words',0)==0:summary['missing_description']+=1
 if p.get('short_description_words',0)==0:summary['missing_short_description']+=1
 if not p.get('featured_image'):summary['missing_featured_image']+=1
 empty=[x for x in p.get('images',[]) if not str(x.get('alt','')).strip()];summary['empty_alt_images']+=len(empty);summary['products_with_empty_alt']+=1 if empty else 0
 seo=p.get('seo') or {};summary['missing_seo_title']+=0 if str(seo.get('title','')).strip() else 1;summary['missing_seo_description']+=0 if str(seo.get('description','')).strip() else 1;summary['explicit_canonical']+=1 if str(seo.get('canonical','')).strip() else 0
 if not p.get('categories'):summary['no_category']+=1
 if p.get('type')=='variable':summary['variable_products']+=1
 for v in p.get('variations',[]):
  summary['variations']+=1;summary['variation_sku_missing']+=0 if str(v.get('sku','')).strip() else 1;summary['variation_price_missing']+=0 if str(v.get('price','')).strip() else 1;summary['out_of_stock_variations']+=1 if v.get('stock_status')=='outofstock' else 0
 reasons=[]
 if not p.get('sku'):reasons.append('parent_sku')
 if p.get('description_words',0)==0:reasons.append('description')
 if p.get('short_description_words',0)==0:reasons.append('short_description')
 if empty:reasons.append('image_alt:'+str(len(empty)))
 if any(not str(v.get('sku','')).strip() for v in p.get('variations',[])):reasons.append('variation_sku')
 if any(not str(v.get('price','')).strip() for v in p.get('variations',[])):reasons.append('variation_price')
 if reasons:flags.append({'id':p['id'],'title':p['title'],'slug':p['slug'],'type':p['type'],'reasons':reasons})
# Public page verification for every published product.
sitemap_set={norm(u) for u in purls};published_set=set()
for p in published:
 u=p.get('url');published_set.add(norm(u));st,raw,final=get(u+'?t='+str(int(time.time())),150);txt=raw.decode('utf-8','replace');m=head(raw);robots=m.get('robots','').lower();types=re.findall(r'"@type"\s*:\s*"Product"',txt,re.I);print('PUBLIC_PRODUCT',p['id'],st,'CANON',m.get('canonical'),'ROBOTS',m.get('robots'),'PRODUCT_SCHEMA_COUNT',len(types))
 if st!=200:summary['public_http_bad']+=1
 if norm(m.get('canonical',''))!=norm(u):summary['public_canonical_bad']+=1
 if 'noindex' in robots or 'index' not in robots:summary['public_noindex']+=1
 if len(types)==0:summary['public_product_schema_missing']+=1
 if len(types)>1:summary['public_duplicate_product_schema']+=1
summary['sitemap_published_mismatch']=len(published_set.symmetric_difference(sitemap_set))
print('PRODUCT_READINESS_SUMMARY',json.dumps(summary,ensure_ascii=False,sort_keys=True))
for x in flags:print('PRODUCT_GAP',json.dumps(x,ensure_ascii=False,separators=(',',':')))
# Print anomaly candidates without mutating anything.
from collections import defaultdict
by_title=defaultdict(list)
for p in published:by_title[p['title'].strip()].append(p['id'])
for title,ids in by_title.items():
 if len(ids)>1:print('DUPLICATE_TITLE',json.dumps({'title':title,'ids':ids},ensure_ascii=False))
for c in d.get('categories',[]):
 if c.get('count',0)>0:print('ACTIVE_CATEGORY',json.dumps(c,ensure_ascii=False,separators=(',',':')))
print('NONPUBLIC_PRODUCTS',json.dumps([{'id':p['id'],'status':p['status'],'title':p['title']} for p in drafts],ensure_ascii=False,separators=(',',':')))
post={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_POST',json.dumps(post,sort_keys=True));
if post!=protected:raise SystemExit('ABORT protected changed during read-only audit')
print('PASS PRODUCT ENTRY READINESS AUDIT V1')