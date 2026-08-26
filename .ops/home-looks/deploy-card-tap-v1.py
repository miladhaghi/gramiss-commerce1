import hashlib
import json
import os
import re
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

CSS_MARKER = 'GRAMISS_HOME_LOOKS_CARD_CTA_V1'
JS_MARKER = 'GRAMISS_HOME_LOOKS_CARD_TAP_V1'

CSS_PATCH = r'''
/* GRAMISS_HOME_LOOKS_CARD_CTA_V1 */
@media (max-width:650px){
  .g1-looks__product-card:not(.is-soon){
    cursor:pointer;
    touch-action:pan-y;
    transition:opacity .16s ease,box-shadow .18s ease,background-color .18s ease;
  }
  .g1-looks__product-card.g1-card-pressing{
    opacity:.975!important;
    box-shadow:0 18px 46px rgba(53,35,23,.16),0 2px 8px rgba(53,35,23,.08)!important;
  }
  .g1-looks__product-card>a{
    min-height:52px!important;
    margin-top:4px;
    padding-top:14px!important;
    border-top:1px solid rgba(47,32,22,.12);
    display:flex!important;
    align-items:center!important;
    justify-content:space-between!important;
    gap:12px;
    font-weight:800!important;
    text-decoration:none!important;
  }
  .g1-looks__product-card>a span{
    flex:0 0 38px;
    width:38px;
    height:38px;
    border-radius:999px;
    display:grid;
    place-items:center;
    background:#25170f;
    color:#fff;
    font-size:16px;
    line-height:1;
    box-shadow:0 8px 20px rgba(37,23,15,.16);
  }
  .g1-looks__spot.is-active .g1-looks__product-card>a span{
    animation:g1LooksArrowNudge .46s ease-out .18s 1;
  }
}
@keyframes g1LooksArrowNudge{
  0%,100%{transform:translate(0,0)}
  48%{transform:translate(3px,-3px)}
}
@media (prefers-reduced-motion:reduce){
  .g1-looks__spot.is-active .g1-looks__product-card>a span{animation:none!important}
}
'''.strip()

JS_PATCH = r'''
/* GRAMISS_HOME_LOOKS_CARD_TAP_V1 */
(() => {
  'use strict';
  const root = document.querySelector('[data-g1-looks]');
  if (!root || !window.matchMedia) return;
  const mobile = () => window.matchMedia('(max-width:650px)').matches;
  const interactive = 'a,button,input,select,textarea,label';

  root.querySelectorAll('.g1-looks__product-card:not(.is-soon)').forEach((card) => {
    const link = Array.from(card.children).find((el) => el.tagName === 'A' && el.href);
    if (!link) return;

    card.classList.add('g1-card-linkable');
    let pointerId = null;
    let startX = 0;
    let startY = 0;
    let moved = false;

    const reset = () => {
      pointerId = null;
      moved = false;
      card.classList.remove('g1-card-pressing');
    };

    card.addEventListener('pointerdown', (event) => {
      if (!mobile() || (typeof event.button === 'number' && event.button !== 0)) return;
      if (event.target.closest(interactive)) return;
      pointerId = event.pointerId;
      startX = event.clientX;
      startY = event.clientY;
      moved = false;
      card.classList.add('g1-card-pressing');
    }, { passive: true });

    card.addEventListener('pointermove', (event) => {
      if (event.pointerId !== pointerId) return;
      if (Math.hypot(event.clientX - startX, event.clientY - startY) > 10) {
        moved = true;
        card.classList.remove('g1-card-pressing');
      }
    }, { passive: true });

    card.addEventListener('pointercancel', reset, { passive: true });

    card.addEventListener('pointerup', (event) => {
      if (event.pointerId !== pointerId) return;
      const selection = window.getSelection ? window.getSelection().toString().trim() : '';
      const shouldOpen = mobile() && !moved && !selection && !event.target.closest(interactive);
      reset();
      if (shouldOpen) window.setTimeout(() => link.click(), 55);
    }, { passive: true });
  });
})();
'''.strip()


def call(fn, params, post=False):
    url = f'https://{HOST}:2083/execute/Fileman/{fn}'
    data = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 6):
        try:
            req = urllib.request.Request(
                url if post else url + '?' + data.decode(),
                data=data if post else None,
                method='POST' if post else 'GET',
            )
            req.add_header('Authorization', f'cpanel {USER}:{TOKEN}')
            if post:
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, context=CTX, timeout=90) as response:
                obj = json.loads(response.read().decode('utf-8', 'replace'))
            result = obj.get('result') if isinstance(obj.get('result'), dict) else obj
            if not isinstance(result, dict) or result.get('status') != 1:
                raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last = exc
            print(f'Attempt {attempt}/5 {fn}: {exc}')
            if attempt < 5:
                time.sleep(attempt * 3)
    raise last


