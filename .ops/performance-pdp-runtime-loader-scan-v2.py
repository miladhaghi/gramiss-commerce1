#!/usr/bin/env python3
import json, os, ssl, urllib.parse, urllib.request

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']
ROOT='public_html/wp-content/themes/gramiss-theme-next'; CTX=ssl._create_unverified_context()
FILES=['assets/js/product-mobile-v1.js','assets/js/product-mobile-v1-2.js','assets/js/product-mobile-v1-3.js','assets/js/product-mobile-v1-4.js']

def api(fn,params):
    u=f'https://{HOST}:2083/execute/Fileman/{fn}?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(u,headers={'Authorization':f'cpanel {USER}:{TOKEN}'})
    with urllib.request.urlopen(req,context=CTX,timeout=90) as r:p=json.loads(r.read().decode('utf-8','replace'))
    z=p.get('result') if isinstance(p.get('result'),dict) else p
    if not isinstance(z,dict) or z.get('status')!=1:raise RuntimeError(str(z))
    return z.get('data')
def extract(d):
    if isinstance(d,str):return d
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str):return d[k]
    return ''
def read(rel):
    parent,name=rel.rsplit('/',1)
    return extract(api('get_file_content',{'dir':ROOT+'/'+parent,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'}))
def snippets(text,needles,radius=1250,cap=10):
    out=[]
    for needle in needles:
        pos=0;n=0
        while True:
            i=text.find(needle,pos)
            if i<0:break
            n+=1;out.append({'needle':needle,'index':i,'text':text[max(0,i-radius):min(len(text),i+radius)]})
            pos=i+max(1,len(needle))
            if n>=cap:break
    return out
needles=['g1-style','related.products','section.related','ul.products','createElement(\'img\')','createElement("img")','img.src','image:',
         'products?category','wc/store/v1','fetch(','XMLHttpRequest','localStorage','eager','lazy','currentSrc','full_src','data-large_image',
         'woocommerce-product-gallery','g3-dual','querySelectorAll(\':scope > li.product\')','querySelectorAll(":scope > li.product")',
         'DOMContentLoaded','window.addEventListener','requestIdleCallback','setTimeout','MutationObserver','IntersectionObserver']
for rel in FILES:
    text=read(rel)
    print('MOBILE_RUNTIME_SCAN',json.dumps({
      'path':rel,'bytes':len(text.encode('utf-8')),
      'counts':{k:text.count(k) for k in ['g1-style','related.products','wc/store/v1','img.src','full_src','data-large_image','eager','fetch(','localStorage']},
      'snippets':snippets(text,needles)
    },ensure_ascii=False))
print('PASS PDP MOBILE RUNTIME SCAN V2 READ ONLY')
