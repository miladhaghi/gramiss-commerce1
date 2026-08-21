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

ENAMAD = "<a referrerpolicy='origin' target='_blank' href='https://trustseal.enamad.ir/?id=7094948&Code=xJ8HkTjjBF0ykbRRdp0yoXAzjUguqwgJ'><img referrerpolicy='origin' src='https://trustseal.enamad.ir/logo.aspx?id=7094948&Code=xJ8HkTjjBF0ykbRRdp0yoXAzjUguqwgJ' alt='' style='cursor:pointer' code='xJ8HkTjjBF0ykbRRdp0yoXAzjUguqwgJ'></a>"


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


footer = read_live('footer.php')
css = read_live('assets/css/theme.css')

save_live(f'footer.php.bak-enamad-v1-{STAMP}', footer)
save_live(f'assets/css/theme.css.bak-enamad-v1-{STAMP}', css)
print('Backups created:', STAMP)

if ENAMAD not in footer:
    needle = '        <div class="footer-bottom">'
    if needle not in footer:
        raise SystemExit('Footer insertion point missing; refusing blind edit')
    block = '''        <div class="footer-trust" aria-label="اعتماد و مجوزهای Gramiss">\n            <div class="footer-trust-meta">\n                <strong>اعتماد و مجوزها</strong>\n                <span>برای مشاهده وضعیت اعتبار، روی نماد کلیک کنید.</span>\n            </div>\n            <div class="footer-enamad">''' + ENAMAD + '''</div>\n        </div>\n'''
    footer = footer.replace(needle, block + needle, 1)

marker = '/* GRAMISS_ENAMAD_FOOTER_V1 */'
styles = '''\n/* GRAMISS_ENAMAD_FOOTER_V1 */\n.footer-trust{margin-top:38px;padding-top:24px;border-top:1px solid #29292d;display:flex;align-items:center;justify-content:space-between;gap:28px}\n.footer-trust-meta{display:flex;flex-direction:column;gap:5px}\n.footer-trust-meta strong{font-size:13px;font-weight:700;color:#fff}\n.footer-trust-meta span{font-size:11px;color:#85858c}\n.footer-enamad{flex:0 0 auto;display:flex;align-items:center;justify-content:center;min-height:86px}\n@media(max-width:760px){.footer-trust{align-items:flex-start;flex-direction:column}.footer-enamad{align-self:flex-start}}\n'''
if marker not in css:
    css = css.rstrip() + styles

save_live('footer.php', footer)
save_live('assets/css/theme.css', css)

live_footer = read_live('footer.php')
live_css = read_live('assets/css/theme.css')
checks = {
    'exact official eNAMAD snippet': ENAMAD in live_footer,
    'snippet appears exactly once': live_footer.count(ENAMAD) == 1,
    'Gramiss trust wrapper': 'class="footer-trust"' in live_footer,
    'footer CSS marker': marker in live_css,
    'no direct eNAMAD img CSS': '.footer-enamad img' not in live_css,
    'no direct eNAMAD anchor CSS': '.footer-enamad a' not in live_css,
}
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
if not all(checks.values()):
    raise SystemExit('eNAMAD footer verification failed')

for label, url, marker_text in (
    ('Home', f'https://gramiss.ir/?_enamad_v1={STAMP}', 'trustseal.enamad.ir/?id=7094948'),
    ('Theme CSS', f'https://gramiss.ir/wp-content/themes/gramiss-theme-next/assets/css/theme.css?_v={STAMP}', 'GRAMISS_ENAMAD_FOOTER_V1'),
):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'GramissEnamadDeploy/1.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
        body = response.read().decode('utf-8', 'replace')
        print(label + ' HTTP status:', response.status)
        if response.status != 200 or marker_text not in body:
            raise SystemExit(label + ' served verification failed')

print('SUCCESS: eNAMAD OFFICIAL SNIPPET ADDED TO LIVE FOOTER UNMODIFIED')
