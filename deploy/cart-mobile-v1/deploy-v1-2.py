import hashlib, json, os, re, ssl, subprocess, time, urllib.parse, urllib.request
from pathlib import Path
host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']; theme=os.environ['THEME_ROOT'].strip('/'); public='public_html'
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime()); version='20260827-3'
files={
 'assets/css/cart-mobile-v1.css':Path('deploy/cart-mobile-v1/cart-mobile-v1.css'),
 'assets/js/cart-mobile-v1-bootstrap.js':Path('deploy/cart-mobile-v1/cart-mobile-v1-bootstrap.js'),
 'assets/js/cart-mobile-v1.js':Path('deploy/cart-mobile-v1/cart-mobile-v1.js'),
}
contents={rel:path.read_text(encoding='utf-8') for rel,path in files.items()}
if 'GRAMISS_CART_MOBILE_V1' not in contents['assets/css/cart-mobile-v1.css'] or 'GRAMISS_CART_MOBILE_V1' not in contents['assets/js/cart-mobile-v1.js'] or 'GRAMISS_CART_MOBILE_V1_BOOTSTRAP' not in contents['assets/js/cart-mobile-v1-bootstrap.js']: raise SystemExit('ABORT: Cart markers missing')
subprocess.run(['node','--check',str(files['assets/js/cart-mobile-v1-bootstrap.js'])],check=True); subprocess.run(['node','--check',str(files['assets/js/cart-mobile-v1.js'])],check=True)
shas={rel:hashlib.sha256(content.encode()).hexdigest() for rel,content in contents.items()}
for rel in contents: print('CANDIDATE',rel,len(contents[rel].encode()),shas[rel])
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
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 GramissCartMobile/1.2','Cache-Control':'no-cache','Pragma':'no-cache','Accept':'*/*'})
    with urllib.request.urlopen(req,context=ctx,timeout=90) as r:return r.status,r.read()
header=read_at(theme,'header.php'); original=header
pdp_start='<!-- GRAMISS PDP MOBILE UX V1 START -->'; pdp_end='<!-- GRAMISS PDP MOBILE UX V1 END -->'
if pdp_start not in header or pdp_end not in header: raise SystemExit('ABORT: PDP markers missing')
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
header,n=re.subn(re.escape(pdp_start)+r'.*?'+re.escape(pdp_end),pdp_clean,header,count=1,flags=re.S)
if n!=1: raise SystemExit('ABORT: PDP block repair failed')
cart_start='<!-- GRAMISS CART MOBILE V1 START -->'; cart_end='<!-- GRAMISS CART MOBILE V1 END -->'
cart_block=f'''<!-- GRAMISS CART MOBILE V1 START -->
<link id="gramiss-cart-mobile-v1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/cart-mobile-v1.css?v={version}' ); ?>" media="(max-width:760px)">
<script id="gramiss-cart-mobile-v1-bootstrap-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/cart-mobile-v1-bootstrap.js?v={version}' ); ?>" defer></script>
<script id="gramiss-cart-mobile-v1-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/cart-mobile-v1.js?v={version}' ); ?>" defer></script>
<!-- GRAMISS CART MOBILE V1 END -->'''
if cart_start in header and cart_end in header:
    header,n2=re.subn(re.escape(cart_start)+r'.*?'+re.escape(cart_end),cart_block,header,count=1,flags=re.S)
    if n2!=1: raise SystemExit('ABORT: Cart block replacement failed')
else: header=header.replace('</head>',cart_block+'\n</head>',1)
write_at(theme,'header.php.bak-cart-mobile-v1-2-'+stamp,original); print('BACKUP header.php.bak-cart-mobile-v1-2-'+stamp)
for rel,content in contents.items():
    try:
        old=read_at(theme,rel); write_at(theme,rel+'.bak-'+stamp,old); print('BACKUP '+rel+'.bak-'+stamp)
    except Exception: pass
    write_at(theme,rel,content)
write_at(theme,'header.php',header)
def rollback(reason):
    write_at(theme,'header.php',original); raise SystemExit('ROLLED BACK HEADER: '+reason)
live_h=read_at(theme,'header.php')
checks={
 'cart css once':live_h.count('gramiss-cart-mobile-v1-css')==1,
 'cart bootstrap once':live_h.count('gramiss-cart-mobile-v1-bootstrap-js')==1,
 'cart main once':live_h.count('gramiss-cart-mobile-v1-js')==1,
 'pdp block once':live_h.count(pdp_start)==1 and live_h.count(pdp_end)==1,
 'pdp malformed css gone':'">">' not in live_h[live_h.find(pdp_start):live_h.find(pdp_end)+len(pdp_end)],
 'pdp malformed js gone':'</script>" defer></script>' not in live_h,
 'pdp guarded':"function_exists( 'is_product' ) && is_product()" in live_h,
}
for rel in contents: checks['exact '+rel]=hashlib.sha256(read_at(theme,rel).encode()).hexdigest()==shas[rel]
for label,ok in checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(checks.values()): rollback('live verification failed')
purge='gramiss-purge-cart-mobile-v12-'+stamp+'.php'; purge_php="<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
write_at(public,purge,purge_php); st,b=public_get('https://gramiss.ir/'+purge+'?t='+str(int(time.time()))); print('PURGE',st,b.decode('utf-8','replace')[:30])
nonce=str(int(time.time()))
for label,url in [('cart','https://gramiss.ir/?page_id=1&g1_cart_v12='+nonce),('product','https://gramiss.ir/?p=392&g1_product_safety_cart_v12='+nonce),('home','https://gramiss.ir/?g1_home_safety_cart_v12='+nonce)]:
    st,b=public_get(url); html=b.decode('utf-8','replace')
    refs=all(f'{rel}?v={version}' in html for rel in contents)
    malformed='">">' in html or 'defer></script>"' in html
    base=st==200 and refs and not malformed
    if label=='product': base=base and 'product-mobile-v1-4.css?v=20260827-5' in html and 'product-mobile-v1-4.js?v=20260827-5' in html
    if label=='home': base=base and 'g1-floating-hero' in html and 'data-g1-looks' in html and 'product-mobile-v1-4.css' not in html
    print(('PASS' if base else 'FAIL')+': public '+label+' refs/safety')
    if not base: rollback('public '+label+' verification failed')
for rel,content in contents.items():
    st,b=public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/'+rel+'?v='+nonce); got=hashlib.sha256(b).hexdigest(); ok=st==200 and got==shas[rel]
    print(('PASS' if ok else 'FAIL')+': public '+rel+' bytes='+str(len(b))+' sha='+got)
    if not ok: rollback('public asset failed '+rel)
print('LIVE GRAMISS CART MOBILE V1.2 DEPLOYED; PDP HEADER REPAIRED')
