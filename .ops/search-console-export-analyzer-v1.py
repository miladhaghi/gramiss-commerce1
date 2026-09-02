import argparse,csv,json,math,statistics,tempfile
from pathlib import Path

def n(s): return ' '.join(str(s or '').strip().lower().replace('_',' ').split())
def num(v):
    s=str(v or '').strip().replace(',','')
    if not s:return 0.0
    if s.endswith('%'):return float(s[:-1])/100.0
    try:return float(s)
    except:return 0.0

def load(path):
    raw=Path(path).read_text(encoding='utf-8-sig')
    try:d=csv.Sniffer().sniff(raw[:4096],delimiters=',;\t')
    except:d=csv.excel
    rows=list(csv.DictReader(raw.splitlines(),dialect=d))
    if not rows:raise SystemExit('No rows found')
    headers=list(rows[0]); hm={n(h):h for h in headers}
    aliases={
      'clicks':['clicks','کلیک'], 'impressions':['impressions','نمایش'], 'ctr':['ctr','میانگین نرخ کلیک'],
      'position':['position','average position','میانگین موقعیت'],
      'query':['query','queries','top queries','جستجوها','عبارت جستجو'],
      'page':['page','pages','top pages','صفحه','صفحات'], 'date':['date','dates','تاریخ']}
    cols={}
    for k,vals in aliases.items():
        for a in vals:
            if a in hm: cols[k]=hm[a];break
    for req in ('clicks','impressions','ctr','position'):
        if req not in cols:raise SystemExit('Missing required metric column: '+req+'; headers='+repr(headers))
    dim=next((k for k in ('query','page','date') if k in cols),None)
    if not dim:
        metric={cols[x] for x in ('clicks','impressions','ctr','position')}
        extra=[h for h in headers if h not in metric]
        if not extra:raise SystemExit('No dimension column found')
        cols['dimension']=extra[0];dim='dimension'
    out=[]
    for r in rows:
        out.append({'key':str(r.get(cols[dim],'')).strip(),'clicks':num(r.get(cols['clicks'])),'impressions':num(r.get(cols['impressions'])),'ctr':num(r.get(cols['ctr'])),'position':num(r.get(cols['position']))})
    return dim,out

def analyze(path,top=20):
    dim,rows=load(path); imp=sum(x['impressions'] for x in rows); clk=sum(x['clicks'] for x in rows)
    weighted=sum(x['position']*x['impressions'] for x in rows if x['impressions']>0)/(imp or 1)
    summary={'dimension':dim,'rows':len(rows),'clicks':round(clk,2),'impressions':round(imp,2),'ctr':round(clk/(imp or 1),6),'impression_weighted_position':round(weighted,2)}
    striking=sorted([x for x in rows if 4<=x['position']<=20 and x['impressions']>0],key=lambda x:(-x['impressions'],x['position']))[:top]
    ranked=[x for x in rows if 1<=x['position']<=10 and x['impressions']>0]
    ctr_med=statistics.median([x['ctr'] for x in ranked]) if ranked else 0
    imps=[x['impressions'] for x in rows if x['impressions']>0]; q75=statistics.quantiles(imps,n=4,method='inclusive')[2] if len(imps)>=2 else (imps[0] if imps else 0)
    ctr_opps=sorted([x for x in ranked if x['impressions']>=q75 and x['ctr']<ctr_med],key=lambda x:(-x['impressions'],x['ctr']))[:top]
    discovery=sorted([x for x in rows if x['position']>20 and x['impressions']>=q75],key=lambda x:-x['impressions'])[:top]
    result={'summary':summary,'relative_thresholds':{'top_impression_quartile_floor':round(q75,2),'top10_ctr_median':round(ctr_med,6)},'striking_distance':striking,'high_impression_relative_low_ctr':ctr_opps,'high_impression_lower_rank':discovery}
    print(json.dumps(result,ensure_ascii=False,indent=2));return result

def selftest():
    text='Query,Clicks,Impressions,CTR,Position\nboxy tee,8,400,2%,7.2\nbaggy pants,2,300,0.67%,14\nlinen shirt,20,500,4%,3.1\nwhite sneakers,1,250,0.4%,27\n'
    with tempfile.NamedTemporaryFile('w',suffix='.csv',encoding='utf-8',delete=False) as f:f.write(text);p=f.name
    r=analyze(p,5);assert r['summary']['rows']==4;assert any(x['key']=='boxy tee' for x in r['striking_distance']);assert any(x['key']=='white sneakers' for x in r['high_impression_lower_rank']);print('PASS SEARCH CONSOLE EXPORT ANALYZER V1 SELFTEST')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('path',nargs='?');ap.add_argument('--top',type=int,default=20);ap.add_argument('--self-test',action='store_true');a=ap.parse_args()
    if a.self_test:selftest()
    elif a.path:analyze(a.path,a.top)
    else:ap.error('provide CSV path or --self-test')
