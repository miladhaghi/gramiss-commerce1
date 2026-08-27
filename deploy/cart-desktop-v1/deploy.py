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
site_root = theme.split('/wp-content/themes/')[0]
ctx = ssl._create_unverified_context()
stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
version = '20260828-1'

css_rel = 'assets/css/cart-desktop-v1.css'
js_rel = 'assets/js/cart-desktop-v1.js'
css_file = Path('deploy/cart-desktop-v1/cart-desktop-v1.css')
js_file = Path('deploy/cart-desktop-v1/cart-desktop-v1.js')
css = css_file.read_text(encoding='utf-8')
js = js_file.read_text(encoding='utf-8')

if 'GRAMISS_CART_DESKTOP_V1' not in css or 'GRAMISS_CART_DESKTOP_V1' not in js:
    raise SystemExit('ABORT: desktop V1 markers missing')
if "matchMedia('(min-width:761px)')" not in js or "classList.contains('woocommerce-cart')" not in js:
    raise SystemExit('ABORT: desktop/cart JS guards missing')
if '.gramiss-cart-service-rail' not in css or '.gramiss-cart-safe' not in css:
    raise SystemExit('ABORT: duplicate trust suppression missing')
subprocess.run(['node', '--check', str(js_file)], check=True)

css_sha = hashlib.sha256(css.encode()).hexdigest()
js_sha = hashlib.sha256(js.encode()).hexdigest()
print('CANDIDATE CSS', len(css.encode()), css_sha)
print('CANDIDATE JS', len(js.encode()), js_sha)


def call(fn, params, post=False):
    url = f'https://{host}:2083/execute/Fileman/{fn}'
    data = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 5):
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
            print(f'Attempt {attempt}/4 {fn}: {exc}')
            if attempt < 4:
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
        'User-Agent': 'Mozilla/5.0 GramissCartDesktopV1/1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Accept': '*/*',
    })
    with urllib.request.urlopen(req, context=ctx, timeout=90) as response:
        return response.status, response.geturl(), response.read()


header = read_at(theme, 'header.php')
original_header = header
front = read_at(theme, 'front-page.php')
front_sha = hashlib.sha256(front.encode()).hexdigest()
expected_home = os.environ.get('HEALTHY_HOME_SHA', '').strip()
print('LIVE_HOME_SHA', front_sha)
if expected_home and front_sha != expected_home:
    raise SystemExit('ABORT: Home baseline mismatch; nothing changed')

mobile_start = '<!-- GRAMISS CART MOBILE V2 START -->'
mobile_end = '<!-- GRAMISS CART MOBILE V2 END -->'
mobile_match = re.search(re.escape(mobile_start) + r'.*?' + re.escape(mobile_end), header, flags=re.S)
if not mobile_match:
    raise SystemExit('ABORT: mobile Cart V2 block missing from live header')
mobile_snapshot = mobile_match.group(0)

start = '<!-- GRAMISS CART DESKTOP V1 START -->'
end = '<!-- GRAMISS CART DESKTOP V1 END -->'
block = f'''<!-- GRAMISS CART DESKTOP V1 START -->
<?php if ( function_exists( 'is_cart' ) && is_cart() ) : ?>
<link id="gramiss-cart-desktop-v1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/{css_rel}?v={version}' ); ?>" media="(min-width:761px)">
<script id="gramiss-cart-desktop-v1-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/{js_rel}?v={version}' ); ?>" defer></script>
<?php endif; ?>
<!-- GRAMISS CART DESKTOP V1 END -->'''

if start in header and end in header:
    header, count = re.subn(re.escape(start) + r'.*?' + re.escape(end), block, header, count=1, flags=re.S)
    if count != 1:
        raise SystemExit('ABORT: desktop block replacement failed')
else:
    if '</head>' not in header:
        raise SystemExit('ABORT: </head> missing')
    header = header.replace('</head>', block + '\n</head>', 1)

if mobile_snapshot not in header:
    raise SystemExit('ABORT: candidate header altered mobile Cart V2 block')

backup_header = 'header.php.bak-cart-desktop-v1-' + stamp
write_at(theme, backup_header, original_header)
print('BACKUP', backup_header)

asset_backups = {}
for rel in (css_rel, js_rel):
    try:
        old = read_at(theme, rel)
        asset_backups[rel] = old
        write_at(theme, rel + '.bak-' + stamp, old)
        print('BACKUP', rel + '.bak-' + stamp)
    except Exception:
        asset_backups[rel] = None


