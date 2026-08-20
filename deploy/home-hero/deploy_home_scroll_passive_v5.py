import json
import os
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
    raise RuntimeError('Unexpected content payload for ' + rel)


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


new_css = Path('wordpress/gramiss-theme/assets/css/home-floating-header.css').read_text(encoding='utf-8')
new_js = Path('wordpress/gramiss-theme/assets/js/home-floating-header.js').read_text(encoding='utf-8')

if 'GRAMISS HOME FLOATING HEADER V3' not in new_css:
    raise SystemExit('Header V3 CSS marker missing')
if 'GRAMISS HOME FLOATING HEADER V3' not in new_js:
    raise SystemExit('Header V3 JS marker missing')
if 'position:sticky' in new_css:
    raise SystemExit('Sticky header still present in V3 CSS')
if 'backdrop-filter:blur' in new_css:
    raise SystemExit('Backdrop blur still present in V3 CSS')
if "addEventListener('scroll'" in new_js or 'window.scrollY' in new_js:
    raise SystemExit('Scroll-time header JS still present')

css_before = read_live('assets/css/home-floating-header.css')
js_before = read_live('assets/js/home-floating-header.js')
save_live(f'assets/css/home-floating-header.css.bak-scroll-v5-{STAMP}', css_before)
save_live(f'assets/js/home-floating-header.js.bak-scroll-v5-{STAMP}', js_before)
print('Backups created:', STAMP)

save_live('assets/css/home-floating-header.css', new_css)
save_live('assets/js/home-floating-header.js', new_js)

live_css = read_live('assets/css/home-floating-header.css')
live_js = read_live('assets/js/home-floating-header.js')
checks = {
    'V3 header CSS': 'GRAMISS HOME FLOATING HEADER V3' in live_css,
    'non sticky header': 'position:relative' in live_css and 'position:sticky' not in live_css,
    'no backdrop blur': 'backdrop-filter:blur' not in live_css,
    'compact neutralized': 'Deliberately neutralize legacy compact-on-scroll state' in live_css,
    'V3 header JS': 'GRAMISS HOME FLOATING HEADER V3' in live_js,
    'no window scroll listener': "addEventListener('scroll'" not in live_js and 'window.scrollY' not in live_js,
    'no compact toggle': "classList.toggle('is-compact'" not in live_js,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('Home header V5 live verification failed')

for label, url, marker in (
    ('Home', f'https://gramiss.ir/?_scroll_v5={STAMP}', 'site-header--home-float'),
    ('Header CSS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/home-floating-header.css?_v={STAMP}', 'GRAMISS HOME FLOATING HEADER V3'),
    ('Header JS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/js/home-floating-header.js?_v={STAMP}', 'GRAMISS HOME FLOATING HEADER V3'),
):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'GramissScrollV5Deploy/1.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
        body = response.read().decode('utf-8', 'replace')
        print(label + ' HTTP status:', response.status)
        if response.status != 200 or marker not in body:
            raise SystemExit(label + ' served verification failed')

print('SUCCESS: HOME HEADER V5 LIVE — NON-STICKY + NO SCROLL COMPACT + NO BACKDROP BLUR')
