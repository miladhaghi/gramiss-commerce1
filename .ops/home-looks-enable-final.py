import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
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
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def get(u,follow=True,timeout=120):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissSEOIndexationV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 hs=[urllib.request.HTTPSHandler(context=ctx)]
 if not follow:hs.insert(0,NoRedirect())
 op=urllib.request.build_opener(*hs)
 try:
  with op.open(req,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def hval(h,n):
 for k,v in h.items():
  if k.lower()==n.lower():return v
 return ''
def robots(raw):
 t=raw.decode('utf-8','replace');head=t.split('</head>',1)[0].lower();m=re.findall(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)',head,re.I);return ','.join(m).lower()
front=read_theme('front-page.php');home_sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch; no write')
stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime());nonce=hashlib.sha256((stamp+home_sha).encode()).hexdigest()[:14]
# Phase 1: intentional Rank Math sitemap/indexation policy with exact rollback snapshot.
p='gramiss-seo-indexation-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
if(!function_exists('rank_math') || (bool)rank_math()->registration->invalid){http_response_code(409);echo wp_json_encode(['error'=>'Rank Math runtime unavailable']);exit;}
$sm_name='rank-math-options-sitemap';$ti_name='rank-math-options-titles';$old_sm=(array)get_option($sm_name,[]);$old_ti=(array)get_option($ti_name,[]);
$ids=[1,10,11,12,22,36,37,38];$old_meta=[];foreach($ids as $id){$old_meta[(string)$id]=['exists'=>metadata_exists('post',$id,'rank_math_robots'),'value'=>get_post_meta($id,'rank_math_robots',true)];}
$manifest=['created_at'=>gmdate('c'),'sitemap_option_name'=>$sm_name,'titles_option_name'=>$ti_name,'old_sitemap'=>$old_sm,'old_titles'=>$old_ti,'old_post_robots'=>$old_meta];$mp=WP_CONTENT_DIR.'/gramiss-seo-indexation-v1-'.gmdate('Ymd-His').'.json';file_put_contents($mp,wp_json_encode($manifest,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT));
$sm=$old_sm;$sm['authors_sitemap']='off';$sm['pt_post_sitemap']='off';$sm['pt_page_sitemap']='on';$sm['pt_attachment_sitemap']='off';$sm['pt_product_sitemap']='on';$sm['tax_category_sitemap']='off';$sm['tax_post_tag_sitemap']='off';$sm['tax_post_format_sitemap']='off';$sm['tax_product_cat_sitemap']='on';$sm['tax_pa_color_sitemap']='off';$sm['tax_pa_57-7cm_sitemap']='off';$sm['tax_pa_58-7cm_sitemap']='off';$sm['include_images']='on';$sm['include_featured_image']='on';
$ti=$old_ti;$ti['tax_product_cat_title']='%term% %sep% %sitename%';$ti['tax_product_cat_description']='%term_description%';$ti['tax_product_cat_robots']=['index'];$ti['tax_product_cat_custom_robots']='off';$ti['tax_product_cat_add_meta_box']='on';foreach(['pa_color','pa_57-7cm','pa_58-7cm'] as $tax){$ti['tax_'.$tax.'_robots']=['noindex'];$ti['tax_'.$tax.'_custom_robots']='on';$ti['tax_'.$tax.'_add_meta_box']='off';}
update_option($sm_name,$sm,false);update_option($ti_name,$ti,false);foreach($ids as $id)update_post_meta($id,'rank_math_robots',['noindex','follow']);
do_action('rank_math/sitemap/flush_cache');global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');
echo wp_json_encode(['ok'=>true,'manifest'=>$mp,'sitemap'=>['pt_post_sitemap'=>$sm['pt_post_sitemap'],'pt_page_sitemap'=>$sm['pt_page_sitemap'],'pt_product_sitemap'=>$sm['pt_product_sitemap'],'tax_category_sitemap'=>$sm['tax_category_sitemap'],'tax_product_cat_sitemap'=>$sm['tax_product_cat_sitemap'],'authors_sitemap'=>$sm['authors_sitemap'],'include_featured_image'=>$sm['include_featured_image']],'noindex_ids'=>$ids],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(p,php);s,b,_,_=get('https://gramiss.ir/'+p+'?t='+str(int(time.time())),True,180);print('WRITE',s,b.decode('utf-8','replace'))
if s!=200:raise SystemExit('ABORT indexation write failed')
data=json.loads(b.decode('utf-8','replace'));manifest=data['manifest'];time.sleep(2);errors=[]
# Verify sitemap index + every child.
st,raw,final,_=get('https://gramiss.ir/sitemap_index.xml?t='+str(int(time.time())),True,120);txt=raw.decode('utf-8','replace');children=re.findall(r'<loc>(.*?)</loc>',txt,re.I);print('INDEX',st,final,json.dumps(children,ensure_ascii=False))
if st!=200 or '<sitemapindex' not in txt.lower():errors.append('sitemap index unavailable')
names=[u.rsplit('/',1)[-1] for u in children]
for forbidden in ('post-sitemap.xml','category-sitemap.xml','author-sitemap.xml'):
 if forbidden in names:errors.append('forbidden child '+forbidden)
if not any('product-sitemap' in x for x in names):errors.append('product sitemap missing')
if not any('page-sitemap' in x for x in names):errors.append('page sitemap missing')
if not any('product_cat-sitemap' in x for x in names):errors.append('product_cat sitemap missing')
all_urls=[]
for child in children:
 cs,cr,cu,_=get(child+'?t='+str(int(time.time())),True,120);ct=cr.decode('utf-8','replace');locs=re.findall(r'<loc>(.*?)</loc>',ct,re.I);all_urls+=locs;print('CHILD',child,'STATUS',cs,'COUNT',len(locs))
 if cs!=200:errors.append('child non-200 '+child)
uniq=set(all_urls);prod=[u for u in uniq if '/product/' in u];pcat=[u for u in uniq if '/product-category/' in u];print('COUNTS','UNIQUE',len(uniq),'PRODUCTS',len(prod),'PRODUCT_CATS',len(pcat))
if len(prod)!=48:errors.append('published product sitemap count !=48')
if len(pcat)!=21:errors.append('active product category sitemap count !=21')
for bad in ['/cart/','/checkout/','/my-account/','/wishlist/','/compare/','/track-order/','سلام-دنیا','%d8%b3%d9%84%d8%a7%d9%85-%d8%af%d9%86%db%8c%d8%a7','/category/','/color/','/57-7cm/','/58-7cm/']:
 if any(bad.lower() in u.lower() for u in uniq):errors.append('unwanted sitemap URL '+bad)
if 'https://gramiss.ir/' not in uniq:errors.append('home missing from sitemap')
if 'https://gramiss.ir/shop/' not in uniq:errors.append('shop missing from sitemap')
# Verify noindex utilities and attribute archives.
checks={'cart':'https://gramiss.ir/cart/','checkout':'https://gramiss.ir/checkout/','account':'https://gramiss.ir/my-account/','wishlist':'https://gramiss.ir/wishlist/','compare':'https://gramiss.ir/compare/','track':'https://gramiss.ir/track-order/','blog':'https://gramiss.ir/%D9%88%D8%A8%D9%84%D8%A7%DA%AF/','color':'https://gramiss.ir/color/navy/','cap57':'https://gramiss.ir/57-7cm/57-7cm/','cap58':'https://gramiss.ir/58-7cm/58-7cm/'}
for label,u in checks.items():
 cs,cr,cu,_=get(u,True,120);rb=robots(cr);print('ROBOTS_CHECK',label,cs,cu,rb)
 if 'noindex' not in rb:errors.append(label+' missing noindex')
# Money pages/categories stay indexable and canonical.
for label,u in {'shop':'https://gramiss.ir/shop/','product':'https://gramiss.ir/product/%D8%AA%DB%8C%D8%B4%D8%B1%D8%AA-%D8%A8%D8%A7%DA%A9%D8%B3-%D8%B7%D8%B1%D8%AD-%D9%85%D8%B3%DB%8C%D8%AD/','category':'https://gramiss.ir/product-category/tshirt/'}.items():
 cs,cr,cu,_=get(u,True,120);head=cr.decode('utf-8','replace').split('</head>',1)[0];rb=robots(cr);cans=re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',head,re.I);print('MONEY',label,cs,rb,json.dumps(cans,ensure_ascii=False))
 if cs!=200 or 'noindex' in rb or len(cans)!=1:errors.append(label+' index/canonical failed')
# robots points to Rank Math sitemap.
rs,rr,rf,_=get('https://gramiss.ir/robots.txt?t='+str(int(time.time())),True,90);rbody=rr.decode('utf-8','replace');print('ROBOTS_TXT',rs,rbody.replace('\n',' | ')[:1000])
if rs!=200 or 'Sitemap: https://gramiss.ir/sitemap_index.xml' not in rbody:errors.append('robots sitemap directive wrong')
# Legacy redirect and Home invariant.
old='https://gramiss.ir/?product='+urllib.parse.quote('تیشرت-باکس-طرح-مسیح',safe='-');ls,_,_,lh=get(old,False,60);loc=hval(lh,'Location');print('LEGACY',ls,loc)
if ls!=301 or '/product/' not in loc:errors.append('legacy redirect broken')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:errors.append('Home changed')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));rb='gramiss-seo-index-rollback-'+nonce+'.php';mp=json.dumps(manifest)
 rbphp="<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$m=json_decode(file_get_contents("+mp+"),true);update_option($m['sitemap_option_name'],$m['old_sitemap'],false);update_option($m['titles_option_name'],$m['old_titles'],false);foreach($m['old_post_robots'] as $id=>$r){if(!$r['exists'])delete_post_meta((int)$id,'rank_math_robots');else update_post_meta((int)$id,'rank_math_robots',$r['value']);}do_action('rank_math/sitemap/flush_cache');global $wp_rewrite;if($wp_rewrite)$wp_rewrite->flush_rules(false);do_action('litespeed_purge_all');echo 'ROLLED_BACK';"
 save(rb,rbphp);bs,bb,_,_=get('https://gramiss.ir/'+rb+'?t='+str(int(time.time())),True,180);print('ROLLBACK',bs,bb[:120]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS SEO SITEMAP + INDEXATION V1')
print('PRODUCTS',len(prod),'PRODUCT_CATEGORIES',len(pcat),'TOTAL_UNIQUE',len(uniq))
print('HOME SHA PRESERVED',home_sha)
