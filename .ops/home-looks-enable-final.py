import hashlib, json, os, ssl, time, urllib.parse, urllib.request
from pathlib import Path

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

def save_theme(rel,content):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=root if not parent else root+'/'+parent
    call('save_file_content',{'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def public_get(url,timeout=50):
    req=urllib.request.Request(url,headers={'User-Agent':'GramissCheckoutDesktop/1.1','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req,context=ctx,timeout=timeout) as r: return r.status,r.read(),r.geturl()

def section(source,start,end):
    if start not in source or end not in source: return None
    a=source.index(start); b=source.index(end,a)+len(end); return source[a:b]

front=read_theme('front-page.php'); front_sha=hashlib.sha256(front.encode()).hexdigest(); print('LIVE_HOME_SHA',front_sha)
if healthy and front_sha!=healthy: raise SystemExit('ABORT: Home baseline mismatch; nothing changed')
header=read_theme('header.php')
if '</head>' not in header: raise SystemExit('ABORT: header closing head missing')

css=Path('deploy/checkout-desktop-v1/checkout-desktop-v1.css').read_text(encoding='utf-8')
polish=Path('deploy/checkout-desktop-v1/checkout-desktop-v1-1.css').read_text(encoding='utf-8')
js=Path('deploy/checkout-desktop-v1/checkout-desktop-v1.js').read_text(encoding='utf-8')
if 'GRAMISS_CHECKOUT_DESKTOP_V1' not in css or 'GRAMISS_CHECKOUT_DESKTOP_V1_1' not in polish or 'GRAMISS_CHECKOUT_DESKTOP_V1' not in js: raise SystemExit('ABORT: desktop candidates invalid')
print('CANDIDATE CSS',len(css),hashlib.sha256(css.encode()).hexdigest())
print('CANDIDATE POLISH',len(polish),hashlib.sha256(polish.encode()).hexdigest())
print('CANDIDATE JS',len(js),hashlib.sha256(js.encode()).hexdigest())

# Capture existing mobile checkout blocks; desktop deployment must preserve them byte-for-byte.
mobile_markers=[
 ('<!-- GRAMISS CHECKOUT MOBILE V1 START -->','<!-- GRAMISS CHECKOUT MOBILE V1 END -->'),
 ('<!-- GRAMISS CHECKOUT MOBILE V21 START -->','<!-- GRAMISS CHECKOUT MOBILE V21 END -->')
]
mobile_before={a:section(header,a,b) for a,b in mobile_markers}

old_css=old_polish=old_js=None
try: old_css=read_theme('assets/css/checkout-desktop-v1.css')
except Exception: pass
try: old_polish=read_theme('assets/css/checkout-desktop-v1-1.css')
except Exception: pass
try: old_js=read_theme('assets/js/checkout-desktop-v1.js')
except Exception: pass

start='<!-- GRAMISS CHECKOUT DESKTOP V1 START -->'; end='<!-- GRAMISS CHECKOUT DESKTOP V1 END -->'
base=header
if start in base and end in base:
    a=base.index(start); b=base.index(end,a)+len(end); base=base[:a]+base[b:]
loader=f'''\n{start}\n<?php if ( function_exists( 'is_checkout' ) && is_checkout() && ! ( function_exists( 'is_order_received_page' ) && is_order_received_page() ) ) : ?>\n<link id="gramiss-checkout-desktop-v1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/checkout-desktop-v1.css?v=20260828-2' ); ?>" media="(min-width:761px)">\n<link id="gramiss-checkout-desktop-v1-1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/checkout-desktop-v1-1.css?v=20260828-2' ); ?>" media="(min-width:761px)">\n<script id="gramiss-checkout-desktop-v1-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/checkout-desktop-v1.js?v=20260828-2' ); ?>" defer></script>\n<?php endif; ?>\n{end}\n'''
patched=base.replace('</head>',loader+'</head>',1)
if patched==base: raise SystemExit('ABORT: loader injection failed')

# Pre-write invariant: desktop edit itself must not alter any existing mobile block.
for a,b in mobile_markers:
    before=mobile_before[a]; after=section(patched,a,b)
    if before != after: raise SystemExit('ABORT: candidate would alter mobile checkout block '+a)

save_theme('header.php.bak-checkout-desktop-v1-'+stamp,header)
if old_css is not None: save_theme('assets/css/checkout-desktop-v1.css.bak-'+stamp,old_css)
if old_polish is not None: save_theme('assets/css/checkout-desktop-v1-1.css.bak-'+stamp,old_polish)
if old_js is not None: save_theme('assets/js/checkout-desktop-v1.js.bak-'+stamp,old_js)

def rollback(reason):
    print('ROLLBACK',reason)
    save_theme('header.php',header)
    if old_css is not None: save_theme('assets/css/checkout-desktop-v1.css',old_css)
    if old_polish is not None: save_theme('assets/css/checkout-desktop-v1-1.css',old_polish)
    if old_js is not None: save_theme('assets/js/checkout-desktop-v1.js',old_js)
    raise SystemExit('ROLLED BACK: '+reason)

save_theme('assets/css/checkout-desktop-v1.css',css)
save_theme('assets/css/checkout-desktop-v1-1.css',polish)
save_theme('assets/js/checkout-desktop-v1.js',js)
save_theme('header.php',patched)

live_header=read_theme('header.php'); live_css=read_theme('assets/css/checkout-desktop-v1.css'); live_polish=read_theme('assets/css/checkout-desktop-v1-1.css'); live_js=read_theme('assets/js/checkout-desktop-v1.js')
if live_header!=patched: rollback('header write mismatch')
if live_css!=css or live_polish!=polish or live_js!=js: rollback('asset write mismatch')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=front_sha: rollback('Home changed')
for a,b in mobile_markers:
    if mobile_before[a] != section(live_header,a,b): rollback('mobile checkout block changed '+a)
if live_header.count('gramiss-checkout-desktop-v1-css')!=1 or live_header.count('gramiss-checkout-desktop-v1-1-css')!=1 or live_header.count('gramiss-checkout-desktop-v1-js')!=1: rollback('desktop loader count invalid')
if 'v=20260828-2' not in live_header: rollback('desktop cache version missing')
print('PASS exact writes / Home preserved / mobile checkout preserved')

# Purge LiteSpeed via one-time WP bootstrap. Failure here does not justify destructive rollback after exact writes.
try:
    purge='gramiss-purge-checkout-desktop-'+stamp+'.php'
    php="<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo function_exists('wc_get_checkout_url') ? wc_get_checkout_url() : 'OK'; @unlink(__FILE__);"
    call('save_file_content',{'dir':'public_html','file':purge,'content':php,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
    status,body,_=public_get('https://gramiss.ir/'+purge+'?t='+str(int(time.time())),70); print('PURGE/CHECKOUT_URL',status,body.decode('utf-8','replace')[:180])
except Exception as exc:
    print('WARN purge request:',exc)

# Public asset checks with retries. Exact cPanel reads above remain authoritative.
for rel,marker in [('assets/css/checkout-desktop-v1.css',b'GRAMISS_CHECKOUT_DESKTOP_V1'),('assets/css/checkout-desktop-v1-1.css',b'GRAMISS_CHECKOUT_DESKTOP_V1_1'),('assets/js/checkout-desktop-v1.js',b'GRAMISS_CHECKOUT_DESKTOP_V1')]:
    ok=False
    for attempt in range(3):
        try:
            status,body,_=public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/'+rel+'?v='+stamp,45)
            ok=status==200 and marker in body and len(body)>800
            print(('PASS' if ok else 'FAIL'),'public',rel,status,len(body))
            if ok: break
        except Exception as exc:
            print('WARN public asset',rel,'attempt',attempt+1,exc); time.sleep(2)
    if not ok: print('WARN: public asset verification incomplete; cPanel exact-write verification passed')

print('LIVE CHECKOUT DESKTOP V1.1 DEPLOYED')
