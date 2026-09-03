#!/usr/bin/env python3
import hashlib
import json
import os
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
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@'), p.query, p.fragment))

nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
probe = 'gramiss-performance-image-size-facts-' + nonce + '.php'
php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);

$wanted = ['thumbnail','medium','large','woocommerce_thumbnail','woocommerce_single','gramiss-product-card','full'];
$registered = wp_get_registered_image_subsizes();
$reg = [];
foreach ($wanted as $s) {
  if ($s === 'full') { $reg[$s] = ['native'=>true]; continue; }
  $reg[$s] = isset($registered[$s]) ? $registered[$s] : null;
}

function gramiss_size_info($id, $size) {
  $src = wp_get_attachment_image_src($id, $size);
  $srcset = wp_get_attachment_image_srcset($id, $size);
  $inter = $size === 'full' ? false : image_get_intermediate_size($id, $size);
  $fullpath = get_attached_file($id);
  $path = $fullpath;
  if ($inter && !empty($inter['path'])) {
    $uploads = wp_get_upload_dir();
    $path = trailingslashit($uploads['basedir']) . ltrim($inter['path'], '/');
  }
  return [
    'url' => $src ? $src[0] : '',
    'width' => $src ? (int)$src[1] : 0,
    'height' => $src ? (int)$src[2] : 0,
    'is_intermediate' => $src ? (bool)$src[3] : false,
    'has_intermediate_record' => (bool)$inter,
    'bytes' => ($path && is_file($path)) ? filesize($path) : null,
    'srcset' => $srcset ?: '',
  ];
}

$products = wc_get_products([
  'status' => 'publish',
  'limit' => 3,
  'category' => ['tshirt'],
  'orderby' => 'ID',
  'order' => 'ASC',
]);
$out = [];
foreach ($products as $product) {
  $id = $product->get_image_id();
  if (!$id) continue;
  $sizes = [];
  foreach ($wanted as $s) $sizes[$s] = gramiss_size_info($id, $s);
  $out[] = [
    'product_id' => $product->get_id(),
    'title' => $product->get_name(),
    'image_id' => $id,
    'sizes' => $sizes,
  ];
}

echo wp_json_encode(['registered'=>$reg,'products'=>$out], JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''

save(probe, php)
req = urllib.request.Request(safe_url(BASE + '/' + probe + '?t=' + str(int(time.time()))), headers={'User-Agent':'GramissPerformanceImageSizeFactsV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
with urllib.request.urlopen(req, context=CTX, timeout=240) as response:
    raw = response.read().decode('utf-8','replace')
    if response.status != 200:
        raise SystemExit('FAIL HTTP ' + str(response.status))
state = json.loads(raw)
print('REGISTERED_IMAGE_SIZES', json.dumps(state.get('registered'), ensure_ascii=False, sort_keys=True))
for row in state.get('products', []):
    print('PRODUCT_IMAGE_SIZE_FACT', json.dumps(row, ensure_ascii=False, sort_keys=True))
if not state.get('products'):
    raise SystemExit('FAIL no tshirt product images')
print('PASS PERFORMANCE PRODUCT IMAGE SIZE FACTS V1 READ ONLY')
