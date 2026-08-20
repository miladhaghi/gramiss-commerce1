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


new_css = Path('wordpress/gramiss-theme/assets/css/interactive-hero.css').read_text(encoding='utf-8')
new_js = Path('wordpress/gramiss-theme/assets/js/interactive-hero.js').read_text(encoding='utf-8')

if 'Gramiss 1.2 — cinematic interactive fashion hero' not in new_css:
    raise SystemExit('V2 CSS marker missing')
if 'GRAMISS_HOME_HERO_V2' not in new_js:
    raise SystemExit('V2 JS marker missing')
if 'createElement' in new_js or 'innerHTML' in new_js:
    raise SystemExit('Hero JS is not enhancement-only')

front = read_live('front-page.php')
live_css_before = read_live('assets/css/interactive-hero.css')
live_js_before = read_live('assets/js/interactive-hero.js')

if 'g1-floating-hero' not in front:
    raise SystemExit('Live floating hero markup not found; refusing blind deploy')
if 'Gramiss 1.1 — unified floating fashion hero' not in live_css_before and 'Gramiss 1.2 — cinematic interactive fashion hero' not in live_css_before:
    raise SystemExit('Unexpected live hero CSS baseline; refusing blind deploy')

save_live(f'front-page.php.bak-homehero-v2-{STAMP}', front)
save_live(f'assets/css/interactive-hero.css.bak-homehero-v2-{STAMP}', live_css_before)
save_live(f'assets/js/interactive-hero.js.bak-homehero-v2-{STAMP}', live_js_before)
print('Backups created:', STAMP)

old_title = '<h1 id="g1-hero-title">کمتر حدس بزن،<br>بهتر انتخاب کن.</h1>'
new_title = '<h1 id="g1-hero-title" aria-label="کمتر حدس بزن، بهتر انتخاب کن."><span>کمتر حدس بزن،</span><span class="g1-hero-title-emphasis">بهتر انتخاب کن.</span></h1>'
if 'g1-hero-title-emphasis' not in front:
    if old_title not in front:
        raise SystemExit('Expected live hero title not found')
    front = front.replace(old_title, new_title, 1)

old_primary = '<a class="g1-btn g1-btn-dark" href="<?php echo esc_url( $shop_url ); ?>">ورود به فروشگاه</a>'
new_primary = '<a class="g1-btn g1-btn-dark g1-hero-primary-cta" href="<?php echo esc_url( $shop_url ); ?>">ورود به فروشگاه</a>'
if 'g1-hero-primary-cta' not in front:
    if old_primary not in front:
        raise SystemExit('Expected live primary CTA not found')
    front = front.replace(old_primary, new_primary, 1)

old_secondary = '<a class="g1-btn g1-btn-ghost" href="#smart-guide">راهنمای هوشمند</a>'
new_secondary = '<a class="g1-btn g1-btn-ghost g1-hero-secondary-cta" href="#smart-guide">راهنمای هوشمند</a>'
if 'g1-hero-secondary-cta' not in front:
    if old_secondary not in front:
        raise SystemExit('Expected live secondary CTA not found')
    front = front.replace(old_secondary, new_secondary, 1)

save_live('front-page.php', front)
save_live('assets/css/interactive-hero.css', new_css)
save_live('assets/js/interactive-hero.js', new_js)

live_front = read_live('front-page.php')
live_css = read_live('assets/css/interactive-hero.css')
live_js = read_live('assets/js/interactive-hero.js')

checks = {
    'server-rendered editorial title': 'g1-hero-title-emphasis' in live_front,
    'server-rendered primary CTA': 'g1-hero-primary-cta' in live_front,
    'server-rendered secondary CTA': 'g1-hero-secondary-cta' in live_front,
    'V2 CSS replaced old hero skin': 'Gramiss 1.2 — cinematic interactive fashion hero' in live_css and 'Gramiss 1.1 — unified floating fashion hero' not in live_css,
    'dynamic central light': '--hero-light-x' in live_css and '--hero-light-y' in live_css,
    'depth hierarchy': 'Depth hierarchy: same composition' in live_css,
    'discover labels': 'مشاهده مجموعه' in live_css,
    'CTA micro motion': 'g1-hero-primary-cta::after' in live_css,
    'V2 parallax JS': 'GRAMISS_HOME_HERO_V2' in live_js and '--mobile-drift' in live_js,
    'JS enhancement only': 'createElement' not in live_js and 'innerHTML' not in live_js,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('Live Home hero V2 file verification failed')

home_url = 'https://gramiss.ir/?_hero_v2=' + STAMP
req = urllib.request.Request(home_url, headers={
    'Cache-Control': 'no-cache',
    'User-Agent': 'GramissHeroV2Deploy/1.0',
})
with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
    html = response.read().decode('utf-8', 'replace')
    status = response.status
print('Home HTTP status:', status)
if status != 200:
    raise SystemExit('Home did not return HTTP 200')
if 'g1-hero-title-emphasis' not in html or 'g1-hero-primary-cta' not in html:
    raise SystemExit('Hero V2 markup not present in first HTML response')
if 'data-g1-floating-hero' not in html:
    raise SystemExit('Floating hero missing from first HTML response')

css_url = 'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/interactive-hero.css?_v=' + STAMP
req = urllib.request.Request(css_url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'GramissHeroV2Deploy/1.0'})
with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
    served_css = response.read().decode('utf-8', 'replace')
    css_status = response.status
print('Hero CSS HTTP status:', css_status)
if css_status != 200 or 'Gramiss 1.2 — cinematic interactive fashion hero' not in served_css:
    raise SystemExit('Hero V2 CSS serving verification failed')

js_url = 'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/js/interactive-hero.js?_v=' + STAMP
req = urllib.request.Request(js_url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'GramissHeroV2Deploy/1.0'})
with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
    served_js = response.read().decode('utf-8', 'replace')
    js_status = response.status
print('Hero JS HTTP status:', js_status)
if js_status != 200 or 'GRAMISS_HOME_HERO_V2' not in served_js:
    raise SystemExit('Hero V2 JS serving verification failed')

print('SUCCESS: HOME HERO V2 REPLACED LIVE — SERVER MARKUP + CINEMATIC DEPTH + PARALLAX; NO OVERLAY')
