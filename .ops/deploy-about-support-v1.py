#!/usr/bin/env python3
import base64
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

THEME_SOURCES = {
    'page-about-gramiss.php': Path('wordpress/theme/gramiss-theme-next/page-about-gramiss.php').read_text(encoding='utf-8'),
    'page-contact.php': Path('wordpress/theme/gramiss-theme-next/page-contact.php').read_text(encoding='utf-8'),
    'assets/css/about-support-v1.css': Path('wordpress/theme/gramiss-theme-next/assets/css/about-support-v1.css').read_text(encoding='utf-8'),
}
PLUGIN_SOURCE = Path('wordpress/plugins/gramiss-site-info/gramiss-site-info.php').read_text(encoding='utf-8')

EXPECTED_BEFORE = {
    'header.php': 'a458e1ce03890a596d873a7e231728c2ef41269ec06783802028ba485951c061',
    'footer.php': '107df3bb4fa8b97401beaf1bffd4d351318988f93377f731372065c34620824a',
    'functions.php': '178d68c8af56fb1568874abe5bd704ff0c23b2f0bf6c15882a3367ee9c682524',
}
PROTECTED = {
    'front-page.php': 'e92d85b78f33470171a9b76c40c29b134148a4ef0dfda575004b6e6b6d6a3f00',
    'assets/css/gramiss-1.css': '73e1e46ec5007e9842a3fba86c53fd9ea630cd5b1d64586545822301b8c14d9d',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}

ASSET_BLOCK = '''<!-- GRAMISS ABOUT SUPPORT V1 ASSETS START -->
<link id="gramiss-about-support-v1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/css/about-support-v1.css?v=20260907-1' ); ?>" media="all">
<!-- GRAMISS ABOUT SUPPORT V1 ASSETS END -->
'''
MOBILE_BLOCK = '''        <div class="mobile-panel-info-links" aria-label="اطلاعات و پشتیبانی">
            <a href="<?php echo esc_url( home_url( '/about-gramiss/' ) ); ?>">درباره Gramiss</a>
            <a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>">پشتیبانی و تماس</a>
        </div>

'''
FOOTER_GUIDE = '''<div class="footer-column"><h3>راهنما</h3><ul><li><a href="<?php echo esc_url( home_url( '/about-gramiss/' ) ); ?>">درباره Gramiss</a></li><li><a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>">پشتیبانی و تماس</a></li><li><a href="<?php echo esc_url( get_permalink( (int) get_option( 'page_for_posts' ) ) ); ?>">مجله Gramiss</a></li><li><a href="<?php echo esc_url( home_url( '/shipping/' ) ); ?>">ارسال سفارش</a></li><li><a href="<?php echo esc_url( home_url( '/returns/' ) ); ?>">تعویض و مرجوعی</a></li></ul></div>'''


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected 1 exact match, got {count}')
    return text.replace(old, new, 1)


def patch_header(text):
    if 'GRAMISS ABOUT SUPPORT V1 ASSETS START' in text or 'mobile-panel-info-links' in text:
        raise RuntimeError('About/Support markers already present in header')
    text = replace_once(text, '</head>', ASSET_BLOCK + '</head>', 'head asset insertion')
    needle = '        </nav>\n\n        <div class="mobile-panel-actions">'
    replacement = '        </nav>\n\n' + MOBILE_BLOCK + '        <div class="mobile-panel-actions">'
    text = replace_once(text, needle, replacement, 'mobile drawer info links')
    return text


def patch_footer(text):
    if 'درباره Gramiss' in text:
        raise RuntimeError('About link already present in footer')
    pattern = r'<div class="footer-column"><h3>راهنما</h3><ul>.*?</ul></div>'
    out, count = re.subn(pattern, FOOTER_GUIDE, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f'footer guide replacement expected 1 match, got {count}')
    return out


