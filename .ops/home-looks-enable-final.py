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
 req=urllib.request.Request(u,headers={'User-Agent':'GramissCategoryMetadataV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 try:
  with urllib.request.urlopen(req,context=ctx,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def head_info(raw):
 t=raw.decode('utf-8','replace');h=t.split('</head>',1)[0]
 def one(p):
  m=re.search(p,h,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
 return {'title':one(r'<title[^>]*>(.*?)</title>'),'description':one(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':one(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':one(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)'),'og_title':one(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)'),'og_description':one(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)')}
pages={
 '20':{'label':'home','url':'https://gramiss.ir/','title':'Gramiss | فروشگاه پوشاک و استایل مردانه','description':'در Gramiss مدل‌های تیشرت، شلوار، پیراهن، کلاه و کتونی مردانه را ببینید، دسته‌ها را بررسی کنید و انتخاب مناسب خودتان را پیدا کنید.'},
 '9':{'label':'shop','url':'https://gramiss.ir/shop/','title':'خرید پوشاک مردانه | فروشگاه Gramiss','description':'محصولات موجود Gramiss را در دسته‌های تیشرت، شلوار، پیراهن، کلاه و کتونی مردانه ببینید و مدل‌های مختلف را بررسی و انتخاب کنید.'}
}
categories={
 '16':{'url':'https://gramiss.ir/product-category/hat/fitted-cap/','title':'خرید کلاه فیت کپ مردانه | Gramiss','description':'مدل‌های کلاه فیت کپ مردانه در Gramiss را ببینید و طرح‌های موجود این دسته را برای انتخاب بهتر بررسی و مقایسه کنید.'},
 '21':{'url':'https://gramiss.ir/product-category/pants/','title':'خرید شلوار مردانه | Gramiss','description':'مدل‌های شلوار مردانه Gramiss را در دسته‌های جین، پارچه‌ای و کارگو ببینید و گزینه‌های موجود را برای انتخاب بهتر بررسی کنید.'},
 '22':{'url':'https://gramiss.ir/product-category/tshirt/','title':'خرید تیشرت مردانه | Gramiss','description':'مدل‌های تیشرت مردانه Gramiss را در دسته‌های چاپی، اورسایز، یقه‌گرد و یقه‌دار ببینید و گزینه‌های موجود را بررسی کنید.'},
 '23':{'url':'https://gramiss.ir/product-category/hat/','title':'خرید کلاه مردانه | Gramiss','description':'مدل‌های کلاه مردانه Gramiss، شامل فیت کپ و اسنپ‌بک، را ببینید و طرح‌های موجود را برای انتخاب بهتر بررسی کنید.'},
 '25':{'url':'https://gramiss.ir/product-category/shirt/','title':'خرید پیراهن مردانه | Gramiss','description':'مدل‌های پیراهن مردانه Gramiss را در دسته‌های اسپرت، آستین کوتاه، آستین بلند، لینن و پارچه سیلک ببینید و مقایسه کنید.'},
 '27':{'url':'https://gramiss.ir/product-category/sneakers/','title':'خرید کتونی مردانه | Gramiss','description':'مدل‌های کتونی مردانه Gramiss را در دسته‌های روزمره و پیاده‌روی ببینید و گزینه‌های موجود را برای انتخاب بهتر بررسی کنید.'},
 '31':{'url':'https://gramiss.ir/product-category/pants/jeans/','title':'خرید شلوار جین مردانه | Gramiss','description':'مدل‌های شلوار جین مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را از نظر مدل و طرح بررسی و انتخاب کنید.'},
 '32':{'url':'https://gramiss.ir/product-category/pants/fabric-pants/','title':'خرید شلوار پارچه‌ای مردانه | Gramiss','description':'مدل‌های شلوار پارچه‌ای مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب بهتر بررسی و مقایسه کنید.'},
 '35':{'url':'https://gramiss.ir/product-category/pants/cargo-pants/','title':'خرید شلوار کارگو مردانه | Gramiss','description':'مدل‌های شلوار کارگو مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را از نظر مدل و طرح بررسی کنید.'},
 '38':{'url':'https://gramiss.ir/product-category/tshirt/graphic-tshirt/','title':'خرید تیشرت چاپی مردانه | Gramiss','description':'مدل‌های تیشرت چاپی مردانه Gramiss را ببینید و طرح‌های موجود این دسته را برای انتخاب استایل موردنظر خود بررسی کنید.'},
 '39':{'url':'https://gramiss.ir/product-category/tshirt/oversized-tshirt/','title':'خرید تیشرت اورسایز مردانه | Gramiss','description':'مدل‌های تیشرت اورسایز مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را از نظر مدل و طرح بررسی کنید.'},
 '40':{'url':'https://gramiss.ir/product-category/tshirt/crewneck-tshirt/','title':'خرید تیشرت یقه‌گرد مردانه | Gramiss','description':'مدل‌های تیشرت یقه‌گرد مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب بهتر بررسی کنید.'},
 '41':{'url':'https://gramiss.ir/product-category/tshirt/polo-tshirt/','title':'خرید تیشرت یقه‌دار مردانه | Gramiss','description':'مدل‌های تیشرت یقه‌دار مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب خود بررسی کنید.'},
 '44':{'url':'https://gramiss.ir/product-category/hat/snapback-cap/','title':'خرید کلاه اسنپ‌بک مردانه | Gramiss','description':'مدل‌های کلاه اسنپ‌بک مردانه Gramiss را ببینید و طرح‌های موجود این دسته را برای انتخاب بهتر بررسی و مقایسه کنید.'},
 '55':{'url':'https://gramiss.ir/product-category/shirt/casual-shirt/','title':'خرید پیراهن اسپرت مردانه | Gramiss','description':'مدل‌های پیراهن اسپرت مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب استایل خود بررسی کنید.'},
 '56':{'url':'https://gramiss.ir/product-category/shirt/short-sleeve-shirt/','title':'خرید پیراهن آستین کوتاه مردانه | Gramiss','description':'مدل‌های پیراهن آستین کوتاه مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب بهتر بررسی کنید.'},
 '57':{'url':'https://gramiss.ir/product-category/shirt/long-sleeve-shirt/','title':'خرید پیراهن آستین بلند مردانه | Gramiss','description':'مدل‌های پیراهن آستین بلند مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب بهتر بررسی کنید.'},
 '59':{'url':'https://gramiss.ir/product-category/shirt/linen-shirt/','title':'خرید پیراهن لینن مردانه | Gramiss','description':'مدل‌های پیراهن لینن مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب خود بررسی و مقایسه کنید.'},
 '66':{'url':'https://gramiss.ir/product-category/sneakers/casual-sneakers/','title':'خرید کتونی روزمره مردانه | Gramiss','description':'مدل‌های کتونی روزمره مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب بهتر بررسی و مقایسه کنید.'},
 '68':{'url':'https://gramiss.ir/product-category/sneakers/walking-shoes/','title':'خرید کتونی پیاده‌روی مردانه | Gramiss','description':'مدل‌های کتونی پیاده‌روی مردانه Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب بهتر بررسی کنید.'},
 '217':{'url':'https://gramiss.ir/product-category/shirt/%d9%be%d8%a7%d8%b1%da%86%d9%87-%d8%b3%db%8c%d9%84%da%a9/','title':'خرید پیراهن پارچه سیلک | Gramiss','description':'مدل‌های پیراهن پارچه سیلک Gramiss را ببینید و گزینه‌های موجود این دسته را برای انتخاب بهتر بررسی و مقایسه کنید.'}
}
payload={'pages':pages,'categories':categories}
front=read_theme('front-page.php');home_sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch; no write')
stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime());nonce=hashlib.sha256((stamp+home_sha).encode()).hexdigest()[:14];enc=base64.b64encode(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode()).decode()
probe='gramiss-category-meta-write-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
if(!function_exists('rank_math') || (bool)rank_math()->registration->invalid){http_response_code(409);echo wp_json_encode(['error'=>'Rank Math unavailable']);exit;}
$data=json_decode(base64_decode('__PAYLOAD__'),true);$keys=['rank_math_title','rank_math_description'];$manifest=['created_at'=>gmdate('c'),'pages'=>[],'terms'=>[]];$conflicts=[];
foreach($data['pages'] as $id=>$row){foreach($keys as $k){$exists=metadata_exists('post',(int)$id,$k);$old=get_post_meta((int)$id,$k,true);$manifest['pages'][$id][$k]=['exists'=>$exists,'value'=>$old];if(trim((string)$old)!=='')$conflicts[]='page '.$id.' '.$k.' already populated';}}
foreach($data['categories'] as $id=>$row){foreach($keys as $k){$exists=metadata_exists('term',(int)$id,$k);$old=get_term_meta((int)$id,$k,true);$manifest['terms'][$id][$k]=['exists'=>$exists,'value'=>$old];if(trim((string)$old)!=='')$conflicts[]='term '.$id.' '.$k.' already populated';}}
if($conflicts){http_response_code(409);echo wp_json_encode(['error'=>'metadata baseline changed','conflicts'=>$conflicts],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);exit;}
$mp=WP_CONTENT_DIR.'/gramiss-category-metadata-v1-'.gmdate('Ymd-His').'.json';$manifest['payload']=$data;file_put_contents($mp,wp_json_encode($manifest,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT));
foreach($data['pages'] as $id=>$row){update_post_meta((int)$id,'rank_math_title',$row['title']);update_post_meta((int)$id,'rank_math_description',$row['description']);clean_post_cache((int)$id);}
foreach($data['categories'] as $id=>$row){update_term_meta((int)$id,'rank_math_title',$row['title']);update_term_meta((int)$id,'rank_math_description',$row['description']);clean_term_cache((int)$id,'product_cat');}
do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'manifest'=>$mp,'pages'=>count($data['pages']),'categories'=>count($data['categories'])],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''.replace('__PAYLOAD__',enc)
save(probe,php);s,b,_,_=get('https://gramiss.ir/'+probe+'?t='+str(int(time.time())),True,180);print('WRITE',s,b.decode('utf-8','replace'))
if s!=200:raise SystemExit('ABORT metadata write failed')
write=json.loads(b.decode('utf-8','replace'));manifest=write['manifest'];time.sleep(2);errors=[]
# Verify every public head exactly: title + description, one canonical, indexable.
for idv,row in pages.items():
 st,raw,final,_=get(row['url'],True,120);info=head_info(raw);print('VERIFY_PAGE',idv,json.dumps({'status':st,'final':final,**info},ensure_ascii=False,separators=(',',':')))
 if st!=200 or info['title']!=row['title'] or info['description']!=row['description'] or info['canonical']=='' or 'noindex' in info['robots'].lower():errors.append('page '+idv+' head mismatch')
 if info['og_title']!=row['title'] or info['og_description']!=row['description']:errors.append('page '+idv+' OG mismatch')
for idv,row in categories.items():
 st,raw,final,_=get(row['url'],True,120);info=head_info(raw);print('VERIFY_TERM',idv,json.dumps({'status':st,'final':final,**info},ensure_ascii=False,separators=(',',':')))
 if st!=200 or info['title']!=row['title'] or info['description']!=row['description'] or info['canonical']=='' or 'noindex' in info['robots'].lower():errors.append('term '+idv+' head mismatch')
 if info['og_title']!=row['title'] or info['og_description']!=row['description']:errors.append('term '+idv+' OG mismatch')
# Sitemap/indexation contract must remain intact.
st,raw,final,_=get('https://gramiss.ir/sitemap_index.xml?t='+str(int(time.time())),True,120);txt=raw.decode('utf-8','replace');children=re.findall(r'<loc>(.*?)</loc>',txt,re.I);print('SITEMAP_INDEX',st,json.dumps(children,ensure_ascii=False))
if st!=200 or len(children)!=3 or not any('product_cat-sitemap.xml' in x for x in children):errors.append('sitemap contract changed')
for label,u in [('cart','https://gramiss.ir/cart/'),('account','https://gramiss.ir/my-account/'),('blog','https://gramiss.ir/%D9%88%D8%A8%D9%84%D8%A7%DA%AF/')]:
 st,raw,final,_=get(u,True,120);info=head_info(raw);print('UTILITY',label,st,info['robots']);
 if 'noindex' not in info['robots'].lower():errors.append(label+' lost noindex')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:errors.append('Home changed')
if errors:
 print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False));rb='gramiss-category-meta-rollback-'+nonce+'.php';mp_json=json.dumps(manifest)
 rbphp="<?php define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$m=json_decode(file_get_contents("+mp_json+"),true);foreach($m['pages'] as $id=>$ks){foreach($ks as $k=>$r){if(!$r['exists'])delete_post_meta((int)$id,$k);else update_post_meta((int)$id,$k,$r['value']);}clean_post_cache((int)$id);}foreach($m['terms'] as $id=>$ks){foreach($ks as $k=>$r){if(!$r['exists'])delete_term_meta((int)$id,$k);else update_term_meta((int)$id,$k,$r['value']);}clean_term_cache((int)$id,'product_cat');}do_action('litespeed_purge_all');echo 'ROLLED_BACK';"
 save(rb,rbphp);rs,rbody,_,_=get('https://gramiss.ir/'+rb+'?t='+str(int(time.time())),True,180);print('ROLLBACK',rs,rbody[:120]);raise SystemExit('ROLLED BACK: '+'; '.join(errors))
print('PASS CATEGORY METADATA V1')
print('PAGES',len(pages),'CATEGORIES',len(categories))
print('HOME SHA PRESERVED',home_sha)
