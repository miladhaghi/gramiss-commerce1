import hashlib, json, os, ssl, time, urllib.parse, urllib.request
from pathlib import Path

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']
theme=os.environ['THEME_ROOT'].strip('/'); public='public_html'
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime())
rel='assets/css/product-mobile-v1-1.css'; version='20260827-2'
css=Path('deploy/pdp-mobile-v1/product-mobile-v1-1.css').read_text(encoding='utf-8')
marker='GRAMISS_PDP_MOBILE_UX_V1_1_REAL_RUNTIME'
if marker not in css: raise SystemExit('ABORT: candidate marker missing')
css_sha=hashlib.sha256(css.encode()).hexdigest(); print('CANDIDATE PATCH SHA',css_sha)

def call(func,params,post=False):
    url=f'https://{host}:2083/execute/Fileman/{func}'; enc=urllib.parse.urlencode(params).encode(); last=None
    for attempt in range(1,6):
        try:
            req=urllib.request.Request(url if post else url+'?'+enc.decode(),data=enc if post else None,method='POST' if post else 'GET')
            req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as r: payload=json.loads(r.read().decode('utf-8','replace'))
            result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
            if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last=exc; print(f'Attempt {attempt}/5 {func}: {exc}')
            if attempt<5: time.sleep(attempt*2)
    raise last

def read_at(root,relpath):
    parent,name=relpath.rsplit('/',1) if '/' in relpath else ('',relpath); directory=root if not parent else root+'/'+parent
    data=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for key in ('content','file_content','data'):
            if isinstance(data.get(key),str): return data[key]
    if isinstance(data,str): return data
    raise RuntimeError('Cannot read '+relpath)

def write_at(root,relpath,content):
    parent,name=relpath.rsplit('/',1) if '/' in relpath else ('',relpath); directory=root if not parent else root+'/'+parent
    call('save_file_content',{'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def public_get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 GramissPDPMobileHotfix/1','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req,context=ctx,timeout=90) as r: return r.status,r.read()

header=read_at(theme,'header.php'); original=header
start='<!-- GRAMISS PDP MOBILE UX V1 START -->'; end='<!-- GRAMISS PDP MOBILE UX V1 END -->'
if start not in header or end not in header: raise SystemExit('ABORT: existing mobile PDP loader block missing; nothing changed')
if 'product-mobile-v1.css?v=20260827-1' not in header or 'product-mobile-v1.js?v=20260827-1' not in header:
    raise SystemExit('ABORT: V1 loader baseline differs; nothing changed')
link=f'<link id="gramiss-pdp-mobile-v1-1-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . \'/assets/css/product-mobile-v1-1.css?v={version}\' ); ?>">'
import re
pattern=r'<link id="gramiss-pdp-mobile-v1-1-css"[^>]*>'
if re.search(pattern,header): header_new=re.sub(pattern,link,header,count=1)
else: header_new=header.replace(end,link+'\n'+end,1)

write_at(theme,'header.php.bak-pdp-mobile-v1-1-'+stamp,original); print('BACKUP header.php.bak-pdp-mobile-v1-1-'+stamp)
try:
    old=read_at(theme,rel); write_at(theme,rel+'.bak-'+stamp,old); print('BACKUP '+rel+'.bak-'+stamp)
except Exception: pass
write_at(theme,rel,css); write_at(theme,'header.php',header_new)

def rollback(reason):
    write_at(theme,'header.php',original)
    raise SystemExit('ROLLED BACK HEADER: '+reason)

live_header=read_at(theme,'header.php'); live_css=read_at(theme,rel)
checks={
 'patch link once':live_header.count('gramiss-pdp-mobile-v1-1-css')==1,
 'patch version':f'product-mobile-v1-1.css?v={version}' in live_header,
 'v1 css preserved':'product-mobile-v1.css?v=20260827-1' in live_header,
 'v1 js preserved':'product-mobile-v1.js?v=20260827-1' in live_header,
 'patch exact':hashlib.sha256(live_css.encode()).hexdigest()==css_sha,
 'patch marker':marker in live_css,
 'mobile guarded':'@media (max-width: 760px)' in live_css,
}
for label,ok in checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(checks.values()): rollback('live file verification failed')

purge='gramiss-purge-pdp-mobile-v11-'+stamp+'.php'
purge_php="<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
write_at(public,purge,purge_php)
st,b=public_get('https://gramiss.ir/'+purge+'?t='+str(int(time.time()))); print('PURGE',st,b.decode('utf-8','replace')[:30])

nonce=str(int(time.time())); st,b=public_get('https://gramiss.ir/?p=392&g1_pdp_mobile_v11='+nonce); html=b.decode('utf-8','replace')
public_checks={
 'product 200':st==200,
 'v1 css ref':'product-mobile-v1.css?v=20260827-1' in html,
 'v1 js ref':'product-mobile-v1.js?v=20260827-1' in html,
 'v1.1 patch ref':f'product-mobile-v1-1.css?v={version}' in html,
 'woo variation form':'variations_form' in html,
 'premium runtime asset':'product-runtime-premium' in html,
}
for label,ok in public_checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(public_checks.values()): rollback('public PDP verification failed')

st,b=public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/'+rel+'?v='+nonce); got=hashlib.sha256(b).hexdigest(); ok=st==200 and marker.encode() in b and got==css_sha
print(('PASS' if ok else 'FAIL')+': public patch bytes='+str(len(b))+' sha='+got)
if not ok: rollback('public patch verification failed')

st,b=public_get('https://gramiss.ir/?g1_home_safety_v11='+nonce); home=b.decode('utf-8','replace'); home_ok=st==200 and 'g1-floating-hero' in home and 'data-g1-looks' in home
print(('PASS' if home_ok else 'FAIL')+': Home/Looks untouched')
if not home_ok: rollback('Home safety verification failed')
print('LIVE PDP MOBILE UX V1.1 RUNTIME FIX DEPLOYED')
