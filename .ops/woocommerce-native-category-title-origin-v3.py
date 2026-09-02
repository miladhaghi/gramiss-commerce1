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
        p.query,
        p.fragment,
    ))


nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
probe = 'gramiss-wc-native-title-origin-v3-' + nonce + '.php'
php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);

function g1_source_excerpt($file, $start, $end, $pad = 8) {
    if (!$file || !is_file($file)) return null;
    $lines = @file($file);
    if (!$lines) return null;
    $a = max(1, (int)$start - $pad);
    $b = min(count($lines), (int)$end + $pad);
    $out = [];
    for ($i = $a; $i <= $b; $i++) {
        $out[] = $i . ': ' . rtrim($lines[$i - 1], "\r\n");
    }
    return implode("\n", $out);
}

function g1_callback_label($callback) {
    if (is_string($callback)) return $callback;
    if (is_array($callback) && count($callback) === 2) {
        $left = is_object($callback[0]) ? get_class($callback[0]) : (string)$callback[0];
        return $left . '::' . (string)$callback[1];
    }
    if ($callback instanceof Closure) {
        try {
            $r = new ReflectionFunction($callback);
            return 'Closure@' . $r->getFileName() . ':' . $r->getStartLine();
        } catch (Throwable $e) {
            return 'Closure';
        }
    }
    return gettype($callback);
}

$out = [
    'woocommerce_version' => defined('WC_VERSION') ? WC_VERSION : null,
    'wc_abspath' => defined('WC_ABSPATH') ? WC_ABSPATH : null,
    'woocommerce_content' => null,
    'literal_hits' => [],
    'hook_callbacks' => [],
    'filter_callbacks' => [],
];

if (function_exists('woocommerce_content')) {
    $r = new ReflectionFunction('woocommerce_content');
    $out['woocommerce_content'] = [
        'file' => $r->getFileName(),
        'start' => $r->getStartLine(),
        'end' => $r->getEndLine(),
        'source' => g1_source_excerpt($r->getFileName(), $r->getStartLine(), $r->getEndLine(), 12),
    ];
}

$root = defined('WC_ABSPATH') ? rtrim(WC_ABSPATH, '/\\') : '';
$needles = [
    '<h1 class="page-title"',
    "<h1 class='page-title'",
    'woocommerce_show_page_title',
    'woocommerce_page_title()',
    'woocommerce_page_title( false )',
    'woocommerce_archive_description',
];
if ($root && is_dir($root)) {
    $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
    foreach ($it as $file) {
        if (!$file->isFile() || strtolower(pathinfo($file->getFilename(), PATHINFO_EXTENSION)) !== 'php') continue;
        $path = $file->getPathname();
        $text = @file_get_contents($path);
        if ($text === false) continue;
        $hits = [];
        foreach ($needles as $needle) {
            $offset = 0;
            $parts = [];
            while (($pos = strpos($text, $needle, $offset)) !== false && count($parts) < 6) {
                $line = substr_count(substr($text, 0, $pos), "\n") + 1;
                $start = max(0, $pos - 420);
                $parts[] = ['line' => $line, 'excerpt' => substr($text, $start, 1100)];
                $offset = $pos + strlen($needle);
            }
            if ($parts) $hits[$needle] = $parts;
        }
        if ($hits) {
            $out['literal_hits'][] = [
                'path' => $path,
                'sha256' => hash_file('sha256', $path),
                'hits' => $hits,
            ];
        }
    }
}

$hook_names = [
    'woocommerce_before_main_content',
    'woocommerce_archive_description',
    'woocommerce_before_shop_loop',
    'woocommerce_after_main_content',
];
foreach ($hook_names as $hook_name) {
    $rows = [];
    global $wp_filter;
    if (isset($wp_filter[$hook_name]) && $wp_filter[$hook_name] instanceof WP_Hook) {
        foreach ($wp_filter[$hook_name]->callbacks as $priority => $callbacks) {
            foreach ($callbacks as $cb) {
                $rows[] = [
                    'priority' => (int)$priority,
                    'callback' => g1_callback_label($cb['function'] ?? null),
                    'accepted_args' => (int)($cb['accepted_args'] ?? 0),
                ];
            }
        }
    }
    $out['hook_callbacks'][$hook_name] = $rows;
}

$filter_names = ['woocommerce_show_page_title', 'woocommerce_page_title'];
foreach ($filter_names as $filter_name) {
    $rows = [];
    global $wp_filter;
    if (isset($wp_filter[$filter_name]) && $wp_filter[$filter_name] instanceof WP_Hook) {
        foreach ($wp_filter[$filter_name]->callbacks as $priority => $callbacks) {
            foreach ($callbacks as $cb) {
                $rows[] = [
                    'priority' => (int)$priority,
                    'callback' => g1_callback_label($cb['function'] ?? null),
                    'accepted_args' => (int)($cb['accepted_args'] ?? 0),
                ];
            }
        }
    }
    $out['filter_callbacks'][$filter_name] = $rows;
}

echo wp_json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
?>'''

save(probe, php)
req = urllib.request.Request(
    safe_url(BASE + '/' + probe + '?t=' + str(int(time.time()))),
    headers={
        'User-Agent': 'GramissWooNativeTitleOriginV3/1.0',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    },
)
with urllib.request.urlopen(req, context=CTX, timeout=300) as response:
    raw = response.read().decode('utf-8', 'replace')
    print('HTTP', response.status)
state = json.loads(raw)
print('WC_VERSION', state.get('woocommerce_version'))
print('WOOCOMMERCE_CONTENT', json.dumps(state.get('woocommerce_content'), ensure_ascii=False, sort_keys=True))
for row in state.get('literal_hits', []):
    print('WC_LITERAL_HIT', json.dumps(row, ensure_ascii=False, sort_keys=True))
print('HOOK_CALLBACKS', json.dumps(state.get('hook_callbacks'), ensure_ascii=False, sort_keys=True))
print('FILTER_CALLBACKS', json.dumps(state.get('filter_callbacks'), ensure_ascii=False, sort_keys=True))
print('PASS WOOCOMMERCE NATIVE CATEGORY TITLE ORIGIN V3 READ ONLY')
