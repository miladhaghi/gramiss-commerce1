import hashlib, json, os, re, ssl, subprocess, time, urllib.parse, urllib.request
from pathlib import Path

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']; theme=os.environ['THEME_ROOT'].strip('/'); public='public_html'
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime()); version='20260827-4'
css_rel='assets/css/product-mobile-v1-4.css'; js_rel='assets/js/product-mobile-v1-4.js'
css_path=Path('deploy/pdp-mobile-v1/product-mobile-v1-4.css'); js_path=Path('deploy/pdp-mobile-v1/product-mobile-v1-4.js')
css=css_path.read_text(encoding='utf-8'); js=js_path.read_text(encoding='utf-8')
if 'GRAMISS_PDP_MOBILE_STYLE_INTELLIGENCE_V1_4' not in css or 'GRAMISS_PDP_MOBILE_STYLE_INTELLIGENCE_V1_4' not in js: raise SystemExit('ABORT: V1.4 markers missing')
subprocess.run(['node','--check',str(js_path)],check=True)
css_sha=hashlib.sha256(css.encode()).hexdigest(); js_sha=hashlib.sha256(js.encode()).hexdigest(); print('CANDIDATE CSS',len(css.encode()),css_sha); print('CANDIDATE JS',len(js.encode()),js_sha)

def call(func,params,post=False):
    url=f'https://{host}:2083/execute/Fileman/{func}'; enc=urllib.parse.urlencode(params).encode(); last=None
    for attempt in range(1,6):
        try:
            req=urllib.request.Request(url if post else url+'?'+enc.decode(),data=enc if post else None,method='POST' if post else 'GET'); req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as r: payload=json.loads(r.read().decode('utf-8','replace'))
            result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
            if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last=exc; print(f'Attempt {attempt}/5 {func}: {exc}'); time.sleep(attempt*2 if attempt<5 else 0)
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
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 GramissStyleLogic/1.4','Cache-Control':'no-cache','Pragma':'no-cache','Accept':'*/*'})
    with urllib.request.urlopen(req,context=ctx,timeout=90) as r:return r.status,r.read()

header=read_at(theme,'header.php'); original=header; end='<!-- GRAMISS PDP MOBILE UX V1 END -->'
if end not in header: raise SystemExit('ABORT: PDP mobile loader end marker missing')
for needle in ('product-mobile-v1.css?v=20260827-1','product-mobile-v1.js?v=20260827-1','product-mobile-v1-1.css','product-mobile-v1-2.css','product-mobile-v1-2.js','product-mobile-v1-3.css','product-mobile-v1-3.js'):
    if needle not in header: raise SystemExit('ABORT: live PDP mobile baseline differs: '+needle)
css_link=f'<link id="gramiss-pdp-mobile-v1-4-css" rel="stylesheet" href="<?php echo esc_url( get_stylesheet_directory_uri() . \'/{css_rel}?v={version}\' ); ?>">'
js_link=f'<script id="gramiss-pdp-mobile-v1-4-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . \'/{js_rel}?v={version}\' ); ?>" defer></script>'
for ident,markup in [('gramiss-pdp-mobile-v1-4-css',css_link),('gramiss-pdp-mobile-v1-4-js',js_link)]:
    pattern=rf'<(?:link|script) id="{ident}"[^>]*>(?:</script>)?'
    if re.search(pattern,header): header=re.sub(pattern,markup,header,count=1)
    else: header=header.replace(end,markup+'\n'+end,1)

write_at(theme,'header.php.bak-pdp-mobile-v1-4-'+stamp,original); print('BACKUP header.php.bak-pdp-mobile-v1-4-'+stamp)
for rel in (css_rel,js_rel):
    try: old=read_at(theme,rel); write_at(theme,rel+'.bak-'+stamp,old); print('BACKUP '+rel+'.bak-'+stamp)
    except Exception: pass
write_at(theme,css_rel,css); write_at(theme,js_rel,js); write_at(theme,'header.php',header)

def rollback(reason):
    write_at(theme,'header.php',original); raise SystemExit('ROLLED BACK HEADER: '+reason)

live_h=read_at(theme,'header.php'); live_css=read_at(theme,css_rel); live_js=read_at(theme,js_rel)
checks={'v1.4 css once':live_h.count('gramiss-pdp-mobile-v1-4-css')==1,'v1.4 js once':live_h.count('gramiss-pdp-mobile-v1-4-js')==1,'v1.4 css version':f'{css_rel}?v={version}' in live_h,'v1.4 js version':f'{js_rel}?v={version}' in live_h,'css exact':hashlib.sha256(live_css.encode()).hexdigest()==css_sha,'js exact':hashlib.sha256(live_js.encode()).hexdigest()==js_sha,'mobile guarded':'@media (max-width: 760px)' in live_css,'curated module':'curatedByProduct' in live_js and 'calc(100vw - 74px)' in live_css}
for label,ok in checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(checks.values()): rollback('live file verification failed')

purge='gramiss-purge-pdp-style-v14-'+stamp+'.php'; purge_php="<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
write_at(public,purge,purge_php); st,b=public_get('https://gramiss.ir/'+purge+'?t='+str(int(time.time()))); print('PURGE',st,b.decode('utf-8','replace')[:30])
nonce=str(int(time.time())); st,b=public_get('https://gramiss.ir/?p=392&g1_pdp_style_v14='+nonce); html=b.decode('utf-8','replace')
public_checks={'product 200':st==200,'v1.4 css ref':f'{css_rel}?v={version}' in html,'v1.4 js ref':f'{js_rel}?v={version}' in html,'v1.3 preserved':'product-mobile-v1-3.css' in html and 'product-mobile-v1-3.js' in html,'woo related section':'related products' in html.lower() or 'related products' in html,'woo variation form':'variations_form' in html}
for label,ok in public_checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(public_checks.values()): rollback('public PDP verification failed')
for rel,sha,marker in ((css_rel,css_sha,b'GRAMISS_PDP_MOBILE_STYLE_INTELLIGENCE_V1_4'),(js_rel,js_sha,b'GRAMISS_PDP_MOBILE_STYLE_INTELLIGENCE_V1_4')):
    st,b=public_get('https://gramiss.ir/wp-content/themes/gramiss-theme-next/'+rel+'?v='+nonce); got=hashlib.sha256(b).hexdigest(); ok=st==200 and got==sha and marker in b; print(('PASS' if ok else 'FAIL')+': public '+rel+' bytes='+str(len(b))+' sha='+got)
    if not ok: rollback('public asset verification failed '+rel)
for pid in (284,435,366,403):
    try:
        st,b=public_get(f'https://gramiss.ir/wp-json/wc/store/v1/products/{pid}'); obj=json.loads(b.decode('utf-8','replace')) if st==200 else {}; print('CURATED',pid,st,obj.get('name','?'))
    except Exception as exc: print('CURATED optional',pid,exc)
st,b=public_get('https://gramiss.ir/?g1_home_safety_style_v14='+nonce); home=b.decode('utf-8','replace'); home_ok=st==200 and 'g1-floating-hero' in home and 'data-g1-looks' in home; print(('PASS' if home_ok else 'FAIL')+': Home/Looks untouched')
if not home_ok: rollback('Home safety verification failed')
print('LIVE PDP MOBILE STYLE INTELLIGENCE V1.4 DEPLOYED')
