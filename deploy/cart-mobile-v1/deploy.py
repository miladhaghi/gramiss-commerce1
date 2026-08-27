import hashlib, json, os, re, ssl, subprocess, time, urllib.parse, urllib.request
from pathlib import Path
host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']; theme=os.environ['THEME_ROOT'].strip('/'); public='public_html'
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime()); version='20260827-1'
css_rel='assets/css/cart-mobile-v1.css'; js_rel='assets/js/cart-mobile-v1.js'
css_path=Path('deploy/cart-mobile-v1/cart-mobile-v1.css'); js_path=Path('deploy/cart-mobile-v1/cart-mobile-v1.js')
css=css_path.read_text(encoding='utf-8'); js=js_path.read_text(encoding='utf-8')
if 'GRAMISS_CART_MOBILE_V1' not in css or 'GRAMISS_CART_MOBILE_V1' not in js: raise SystemExit('ABORT: cart V1 markers missing')
subprocess.run(['node','--check',str(js_path)],check=True)
css_sha=hashlib.sha256(css.encode()).hexdigest(); js_sha=hashlib.sha256(js.encode()).hexdigest(); print('CANDIDATE CSS',len(css.encode()),css_sha); print('CANDIDATE JS',len(js.encode()),js_sha)
def call(fn,params,post=False):
    url=f'https://{host}:2083/execute/Fileman/{fn}'; enc=urllib.parse.urlencode(params).encode(); last=None
    for attempt in range(1,6):
        try:
            req=urllib.request.Request(url if post else url+'?'+enc.decode(),data=enc if post else None,method='POST' if post else 'GET'); req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as r: payload=json.loads(r.read().decode('utf-8','replace'))
            result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
            if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last=exc; print(f'Attempt {attempt}/5 {fn}: {exc}'); time.sleep(attempt*2 if attempt<5 else 0)
    raise last
