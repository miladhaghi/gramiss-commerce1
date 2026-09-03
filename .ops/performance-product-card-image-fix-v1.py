#!/usr/bin/env python3
import hashlib
import html
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
ROOT = 'public_html/wp-content/themes/gramiss-theme-next'
CTX = ssl._create_unverified_context()
BASE = 'https://gramiss.ir'
HEADER_EXPECTED_SHA = 'fa5d2cbe59a3464de54d2f936ce66db13ef6ae95592c2626ca7319427a7be889'
PRODUCT_SHA = '70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'
PCAT_SHA = '75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PROTECTED = {
    'front-page.php': '0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}
OLD = "$product->get_image('full',array('loading'=>'lazy','decoding'=>'async'))"
NEW = "$product->get_image('gramiss-product-card',array('loading'=>'lazy','decoding'=>'async','sizes'=>'(max-width: 900px) 50vw, (max-width: 1100px) 33vw, 25vw'))"


def api(fn, params, post=False):
    url = f'https://{HOST}:2083/execute/Fileman/{fn}'
    encoded = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url if post else url + '?' + encoded.decode(), data=encoded if post else None, method='POST' if post else 'GET')
    req.add_header('Authorization', f'cpanel {USER}:{TOKEN}')
    if post:
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, context=CTX, timeout=90) as response:
        payload = json.loads(response.read().decode('utf-8', 'replace'))
    result = payload.get('result') if isinstance(payload.get('result'), dict) else payload
    if not isinstance(result, dict) or result.get('status') != 1:
        raise RuntimeError(str(result))
    return result.get('data')


def extract_content(data):
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        for key in ('content', 'file_content', 'data'):
            if isinstance(data.get(key), str):
                return data[key]
    return ''


def read_theme(rel):
    directory, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    data = api('get_file_content', {
        'dir': ROOT if not directory else ROOT + '/' + directory,
        'file': name,
        'from_charset': '_DETECT_',
        'to_charset': 'utf-8',
    })
    return extract_content(data)


def save_theme(rel, content):
    directory, name = rel.rsplit('/', 1) if '/' in rel else ('', rel)
    return api('save_file_content', {
        'dir': ROOT if not directory else ROOT + '/' + directory,
        'file': name,
        'content': content,
        'from_charset': 'UTF-8',
        'to_charset': 'UTF-8',
        'fallback': '0',
    }, True)


def save_root(name, content):
    return api('save_file_content', {
        'dir': 'public_html', 'file': name, 'content': content,
        'from_charset': 'UTF-8', 'to_charset': 'UTF-8', 'fallback': '0',
    }, True)


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@'), urllib.parse.quote(urllib.parse.unquote(p.query), safe='=&%:@,+'), p.fragment))


