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
        raise SystemExit(f'Expected fragment missing: {label}')
    return text.replace(old, new, 1)


hero_css = read_live('assets/css/interactive-hero.css')
header_css = read_live('assets/css/home-floating-header.css')
js_before = read_live('assets/js/interactive-hero.js')
new_js = Path('wordpress/gramiss-theme/assets/js/interactive-hero.js').read_text(encoding='utf-8')

if 'Gramiss 1.3 — cinematic interactive fashion hero / fast motion pass' not in hero_css:
    raise SystemExit('Unexpected live Hero CSS baseline; refusing blind patch')
if 'GRAMISS HOME FLOATING HEADER V2' not in header_css:
    raise SystemExit('Unexpected live Home header CSS baseline; refusing blind patch')
if 'GRAMISS_HOME_HERO_MOTION_V4' not in new_js:
    raise SystemExit('Motion V4 JS marker missing in repository')
if 'window.addEventListener(\'scroll\'' in new_js or 'window.addEventListener("scroll"' in new_js:
    raise SystemExit('V4 JS must not listen to vertical window scroll')
if 'createElement' in new_js or 'innerHTML' in new_js:
    raise SystemExit('V4 JS must remain enhancement-only')

save_live(f'assets/css/interactive-hero.css.bak-scroll-v4-{STAMP}', hero_css)
save_live(f'assets/css/home-floating-header.css.bak-scroll-v4-{STAMP}', header_css)
save_live(f'assets/js/interactive-hero.js.bak-scroll-v4-{STAMP}', js_before)
print('Backups created:', STAMP)

hero_css = hero_css.replace(
    '/* Gramiss 1.3 — cinematic interactive fashion hero / fast motion pass',
    '/* Gramiss 1.4 — scroll-optimized cinematic interactive fashion hero',
    1,
)
hero_css = replace_once(
    hero_css,
    '  filter:blur(34px);\n  transform:perspective(500px) rotateX(64deg) scaleX(1.08);',
    '  filter:none;\n  opacity:.72;\n  transform:perspective(500px) rotateX(64deg) scaleX(1.08);',
    'large ground blur',
)
hero_css = replace_once(
    hero_css,
    '  filter:blur(15px);\n  opacity:.96;',
    '  filter:none;\n  opacity:.88;',
    'large aura blur',
)
hero_css = replace_once(
    hero_css,
    '  filter:blur(var(--halo-blur,18px));\n  transform:scale(1.05);',
    '  filter:none;\n  transform:scale(1.06);',
    'product halo blur',
)
hero_css = replace_once(
    hero_css,
    'border-radius:50%;background:radial-gradient(ellipse,rgba(255,255,255,.16),transparent 67%);filter:blur(17px);pointer-events:none;',
    'border-radius:50%;background:radial-gradient(ellipse,rgba(255,255,255,.14),transparent 70%);filter:none;pointer-events:none;',
    'product secondary blur',
)
hero_css = hero_css.replace(
    'filter:brightness(var(--object-brightness,1)) saturate(var(--object-saturation,1)) drop-shadow(0 var(--shadow-y,28px) var(--shadow-blur,28px) rgba(28,25,23,var(--shadow-opacity,.21)))',
    'filter:brightness(var(--object-brightness,1)) saturate(var(--object-saturation,1)) drop-shadow(0 calc(var(--shadow-y,28px) * .72) calc(var(--shadow-blur,28px) * .68) rgba(28,25,23,var(--shadow-opacity,.21)))',
    1,
)
hero_css = hero_css.replace(
    'filter:brightness(1.04) saturate(1.035) drop-shadow(0 39px 35px rgba(23,21,20,.31));',
    'filter:brightness(1.04) saturate(1.035) drop-shadow(0 26px 24px rgba(23,21,20,.27));',
    1,
)

header_css = header_css.replace('/* GRAMISS HOME FLOATING HEADER V2', '/* GRAMISS HOME FLOATING HEADER V2.1 SCROLL PERF', 1)
header_css = replace_once(
    header_css,
    '  -webkit-backdrop-filter:blur(22px) saturate(116%);\n  backdrop-filter:blur(22px) saturate(116%);',
    '  -webkit-backdrop-filter:blur(8px) saturate(108%);\n  backdrop-filter:blur(8px) saturate(108%);',
    'header heavy backdrop blur',
)
header_css = header_css.replace(
    'background:linear-gradient(110deg,rgba(226,215,203,.72),rgba(247,241,234,.76) 48%,rgba(221,210,198,.70))!important;',
    'background:linear-gradient(110deg,rgba(226,215,203,.80),rgba(247,241,234,.84) 48%,rgba(221,210,198,.78))!important;',
    1,
)

save_live('assets/css/interactive-hero.css', hero_css)
save_live('assets/css/home-floating-header.css', header_css)
save_live('assets/js/interactive-hero.js', new_js)

live_hero_css = read_live('assets/css/interactive-hero.css')
live_header_css = read_live('assets/css/home-floating-header.css')
live_js = read_live('assets/js/interactive-hero.js')

checks = {
    'V4 hero CSS marker': 'Gramiss 1.4 — scroll-optimized cinematic interactive fashion hero' in live_hero_css,
    'large hero blur removed': 'filter:blur(34px)' not in live_hero_css and 'filter:blur(15px)' not in live_hero_css,
    'product halo blur removed': 'filter:blur(var(--halo-blur,18px))' not in live_hero_css,
    'lighter object shadow': 'calc(var(--shadow-blur,28px) * .68)' in live_hero_css,
    'header scroll perf marker': 'GRAMISS HOME FLOATING HEADER V2.1 SCROLL PERF' in live_header_css,
    'header blur reduced': 'blur(8px) saturate(108%)' in live_header_css and 'blur(22px)' not in live_header_css,
    'motion V4 JS': 'GRAMISS_HOME_HERO_MOTION_V4' in live_js,
    'no vertical window scroll listener': "window.addEventListener('scroll'" not in live_js and 'window.addEventListener("scroll"' not in live_js,
    'no continuous idle loop': 'idlePhase' not in live_js and 'motionLoop' not in live_js,
    'JS enhancement only': 'createElement' not in live_js and 'innerHTML' not in live_js,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('Scroll performance V4 live verification failed')

for label, url, marker in (
    ('Home', f'https://gramiss.ir/?_scroll_v4={STAMP}', 'data-g1-floating-hero'),
    ('Hero CSS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/interactive-hero.css?_v={STAMP}', 'Gramiss 1.4 — scroll-optimized cinematic interactive fashion hero'),
    ('Header CSS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/home-floating-header.css?_v={STAMP}', 'GRAMISS HOME FLOATING HEADER V2.1 SCROLL PERF'),
    ('Hero JS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/js/interactive-hero.js?_v={STAMP}', 'GRAMISS_HOME_HERO_MOTION_V4'),
):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'GramissScrollV4Deploy/1.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
        body = response.read().decode('utf-8', 'replace')
        print(label + ' HTTP status:', response.status)
        if response.status != 200 or marker not in body:
            raise SystemExit(label + ' served verification failed')

print('SUCCESS: HOME SCROLL V4 LIVE — NO VERTICAL HERO MOTION + LIGHTER GLASS/BLURS + EVENT-DRIVEN PARALLAX')
