import hashlib
import json
import os
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

host = os.environ['CPANEL_HOST']
user = os.environ['CPANEL_USER']
token = os.environ['CPANEL_TOKEN']
root = os.environ['THEME_ROOT'].strip('/')
healthy_home = os.environ.get('HEALTHY_HOME_SHA','')
ctx = ssl._create_unverified_context()
stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())


def call(fn, params, post=False):
    url = f'https://{host}:2083/execute/Fileman/{fn}'
    data = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 5):
        try:
            req = urllib.request.Request(url if post else url + '?' + data.decode(), data=data if post else None, method='POST' if post else 'GET')
            req.add_header('Authorization', f'cpanel {user}:{token}')
            if post:
                req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, context=ctx, timeout=90) as response:
                obj = json.loads(response.read().decode('utf-8','replace'))
            result = obj.get('result') if isinstance(obj.get('result'),dict) else obj
            if not isinstance(result,dict) or result.get('status') != 1:
                raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last = exc
            print(f'Attempt {attempt}/4 {fn}: {exc}')
            if attempt < 4: time.sleep(attempt*2)
    raise last


def read_theme(rel):
    parent,name = rel.rsplit('/',1) if '/' in rel else ('',rel)
    directory = root if not parent else root + '/' + parent
    data = call('get_file_content', {'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for key in ('content','file_content','data'):
            if isinstance(data.get(key),str): return data[key]
    if isinstance(data,str): return data
    raise RuntimeError('Cannot read '+rel)


def save_theme(rel,content):
    parent,name = rel.rsplit('/',1) if '/' in rel else ('',rel)
    directory = root if not parent else root + '/' + parent
    call('save_file_content', {'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'}, True)


def public_get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'GramissCheckoutMobile/1','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req, context=ctx, timeout=90) as response:
        return response.status, response.read(), response.geturl()

front = read_theme('front-page.php')
front_sha = hashlib.sha256(front.encode()).hexdigest()
print('LIVE_HOME_SHA', front_sha)
if healthy_home and front_sha != healthy_home:
    raise SystemExit('ABORT: Home baseline mismatch; nothing changed')

header = read_theme('header.php')
if '</head>' not in header:
    raise SystemExit('ABORT: header closing head missing')
if 'GRAMISS PDP MOBILE UX V1' not in header or 'GRAMISS CART MOBILE V1' not in header:
    raise SystemExit('ABORT: expected existing mobile loaders missing')

css = Path('deploy/checkout-mobile-v1/checkout-mobile-v1.css').read_text(encoding='utf-8')
js = Path('deploy/checkout-mobile-v1/checkout-mobile-v1.js').read_text(encoding='utf-8')
if 'GRAMISS_CHECKOUT_MOBILE_V1' not in css or 'GRAMISS_CHECKOUT_MOBILE_V1' not in js:
    raise SystemExit('ABORT: candidate assets invalid')

old_css = None
old_js = None
try: old_css = read_theme('assets/css/checkout-mobile-v1.css')
except Exception: pass
try: old_js = read_theme('assets/js/checkout-mobile-v1.js')
except Exception: pass

start='<!-- GRAMISS CHECKOUT MOBILE V1 START -->'
end='<!-- GRAMISS CHECKOUT MOBILE V1 END -->'
patched = header
if start in patched and end in patched:
    a=patched.index(start); b=patched.index(end,a)+len(end)
    patched=patched[:a]+patched[b:]
loader = f'''\n{start}\n<?php if ( function_exists( 'is_checkout' ) && is_checkout() && ! ( function_exists( 'is_order_received_page' ) && is_order_received_page() ) ) : ?>\n<link id="gramiss-checkout-mobile-v1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/checkout-mobile-v1.css?v=20260827-1' ); ?>" media="(max-width:760px)">\n<script id="gramiss-checkout-mobile-v1-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/checkout-mobile-v1.js?v=20260827-1' ); ?>" defer></script>\n<?php endif; ?>\n{end}\n'''
patched = patched.replace('</head>', loader + '</head>', 1)

save_theme('header.php.bak-checkout-mobile-v1-'+stamp, header)
if old_css is not None: save_theme('assets/css/checkout-mobile-v1.css.bak-'+stamp, old_css)
if old_js is not None: save_theme('assets/js/checkout-mobile-v1.js.bak-'+stamp, old_js)

save_theme('assets/css/checkout-mobile-v1.css', css)
save_theme('assets/js/checkout-mobile-v1.js', js)
save_theme('header.php', patched)


def rollback(reason):
    save_theme('header.php', header)
    if old_css is not None: save_theme('assets/css/checkout-mobile-v1.css', old_css)
    if old_js is not None: save_theme('assets/js/checkout-mobile-v1.js', old_js)
    raise SystemExit('ROLLED BACK: '+reason)

live_header=read_theme('header.php')
if live_header != patched: rollback('header write mismatch')
if live_header.count(start) != 1 or live_header.count(end) != 1: rollback('checkout loader marker count invalid')
if 'GRAMISS PDP MOBILE UX V1' not in live_header or 'GRAMISS CART MOBILE V1' not in live_header: rollback('existing mobile loaders changed')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest() != front_sha: rollback('Home changed')
if read_theme('assets/css/checkout-mobile-v1.css') != css: rollback('CSS write mismatch')
if read_theme('assets/js/checkout-mobile-v1.js') != js: rollback('JS write mismatch')

try:
    purge='gramiss-purge-checkout-'+stamp+'.php'
    php="<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo function_exists('wc_get_checkout_url') ? wc_get_checkout_url() : 'OK'; @unlink(__FILE__);"
    call('save_file_content', {'dir':'public_html','file':purge,'content':php,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'}, True)
    status,body,final=public_get('https://gramiss.ir/'+purge+'?t='+str(int(time.time())))
    print('PURGE',status,body.decode('utf-8','replace')[:200])

    for path,marker in [('assets/css/checkout-mobile-v1.css','GRAMISS_CHECKOUT_MOBILE_V1'),('assets/js/checkout-mobile-v1.js','GRAMISS_CHECKOUT_MOBILE_V1')]:
        status,body,final=public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/'+path+'?v='+stamp)
        ok=status==200 and marker.encode() in body and len(body)>1000
        print(('PASS' if ok else 'FAIL'),path,status,len(body))
        if not ok: rollback('public asset verify failed '+path)

    status,body,final=public_get('https://gramiss.ir/?checkout_mobile_verify='+str(int(time.time())))
    home=body.decode('utf-8','replace')
    checks={'home 200':status==200,'hero preserved':'g1-floating-hero' in home,'looks preserved':'data-g1-looks' in home}
    for label,ok in checks.items(): print(('PASS' if ok else 'FAIL'),label)
    if not all(checks.values()): rollback('Home public verify failed')
    print('LIVE CHECKOUT MOBILE V1 DEPLOYED')
except SystemExit:
    raise
except Exception as exc:
    rollback('post-write verification error: '+str(exc))