def read_at(root,rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=root if not parent else root+'/'+parent
    data=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for k in ('content','file_content','data'):
            if isinstance(data.get(k),str): return data[k]
    if isinstance(data,str): return data
    raise RuntimeError('Cannot read '+rel)
def write_at(root,rel,content):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=root if not parent else root+'/'+parent
    call('save_file_content',{'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def public_get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 GramissCartMobile/1','Cache-Control':'no-cache','Pragma':'no-cache','Accept':'*/*'})
    with urllib.request.urlopen(req,context=ctx,timeout=90) as r:return r.status,r.read()
header=read_at(theme,'header.php'); original=header
pdp_start='<!-- GRAMISS PDP MOBILE UX V1 START -->'; pdp_end='<!-- GRAMISS PDP MOBILE UX V1 END -->'
if pdp_start not in header or pdp_end not in header: raise SystemExit('ABORT: PDP mobile block markers missing')
pdp_clean='''<!-- GRAMISS PDP MOBILE UX V1 START -->
<?php if ( function_exists( 'is_product' ) && is_product() ) : ?>
<link id="gramiss-pdp-mobile-v1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/product-mobile-v1.css?v=20260827-1' ); ?>">
<script id="gramiss-pdp-mobile-v1-js" defer src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/product-mobile-v1.js?v=20260827-1' ); ?>"></script>
<link id="gramiss-pdp-mobile-v1-1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/product-mobile-v1-1.css?v=20260827-2' ); ?>">
<link id="gramiss-pdp-mobile-v1-2-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/product-mobile-v1-2.css?v=20260827-3' ); ?>">
<script id="gramiss-pdp-mobile-v1-2-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/product-mobile-v1-2.js?v=20260827-3' ); ?>" defer></script>
<link id="gramiss-pdp-mobile-v1-3-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/product-mobile-v1-3.css?v=20260827-3' ); ?>">
<script id="gramiss-pdp-mobile-v1-3-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/product-mobile-v1-3.js?v=20260827-3' ); ?>" defer></script>
<link id="gramiss-pdp-mobile-v1-4-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/product-mobile-v1-4.css?v=20260827-5' ); ?>">
<script id="gramiss-pdp-mobile-v1-4-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/product-mobile-v1-4.js?v=20260827-5' ); ?>" defer></script>
<?php endif; ?>
<!-- GRAMISS PDP MOBILE UX V1 END -->'''
pattern=re.escape(pdp_start)+r'.*?'+re.escape(pdp_end)
header,n=re.subn(pattern,pdp_clean,header,count=1,flags=re.S)
if n!=1: raise SystemExit('ABORT: could not normalize PDP mobile block')
cart_start='<!-- GRAMISS CART MOBILE V1 START -->'; cart_end='<!-- GRAMISS CART MOBILE V1 END -->'
cart_block=f'''<!-- GRAMISS CART MOBILE V1 START -->
<?php if ( function_exists( 'is_cart' ) && is_cart() ) : ?>
<link id="gramiss-cart-mobile-v1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/{css_rel}?v={version}' ); ?>">
<script id="gramiss-cart-mobile-v1-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/{js_rel}?v={version}' ); ?>" defer></script>
<?php endif; ?>
<!-- GRAMISS CART MOBILE V1 END -->'''
if cart_start in header and cart_end in header:
    header,n2=re.subn(re.escape(cart_start)+r'.*?'+re.escape(cart_end),cart_block,header,count=1,flags=re.S)
    if n2!=1: raise SystemExit('ABORT: cart block replacement failed')
else:
    header=header.replace('</head>',cart_block+'\n</head>',1)
if '</head>' not in header: raise SystemExit('ABORT: header end missing')
write_at(theme,'header.php.bak-cart-mobile-v1-'+stamp,original); print('BACKUP header.php.bak-cart-mobile-v1-'+stamp)
for rel in (css_rel,js_rel):
    try: old=read_at(theme,rel); write_at(theme,rel+'.bak-'+stamp,old); print('BACKUP '+rel+'.bak-'+stamp)
    except Exception: pass
write_at(theme,css_rel,css); write_at(theme,js_rel,js); write_at(theme,'header.php',header)
def rollback(reason):
    write_at(theme,'header.php',original); raise SystemExit('ROLLED BACK HEADER: '+reason)
live_h=read_at(theme,'header.php'); live_css=read_at(theme,css_rel); live_js=read_at(theme,js_rel)
checks={
 'cart css once':live_h.count('gramiss-cart-mobile-v1-css')==1,
 'cart js once':live_h.count('gramiss-cart-mobile-v1-js')==1,
 'cart guarded':"function_exists( 'is_cart' ) && is_cart()" in live_h,
 'pdp block once':live_h.count(pdp_start)==1 and live_h.count(pdp_end)==1,
 'pdp malformed css gone':'product-mobile-v1-4.css?v=20260827-5\' ); ?>">">' not in live_h,
 'pdp malformed js gone':'</script>" defer></script>' not in live_h,
 'pdp guarded':"function_exists( 'is_product' ) && is_product()" in live_h,
 'css exact':hashlib.sha256(live_css.encode()).hexdigest()==css_sha,
 'js exact':hashlib.sha256(live_js.encode()).hexdigest()==js_sha,
 'mobile guard':'@media (max-width:760px)' in live_css,
}
for label,ok in checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(checks.values()): rollback('live verification failed')
purge='gramiss-purge-cart-mobile-v1-'+stamp+'.php'; purge_php="<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
write_at(public,purge,purge_php); st,b=public_get('https://gramiss.ir/'+purge+'?t='+str(int(time.time()))); print('PURGE',st,b.decode('utf-8','replace')[:30])
nonce=str(int(time.time())); st,b=public_get('https://gramiss.ir/?page_id=1&g1_cart_v1='+nonce); cart_html=b.decode('utf-8','replace')
public_checks={
 'cart page 200':st==200,
 'cart css ref':f'{css_rel}?v={version}' in cart_html,
 'cart js ref':f'{js_rel}?v={version}' in cart_html,
 'raw malformed fragment absent':'">">' not in cart_html and 'defer></script>"' not in cart_html,
}
for label,ok in public_checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(public_checks.values()): rollback('public cart verification failed')
for rel,sha,marker in ((css_rel,css_sha,b'GRAMISS_CART_MOBILE_V1'),(js_rel,js_sha,b'GRAMISS_CART_MOBILE_V1')):
    st,b=public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/'+rel+'?v='+nonce); got=hashlib.sha256(b).hexdigest(); ok=st==200 and got==sha and marker in b; print(('PASS' if ok else 'FAIL')+': public '+rel+' bytes='+str(len(b))+' sha='+got)
    if not ok: rollback('public asset verification failed '+rel)
st,b=public_get('https://gramiss.ir/?p=392&g1_product_safety_cart_v1='+nonce); product_html=b.decode('utf-8','replace')
product_ok=st==200 and 'product-mobile-v1-4.css?v=20260827-5' in product_html and 'product-mobile-v1-4.js?v=20260827-5' in product_html and f'{css_rel}?v={version}' not in product_html
print(('PASS' if product_ok else 'FAIL')+': PDP assets preserved and Cart assets isolated')
if not product_ok: rollback('PDP safety verification failed')
st,b=public_get('https://gramiss.ir/?g1_home_safety_cart_v1='+nonce); home=b.decode('utf-8','replace'); home_ok=st==200 and 'g1-floating-hero' in home and 'data-g1-looks' in home and f'{css_rel}?v={version}' not in home
print(('PASS' if home_ok else 'FAIL')+': Home/Looks untouched')
if not home_ok: rollback('Home safety verification failed')
print('LIVE GRAMISS CART MOBILE V1 DEPLOYED')
