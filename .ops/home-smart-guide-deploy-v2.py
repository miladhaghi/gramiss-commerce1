#!/usr/bin/env python3
import importlib.util
import json
import re
import time
from pathlib import Path

base = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_live_helpers', base)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

EXPECTED_HOME = '0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7'
EXPECTED_CSS = 'd62f85caf10a4bc154e83e8085f0d03bb1d99694bce216224a2d72a4ed2f8779'
PROTECTED = {
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}

NEW_SMART = r'''/* GRAMISS_HOME_SMART_GUIDE_V2 — unified dark counterpart of the Home visual system */
#smart-guide .g1-smart{
  position:relative;isolation:isolate;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);min-height:650px;
  border:1px solid rgba(255,255,255,.08);border-radius:42px;overflow:hidden;color:#fff;
  background:
    radial-gradient(ellipse at 18% 46%,rgba(146,126,107,.075) 0%,rgba(146,126,107,.035) 25%,transparent 54%),
    radial-gradient(ellipse at 74% 44%,rgba(77,112,157,.085) 0%,rgba(77,112,157,.035) 31%,transparent 58%),
    linear-gradient(116deg,#242320 0%,#202123 34%,#1b1e22 61%,#151b23 82%,#131820 100%);
  box-shadow:0 34px 84px rgba(13,16,21,.12),inset 0 1px 0 rgba(255,255,255,.035)
}
#smart-guide .g1-smart::before{content:"";position:absolute;z-index:-1;inset:-28%;pointer-events:none;background:radial-gradient(circle at 55% 50%,rgba(110,145,196,.055),transparent 35%);filter:blur(28px)}
#smart-guide .g1-smart::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:inherit;box-shadow:inset 0 0 120px rgba(3,7,12,.14)}
#smart-guide .g1-smart-copy{position:relative;z-index:3;padding:clamp(56px,5vw,84px);display:flex;flex-direction:column;justify-content:center}
#smart-guide .g1-smart-copy small{font:650 10px/1 Inter,Arial,sans-serif;letter-spacing:.21em;color:#8fafe0;direction:ltr}
#smart-guide .g1-smart-copy small::after{content:" / SMART GUIDE"}
#smart-guide .g1-smart-copy h2{max-width:640px;margin:24px 0 18px;font-size:clamp(48px,4.75vw,74px);line-height:1.34;letter-spacing:-.045em;text-wrap:balance}
#smart-guide .g1-smart-copy p{max-width:570px;margin:0;color:rgba(226,230,236,.65);font-size:14px;line-height:2.05}
body.gramiss-next-staging #smart-guide .g1-smart-points{margin:34px 0 38px!important;display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr));gap:0!important}
body.gramiss-next-staging #smart-guide .g1-smart-points span{position:relative;padding:25px 0 0 16px!important;border:0!important;border-radius:0!important;background:transparent!important;color:rgba(246,247,249,.86)!important;font-size:11px!important;line-height:1.7}
body.gramiss-next-staging #smart-guide .g1-smart-points span+span{border-inline-start:1px solid rgba(255,255,255,.09)!important;padding-inline-start:22px!important}
body.gramiss-next-staging #smart-guide .g1-smart-points span::before{position:absolute;inset:0 auto auto 0;color:#85a9dd;font:650 10px/1 Inter,Arial,sans-serif;letter-spacing:.08em;direction:ltr}
body.gramiss-next-staging #smart-guide .g1-smart-points span:nth-child(1)::before{content:"01"}
body.gramiss-next-staging #smart-guide .g1-smart-points span:nth-child(2)::before{content:"02"}
body.gramiss-next-staging #smart-guide .g1-smart-points span:nth-child(3)::before{content:"03"}
body.gramiss-next-staging #smart-guide .g1-actions{display:flex!important;flex-direction:column;align-items:flex-start;gap:16px}
body.gramiss-next-staging #smart-guide .g1-btn-light{width:auto!important;min-width:230px;min-height:58px;padding-inline:30px!important;border:1px solid rgba(255,255,255,.82)!important;background:#f7f6f3!important;color:#12161c!important;box-shadow:0 16px 38px rgba(0,0,0,.14)}
body.gramiss-next-staging #smart-guide .g1-btn-light::after{content:"↗";margin-inline-start:16px;font:600 15px/1 Inter,Arial,sans-serif}
body.gramiss-next-staging #smart-guide .g1-btn-light:hover{background:#fff!important;transform:translateY(-2px);box-shadow:0 20px 44px rgba(0,0,0,.18)}
body.gramiss-next-staging #smart-guide .g1-actions::after{content:"Smart Guide چطور تصمیم می‌گیرد؟";padding-bottom:4px;border-bottom:1px solid rgba(145,173,214,.36);color:rgba(226,231,238,.58);font-size:11px;line-height:1.5;direction:rtl}
#smart-guide .g1-smart-visual{position:relative;z-index:2;min-height:650px;display:grid;place-items:center;overflow:hidden;background:transparent}
#smart-guide .g1-smart-visual::before,#smart-guide .g1-smart-visual::after{content:"";position:absolute;width:112px;height:142px;border:1px solid rgba(255,255,255,.055);border-radius:14px;background:linear-gradient(155deg,rgba(255,255,255,.018),rgba(255,255,255,.004));box-shadow:0 18px 40px rgba(0,0,0,.06)}
#smart-guide .g1-smart-visual::before{left:11%;top:18%;transform:rotate(-5deg);box-shadow:330px 48px 0 -1px rgba(255,255,255,.008),24px 330px 0 -1px rgba(255,255,255,.006)}
#smart-guide .g1-smart-visual::after{right:12%;bottom:17%;transform:rotate(5deg);box-shadow:-315px -26px 0 -1px rgba(255,255,255,.006)}
body.gramiss-next-staging #smart-guide .g1-orbit{position:relative;z-index:3;width:360px!important;height:360px!important;border:1px solid rgba(218,228,242,.16)!important;border-radius:50%;display:grid!important;place-items:center!important;background:linear-gradient(rgba(211,223,239,.12),rgba(211,223,239,.12)) center/100% 1px no-repeat,linear-gradient(90deg,rgba(211,223,239,.12),rgba(211,223,239,.12)) center/1px 100% no-repeat,radial-gradient(circle,transparent 0 81px,rgba(212,225,243,.13) 82px 83px,transparent 84px 128px,rgba(212,225,243,.09) 129px 130px,transparent 131px);box-shadow:none!important}
body.gramiss-next-staging #smart-guide .g1-orbit::before,body.gramiss-next-staging #smart-guide .g1-orbit::after,body.gramiss-next-staging #smart-guide .g1-orbit>span::before,body.gramiss-next-staging #smart-guide .g1-orbit>span::after{position:absolute;width:78px;height:78px;display:grid;place-items:center;border:1px solid rgba(224,232,243,.18);border-radius:50%;background:rgba(23,28,34,.72);color:rgba(246,247,249,.80);font:500 10px/1.5 Estedad,Tahoma,sans-serif;box-shadow:0 10px 28px rgba(0,0,0,.10);backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px)}
body.gramiss-next-staging #smart-guide .g1-orbit::before{content:"استایل";top:-40px;left:50%;transform:translateX(-50%)}
body.gramiss-next-staging #smart-guide .g1-orbit::after{content:"کاربرد";bottom:-40px;left:50%;transform:translateX(-50%)}
body.gramiss-next-staging #smart-guide .g1-orbit>span{position:relative;z-index:4;width:116px;height:116px;display:grid;place-items:center;border-radius:50%;background:#fafafa;color:#11151b!important;font:800 35px/1 Inter,Arial,sans-serif!important;box-shadow:0 0 0 1px rgba(255,255,255,.52),0 0 0 13px rgba(121,155,204,.035),0 0 52px rgba(115,151,205,.24)}
body.gramiss-next-staging #smart-guide .g1-orbit>span::before{content:"فیت";right:-210px;top:19px}
body.gramiss-next-staging #smart-guide .g1-orbit>span::after{content:"بودجه";left:-210px;top:19px}
body.gramiss-next-staging #smart-guide .g1-smart-visual>p{position:absolute!important;z-index:4;inset:auto auto 46px 42px!important;width:190px;margin:0!important;font-size:0!important;letter-spacing:0!important;text-align:right!important;direction:rtl!important;color:transparent!important}
body.gramiss-next-staging #smart-guide .g1-smart-visual>p::before,body.gramiss-next-staging #smart-guide .g1-smart-visual>p::after{display:block;color:rgba(238,241,245,.68);font:500 11px/2 Estedad,Tahoma,sans-serif}
body.gramiss-next-staging #smart-guide .g1-smart-visual>p::before{content:"۱۲ گزینه بررسی شد"}
body.gramiss-next-staging #smart-guide .g1-smart-visual>p::after{content:"۳ انتخاب مناسب";color:rgba(238,241,245,.48)}
'''

