#!/usr/bin/env python3
import json, math, os, statistics, subprocess, time
from pathlib import Path

OUT=Path(os.environ.get('PERF_OUT','/tmp/gramiss-perf-after'))
LH='npx -y lighthouse@12.2.1'
TARGETS={
  'category_tshirt':'https://gramiss.ir/product-category/tshirt/',
  'shop':'https://gramiss.ir/shop/',
  'home':'https://gramiss.ir/',
}
BEFORE={
  ('category_tshirt','mobile'):{'score':69.5,'lcp_ms':13790.9,'total_bytes':29984796},
  ('category_tshirt','desktop'):{'score':80.0,'lcp_ms':2623.0,'total_bytes':29980000},
  ('shop','mobile'):{'score':64.0,'lcp_ms':9284.0,'total_bytes':5390000},
  ('shop','desktop'):{'score':81.5,'lcp_ms':1762.0,'total_bytes':4070000},
  ('home','mobile'):{'score':89.0,'lcp_ms':3228.6,'total_bytes':2010000},
}

def num(rep,key):
    v=rep.get('audits',{}).get(key,{}).get('numericValue')
    return float(v) if isinstance(v,(int,float)) else None

def summarize(rep):
    s=rep.get('categories',{}).get('performance',{}).get('score')
    reqs=rep.get('audits',{}).get('network-requests',{}).get('details',{}).get('items',[])
    return {'score':round(float(s)*100,1) if isinstance(s,(int,float)) else None,'lcp_ms':num(rep,'largest-contentful-paint'),'tbt_ms':num(rep,'total-blocking-time'),'cls':num(rep,'cumulative-layout-shift'),'total_bytes':num(rep,'total-byte-weight'),'requests':len(reqs),'server_ms':num(rep,'server-response-time')}

def med(rows,key):
    vals=[r[key] for r in rows if isinstance(r.get(key),(int,float)) and not math.isnan(r[key])]
    return statistics.median(vals) if vals else None

def run(label,url,mode,n):
    OUT.mkdir(parents=True,exist_ok=True); p=OUT/f'{label}-{mode}-{n}.json'
    cmd=LH.split()+[url,'--quiet','--chrome-flags=--headless --no-sandbox --disable-gpu','--output=json',f'--output-path={p}','--only-categories=performance','--max-wait-for-load=90000']
    if mode=='desktop':cmd.append('--preset=desktop')
    cp=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    if cp.returncode!=0 or not p.exists(): raise RuntimeError(cp.stdout[-1200:])
    row=summarize(json.loads(p.read_text('utf-8'))); print('AFTER_RUN',json.dumps({'label':label,'mode':mode,'run':n,**row},sort_keys=True)); return row

def main():
    plan=[('category_tshirt','mobile',2),('category_tshirt','desktop',2),('shop','mobile',2),('shop','desktop',2),('home','mobile',1)]
    summary={}
    for label,mode,repeats in plan:
        rows=[run(label,TARGETS[label],mode,i+1) for i in range(repeats)]
        after={k:med(rows,k) for k in rows[0].keys()}
        before=BEFORE[(label,mode)]
        delta={
          'score':after['score']-before['score'] if after['score'] is not None else None,
          'lcp_ms':after['lcp_ms']-before['lcp_ms'] if after['lcp_ms'] is not None else None,
          'total_bytes':after['total_bytes']-before['total_bytes'] if after['total_bytes'] is not None else None,
        }
        row={'label':label,'mode':mode,'before':before,'after':after,'delta':delta}
        summary[f'{label}:{mode}']=row; print('BEFORE_AFTER',json.dumps(row,sort_keys=True))
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True),'utf-8')
    cat=summary['category_tshirt:mobile']
    if cat['after']['total_bytes'] is None or cat['after']['total_bytes'] >= cat['before']['total_bytes']*0.5:
        raise SystemExit('FAIL category mobile weight did not improve by at least 50%')
    print('PASS PERFORMANCE AFTER IMAGE FIX V1 READ ONLY')

if __name__=='__main__': main()
