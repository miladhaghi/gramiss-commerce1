#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import re
import time
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

EXPECTED_THEME = {
    'header.php': '3f0873f2e21904f9392607169bd1f8e72b590bab36afdef409bf0952b32e5cb1',
    'footer.php': 'e4836e538a4ef25d2ff49adceec1ab296fe93dab1fbef2ec7fb1fa1a71923f86',
    'functions.php': '178d68c8af56fb1568874abe5bd704ff0c23b2f0bf6c15882a3367ee9c682524',
    'page-about-gramiss.php': 'f3ce1ee7fc3604594c7b952d4ada78f5f6eb6b9ff3add965097d40740adcb9e1',
    'page-contact.php': '26f35ef92301f0e2c1b99a9f350d29cc78d60e86a3fa36d50dd25b5006054f48',
    'assets/css/about-support-v1.css': 'cf48554bbed0fcdaba96328a5ebb9f0efd55ba097362bf5fcc7506ebe28db433',
}
PROTECTED = {
    'front-page.php': 'e92d85b78f33470171a9b76c40c29b134148a4ef0dfda575004b6e6b6d6a3f00',
    'assets/css/gramiss-1.css': '73e1e46ec5007e9842a3fba86c53fd9ea630cd5b1d64586545822301b8c14d9d',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}
PLUGIN_DIR = 'public_html/wp-content/plugins/gramiss-site-info'
PLUGIN_FILE = 'gramiss-site-info.php'
PLUGIN_SHA = '6c11d2e383fc0fee51838c68621371d409b9b5d4718d6230db34ba17ab6cf5b0'


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def read_plugin():
    data = mod.api('get_file_content', {
        'dir': PLUGIN_DIR,
        'file': PLUGIN_FILE,
        'from_charset': '_DETECT_',
        'to_charset': 'utf-8',
    })
    return mod.extract(data)


def main():
    for path, expected in {**EXPECTED_THEME, **PROTECTED}.items():
        actual = sha(mod.read(path))
        print('FILE', path, actual)
        if actual != expected:
            raise SystemExit('Drift detected: ' + path)

    plugin_sha = sha(read_plugin())
    print('PLUGIN_SHA', plugin_sha)
    if plugin_sha != PLUGIN_SHA:
        raise SystemExit('Gramiss Site Info plugin drift')

    stamp = str(int(time.time()))
    temp_name = 'gramiss-about-support-verify-' + stamp + '.php'
    php = '''<?php
header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';
$info = get_option('gramiss_site_info_v1', array());
$about = get_page_by_path('about-gramiss', OBJECT, 'page');
$contact = get_page_by_path('contact', OBJECT, 'page');
$out = array(
  'plugin_active' => is_plugin_active('gramiss-site-info/gramiss-site-info.php'),
  'about_published' => $about && $about->post_status === 'publish',
  'contact_published' => $contact && $contact->post_status === 'publish',
  'about_template' => $about ? get_post_meta($about->ID, '_wp_page_template', true) : '',
  'contact_template' => $contact ? get_post_meta($contact->ID, '_wp_page_template', true) : '',
  'contact_info' => array(
    'phone_configured' => !empty($info['phone']),
    'email_configured' => !empty($info['email']),
    'hours_configured' => !empty($info['hours'])
  ),
  'shipping_exists' => (bool) get_page_by_path('shipping', OBJECT, 'page'),
  'returns_exists' => (bool) get_page_by_path('returns', OBJECT, 'page')
);
@unlink(__FILE__);
echo wp_json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
?>'''
    mod.save_root(temp_name, php)
    status, body = mod.get(mod.BASE + '/' + temp_name + '?t=' + stamp, 120)
    print('WP_HTTP', status)
    print('WP_STATE', body)
    if status != 200:
        raise SystemExit('WordPress state endpoint failed')
    state = json.loads(body)
    if not state.get('plugin_active') or not state.get('about_published') or not state.get('contact_published'):
        raise SystemExit('Plugin/pages not healthy: ' + str(state))
    if state.get('about_template') != 'page-about-gramiss.php' or state.get('contact_template') != 'page-contact.php':
        raise SystemExit('Page template assignment drift')

    home_status, home = mod.get(mod.BASE + '/?about-support-verify=' + stamp, 120)
    print('HOME_HTTP', home_status, 'BYTES', len(home.encode()))
    if home_status != 200:
        raise SystemExit('Home unhealthy')
    primary = re.search(r'<nav class="primary-nav".*?</nav>', home, re.I | re.S)
    labels = [] if not primary else [re.sub(r'<[^>]+>', '', x).strip() for x in re.findall(r'<a\b[^>]*>(.*?)</a>', primary.group(0), re.I | re.S)]
    print('PRIMARY_NAV_LABELS', json.dumps(labels, ensure_ascii=False))
    if labels != ['Shop', 'Collections', 'Journal', 'Smart Guide']:
        raise SystemExit('Desktop primary nav changed')
    if 'mobile-panel-info-links' not in home:
        raise SystemExit('Mobile info links missing')

    for route, marker in [('/about-gramiss/', 'GRAMISS ABOUT V1 START'), ('/contact/', 'GRAMISS SUPPORT V1 START')]:
        page_status, page = mod.get(mod.BASE + route + '?v=' + stamp, 120)
        print('PAGE', route, page_status, len(page.encode()))
        if page_status != 200 or marker not in page or len(re.findall(r'<h1\b', page, re.I)) != 1:
            raise SystemExit('Page verification failed: ' + route)

    print('PASS ABOUT SUPPORT V1 VERIFY')

if __name__ == '__main__':
    main()