MOBILE_OLD = '.g1-smart{min-height:0;border-radius:26px}.g1-smart-copy{padding:42px 24px}.g1-smart-copy h2{font-size:44px}.g1-smart-visual{min-height:330px}.g1-orbit{width:230px;height:230px}.g1-orbit::before{inset:38px}.g1-orbit::after{inset:80px}'
MOBILE_NEW = r'''#smart-guide .g1-smart{min-height:0;border-radius:28px}#smart-guide .g1-smart-copy{padding:44px 24px 38px}#smart-guide .g1-smart-copy h2{font-size:clamp(40px,11.2vw,52px);line-height:1.38}#smart-guide .g1-smart-copy p{font-size:12.5px;line-height:2}body.gramiss-next-staging #smart-guide .g1-smart-points{margin:28px 0 31px!important}body.gramiss-next-staging #smart-guide .g1-smart-points span{padding-top:22px!important;padding-inline:8px!important;font-size:9.5px!important}body.gramiss-next-staging #smart-guide .g1-smart-points span+span{padding-inline-start:12px!important}body.gramiss-next-staging #smart-guide .g1-btn-light{width:100%!important;min-width:0}body.gramiss-next-staging #smart-guide .g1-actions{width:100%;align-items:stretch}body.gramiss-next-staging #smart-guide .g1-actions::after{text-align:center;align-self:center}body.gramiss-next-staging #smart-guide .g1-smart-visual{min-height:400px!important}body.gramiss-next-staging #smart-guide .g1-orbit{width:235px!important;height:235px!important;background:linear-gradient(rgba(211,223,239,.11),rgba(211,223,239,.11)) center/100% 1px no-repeat,linear-gradient(90deg,rgba(211,223,239,.11),rgba(211,223,239,.11)) center/1px 100% no-repeat,radial-gradient(circle,transparent 0 59px,rgba(212,225,243,.12) 60px 61px,transparent 62px 90px,rgba(212,225,243,.08) 91px 92px,transparent 93px)}body.gramiss-next-staging #smart-guide .g1-orbit>span{width:88px;height:88px;font-size:29px!important}body.gramiss-next-staging #smart-guide .g1-orbit::before,body.gramiss-next-staging #smart-guide .g1-orbit::after,body.gramiss-next-staging #smart-guide .g1-orbit>span::before,body.gramiss-next-staging #smart-guide .g1-orbit>span::after{width:60px;height:60px;font-size:9px}body.gramiss-next-staging #smart-guide .g1-orbit::before{top:-30px}body.gramiss-next-staging #smart-guide .g1-orbit::after{bottom:-30px}body.gramiss-next-staging #smart-guide .g1-orbit>span::before{right:-132px;top:14px}body.gramiss-next-staging #smart-guide .g1-orbit>span::after{left:-132px;top:14px}body.gramiss-next-staging #smart-guide .g1-smart-visual>p{inset:auto auto 17px 18px!important;width:150px}body.gramiss-next-staging #smart-guide .g1-smart-visual>p::before,body.gramiss-next-staging #smart-guide .g1-smart-visual>p::after{font-size:9.5px}#smart-guide .g1-smart-visual::before,#smart-guide .g1-smart-visual::after{width:76px;height:98px;opacity:.6}'''

