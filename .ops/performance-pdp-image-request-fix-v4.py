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
    url=f'https://{HOST}:2083/execute/Fileman/{fn}'; encoded=urllib.parse.urlencode(params).encode()
    req=urllib.request.Request(url if post else url+'?'+encoded.decode(),data=encoded if post else None,method='POST' if post else 'GET')
    req.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
    if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
    with urllib.request.urlopen(req,context=CTX,timeout=90) as r: payload=json.loads(r.read().decode('utf-8','replace'))
    result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
    if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
    return result.get('data')

def extract(data):
    if isinstance(data,str): return data
    if isinstance(data,dict):
        for k in ('content','file_content','data'):
            if isinstance(data.get(k),str): return data[k]
    return ''

def read(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel)
    return extract(api('get_file_content',{'dir':ROOT+('/'+parent if parent else ''),'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'}))

def save(rel,text):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel)
    return api('save_file_content',{'dir':ROOT+('/'+parent if parent else ''),'file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def save_root(name,text):
    return api('save_file_content',{'dir':'public_html','file':name,'content':text,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def sha(text): return hashlib.sha256(text.encode()).hexdigest()

def safe_url(url):
    p=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))

def get(url,timeout=180):
    req=urllib.request.Request(safe_url(url),headers={'User-Agent':'GramissPDPImageFixV4/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req,context=CTX,timeout=timeout) as r: return r.status,r.read().decode('utf-8','replace')

def flush():
    name='gramiss-perf-flush-'+str(int(time.time()))+'.php'
    php="<?php require __DIR__.'/wp-load.php'; if(function_exists('wp_cache_flush'))wp_cache_flush(); if(function_exists('opcache_reset'))@opcache_reset(); @unlink(__FILE__); header('Content-Type:text/plain'); echo 'OK'; ?>"
    save_root(name,php); status,body=get(BASE+'/'+name+'?t='+str(time.time()),120)
    if status!=200 or body.strip()!='OK': raise RuntimeError('cache flush failed')

def replace_once(text,old,new,label):
    count=text.count(old)
    if count!=1: raise RuntimeError(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

def sub_once(text,pattern,repl,label):
    out,count=re.subn(pattern,repl,text,count=1)
    if count!=1: raise RuntimeError(f'{label}: expected 1 match, got {count}')
    return out

def attr(tag,name):
    m=re.search(r'\b'+re.escape(name)+r'\s*=\s*["\']([^"\']*)["\']',tag,re.I|re.S)
    return html.unescape(m.group(1)).strip() if m else ''

OLD_RELATED="add_filter( 'single_product_archive_thumbnail_size', function( $size ) { return 'full'; }, 999 );"
NEW_RELATED="add_filter( 'single_product_archive_thumbnail_size', function( $size ) { return 'gramiss-product-card'; }, 999 );"
LOADER='<script id="gramiss-pdp-gallery-switch-js"'
FILTERS="""<!-- GRAMISS PERFORMANCE PDP IMAGE REQUEST V1 START -->
<?php
add_filter( 'wp_get_attachment_image_attributes', function( $attr, $attachment, $size ) {
  if ( function_exists( 'is_product' ) && is_product() && $size === 'gramiss-product-card' && ! empty( $attr['class'] ) && strpos( $attr['class'], 'attachment-gramiss-product-card' ) !== false ) {
    $attr['sizes'] = '(max-width: 767px) 82vw, (max-width: 1200px) 33vw, 25vw';
    $attr['loading'] = 'lazy';
    $attr['decoding'] = 'async';
  }
  return $attr;
}, 99, 3 );
add_filter( 'woocommerce_gallery_image_html_attachment_image_params', function( $params, $attachment_id, $image_size, $main_image ) {
  $params['loading'] = $main_image ? 'eager' : 'lazy';
  $params['decoding'] = 'async';
  $params['sizes'] = $main_image ? '(max-width: 767px) 66vw, (max-width: 1200px) 42vw, 520px' : '(max-width: 767px) 38vw, (max-width: 1200px) 18vw, 220px';
  if ( $main_image ) { $params['fetchpriority'] = 'high'; } else { unset( $params['fetchpriority'] ); }
  return $params;
}, 99, 4 );
?>
<!-- GRAMISS PERFORMANCE PDP IMAGE REQUEST V1 END -->
"""
GALLERY_SOURCE_OLD="src: img.getAttribute('data-large_image') || img.getAttribute('data-src') || img.currentSrc || img.src,"
GALLERY_SOURCE_NEW="src: img.getAttribute('src') || img.currentSrc || img.getAttribute('data-src') || img.getAttribute('data-large_image') || img.src,"
GALLERY_APPLY_OLD="""function applyImage(node,data){
      if(!node || !data) return;
      var src=data.full_src || data.src || data.url || '';
      if(src) node.src=src;
      var srcset=data.srcset || data.src_set || '';
      if(srcset) node.srcset=srcset; else node.removeAttribute('srcset');
      if(data.sizes) node.sizes=data.sizes; else node.removeAttribute('sizes');
      node.alt=data.alt || '';
    }"""
GALLERY_APPLY_NEW="""function applyImage(node,data){
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
STYLE_SOURCE_OLD="""const image =
      doc.querySelector('meta[property=\"og:image\"]')?.content ||
      doc.querySelector('.woocommerce-product-gallery__image img')?.getAttribute('data-large_image') ||
      doc.querySelector('.woocommerce-product-gallery__image img')?.src ||
      doc.querySelector('.g3-gallery img, .product img')?.src || '';"""
STYLE_SOURCE_NEW="""const productImage = doc.querySelector('.woocommerce-product-gallery__image img');
    const image =
      productImage?.getAttribute('src') ||
      productImage?.src ||
      doc.querySelector('.g3-gallery img, .product img')?.getAttribute('src') ||
      doc.querySelector('meta[property=\"og:image\"]')?.content || '';"""
STYLE_CARD_OLD="const img = document.createElement('img');\n    img.src = item.image;\n    img.alt = item.name;\n    img.loading = index === 0 ? 'eager' : 'lazy';\n    img.decoding = 'async';\n    media.append(img);"
STYLE_CARD_NEW="const img = document.createElement('img');\n    img.src = item.image;\n    img.alt = item.name;\n    img.loading = 'lazy';\n    img.fetchPriority = 'low';\n    img.decoding = 'async';\n    media.append(img);"

def verify_rendered():
    status,page=get(PDP+'?perf-image-v4='+str(time.time())); errors=[]
    if status!=200: return ['PDP HTTP '+str(status)]
    if "return 'gramiss-product-card'; }, 999" not in page: errors.append('related card-size filter missing')
    if "return 'full'; }, 999" in page: errors.append('legacy related full-size filter still rendered')
    if 'GRAMISS PERFORMANCE PDP IMAGE REQUEST V1 START' not in page: errors.append('image attribute filter block missing')
    if 'product-runtime-gallery-fix.js?v=20260903-perf4' not in page: errors.append('gallery cache bust missing')
    if 'product-mobile-v1-4.js?v=20260903-perf4' not in page: errors.append('style-card cache bust missing')
    gallery=[]; related=[]
    for m in re.finditer(r'<img\b[^>]*>',page,re.I|re.S):
        tag=m.group(0); context=page[max(0,m.start()-1000):m.end()+220].lower()
        if 'woocommerce-product-gallery' in context and len(gallery)<3: gallery.append(tag)
        if ('related products' in context or 'woocommerce-loop-product__link' in context) and 'attachment-' in tag and len(related)<4: related.append(tag)
    print('GALLERY_TAGS',json.dumps(gallery,ensure_ascii=False)); print('RELATED_TAGS',json.dumps(related,ensure_ascii=False))
    if len(gallery)<3: errors.append('gallery count < 3')
    else:
        if attr(gallery[0],'loading')!='eager': errors.append('main gallery image not eager')
        if attr(gallery[0],'fetchpriority')!='high': errors.append('main gallery image priority not high')
        if '66vw' not in attr(gallery[0],'sizes'): errors.append('main gallery sizes missing 66vw')
        for i,tag in enumerate(gallery[1:3],1):
            if attr(tag,'loading')!='lazy': errors.append(f'gallery image {i} not lazy')
            if '38vw' not in attr(tag,'sizes'): errors.append(f'gallery image {i} sizes missing 38vw')
    if len(related)<4: errors.append('related count < 4')
    for i,tag in enumerate(related[:4]):
        cls=attr(tag,'class'); src=attr(tag,'src'); sizes=attr(tag,'sizes')
        if 'attachment-full' in cls or 'size-full' in cls: errors.append(f'related {i} still full')
        if 'attachment-gramiss-product-card' not in cls: errors.append(f'related {i} missing card class')
        if '82vw' not in sizes: errors.append(f'related {i} sizes missing 82vw')
        if not re.search(r'-\d+x\d+\.(?:png|jpe?g|webp)(?:\?|$)',src,re.I): errors.append(f'related {i} src not intermediate: {src}')
    if len(re.findall(r'<h1\b',page,re.I))!=1: errors.append('PDP H1 count changed')
    return errors

def main():
    before={path:read(path) for path in EXPECTED}
    for path,expected in EXPECTED.items():
        actual=sha(before[path]); print('BEFORE_SHA',path,actual)
        if actual!=expected: raise SystemExit(f'REFUSE live drift {path}: {actual}')
    protected_before={path:sha(read(path)) for path in PROTECTED}
    for path,expected in PROTECTED.items():
        if protected_before[path]!=expected: raise SystemExit('REFUSE protected drift '+path)

    header=before['header.php']; gallery=before['assets/js/product-runtime-gallery-fix.js']; style=before['assets/js/product-mobile-v1-4.js']
    new_header=replace_once(header,OLD_RELATED,NEW_RELATED,'exact related full-size filter')
    if new_header.count('GRAMISS PERFORMANCE PDP IMAGE REQUEST V1 START')!=0: raise SystemExit('REFUSE performance block already exists')
    new_header=replace_once(new_header,LOADER,FILTERS+LOADER,'gallery loader insertion')
    new_header=sub_once(new_header,r'product-runtime-gallery-fix\.js\?v=[^"\']+','product-runtime-gallery-fix.js?v=20260903-perf4','gallery cache bust')
    new_header=sub_once(new_header,r'product-mobile-v1-4\.js\?v=[^"\']+','product-mobile-v1-4.js?v=20260903-perf4','style cache bust')
    new_gallery=replace_once(gallery,GALLERY_SOURCE_OLD,GALLERY_SOURCE_NEW,'gallery source priority')
    new_gallery=replace_once(new_gallery,GALLERY_APPLY_OLD,GALLERY_APPLY_NEW,'gallery apply image')
    new_style=replace_once(style,STYLE_SOURCE_OLD,STYLE_SOURCE_NEW,'style-card source priority')
    new_style=replace_once(new_style,STYLE_CARD_OLD,STYLE_CARD_NEW,'style-card loading')
    changed={'header.php':new_header,'assets/js/product-runtime-gallery-fix.js':new_gallery,'assets/js/product-mobile-v1-4.js':new_style}

    try:
        for path,text in changed.items(): save(path,text)
        flush(); errors=[]
        for path,text in changed.items():
            actual=sha(read(path)); print('AFTER_SHA',path,actual)
            if actual!=sha(text): errors.append('stored mismatch '+path)
        for path,expected in protected_before.items():
            if sha(read(path))!=expected: errors.append('protected file changed '+path)
        errors.extend(verify_rendered()); print('VERIFY_ERRORS',json.dumps(errors,ensure_ascii=False))
        if errors: raise RuntimeError('; '.join(errors))
    except Exception:
        for path,text in before.items(): save(path,text)
        flush(); bad=[path for path,text in before.items() if sha(read(path))!=sha(text)]
        print('ROLLBACK_ERRORS',json.dumps(bad)); print('ROLLBACK PERFORMANCE PDP IMAGE REQUEST FIX V4 COMPLETE')
        if bad: raise RuntimeError('rollback mismatch '+','.join(bad))
        raise
    print('PASS PERFORMANCE PDP IMAGE REQUEST FIX V4')

if __name__=='__main__': main()
