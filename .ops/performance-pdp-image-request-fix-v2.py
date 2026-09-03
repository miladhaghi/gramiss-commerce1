#!/usr/bin/env python3
import hashlib, html, json, os, re, ssl, time, urllib.parse, urllib.request

HOST=os.environ['CPANEL_HOST']; USER=os.environ['CPANEL_USER']; TOKEN=os.environ['CPANEL_TOKEN']
ROOT='public_html/wp-content/themes/gramiss-theme-next'; BASE='https://gramiss.ir'
PDP='https://gramiss.ir/product/%d8%b4%d9%84%d9%88%d8%a7%d8%b1-%d8%ac%db%8c%d9%86-%d8%a8%d8%a7%d9%84%d9%86%db%8c-%d8%aa%db%8c%d9%86%d8%aa-%d8%b3%d8%a8%d8%b2/'
CTX=ssl._create_unverified_context()
EXPECTED={
 'header.php':'94456594e7f2699b677e9c4193c0626a67e5fdce573aa74180cbd00d1539f66f',
 'assets/js/product-runtime-gallery-fix.js':'b22a84f502748116d38d9a76039a341b57369c0e16daafcbb66454e09f0632de',
 'assets/js/product-mobile-v1-4.js':'ad34ed1b570a3d5f13d5fb8493d933b624eda9b75d2d2fb1f6dc16f9ae0841e8'}
PROTECTED={
 'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
 'template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
 'assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
 'assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'}

def api(fn,params,post=False):
 u=f'https://{HOST}:2083/execute/Fileman/{fn}'; enc=urllib.parse.urlencode(params).encode()
 r=urllib.request.Request(u if not post else u,data=enc if post else None,method='POST' if post else 'GET')
 if not post: r=urllib.request.Request(u+'?'+enc.decode())
 r.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
 if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(r,context=CTX,timeout=90) as x:p=json.loads(x.read().decode('utf-8','replace'))
 z=p.get('result') if isinstance(p.get('result'),dict) else p
 if not isinstance(z,dict) or z.get('status')!=1: raise RuntimeError(str(z))
 return z.get('data')

def content(d):
 if isinstance(d,str):return d
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return ''

def read(rel):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel)
 return content(api('get_file_content',{'dir':ROOT+('/'+d if d else ''),'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'}))

