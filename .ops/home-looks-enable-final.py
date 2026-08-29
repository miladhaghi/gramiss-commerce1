import hashlib, html, json, os, re, ssl, time, urllib.error, urllib.parse, urllib.request, xml.etree.ElementTree as ET

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']
root=os.environ['THEME_ROOT'].strip('/'); healthy=os.environ.get('HEALTHY_HOME_SHA','')
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime())

def call(fn,params,post=False):
    url=f'https://{host}:2083/execute/Fileman/{fn}'; data=urllib.parse.urlencode(params).encode(); last=None
    for attempt in range(1,5):
        try:
            req=urllib.request.Request(url if post else url+'?'+data.decode(),data=data if post else None,method='POST' if post else 'GET')
            req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as r: obj=json.loads(r.read().decode('utf-8','replace'))
            result=obj.get('result') if isinstance(obj.get('result'),dict) else obj
            if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last=exc; print(f'Attempt {attempt}/4 {fn}: {exc}')
            if attempt<4: time.sleep(attempt*2)
    raise last

def read_theme(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=root if not parent else root+'/'+parent
    data=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for key in ('content','file_content','data'):
            if isinstance(data.get(key),str): return data[key]
    if isinstance(data,str): return data
    raise RuntimeError('Cannot read '+rel)

def save_public(name,content):
    return call('save_file_content',{'dir':'public_html','file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def get(url,follow=True,timeout=90):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl): return None
    req=urllib.request.Request(url,headers={'User-Agent':'GramissSEOIndexationAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    handlers=[urllib.request.HTTPSHandler(context=ctx)]
    if not follow: handlers.insert(0,NoRedirect())
    opener=urllib.request.build_opener(*handlers)
    try:
        with opener.open(req,timeout=timeout) as r: return r.status,r.read(),r.geturl(),dict(r.headers)
    except urllib.error.HTTPError as e: return e.code,e.read(),url,dict(e.headers)

def xlocs(raw):
    try:
        rootx=ET.fromstring(raw)
        out=[]
        for el in rootx.iter():
            if el.tag.endswith('loc') and el.text: out.append(el.text.strip())
        return out
    except Exception as exc:
        print('XML_PARSE_WARN',str(exc)[:180]); return []

def extract_head(raw):
    text=raw.decode('utf-8','replace')
    m=re.search(r'<head\b[^>]*>(.*?)</head>',text,re.I|re.S); head=m.group(1) if m else text[:30000]
    title=''; tm=re.search(r'<title[^>]*>(.*?)</title>',head,re.I|re.S)
    if tm: title=html.unescape(re.sub(r'<[^>]+>','',tm.group(1))).strip()
    canon=''; cm=re.search(r'<link[^>]+rel=["\'][^"\']*canonical[^"\']*["\'][^>]*href=["\']([^"\']+)',head,re.I)
    if not cm: cm=re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*canonical',head,re.I)
    if cm: canon=html.unescape(cm.group(1)).strip()
    robots=[]
    for mm in re.finditer(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)',head,re.I): robots.append(mm.group(1).strip())
    for mm in re.finditer(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']robots["\']',head,re.I): robots.append(mm.group(1).strip())
    desc=''; dm=re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)',head,re.I)
    if not dm: dm=re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']',head,re.I)
    if dm: desc=html.unescape(dm.group(1)).strip()
    og=bool(re.search(r'<meta[^>]+property=["\']og:',head,re.I)); twitter=bool(re.search(r'<meta[^>]+(?:name|property)=["\']twitter:',head,re.I))
    jsonld_types=sorted(set(re.findall(r'["\']@type["\']\s*:\s*["\']([^"\']+)',head,re.I)))
    return {'title':title,'canonical':canon,'robots':robots,'description_len':len(desc),'has_og':og,'has_twitter':twitter,'jsonld_types':jsonld_types}

front=read_theme('front-page.php'); front_sha=hashlib.sha256(front.encode()).hexdigest(); print('LIVE_HOME_SHA',front_sha)
if healthy and front_sha!=healthy: raise SystemExit('ABORT: Home baseline mismatch; audit not run')

nonce=hashlib.sha256((stamp+front_sha).encode()).hexdigest()[:18]; probe=f'gramiss-seo-index-audit-{nonce}.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function g1_opt($n){$v=get_option($n,null);return $v===null?'__MISSING__':$v;}
$active=(array)get_option('active_plugins',[]);$rank=array_values(array_filter($active,fn($p)=>strpos($p,'rank-math')!==false));
$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);$products=[];foreach($ids as $id)$products[]=['id'=>(int)$id,'url'=>get_permalink($id),'slug'=>(string)get_post_field('post_name',$id)];
$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>false]);$cats=[];if(!is_wp_error($terms)){foreach($terms as $t)$cats[]=['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug,'count'=>(int)$t->count,'parent'=>(int)$t->parent,'url'=>get_term_link($t)];}
$pages=[];foreach(['shop'=>'woocommerce_shop_page_id','cart'=>'woocommerce_cart_page_id','checkout'=>'woocommerce_checkout_page_id','account'=>'woocommerce_myaccount_page_id'] as $k=>$o){$id=(int)get_option($o);$pages[$k]=['id'=>$id,'url'=>$id?get_permalink($id):''];}
$out=['permalink_structure'=>(string)get_option('permalink_structure'),'blog_public'=>(int)get_option('blog_public'),'active_rank_math'=>$rank,'rank_math_version'=>defined('RANK_MATH_VERSION')?RANK_MATH_VERSION:'','rank_math_modules'=>g1_opt('rank_math_modules'),'rank_math_sitemap'=>g1_opt('rank-math-options-sitemap'),'rank_math_titles'=>g1_opt('rank-math-options-titles'),'rank_math_general'=>g1_opt('rank-math-options-general'),'show_on_front'=>get_option('show_on_front'),'page_on_front'=>(int)get_option('page_on_front'),'products'=>$products,'categories'=>$cats,'pages'=>$pages,'home'=>home_url('/')];
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save_public(probe,php)
st,b,final,_=get('https://gramiss.ir/'+probe+'?t='+str(int(time.time())),True,180); print('PROBE_STATUS',st,'BYTES',len(b),'FINAL',final)
if st!=200: raise SystemExit('ABORT: read-only probe failed')
data=json.loads(b.decode('utf-8','replace'))
print('WP_STATE',json.dumps({k:data.get(k) for k in ['permalink_structure','blog_public','active_rank_math','rank_math_version','rank_math_modules','show_on_front','page_on_front']},ensure_ascii=False,separators=(',',':')))
# Print only sitemap/titles keys relevant to indexability, not arbitrary plugin data.
for optkey in ['rank_math_sitemap','rank_math_titles']:
    val=data.get(optkey)
    if isinstance(val,dict):
        filtered={k:v for k,v in val.items() if any(x in str(k).lower() for x in ['sitemap','include','exclude','robots','noindex','product','page','post','category','tax','author','attachment','links_per_sitemap'])}
        print(optkey.upper(),json.dumps(filtered,ensure_ascii=False,separators=(',',':')))
    else: print(optkey.upper(),json.dumps(val,ensure_ascii=False,separators=(',',':')))

# Endpoint inventory.
endpoints={}
for path in ['robots.txt','wp-sitemap.xml','sitemap_index.xml']:
    s,raw,f,h=get('https://gramiss.ir/'+path,True,90); endpoints[path]={'status':s,'final':f,'bytes':len(raw),'content_type':h.get('Content-Type',''),'locs':xlocs(raw) if s==200 and b'<loc>' in raw else []}
    print('ENDPOINT',path,json.dumps(endpoints[path],ensure_ascii=False,separators=(',',':')))
    if path=='robots.txt': print('ROBOTS_BODY',raw.decode('utf-8','replace')[:3000].replace('\n',' | '))

# Crawl native WP sitemap index and child sitemap locations.
all_native=set(); child_reports=[]
for child in endpoints.get('wp-sitemap.xml',{}).get('locs',[]):
    s,raw,f,h=get(child,True,90); locs=xlocs(raw) if s==200 else []; all_native.update(locs)
    report={'url':child,'status':s,'count':len(locs),'sample':locs[:5]}; child_reports.append(report); print('NATIVE_CHILD',json.dumps(report,ensure_ascii=False,separators=(',',':')))
print('NATIVE_TOTAL_UNIQUE',len(all_native))

products=data.get('products',[]); product_urls={p['url'] for p in products}; cats=data.get('categories',[]); active_cat_urls={c['url'] for c in cats if c.get('count',0)>0}; empty_cat_urls={c['url'] for c in cats if c.get('count',0)==0}; pages=data.get('pages',{})
print('NATIVE_PRODUCT_COVERAGE',json.dumps({'published':len(product_urls),'present':len(product_urls & all_native),'missing':sorted(product_urls-all_native)[:20]},ensure_ascii=False,separators=(',',':')))
print('NATIVE_ACTIVE_CATEGORY_COVERAGE',json.dumps({'active':len(active_cat_urls),'present':len(active_cat_urls & all_native),'missing':sorted(active_cat_urls-all_native)[:20]},ensure_ascii=False,separators=(',',':')))
print('NATIVE_EMPTY_CATEGORIES_INCLUDED',json.dumps(sorted(empty_cat_urls & all_native)[:50],ensure_ascii=False,separators=(',',':')))
for key,row in pages.items(): print('UTILITY_IN_NATIVE',key,row.get('url') in all_native,row.get('url'))

# Audit indexation/head output of representative page types.
checks=[('home',data.get('home','')),('shop',pages.get('shop',{}).get('url','')),('product',next((p['url'] for p in products if p.get('id')==392),products[0]['url'] if products else '')),('category',next((c['url'] for c in cats if c.get('slug')=='tshirt'),'')),('cart',pages.get('cart',{}).get('url','')),('account',pages.get('account',{}).get('url','')),('search','https://gramiss.ir/?s=تیشرت')]
for label,url in checks:
    if not url: continue
    s,raw,f,h=get(url,True,90); info=extract_head(raw); print('HEAD_AUDIT',label,json.dumps({'requested':url,'status':s,'final':f,**info},ensure_ascii=False,separators=(',',':')))

# Rank Math sitemap path may be disabled. If index exists, crawl children too.
rank_total=set()
for child in endpoints.get('sitemap_index.xml',{}).get('locs',[]):
    s,raw,f,h=get(child,True,90); locs=xlocs(raw) if s==200 else []; rank_total.update(locs); print('RANK_CHILD',json.dumps({'url':child,'status':s,'count':len(locs),'sample':locs[:5]},ensure_ascii=False,separators=(',',':')))
if rank_total:
    print('RANK_PRODUCT_COVERAGE',json.dumps({'published':len(product_urls),'present':len(product_urls & rank_total),'missing':sorted(product_urls-rank_total)[:20]},ensure_ascii=False,separators=(',',':')))
    for key,row in pages.items(): print('UTILITY_IN_RANK',key,row.get('url') in rank_total,row.get('url'))

if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=front_sha: raise SystemExit('ABORT: Home changed during read-only audit')
print('=== END SITEMAP/INDEXATION AUDIT; NO SETTINGS, CONTENT, URLS OR SEO META CHANGED ===')
