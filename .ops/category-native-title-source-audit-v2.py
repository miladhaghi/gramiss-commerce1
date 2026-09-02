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
        'dir': 'public_html', 'file': name, 'content': text,
        'from_charset': 'UTF-8', 'to_charset': 'UTF-8', 'fallback': '0',
    }, True)


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@'), p.query, p.fragment))

nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
probe = 'gramiss-category-native-title-source-v2-' + nonce + '.php'
php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$root = get_stylesheet_directory();
$needles = [
  'shop-premium-shell.php',
  'gramiss-commerce-main',
  'woocommerce_show_page_title',
  'woocommerce_page_title',
  'woocommerce_before_main_content',
  'woocommerce_before_shop_loop',
  'woocommerce_archive_description',
  'the_archive_title',
  'get_the_archive_title',
  'single_term_title',
  'the_title(',
  'page-title',
  'is_product_category',
  'archive-product.php'
];
$out = [];
$it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
foreach ($it as $file) {
  if (!$file->isFile()) continue;
  if (strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION)) !== 'php') continue;
  $text = @file_get_contents($file->getPathname());
  if ($text === false) continue;
  $hits = [];
  foreach ($needles as $needle) {
    $offset = 0;
    $parts = [];
    while (($pos = stripos($text, $needle, $offset)) !== false && count($parts) < 4) {
      $start = max(0, $pos - 360);
      $parts[] = substr($text, $start, 900);
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
// Also report the standard WooCommerce archive template actually available from the plugin.
$wc = defined('WC_ABSPATH') ? WC_ABSPATH . 'templates/archive-product.php' : '';
$wcrow = null;
if ($wc && is_file($wc)) {
  $text = file_get_contents($wc);
  $wcrow = ['path'=>$wc,'sha256'=>hash_file('sha256',$wc),'size'=>filesize($wc)];
  foreach (['woocommerce_show_page_title','page-title','woocommerce_page_title'] as $needle) {
    $pos = stripos($text,$needle);
    if ($pos !== false) $wcrow['hits'][$needle] = substr($text,max(0,$pos-300),900);
  }
}
echo wp_json_encode([
  'theme'=>$root,
  'stylesheet'=>get_stylesheet(),
  'template'=>get_template(),
  'matches'=>$out,
  'wc_archive'=>$wcrow,
], JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save($probe ?? probe, php) if False else None
