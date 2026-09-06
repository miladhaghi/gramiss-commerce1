#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import time
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

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
    stored = plugin_read()
    print('SOURCE_SHA', SOURCE_SHA)
    print('PLUGIN_STORED_SHA', sha(stored))
    if sha(stored) != SOURCE_SHA:
        raise SystemExit('Live plugin content differs from guarded source')

    for path, expected in PROTECTED.items():
        actual = sha(mod.read(path))
        print('PROTECTED', path, actual)
        if actual != expected:
            raise SystemExit('Protected drift: ' + path)

    stamp = str(int(time.time()))
    temp_name = 'gramiss-sms-verify-' + stamp + '.php'
    php = """<?php
header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';
$out = array(
  'active' => is_plugin_active('gramiss-sms/gramiss-sms.php'),
  'woocommerce' => class_exists('WooCommerce'),
  'class_loaded' => class_exists('Gramiss_SMS_V1'),
  'template_default' => '761339'
);
@unlink(__FILE__);
echo wp_json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
?>"""
    mod.save_root(temp_name, php)
    status, body = mod.get(mod.BASE + '/' + temp_name + '?t=' + stamp, 120)
    print('WP_VERIFY_HTTP', status)
    print('WP_VERIFY_BODY', body)
    if status != 200:
        raise SystemExit('WordPress verification endpoint failed')
    result = json.loads(body)
    if not result.get('active') or not result.get('woocommerce') or not result.get('class_loaded'):
        raise SystemExit('Plugin is not active/loaded: ' + str(result))

    home_status, home = mod.get(mod.BASE + '/?gramiss-sms-verify=' + stamp, 120)
    print('HOME_HTTP', home_status, 'BYTES', len(home.encode()))
    if home_status != 200:
        raise SystemExit('Home is not healthy')

    print('PASS GRAMISS SMS V1 VERIFY')

if __name__ == '__main__':
    main()
