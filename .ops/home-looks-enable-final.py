import hashlib
import json
import os
import ssl
import time
import urllib.parse
import urllib.request

host = os.environ['CPANEL_HOST']
user = os.environ['CPANEL_USER']
token = os.environ['CPANEL_TOKEN']
root = os.environ['THEME_ROOT'].strip('/')
healthy = os.environ['HEALTHY_HOME_SHA']
ctx = ssl._create_unverified_context()
stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())


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


def read_theme(rel):
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


def save_theme(rel, content):
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
        'User-Agent': 'GramissLooksFinal/1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    })
    with urllib.request.urlopen(req, context=ctx, timeout=90) as response:
        return response.status, response.read()


front = read_theme('front-page.php')
front_sha = hashlib.sha256(front.encode()).hexdigest()
print('LIVE_HOME_SHA', front_sha)
if front_sha != healthy:
    raise SystemExit('ABORT: current live Home differs from confirmed healthy baseline; nothing changed')
if 'g1-floating-hero' not in front or 'g1-signal-strip' not in front:
    raise SystemExit('ABORT: Hero markers missing; nothing changed')
if "get_template_part( 'template-parts/home-looks' )" in front:
    raise SystemExit('ABORT: Looks include already present; nothing changed')

anchor = '    <section class="g1-section g1-reveal" id="collections">'
pos = front.find(anchor)
if pos < 0:
    raise SystemExit('ABORT: Collections anchor missing; nothing changed')
prefix = front[:pos]
prefix_sha = hashlib.sha256(prefix.encode()).hexdigest()

partial = read_theme('template-parts/home-looks.php')
css = read_theme('assets/css/home-looks.css')
js = read_theme('assets/js/home-looks.js')
if 'GRAMISS_HOME_LOOKS_SURGICAL_V2' not in partial or 'data-g1-looks' not in partial:
    raise SystemExit('ABORT: live Looks PHP invalid')
if 'GRAMISS_HOME_LOOKS_SURGICAL_V2' not in css:
    raise SystemExit('ABORT: live Looks CSS invalid')
if 'GRAMISS_HOME_LOOKS_SURGICAL_V2' not in js:
    raise SystemExit('ABORT: live Looks JS invalid')

for path, expected, minbytes in [
    ('assets/images/home/gramiss-look-01.webp', os.environ['LOOK1_SHA'], 14000),
    ('assets/images/home/gramiss-look-02.webp', os.environ['LOOK2_SHA'], 17000),
]:
    status, body = public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/' + path + '?pre=' + stamp)
    got = hashlib.sha256(body).hexdigest()
    print('PRE_ASSET', path, status, len(body), got)
    if status != 200 or len(body) < minbytes or got != expected or not (body.startswith(b'RIFF') and b'WEBP' in body[:16]):
        raise SystemExit('ABORT: model asset verification failed; nothing changed')

save_theme('front-page.php.bak-before-looks-enable-' + stamp, front)
include = "    <?php get_template_part( 'template-parts/home-looks' ); ?>\n\n"
patched = front[:pos] + include + front[pos:]
save_theme('front-page.php', patched)


def rollback(reason):
    save_theme('front-page.php', front)
    raise SystemExit('ROLLED BACK: ' + reason)


live_after = read_theme('front-page.php')
if live_after != patched:
    rollback('front-page write mismatch')
if hashlib.sha256(live_after[:pos].encode()).hexdigest() != prefix_sha:
    rollback('Hero/prefix changed')
if live_after.count("get_template_part( 'template-parts/home-looks' )") != 1:
    rollback('include count invalid')
print('PASS HERO/PREFIX UNCHANGED BYTE-FOR-BYTE', prefix_sha)

try:
    purge = 'gramiss-purge-looks-final-' + stamp + '.php'
    php = "<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
    call('save_file_content', {
        'dir': 'public_html',
        'file': purge,
        'content': php,
        'from_charset': 'UTF-8',
        'to_charset': 'UTF-8',
        'fallback': '0',
    }, True)
    status, body = public_get('https://gramiss.ir/' + purge + '?t=' + str(int(time.time())))
    print('PURGE', status, body.decode('utf-8', 'replace')[:40])

    status, body = public_get('https://gramiss.ir/?gramiss_looks_final=' + str(int(time.time())))
    html = body.decode('utf-8', 'replace')
    checks = {
        'home 200': status == 200,
        'hero preserved': 'g1-floating-hero' in html and 'کمتر حدس بزن' in html,
        'looks visible': 'data-g1-looks' in html and 'GRAMISS LOOKS / 01' in html and 'استایل را لمس کن.' in html,
        'position': html.find('g1-signal-strip') < html.find('data-g1-looks') < html.find('id="collections"'),
        'models': 'gramiss-look-01.webp' in html and 'gramiss-look-02.webp' in html,
        'cards': 'g1-looks__product-card' in html,
    }
    for label, ok in checks.items():
        print(('PASS' if ok else 'FAIL'), label)
    if not all(checks.values()):
        rollback('public Home verification failed')

    for path, marker in [
        ('assets/css/home-looks.css', 'GRAMISS_HOME_LOOKS_SURGICAL_V2'),
        ('assets/js/home-looks.js', 'GRAMISS_HOME_LOOKS_SURGICAL_V2'),
    ]:
        status, body = public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/' + path + '?post=' + stamp)
        if status != 200 or marker.encode() not in body:
            rollback('public text asset failed ' + path)

    print('LIVE GRAMISS LOOKS ENABLED — HERO PRESERVED')
except SystemExit:
    raise
except Exception as exc:
    rollback('post-write verification error: ' + str(exc))
