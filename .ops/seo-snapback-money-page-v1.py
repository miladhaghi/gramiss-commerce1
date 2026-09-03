#!/usr/bin/env python3
import hashlib, html, json, os, re, ssl, time, urllib.error, urllib.parse, urllib.request

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']
BASE='https://gramiss.ir'; ROOT=os.environ['THEME_ROOT'].strip('/'); CTX=ssl._create_unverified_context()
PRODUCT_COUNT=49; PRODUCT_SHA='05e81da96bcc57927bf8d2b467866a1236e9ea0307e1c3902519136294e805bf'
PCAT_COUNT=21; PCAT_SHA='e56e71dfe5a97014bb645c3726b916c1883c87eb2e21b5eab8cc4598942c13bf'
PROTECTED={
 'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
 'template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
 'assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
 'assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}
TARGET_SLUG='snapback-cap'
EXPECTED_TITLE='خرید کلاه اسنپ‌بک مردانه | Gramiss'
EXPECTED_META='مدل‌های کلاه اسنپ‌بک مردانه Gramiss را ببینید و طرح‌های موجود این دسته را برای انتخاب بهتر بررسی و مقایسه کنید.'

def api(fn,params,post=False):
    url=f'https://{HOST}:2083/execute/Fileman/{fn}'; enc=urllib.parse.urlencode(params).encode(); last=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(url if post else url+'?'+enc.decode(),data=enc if post else None,method='POST' if post else 'GET')
            req.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=CTX,timeout=90) as r: payload=json.loads(r.read().decode('utf-8','replace'))
            result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
            if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last=exc; print('API_RETRY',fn,attempt+1,exc); time.sleep(attempt+1)
    raise last

