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


css = read_live('assets/css/interactive-hero.css')
js_before = read_live('assets/js/interactive-hero.js')
new_js = Path('wordpress/gramiss-theme/assets/js/interactive-hero.js').read_text(encoding='utf-8')

if 'Gramiss 1.5 — instant-hover cinematic interactive fashion hero' not in css:
    raise SystemExit('Unexpected live Hero CSS baseline; refusing blind V7 patch')
if 'GRAMISS_HOME_HERO_MOTION_V7' not in new_js:
    raise SystemExit('V7 JS marker missing')
if 'is-page-scrolling' not in new_js or "window.addEventListener('wheel'" not in new_js:
    raise SystemExit('V7 scroll guard behavior missing')
if 'createElement' in new_js or 'innerHTML' in new_js:
    raise SystemExit('V7 JS must remain enhancement-only')

save_live(f'assets/css/interactive-hero.css.bak-scrollguard-v7-{STAMP}', css)
save_live(f'assets/js/interactive-hero.js.bak-scrollguard-v7-{STAMP}', js_before)
print('Backups created:', STAMP)

start = '/* GRAMISS_HERO_SCROLL_GUARD_V7_START */'
end = '/* GRAMISS_HERO_SCROLL_GUARD_V7_END */'
if start in css and end in css:
    css = css.split(start, 1)[0].rstrip() + '\n' + css.split(end, 1)[1].lstrip()

guard = r'''
/* GRAMISS_HERO_SCROLL_GUARD_V7_START */
/* During page scroll, products must not react to a stationary pointer passing over them. */
.g1-floating-hero.is-page-scrolling .g1-floating-product{
  pointer-events:none!important;
  transition:none!important;
  opacity:1!important;
  --hover-scale:1!important;
  --depth-z:0px!important;
}
.g1-floating-hero.is-page-scrolling .g1-floating-product::before,
.g1-floating-hero.is-page-scrolling .g1-floating-product-media,
.g1-floating-hero.is-page-scrolling .g1-floating-product-label{
  transition:none!important;
}
.g1-floating-hero.is-page-scrolling .g1-floating-product-label{
  opacity:0!important;
}
.g1-floating-hero.is-page-scrolling .g1-floating-products:has(.g1-floating-product:hover) .g1-floating-product:not(:hover){
  opacity:1!important;
}
/* GRAMISS_HERO_SCROLL_GUARD_V7_END */
'''.strip()

css = css.rstrip() + '\n\n' + guard + '\n'

save_live('assets/css/interactive-hero.css', css)
save_live('assets/js/interactive-hero.js', new_js)

live_css = read_live('assets/css/interactive-hero.css')
live_js = read_live('assets/js/interactive-hero.js')
checks = {
    'V7 CSS guard marker': 'GRAMISS_HERO_SCROLL_GUARD_V7_START' in live_css,
    'scroll pointer suspension': 'pointer-events:none!important' in live_css,
    'scroll transition suspension': 'transition:none!important' in live_css,
    'V7 JS marker': 'GRAMISS_HOME_HERO_MOTION_V7' in live_js,
    'page scroll state': "hero.classList.add('is-page-scrolling')" in live_js,
    'wheel pre-arm': "window.addEventListener('wheel', beginPageScroll" in live_js,
    'keyboard/scrollbar fallback': "window.addEventListener('scroll', beginPageScroll" in live_js,
    'idle re-enable': 'window.setTimeout(finishPageScroll, 145)' in live_js,
    'enhancement only': 'createElement' not in live_js and 'innerHTML' not in live_js,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('Hero V7 scroll guard verification failed')

for label, url, marker in (
    ('Home', f'https://gramiss.ir/?_scrollguard_v7={STAMP}', 'data-g1-floating-hero'),
    ('Hero CSS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/interactive-hero.css?_v={STAMP}', 'GRAMISS_HERO_SCROLL_GUARD_V7_START'),
    ('Hero JS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/js/interactive-hero.js?_v={STAMP}', 'GRAMISS_HOME_HERO_MOTION_V7'),
):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'GramissScrollGuardV7Deploy/1.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
        body = response.read().decode('utf-8', 'replace')
        print(label + ' HTTP status:', response.status)
        if response.status != 200 or marker not in body:
            raise SystemExit(label + ' served verification failed')

print('SUCCESS: HOME HERO V7 LIVE — HOVER/PARALLAX SUSPENDED DURING PAGE SCROLL')
