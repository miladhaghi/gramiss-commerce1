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

ABOUT_PATH = 'page-about-gramiss.php'
V2_CSS_PATH = 'assets/css/about-gramiss-v2.css'
ABOUT_SOURCE = Path('wordpress/theme/gramiss-theme-next/page-about-gramiss.php').read_text(encoding='utf-8')
V2_CSS_SOURCE = Path('wordpress/theme/gramiss-theme-next/assets/css/about-gramiss-v2.css').read_text(encoding='utf-8')

EXPECTED_LIVE = {
    'header.php': '3f0873f2e21904f9392607169bd1f8e72b590bab36afdef409bf0952b32e5cb1',
    'footer.php': 'e4836e538a4ef25d2ff49adceec1ab296fe93dab1fbef2ec7fb1fa1a71923f86',
    'functions.php': '178d68c8af56fb1568874abe5bd704ff0c23b2f0bf6c15882a3367ee9c682524',
    'page-about-gramiss.php': 'f3ce1ee7fc3604594c7b952d4ada78f5f6eb6b9ff3add965097d40740adcb9e1',
    'assets/css/about-support-v1.css': 'cf48554bbed0fcdaba96328a5ebb9f0efd55ba097362bf5fcc7506ebe28db433',
}
PROTECTED = {
    'front-page.php': 'e92d85b78f33470171a9b76c40c29b134148a4ef0dfda575004b6e6b6d6a3f00',
    'assets/css/gramiss-1.css': '73e1e46ec5007e9842a3fba86c53fd9ea630cd5b1d64586545822301b8c14d9d',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def verify_public():
    stamp = str(int(time.time()))
    errors = []

    status, home = mod.get(mod.BASE + '/?about-v2-guard=' + stamp, 180)
    print('HOME_HTTP', status, 'BYTES', len(home.encode()))
    if status != 200:
        errors.append('Home HTTP != 200')
    primary = re.search(r'<nav class="primary-nav".*?</nav>', home, re.I | re.S)
    if not primary:
        errors.append('Primary desktop nav missing')
    else:
        labels = re.findall(r'<a\b[^>]*>(.*?)</a>', primary.group(0), re.I | re.S)
        labels = [re.sub(r'<[^>]+>', '', x).strip() for x in labels]
        print('PRIMARY_NAV_LABELS', json.dumps(labels, ensure_ascii=False))
        if labels != ['Shop', 'Collections', 'Journal', 'Smart Guide']:
            errors.append('Desktop primary nav changed: ' + repr(labels))

    status, page = mod.get(mod.BASE + '/about-gramiss/?v2=' + stamp, 180)
    print('ABOUT_HTTP', status, 'BYTES', len(page.encode()))
    if status != 200:
        errors.append('About HTTP != 200')
    else:
        if 'GRAMISS ABOUT V2 START' not in page:
            errors.append('V2 marker missing')
        if 'id="gramiss-about-v2-css"' not in page:
            errors.append('About V2 stylesheet not enqueued')
        if len(re.findall(r'<h1\b', page, re.I)) != 1:
            errors.append('About H1 count != 1')
        for needle in ['کمتر حدس بزن', 'فقط یک ویترین', 'سه اصل ساده', 'از چیزی که واقعاً نیاز داری شروع کن', 'راهنما، قبل از فروش']:
            if needle not in page:
                errors.append('Missing About content: ' + needle)
    return errors


def main():
    before = {}
    for path, expected in EXPECTED_LIVE.items():
        text = mod.read(path)
        before[path] = text
        actual = sha(text)
        print('LIVE_PRE', path, actual)
        if actual != expected:
            raise SystemExit('REFUSE live drift: ' + path + ' ' + actual)
    for path, expected in PROTECTED.items():
        actual = sha(mod.read(path))
        print('PROTECTED_PRE', path, actual)
        if actual != expected:
            raise SystemExit('REFUSE protected drift: ' + path + ' ' + actual)

    try:
        existing_v2 = mod.read(V2_CSS_PATH)
    except Exception:
        existing_v2 = ''
    if existing_v2.strip():
        raise SystemExit('REFUSE: About V2 CSS already exists on live theme')

    stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
    mod.save(ABOUT_PATH + '.bak-v2-' + stamp, before[ABOUT_PATH])

    try:
        mod.save(ABOUT_PATH, ABOUT_SOURCE)
        mod.save(V2_CSS_PATH, V2_CSS_SOURCE)
        mod.flush()

        about_sha = sha(mod.read(ABOUT_PATH))
        css_sha = sha(mod.read(V2_CSS_PATH))
        print('ABOUT_STORED_SHA', about_sha)
        print('V2_CSS_STORED_SHA', css_sha)
        if about_sha != sha(ABOUT_SOURCE):
            raise RuntimeError('Stored About V2 template mismatch')
        if css_sha != sha(V2_CSS_SOURCE):
            raise RuntimeError('Stored About V2 CSS mismatch')

        for path in ['header.php', 'footer.php', 'functions.php', 'assets/css/about-support-v1.css']:
            actual = sha(mod.read(path))
            print('UNCHANGED', path, actual)
            if actual != EXPECTED_LIVE[path]:
                raise RuntimeError('Unexpected collateral change: ' + path)
        for path, expected in PROTECTED.items():
            actual = sha(mod.read(path))
            print('PROTECTED_POST', path, actual)
            if actual != expected:
                raise RuntimeError('Protected file changed: ' + path)

        errors = verify_public()
        print('VERIFY_ERRORS', json.dumps(errors, ensure_ascii=False))
        if errors:
            raise RuntimeError('; '.join(errors))

        print('PASS ABOUT GRAMISS V2 DEPLOY')
        print('NEW_ABOUT_SHA', about_sha)
        print('NEW_ABOUT_CSS_SHA', css_sha)
    except Exception as exc:
        print('ROLLBACK_REASON', str(exc))
        mod.save(ABOUT_PATH, before[ABOUT_PATH])
        mod.flush()
        raise

if __name__ == '__main__':
    main()
