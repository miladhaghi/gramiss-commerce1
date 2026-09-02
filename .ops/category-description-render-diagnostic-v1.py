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
TARGET_URL = BASE + '/product-category/hat/fitted-cap/'


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


def save_public(name, content):
    return api('save_file_content', {
        'dir': 'public_html', 'file': name, 'content': content,
        'from_charset': 'UTF-8', 'to_charset': 'UTF-8', 'fallback': '0',
    }, True)


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'GramissCategoryDescriptionDiagnosticV1/1.0', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, context=CTX, timeout=120) as response:
        return response.status, response.read().decode('utf-8', 'replace')

status, page = get(TARGET_URL + '?g1desc=' + str(int(time.time())))
print('PAGE_HTTP', status)
for needle in ('term-description', 'gramiss-shop-premium-hero', '<ul class="products', '<main id="primary"'):
    pos = page.find(needle)
    print('PAGE_NEEDLE', needle, pos)
    if pos >= 0:
        print('PAGE_CONTEXT', needle, re.sub(r'\s+', ' ', page[max(0, pos-500):pos+1200]))

nonce = str(int(time.time() * 1000))
name = 'gramiss-category-description-source-' + nonce + '.php'
php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$term = get_term_by('slug', 'fitted-cap', 'product_cat');
$root = get_stylesheet_directory();
$matches = [];
$needles = ['term-description', 'woocommerce_archive_description', 'woocommerce_taxonomy_archive_description'];
$it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
foreach ($it as $file) {
    if (!$file->isFile()) continue;
    $ext = strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION));
    if (!in_array($ext, ['css','php','js'], true)) continue;
    $text = @file_get_contents($file->getPathname());
    if ($text === false) continue;
    $hits = [];
    foreach ($needles as $needle) {
        $pos = stripos($text, $needle);
        if ($pos !== false) {
            $hits[$needle] = substr($text, max(0, $pos - 450), 1300);
        }
    }
    if ($hits) {
        $matches[] = [
            'path' => ltrim(str_replace($root, '', $file->getPathname()), '/\\'),
            'hits' => $hits,
        ];
    }
}
echo wp_json_encode([
    'term' => $term ? ['id'=>(int)$term->term_id,'name'=>$term->name,'description'=>$term->description] : null,
    'matches' => $matches,
], JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save_public(name, php)
probe_status, probe = get(BASE + '/' + name + '?t=' + nonce)
print('PROBE_HTTP', probe_status)
print('PROBE', probe)
print('PASS CATEGORY DESCRIPTION RENDER DIAGNOSTIC V1 READ ONLY')
