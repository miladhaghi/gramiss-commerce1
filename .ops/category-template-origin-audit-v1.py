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
probe = 'gramiss-category-template-origin-audit-v1-' + nonce + '.php'
php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$root = get_stylesheet_directory();
$needles = ['gramiss-premium-shop-title','gramiss-shop-premium-hero','woocommerce_page_title','woocommerce_show_page_title','page-title'];
$out = [];
$it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
foreach ($it as $file) {
  if (!$file->isFile()) continue;
  $ext = strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION));
  if (!in_array($ext, ['php','css','js'], true)) continue;
  $text = @file_get_contents($file->getPathname());
  if ($text === false) continue;
  $hits = [];
  foreach ($needles as $needle) {
    $pos = stripos($text, $needle);
    if ($pos !== false) {
      $start = max(0, $pos - 240);
      $hits[$needle] = substr($text, $start, 620);
    }
  }
  if ($hits) {
    $rel = ltrim(str_replace($root, '', $file->getPathname()), '/\\');
    $out[] = ['path'=>$rel,'sha256'=>hash_file('sha256',$file->getPathname()),'hits'=>$hits];
  }
}
echo wp_json_encode(['theme'=>$root,'matches'=>$out], JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save(probe, php)
req = urllib.request.Request(safe_url(BASE + '/' + probe + '?t=' + str(int(time.time()))), headers={
    'User-Agent': 'GramissCategoryTemplateOriginAuditV1/1.0',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
})
with urllib.request.urlopen(req, context=CTX, timeout=240) as response:
    raw = response.read().decode('utf-8', 'replace')
    print('HTTP', response.status)
state = json.loads(raw)
print('THEME', state.get('theme'))
for row in state.get('matches', []):
    print('TEMPLATE_MATCH', json.dumps(row, ensure_ascii=False, sort_keys=True))
print('MATCH_COUNT', len(state.get('matches', [])))
print('PASS CATEGORY TEMPLATE ORIGIN AUDIT V1 READ ONLY')