def read_live(rel):
    parent, name = rel.rsplit('/', 1)
    data = call('get_file_content', {
        'dir': ROOT + '/' + parent,
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
    raise RuntimeError('Unexpected live content: ' + rel)


def save_live(rel, content):
    parent, name = rel.rsplit('/', 1)
    call('save_file_content', {
        'dir': ROOT + '/' + parent,
        'file': name,
        'content': content,
        'from_charset': 'UTF-8',
        'to_charset': 'UTF-8',
        'fallback': '0',
    }, True)


def public_get(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'GramissLooksCardTap/1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    })
    with urllib.request.urlopen(req, context=CTX, timeout=90) as response:
        return response.status, response.read()


def verify_home(tag, expect_v23=False):
    status, body = public_get(f'https://gramiss.ir/?card_tap_{tag}={int(time.time())}')
    html = body.decode('utf-8', 'replace')
    checks = {
        'home 200': status == 200,
        'hero': 'g1-floating-hero' in html,
        'signal': 'g1-signal-strip' in html,
        'looks': 'data-g1-looks' in html,
        'collections': 'id="collections"' in html,
        'order': html.find('g1-signal-strip') < html.find('data-g1-looks') < html.find('id="collections"'),
    }
    if expect_v23:
        checks['css v2.3.0'] = 'home-looks.css?v=2.3.0' in html
        checks['js v2.3.0'] = 'home-looks.js?v=2.3.0' in html
    for label, ok in checks.items():
        print(('PASS' if ok else 'FAIL') + ': ' + tag + ' ' + label)
    if not all(checks.values()):
        raise SystemExit(f'ABORT: Home verification failed at {tag}')


verify_home('pre')

css_rel = 'assets/css/home-looks.css'
js_rel = 'assets/js/home-looks.js'
partial_rel = 'template-parts/home-looks.php'
css = read_live(css_rel)
js = read_live(js_rel)
partial = read_live(partial_rel)

if 'GRAMISS_HOME_LOOKS_MOBILE_CARD_FIX_V1' not in css:
    raise SystemExit('ABORT: mobile bottom-sheet fix missing')
if 'GRAMISS_HOME_LOOKS_SURGICAL_V2' not in js or 'GRAMISS_HOME_LOOKS_SURGICAL_V2' not in partial:
    raise SystemExit('ABORT: unexpected Home Looks source')

save_live(css_rel + '.bak-card-tap-' + STAMP, css)
save_live(js_rel + '.bak-card-tap-' + STAMP, js)
save_live(partial_rel + '.bak-card-tap-' + STAMP, partial)

new_css = css if CSS_MARKER in css else css.rstrip() + '\n\n' + CSS_PATCH + '\n'
new_js = js if JS_MARKER in js else js.rstrip() + '\n\n' + JS_PATCH + '\n'
new_partial, css_count = re.subn(
    r'/assets/css/home-looks\.css\?v=[^\'\"]+',
    '/assets/css/home-looks.css?v=2.3.0',
    partial,
    count=1,
)
new_partial, js_count = re.subn(
    r'/assets/js/home-looks\.js\?v=[^\'\"]+',
    '/assets/js/home-looks.js?v=2.3.0',
    new_partial,
    count=1,
)
if css_count != 1 or js_count != 1:
    raise SystemExit('ABORT: asset URL patch mismatch')

save_live(css_rel, new_css)
save_live(js_rel, new_js)
save_live(partial_rel, new_partial)

if CSS_MARKER not in read_live(css_rel):
    raise SystemExit('ABORT: CSS write verification failed')
if JS_MARKER not in read_live(js_rel):
    raise SystemExit('ABORT: JS write verification failed')
print('PASS: production files written and backups created')
print('CSS SHA:', hashlib.sha256(read_live(css_rel).encode()).hexdigest())
print('JS SHA:', hashlib.sha256(read_live(js_rel).encode()).hexdigest())

purge_name = 'gramiss-purge-card-tap-' + STAMP + '.php'
purge_php = "<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
call('save_file_content', {
    'dir': 'public_html',
    'file': purge_name,
    'content': purge_php,
    'from_charset': 'UTF-8',
    'to_charset': 'UTF-8',
    'fallback': '0',
}, True)
with urllib.request.urlopen(
    urllib.request.Request('https://gramiss.ir/' + purge_name + '?t=' + str(int(time.time())), headers={'User-Agent': 'GramissLooksCardTap/1'}),
    context=CTX,
    timeout=90,
) as response:
    print('PURGE', response.status, response.read().decode('utf-8', 'replace')[:30])

verify_home('post', True)

status, css_public = public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/home-looks.css?v=2.3.0&x=' + STAMP)
if status != 200 or CSS_MARKER.encode() not in css_public or b'g1LooksArrowNudge' not in css_public:
    raise SystemExit('ABORT: public CSS verification failed')
status, js_public = public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/js/home-looks.js?v=2.3.0&x=' + STAMP)
if status != 200 or JS_MARKER.encode() not in js_public or b'pointerdown' not in js_public:
    raise SystemExit('ABORT: public JS verification failed')

print('LIVE HOME LOOKS TAPPABLE CARD V1 DEPLOYED')
