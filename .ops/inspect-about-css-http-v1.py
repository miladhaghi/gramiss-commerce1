#!/usr/bin/env python3
import importlib.util
import re
import time
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

stamp = str(int(time.time()))
status, page = mod.get(mod.BASE + '/about-gramiss/?css-check=' + stamp, 120)
print('PAGE_HTTP', status, 'BYTES', len(page.encode()))
match = re.search(r'<link[^>]+href=["\']([^"\']*about-gramiss-v2\.css[^"\']*)["\']', page, re.I)
if not match:
    raise SystemExit('V2 CSS href missing')
href = match.group(1).replace('&amp;', '&')
print('CSS_HREF', href)
css_status, css = mod.get(href, 120)
print('CSS_HTTP', css_status, 'BYTES', len(css.encode()))
for needle in ['.g-about-v2{', '.gav2-copy h1{', '.gav2-card-grid{', '.gav2-smart-panel{']:
    print('HAS', needle, needle in css)
if css_status != 200 or '.gav2-copy h1{' not in css:
    raise SystemExit('Public V2 CSS unhealthy')
print('PASS ABOUT CSS HTTP INSPECT')
