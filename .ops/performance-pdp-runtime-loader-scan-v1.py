#!/usr/bin/env python3
import json, os, re, ssl, urllib.parse, urllib.request

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']
ROOT='public_html/wp-content/themes/gramiss-theme-next'
CTX=ssl._create_unverified_context()

FILES=[
  'header.php',
  'assets/js/product-mobile-v1-3.js',
  'assets/js/product-mobile-v1-4.js',
  'assets/js/product-runtime-gallery-fix.js',
  'assets/js/product-runtime-variation-ui.js',
]


def api(fn,params):
    url=f'https://{HOST}:2083/execute/Fileman/{fn}?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={'Authorization':f'cpanel {USER}:{TOKEN}'})
    with urllib.request.urlopen(req,context=CTX,timeout=90) as r:
        payload=json.loads(r.read().decode('utf-8','replace'))
    result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
    if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
    return result.get('data')


def extract(data):
    if isinstance(data,str): return data
    if isinstance(data,dict):
        for k in ('content','file_content','data'):
            if isinstance(data.get(k),str): return data[k]
    return ''


def read(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel)
    return extract(api('get_file_content',{
      'dir':ROOT+('/'+parent if parent else ''),
      'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'
    }))


def snippets(text, needles, radius=1000, cap=8):
    out=[]
    for needle in needles:
        pos=0; count=0
        while True:
            i=text.find(needle,pos)
            if i<0: break
            count+=1
            out.append({'needle':needle,'index':i,'text':text[max(0,i-radius):min(len(text),i+radius)]})
            pos=i+max(1,len(needle))
            if count>=cap: break
    return out

texts={f:read(f) for f in FILES}
header=texts['header.php']

# Exact live loader inventory in source order.
loader_patterns=[
  r'<script\b[^>]*\bsrc=["\'][^"\']*(?:product-mobile|product-runtime)[^"\']*["\'][^>]*></script>',
  r'<link\b[^>]*\bhref=["\'][^"\']*(?:product-mobile|product-runtime)[^"\']*["\'][^>]*>',
]
loaders=[]
for pattern in loader_patterns:
    for m in re.finditer(pattern,header,re.I|re.S):
        loaders.append((m.start(),re.sub(r'\s+',' ',m.group(0)).strip()))
loaders.sort(key=lambda x:x[0])
print('LIVE_RUNTIME_LOADERS',json.dumps([{'index':i,'tag':tag} for i,tag in loaders],ensure_ascii=False))

# Search source for relevant loader names even if embedded in PHP strings.
print('HEADER_RUNTIME_SNIPPETS',json.dumps(snippets(header,[
  'product-mobile-v1.js','product-mobile-v1-2.js','product-mobile-v1-3.js','product-mobile-v1-4.js',
  'product-runtime-gallery-fix.js','product-runtime-variation-ui.js',
  'GRAMISS PRODUCT MOBILE','GRAMISS PDP MOBILE','g1-style-intelligence'
],1200,12),ensure_ascii=False))

for rel in FILES[1:]:
    text=texts[rel]
    needles=['localStorage','sessionStorage','selectedKey','buildCard','fetchProduct','fetch(',
             'DOMContentLoaded','window.addEventListener','requestIdleCallback','IntersectionObserver',
             'g3ApplyVariationImage','applyVariationImage','previewSelectedColor','resetOrPreview',
             'full_src','data-large_image','srcset','sizes','initGallery','initForm','init()']
    print('JS_SCAN',json.dumps({
      'path':rel,'bytes':len(text.encode('utf-8')),
      'snippets':snippets(text,needles,900,6)
    },ensure_ascii=False))

# Count duplicate style-intelligence signatures across loaded source files.
for rel in ['assets/js/product-mobile-v1-3.js','assets/js/product-mobile-v1-4.js']:
    text=texts[rel]
    print('STYLE_SIGNATURE',json.dumps({
      'path':rel,
      'g1_style_card':text.count('g1-style-card'),
      'fetch_product':text.count('fetchProduct'),
      'local_storage':text.count('localStorage'),
      'eager_literal':text.count("'eager'")+text.count('"eager"'),
      'og_image':text.count('og:image'),
      'data_large_image':text.count('data-large_image'),
    },sort_keys=True))

print('PASS PDP RUNTIME LOADER SCAN READ ONLY')
