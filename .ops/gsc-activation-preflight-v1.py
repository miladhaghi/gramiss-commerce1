import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://gramiss.ir'
CTX = ssl._create_unverified_context()
REQUIRED_SITEMAPS = {
    'post-sitemap.xml',
    'product-sitemap.xml',
    'product_cat-sitemap.xml',
}


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((
        p.scheme,
        p.netloc,
        urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@'),
        urllib.parse.quote(urllib.parse.unquote(p.query), safe='=&%:@,+'),
        p.fragment,
    ))


def get(url, timeout=120):
    url = safe_url(url)
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'GramissGSCActivationPreflight/1.0',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            })
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
                return r.status, r.read(), dict(r.headers), r.geturl()
        except urllib.error.HTTPError as e:
            return e.code, e.read(), dict(e.headers), e.geturl()
        except Exception as e:
            last = e
            print('HTTP_RETRY', attempt + 1, url, repr(e))
            time.sleep(attempt + 1)
    raise last


def robots_blocks_root(text):
    active = False
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or ':' not in line:
            continue
        key, value = [x.strip() for x in line.split(':', 1)]
        key = key.lower()
        if key == 'user-agent':
            active = value == '*'
        elif key == 'disallow' and active and value == '/':
            return True
    return False


def sitemap_locs(raw):
    text = raw.decode('utf-8', 'replace')
    return [x.strip() for x in re.findall(r'<loc>\s*(.*?)\s*</loc>', text, flags=re.I | re.S)]


def basename(url):
    return urllib.parse.unquote(urllib.parse.urlsplit(url).path).rstrip('/').rsplit('/', 1)[-1]


errors = []
nonce = str(int(time.time()))

home_status, _, home_headers, home_final = get(BASE + '/?gsc-preflight=' + nonce)
print('GSC_HOME', json.dumps({
    'status': home_status,
    'final': home_final,
    'x_robots_tag': home_headers.get('X-Robots-Tag', ''),
}, ensure_ascii=False, sort_keys=True))
if home_status != 200:
    errors.append('home HTTP ' + str(home_status))
if 'noindex' in home_headers.get('X-Robots-Tag', '').lower():
    errors.append('home X-Robots-Tag noindex')

robots_status, robots_raw, _, _ = get(BASE + '/robots.txt?t=' + nonce)
robots = robots_raw.decode('utf-8', 'replace')
robots_sitemap_lines = [
    x.split(':', 1)[1].strip()
    for x in robots.splitlines()
    if x.strip().lower().startswith('sitemap:')
]
robots_summary = {
    'status': robots_status,
    'blocks_root_for_star': robots_blocks_root(robots),
    'sitemap_lines': robots_sitemap_lines,
}
print('GSC_ROBOTS', json.dumps(robots_summary, ensure_ascii=False, sort_keys=True))
if robots_status != 200:
    errors.append('robots HTTP ' + str(robots_status))
if robots_summary['blocks_root_for_star']:
    errors.append('robots blocks root for User-agent *')
if not any('sitemap_index.xml' in x for x in robots_sitemap_lines):
    errors.append('robots missing sitemap_index.xml declaration')

index_status, index_raw, _, _ = get(BASE + '/sitemap_index.xml?t=' + nonce)
index_text = index_raw.decode('utf-8', 'replace')
index_locs = sitemap_locs(index_raw)
index_names = {basename(x) for x in index_locs}
print('GSC_SITEMAP_INDEX', json.dumps({
    'status': index_status,
    'is_sitemapindex': '<sitemapindex' in index_text.lower(),
    'count': len(index_locs),
    'members': sorted(index_names),
}, ensure_ascii=False, sort_keys=True))
if index_status != 200:
    errors.append('sitemap index HTTP ' + str(index_status))
if '<sitemapindex' not in index_text.lower():
    errors.append('sitemap index root is not sitemapindex')
for required in sorted(REQUIRED_SITEMAPS):
    if required not in index_names:
        errors.append('sitemap index missing ' + required)

for name in sorted(REQUIRED_SITEMAPS):
    status, raw, _, final = get(BASE + '/' + name + '?t=' + nonce)
    text = raw.decode('utf-8', 'replace')
    locs = sitemap_locs(raw)
    row = {
        'name': name,
        'status': status,
        'final': final,
        'is_urlset': '<urlset' in text.lower(),
        'url_count': len(locs),
    }
    print('GSC_SITEMAP_MEMBER', json.dumps(row, ensure_ascii=False, sort_keys=True))
    if status != 200:
        errors.append(name + ' HTTP ' + str(status))
    if '<urlset' not in text.lower():
        errors.append(name + ' root is not urlset')
    if not locs:
        errors.append(name + ' contains no loc entries')

print('GSC_ACTIVATION_ERRORS', json.dumps(errors, ensure_ascii=False))
if errors:
    raise SystemExit('FAIL GSC ACTIVATION PREFLIGHT V1')
print('PASS GSC ACTIVATION PREFLIGHT V1 READ ONLY')