def get(url, timeout=180):
    req = urllib.request.Request(safe_url(url), headers={'User-Agent':'GramissPerformanceImageFixV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as response:
        return response.status, response.read().decode('utf-8','replace'), response.geturl()


def flush():
    helper = 'gramiss-performance-flush-' + str(int(time.time())) + '.php'
    php = "<?php require __DIR__.'/wp-load.php'; if(function_exists('wp_cache_flush'))wp_cache_flush(); if(function_exists('opcache_reset'))@opcache_reset(); @unlink(__FILE__); header('Content-Type:text/plain'); echo 'OK'; ?>"
    save_root(helper, php)
    status, body, _ = get(BASE + '/' + helper + '?t=' + str(int(time.time())), 120)
    if status != 200 or body.strip() != 'OK':
        raise RuntimeError('cache flush helper failed')


def sitemap(path):
    status, text, _ = get(BASE + '/' + path + '?t=' + str(int(time.time())), 150)
    urls = sorted(html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>', text, re.I))
    return status, urls, hashlib.sha256('\n'.join(urls).encode()).hexdigest()


def safety():
    errors = []
    ph = {p: hashlib.sha256(read_theme(p).encode()).hexdigest() for p in PROTECTED}
    for p, expected in PROTECTED.items():
        if ph[p] != expected:
            errors.append('protected drift ' + p)
    ps, pu, psha = sitemap('product-sitemap.xml')
    cs, cu, csha = sitemap('product_cat-sitemap.xml')
    if ps != 200 or len(pu) != 47 or psha != PRODUCT_SHA:
        errors.append('product sitemap drift')
    if cs != 200 or len(cu) != 20 or csha != PCAT_SHA:
        errors.append('category sitemap drift')
    return errors


def rendered_verify():
    status, page, final = get(BASE + '/product-category/tshirt/?perf-fix=' + str(int(time.time())), 180)
    if status != 200:
        return ['category HTTP ' + str(status)]
    errors = []
    tags = re.findall(r'<img\b[^>]*>', page, re.I | re.S)
    product_tags = [t for t in tags if 'attachment-gramiss-product-card' in t or 'attachment-full' in t]
    if len(product_tags) < 6:
        errors.append('too few rendered product image tags')
    for i, tag in enumerate(product_tags[:6]):
        def attr(name):
            m = re.search(r'\b' + re.escape(name) + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I | re.S)
            return html.unescape(m.group(1)).strip() if m else ''
        cls = attr('class')
        src = attr('src')
        srcset = attr('srcset')
        sizes = attr('sizes')
        if 'attachment-full' in cls or 'size-full' in cls:
            errors.append(f'image {i} still full')
        if 'attachment-gramiss-product-card' not in cls:
            errors.append(f'image {i} missing card class')
        if not srcset:
            errors.append(f'image {i} missing srcset')
        if '50vw' not in sizes or '33vw' not in sizes or '25vw' not in sizes:
            errors.append(f'image {i} missing responsive sizes')
        if not re.search(r'-\d+x\d+\.(?:png|jpe?g|webp)(?:\?|$)', src, re.I):
            errors.append(f'image {i} src is not intermediate: {src}')
    h1_count = len(re.findall(r'<h1\b', page, re.I))
    if h1_count != 1:
        errors.append('category H1 count ' + str(h1_count))
    return errors


def main():
    pre = safety()
    if pre:
        raise SystemExit('REFUSE preflight: ' + '; '.join(pre))
    old = read_theme('header.php')
    old_sha = hashlib.sha256(old.encode()).hexdigest()
    print('HEADER_BEFORE_SHA', old_sha)
    if old_sha != HEADER_EXPECTED_SHA:
        raise SystemExit('REFUSE header SHA mismatch')
    if old.count(OLD) != 1:
        raise SystemExit('REFUSE old image call count != 1')
    if NEW in old:
        raise SystemExit('REFUSE new call already present')
    new = old.replace(OLD, NEW, 1)
    expected_new_sha = hashlib.sha256(new.encode()).hexdigest()
    try:
        save_theme('header.php', new)
        flush()
        stored = read_theme('header.php')
        stored_sha = hashlib.sha256(stored.encode()).hexdigest()
        print('HEADER_AFTER_SHA', stored_sha)
        errors = []
        if stored_sha != expected_new_sha:
            errors.append('stored header mismatch')
        errors.extend(rendered_verify())
        errors.extend(safety())
        print('VERIFY_ERRORS', json.dumps(errors, ensure_ascii=False))
        if errors:
            raise RuntimeError('; '.join(errors))
    except Exception:
        save_theme('header.php', old)
        flush()
        rolled = hashlib.sha256(read_theme('header.php').encode()).hexdigest()
        print('ROLLBACK_HEADER_SHA', rolled)
        if rolled != old_sha:
            raise RuntimeError('rollback header mismatch')
        print('ROLLBACK PERFORMANCE PRODUCT CARD IMAGE FIX V1 COMPLETE')
        raise
    print('PASS PERFORMANCE PRODUCT CARD IMAGE FIX V1')


if __name__ == '__main__':
    main()
