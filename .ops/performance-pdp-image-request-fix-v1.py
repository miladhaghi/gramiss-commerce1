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
TARGET_PDP = 'https://gramiss.ir/product/%d8%b4%d9%84%d9%88%d8%a7%d8%b1-%d8%ac%db%8c%d9%86-%d8%a8%d8%a7%d9%84%d9%86%db%8c-%d8%aa%db%8c%d9%86%d8%aa-%d8%b3%d8%a8%d8%b2/'

EXPECTED = {
    'header.php': '94456594e7f2699b677e9c4193c0626a67e5fdce573aa74180cbd00d1539f66f',
    'assets/js/product-runtime-gallery-fix.js': 'b22a84f502748116d38d9a76039a341b57369c0e16daafcbb66454e09f0632de',
    'assets/js/product-mobile-v1-4.js': 'ad34ed1b570a3d5f13d5fb8493d933b624eda9b75d2d2fb1f6dc16f9ae0841e8',
}
PROTECTED = {
    'front-page.php': '0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}

OLD_RELATED_FILTER = "add_filter( 'single_product_archive_thumbnail_size', function( $size ) { return 'full'; } );"
NEW_RELATED_FILTER = r"""add_filter( 'single_product_archive_thumbnail_size', function( $size ) { return 'gramiss-product-card'; } );
add_filter( 'wp_get_attachment_image_attributes', function( $attr, $attachment, $size ) {
  if ( function_exists( 'is_product' ) && is_product() && $size === 'gramiss-product-card' && ! empty( $attr['class'] ) && strpos( $attr['class'], 'attachment-gramiss-product-card' ) !== false ) {
    $attr['sizes'] = '(max-width: 767px) 82vw, (max-width: 1200px) 33vw, 25vw';
    $attr['loading'] = 'lazy';
    $attr['decoding'] = 'async';
  }
  return $attr;
}, 30, 3 );
add_filter( 'woocommerce_gallery_image_html_attachment_image_params', function( $params, $attachment_id, $image_size, $main_image ) {
  $params['loading'] = $main_image ? 'eager' : 'lazy';
  $params['decoding'] = 'async';
  if ( $main_image ) {
    $params['fetchpriority'] = 'high';
  } else {
    unset( $params['fetchpriority'] );
  }
  return $params;
}, 30, 4 );"""

OLD_GALLERY_SOURCE = "src: img.getAttribute('data-large_image') || img.getAttribute('data-src') || img.currentSrc || img.src,"
NEW_GALLERY_SOURCE = "src: img.getAttribute('src') || img.currentSrc || img.getAttribute('data-src') || img.getAttribute('data-large_image') || img.src,"

OLD_APPLY_IMAGE = """function applyImage(node,data){
      if(!node || !data) return;
      var src=data.full_src || data.src || data.url || '';
      if(src) node.src=src;
      var srcset=data.srcset || data.src_set || '';
      if(srcset) node.srcset=srcset; else node.removeAttribute('srcset');
      if(data.sizes) node.sizes=data.sizes; else node.removeAttribute('sizes');
      node.alt=data.alt || '';
    }"""
NEW_APPLY_IMAGE = """function applyImage(node,data){
      if(!node || !data) return;
      var src=data.src || data.url || data.full_src || '';
      var srcset=data.srcset || data.src_set || '';
      if(srcset) node.srcset=srcset; else node.removeAttribute('srcset');
      node.sizes=node.classList.contains('g3-dual-image-secondary')
        ? '(max-width: 767px) 38vw, (max-width: 1200px) 18vw, 220px'
        : '(max-width: 767px) 66vw, (max-width: 1200px) 42vw, 520px';
      if(src) node.src=src;
      node.alt=data.alt || '';
    }"""

OLD_STYLE_IMAGE = """const image =
      doc.querySelector('meta[property=\"og:image\"]')?.content ||
      doc.querySelector('.woocommerce-product-gallery__image img')?.getAttribute('data-large_image') ||
      doc.querySelector('.woocommerce-product-gallery__image img')?.src ||
      doc.querySelector('.g3-gallery img, .product img')?.src || '';"""
NEW_STYLE_IMAGE = """const productImage = doc.querySelector('.woocommerce-product-gallery__image img');
    const image =
      productImage?.getAttribute('src') ||
      productImage?.src ||
      doc.querySelector('.g3-gallery img, .product img')?.getAttribute('src') ||
      doc.querySelector('meta[property=\"og:image\"]')?.content || '';"""

OLD_STYLE_CARD = "const img = document.createElement('img');\n    img.src = item.image;\n    img.alt = item.name;\n    img.loading = index === 0 ? 'eager' : 'lazy';\n    img.decoding = 'async';\n    media.append(img);"
NEW_STYLE_CARD = "const img = document.createElement('img');\n    img.src = item.image;\n    img.alt = item.name;\n    img.loading = 'lazy';\n    img.fetchPriority = 'low';\n    img.decoding = 'async';\n    media.append(img);"


def api(fn, params, post=False):
    url = f'https://{HOST}:2083/execute/Fileman/{fn}'
    encoded = urllib.parse.urlencode(params).encode()
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
    req = urllib.request.Request(safe_url(url), headers={
        'User-Agent': 'GramissPDPImageRequestFixV1/1.0',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    })
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as response:
        return response.status, response.read().decode('utf-8', 'replace'), response.geturl()


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def flush():
    helper = 'gramiss-performance-flush-' + str(int(time.time())) + '.php'
    php = "<?php require __DIR__.'/wp-load.php'; if(function_exists('wp_cache_flush'))wp_cache_flush(); if(function_exists('opcache_reset'))@opcache_reset(); @unlink(__FILE__); header('Content-Type:text/plain'); echo 'OK'; ?>"
    save_root(helper, php)
    status, body, _ = get(BASE + '/' + helper + '?t=' + str(int(time.time())), 120)
    if status != 200 or body.strip() != 'OK':
        raise RuntimeError('cache flush helper failed')


def protected_state():
    return {path: sha(read_theme(path)) for path in PROTECTED}


def attr(tag, name):
    m = re.search(r'\b' + re.escape(name) + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I | re.S)
    return html.unescape(m.group(1)).strip() if m else ''


def rendered_verify():
    errors = []
    status, page, _ = get(TARGET_PDP + '?perf-image-fix=' + str(int(time.time())), 180)
    if status != 200:
        return ['PDP HTTP ' + str(status)]

    if 'product-runtime-gallery-fix.js?v=20260903-perf1' not in page:
        errors.append('gallery cache-bust version missing')
    if 'product-mobile-v1-4.js?v=20260903-perf1' not in page:
        errors.append('style-card cache-bust version missing')

    gallery = []
    related = []
    for match in re.finditer(r'<img\b[^>]*>', page, re.I | re.S):
        tag = match.group(0)
        context = page[max(0, match.start()-900):match.end()+180].lower()
        if 'woocommerce-product-gallery' in context and len(gallery) < 3:
            gallery.append(tag)
        if ('related products' in context or 'woocommerce-loop-product__link' in context) and ('attachment-' in tag) and len(related) < 4:
            related.append(tag)

    print('VERIFY_GALLERY_TAGS', json.dumps(gallery, ensure_ascii=False))
    print('VERIFY_RELATED_TAGS', json.dumps(related, ensure_ascii=False))
    if len(gallery) < 3:
        errors.append('too few native gallery images')
    else:
        if attr(gallery[0], 'loading') != 'eager':
            errors.append('main gallery image not eager')
        if attr(gallery[0], 'fetchpriority') != 'high':
            errors.append('main gallery image not high priority')
        for i, tag in enumerate(gallery[1:3], 1):
            if attr(tag, 'loading') != 'lazy':
                errors.append(f'gallery image {i} not lazy')

    if len(related) < 4:
        errors.append('too few related images')
    for i, tag in enumerate(related[:4]):
        cls = attr(tag, 'class')
        sizes = attr(tag, 'sizes')
        src = attr(tag, 'src')
        if 'attachment-full' in cls or 'size-full' in cls:
            errors.append(f'related image {i} still full class')
        if 'attachment-gramiss-product-card' not in cls:
            errors.append(f'related image {i} missing gramiss card class')
        if '82vw' not in sizes:
            errors.append(f'related image {i} missing 82vw sizes')
        if not re.search(r'-\d+x\d+\.(?:png|jpe?g|webp)(?:\?|$)', src, re.I):
            errors.append(f'related image {i} src not intermediate: {src}')

    if len(re.findall(r'<h1\b', page, re.I)) != 1:
        errors.append('PDP H1 count changed')
    return errors


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label} expected once, found {count}')
    return text.replace(old, new, 1)