def deploy_plugin_and_pages():
    stamp = str(int(time.time()))
    temp_name = 'gramiss-about-support-deploy-' + stamp + '.php'
    plugin_b64 = base64.b64encode(PLUGIN_SOURCE.encode()).decode()
    php = '''<?php
header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';

$result = array();
$plugin_rel = 'gramiss-site-info/gramiss-site-info.php';
$plugin_dir = WP_PLUGIN_DIR . '/gramiss-site-info';
$plugin_file = $plugin_dir . '/gramiss-site-info.php';
$source = base64_decode(''' + repr(plugin_b64) + ''');
$had_plugin = file_exists($plugin_file);
$old_plugin = $had_plugin ? file_get_contents($plugin_file) : null;

function gramiss_ensure_info_page($slug, $title, $template) {
    $page = get_page_by_path($slug, OBJECT, 'page');
    if ($page) {
        $id = (int) $page->ID;
        $update = array('ID' => $id, 'post_status' => 'publish', 'post_title' => $title);
        $r = wp_update_post($update, true);
        if (is_wp_error($r)) { throw new Exception($r->get_error_message()); }
    } else {
        $id = wp_insert_post(array(
            'post_type' => 'page',
            'post_status' => 'publish',
            'post_title' => $title,
            'post_name' => $slug,
            'post_content' => ''
        ), true);
        if (is_wp_error($id)) { throw new Exception($id->get_error_message()); }
        $id = (int) $id;
    }
    update_post_meta($id, '_wp_page_template', $template);
    return array('id' => $id, 'url' => get_permalink($id), 'template' => get_post_meta($id, '_wp_page_template', true));
}

try {
    if (!is_dir($plugin_dir) && !wp_mkdir_p($plugin_dir)) {
        throw new Exception('Could not create Gramiss Site Info plugin directory');
    }
    if (false === file_put_contents($plugin_file, $source)) {
        throw new Exception('Could not write Gramiss Site Info plugin');
    }
    clearstatcache(true, $plugin_file);
    $valid = validate_plugin($plugin_rel);
    if (is_wp_error($valid)) { throw new Exception('Plugin validation: ' . $valid->get_error_message()); }
    $activation = activate_plugin($plugin_rel, '', false, false);
    if (is_wp_error($activation)) { throw new Exception('Plugin activation: ' . $activation->get_error_message()); }
    if (!is_plugin_active($plugin_rel)) { throw new Exception('Gramiss Site Info plugin is not active'); }

    $result['plugin_active'] = true;
    $result['plugin_sha256'] = hash_file('sha256', $plugin_file);
    $result['about'] = gramiss_ensure_info_page('about-gramiss', 'درباره Gramiss', 'page-about-gramiss.php');
    $result['contact'] = gramiss_ensure_info_page('contact', 'پشتیبانی و تماس', 'page-contact.php');
    $result['shipping_exists'] = (bool) get_page_by_path('shipping', OBJECT, 'page');
    $result['returns_exists'] = (bool) get_page_by_path('returns', OBJECT, 'page');
    if (function_exists('wp_cache_flush')) { wp_cache_flush(); }
    if (function_exists('opcache_reset')) { @opcache_reset(); }
    $result['ok'] = true;
} catch (Throwable $e) {
    if ($had_plugin && null !== $old_plugin) {
        @file_put_contents($plugin_file, $old_plugin);
    } elseif (!$had_plugin && file_exists($plugin_file)) {
        @unlink($plugin_file);
    }
    $result['ok'] = false;
    $result['error'] = $e->getMessage();
    http_response_code(500);
}
@unlink(__FILE__);
echo wp_json_encode($result, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
?>'''
    mod.save_root(temp_name, php)
    status, body = mod.get(mod.BASE + '/' + temp_name + '?t=' + stamp, 180)
    print('WP_DEPLOY_HTTP', status)
    print('WP_DEPLOY_BODY', body)
    if status != 200:
        raise RuntimeError('WordPress page/plugin deploy endpoint failed')
    result = json.loads(body)
    if not result.get('ok') or not result.get('plugin_active'):
        raise RuntimeError('WordPress page/plugin deploy failed: ' + str(result))
    if result.get('plugin_sha256') != sha(PLUGIN_SOURCE):
        raise RuntimeError('Gramiss Site Info plugin SHA mismatch')
    return result


