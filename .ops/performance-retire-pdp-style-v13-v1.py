#!/usr/bin/env python3
import hashlib, json, os, re, ssl, time, urllib.parse, urllib.request

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']
ROOT='public_html/wp-content/themes/gramiss-theme-next'; BASE='https://gramiss.ir'
PDP='https://gramiss.ir/product/%d8%b4%d9%84%d9%88%d8%a7%d8%b1-%d8%ac%db%8c%d9%86-%d8%a8%d8%a7%d9%86%db%8c-%d8%aa%db%8c%d9%86%d8%aa-%d8%b3%d8%a8%d8%b2/'
# Correct canonical target; kept separate to avoid typo risk above.
PDP='https://gramiss.ir/product/%d8%b4%d9%84%d9%88%d8%a7%d8%b1-%d8%ac%db%8c%d9%86-%d8%a8%d8%a7%d9%84%d9%86%db%8c-%d8%aa%db%8c%d9%86%d8%aa-%d8%b3%d8%a8%d8%b2/'
CTX=ssl._create_unverified_context()
EXPECTED_HEADER='6018c0d5ae0b588dd5a6e8f99b53cef9ce075b9d51441e8df4f8c8a58d1b0686'
PROTECTED={
 'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
 'template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
 'assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
 'assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
OLD='''<script id="gramiss-pdp-mobile-v1-3-js" src="<?php echo esc_url( get_stylesheet_directory_uri() . '/assets/js/product-mobile-v1-3.js?v=20260827-3' ); ?>" defer></script>'''
NEW='''<!-- gramiss-pdp-mobile-v1-3-js retired: duplicate style-intelligence runtime; v1-3 CSS intentionally retained for v1-4 layering -->'''

def api(fn,params,post=False):
    url=f'https://{HOST}:2083/execute/Fileman/{fn}'; encoded=urllib.parse.urlencode(params).encode()
    req=urllib.request.Request(url if post else url+'?'+encoded.decode(),data=encoded if post else None,method='POST' if post else 'GET')
    req.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
    if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
    with urllib.request.urlopen(req,context=CTX,timeout=90) as r: payload=json.loads(r.read().decode('utf-8','replace'))
    result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
    if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
    return result.get('data')

def extract(d):
    if isinstance(d,str): return d
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str): return d[k]
    return ''
def read(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel)
    return extract(api('get_file_content',{'dir':ROOT+('/'+parent if parent else ''),'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'}))
def save(rel,text):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel)
    return api('save_file_content',{'dir':ROOT+('/'+parent if parent else ''),'file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def save_root(name,text): return api('save_file_content',{'dir':'public_html','file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def sha(text): return hashlib.sha256(text.encode()).hexdigest()
def safe_url(url):
    p=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def get(url):
    req=urllib.request.Request(safe_url(url),headers={'User-Agent':'GramissPerfStyleV13Retire/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req,context=CTX,timeout=180) as r:return r.status,r.read().decode('utf-8','replace')
def flush():
    n='gramiss-perf-flush-'+str(int(time.time()))+'.php'
    php="<?php require __DIR__.'/wp-load.php'; if(function_exists('wp_cache_flush'))wp_cache_flush(); if(function_exists('opcache_reset'))@opcache_reset(); @unlink(__FILE__); header('Content-Type:text/plain'); echo 'OK'; ?>"
    save_root(n,php); st,b=get(BASE+'/'+n+'?t='+str(time.time()))
    if st!=200 or b.strip()!='OK': raise RuntimeError('flush failed')

def main():
    header=read('header.php'); actual=sha(header); print('BEFORE_HEADER_SHA',actual)
    if actual!=EXPECTED_HEADER: raise SystemExit('REFUSE header drift '+actual)
    for p,x in PROTECTED.items():
        a=sha(read(p)); print('PROTECTED_BEFORE',p,a)
        if a!=x: raise SystemExit('REFUSE protected drift '+p)
    if header.count(OLD)!=1: raise SystemExit('REFUSE v1-3 loader match count '+str(header.count(OLD)))
    if header.count("product-mobile-v1-4.js?v=20260903-perf4")!=1: raise SystemExit('REFUSE v1-4 loader not singular')
    if header.count("product-mobile-v1-3.css?v=20260827-3")!=1: raise SystemExit('REFUSE v1-3 CSS not singular')
    new_header=header.replace(OLD,NEW,1)
    expected_after=sha(new_header)
    try:
        save('header.php',new_header); flush()
        stored=read('header.php'); print('AFTER_HEADER_SHA',sha(stored))
        errors=[]
        if sha(stored)!=expected_after: errors.append('stored header mismatch')
        for p,x in PROTECTED.items():
            if sha(read(p))!=x: errors.append('protected changed '+p)
        st,page=get(PDP+'?perf-style-v13-retire='+str(time.time()))
        if st!=200: errors.append('PDP HTTP '+str(st))
        if 'product-mobile-v1-3.js' in page: errors.append('v1-3 JS still rendered')
        if 'product-mobile-v1-3.css' not in page: errors.append('v1-3 CSS lost')
        if 'product-mobile-v1-4.js?v=20260903-perf4' not in page: errors.append('v1-4 JS missing')
        if page.count('id="gramiss-pdp-mobile-v1-4-js"')!=1: errors.append('v1-4 loader count wrong')
        if len(re.findall(r'<h1\b',page,re.I))!=1: errors.append('PDP H1 count changed')
        if 'g1-style-intelligence' not in read('assets/css/product-mobile-v1-4.css'): errors.append('v1-4 style CSS marker missing')
        print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False))
        if errors: raise RuntimeError('; '.join(errors))
    except Exception:
        save('header.php',header); flush()
        if sha(read('header.php'))!=sha(header): raise RuntimeError('rollback header mismatch')
        print('ROLLBACK DUPLICATE PDP STYLE V1-3 COMPLETE')
        raise
    print('PASS RETIRE DUPLICATE PDP STYLE V1-3')

if __name__=='__main__':main()
