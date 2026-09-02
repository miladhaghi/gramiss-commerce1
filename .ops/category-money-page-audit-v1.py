import hashlib
import html
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

HOST = os.environ['CPANEL_HOST']
USER = os.environ['CPANEL_USER']
TOKEN = os.environ['CPANEL_TOKEN']
ROOT = os.environ['THEME_ROOT'].strip('/')
CTX = ssl._create_unverified_context()
BASE = 'https://gramiss.ir'
PRODUCT_SHA = '70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'
PCAT_SHA = '75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PROTECTED = {
    'front-page.php': '0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}


def api(fn, params, post=False):
    url = f'https://{HOST}:2083/execute/Fileman/{fn}'
    encoded = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                url if post else url + '?' + encoded.decode(),
                data=encoded if post else None,
                method='POST' if post else 'GET',
            )
            req.add_header('Authorization', f'cpanel {USER}:{TOKEN}')
            if post:
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, context=CTX, timeout=90) as response:
                payload = json.loads(response.read().decode('utf-8', 'replace'))
            result = payload.get('result') if isinstance(payload.get('result'), dict) else payload
            if not isinstance(result, dict) or result.get('status') != 1:
                raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last = exc
            print('API_RETRY', fn, attempt + 1, exc)
            time.sleep(attempt + 1)
    raise last


def theme(rel):
    directory, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    data = api('get_file_content', {
        'dir': ROOT if not directory else ROOT + '/' + directory,
        'file': name,
        'from_charset': '_DETECT_',
        'to_charset': 'utf-8',
    })
    if isinstance(data, dict):
        for key in ('content', 'file_content', 'data'):
            if isinstance(data.get(key), str):
                return data[key]
    return data if isinstance(data, str) else ''


def save(name, text):
    return api('save_file_content', {
        'dir': 'public_html',
        'file': name,
        'content': text,
        'from_charset': 'UTF-8',
        'to_charset': 'UTF-8',
        'fallback': '0',
    }, True)


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((
        p.scheme,
        p.netloc,
        urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@'),
        urllib.parse.quote(urllib.parse.unquote(p.query), safe='=&%:@,+'),
        p.fragment,
    ))


def get(url, timeout=180):
    last = None
    url = safe_url(url)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'GramissCategoryMoneyPageAuditV1/1.0',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            })
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as response:
                return response.status, response.read(), response.geturl()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), exc.geturl()
        except Exception as exc:
            last = exc
            print('HTTP_RETRY', attempt + 1, url, exc)
            time.sleep(attempt + 1)
    raise last


def norm(url):
    if not url:
        return ''
    return urllib.parse.unquote(url).split('?', 1)[0].rstrip('/') + '/'


def strip_markup(value):
    value = re.sub(r'<script\b[^>]*>.*?</script>', ' ', value or '', flags=re.I | re.S)
    value = re.sub(r'<style\b[^>]*>.*?</style>', ' ', value, flags=re.I | re.S)
    value = re.sub(r'<[^>]+>', ' ', value)
    return re.sub(r'\s+', ' ', html.unescape(value)).strip()


