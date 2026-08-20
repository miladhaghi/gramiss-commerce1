import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

HOST = os.environ['CPANEL_HOST']
USER = os.environ['CPANEL_USER']
TOKEN = os.environ['CPANEL_TOKEN']
ROOT = os.environ['THEME_ROOT'].strip('/')
CTX = ssl._create_unverified_context()
STAMP = time.strftime('%Y%m%d-%H%M%S', time.gmtime())


def call(func, params, post=False):
    url = f'https://{HOST}:2083/execute/Fileman/{func}'
    encoded = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 5):
        try:
            req = urllib.request.Request(
                url if post else url + '?' + encoded.decode(),
                data=encoded if post else None,
                method='POST' if post else 'GET',
            )
            req.add_header('Authorization', f'cpanel {USER}:{TOKEN}')
            if post:
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
                payload = json.loads(response.read().decode('utf-8'))
            result = payload.get('result') if isinstance(payload.get('result'), dict) else payload
            if not isinstance(result, dict) or result.get('status') != 1:
                raise RuntimeError(str(result.get('errors') if isinstance(result, dict) else result))
            return result.get('data')
        except Exception as exc:
            last = exc
            print(f'Attempt {attempt}/4 {func}: {exc}')
            if attempt < 4:
                time.sleep(attempt * 3)
    raise last


def read_live(rel):
    parent, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    directory = ROOT if not parent else f'{ROOT}/{parent}'
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
    raise RuntimeError(f'Unexpected content payload for {rel}')


def save_live(rel, content):
    parent, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    directory = ROOT if not parent else f'{ROOT}/{parent}'
    call('save_file_content', {
        'dir': directory,
        'file': name,
        'content': content,
        'from_charset': 'UTF-8',
        'to_charset': 'UTF-8',
        'fallback': '0',
    }, post=True)


css = Path('wordpress/gramiss-theme/assets/css/home-floating-header.css').read_text(encoding='utf-8')
js = Path('wordpress/gramiss-theme/assets/js/home-floating-header.js').read_text(encoding='utf-8')

if 'GRAMISS HOME FLOATING HEADER V1' not in css:
    raise SystemExit('Home header CSS marker missing')
if 'site-header--home-float' not in css:
    raise SystemExit('Home header selector missing')
if 'createElement' in js or 'innerHTML' in js:
    raise SystemExit('Home header JS must not build or replace DOM')

header = read_live('header.php')
save_live(f'header.php.bak-home-floating-{STAMP}', header)
save_live('assets/css/home-floating-header.css', css)
save_live('assets/js/home-floating-header.js', js)

start = '<!-- GRAMISS HOME FLOATING HEADER ASSETS START -->'
end = '<!-- GRAMISS HOME FLOATING HEADER ASSETS END -->'
asset_block = start + """
<?php if ( is_front_page() ) : ?>
<link rel="stylesheet" id="gramiss-home-floating-header-css" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/home-floating-header.css?v=20260820-1' ); ?>" media="all">
<script id="gramiss-home-floating-header-js" defer src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/home-floating-header.js?v=20260820-1' ); ?>"></script>
<?php endif; ?>
""" + end

patched = header
if start in patched and end in patched:
    patched = patched.split(start, 1)[0] + asset_block + patched.split(end, 1)[1]
elif '</head>' in patched:
    patched = patched.replace('</head>', asset_block + '\n</head>', 1)
else:
    raise SystemExit('Could not find </head> in live header.php')

if 'site-header--home-float' not in patched:
    patched, count = re.subn(
        r'<header\s+class=["\']site-header["\']',
        '<header class="site-header<?php echo is_front_page() ? \' site-header--home-float\' : \'\'; ?>"',
        patched,
        count=1,
        flags=re.I,
    )
    if count != 1:
        raise SystemExit('Could not patch live site-header class')

if 'header-inner--home-float' not in patched:
    patched, count = re.subn(
        r'class=["\']gramiss-container\s+header-inner["\']',
        'class="gramiss-container header-inner<?php echo is_front_page() ? \' header-inner--home-float\' : \'\'; ?>"',
        patched,
        count=1,
        flags=re.I,
    )
    if count != 1:
        raise SystemExit('Could not patch live header-inner class')

save_live('header.php', patched)

live_header = read_live('header.php')
live_css = read_live('assets/css/home-floating-header.css')
live_js = read_live('assets/js/home-floating-header.js')

checks = {
    'server-side outer class': "is_front_page() ? ' site-header--home-float'" in live_header,
    'server-side inner class': "is_front_page() ? ' header-inner--home-float'" in live_header,
    'render-blocking CSS in head': start in live_header and 'gramiss-home-floating-header-css' in live_header,
    'CSS installed': 'GRAMISS HOME FLOATING HEADER V1' in live_css,
    'JS enhancement only': 'createElement' not in live_js and 'innerHTML' not in live_js,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('Live file verification failed')

home_url = 'https://gramiss.ir/?_home_header=' + STAMP
request = urllib.request.Request(home_url, headers={
    'Cache-Control': 'no-cache',
    'User-Agent': 'GramissHomeHeaderDeploy/1.0',
})
with urllib.request.urlopen(request, context=CTX, timeout=60) as response:
    html = response.read().decode('utf-8', 'replace')
    status = response.status

head_end = html.lower().find('</head>')
css_pos = html.find('gramiss-home-floating-header-css')
header_pos = html.find('site-header site-header--home-float')
inner_pos = html.find('header-inner header-inner--home-float')
print('Home HTTP status:', status)
print('Positions css/head/header/inner:', css_pos, head_end, header_pos, inner_pos)

if status != 200:
    raise SystemExit('Home did not return HTTP 200')
if css_pos < 0 or head_end < 0 or css_pos > head_end:
    raise SystemExit('Home header CSS is not loaded in <head> before first paint')
if header_pos < 0 or inner_pos < 0:
    raise SystemExit('Home header modifier classes are not server-rendered in first HTML')

css_url = (
    'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/'
    'home-floating-header.css?v=20260820-1&_verify=' + STAMP
)
request = urllib.request.Request(css_url, headers={
    'Cache-Control': 'no-cache',
    'User-Agent': 'GramissHomeHeaderDeploy/1.0',
})
with urllib.request.urlopen(request, context=CTX, timeout=60) as response:
    served_css = response.read().decode('utf-8', 'replace')
    css_status = response.status

print('Home header CSS HTTP status:', css_status)
if css_status != 200 or 'GRAMISS HOME FLOATING HEADER V1' not in served_css:
    raise SystemExit('Served Home header CSS verification failed')

print('SUCCESS: HOME FLOATING HEADER DEPLOYED FROM FIRST HTML; NO LEGACY-TO-NEW SWAP')