def main():
    before = {path: read_theme(path) for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = sha(before[path])
        print('BEFORE_SHA', path, actual)
        if actual != expected:
            raise SystemExit(f'REFUSE live drift {path}: {actual}')

    protected_before = protected_state()
    for path, expected in PROTECTED.items():
        if protected_before[path] != expected:
            raise SystemExit('REFUSE protected drift ' + path)

    header = before['header.php']
    gallery = before['assets/js/product-runtime-gallery-fix.js']
    style = before['assets/js/product-mobile-v1-4.js']

    if len(re.findall(r'product-runtime-gallery-fix\.js\?v=[^\"\']+', header)) != 1:
        raise SystemExit('REFUSE gallery loader ambiguity')
    if len(re.findall(r'product-mobile-v1-4\.js\?v=[^\"\']+', header)) != 1:
        raise SystemExit('REFUSE v1-4 style loader ambiguity')

    new_header = replace_once(header, OLD_RELATED_FILTER, NEW_RELATED_FILTER, 'related filter')
    new_header = re.sub(r'product-runtime-gallery-fix\.js\?v=[^\"\']+', 'product-runtime-gallery-fix.js?v=20260903-perf1', new_header, count=1)
    new_header = re.sub(r'product-mobile-v1-4\.js\?v=[^\"\']+', 'product-mobile-v1-4.js?v=20260903-perf1', new_header, count=1)

    new_gallery = replace_once(gallery, OLD_GALLERY_SOURCE, NEW_GALLERY_SOURCE, 'gallery source')
    new_gallery = replace_once(new_gallery, OLD_APPLY_IMAGE, NEW_APPLY_IMAGE, 'gallery applyImage')

    new_style = replace_once(style, OLD_STYLE_IMAGE, NEW_STYLE_IMAGE, 'style image parser')
    new_style = replace_once(new_style, OLD_STYLE_CARD, NEW_STYLE_CARD, 'style card image')

    changed = {
        'header.php': new_header,
        'assets/js/product-runtime-gallery-fix.js': new_gallery,
        'assets/js/product-mobile-v1-4.js': new_style,
    }
    expected_after = {path: sha(text) for path, text in changed.items()}

    try:
        for path, text in changed.items():
            save_theme(path, text)
        flush()

        errors = []
        for path, expected_sha in expected_after.items():
            actual = sha(read_theme(path))
            print('AFTER_SHA', path, actual)
            if actual != expected_sha:
                errors.append('stored mismatch ' + path)

        protected_after = protected_state()
        for path in PROTECTED:
            if protected_after[path] != protected_before[path]:
                errors.append('protected file changed ' + path)

        errors.extend(rendered_verify())
        print('VERIFY_ERRORS', json.dumps(errors, ensure_ascii=False))
        if errors:
            raise RuntimeError('; '.join(errors))
    except Exception:
        for path, text in before.items():
            save_theme(path, text)
        flush()
        rollback_errors = []
        for path, text in before.items():
            if sha(read_theme(path)) != sha(text):
                rollback_errors.append(path)
        print('ROLLBACK_ERRORS', json.dumps(rollback_errors))
        if rollback_errors:
            raise RuntimeError('rollback mismatch ' + ','.join(rollback_errors))
        print('ROLLBACK PERFORMANCE PDP IMAGE REQUEST FIX V1 COMPLETE')
        raise

    print('PASS PERFORMANCE PDP IMAGE REQUEST FIX V1')


if __name__ == '__main__':
    main()