def theme(rel):
    d,n=rel.rsplit('/',1) if '/' in rel else ('',rel)
    data=api('get_file_content',{'dir':ROOT if not d else ROOT+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for k in ('content','file_content','data'):
            if isinstance(data.get(k),str): return data[k]
    return data if isinstance(data,str) else ''

def save_root(name,text):
    return api('save_file_content',{'dir':'public_html','file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def safe_url(url):
    p=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))

def get(url,timeout=180):
    req=urllib.request.Request(safe_url(url),headers={'User-Agent':'GramissSnapbackMoneyPageV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    try:
        with urllib.request.urlopen(req,context=CTX,timeout=timeout) as r:return r.status,r.read().decode('utf-8','replace'),r.geturl()
    except urllib.error.HTTPError as e:return e.code,e.read().decode('utf-8','replace'),e.geturl()

def norm(url):
    return urllib.parse.unquote((url or '').split('?',1)[0]).rstrip('/')+'/' if url else ''

def attr(tag,name):
    m=re.search(r'\b'+re.escape(name)+r'\s*=\s*["\']([^"\']*)["\']',tag,re.I|re.S)
    return html.unescape(m.group(1)).strip() if m else ''

def strip_markup(value):
    value=re.sub(r'<script\b[^>]*>.*?</script>',' ',value or '',flags=re.I|re.S)
    value=re.sub(r'<style\b[^>]*>.*?</style>',' ',value,flags=re.I|re.S)
    value=re.sub(r'<[^>]+>',' ',value)
    return re.sub(r'\s+',' ',html.unescape(value)).strip()

def parse_head(text):
    head=text.split('</head>',1)[0]; title=''; desc=''; robots=''; canonical=''
    m=re.search(r'<title[^>]*>(.*?)</title>',head,re.I|re.S)
    if m:title=strip_markup(m.group(1))
    for tag in re.findall(r'<meta\b[^>]*>',head,re.I|re.S):
        n=attr(tag,'name').lower()
        if n=='description':desc=attr(tag,'content')
        elif n=='robots':robots=attr(tag,'content')
    for tag in re.findall(r'<link\b[^>]*>',head,re.I|re.S):
        if 'canonical' in attr(tag,'rel').lower().split():canonical=attr(tag,'href');break
    return title,desc,robots,canonical

def sitemap(path):
    st,xml,_=get(BASE+'/'+path+'?v='+str(int(time.time()*1000)),150)
    urls=sorted(html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>',xml,re.I))
    return st,urls,hashlib.sha256('\n'.join(urls).encode()).hexdigest()

def safety(label):
    errors=[]; hashes={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED}
    for p,h in PROTECTED.items():
        if hashes[p]!=h:errors.append('protected drift '+p)
    ps,pu,ph=sitemap('product-sitemap.xml'); cs,cu,ch=sitemap('product_cat-sitemap.xml')
    if ps!=200 or len(pu)!=PRODUCT_COUNT or ph!=PRODUCT_SHA:errors.append('product sitemap drift')
    if cs!=200 or len(cu)!=PCAT_COUNT or ch!=PCAT_SHA:errors.append('product_cat sitemap drift')
    print('SAFETY',label,json.dumps({'protected':hashes,'product':[ps,len(pu),ph],'product_cat':[cs,len(cu),ch],'errors':errors},ensure_ascii=False,sort_keys=True))
    if errors:raise RuntimeError('; '.join(errors))

def run_php(label,body):
    name='gramiss-snapback-'+label+'-'+hashlib.sha256((str(time.time())+label).encode()).hexdigest()[:12]+'.php'
    save_root(name,body)
    st,text,_=get(BASE+'/'+name+'?t='+str(int(time.time()*1000)),240)
    if st!=200:raise RuntimeError(label+' HTTP '+str(st))
    return json.loads(text)

def state():
    php=r'''<?php
header('Content-Type: application/json; charset=utf-8'); define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; @unlink(__FILE__);
$t=get_term_by('slug','snapback-cap','product_cat'); if(!$t){http_response_code(404); echo '{}'; exit;}
$u=get_term_link($t); echo wp_json_encode(['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'description'=>$t->description,'url'=>is_wp_error($u)?'':$u,'title'=>(string)get_term_meta($t->term_id,'rank_math_title',true),'meta'=>(string)get_term_meta($t->term_id,'rank_math_description',true),'robots'=>get_term_meta($t->term_id,'rank_math_robots',true)],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES); ?>'''
    return run_php('state',php)

def mutate(old_description,rollback=False):
    if rollback:
        encoded=json.dumps(old_description,ensure_ascii=False)
        php="""<?php
header('Content-Type: application/json; charset=utf-8'); define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; @unlink(__FILE__);
$t=get_term_by('slug','snapback-cap','product_cat'); if(!$t){http_response_code(404); echo '{}'; exit;}
$desc=%s; $r=wp_update_term($t->term_id,'product_cat',['description'=>$desc]); if(is_wp_error($r)){http_response_code(500); echo wp_json_encode(['error'=>$r->get_error_message()]); exit;} clean_term_cache($t->term_id,'product_cat'); if(function_exists('wp_cache_flush'))wp_cache_flush(); if(has_action('litespeed_purge_all'))do_action('litespeed_purge_all'); echo wp_json_encode(['rolled_back'=>true,'id'=>(int)$t->term_id],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES); ?>""" % encoded
        return run_php('rollback',php)
    php=r'''<?php
header('Content-Type: application/json; charset=utf-8'); define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; @unlink(__FILE__);
$t=get_term_by('slug','snapback-cap','product_cat'); if(!$t){http_response_code(404); echo '{}'; exit;}
$hat=get_term_by('slug','hat','product_cat'); $fit=get_term_by('slug','fitted-cap','product_cat');
$hat_url=$hat?get_term_link($hat):''; $fit_url=$fit?get_term_link($fit):'';
$desc='<h2>خرید کلاه اسنپ‌بک مردانه؛ انتخاب مدل و جزئیات مناسب</h2><p>در دسته کلاه اسنپ‌بک مردانه Gramiss می‌توانید مدل‌های موجود را کنار هم ببینید و بر اساس فرم کلی کلاه، رنگ و جزئیاتی که در صفحه هر محصول درج شده مقایسه کنید. برای انتخاب دقیق‌تر، تصاویر محصول و مشخصات همان مدل را بررسی کنید و تصمیم را بر اساس اطلاعات واقعی هر کالا بگیرید.</p><p>اگر می‌خواهید مدل‌های بیشتری از این گروه را مقایسه کنید، <a href="'.esc_url($hat_url).'">دسته کلاه مردانه</a> را ببینید. برای مقایسه فرم متفاوت کلاه نیز می‌توانید مدل‌های <a href="'.esc_url($fit_url).'">فیت کپ مردانه</a> را بررسی کنید. این تفکیک کمک می‌کند بدون ترکیب‌کردن مدل‌ها، گزینه‌ای را انتخاب کنید که از نظر فرم و استایل به انتخاب شما نزدیک‌تر است.</p>';
$r=wp_update_term($t->term_id,'product_cat',['description'=>$desc]); if(is_wp_error($r)){http_response_code(500); echo wp_json_encode(['error'=>$r->get_error_message()]); exit;}
clean_term_cache($t->term_id,'product_cat'); if(function_exists('wp_cache_flush'))wp_cache_flush(); if(has_action('litespeed_purge_all'))do_action('litespeed_purge_all');
echo wp_json_encode(['updated'=>true,'id'=>(int)$t->term_id,'description'=>$desc],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES); ?>'''
    return run_php('mutate',php)

def verify(expected_description,url):
    errors=[]; st,text,final=get(url+'?snapbackqa='+str(int(time.time()*1000)),180); title,desc,robots,canon=parse_head(text)
    h1s=[strip_markup(x) for x in re.findall(r'<h1\b[^>]*>(.*?)</h1>',text,re.I|re.S)]
    plain=strip_markup(expected_description); sample=plain[:90]
    if st!=200:errors.append('HTTP '+str(st))
    if title!=EXPECTED_TITLE:errors.append('title drift: '+title)
    if desc!=EXPECTED_META:errors.append('meta drift: '+desc)
    if 'noindex' in robots.lower() or 'index' not in robots.lower():errors.append('robots '+robots)
    if norm(canon)!=norm(url):errors.append('canonical '+canon)
    if len(h1s)!=1:errors.append('H1 count '+str(len(h1s)))
    if sample not in strip_markup(text):errors.append('description not rendered')
    if len(plain)<120:errors.append('description thin')
    if norm(final)!=norm(url):errors.append('final URL drift '+final)
    if norm('/product-category/hat/') not in norm('/product-category/hat/'):pass
    print('PUBLIC_VERIFY',json.dumps({'http':st,'final':final,'title':title,'meta':desc,'robots':robots,'canonical':canon,'h1':h1s,'description_chars':len(plain),'sample_rendered':sample in strip_markup(text),'errors':errors},ensure_ascii=False))
    if errors:raise RuntimeError('; '.join(errors))

safety('before')
before=state(); print('TERM_BEFORE',json.dumps(before,ensure_ascii=False))
if before.get('id')!=44:raise SystemExit('REFUSE unexpected snapback term id '+str(before.get('id')))
if before.get('count',0)<1:raise SystemExit('REFUSE empty snapback inventory')
if before.get('title')!=EXPECTED_TITLE or before.get('meta')!=EXPECTED_META:raise SystemExit('REFUSE metadata drift')
if strip_markup(before.get('description','')):raise SystemExit('REFUSE description is no longer empty')
old=before.get('description','')
try:
    changed=mutate(old,False); print('MUTATION',json.dumps(changed,ensure_ascii=False))
    after=state(); print('TERM_AFTER',json.dumps(after,ensure_ascii=False))
    if not strip_markup(after.get('description','')):raise RuntimeError('description remained empty')
    verify(after['description'],after['url'])
    safety('after')
except Exception:
    print('VERIFY_FAILED_ROLLING_BACK')
    try:
        print('ROLLBACK',json.dumps(mutate(old,True),ensure_ascii=False)); safety('rollback')
    finally:
        raise
print('PASS SNAPBACK MONEY PAGE V1')
