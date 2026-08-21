import json, os, ssl, urllib.parse, urllib.request
HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']; ROOT=os.environ['THEME_ROOT'].strip('/'); CTX=ssl._create_unverified_context()

def call(func, params):
    url=f'https://{HOST}:2083/execute/Fileman/{func}?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={'Authorization':f'cpanel {USER}:{TOKEN}'})
    with urllib.request.urlopen(req,context=CTX,timeout=60) as r:
        p=json.loads(r.read().decode())
    result=p.get('result') if isinstance(p.get('result'),dict) else p
    if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
    return result.get('data')

def read_live(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=ROOT if not parent else f'{ROOT}/{parent}'
    d=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str): return d[k]
    return d if isinstance(d,str) else ''
footer=read_live('footer.php'); css=read_live('assets/css/theme.css')
print('LIVE footer trust wrapper:', 'class="footer-trust"' in footer)
print('LIVE trustseal href:', 'trustseal.enamad.ir/?id=7094948' in footer)
print('LIVE exact code token:', "code='xJ8HkTjjBF0ykbRRdp0yoXAzjUguqwgJ'" in footer)
print('LIVE theme marker:', 'GRAMISS_ENAMAD_FOOTER_V1' in css)

def fetch_url(label,url,headers=None):
    h={'User-Agent':'GramissEnamadDiag/3.0'}
    if headers: h.update(headers)
    req=urllib.request.Request(url,headers=h)
    with urllib.request.urlopen(req,context=CTX,timeout=60) as r:
        body=r.read().decode('utf-8','replace')
        print(label,'HTTP:',r.status)
        print(label,'cache-control:',r.headers.get('Cache-Control'))
        print(label,'age:',r.headers.get('Age'))
        print(label,'x-cache:',r.headers.get('X-Cache'))
        print(label,'cf-cache-status:',r.headers.get('CF-Cache-Status'))
        print(label,'wrapper:', 'class="footer-trust"' in body)
        print(label,'trustseal:', 'trustseal.enamad.ir/?id=7094948' in body)
        return body
fetch_url('PLAIN HOME','https://gramiss.ir/')
fetch_url('NO-CACHE HOME','https://gramiss.ir/',{'Cache-Control':'no-cache','Pragma':'no-cache'})
fetch_url('QUERY HOME','https://gramiss.ir/?_enamad_diag=3',{'Cache-Control':'no-cache'})
