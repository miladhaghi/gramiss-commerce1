#!/usr/bin/env python3
import hashlib
import html
import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request

HOST = os.environ['CPANEL_HOST']
USER = os.environ['CPANEL_USER']
TOKEN = os.environ['CPANEL_TOKEN']
CTX = ssl._create_unverified_context()
BASE = 'https://gramiss.ir'
ROOT = 'public_html/wp-content/themes/gramiss-theme-next'
HEADER_EXPECTED_SHA = '94456594e7f2699b677e9c4193c0626a67e5fdce573aa74180cbd00d1539f66f'
PRODUCT_SHA = '70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'
PCAT_SHA = '75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'
PROTECTED = {
    'front-page.php': '0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
    'template-parts/home-looks.php': '3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
    'assets/css/home-looks.css': '98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
    'assets/js/home-looks.js': '6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}
CHROME = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36'


def api(fn, params, post=False):
    url = f'https://{HOST}:2083/execute/Fileman/{fn}'
    enc = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url if post else url + '?' + enc.decode(), data=enc if post else None, method='POST' if post else 'GET')
    req.add_header('Authorization', f'cpanel {USER}:{TOKEN}')
    if post:
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
        payload = json.loads(r.read().decode('utf-8', 'replace'))
    result = payload.get('result') if isinstance(payload.get('result'), dict) else payload
    if not isinstance(result, dict) or result.get('status') != 1:
        raise RuntimeError(str(result))
    return result.get('data')


def extract(data):
    if isinstance(data, str): return data
    if isinstance(data, dict):
        for k in ('content','file_content','data'):
            if isinstance(data.get(k), str): return data[k]
    return ''


def read_theme(rel):
    d, n = rel.rsplit('/',1) if '/' in rel else ('', rel)
    return extract(api('get_file_content', {'dir': ROOT if not d else ROOT+'/'+d, 'file': n, 'from_charset':'_DETECT_', 'to_charset':'utf-8'}))


def save_root(name, content):
    return api('save_file_content', {'dir':'public_html','file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'}, True)


def safe_url(url):
    p=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))


def get(url, headers=None, timeout=180):
    req=urllib.request.Request(safe_url(url), headers=headers or {'User-Agent':CHROME})
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8','replace'), {k.lower():v for k,v in r.headers.items()}


def sitemap(path):
    status,text,_=get(BASE+'/'+path+'?perf-purge-check='+str(int(time.time())), {'User-Agent':'GramissPerfPurge/1.0','Cache-Control':'no-cache'})
    urls=sorted(html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>', text, re.I))
    return status,len(urls),hashlib.sha256('\n'.join(urls).encode()).hexdigest()


def safety():
    errs=[]
    if hashlib.sha256(read_theme('header.php').encode()).hexdigest()!=HEADER_EXPECTED_SHA:
        errs.append('header SHA mismatch')
    for p,sha in PROTECTED.items():
        if hashlib.sha256(read_theme(p).encode()).hexdigest()!=sha:
            errs.append('protected drift '+p)
    ps,pc,ph=sitemap('product-sitemap.xml')
    cs,cc,ch=sitemap('product_cat-sitemap.xml')
    if ps!=200 or pc!=47 or ph!=PRODUCT_SHA: errs.append('product sitemap drift')
    if cs!=200 or cc!=20 or ch!=PCAT_SHA: errs.append('category sitemap drift')
    return errs


def inspect_archive(label):
    status,body,h=get(BASE+'/product-category/tshirt/', {'User-Agent':CHROME})
    full=len(re.findall(r'attachment-full|size-full',body,re.I))
    card=len(re.findall(r'attachment-gramiss-product-card|size-gramiss-product-card',body,re.I))
    print('ARCHIVE_STATE', {'label':label,'status':status,'full_tokens':full,'card_tokens':card,'x_litespeed_cache':h.get('x-litespeed-cache',''),'html_bytes':len(body.encode())})
    return status,full,card,h.get('x-litespeed-cache','')


pre=safety()
if pre:
    raise SystemExit('REFUSE preflight: '+'; '.join(pre))

before=inspect_archive('before-purge')
if before[0]!=200:
    raise SystemExit('REFUSE archive not 200')

helper='gramiss-performance-litespeed-purge-'+str(int(time.time()))+'.php'
php="""<?php
header('Content-Type: text/plain; charset=utf-8');
require __DIR__ . '/wp-load.php';
if ( has_action( 'litespeed_purge_all' ) ) { do_action( 'litespeed_purge_all' ); }
if ( function_exists( 'wp_cache_flush' ) ) { wp_cache_flush(); }
if ( function_exists( 'opcache_reset' ) ) { @opcache_reset(); }
@unlink(__FILE__);
echo 'PURGED';
?>"""
save_root(helper, php)
status,body,_=get(BASE+'/'+helper+'?t='+str(int(time.time())), {'User-Agent':'GramissPerfPurge/1.0','Cache-Control':'no-cache'})
if status!=200 or body.strip()!='PURGED':
    raise SystemExit('FAIL purge helper')

time.sleep(2)
first=inspect_archive('first-after-purge')
time.sleep(1)
second=inspect_archive('second-after-purge')

errs=[]
for label,state in [('first',first),('second',second)]:
    if state[0]!=200: errs.append(label+' not 200')
    if state[1]!=0: errs.append(label+' still full HTML')
    if state[2]<6: errs.append(label+' missing responsive card HTML')
post=safety()
errs.extend(post)
if errs:
    raise SystemExit('FAIL '+ '; '.join(errs))
print('PASS PERFORMANCE LITESPEED CACHE PURGE V1')
