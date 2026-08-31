import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']
root=os.environ['THEME_ROOT'].strip('/'); healthy=os.environ.get('HEALTHY_HOME_SHA','')
ctx=ssl._create_unverified_context(); BASE='https://gramiss.ir'
EXPECTED_PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'
EXPECTED_IDS=[453,459,460,463,464,467,468,471,472]
EXPECTED_CATEGORY_COUNTS={'fit-size-guide':3,'fabric-care':2,'style-guide':2,'buying-guide':2}
EXPECTED_TITLES={
453:'تیشرت باکسی چیست و چه تفاوتی با اورسایز دارد؟',
459:'راهنمای انتخاب سایز تیشرت باکسی مردانه؛ اندازه‌گیری و فیت مناسب',
460:'تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ کدام فیت مناسب شماست؟',
463:'پارچه لینن چیست؟ راهنمای شناخت، چروک و انتخاب لباس لینن',
464:'شست‌وشوی پیراهن لینن مردانه؛ راهنمای خشک‌کردن و اتوکشی',
467:'استایل با پیراهن لینن مردانه؛ شلوار، کفش و ترکیب رنگ',
468:'با شلوار بگ مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و قد شلوار',
471:'راهنمای خرید تیشرت مردانه؛ فیت، اندازه، پارچه، دوخت و چاپ',
472:'راهنمای خرید شلوار جین مردانه؛ فیت، قد، پارچه و جزئیات',
}

def call(fn,p,post=False):
    u=f'https://{host}:2083/execute/Fileman/{fn}'; d=urllib.parse.urlencode(p).encode(); last=None
    for attempt in range(1,5):
        try:
            req=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET')
            req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
            q=o.get('result') if isinstance(o.get('result'),dict) else o
            if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
            return q.get('data')
        except Exception as exc:
            last=exc; print('API_RETRY',fn,attempt,exc)
            if attempt<4:time.sleep(attempt*2)
    raise last

def read_theme(rel):
    p,n=rel.rsplit('/',1) if '/' in rel else ('',rel)
    d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(d,dict):
        for k in ('content','file_content','data'):
            if isinstance(d.get(k),str):return d[k]
    return d if isinstance(d,str) else ''

