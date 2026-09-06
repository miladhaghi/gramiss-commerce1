#!/usr/bin/env python3
import base64
import hashlib
import importlib.util
import json
import time
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PLUGIN_REL = 'gramiss-sms/gramiss-sms.php'
PLUGIN_DIR = 'public_html/wp-content/plugins/gramiss-sms'
PLUGIN_FILE = 'gramiss-sms.php'
SOURCE = Path('wordpress/plugins/gramiss-sms/gramiss-sms.php').read_text(encoding='utf-8')
SOURCE_SHA = hashlib.sha256(SOURCE.encode()).hexdigest()

PROTECTED = {
    'front-page.php': 'e92d85b78f33470171a9b76c40c29b134148a4ef0dfda575004b6e6b6d6a3f00',
    'assets/css/gramiss-1.css': '73e1e46ec5007e9842a3fba86c53fd9ea630cd5b1d64586545822301b8c14d9d',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def plugin_read():
    data = mod.api('get_file_content', {
        'dir': PLUGIN_DIR,
        'file': PLUGIN_FILE,
        'from_charset': '_DETECT_',
        'to_charset': 'utf-8',
    })
    return mod.extract(data)

def main():
    print('SOURCE_SHA', SOURCE_SHA)
    for path, expected in PROTECTED.items():
        actual = sha(mod.read(path))
        print('PROTECTED_PRE', path, actual)
        if actual != expected:
            raise SystemExit('REFUSE protected drift: ' + path)

    stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
    temp_name = 'gramiss-sms-deploy-' + stamp + '.php'
    payload = base64.b64encode(SOURCE.encode()).decode()
    php = '''<?php
header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';

$plugin_rel = 'gramiss-sms/gramiss-sms.php';
$dir = WP_PLUGIN_DIR . '/gramiss-sms';
$target = $dir . '/gramiss-sms.php';
$result = array('woocommerce' => class_exists('WooCommerce'));
$old = null;
$had_old = file_exists($target);

try {
    if (!is_dir($dir) && !wp_mkdir_p($dir)) {
        throw new Exception('Could not create plugin directory');
    }
    if ($had_old) {
        $old = file_get_contents($target);
        $backup = $target . '.bak-''' + stamp + '''';
        if (false === file_put_contents($backup, $old)) {
            throw new Exception('Could not create plugin backup');
        }
        $result['backup'] = basename($backup);
    }
    $source = base64_decode(''' + repr(payload) + ''');
    if (false === file_put_contents($target, $source)) {
        throw new Exception('Could not write plugin file');
    }
    clearstatcache(true, $target);
    $valid = validate_plugin($plugin_rel);
    if (is_wp_error($valid)) {
        throw new Exception('Plugin validation failed: ' . $valid->get_error_message());
    }
    $activation = activate_plugin($plugin_rel, '', false, false);
    if (is_wp_error($activation)) {
        throw new Exception('Activation failed: ' . $activation->get_error_message());
    }
    $result['active'] = is_plugin_active($plugin_rel);
    $result['size'] = filesize($target);
    $result['sha256'] = hash_file('sha256', $target);
    if (!$result['active']) {
        throw new Exception('Plugin did not become active');
    }
    if (function_exists('wp_cache_flush')) { wp_cache_flush(); }
    if (function_exists('opcache_reset')) { @opcache_reset(); }
    $result['ok'] = true;
} catch (Throwable $e) {
    if ($had_old && null !== $old) {
        @file_put_contents($target, $old);
    } elseif (!$had_old && file_exists($target)) {
        @unlink($target);
    }
    if (function_exists('deactivate_plugins')) { deactivate_plugins($plugin_rel, true, false); }
    $result['ok'] = false;
    $result['error'] = $e->getMessage();
    http_response_code(500);
}
@unlink(__FILE__);
echo wp_json_encode($result, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
?>'''

    mod.save_root(temp_name, php)
    status, body = mod.get(mod.BASE + '/' + temp_name + '?t=' + str(time.time()), 180)
    print('DEPLOY_HTTP', status)
    print('DEPLOY_BODY', body)
    if status != 200:
        raise SystemExit('Deploy endpoint failed')
    try:
        result = json.loads(body)
    except Exception as exc:
        raise SystemExit('Invalid deploy JSON: ' + str(exc))
    if not result.get('ok') or not result.get('active'):
        raise SystemExit('Plugin deploy/activation failed: ' + str(result))
    if result.get('sha256') != SOURCE_SHA:
        raise SystemExit('Server plugin SHA mismatch in activation result')

    stored = plugin_read()
    stored_sha = sha(stored)
    print('PLUGIN_STORED_SHA', stored_sha)
    if stored_sha != SOURCE_SHA:
        raise SystemExit('Server plugin content mismatch')

    for path, expected in PROTECTED.items():
        actual = sha(mod.read(path))
        print('PROTECTED_POST', path, actual)
        if actual != expected:
            raise SystemExit('Protected file changed: ' + path)

    home_status, home = mod.get(mod.BASE + '/?gramiss-sms-v1=' + str(time.time()), 180)
    print('HOME_HTTP', home_status, 'BYTES', len(home.encode()))
    if home_status != 200:
        raise SystemExit('Home failed after plugin activation')
    if len(__import__('re').findall(r'<h1\\b', home, __import__('re').I)) != 1:
        raise SystemExit('Home H1 invariant changed')

    print('PASS GRAMISS SMS V1 DEPLOY')

if __name__ == '__main__':
    main()
