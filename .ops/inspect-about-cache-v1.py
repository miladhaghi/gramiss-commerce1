#!/usr/bin/env python3
import importlib.util
import json
import time
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def state(body):
    return {
        'v2_marker': 'GRAMISS ABOUT V2 START' in body,
        'v2_css': 'about-gramiss-v2.css' in body,
        'old_marker': 'GRAMISS ABOUT V1 START' in body,
        'hero_title': 'کمتر حدس بزن' in body,
    }

stamp = str(int(time.time()))
plain_status, plain = mod.get(mod.BASE + '/about-gramiss/', 120)
busted_status, busted = mod.get(mod.BASE + '/about-gramiss/?cache-check=' + stamp, 120)
print('PLAIN_HTTP', plain_status, 'STATE', json.dumps(state(plain), ensure_ascii=False), 'BYTES', len(plain.encode()))
print('BUSTED_HTTP', busted_status, 'STATE', json.dumps(state(busted), ensure_ascii=False), 'BYTES', len(busted.encode()))
print('DIFFERENT', state(plain) != state(busted) or plain != busted)
if busted_status != 200 or not state(busted)['v2_marker'] or not state(busted)['v2_css']:
    raise SystemExit('Cache-busted About V2 unhealthy')
print('PASS ABOUT CACHE INSPECT')