def save_public(n,c):
    return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def get(u,timeout=180):
    req=urllib.request.Request(u,headers={'User-Agent':'GramissEditorialFoundationAuditV2/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    try:
        with urllib.request.urlopen(req,context=ctx,timeout=timeout) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
    except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)

def hv(t,p):
    m=re.search(p,t,re.I|re.S); return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''

def head(raw):
    t=raw.decode('utf-8','replace').split('</head>',1)[0]
    return {
      'title':hv(t,r'<title[^>]*>(.*?)</title>'),
      'description':hv(t,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),
      'canonical':hv(t,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),
      'robots':hv(t,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')
    }

def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sitemap(path):
    s,r,_,_=get(BASE+'/'+path+'?t='+str(int(time.time())),120)
    return s,[x.replace('&amp;','&') for x in re.findall(r'<loc>(.*?)</loc>',r.decode('utf-8','replace'),re.I)]

protected={
'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
'template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
'assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
'assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2',
}
errors=[]
hashes={f:hashlib.sha256(read_theme(f).encode()).hexdigest() for f in protected}
print('PROTECTED',json.dumps(hashes,ensure_ascii=False,sort_keys=True))
for f,sha in protected.items():
    if hashes.get(f)!=sha:errors.append('protected hash mismatch '+f)
if healthy and hashes['front-page.php']!=healthy:errors.append('healthy home sha mismatch')
for f,m in [('home.php','g1-editorial-index'),('single.php','g1-editorial-single'),('category.php','g1-editorial-category'),('assets/css/editorial-v1.css','GRAMISS_EDITORIAL_V1')]:
    if m not in read_theme(f):errors.append('editorial foundation marker missing '+f)

nonce=hashlib.sha256((str(time.time())+hashes['front-page.php']).encode()).hexdigest()[:14]
probe='gramiss-editorial-foundation-audit-v2-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$ids=[453,459,460,463,464,467,468,471,472];$posts=[];
foreach($ids as $id){$p=get_post($id);$posts[]=$p?['id'=>(int)$p->ID,'status'=>$p->post_status,'title'=>$p->post_title,'url'=>get_permalink($p),'cats'=>wp_get_post_categories($p->ID,['fields'=>'slugs']),'focus'=>get_post_meta($p->ID,'rank_math_focus_keyword',true)]:['id'=>$id,'missing'=>true];}
$cats=[];foreach(['fit-size-guide','fabric-care','style-guide','buying-guide'] as $slug){$t=get_term_by('slug',$slug,'category');$cats[$slug]=$t?['id'=>(int)$t->term_id,'count'=>(int)$t->count,'url'=>get_term_link($t)]:null;}
$blog=get_post(22);
echo wp_json_encode(['published'=>(int)wp_count_posts('post')->publish,'posts'=>$posts,'categories'=>$cats,'blog'=>$blog?['id'=>(int)$blog->ID,'title'=>$blog->post_title,'url'=>get_permalink($blog)]:null],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save_public(probe,php)
s,raw,_,_=get(BASE+'/'+probe+'?t='+str(int(time.time())),180)
print('WP_STATE',s,raw.decode('utf-8','replace'))
if s!=200:
    errors.append('wp state probe failed')
    state={}
else:
    try:state=json.loads(raw.decode('utf-8','replace'))
    except Exception as exc:errors.append('wp state json failed '+str(exc));state={}
if state.get('published')!=9:errors.append('published post count != 9')
if not state.get('blog') or state['blog'].get('title')!='مجله Gramiss':errors.append('blog page drift')
rows={int(p.get('id',0)):p for p in state.get('posts',[])}
for pid in EXPECTED_IDS:
    p=rows.get(pid)
    if not p or p.get('missing'):errors.append('missing post '+str(pid));continue
    if p.get('status')!='publish':errors.append('post not publish '+str(pid))
    if p.get('title')!=EXPECTED_TITLES[pid]:errors.append('title drift '+str(pid))
    if not p.get('url'):errors.append('url missing '+str(pid))
for slug,count in EXPECTED_CATEGORY_COUNTS.items():
    c=(state.get('categories') or {}).get(slug)
    if not c:errors.append('missing editorial category '+slug);continue
    if c.get('count')!=count:errors.append('category count drift '+slug)

live_urls={pid:rows[pid]['url'] for pid in EXPECTED_IDS if pid in rows and rows[pid].get('url')}
all_article_norm={norm(u) for u in live_urls.values()}
for pid,u in live_urls.items():
    st,r,final,_=get(u+'?t='+str(int(time.time())),150);h=head(r);body=r.decode('utf-8','replace');internal=[]
    for href in re.findall(r'<a\b[^>]*href=["\']([^"\']+)',body,re.I):
        if href.startswith(BASE):internal.append(norm(href))
    article_links=sorted(set(x for x in internal if x in all_article_norm and x!=norm(u)))
    print('ARTICLE',pid,st,final,json.dumps(h,ensure_ascii=False,separators=(',',':')),'H2',body.count('<h2>'),'BLOGPOSTING',('BlogPosting' in body),'ARTICLE_LINKS',len(article_links))
    if st!=200:errors.append('article http '+str(pid));continue
    if EXPECTED_TITLES[pid] not in body:errors.append('live title missing '+str(pid))
    if 'g1-editorial-single' not in body:errors.append('single template marker missing '+str(pid))
    if norm(h.get('canonical',''))!=norm(u):errors.append('canonical mismatch '+str(pid))
    rob=h.get('robots','').lower()
    if 'noindex' in rob or 'index' not in rob or 'follow' not in rob:errors.append('robots mismatch '+str(pid))
    if 'BlogPosting' not in body:errors.append('BlogPosting missing '+str(pid))
    if re.search(r'"@type"\s*:\s*"Product"',body,re.I):errors.append('accidental Product schema '+str(pid))
    if body.count('<h2>')<8:errors.append('thin heading structure '+str(pid))
    if len(article_links)<1:errors.append('article orphan/no editorial internal link '+str(pid))

for slug,count in EXPECTED_CATEGORY_COUNTS.items():
    c=state['categories'][slug];u=c['url'];st,r,final,_=get(u+'?t='+str(int(time.time())),150);h=head(r);body=r.decode('utf-8','replace')
    print('CATEGORY',slug,st,final,json.dumps(h,ensure_ascii=False,separators=(',',':')),'COUNT',count)
    if st!=200:errors.append('category http '+slug);continue
    if 'g1-editorial-category' not in body:errors.append('category template marker '+slug)
    if norm(h.get('canonical',''))!=norm(u):errors.append('category canonical '+slug)
    rob=h.get('robots','').lower()
    if 'noindex' in rob or 'index' not in rob or 'follow' not in rob:errors.append('category robots '+slug)

blog=state.get('blog',{}).get('url','')
if blog:
    st,r,final,_=get(blog+'?t='+str(int(time.time())),150);h=head(r);body=r.decode('utf-8','replace')
    print('BLOG',st,final,json.dumps(h,ensure_ascii=False,separators=(',',':')),'CARDS',sum(1 for t in EXPECTED_TITLES.values() if t in body))
    if st!=200 or 'g1-editorial-index' not in body:errors.append('blog archive render')
    if norm(h.get('canonical',''))!=norm(blog):errors.append('blog canonical')
    if 'noindex' in h.get('robots','').lower():errors.append('blog noindex')
    for title in EXPECTED_TITLES.values():
        if title not in body:errors.append('blog missing card '+title[:25])

ss,posts=sitemap('post-sitemap.xml');print('POST_SITEMAP',ss,len(posts),json.dumps(posts,ensure_ascii=False));pn={norm(x) for x in posts}
if ss!=200 or len(posts)!=10:errors.append('post sitemap count')
for u in live_urls.values():
    if norm(u) not in pn:errors.append('post sitemap missing '+norm(u))
if blog and norm(blog) not in pn:errors.append('post sitemap missing blog')
ss,cats=sitemap('category-sitemap.xml');print('CATEGORY_SITEMAP',ss,len(cats),json.dumps(cats,ensure_ascii=False));cn={norm(x) for x in cats}
if ss!=200 or len(cats)!=4:errors.append('category sitemap count')
for slug in EXPECTED_CATEGORY_COUNTS:
    u=state['categories'][slug]['url']
    if norm(u) not in cn:errors.append('category sitemap missing '+slug)
ss,products=sitemap('product-sitemap.xml');products=sorted(products);sha=hashlib.sha256('\n'.join(products).encode()).hexdigest();print('PRODUCT_SITEMAP',ss,len(products),sha)
if ss!=200 or len(products)!=47 or sha!=EXPECTED_PRODUCT_SHA:errors.append('product sitemap baseline drift')

print('ERRORS',json.dumps(errors,ensure_ascii=False))
if errors:raise SystemExit('AUDIT FAILED: '+'; '.join(errors))
print('PASS EDITORIAL FOUNDATION AUDIT V2')
