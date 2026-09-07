#!/usr/bin/env python3
import hashlib
import importlib.util
import time
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

TARGET = 'page-about-gramiss.php'
EXPECTED_LIVE_SHA = 'c44d7e0c5ba455c4d927b01e7e9f2e2bd8c7ea5afe2338923cc10caef97b6567'
SOURCE = Path('wordpress/theme/gramiss-theme-next/page-about-gramiss.php').read_text(encoding='utf-8')
PROTECTED = {
    'front-page.php': 'e92d85b78f33470171a9b76c40c29b134148a4ef0dfda575004b6e6b6d6a3f00',
    'assets/css/gramiss-1.css': '73e1e46ec5007e9842a3fba86c53fd9ea630cd5b1d64586545822301b8c14d9d',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
    'header.php': '3f0873f2e21904f9392607169bd1f8e72b590bab36afdef409bf0952b32e5cb1',
    'footer.php': 'e4836e538a4ef25d2ff49adceec1ab296fe93dab1fbef2ec7fb1fa1a71923f86',
}


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    live = mod.read(TARGET)
    live_sha = sha(live)
    print('LIVE_ABOUT_SHA', live_sha)
    if live_sha != EXPECTED_LIVE_SHA:
        raise SystemExit('REFUSE About live drift')
    if 'about-gramiss-v2.css?v=20260907-2' not in live:
        raise SystemExit('REFUSE expected old cache version missing')
    expected_source = live.replace('about-gramiss-v2.css?v=20260907-2', 'about-gramiss-v2.css?v=20260907-3', 1)
    if SOURCE != expected_source:
        raise SystemExit('REFUSE source differs by more than cache-bust token')

    for path, expected in PROTECTED.items():
        actual = sha(mod.read(path))
        print('PROTECTED_PRE', path, actual)
        if actual != expected:
            raise SystemExit('REFUSE protected drift: ' + path)

    try:
        mod.save(TARGET, SOURCE)
        mod.flush()
        stored = mod.read(TARGET)
        print('STORED_ABOUT_SHA', sha(stored))
        if stored != SOURCE:
            raise RuntimeError('Stored About mismatch')
        for path, expected in PROTECTED.items():
            actual = sha(mod.read(path))
            print('PROTECTED_POST', path, actual)
            if actual != expected:
                raise RuntimeError('Protected file changed: ' + path)
        status, page = mod.get(mod.BASE + '/about-gramiss/?cache-bust-v3=' + str(time.time()), 120)
        print('ABOUT_HTTP', status, 'BYTES', len(page.encode()))
        if status != 200:
            raise RuntimeError('About HTTP failed')
        if 'about-gramiss-v2.css?v=20260907-3' not in page:
            raise RuntimeError('New CSS cache version missing in rendered page')
        if 'GRAMISS ABOUT V2 START' not in page:
            raise RuntimeError('About V2 marker missing')
        print('PASS ABOUT CACHE BUST V3 DEPLOY')
    except Exception:
        mod.save(TARGET, live)
        mod.flush()
        raise

if __name__ == '__main__':
    main()
