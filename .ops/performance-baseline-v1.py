#!/usr/bin/env python3
import argparse
import json
import math
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = 'https://gramiss.ir'
OUT = Path(os.environ.get('PERF_OUT', '/tmp/gramiss-perf'))
LIGHTHOUSE = os.environ.get('LIGHTHOUSE_CMD', 'npx -y lighthouse@12.2.1')
REPEATS = int(os.environ.get('PERF_REPEATS', '2'))


def fetch_text(url, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent': 'GramissPerformanceBaselineV1/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8', 'replace'), r.geturl()


def sitemap_urls(path):
    status, text, _ = fetch_text(BASE + '/' + path + '?perf=' + str(int(time.time())))
    if status != 200:
        raise RuntimeError(f'{path} HTTP {status}')
    root = ET.fromstring(text)
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [x.text.strip() for x in root.findall('.//s:loc', ns) if x.text]


def pick_urls():
    products = sitemap_urls('product-sitemap.xml')
    posts = sitemap_urls('post-sitemap.xml')
    if not products:
        raise RuntimeError('product sitemap empty')
    article = next((u for u in posts if '/وبلاگ/' not in u and '%D9%88%D8%A8%D9%84%D8%A7%DA%AF' not in u), posts[0] if posts else None)
    if not article:
        raise RuntimeError('post sitemap empty')
    return {
        'home': BASE + '/',
        'category_tshirt': BASE + '/product-category/tshirt/',
        'blog_archive': BASE + '/وبلاگ/',
        'article': article,
        'product': products[0],
    }


def slugify(label):
    return re.sub(r'[^a-z0-9_-]+', '-', label.lower()).strip('-')


def audit_num(report, audit_id):
    a = report.get('audits', {}).get(audit_id, {})
    v = a.get('numericValue')
    return float(v) if isinstance(v, (int, float)) else None


def audit_score(report, audit_id):
    a = report.get('audits', {}).get(audit_id, {})
    v = a.get('score')
    return float(v) if isinstance(v, (int, float)) else None


def summarize_report(report):
    perf = report.get('categories', {}).get('performance', {}).get('score')
    requests = report.get('audits', {}).get('network-requests', {}).get('details', {}).get('items', [])
    return {
        'score': round(float(perf) * 100, 1) if isinstance(perf, (int, float)) else None,
        'fcp_ms': audit_num(report, 'first-contentful-paint'),
        'lcp_ms': audit_num(report, 'largest-contentful-paint'),
        'cls': audit_num(report, 'cumulative-layout-shift'),
        'tbt_ms': audit_num(report, 'total-blocking-time'),
        'speed_index_ms': audit_num(report, 'speed-index'),
        'tti_ms': audit_num(report, 'interactive'),
        'server_response_ms': audit_num(report, 'server-response-time'),
        'total_bytes': audit_num(report, 'total-byte-weight'),
        'request_count': len(requests),
        'dom_nodes': audit_num(report, 'dom-size'),
        'mainthread_ms': audit_num(report, 'mainthread-work-breakdown'),
        'js_bootup_ms': audit_num(report, 'bootup-time'),
        'unused_js_ms': audit_num(report, 'unused-javascript'),
        'unused_css_ms': audit_num(report, 'unused-css-rules'),
        'render_blocking_ms': audit_num(report, 'render-blocking-resources'),
        'long_cache_score': audit_score(report, 'uses-long-cache-ttl'),
    }


def median(values):
    vals = [v for v in values if isinstance(v, (int, float)) and not math.isnan(v)]
    return statistics.median(vals) if vals else None


def aggregate(rows):
    keys = sorted({k for r in rows for k in r.keys()})
    out = {}
    for k in keys:
        vals = [r.get(k) for r in rows]
        if all(v is None or isinstance(v, (int, float)) for v in vals):
            out[k] = median(vals)
    return out


def run_lighthouse(label, url, mode, run_no):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f'{slugify(label)}-{mode}-{run_no}.json'
    cmd = LIGHTHOUSE.split() + [
        url,
        '--quiet',
        '--chrome-flags=--headless --no-sandbox --disable-gpu',
        '--output=json',
        f'--output-path={path}',
        '--only-categories=performance',
        '--max-wait-for-load=90000',
    ]
    if mode == 'desktop':
        cmd.append('--preset=desktop')
    print('LIGHTHOUSE_START', json.dumps({'label': label, 'mode': mode, 'run': run_no, 'url': url}, ensure_ascii=False))
    last = None
    for attempt in range(2):
        try:
            cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
            if cp.returncode == 0 and path.exists():
                report = json.loads(path.read_text('utf-8'))
                row = summarize_report(report)
                print('LIGHTHOUSE_RUN', json.dumps({'label': label, 'mode': mode, 'run': run_no, **row}, ensure_ascii=False, sort_keys=True))
                return row
            last = RuntimeError(f'lighthouse exit={cp.returncode} output={cp.stdout[-1500:]}')
        except Exception as exc:
            last = exc
        print('LIGHTHOUSE_RETRY', label, mode, run_no, attempt + 1, str(last)[:500])
        time.sleep(3)
    raise last


def verdict(m):
    problems = []
    if m.get('lcp_ms') is not None and m['lcp_ms'] > 2500:
        problems.append('LCP')
    if m.get('cls') is not None and m['cls'] > 0.1:
        problems.append('CLS')
    if m.get('tbt_ms') is not None and m['tbt_ms'] > 200:
        problems.append('TBT')
    if m.get('server_response_ms') is not None and m['server_response_ms'] > 800:
        problems.append('TTFB')
    if m.get('total_bytes') is not None and m['total_bytes'] > 2500000:
        problems.append('WEIGHT')
    return 'PASS' if not problems else 'NEEDS_WORK:' + ','.join(problems)


def run():
    urls = pick_urls()
    summary = {'version': 1, 'repeats': REPEATS, 'pages': {}}
    print('PERF_URLS', json.dumps(urls, ensure_ascii=False, sort_keys=True))
    for label, url in urls.items():
        summary['pages'][label] = {'url': url}
        for mode in ('mobile', 'desktop'):
            rows = [run_lighthouse(label, url, mode, i + 1) for i in range(REPEATS)]
            med = aggregate(rows)
            med['verdict'] = verdict(med)
            summary['pages'][label][mode] = med
            print('PERF_MEDIAN', json.dumps({'label': label, 'mode': mode, **med}, ensure_ascii=False, sort_keys=True))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), 'utf-8')

    mobile_scores = [p.get('mobile', {}).get('score') for p in summary['pages'].values()]
    desktop_scores = [p.get('desktop', {}).get('score') for p in summary['pages'].values()]
    overall = {
        'mobile_score_median': median(mobile_scores),
        'desktop_score_median': median(desktop_scores),
        'pages': len(summary['pages']),
        'repeats': REPEATS,
    }
    print('PERF_BASELINE_SUMMARY', json.dumps(overall, sort_keys=True))
    print('PASS PERFORMANCE BASELINE V1 READ ONLY')


def self_test():
    fake = {
        'categories': {'performance': {'score': 0.91}},
        'audits': {
            'largest-contentful-paint': {'numericValue': 1800},
            'cumulative-layout-shift': {'numericValue': 0.05},
            'total-blocking-time': {'numericValue': 80},
            'server-response-time': {'numericValue': 300},
            'total-byte-weight': {'numericValue': 1000000},
            'network-requests': {'details': {'items': [{}, {}]}},
        },
    }
    row = summarize_report(fake)
    assert row['score'] == 91.0
    assert row['request_count'] == 2
    assert verdict(row) == 'PASS'
    bad = dict(row)
    bad['lcp_ms'] = 3000
    assert verdict(bad).startswith('NEEDS_WORK:LCP')
    assert median([1, 3, 2]) == 2
    print('PASS PERFORMANCE BASELINE V1 SELFTEST')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--run', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        self_test()
    elif args.run:
        run()
    else:
        ap.error('choose --self-test or --run')
