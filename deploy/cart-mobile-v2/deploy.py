import hashlib
import json
import os
import re
import ssl
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

host = os.environ['CPANEL_HOST']
user = os.environ['CPANEL_USER']
token = os.environ['CPANEL_TOKEN']
theme = os.environ['THEME_ROOT'].strip('/')
public = 'public_html'
ctx = ssl._create_unverified_context()
stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
version = '20260827-4'

css_rel = 'assets/css/cart-mobile-v2.css'
js_rel = 'assets/js/cart-mobile-v2.js'
css_file = Path('deploy/cart-mobile-v2/cart-mobile-v2.css')
js_file = Path('deploy/cart-mobile-v2/cart-mobile-v2.js')
css = css_file.read_text(encoding='utf-8')
js = js_file.read_text(encoding='utf-8')

if 'GRAMISS_CART_MOBILE_V2' not in css or 'GRAMISS_CART_MOBILE_V2' not in js:
    raise SystemExit('ABORT: V2 markers missing')
if 'g2-cart-mobile-v2' not in css or "classList.contains('woocommerce-cart')" not in js:
    raise SystemExit('ABORT: V2 mobile/cart guards missing')
subprocess.run(['node', '--check', str(js_file)], check=True)

css_sha = hashlib.sha256(css.encode()).hexdigest()
js_sha = hashlib.sha256(js.encode()).hexdigest()
print('CANDIDATE CSS', len(css.encode()), css_sha)
print('CANDIDATE JS', len(js.encode()), js_sha)


def call(fn, params, post=False):
    url = f'https://{host}:2083/execute/Fileman/{fn}'
    data = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 6):
        try:
            req = urllib.request.Request(
                url if post else url + '?' + data.decode(),
                data=data if post else None,
                method='POST' if post else 'GET',
            )
            req.add_header('Authorization', f'cpanel {user}:{token}')
            if post:
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, context=ctx, timeout=90) as response:
                obj = json.loads(response.read().decode('utf-8', 'replace'))
            result = obj.get('result') if isinstance(obj.get('result'), dict) else obj
            if not isinstance(result, dict) or result.get('status') != 1:
                raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last = exc
            print(f'Attempt {attempt}/5 {fn}: {exc}')
            if attempt < 5:
                time.sleep(attempt * 2)
    raise last


def read_at(root, rel):
    parent, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    directory = root if not parent else root + '/' + parent
    data = call('get_file_content', {
        'dir': directory,
        'file': name,
        'from_charset': '_DETECT_',
        'to_charset': 'utf-8',
    })
    if isinstance(data, dict):
        for key in ('content', 'file_content', 'data'):
            if isinstance(data.get(key), str):
                return data[key]
    if isinstance(data, str):
        return data
    raise RuntimeError('Cannot read ' + rel)


def write_at(root, rel, content):
    parent, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    directory = root if not parent else root + '/' + parent
    call('save_file_content', {
        'dir': directory,
        'file': name,
        'content': content,
        'from_charset': 'UTF-8',
        'to_charset': 'UTF-8',
        'fallback': '0',
    }, True)


