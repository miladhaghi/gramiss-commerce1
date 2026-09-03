#!/usr/bin/env python3
import importlib.util
from pathlib import Path

base = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_live_helpers', base)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

front = mod.read('front-page.php')
css = mod.read('assets/css/gramiss-1.css')

start = front.find('<section class="g1-section g1-reveal" id="smart-guide">')
end = front.find('<section class="g1-section g1-reveal" id="journal">', start)
print('LIVE_HOME_SHA', mod.sha(front))
print('SMART_GUIDE_START', start, 'JOURNAL_START', end)
if start < 0 or end < 0:
    raise SystemExit('SMART GUIDE OR JOURNAL ANCHOR NOT FOUND')
print('SMART_GUIDE_BLOCK_BEGIN')
print(front[start:end])
print('SMART_GUIDE_BLOCK_END')

css_start = css.find('.g1-smart{')
css_end = css.find('.g1-editorial-grid{', css_start)
print('GRAMISS1_CSS_SHA', mod.sha(css))
print('SMART_CSS_START', css_start, 'SMART_CSS_END', css_end)
if css_start < 0 or css_end < 0:
    raise SystemExit('SMART GUIDE CSS ANCHORS NOT FOUND')
print('SMART_GUIDE_CSS_BEGIN')
print(css[css_start:css_end])
print('SMART_GUIDE_CSS_END')
print('PASS SMART GUIDE INSPECT V2 READ ONLY')
