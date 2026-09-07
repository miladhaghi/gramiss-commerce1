#!/usr/bin/env python3
import hashlib
import importlib.util
import re
import time
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

EXPECTED = {
    'header.php': '3f0873f2e21904f9392607169bd1f8e72b590bab36afdef409bf0952b32e5cb1',
    'footer.php': 'e4836e538a4ef25d2ff49adceec1ab296fe93dab1fbef2ec7fb1fa1a71923f86',
    'page-about-gramiss.php': '00f9a57af349072bfb725a16e7c0d2bc3245eaecacf659472970d9c05d55431c',
    'assets/css/about-gramiss-v2.css': '05ee0e219aa14183346316a96a4ec8ccef2f706fd1fbecd559aad97deeadb915',
    'front-page.php': 'e92d85b78f33470171a9b76c40c29b134148a4ef0dfda575004b6e6b6d6a3f00',
    'assets/css/gramiss-1.css': '73e1e46ec5007e9842a3fba86c53fd9ea630cd5b1d64586545822301b8c14d9d',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

for path, expected in EXPECTED.items():
    actual = sha(mod.read(path))
    print('FILE', path, actual)
    if actual != expected:
        raise SystemExit('Drift detected: ' + path)

stamp = str(int(time.time()))
home_status, home = mod.get(mod.BASE + '/?about-v3-verify=' + stamp, 120)
print('HOME_HTTP', home_status, 'BYTES', len(home.encode()))
if home_status != 200:
    raise SystemExit('Home unhealthy')
primary = re.search(r'<nav class="primary-nav".*?</nav>', home, re.I | re.S)
labels = [] if not primary else [re.sub(r'<[^>]+>', '', x).strip() for x in re.findall(r'<a\b[^>]*>(.*?)</a>', primary.group(0), re.I | re.S)]
print('PRIMARY_NAV', labels)
if labels != ['Shop', 'Collections', 'Journal', 'Smart Guide']:
    raise SystemExit('Desktop nav changed')

status, about = mod.get(mod.BASE + '/about-gramiss/?about-v3-verify=' + stamp, 120)
print('ABOUT_HTTP', status, 'BYTES', len(about.encode()))
if status != 200:
    raise SystemExit('About unhealthy')
if 'GRAMISS ABOUT V2 START' not in about:
    raise SystemExit('About V2 marker missing')
if 'about-gramiss-v2.css?v=20260907-3' not in about:
    raise SystemExit('About V3 cache-bust URL missing')
if len(re.findall(r'<h1\b', about, re.I)) != 1:
    raise SystemExit('About H1 count changed')
print('PASS ABOUT SUPPORT V3 VERIFY')
