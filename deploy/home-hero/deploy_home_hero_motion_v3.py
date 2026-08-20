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


def replace_once(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'Expected CSS fragment missing: {label}')
    return text.replace(old, new, 1)


css = read_live('assets/css/interactive-hero.css')
js_before = read_live('assets/js/interactive-hero.js')
new_js = Path('wordpress/gramiss-theme/assets/js/interactive-hero.js').read_text(encoding='utf-8')

if 'Gramiss 1.2 — cinematic interactive fashion hero' not in css:
    raise SystemExit('Unexpected live hero CSS baseline; refusing blind patch')
if 'GRAMISS_HOME_HERO_MOTION_V3' not in new_js:
    raise SystemExit('Motion V3 JS marker missing in repository')
if 'createElement' in new_js or 'innerHTML' in new_js:
    raise SystemExit('Motion V3 JS must remain enhancement-only')

save_live(f'assets/css/interactive-hero.css.bak-motion-v3-{STAMP}', css)
save_live(f'assets/js/interactive-hero.js.bak-motion-v3-{STAMP}', js_before)
print('Backups created:', STAMP)

css = css.replace('/* Gramiss 1.2 — cinematic interactive fashion hero', '/* Gramiss 1.3 — cinematic interactive fashion hero / fast motion pass', 1)
css = replace_once(css,
    '  --hero-light-x:50%;\n  --hero-light-y:31%;',
    '  --hero-light-tx:0px;\n  --hero-light-ty:0px;',
    'light variables')
css = replace_once(css,
    'radial-gradient(circle at var(--hero-light-x) var(--hero-light-y),rgba(255,252,247,.82) 0,rgba(255,246,235,.45) 18%,transparent 39%)',
    'radial-gradient(circle at 50% 31%,rgba(255,252,247,.82) 0,rgba(255,246,235,.45) 18%,transparent 39%)',
    'fixed light gradient')
css = replace_once(css,
    '  filter:saturate(.98);\n  pointer-events:none;\n  transition:background-position .18s linear;',
    '  filter:saturate(.98);\n  transform:translate3d(var(--hero-light-tx),var(--hero-light-ty),0) scale(1.025);\n  transform-origin:center;\n  will-change:transform;\n  pointer-events:none;',
    'compositor light')
css = replace_once(css,
    '  transition:transform .28s cubic-bezier(.2,.8,.2,1);',
    '  will-change:transform;',
    'aura transition')
css = replace_once(css,
    '  transition:transform .32s cubic-bezier(.2,.8,.2,1);',
    '  will-change:transform;\n  backface-visibility:hidden;',
    'copy transition')
css = replace_once(css,
    '  --px:0px;--py:0px;--scale:1;--tilt:0deg;--depth-z:0px;',
    '  --px:0px;--py:0px;--tilt:0deg;--depth-z:0px;--hover-scale:1;',
    'product variables')
css = replace_once(css,
    '  transform:translate3d(var(--px),var(--py),var(--depth-z)) rotate(calc(var(--rot,0deg) + var(--tilt))) scale(var(--scale));',
    '  transform:translate3d(var(--px),var(--py),var(--depth-z)) rotate(calc(var(--rot,0deg) + var(--tilt)));',
    'product transform')
css = replace_once(css,
    '  transition:transform .42s cubic-bezier(.2,.8,.2,1),filter .35s ease,opacity .35s ease;\n  will-change:transform;',
    '  transition:opacity .2s ease;\n  will-change:transform;\n  backface-visibility:hidden;',
    'product lag transition')
css = replace_once(css,
    '  transform:translate3d(0,var(--mobile-drift,0px),0);\n  transition:filter .35s ease,transform .38s cubic-bezier(.2,.8,.2,1);',
    '  transform:translate3d(0,var(--mobile-drift,0px),0) scale(var(--hover-scale));\n  transform-origin:center;\n  transition:filter .18s ease,transform .18s cubic-bezier(.2,.8,.2,1);\n  will-change:transform;\n  backface-visibility:hidden;',
    'media hover scale')
css = replace_once(css,
    '.g1-floating-product:hover,.g1-floating-product:focus-visible{--scale:1.058;--depth-z:34px;z-index:35}',
    '.g1-floating-product:hover,.g1-floating-product:focus-visible{--hover-scale:1.05;--depth-z:26px;z-index:35}',
    'hover variables')
css = css.replace('opacity:.84}', 'opacity:.87}', 1)
css = css.replace('--rot:0deg;--scale:1;--tilt:0deg;--depth-z:0;', '--rot:0deg;--hover-scale:1;--tilt:0deg;--depth-z:0;', 1)
css = css.replace('.g1-floating-product:hover,.g1-floating-product:focus-visible{--scale:1;--depth-z:0}', '.g1-floating-product:hover,.g1-floating-product:focus-visible{--hover-scale:1;--depth-z:0}', 1)
css = css.replace('background:radial-gradient(circle at 50% 19%,rgba(255,248,239,.64),transparent 35%)}', 'background:radial-gradient(circle at 50% 19%,rgba(255,248,239,.64),transparent 35%);transform:none}', 1)

save_live('assets/css/interactive-hero.css', css)
save_live('assets/js/interactive-hero.js', new_js)

live_css = read_live('assets/css/interactive-hero.css')
live_js = read_live('assets/js/interactive-hero.js')
checks = {
    'fast CSS marker': 'Gramiss 1.3 — cinematic interactive fashion hero / fast motion pass' in live_css,
    'no dynamic gradient repaint': '--hero-light-x' not in live_css and '--hero-light-tx' in live_css,
    'no 420ms product chase': 'transition:transform .42s' not in live_css,
    'GPU light transform': 'translate3d(var(--hero-light-tx),var(--hero-light-ty),0)' in live_css,
    'separate hover scale': '--hover-scale:1.05' in live_css,
    'motion V3 JS': 'GRAMISS_HOME_HERO_MOTION_V3' in live_js,
    'RAF interpolation': 'currentX +=' in live_js and 'targetX' in live_js,
    'JS enhancement only': 'createElement' not in live_js and 'innerHTML' not in live_js,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('Motion V3 live verification failed')

for label, url, marker in (
    ('Home', f'https://gramiss.ir/?_motion_v3={STAMP}', 'data-g1-floating-hero'),
    ('Hero CSS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/interactive-hero.css?_v={STAMP}', 'Gramiss 1.3 — cinematic interactive fashion hero / fast motion pass'),
    ('Hero JS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/js/interactive-hero.js?_v={STAMP}', 'GRAMISS_HOME_HERO_MOTION_V3'),
):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'GramissMotionV3Deploy/1.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
        body = response.read().decode('utf-8', 'replace')
        print(label + ' HTTP status:', response.status)
        if response.status != 200 or marker not in body:
            raise SystemExit(label + ' served verification failed')

print('SUCCESS: HOME HERO MOTION V3 LIVE — FAST RAF PARALLAX + GPU LIGHT; SAME SERVER-RENDERED HERO')
