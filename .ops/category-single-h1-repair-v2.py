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
TARGET = 'woocommerce.php'
TARGET_SHA = 'f56f21bcfc21a4c912b6d4d5dd939e716be4ecbf05680b67ef12850f991af369'
PRODUCT_SHA = '70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'
PCAT_SHA = '75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
MARKER = 'GRAMISS_CATEGORY_SINGLE_H1_V2'
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


def read_theme(rel):
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


def write_theme(rel, content):
    directory, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    return api('save_file_content', {
        'dir': ROOT if not directory else ROOT + '/' + directory,
        'file': name,
        'content': content,
        'from_charset': 'UTF-8',
        'to_charset': 'UTF-8',
        'fallback': '0',
    }, True)


def save_public(name, content):
    return api('save_file_content', {
        'dir': 'public_html',
        'file': name,
        'content': content,
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
                'User-Agent': 'GramissCategorySingleH1RepairV2/1.0',
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
    value = re.sub(r'<[^>]+>', ' ', value or '')
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
        if 'canonical' in attr(tag, 'rel').lower().split():
            canonical = attr(tag, 'href')
            break
    return {'title': title, 'description': description, 'robots': robots, 'canonical': norm(canonical)}


def inspect_category(url):
    status, raw, final = get(url + ('&' if '?' in url else '?') + 'g1h1v2=' + str(int(time.time() * 1000)), 180)
    text = raw.decode('utf-8', 'replace')
    h1_tags = re.findall(r'<h1\b[^>]*>.*?</h1>', text, re.I | re.S)
    h1_texts = [strip_markup(x) for x in h1_tags]
    native = [x for x in h1_tags if re.search(r'class=["\'][^"\']*\bpage-title\b', x, re.I)]
    premium = [x for x in h1_tags if re.search(r'id=["\']gramiss-premium-shop-title["\']', x, re.I)]
    return {
        'status': status,
        'final': norm(final),
        'meta': parse_head(raw),
        'h1_count': len(h1_tags),
        'h1_texts': h1_texts,
        'native_count': len(native),
        'premium_count': len(premium),
    }


def sitemap(path):
    status, raw, _ = get(BASE + '/' + path + '?g1h1v2=' + str(int(time.time() * 1000)), 150)
    urls = sorted(html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>', raw.decode('utf-8', 'replace'), re.I))
    return status, urls, hashlib.sha256('\n'.join(urls).encode()).hexdigest()


def purge():
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-h1-purge-v2-' + nonce + '.php'
    php = r'''<?php
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
if (function_exists('wp_cache_flush')) { wp_cache_flush(); }
if (has_action('litespeed_purge_all')) { do_action('litespeed_purge_all'); }
header('Content-Type: text/plain; charset=utf-8');
echo 'PURGED';
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 120)
    print('PURGE', status, raw.decode('utf-8', 'replace')[:120])
    if status != 200 or b'PURGED' not in raw:
        raise RuntimeError('cache purge failed')


def assert_safety(label):
    errors = []
    protected = {path: hashlib.sha256(read_theme(path).encode()).hexdigest() for path in PROTECTED}
    for path, expected in PROTECTED.items():
        if protected.get(path) != expected:
            errors.append('protected drift ' + path)
    ps, pu, ph = sitemap('product-sitemap.xml')
    cs, cu, ch = sitemap('product_cat-sitemap.xml')
    if ps != 200 or len(pu) != 47 or ph != PRODUCT_SHA:
        errors.append('product sitemap drift')
    if cs != 200 or len(cu) != 20 or ch != PCAT_SHA:
        errors.append('product_cat sitemap drift')
    print('SAFETY', label, json.dumps({'protected': protected, 'product': [ps, len(pu), ph], 'product_cat': [cs, len(cu), ch], 'errors': errors}, sort_keys=True))
    if errors:
        raise RuntimeError('; '.join(errors))
    return cu


urls = assert_safety('PRE')
old = read_theme(TARGET)
old_sha = hashlib.sha256(old.encode()).hexdigest()
print('TARGET_PRE', TARGET, old_sha, 'marker', MARKER in old)

pre = {norm(url): inspect_category(url) for url in urls}
pre_errors = []
for url, row in pre.items():
    if row['status'] != 200 or row['h1_count'] != 2 or row['native_count'] != 1 or row['premium_count'] != 1:
        pre_errors.append(url + ' unexpected pre-H1 state ' + json.dumps(row, ensure_ascii=False))
print('PRE_H1_SUMMARY', json.dumps({u: [r['h1_count'], r['native_count'], r['premium_count']] for u, r in pre.items()}, ensure_ascii=False, sort_keys=True))
if pre_errors and MARKER not in old:
    raise SystemExit('FAIL PRECONDITION ' + ' | '.join(pre_errors))

patch = r'''/* GRAMISS_CATEGORY_SINGLE_H1_V2
 * Product-category archives use the Gramiss premium hero as their sole H1.
 * Register this filter before get_header()/woocommerce_content() so WooCommerce
 * never renders its native hidden page-title H1 on product-category archives.
 */
if ( ! function_exists( 'gramiss_category_single_h1_v2' ) ) {
    function gramiss_category_single_h1_v2( $show ) {
        if ( function_exists( 'is_product_category' ) && is_product_category() ) {
            return false;
        }
        return $show;
    }
}
add_filter( 'woocommerce_show_page_title', 'gramiss_category_single_h1_v2', 999 );

'''

changed = False
if MARKER not in old:
    if old_sha != TARGET_SHA:
        raise SystemExit('FAIL TARGET DRIFT expected=' + TARGET_SHA + ' got=' + old_sha)
    anchor = 'get_header();'
    if anchor not in old:
        raise SystemExit('FAIL TARGET ANCHOR MISSING')
    if old.count(anchor) != 1:
        raise SystemExit('FAIL TARGET ANCHOR NOT UNIQUE')
    new = old.replace(anchor, patch + anchor, 1)
    write_theme(TARGET, new)
    changed = True
    print('TARGET_WRITTEN', hashlib.sha256(new.encode()).hexdigest())
else:
    new = old
    print('TARGET_ALREADY_PATCHED')

try:
    purge()
    time.sleep(2)
    post_urls = assert_safety('POST')
    if [norm(x) for x in post_urls] != [norm(x) for x in urls]:
        raise RuntimeError('category sitemap URL set changed')
    post = {norm(url): inspect_category(url) for url in post_urls}
    errors = []
    for url, after in post.items():
        before = pre[url]
        if after['status'] != 200:
            errors.append(url + ' HTTP ' + str(after['status']))
        if after['h1_count'] != 1 or after['native_count'] != 0 or after['premium_count'] != 1:
            errors.append(url + ' H1 state ' + json.dumps(after, ensure_ascii=False))
        if before['meta'] != after['meta']:
            errors.append(url + ' head metadata changed before=' + json.dumps(before['meta'], ensure_ascii=False) + ' after=' + json.dumps(after['meta'], ensure_ascii=False))
        if before['h1_texts'][-1:] != after['h1_texts']:
            errors.append(url + ' premium H1 text changed')
    print('POST_H1_SUMMARY', json.dumps({u: [r['h1_count'], r['native_count'], r['premium_count']] for u, r in post.items()}, ensure_ascii=False, sort_keys=True))
    if errors:
        raise RuntimeError(' | '.join(errors))
except Exception as exc:
    print('VERIFY_FAIL', repr(exc))
    if changed:
        write_theme(TARGET, old)
        purge()
        time.sleep(2)
        restored = read_theme(TARGET)
        restored_sha = hashlib.sha256(restored.encode()).hexdigest()
        print('ROLLBACK_TARGET', restored_sha)
        if restored_sha != old_sha:
            raise SystemExit('CRITICAL ROLLBACK FILE HASH MISMATCH')
        assert_safety('ROLLBACK')
    raise

final_content = read_theme(TARGET)
final_sha = hashlib.sha256(final_content.encode()).hexdigest()
if MARKER not in final_content:
    raise SystemExit('FAIL FINAL MARKER MISSING')
print('PASS CATEGORY SINGLE H1 REPAIR V2', final_sha)
