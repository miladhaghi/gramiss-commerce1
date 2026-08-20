import json
import os
import ssl
import time
import urllib.parse
import urllib.request

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


css = read_live('assets/css/interactive-hero.css')
if 'Gramiss 1.4 — scroll-optimized cinematic interactive fashion hero' not in css:
    raise SystemExit('Unexpected live Hero CSS baseline; refusing blind hover patch')

save_live(f'assets/css/interactive-hero.css.bak-hover-v6-{STAMP}', css)
print('Backup created:', STAMP)

css = css.replace(
    '/* Gramiss 1.4 — scroll-optimized cinematic interactive fashion hero',
    '/* Gramiss 1.5 — instant-hover cinematic interactive fashion hero',
    1,
)

css = replace_once(
    css,
    '  transition:opacity .2s ease;\n  will-change:transform;',
    '  transition:opacity .10s ease-out;\n  will-change:transform;',
    'product opacity response',
)

css = replace_once(
    css,
    '  transition:opacity .32s ease,transform .38s cubic-bezier(.2,.8,.2,1);',
    '  transition:opacity .16s ease-out,transform .17s cubic-bezier(.16,1,.3,1);',
    'halo response',
)

css = replace_once(
    css,
    '  transition:filter .18s ease,transform .18s cubic-bezier(.2,.8,.2,1);',
    '  transition:filter .15s ease-out,transform .16s cubic-bezier(.16,1,.3,1);',
    'media base response',
)

css = replace_once(
    css,
    '  transition:opacity .25s ease,transform .3s cubic-bezier(.2,.8,.2,1),background .25s ease;',
    '  transition:opacity .14s ease-out,transform .16s cubic-bezier(.16,1,.3,1),background .14s ease-out;',
    'label response',
)

css = replace_once(
    css,
    '.g1-floating-product:hover,.g1-floating-product:focus-visible{--hover-scale:1.05;--depth-z:26px;z-index:35}',
    '.g1-floating-product:hover,.g1-floating-product:focus-visible{--hover-scale:1.062;--depth-z:38px;z-index:35}',
    'hover separation strength',
)

css = replace_once(
    css,
    '.g1-floating-product:hover::before,.g1-floating-product:focus-visible::before{opacity:1;transform:scale(1.18)}',
    '.g1-floating-product:hover::before,.g1-floating-product:focus-visible::before{opacity:1;transform:scale(1.18);transition-duration:.055s,.065s}',
    'instant halo entry',
)

css = replace_once(
    css,
    '.g1-floating-product:hover .g1-floating-product-media,.g1-floating-product:focus-visible .g1-floating-product-media{\n  filter:brightness(1.04) saturate(1.035) drop-shadow(0 26px 24px rgba(23,21,20,.27));\n}',
    '.g1-floating-product:hover .g1-floating-product-media,.g1-floating-product:focus-visible .g1-floating-product-media{\n  filter:brightness(1.04) saturate(1.035) drop-shadow(0 26px 24px rgba(23,21,20,.27));\n  transition-duration:.045s,.06s;\n}',
    'instant media entry',
)

css = replace_once(
    css,
    '.g1-floating-product:hover .g1-floating-product-label,.g1-floating-product:focus-visible .g1-floating-product-label{opacity:1;transform:translate(-50%,0) scale(1);background:rgba(15,17,21,.82)}',
    '.g1-floating-product:hover .g1-floating-product-label,.g1-floating-product:focus-visible .g1-floating-product-label{opacity:1;transform:translate(-50%,0) scale(1);background:rgba(15,17,21,.82);transition-duration:.055s,.07s,.055s}',
    'instant label entry',
)

save_live('assets/css/interactive-hero.css', css)
live = read_live('assets/css/interactive-hero.css')
checks = {
    'V6 marker': 'Gramiss 1.5 — instant-hover cinematic interactive fashion hero' in live,
    'stronger immediate separation': '--hover-scale:1.062;--depth-z:38px' in live,
    'fast media entry': 'transition-duration:.045s,.06s' in live,
    'fast halo entry': 'transition-duration:.055s,.065s' in live,
    'fast label entry': 'transition-duration:.055s,.07s,.055s' in live,
    'faster sibling fade': 'transition:opacity .10s ease-out' in live,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('Hover response V6 verification failed')

for label, url, marker in (
    ('Home', f'https://gramiss.ir/?_hover_v6={STAMP}', 'data-g1-floating-hero'),
    ('Hero CSS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/interactive-hero.css?_v={STAMP}', 'Gramiss 1.5 — instant-hover cinematic interactive fashion hero'),
):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'GramissHoverV6Deploy/1.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
        body = response.read().decode('utf-8', 'replace')
        print(label + ' HTTP status:', response.status)
        if response.status != 200 or marker not in body:
            raise SystemExit(label + ' served verification failed')

print('SUCCESS: HOME HERO HOVER V6 LIVE — NEAR-INSTANT ENTRY + SMOOTH EXIT')
