#!/usr/bin/env python3
import importlib.util
import re
import time
from pathlib import Path

base = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_live_helpers', base)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

EXPECTED_HOME='e92d85b78f33470171a9b76c40c29b134148a4ef0dfda575004b6e6b6d6a3f00'
EXPECTED_CSS='73e1e46ec5007e9842a3fba86c53fd9ea630cd5b1d64586545822301b8c14d9d'
PROTECTED={
 'template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
 'assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
 'assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}
front=mod.read('front-page.php'); css=mod.read('assets/css/gramiss-1.css')
print('HOME_SHA',mod.sha(front)); print('CSS_SHA',mod.sha(css))
if mod.sha(front)!=EXPECTED_HOME: raise SystemExit('FAIL Home V3 drift')
if mod.sha(css)!=EXPECTED_CSS: raise SystemExit('FAIL CSS V3 drift')
for p,e in PROTECTED.items():
 a=mod.sha(mod.read(p)); print('PROTECTED',p,a)
 if a!=e: raise SystemExit('FAIL protected drift '+p)
status,page=mod.get(mod.BASE+'/?smart-guide-v3-verify='+str(time.time()),180)
print('HOME_HTTP',status,'BYTES',len(page.encode()))
if status!=200: raise SystemExit('FAIL Home HTTP')
for marker in ['g1-smart-v3','GRAMISS / SMART GUIDE','فروشنده‌ای آرام،','دقیق و بی‌قضاوت.','g1-smart-product-card','g1-smart-map','id="journal"','g1-looks','id="collections"','id="products"']:
 if marker not in page: raise SystemExit('FAIL missing '+marker)
imgs=len(re.findall(r'g1-smart-product-card[^>]*>.*?<img\b',page,re.I|re.S))
print('SMART_PRODUCT_IMAGE_CARDS',imgs)
if imgs<4: raise SystemExit('FAIL too few Smart Guide product images')
if len(re.findall(r'<h1\b',page,re.I))!=1: raise SystemExit('FAIL H1 count')
print('PASS HOME SMART GUIDE V3 VERIFY')
