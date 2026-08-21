import json, os, ssl, time, urllib.parse, urllib.request
HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']; ROOT=os.environ['THEME_ROOT'].strip('/'); CTX=ssl._create_unverified_context(); PUBLIC='public_html'
ENAMAD_TOKEN='trustseal.enamad.ir/?id=7094948'

def call(func, params, post=False):
    url=f'https://{HOST}:2083/execute/Fileman/{func}'
    data=urllib.parse.urlencode(params).encode()
    req=urllib.request.Request(url if post else url+'?'+data.decode(),data=data if post else None,method='POST' if post else 'GET')
    req.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
    if post: req.add_header('Content-Type','application/x-www-form-urlencoded')
    with urllib.request.urlopen(req,context=CTX,timeout=60) as r: p=json.loads(r.read().decode())
    result=p.get('result') if isinstance(p.get('result'),dict) else p
    if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
    return result.get('data')

def read_file(directory,name):
    d=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str): return d[k]
    return d if isinstance(d,str) else ''

def save_file(directory,name,content):
    call('save_file_content',{'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

footer=read_file(ROOT,'footer.php')
if ENAMAD_TOKEN not in footer or 'class="footer-trust"' not in footer:
    raise SystemExit('Live footer no longer contains the eNAMAD block; refusing cache-only operation')
print('PASS: live footer contains eNAMAD block before purge')

stamp=str(int(time.time()))
filename=f'gramiss-lscache-purge-{stamp}.php'
php="""<?php
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('X-LiteSpeed-Purge: public,*');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
if (function_exists('do_action')) {
    do_action('litespeed_purge_all');
    do_action('litespeed_purge_front');
}
echo 'GRAMISS_LSCACHE_PURGED';
@unlink(__FILE__);
"""
save_file(PUBLIC,filename,php)
print('Temporary purge endpoint created:', filename)
url=f'https://gramiss.ir/{filename}?t={stamp}'
req=urllib.request.Request(url,headers={'Cache-Control':'no-cache','Pragma':'no-cache','User-Agent':'Mozilla/5.0 GramissCachePurge/2.1'})
with urllib.request.urlopen(req,context=CTX,timeout=60) as r:
    body=r.read().decode('utf-8','replace')
    print('Purge endpoint HTTP:',r.status)
    print('Purge response X-LiteSpeed-Purge:',r.headers.get('X-LiteSpeed-Purge'))
    if 'GRAMISS_LSCACHE_PURGED' not in body: raise SystemExit('Purge endpoint did not confirm execution')
print('PASS: LiteSpeed purge endpoint executed and self-deleted')
time.sleep(3)

def fetch_home(label):
    req=urllib.request.Request('https://gramiss.ir/',headers={'User-Agent':'Mozilla/5.0 GramissCacheVerify/2.1'})
    with urllib.request.urlopen(req,context=CTX,timeout=60) as r:
        body=r.read().decode('utf-8','replace')
        state=r.headers.get('X-LiteSpeed-Cache')
        ok=ENAMAD_TOKEN in body and 'class="footer-trust"' in body
        print(label,'HTTP:',r.status,'X-LiteSpeed-Cache:',state,'eNAMAD:',ok)
        if r.status!=200 or not ok: raise SystemExit(label+' still serves stale homepage HTML')
        return state
state1=fetch_home('PLAIN HOME #1')
time.sleep(2)
state2=fetch_home('PLAIN HOME #2')
print('SUCCESS: LITESPEED PURGED; PLAIN HOME NOW SERVES eNAMAD ON BOTH CHECKS',state1,state2)
