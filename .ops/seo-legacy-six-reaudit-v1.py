#!/usr/bin/env python3
import hashlib, json, os, re, ssl, time, urllib.parse, urllib.request, urllib.error

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']
BASE='https://gramiss.ir'; CTX=ssl._create_unverified_context(); TARGETS=[97,141,210,344,62,68]

def api(fn,params,post=False):
    url=f'https://{HOST}:2083/execute/Fileman/{fn}'; enc=urllib.parse.urlencode(params).encode()
    req=urllib.request.Request(url if post else url+'?'+enc.decode(),data=enc if post else None,method='POST' if post else 'GET')
    req.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
    if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
    with urllib.request.urlopen(req,context=CTX,timeout=90) as r: payload=json.loads(r.read().decode('utf-8','replace'))
    result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
    if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
    return result.get('data')

def save_root(name,text):
    return api('save_file_content',{'dir':'public_html','file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def safe(url):
    p=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))

def get(url,timeout=150):
    req=urllib.request.Request(safe(url),headers={'User-Agent':'GramissLegacySixReauditV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    try:
        with urllib.request.urlopen(req,context=CTX,timeout=timeout) as r:return r.status,r.read().decode('utf-8','replace'),r.geturl()
    except urllib.error.HTTPError as e:return e.code,e.read().decode('utf-8','replace'),e.geturl()

def meta(html,name):
    m=re.search(r'<meta[^>]+name=["\']'+re.escape(name)+r'["\'][^>]+content=["\']([^"\']*)',html,re.I|re.S)
    if not m:
        m=re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']'+re.escape(name)+r'["\']',html,re.I|re.S)
    return m.group(1).strip() if m else ''

def canonical(html):
    m=re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',html,re.I|re.S)
    if not m:m=re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',html,re.I|re.S)
    return m.group(1).strip() if m else ''

def norm(url):
    if not url:return ''
    return urllib.parse.unquote(url.split('?',1)[0]).rstrip('/')+'/'

def sitemap_state(path, nonce):
    status, xml, _=get(BASE+'/'+path+'?t='+nonce,150)
    urls=sorted(x.replace('&amp;','&') for x in re.findall(r'<loc>(.*?)</loc>',xml,re.I)) if status==200 else []
    digest=hashlib.sha256('\n'.join(urls).encode()).hexdigest()
    print('SITEMAP_STATE',path,status,'COUNT',len(urls),'SHA256',digest)
    return status,urls,digest

nonce=str(int(time.time()))
probe='gramiss-legacy-six-reaudit-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$ids=[97,141,210,344,62,68]; $out=[];
foreach($ids as $id){
  $p=get_post($id); $wc=wc_get_product($id);
  if(!$p || !$wc){$out[]=['id'=>$id,'missing'=>true]; continue;}
  $vars=[];
  if($wc->is_type('variable')){
    foreach($wc->get_children() as $vid){
      $v=wc_get_product($vid); if(!$v)continue;
      $vars[]=['id'=>(int)$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price(),'regular_price'=>$v->get_regular_price(),'sale_price'=>$v->get_sale_price(),'stock_status'=>$v->get_stock_status(),'attributes'=>$v->get_attributes()];
    }
  }
  $out[]=[
    'id'=>$id,'status'=>$p->post_status,'title'=>$p->post_title,'slug'=>$p->post_name,
    'url'=>$p->post_status==='publish'?get_permalink($id):null,
    'type'=>$wc->get_type(),'parent_sku'=>$wc->get_sku(),'parent_price'=>$wc->get_price(),
    'rank_math_robots'=>get_post_meta($id,'rank_math_robots',true),
    'rank_math_title'=>(string)get_post_meta($id,'rank_math_title',true),
    'rank_math_description'=>(string)get_post_meta($id,'rank_math_description',true),
    'rank_math_canonical'=>(string)get_post_meta($id,'rank_math_canonical_url',true),
    'variations'=>$vars
  ];
}
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save_root(probe,php)
status,body,_=get(BASE+'/'+probe+'?t='+nonce,300)
if status!=200:raise SystemExit('PROBE_HTTP_'+str(status))
rows=json.loads(body)

s_status,sitemap_urls,product_sha=sitemap_state('product-sitemap.xml',nonce)
pc_status,pcat_urls,pcat_sha=sitemap_state('product_cat-sitemap.xml',nonce)
sitemap_set={norm(x) for x in sitemap_urls}

passed=0; failed=[]
for row in rows:
    pid=row['id']; issues=[]
    if row.get('missing'):
        issues.append('product_missing')
        print('TARGET_RESULT',json.dumps({'id':pid,'issues':issues},ensure_ascii=False)); failed.append(pid); continue
    url=row.get('url') or ''
    public={}
    if url:
        st,html,final=get(url+'?reaudit='+nonce,180)
        public={'http':st,'final_url':final,'robots':meta(html,'robots'),'canonical':canonical(html),'product_schema_count':len(re.findall(r'"@type"\s*:\s*"Product"',html,re.I)),'in_product_sitemap':norm(url) in sitemap_set}
    if pid in (97,141):
        vars=row.get('variations',[])
        if not vars:issues.append('no_variations_found')
        missing=[v['id'] for v in vars if not str(v.get('sku','')).strip()]
        if missing:issues.append('missing_variation_sku:'+','.join(map(str,missing)))
    if pid==210:
        v=next((x for x in row.get('variations',[]) if x.get('id')==213),None)
        if not v:issues.append('variation_213_missing')
        elif not str(v.get('price','')).strip():issues.append('variation_213_price_missing')
    if pid==344:
        v=next((x for x in row.get('variations',[]) if x.get('id')==346),None)
        if not v:issues.append('variation_346_missing')
        elif not str(v.get('price','')).strip():issues.append('variation_346_price_missing')
    if pid in (62,68):
        robots=(public.get('robots') or '').lower()
        rm=row.get('rank_math_robots')
        rm_text=json.dumps(rm,ensure_ascii=False).lower() if not isinstance(rm,str) else rm.lower()
        if 'noindex' in robots:issues.append('public_noindex')
        if 'noindex' in rm_text:issues.append('rank_math_noindex')
        if public.get('http')!=200:issues.append('public_http_'+str(public.get('http')))
        if norm(public.get('canonical'))!=norm(url):issues.append('canonical_not_self')
        if not public.get('in_product_sitemap'):issues.append('not_in_product_sitemap')
    result={'id':pid,'title':row.get('title'),'status':row.get('status'),'type':row.get('type'),'parent_sku':row.get('parent_sku'),'rank_math_robots':row.get('rank_math_robots'),'variations':row.get('variations'),'public':public,'issues':issues,'pass':not issues}
    print('TARGET_RESULT',json.dumps(result,ensure_ascii=False,separators=(',',':')))
    if issues:failed.append(pid)
    else:passed+=1
print('REAUDIT_SUMMARY',json.dumps({'pass':passed,'fail':len(failed),'failed_ids':failed},ensure_ascii=False,separators=(',',':')))
if failed:raise SystemExit('LEGACY_SIX_REAUDIT_FAILED '+','.join(map(str,failed)))
print('PASS LEGACY SIX REAUDIT V1')
