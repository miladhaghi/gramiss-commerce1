#!/usr/bin/env python3
import html
import json
import math
import os
import re
import statistics
import subprocess
import urllib.request
from pathlib import Path

OUT=Path(os.environ.get('PERF_OUT','/tmp/gramiss-pdp-perf'))
LH='npx -y lighthouse@12.2.1'
SITEMAP='https://gramiss.ir/product-sitemap.xml'


def get_text(url):
    req=urllib.request.Request(url,headers={'User-Agent':'GramissPDPPerformanceV1/1.0','Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.status,r.read().decode('utf-8','replace')


def num(rep,key):
    v=rep.get('audits',{}).get(key,{}).get('numericValue')
    return float(v) if isinstance(v,(int,float)) else None


def summarize(rep):
    s=rep.get('categories',{}).get('performance',{}).get('score')
    reqs=rep.get('audits',{}).get('network-requests',{}).get('details',{}).get('items',[])
    return {
      'score': round(float(s)*100,1) if isinstance(s,(int,float)) else None,
      'lcp_ms': num(rep,'largest-contentful-paint'),
      'fcp_ms': num(rep,'first-contentful-paint'),
      'tbt_ms': num(rep,'total-blocking-time'),
      'cls': num(rep,'cumulative-layout-shift'),
      'server_ms': num(rep,'server-response-time'),
      'total_bytes': num(rep,'total-byte-weight'),
      'requests': len(reqs),
    }


def run(url,mode,n):
    OUT.mkdir(parents=True,exist_ok=True)
    p=OUT/f'pdp-{mode}-{n}.json'
    cmd=LH.split()+[url,'--quiet','--chrome-flags=--headless --no-sandbox --disable-gpu','--output=json',f'--output-path={p}','--only-categories=performance','--max-wait-for-load=90000']
    if mode=='desktop': cmd.append('--preset=desktop')
    cp=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    if cp.returncode!=0 or not p.exists(): raise RuntimeError(cp.stdout[-1200:])
    row=summarize(json.loads(p.read_text('utf-8')))
    print('PDP_LIGHTHOUSE_RUN',json.dumps({'url':url,'mode':mode,'run':n,**row},sort_keys=True))
    return row


def median(rows,key):
    vals=[r[key] for r in rows if isinstance(r.get(key),(int,float)) and not math.isnan(r[key])]
    return statistics.median(vals) if vals else None


status,xml=get_text(SITEMAP)
if status!=200: raise SystemExit('FAIL product sitemap HTTP '+str(status))
urls=[html.unescape(x.strip()) for x in re.findall(r'<loc>(.*?)</loc>',xml,re.I|re.S)]
if len(urls)!=47: raise SystemExit('FAIL expected 47 product URLs, got '+str(len(urls)))
# Choose a stable middle sitemap product rather than a boundary item.
url=urls[len(urls)//2]
print('PDP_TARGET',url)
mobile=[run(url,'mobile',1),run(url,'mobile',2)]
desktop=[run(url,'desktop',1)]
summary={
  'url':url,
  'mobile':{k:median(mobile,k) for k in mobile[0]},
  'desktop':{k:median(desktop,k) for k in desktop[0]},
}
print('PDP_PERF_SUMMARY',json.dumps(summary,sort_keys=True))
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True),'utf-8')
if summary['mobile']['score'] is None or summary['mobile']['score']<80:
    raise SystemExit('FAIL PDP mobile performance score below 80')
if summary['mobile']['lcp_ms'] is None or summary['mobile']['lcp_ms']>4000:
    raise SystemExit('FAIL PDP mobile LCP above 4s')
if summary['mobile']['cls'] is not None and summary['mobile']['cls']>0.1:
    raise SystemExit('FAIL PDP mobile CLS above 0.1')
print('PASS REAL PDP PERFORMANCE BASELINE V1 READ ONLY')
