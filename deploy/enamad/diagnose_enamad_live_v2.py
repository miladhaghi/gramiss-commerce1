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
if 'footer-trust' in footer:
    i=footer.index('footer-trust'); print('FOOTER CONTEXT:', footer[max(0,i-180):i+850])
req=urllib.request.Request('https://gramiss.ir/?_enamad_diag=2',headers={'Cache-Control':'no-cache','User-Agent':'GramissEnamadDiag/2.0'})
with urllib.request.urlopen(req,context=CTX,timeout=60) as r:
    html=r.read().decode('utf-8','replace'); print('HOME HTTP:',r.status)
print('SERVED wrapper:', 'class="footer-trust"' in html)
print('SERVED trustseal:', 'trustseal.enamad.ir/?id=7094948' in html)
if 'footer-trust' in html:
    i=html.index('footer-trust'); print('HTML CONTEXT:', html[max(0,i-180):i+900])
