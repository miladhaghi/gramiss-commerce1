#!/usr/bin/env python3
import re
import time
import urllib.request

BASE = 'https://gramiss.ir/product-category/tshirt/'
CHROME = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36'


def fetch(label, url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode('utf-8', 'replace')
        hs = {k.lower(): v for k, v in r.headers.items()}
    full = len(re.findall(r'attachment-full|size-full', body, re.I))
    card = len(re.findall(r'attachment-gramiss-product-card|size-gramiss-product-card', body, re.I))
    print('CACHE_VARIANT', {
        'label': label,
        'status': r.status,
        'bytes_html': len(body.encode('utf-8')),
        'attachment_full_tokens': full,
        'card_tokens': card,
        'cache_control': hs.get('cache-control', ''),
        'age': hs.get('age', ''),
        'x_litespeed_cache': hs.get('x-litespeed-cache', ''),
        'x_cache': hs.get('x-cache', ''),
        'server': hs.get('server', ''),
        'vary': hs.get('vary', ''),
    })
    return full, card


stamp = str(int(time.time()))
results = []
results.append(fetch('chrome-normal', BASE, {'User-Agent': CHROME}))
results.append(fetch('chrome-no-cache', BASE, {'User-Agent': CHROME, 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}))
results.append(fetch('python-no-cache', BASE, {'User-Agent': 'GramissPerfProbe/1.0', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}))
results.append(fetch('chrome-cache-bust', BASE + '?perf-cache-probe=' + stamp, {'User-Agent': CHROME, 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}))

print('CACHE_VARIANT_RESULTS', results)
if not any(card > 0 for _, card in results):
    raise SystemExit('FAIL no responsive card HTML observed in any variant')
print('PASS PERFORMANCE CACHE VARIANT PROBE V1 READ ONLY')