def verify_rendered():
    stamp = str(int(time.time()))
    errors = []
    home_status, home = mod.get(mod.BASE + '/?about-support-v1=' + stamp, 180)
    print('HOME_HTTP', home_status, 'BYTES', len(home.encode()))
    if home_status != 200:
        errors.append('Home HTTP is not 200')
    if 'mobile-panel-info-links' not in home:
        errors.append('Mobile info links missing from rendered Home')
    if '/about-gramiss/' not in home or '/contact/' not in home:
        errors.append('About/Contact routes missing from rendered Home')
    primary = re.search(r'<nav class="primary-nav".*?</nav>', home, re.I | re.S)
    if not primary:
        errors.append('Primary desktop nav missing')
    else:
        labels = re.findall(r'<a\b[^>]*>(.*?)</a>', primary.group(0), re.I | re.S)
        labels = [re.sub(r'<[^>]+>', '', x).strip() for x in labels]
        print('PRIMARY_NAV_LABELS', json.dumps(labels, ensure_ascii=False))
        if labels != ['Shop', 'Collections', 'Journal', 'Smart Guide']:
            errors.append('Desktop primary nav changed: ' + repr(labels))

    for route, marker in [('/about-gramiss/', 'GRAMISS ABOUT V1 START'), ('/contact/', 'GRAMISS SUPPORT V1 START')]:
        status, page = mod.get(mod.BASE + route + '?v=' + stamp, 180)
        print('PAGE', route, 'HTTP', status, 'BYTES', len(page.encode()))
        if status != 200:
            errors.append(route + ' HTTP is not 200')
            continue
        if marker not in page:
            errors.append(route + ' template marker missing')
        if len(re.findall(r'<h1\b', page, re.I)) != 1:
            errors.append(route + ' H1 count is not 1')
        if 'gramiss-about-support-v1-css' not in page:
            errors.append(route + ' stylesheet not loaded')

    return errors


def main():
    before = {}
    for path, expected in EXPECTED_BEFORE.items():
        text = mod.read(path)
        before[path] = text
        actual = sha(text)
        print('PRE_SHA', path, actual)
        if actual != expected:
            raise SystemExit('REFUSE live drift: ' + path + ' ' + actual)
    for path, expected in PROTECTED.items():
        actual = sha(mod.read(path))
        print('PROTECTED_PRE', path, actual)
        if actual != expected:
            raise SystemExit('REFUSE protected drift: ' + path)

    for path in THEME_SOURCES:
        try:
            existing = mod.read(path)
        except Exception:
            existing = ''
        if existing.strip():
            raise SystemExit('REFUSE target theme file already exists: ' + path)

    new_header = patch_header(before['header.php'])
    new_footer = patch_footer(before['footer.php'])
    stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
    mod.save('header.php.bak-about-support-v1-' + stamp, before['header.php'])
    mod.save('footer.php.bak-about-support-v1-' + stamp, before['footer.php'])

    try:
        mod.save('header.php', new_header)
        mod.save('footer.php', new_footer)
        for path, source in THEME_SOURCES.items():
            mod.save(path, source)
        wp_result = deploy_plugin_and_pages()
        mod.flush()

        if sha(mod.read('header.php')) != sha(new_header):
            raise RuntimeError('Stored header mismatch')
        if sha(mod.read('footer.php')) != sha(new_footer):
            raise RuntimeError('Stored footer mismatch')
        for path, source in THEME_SOURCES.items():
            actual = sha(mod.read(path))
            print('SOURCE_STORED', path, actual)
            if actual != sha(source):
                raise RuntimeError('Stored source mismatch: ' + path)
        for path, expected in PROTECTED.items():
            actual = sha(mod.read(path))
            print('PROTECTED_POST', path, actual)
            if actual != expected:
                raise RuntimeError('Protected file changed: ' + path)
        if sha(mod.read('functions.php')) != EXPECTED_BEFORE['functions.php']:
            raise RuntimeError('functions.php changed unexpectedly')

        errors = verify_rendered()
        print('VERIFY_ERRORS', json.dumps(errors, ensure_ascii=False))
        if errors:
            raise RuntimeError('; '.join(errors))

        print('NEW_HEADER_SHA', sha(new_header))
        print('NEW_FOOTER_SHA', sha(new_footer))
        print('PAGE_RESULT', json.dumps(wp_result, ensure_ascii=False))
        print('PASS ABOUT SUPPORT V1 DEPLOY')
    except Exception as exc:
        print('ROLLBACK_REASON', str(exc))
        mod.save('header.php', before['header.php'])
        mod.save('footer.php', before['footer.php'])
        mod.flush()
        raise

if __name__ == '__main__':
    main()