front = mod.read('front-page.php')
css = mod.read('assets/css/gramiss-1.css')
print('PRE_HOME_SHA', mod.sha(front))
print('PRE_CSS_SHA', mod.sha(css))
if mod.sha(front) != EXPECTED_HOME:
    raise SystemExit('REFUSE: live Home changed')
if mod.sha(css) != EXPECTED_CSS:
    raise SystemExit('REFUSE: gramiss-1.css changed')
for path, expected in PROTECTED.items():
    actual = mod.sha(mod.read(path))
    print('PROTECTED_PRE', path, actual)
    if actual != expected:
        raise SystemExit('REFUSE: protected drift ' + path)

start = css.find('.g1-smart{')
end = css.find('.g1-editorial-grid{', start)
if start < 0 or end < 0:
    raise SystemExit('REFUSE: Smart Guide CSS anchors missing')
if css.count('/* GRAMISS_HOME_SMART_GUIDE_V2'):
    raise SystemExit('REFUSE: V2 marker already present')
if css.count(MOBILE_OLD) != 1:
    raise SystemExit('REFUSE: expected one legacy mobile Smart Guide rule')
new_css = css[:start] + NEW_SMART + '\n\n' + css[end:]
new_css = new_css.replace(MOBILE_OLD, MOBILE_NEW, 1)

stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
backup = 'assets/css/gramiss-1.css.bak-smart-guide-v2-' + stamp
try:
    mod.save(backup, css)
    mod.save('assets/css/gramiss-1.css', new_css)
    mod.flush()
    errors = []
    stored = mod.read('assets/css/gramiss-1.css')
    print('POST_CSS_SHA', mod.sha(stored))
    if stored != new_css:
        errors.append('stored CSS mismatch')
    if mod.sha(mod.read('front-page.php')) != EXPECTED_HOME:
        errors.append('Home changed')
    for path, expected in PROTECTED.items():
        if mod.sha(mod.read(path)) != expected:
            errors.append('protected changed ' + path)
    status, page = mod.get(mod.BASE + '/?smart-guide-v2=' + str(time.time()), 180)
    print('HOME_HTTP', status, 'BYTES', len(page.encode()))
    if status != 200:
        errors.append('Home HTTP ' + str(status))
    for marker in ['id="smart-guide"', 'فروشنده‌ای آرام، دقیق و بی‌قضاوت.', 'شناخت نیاز', 'مقایسه شفاف', 'پیشنهاد قابل توضیح', 'g1-looks', 'id="collections"', 'id="products"']:
        if marker not in page:
            errors.append('render missing ' + marker)
    if len(re.findall(r'<h1\b', page, re.I)) != 1:
        errors.append('Home H1 count changed')
    if 'GRAMISS_HOME_SMART_GUIDE_V2' not in stored:
        errors.append('V2 CSS marker missing')
    print('VERIFY_ERRORS', json.dumps(errors, ensure_ascii=False))
    if errors:
        raise RuntimeError('; '.join(errors))
    print('BACKUP', backup)
    print('PASS HOME SMART GUIDE V2 DEPLOY')
except Exception:
    mod.save('assets/css/gramiss-1.css', css)
    mod.flush()
    restored = mod.sha(mod.read('assets/css/gramiss-1.css'))
    print('ROLLBACK_CSS_SHA', restored)
    if restored != EXPECTED_CSS:
        print('ROLLBACK_ERROR expected', EXPECTED_CSS, 'got', restored)
    raise
