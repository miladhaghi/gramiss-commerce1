#!/usr/bin/env python3
import hashlib, html, json, os, re, ssl, time, urllib.parse, urllib.request

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']
ROOT='public_html/wp-content/themes/gramiss-theme-next'; BASE='https://gramiss.ir'
PDP='https://gramiss.ir/product/%d8%b4%d9%84%d9%88%d8%a7%d8%b1-%d8%ac%db%8c%d9%86-%d8%a8%d8%a7%d9%84%d9%86%db%8c-%d8%aa%db%8c%d9%86%d8%aa-%d8%b3%d8%a8%d8%b2/'
CTX=ssl._create_unverified_context()

def api(fn,params,post=False):
    u=f'https://{HOST}:2083/execute/Fileman/{fn}'; enc=urllib.parse.urlencode(params).encode()
    req=urllib.request.Request(u if post else u+'?'+enc.decode(),data=enc if post else None,method='POST' if post else 'GET')
    req.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
    if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
    with urllib.request.urlopen(req,context=CTX,timeout=120) as r:p=json.loads(r.read().decode('utf-8','replace'))
    z=p.get('result') if isinstance(p.get('result'),dict) else p
    if not isinstance(z,dict) or z.get('status')!=1: raise RuntimeError(str(z))
    return z.get('data')

def save_root(name,text):return api('save_file_content',{'dir':'public_html','file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def safe_url(url):
    p=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def get(url):
    req=urllib.request.Request(safe_url(url),headers={'User-Agent':'GramissGlobalRuntimeScan/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req,context=CTX,timeout=180) as r:return r.status,r.read().decode('utf-8','replace'),r.geturl()

# Server-side recursive source search. Self-deleting helper; no theme writes.
nonce=hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]
probe='gramiss-global-runtime-scan-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$root = get_stylesheet_directory();
$needles = [
 'product.images[0].src','images?.[0]?.src','wc/store/v1','g1-style-card','g1-style-intelligence',
 'full_src','data-large_image','data-large-image','new Image','createElement(\'img\')','createElement("img")',
 '.src =','.src=','loading = \'eager\'','loading=\'eager\'','fetchpriority','fetchPriority',
 'srcset','currentSrc','woocommerce-product-gallery','g3-dual-image','g3ApplyVariationImage',
 'found_variation','show_variation','variation.image','wp_get_attachment_image','attachment-full',
 'single_product_archive_thumbnail_size','gramiss-product-card'
];
$out=[];
$it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root,FilesystemIterator::SKIP_DOTS));
foreach($it as $file){
 if(!$file->isFile()) continue;
 $ext=strtolower(pathinfo($file->getFilename(),PATHINFO_EXTENSION));
 if(!in_array($ext,['php','js'],true)) continue;
 $text=@file_get_contents($file->getPathname()); if($text===false) continue;
 $hits=[];
 foreach($needles as $needle){
  $pos=0;$parts=[];
  while(($i=stripos($text,$needle,$pos))!==false && count($parts)<8){
   $parts[]=substr($text,max(0,$i-700),1700);$pos=$i+strlen($needle);
  }
  if($parts)$hits[$needle]=$parts;
 }
 if($hits){
  $rel=ltrim(str_replace($root,'',$file->getPathname()),'/\\');
  $out[]=['path'=>$rel,'sha256'=>hash_file('sha256',$file->getPathname()),'bytes'=>filesize($file->getPathname()),'hits'=>$hits];
 }
}
echo wp_json_encode(['theme'=>$root,'matches'=>$out],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
save_root(probe,php)
st,raw,_=get(BASE+'/'+probe+'?t='+str(time.time()))
if st!=200: raise SystemExit('probe HTTP '+str(st))
state=json.loads(raw)
for row in state.get('matches',[]):
    print('GLOBAL_SOURCE_MATCH',json.dumps(row,ensure_ascii=False,sort_keys=True))
print('GLOBAL_SOURCE_MATCH_COUNT',len(state.get('matches',[])))

# Rendered PDP inventory.
st,page,final=get(PDP+'?perf-global-scan='+str(time.time()))
if st!=200: raise SystemExit('PDP HTTP '+str(st))
body=re.search(r'<body\b([^>]*)>',page,re.I|re.S)
body_tag=body.group(0) if body else ''
classes=re.search(r'\bclass=["\']([^"\']*)["\']',body_tag,re.I|re.S)
body_classes=html.unescape(classes.group(1)) if classes else ''
postids=re.findall(r'\bpostid-(\d+)\b',body_classes)
print('PDP_IDENTITY',json.dumps({'final':final,'body_classes':body_classes,'postids':postids},ensure_ascii=False))

scripts=[]
for m in re.finditer(r'<script\b[^>]*>',page,re.I|re.S):
    tag=m.group(0)
    srcm=re.search(r'\bsrc=["\']([^"\']+)["\']',tag,re.I|re.S)
    idm=re.search(r'\bid=["\']([^"\']+)["\']',tag,re.I|re.S)
    src=html.unescape(srcm.group(1)) if srcm else ''
    sid=html.unescape(idm.group(1)) if idm else ''
    if any(k in (src+' '+sid).lower() for k in ['product','woocommerce','g1','g2','g3','gramiss']):
        scripts.append({'id':sid,'src':src})
print('PDP_SCRIPT_LOADERS',json.dumps(scripts,ensure_ascii=False))

# All PDP img tags that can select >600 candidates, especially related/style/gallery.
imgs=[]
for m in re.finditer(r'<img\b[^>]*>',page,re.I|re.S):
    tag=m.group(0); ctx=page[max(0,m.start()-900):m.end()+300].lower()
    def at(name):
        x=re.search(r'\b'+re.escape(name)+r'\s*=\s*["\']([^"\']*)["\']',tag,re.I|re.S)
        return html.unescape(x.group(1)).strip() if x else ''
    src,ss,sz,cl=at('src'),at('srcset'),at('sizes'),at('class')
    if any(k in ctx for k in ['woocommerce-product-gallery','related products','related products','related','g1-style','g3-dual']) or ss:
        imgs.append({'src':src,'srcset':ss,'sizes':sz,'class':cl,'loading':at('loading'),'fetchpriority':at('fetchpriority'),'flags':[k for k in ['woocommerce-product-gallery','related','g1-style','g3-dual'] if k in ctx]})
print('PDP_RELEVANT_IMG_TAGS',json.dumps(imgs[:40],ensure_ascii=False))

# Look for heavy filenames explicitly in raw HTML to prove server vs runtime origin.
heavy=['Jean-VIPBTike-004-3.png','Jean-VIPBaloonZap-005a-3.png','Jean-VIPNimZap-007b.png','Jean-MBaloon-003a.png','Parche-VBagKerepS-0011-1.png','Vans-CHFSefid-003-1.png']
print('PDP_HEAVY_RAW_HTML_COUNTS',json.dumps({n:page.count(n) for n in heavy},sort_keys=True))
print('PASS GLOBAL LIVE PDP IMAGE RUNTIME SCAN READ ONLY')
