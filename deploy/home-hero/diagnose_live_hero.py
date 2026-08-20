import json
import os
import ssl
import urllib.parse
import urllib.request

HOST = os.environ['CPANEL_HOST']
USER = os.environ['CPANEL_USER']
TOKEN = os.environ['CPANEL_TOKEN']
ROOT = os.environ['THEME_ROOT'].strip('/')
CTX = ssl._create_unverified_context()


def call(func, params):
    url = f'https://{HOST}:2083/execute/Fileman/{func}'
    encoded = urllib.parse.urlencode(params)
    req = urllib.request.Request(url + '?' + encoded)
    req.add_header('Authorization', f'cpanel {USER}:{TOKEN}')
    with urllib.request.urlopen(req, context=CTX, timeout=60) as response:
        payload = json.loads(response.read().decode('utf-8'))
    result = payload.get('result') if isinstance(payload.get('result'), dict) else payload
    if not isinstance(result, dict) or result.get('status') != 1:
        raise RuntimeError(str(result.get('errors') if isinstance(result, dict) else result))
    return result.get('data')


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
    raise RuntimeError('Unexpected payload: ' + rel)

front = read_live('front-page.php')
css = read_live('assets/css/interactive-hero.css')
js = read_live('assets/js/interactive-hero.js')

hero_start = front.find('<section class="g1-hero')
hero_end = front.find('</section>', hero_start)
hero_markup = front[hero_start:hero_end + len('</section>')] if hero_start >= 0 and hero_end >= 0 else 'HERO MARKUP NOT FOUND'

print('=== LIVE HERO MARKUP ===')
print(hero_markup)
print('=== END LIVE HERO MARKUP ===')
print('=== LIVE INTERACTIVE HERO CSS ===')
print(css)
print('=== END LIVE INTERACTIVE HERO CSS ===')
print('=== LIVE INTERACTIVE HERO JS ===')
print(js)
print('=== END LIVE INTERACTIVE HERO JS ===')