def rollback(reason):
    try:
        write_at(theme, 'header.php', original_header)
    except Exception as exc:
        print('ROLLBACK HEADER ERROR', exc)
    for rel, old in asset_backups.items():
        if old is None:
            continue
        try:
            write_at(theme, rel, old)
        except Exception as exc:
            print('ROLLBACK ASSET ERROR', rel, exc)
    raise SystemExit('ROLLED BACK: ' + reason)


write_at(theme, css_rel, css)
write_at(theme, js_rel, js)
write_at(theme, 'header.php', header)

live_header = read_at(theme, 'header.php')
live_css = read_at(theme, css_rel)
live_js = read_at(theme, js_rel)
checks = {
    'desktop css ref once': live_header.count('gramiss-cart-desktop-v1-css') == 1,
    'desktop js ref once': live_header.count('gramiss-cart-desktop-v1-js') == 1,
    'desktop guarded by is_cart': "function_exists( 'is_cart' ) && is_cart()" in live_header,
    'mobile Cart V2 exact preserved': mobile_snapshot in live_header,
    'css exact': hashlib.sha256(live_css.encode()).hexdigest() == css_sha,
    'js exact': hashlib.sha256(live_js.encode()).hexdigest() == js_sha,
    'Home file preserved': hashlib.sha256(read_at(theme, 'front-page.php').encode()).hexdigest() == front_sha,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    rollback('live file verification failed')

purge = 'gramiss-purge-cart-desktop-v1-' + stamp + '.php'
purge_php = "<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
write_at(site_root, purge, purge_php)
try:
    status, _, body = public_get('https://gramiss.ir/' + purge + '?t=' + str(int(time.time())))
    print('PURGE', status, body.decode('utf-8', 'replace')[:40])
except Exception as exc:
    print('PURGE WARNING', exc)

nonce = str(int(time.time()))
status, _, body = public_get('https://gramiss.ir/?page_id=10&g3_cart_desktop=' + nonce)
cart_html = body.decode('utf-8', 'replace')
cart_checks = {
    'Cart 200': status == 200,
    'official Cart page': 'woocommerce-cart' in cart_html and 'page-id-10' in cart_html,
    'desktop css ref': f'{css_rel}?v={version}' in cart_html,
    'desktop js ref': f'{js_rel}?v={version}' in cart_html,
    'mobile V2 still referenced': 'cart-mobile-v2.css' in cart_html and 'cart-mobile-v2.js' in cart_html,
}
for label, ok in cart_checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(cart_checks.values()):
    rollback('public Cart verification failed')

for rel, expected, marker in (
    (css_rel, css_sha, b'GRAMISS_CART_DESKTOP_V1'),
    (js_rel, js_sha, b'GRAMISS_CART_DESKTOP_V1'),
):
    status, _, data = public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/' + rel + '?verify=' + nonce)
    got = hashlib.sha256(data).hexdigest()
    ok = status == 200 and got == expected and marker in data
    print(('PASS' if ok else 'FAIL') + ': public ' + rel + ' bytes=' + str(len(data)) + ' sha=' + got)
    if not ok:
        rollback('public asset verification failed: ' + rel)

status, _, body = public_get('https://gramiss.ir/?p=392&g3_pdp_safety=' + nonce)
product_html = body.decode('utf-8', 'replace')
product_ok = status == 200 and 'cart-desktop-v1.css' not in product_html and 'cart-desktop-v1.js' not in product_html
print(('PASS' if product_ok else 'FAIL') + ': PDP isolated from desktop Cart assets')
if not product_ok:
    rollback('PDP isolation failed')

status, _, body = public_get('https://gramiss.ir/?g3_home_safety=' + nonce)
home_html = body.decode('utf-8', 'replace')
home_ok = (
    status == 200 and
    'g1-floating-hero' in home_html and
    'data-g1-looks' in home_html and
    'cart-desktop-v1.css' not in home_html and
    'cart-desktop-v1.js' not in home_html
)
print(('PASS' if home_ok else 'FAIL') + ': Home/Looks untouched')
if not home_ok:
    rollback('Home safety verification failed')

print('LIVE GRAMISS CART DESKTOP V1 DEPLOYED')
