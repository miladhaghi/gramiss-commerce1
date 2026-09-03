#!/usr/bin/env python3
import json, math, os, statistics, subprocess
from pathlib import Path

OUT = Path(os.environ.get('PERF_OUT','/tmp/gramiss-pdp-after'))
LH = 'npx -y lighthouse@12.2.1'
URL = 'https://gramiss.ir/product/%d8%b4%d9%84%d9%88%d8%a7%d8%b1-%d8%ac%db%8c%d9%86-%d8%a8%d8%a7%d9%84%d9%86%db%8c-%d8%aa%db%8c%d9%86%d8%aa-%d8%b3%d8%a8%d8%b2/'


def num(rep,key):
    v = rep.get('audits',{}).get(key,{}).get('numericValue')
    return float(v) if isinstance(v,(int,float)) else None


def network(rep):
    return rep.get('audits',{}).get('network-requests',{}).get('details',{}).get('items',[]) or []


def summarize(rep):
    score = rep.get('categories',{}).get('performance',{}).get('score')
    reqs = network(rep)
    imgs = [r for r in reqs if str(r.get('resourceType','')).lower() == 'image' or str(r.get('mimeType','')).lower().startswith('image/')]
    def size(r):
        v = r.get('transferSize')
        return float(v) if isinstance(v,(int,float)) else 0.0
    largest = sorted(imgs,key=size,reverse=True)[:12]
    return {
        'score': round(float(score)*100,1) if isinstance(score,(int,float)) else None,
        'lcp_ms': num(rep,'largest-contentful-paint'),
        'fcp_ms': num(rep,'first-contentful-paint'),
        'tbt_ms': num(rep,'total-blocking-time'),
        'cls': num(rep,'cumulative-layout-shift'),
        'server_ms': num(rep,'server-response-time'),
        'total_bytes': num(rep,'total-byte-weight'),
        'requests': len(reqs),
        'image_bytes': sum(size(r) for r in imgs),
        'image_requests': len(imgs),
        'images_over_500kb': sum(1 for r in imgs if size(r) > 500000),
        'images_over_1mb': sum(1 for r in imgs if size(r) > 1000000),
        'largest_images': [{'bytes':size(r),'url':r.get('url','')} for r in largest],
    }


def run(mode,n):
    OUT.mkdir(parents=True,exist_ok=True)
    p = OUT / f'pdp-{mode}-{n}.json'
    cmd = LH.split() + [URL,'--quiet','--chrome-flags=--headless --no-sandbox --disable-gpu','--output=json',f'--output-path={p}','--only-categories=performance','--max-wait-for-load=90000']
    if mode == 'desktop': cmd.append('--preset=desktop')
    cp = subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=210)
    if cp.returncode != 0 or not p.exists():
        raise RuntimeError(cp.stdout[-1600:])
    row = summarize(json.loads(p.read_text('utf-8')))
    print('PDP_AFTER_RUN',json.dumps({'url':URL,'mode':mode,'run':n,**row},sort_keys=True))
    return row


def median(rows,key):
    vals = [r[key] for r in rows if isinstance(r.get(key),(int,float)) and not math.isnan(r[key])]
    return statistics.median(vals) if vals else None

mobile = [run('mobile',1),run('mobile',2)]
desktop = [run('desktop',1)]
keys = ['score','lcp_ms','fcp_ms','tbt_ms','cls','server_ms','total_bytes','requests','image_bytes','image_requests','images_over_500kb','images_over_1mb']
summary = {
    'url': URL,
    'mobile': {k: median(mobile,k) for k in keys},
    'desktop': {k: median(desktop,k) for k in keys},
    'mobile_runs': mobile,
    'desktop_runs': desktop,
}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True),'utf-8')
print('PDP_AFTER_SUMMARY',json.dumps({'url':URL,'mobile':summary['mobile'],'desktop':summary['desktop']},sort_keys=True))
print('PASS PDP POST-FIX LIGHTHOUSE AUDIT')