def public_get(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 GramissCartMobileV2/1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Accept': '*/*',
    })
    with urllib.request.urlopen(req, context=ctx, timeout=90) as response:
        return response.status, response.geturl(), response.read()


header = read_at(theme, 'header.php')
original_header = header
pdp_start = '<!-- GRAMISS PDP MOBILE UX V1 START -->'
pdp_end = '<!-- GRAMISS PDP MOBILE UX V1 END -->'
if header.count(pdp_start) != 1 or header.count(pdp_end) != 1:
    raise SystemExit('ABORT: clean PDP mobile block not found exactly once')
if 'product-mobile-v1-4.css?v=20260827-5' not in header or 'product-mobile-v1-4.js?v=20260827-5' not in header:
    raise SystemExit('ABORT: PDP safety assets missing')

v1_start = '<!-- GRAMISS CART MOBILE V1 START -->'
v1_end = '<!-- GRAMISS CART MOBILE V1 END -->'
v2_start = '<!-- GRAMISS CART MOBILE V2 START -->'
v2_end = '<!-- GRAMISS CART MOBILE V2 END -->'
v2_block = f'''<!-- GRAMISS CART MOBILE V2 START -->
<?php if ( function_exists( 'is_cart' ) && is_cart() ) : ?>
<link id="gramiss-cart-mobile-v2-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/{css_rel}?v={version}' ); ?>" media="(max-width:760px)">
<script id="gramiss-cart-mobile-v2-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/{js_rel}?v={version}' ); ?>" defer></script>
<?php endif; ?>
<!-- GRAMISS CART MOBILE V2 END -->'''

if v2_start in header and v2_end in header:
    header, count = re.subn(re.escape(v2_start) + r'.*?' + re.escape(v2_end), v2_block, header, count=1, flags=re.S)
    if count != 1:
        raise SystemExit('ABORT: V2 block replacement failed')
elif v1_start in header and v1_end in header:
    header, count = re.subn(re.escape(v1_start) + r'.*?' + re.escape(v1_end), v2_block, header, count=1, flags=re.S)
    if count != 1:
        raise SystemExit('ABORT: V1-to-V2 block replacement failed')
else:
    if '</head>' not in header:
        raise SystemExit('ABORT: </head> missing')
    header = header.replace('</head>', v2_block + '\n</head>', 1)

if 'gramiss-cart-mobile-v1' in header:
    raise SystemExit('ABORT: V1 refs remain in candidate header')

backup_header = 'header.php.bak-cart-mobile-v2-' + stamp
write_at(theme, backup_header, original_header)
print('BACKUP', backup_header)

for rel in (css_rel, js_rel):
    try:
        old = read_at(theme, rel)
        write_at(theme, rel + '.bak-' + stamp, old)
        print('BACKUP', rel + '.bak-' + stamp)
    except Exception:
        pass

write_at(theme, css_rel, css)
write_at(theme, js_rel, js)
write_at(theme, 'header.php', header)


def rollback(reason):
    write_at(theme, 'header.php', original_header)
    raise SystemExit('ROLLED BACK HEADER: ' + reason)


live_header = read_at(theme, 'header.php')
live_css = read_at(theme, css_rel)
live_js = read_at(theme, js_rel)
checks = {
    'v2 css once': live_header.count('gramiss-cart-mobile-v2-css') == 1,
    'v2 js once': live_header.count('gramiss-cart-mobile-v2-js') == 1,
    'v2 guarded by is_cart': "function_exists( 'is_cart' ) && is_cart()" in live_header,
    'v1 removed': 'gramiss-cart-mobile-v1' not in live_header,
    'pdp block preserved': live_header.count(pdp_start) == 1 and live_header.count(pdp_end) == 1,
    'pdp assets preserved': 'product-mobile-v1-4.css?v=20260827-5' in live_header and 'product-mobile-v1-4.js?v=20260827-5' in live_header,
    'css exact': hashlib.sha256(live_css.encode()).hexdigest() == css_sha,
    'js exact': hashlib.sha256(live_js.encode()).hexdigest() == js_sha,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    rollback('live file verification failed')

purge = 'gramiss-purge-cart-mobile-v2-' + stamp + '.php'
purge_php = "<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
write_at(public, purge, purge_php)
st, final, body = public_get('https://gramiss.ir/' + purge + '?t=' + str(int(time.time())))
print('PURGE', st, body.decode('utf-8', 'replace')[:40])

nonce = str(int(time.time()))
st, final, body = public_get('https://gramiss.ir/?page_id=10&g2_cart_v2=' + nonce)
cart_html = body.decode('utf-8', 'replace')
cart_checks = {
    'cart 200': st == 200,
    'official cart page': 'woocommerce-cart' in cart_html and 'page-id-10' in cart_html,
    'v2 css ref': f'{css_rel}?v={version}' in cart_html,
    'v2 js ref': f'{js_rel}?v={version}' in cart_html,
    'v1 refs absent': 'cart-mobile-v1.css' not in cart_html and 'cart-mobile-v1.js' not in cart_html,
    'legacy engine still present': 'gramiss-v1-inline-css' in cart_html,
    'pdp assets absent on cart': 'product-mobile-v1-4.css?v=20260827-5' not in cart_html and 'product-mobile-v1-4.js?v=20260827-5' not in cart_html,
}
for label, ok in cart_checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(cart_checks.values()):
    rollback('public Cart verification failed')

for rel, expected, marker in (
    (css_rel, css_sha, b'GRAMISS_CART_MOBILE_V2'),
    (js_rel, js_sha, b'GRAMISS_CART_MOBILE_V2'),
):
    st, final, data = public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/' + rel + '?verify=' + nonce)
    got = hashlib.sha256(data).hexdigest()
    ok = st == 200 and got == expected and marker in data
    print(('PASS' if ok else 'FAIL') + ': public ' + rel + ' bytes=' + str(len(data)) + ' sha=' + got)
    if not ok:
        rollback('public asset verification failed: ' + rel)

st, final, body = public_get('https://gramiss.ir/?p=392&g2_pdp_safety=' + nonce)
product_html = body.decode('utf-8', 'replace')
product_ok = (
    st == 200 and
    'product-mobile-v1-4.css?v=20260827-5' in product_html and
    'product-mobile-v1-4.js?v=20260827-5' in product_html and
    'cart-mobile-v2.css' not in product_html and
    'cart-mobile-v2.js' not in product_html
)
print(('PASS' if product_ok else 'FAIL') + ': PDP isolated/preserved')
if not product_ok:
    rollback('PDP safety verification failed')

st, final, body = public_get('https://gramiss.ir/?g2_home_safety=' + nonce)
home_html = body.decode('utf-8', 'replace')
home_ok = st == 200 and 'g1-floating-hero' in home_html and 'data-g1-looks' in home_html and 'cart-mobile-v2.css' not in home_html and 'cart-mobile-v2.js' not in home_html
print(('PASS' if home_ok else 'FAIL') + ': Home/Looks untouched')
if not home_ok:
    rollback('Home safety verification failed')

print('LIVE GRAMISS CART MOBILE V2 DEPLOYED')
