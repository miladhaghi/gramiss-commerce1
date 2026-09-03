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
CTX = ssl._create_unverified_context()
BASE = 'https://gramiss.ir'


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
    req = urllib.request.Request(safe_url(url), headers={
        'User-Agent': 'GramissPerformanceProductCardSourceScanV1/1.0',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    })
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as response:
        return response.status, response.read().decode('utf-8', 'replace'), response.geturl()


nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
probe = 'gramiss-performance-card-source-' + nonce + '.php'
php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$root = get_stylesheet_directory();
$needles = [
  'gse-media-frame',
  'attachment-full',
  'size-full',
  'wp_get_attachment_image',
  'get_the_post_thumbnail',
  'woocommerce_get_product_thumbnail',
  'woocommerce-loop-product__link',
  'woocommerce_product_get_image',
  'get_image(',
  'thumbnail_id'
];
$out = [];
$it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
foreach ($it as $file) {
  if (!$file->isFile()) continue;
  $ext = strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION));
  if (!in_array($ext, ['php','js','css'], true)) continue;
  $text = @file_get_contents($file->getPathname());
  if ($text === false) continue;
  $hits = [];
  foreach ($needles as $needle) {
    $offset = 0;
    $parts = [];
    while (($pos = stripos($text, $needle, $offset)) !== false && count($parts) < 4) {
      $start = max(0, $pos - 420);
      $parts[] = substr($text, $start, 1100);
      $offset = $pos + strlen($needle);
    }
    if ($parts) $hits[$needle] = $parts;
  }
  if ($hits) {
    $rel = ltrim(str_replace($root, '', $file->getPathname()), '/\\');
    $out[] = [
      'path' => $rel,
      'sha256' => hash_file('sha256', $file->getPathname()),
      'size' => filesize($file->getPathname()),
      'hits' => $hits,
    ];
  }
}
echo wp_json_encode([
  'theme'=>$root,
  'stylesheet'=>get_stylesheet(),
  'template'=>get_template(),
  'matches'=>$out,
], JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''

save(probe, php)
status, raw, _ = get(BASE + '/' + probe + '?t=' + str(int(time.time())), 240)
if status != 200:
    raise SystemExit('FAIL probe HTTP ' + str(status))
state = json.loads(raw)
print('THEME_STATE', json.dumps({
    'theme': state.get('theme'),
    'stylesheet': state.get('stylesheet'),
    'template': state.get('template'),
}, ensure_ascii=False, sort_keys=True))
for row in state.get('matches', []):
    print('SOURCE_MATCH', json.dumps(row, ensure_ascii=False, sort_keys=True))
print('SOURCE_MATCH_COUNT', len(state.get('matches', [])))

status, page, final = get(BASE + '/product-category/tshirt/?perf-source=' + str(int(time.time())), 180)
if status != 200:
    raise SystemExit('FAIL category HTTP ' + str(status))
imgs = []
for tag in re.findall(r'<img\b[^>]*>', page, re.I | re.S):
    if 'gse-media-frame' in page[max(0, page.find(tag)-600):page.find(tag)+len(tag)+100] or 'attachment-full' in tag or 'woocommerce-loop-product__link' in page[max(0, page.find(tag)-800):page.find(tag)+len(tag)+100]:
        def attr(name):
            m = re.search(r'\b' + re.escape(name) + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I | re.S)
            return html.unescape(m.group(1)).strip() if m else ''
        imgs.append({
            'src': attr('src'),
            'srcset': attr('srcset'),
            'sizes': attr('sizes'),
            'class': attr('class'),
            'width': attr('width'),
            'height': attr('height'),
            'loading': attr('loading'),
            'fetchpriority': attr('fetchpriority'),
        })
        if len(imgs) >= 6:
            break
print('RENDERED_PRODUCT_IMAGES', json.dumps(imgs, ensure_ascii=False, sort_keys=True))
if not state.get('matches'):
    raise SystemExit('FAIL no live theme source matches found')
if not imgs:
    raise SystemExit('FAIL no rendered product images found')
print('PASS PERFORMANCE PRODUCT CARD SOURCE SCAN V1 READ ONLY')
