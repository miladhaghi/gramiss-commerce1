import json, os, ssl, urllib.parse, urllib.request, re
HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']; ROOT=os.environ['THEME_ROOT'].strip('/'); CTX=ssl._create_unverified_context()
PUBLIC='public_html'

def call(func, params):
    url=f'https://{HOST}:2083/execute/Fileman/{func}?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={'Authorization':f'cpanel {USER}:{TOKEN}'})
    with urllib.request.urlopen(req,context=CTX,timeout=60) as r:
        p=json.loads(r.read().decode())
    result=p.get('result') if isinstance(p.get('result'),dict) else p
    if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
    return result.get('data')

def read_abs(directory,name):
    d=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str): return d[k]
    return d if isinstance(d,str) else ''

def read_live(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=ROOT if not parent else f'{ROOT}/{parent}'
    return read_abs(directory,name)
footer=read_live('footer.php'); css=read_live('assets/css/theme.css')
print('LIVE footer trust wrapper:', 'class="footer-trust"' in footer)
print('LIVE trustseal href:', 'trustseal.enamad.ir/?id=7094948' in footer)
print('LIVE theme marker:', 'GRAMISS_ENAMAD_FOOTER_V1' in css)

def fetch_url(label,url,headers=None):
    h={'User-Agent':'GramissEnamadDiag/4.0'}
    if headers: h.update(headers)
    req=urllib.request.Request(url,headers=h)
    with urllib.request.urlopen(req,context=CTX,timeout=60) as r:
        body=r.read().decode('utf-8','replace')
        print(label,'HTTP:',r.status,'wrapper:', 'class="footer-trust"' in body,'trustseal:', 'trustseal.enamad.ir/?id=7094948' in body)
        for k in ('Server','X-Powered-By','X-LiteSpeed-Cache','X-LiteSpeed-Tag','X-Cache','CF-Cache-Status','Cache-Control','Age'):
            if r.headers.get(k): print(label,k+':',r.headers.get(k))
        return body
fetch_url('PLAIN HOME','https://gramiss.ir/')
fetch_url('QUERY HOME','https://gramiss.ir/?_enamad_diag=4',{'Cache-Control':'no-cache'})

print('--- CACHE DIAGNOSTIC ---')
try:
    data=call('list_files',{'dir':f'{PUBLIC}/wp-content/plugins','types':'dir','limit':'500'})
    items=data if isinstance(data,list) else (data.get('files',[]) if isinstance(data,dict) else [])
    names=[]
    for item in items:
        if isinstance(item,dict): names.append(str(item.get('file') or item.get('name') or item.get('filename') or ''))
        else: names.append(str(item))
    print('PLUGIN DIRS:', ', '.join(sorted(n for n in names if n)))
except Exception as e: print('PLUGIN LIST ERROR:',e)
try:
    ht=read_abs(PUBLIC,'.htaccess')
    lines=[ln for ln in ht.splitlines() if re.search(r'cache|litespeed|rocket|w3|supercache',ln,re.I)]
    print('HTACCESS CACHE LINES:')
    for ln in lines[:120]: print(ln)
except Exception as e: print('HTACCESS ERROR:',e)
try:
    wc=read_abs(PUBLIC,'wp-config.php')
    m=re.search(r"define\s*\(\s*['\"]WP_CACHE['\"]\s*,\s*(true|false)",wc,re.I)
    print('WP_CACHE:', m.group(1).lower() if m else 'not-defined')
except Exception as e: print('WP-CONFIG ERROR:',e)
try:
    data=call('list_files',{'dir':f'{PUBLIC}/wp-content','types':'dir','limit':'500'})
    items=data if isinstance(data,list) else (data.get('files',[]) if isinstance(data,dict) else [])
    names=[]
    for item in items:
        if isinstance(item,dict): names.append(str(item.get('file') or item.get('name') or item.get('filename') or ''))
        else: names.append(str(item))
    print('WP-CONTENT DIRS:', ', '.join(sorted(n for n in names if n)))
except Exception as e: print('WP-CONTENT LIST ERROR:',e)