def save(rel,text):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel)
 return api('save_file_content',{'dir':ROOT+('/'+d if d else ''),'file':n,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def save_root(n,text):return api('save_file_content',{'dir':'public_html','file':n,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def sha(s):return hashlib.sha256(s.encode()).hexdigest()

def safe_url(url):
 p=urllib.parse.urlsplit(url)
 return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def get(url,timeout=180):
 r=urllib.request.Request(safe_url(url),headers={'User-Agent':'GramissPDPImageFixV2/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 with urllib.request.urlopen(r,context=CTX,timeout=timeout) as x:return x.status,x.read().decode('utf-8','replace')

def flush():
 n='gramiss-perf-flush-'+str(int(time.time()))+'.php'
 php="<?php require __DIR__.'/wp-load.php'; if(function_exists('wp_cache_flush'))wp_cache_flush(); if(function_exists('opcache_reset'))@opcache_reset(); @unlink(__FILE__); header('Content-Type:text/plain'); echo 'OK'; ?>"
 save_root(n,php); st,b=get(BASE+'/'+n+'?t='+str(time.time()),120)
 if st!=200 or b.strip()!='OK':raise RuntimeError('flush failed')

def replace_once(text,old,new,label):
 c=text.count(old)
 if c!=1:raise RuntimeError(f'{label}: expected 1 exact match, got {c}')
 return text.replace(old,new,1)

def sub_once(text,pattern,repl,label,flags=0):
 out,n=re.subn(pattern,repl,text,count=1,flags=flags)
 if n!=1:raise RuntimeError(f'{label}: expected 1 regex match, got {n}')
 return out

def attr(tag,name):
 m=re.search(r'\b'+re.escape(name)+r'\s*=\s*["\']([^"\']*)["\']',tag,re.I|re.S)
 return html.unescape(m.group(1)).strip() if m else ''

RELATED_RE=r"add_filter\s*\(\s*(['\"])single_product_archive_thumbnail_size\1\s*,\s*function\s*\(\s*\$size\s*\)\s*\{\s*return\s*(['\"])full\2\s*;\s*\}\s*\)\s*;"
RELATED_NEW="""add_filter( 'single_product_archive_thumbnail_size', function( $size ) { return 'gramiss-product-card'; } );
add_filter( 'wp_get_attachment_image_attributes', function( $attr, $attachment, $size ) {
  if ( function_exists( 'is_product' ) && is_product() && $size === 'gramiss-product-card' && ! empty( $attr['class'] ) && strpos( $attr['class'], 'attachment-gramiss-product-card' ) !== false ) {
    $attr['sizes'] = '(max-width: 767px) 82vw, (max-width: 1200px) 33vw, 25vw';
    $attr['loading'] = 'lazy'; $attr['decoding'] = 'async';
  }
  return $attr;
}, 30, 3 );
add_filter( 'woocommerce_gallery_image_html_attachment_image_params', function( $params, $attachment_id, $image_size, $main_image ) {
  $params['loading'] = $main_image ? 'eager' : 'lazy';
  $params['decoding'] = 'async';
  $params['sizes'] = $main_image ? '(max-width: 767px) 66vw, (max-width: 1200px) 42vw, 520px' : '(max-width: 767px) 38vw, (max-width: 1200px) 18vw, 220px';
  if ( $main_image ) { $params['fetchpriority'] = 'high'; } else { unset( $params['fetchpriority'] ); }
  return $params;
}, 30, 4 );"""

GALLERY_OLD="src: img.getAttribute('data-large_image') || img.getAttribute('data-src') || img.currentSrc || img.src,"
GALLERY_NEW="src: img.getAttribute('src') || img.currentSrc || img.getAttribute('data-src') || img.getAttribute('data-large_image') || img.src,"
APPLY_OLD="""function applyImage(node,data){
      if(!node || !data) return;
      var src=data.full_src || data.src || data.url || '';
      if(src) node.src=src;
      var srcset=data.srcset || data.src_set || '';
      if(srcset) node.srcset=srcset; else node.removeAttribute('srcset');
      if(data.sizes) node.sizes=data.sizes; else node.removeAttribute('sizes');
      node.alt=data.alt || '';
    }"""
APPLY_NEW="""function applyImage(node,data){
      if(!node || !data) return;
      var src=data.src || data.url || data.full_src || '';
      var srcset=data.srcset || data.src_set || '';
      if(srcset) node.srcset=srcset; else node.removeAttribute('srcset');
      node.sizes=node.classList.contains('g3-dual-image-secondary')
        ? '(max-width: 767px) 38vw, (max-width: 1200px) 18vw, 220px'
        : '(max-width: 767px) 66vw, (max-width: 1200px) 42vw, 520px';
      if(src) node.src=src;
      node.alt=data.alt || '';
    }"""
STYLE_OLD="""const image =
      doc.querySelector('meta[property=\"og:image\"]')?.content ||
      doc.querySelector('.woocommerce-product-gallery__image img')?.getAttribute('data-large_image') ||
      doc.querySelector('.woocommerce-product-gallery__image img')?.src ||
      doc.querySelector('.g3-gallery img, .product img')?.src || '';"""
STYLE_NEW="""const productImage = doc.querySelector('.woocommerce-product-gallery__image img');
    const image =
      productImage?.getAttribute('src') ||
      productImage?.src ||
      doc.querySelector('.g3-gallery img, .product img')?.getAttribute('src') ||
      doc.querySelector('meta[property=\"og:image\"]')?.content || '';"""
CARD_OLD="const img = document.createElement('img');\n    img.src = item.image;\n    img.alt = item.name;\n    img.loading = index === 0 ? 'eager' : 'lazy';\n    img.decoding = 'async';\n    media.append(img);"
CARD_NEW="const img = document.createElement('img');\n    img.src = item.image;\n    img.alt = item.name;\n    img.loading = 'lazy';\n    img.fetchPriority = 'low';\n    img.decoding = 'async';\n    media.append(img);"

def verify():
 st,page=get(PDP+'?perf-image-v2='+str(time.time()))
 e=[]
 if st!=200:return ['PDP HTTP '+str(st)]
 if 'product-runtime-gallery-fix.js?v=20260903-perf2' not in page:e.append('gallery cache bust missing')
 if 'product-mobile-v1-4.js?v=20260903-perf2' not in page:e.append('style cache bust missing')
 gallery=[]; related=[]
 for m in re.finditer(r'<img\b[^>]*>',page,re.I|re.S):
  t=m.group(0); ctx=page[max(0,m.start()-1000):m.end()+220].lower()
  if 'woocommerce-product-gallery' in ctx and len(gallery)<3:gallery.append(t)
  if ('related products' in ctx or 'woocommerce-loop-product__link' in ctx) and 'attachment-' in t and len(related)<4:related.append(t)
 print('GALLERY_TAGS',json.dumps(gallery,ensure_ascii=False)); print('RELATED_TAGS',json.dumps(related,ensure_ascii=False))
 if len(gallery)<3:e.append('gallery count <3')
 else:
  if attr(gallery[0],'loading')!='eager':e.append('main not eager')
  if attr(gallery[0],'fetchpriority')!='high':e.append('main priority not high')
  if '66vw' not in attr(gallery[0],'sizes'):e.append('main sizes not custom')
  for i,t in enumerate(gallery[1:3],1):
   if attr(t,'loading')!='lazy':e.append(f'gallery {i} not lazy')
 if len(related)<4:e.append('related count <4')
 for i,t in enumerate(related[:4]):
  cl=attr(t,'class'); src=attr(t,'src'); sizes=attr(t,'sizes')
  if 'attachment-full' in cl or 'size-full' in cl:e.append(f'related {i} still full')
  if 'attachment-gramiss-product-card' not in cl:e.append(f'related {i} no card size')
  if '82vw' not in sizes:e.append(f'related {i} sizes wrong')
  if not re.search(r'-\d+x\d+\.(png|jpe?g|webp)(\?|$)',src,re.I):e.append(f'related {i} src not intermediate')
 if len(re.findall(r'<h1\b',page,re.I))!=1:e.append('H1 changed')
 return e

def main():
 before={p:read(p) for p in EXPECTED}
 for p,x in EXPECTED.items():
  actual=sha(before[p]); print('BEFORE',p,actual)
  if actual!=x:raise SystemExit('REFUSE drift '+p)
 for p,x in PROTECTED.items():
  if sha(read(p))!=x:raise SystemExit('REFUSE protected drift '+p)
 header=before['header.php']; gallery=before['assets/js/product-runtime-gallery-fix.js']; style=before['assets/js/product-mobile-v1-4.js']
 newh=sub_once(header,RELATED_RE,lambda m:RELATED_NEW,'related full filter',re.S)
 newh=sub_once(newh,r'product-runtime-gallery-fix\.js\?v=[^"\']+','product-runtime-gallery-fix.js?v=20260903-perf2','gallery loader')
 newh=sub_once(newh,r'product-mobile-v1-4\.js\?v=[^"\']+','product-mobile-v1-4.js?v=20260903-perf2','style loader')
 newg=replace_once(gallery,GALLERY_OLD,GALLERY_NEW,'gallery source')
 newg=replace_once(newg,APPLY_OLD,APPLY_NEW,'gallery apply')
 news=replace_once(style,STYLE_OLD,STYLE_NEW,'style source')
 news=replace_once(news,CARD_OLD,CARD_NEW,'style card')
 changed={'header.php':newh,'assets/js/product-runtime-gallery-fix.js':newg,'assets/js/product-mobile-v1-4.js':news}
 try:
  for p,t in changed.items():save(p,t)
  flush(); errs=[]
  for p,t in changed.items():
   a=sha(read(p)); print('AFTER',p,a)
   if a!=sha(t):errs.append('stored mismatch '+p)
  for p,x in PROTECTED.items():
   if sha(read(p))!=x:errs.append('protected changed '+p)
  errs+=verify(); print('VERIFY_ERRORS',json.dumps(errs,ensure_ascii=False))
  if errs:raise RuntimeError('; '.join(errs))
 except Exception:
  for p,t in before.items():save(p,t)
  flush(); bad=[p for p,t in before.items() if sha(read(p))!=sha(t)]
  print('ROLLBACK_ERRORS',json.dumps(bad)); print('ROLLBACK COMPLETE')
  if bad:raise RuntimeError('rollback mismatch '+','.join(bad))
  raise
 print('PASS PERFORMANCE PDP IMAGE REQUEST FIX V2')

if __name__=='__main__':main()
