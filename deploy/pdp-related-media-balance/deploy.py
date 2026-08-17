import json, os, ssl, time, urllib.parse, urllib.request

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']; root=os.environ['THEME_ROOT'].strip('/')
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S', time.gmtime())

def call(func, params, post=False):
    url=f'https://{host}:2083/execute/Fileman/{func}'
    enc=urllib.parse.urlencode(params).encode()
    last=None
    for attempt in range(1,6):
        try:
            req=urllib.request.Request(url if post else url+'?'+enc.decode(), data=enc if post else None, method='POST' if post else 'GET')
            req.add_header('Authorization', f'cpanel {user}:{token}')
            if post: req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, context=ctx, timeout=75) as r:
                payload=json.loads(r.read().decode('utf-8'))
            result=payload.get('result') if isinstance(payload.get('result'),dict) else payload
            if not isinstance(result,dict) or result.get('status')!=1:
                raise RuntimeError(str(result.get('errors') if isinstance(result,dict) else 'UAPI failed'))
            return result.get('data')
        except Exception as exc:
            last=exc; print(f'Attempt {attempt}/5 failed for {func}: {exc}')
            if attempt<5: time.sleep(attempt*4)
    raise last

def get_file(rel):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel)
    directory=root if not parent else f'{root}/{parent}'
    data=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for k in ('content','file_content','data'):
            if isinstance(data.get(k),str): return data[k]
    if isinstance(data,str): return data
    raise RuntimeError('Unexpected content '+rel)

def save_file(rel,content):
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel)
    directory=root if not parent else f'{root}/{parent}'
    call('save_file_content',{'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},post=True)

header=get_file('header.php')
save_file(f'header.php.bak-related-media-{stamp}',header)
print('Header backup:',stamp)

css=r'''/* GRAMISS_PDP_RELATED_MEDIA_BALANCE_V1 */
/* Desktop-only rebalance: same outer card footprint, more of it devoted to product photography. */
@media (min-width:1101px){
  body.single-product .related.products ul.products>li.product{
    padding-bottom:82px!important;
  }

  body.single-product .related.products ul.products>li.product img,
  body.single-product .related.products ul.products>li.product picture img{
    width:100%!important;
    max-width:100%!important;
    height:364px!important;
    padding:6px 6px 0!important;
    box-sizing:border-box!important;
    object-fit:contain!important;
    object-position:center!important;
  }

  body.single-product .related.products ul.products>li.product>a.woocommerce-LoopProduct-link::after,
  body.single-product .related.products ul.products>li.product>a.woocommerce-loop-product__link::after{
    height:82px!important;
    border-top-right-radius:48px!important;
  }

  body.single-product .related.products ul.products>li.product .woocommerce-loop-product__title{
    bottom:35px!important;
  }

  body.single-product .related.products ul.products>li.product .price{
    bottom:11px!important;
  }
}
'''
save_file('assets/css/pdp-related-media-balance.css',css)

start='<!-- GRAMISS PDP RELATED MEDIA BALANCE START -->'
end='<!-- GRAMISS PDP RELATED MEDIA BALANCE END -->'
block=start+'\n<link rel="stylesheet" id="gramiss-pdp-related-media-balance-css" href="<?php echo esc_url( get_stylesheet_directory_uri() . \'/assets/css/pdp-related-media-balance.css?v=20260817-1\' ); ?>">\n'+end
if start in header and end in header:
    before,rest=header.split(start,1); _,after=rest.split(end,1); header=before+block+after
elif '</head>' in header:
    header=header.replace('</head>',block+'\n</head>',1)
else:
    raise RuntimeError('header.php has no </head>; refusing blind injection')
save_file('header.php',header)

live_header=get_file('header.php')
live_css=get_file('assets/css/pdp-related-media-balance.css')
checks={
    'related media marker':'GRAMISS_PDP_RELATED_MEDIA_BALANCE_V1' in live_css,
    'desktop scope':'@media (min-width:1101px)' in live_css,
    'image height':'height:364px!important' in live_css,
    'reduced image padding':'padding:6px 6px 0!important' in live_css,
    'same-footprint bottom reserve':'padding-bottom:82px!important' in live_css,
    'title lowered':'bottom:35px!important' in live_css,
    'price lowered':'bottom:11px!important' in live_css,
    'header loader':'gramiss-pdp-related-media-balance-css' in live_header,
}
for label,ok in checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(checks.values()): raise SystemExit('Related media balance verification failed')
print('LIVE PDP RELATED CARD MEDIA BALANCE DEPLOYED AND VERIFIED')