def attr(tag, name):
    match = re.search(r'\b' + re.escape(name) + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return html.unescape(match.group(1)).strip() if match else ''


def parse_head(raw):
    text = raw.decode('utf-8', 'replace')
    head = text.split('</head>', 1)[0]
    title_match = re.search(r'<title[^>]*>(.*?)</title>', head, re.I | re.S)
    title = strip_markup(title_match.group(1)) if title_match else ''
    description = ''
    robots = ''
    for tag in re.findall(r'<meta\b[^>]*>', head, re.I | re.S):
        name = attr(tag, 'name').lower()
        if name == 'description':
            description = attr(tag, 'content')
        elif name == 'robots':
            robots = attr(tag, 'content')
    canonical = ''
    for tag in re.findall(r'<link\b[^>]*>', head, re.I | re.S):
        rel = attr(tag, 'rel').lower().split()
        if 'canonical' in rel:
            canonical = attr(tag, 'href')
            break
    return {'title': title, 'description': description, 'robots': robots, 'canonical': canonical}


def sitemap(path):
    status, raw, _ = get(BASE + '/' + path + '?t=' + str(int(time.time())), 150)
    urls = [html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>', raw.decode('utf-8', 'replace'), re.I)]
    return status, sorted(urls)


safety_errors = []
protected = {path: hashlib.sha256(theme(path).encode()).hexdigest() for path in PROTECTED}
print('PROTECTED', json.dumps(protected, sort_keys=True))
for path, expected in PROTECTED.items():
    if protected.get(path) != expected:
        safety_errors.append('protected drift ' + path)

prod_status, product_urls = sitemap('product-sitemap.xml')
pcat_status, pcat_urls = sitemap('product_cat-sitemap.xml')
prod_sha = hashlib.sha256('\n'.join(product_urls).encode()).hexdigest()
pcat_sha = hashlib.sha256('\n'.join(pcat_urls).encode()).hexdigest()
print('SITEMAP_BASELINE', 'product', prod_status, len(product_urls), prod_sha, 'product_cat', pcat_status, len(pcat_urls), pcat_sha)
if prod_status != 200 or len(product_urls) != 47 or prod_sha != PRODUCT_SHA:
    safety_errors.append('product sitemap drift')
if pcat_status != 200 or len(pcat_urls) != 20 or pcat_sha != PCAT_SHA:
    safety_errors.append('product_cat sitemap drift')

nonce = hashlib.sha256((str(time.time()) + protected.get('front-page.php', '')).encode()).hexdigest()[:14]
probe = 'gramiss-category-money-page-audit-v1-' + nonce + '.php'
php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$terms = get_terms(['taxonomy' => 'product_cat', 'hide_empty' => false]);
$out = [];
if (!is_wp_error($terms)) {
  foreach ($terms as $t) {
    $url = get_term_link($t);
    if (is_wp_error($url)) { $url = ''; }
    $out[] = [
      'id' => (int)$t->term_id,
      'slug' => $t->slug,
      'name' => $t->name,
      'parent' => (int)$t->parent,
      'count' => (int)$t->count,
      'description' => $t->description,
      'url' => $url,
      'rank_math_title' => get_term_meta($t->term_id, 'rank_math_title', true),
      'rank_math_description' => get_term_meta($t->term_id, 'rank_math_description', true),
      'rank_math_focus_keyword' => get_term_meta($t->term_id, 'rank_math_focus_keyword', true),
      'rank_math_robots' => get_term_meta($t->term_id, 'rank_math_robots', true),
    ];
  }
}
echo wp_json_encode(['terms' => $out], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
?>'''
save(probe, php)
probe_status, probe_raw, _ = get(BASE + '/' + probe + '?t=' + str(int(time.time())), 240)
try:
    state = json.loads(probe_raw.decode('utf-8', 'replace')) if probe_status == 200 else {}
except Exception as exc:
    state = {}
    safety_errors.append('probe json ' + str(exc))
if probe_status != 200:
    safety_errors.append('probe http ' + str(probe_status))

terms = state.get('terms', []) if isinstance(state, dict) else []
by_url = {norm(t.get('url')): t for t in terms if isinstance(t, dict) and t.get('url')}
findings = []
for url in pcat_urls:
    term = by_url.get(norm(url), {})
    status, raw, final = get(url + ('&' if '?' in url else '?') + 't=' + str(int(time.time())), 180)
    text = raw.decode('utf-8', 'replace')
    meta = parse_head(raw)
    h1_raw = re.findall(r'<h1\b[^>]*>(.*?)</h1>', text, re.I | re.S)
    h1s = [strip_markup(x) for x in h1_raw]
    body_text = strip_markup(text.split('<body', 1)[-1])
    term_description = strip_markup(term.get('description', ''))
    description_rendered = False
    if term_description:
        sample = term_description[:60].strip()
        description_rendered = bool(sample and sample in body_text)
    product_links = {
        norm(x) for x in re.findall(r'href=["\']([^"\']+)', text, re.I)
        if '/product/' in x and 'gramiss.ir' in x
    }
    robots = meta.get('robots', '').lower()
    canonical_ok = norm(meta.get('canonical')) == norm(url)
    flags = []
    if status != 200:
        flags.append('HTTP')
    if 'noindex' in robots or 'index' not in robots:
        flags.append('ROBOTS')
    if not canonical_ok:
        flags.append('CANONICAL')
    if len(h1s) != 1:
        flags.append('H1')
    if not meta.get('description'):
        flags.append('META_DESCRIPTION_MISSING')
    elif len(meta['description']) < 90:
        flags.append('META_DESCRIPTION_SHORT')
    elif len(meta['description']) > 180:
        flags.append('META_DESCRIPTION_LONG')
    if not meta.get('title'):
        flags.append('TITLE_MISSING')
    elif len(meta['title']) < 20:
        flags.append('TITLE_SHORT')
    elif len(meta['title']) > 70:
        flags.append('TITLE_LONG')
    if len(term_description) < 120:
        flags.append('THIN_TERM_DESCRIPTION')
    elif not description_rendered:
        flags.append('TERM_DESCRIPTION_NOT_RENDERED')
    if not term:
        flags.append('TERM_STATE_NOT_FOUND')

    technical = any(x in flags for x in ('HTTP', 'ROBOTS', 'CANONICAL', 'H1', 'TERM_STATE_NOT_FOUND'))
    metadata_gap = any(x.startswith('META_') or x.startswith('TITLE_') for x in flags)
    content_gap = any(x.startswith('THIN_') or x.startswith('TERM_DESCRIPTION_') for x in flags)
    priority = 'P0' if technical else ('P1' if metadata_gap else ('P2' if content_gap else 'PASS'))
    row = {
        'priority': priority,
        'id': term.get('id'),
        'slug': term.get('slug'),
        'name': term.get('name'),
        'parent': term.get('parent'),
        'count': term.get('count'),
        'url': url,
        'http': status,
        'final': final,
        'title': meta.get('title'),
        'title_chars': len(meta.get('title', '')),
        'meta_description': meta.get('description'),
        'meta_description_chars': len(meta.get('description', '')),
        'robots': meta.get('robots'),
        'canonical': meta.get('canonical'),
        'canonical_ok': canonical_ok,
        'h1_count': len(h1s),
        'h1': h1s[0] if len(h1s) == 1 else h1s,
        'term_description_chars': len(term_description),
        'term_description_rendered': description_rendered,
        'visible_product_links': len(product_links),
        'rank_math_title_override': term.get('rank_math_title', ''),
        'rank_math_description_override': term.get('rank_math_description', ''),
        'rank_math_focus_keyword': term.get('rank_math_focus_keyword', ''),
        'rank_math_robots_override': term.get('rank_math_robots', ''),
        'flags': flags,
    }
    findings.append(row)
    print('CATEGORY_AUDIT', json.dumps(row, ensure_ascii=False, sort_keys=True))

summary = {
    'total': len(findings),
    'P0': sum(1 for x in findings if x['priority'] == 'P0'),
    'P1': sum(1 for x in findings if x['priority'] == 'P1'),
    'P2': sum(1 for x in findings if x['priority'] == 'P2'),
    'PASS': sum(1 for x in findings if x['priority'] == 'PASS'),
}
print('CATEGORY_AUDIT_SUMMARY', json.dumps(summary, ensure_ascii=False, sort_keys=True))
print('SAFETY_ERRORS', json.dumps(safety_errors, ensure_ascii=False))
if safety_errors:
    raise SystemExit('FAIL CATEGORY MONEY PAGE AUDIT V1 SAFETY GUARDS')
if len(findings) != 20:
    raise SystemExit('FAIL CATEGORY MONEY PAGE AUDIT V1 INVENTORY')
print('PASS CATEGORY MONEY PAGE AUDIT V1 READ ONLY')
