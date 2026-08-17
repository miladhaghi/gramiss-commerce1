import json, os, ssl, time, urllib.parse, urllib.request

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']; root=os.environ['THEME_ROOT'].strip('/')
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S', time.gmtime())

def call(func, params, post=False):
    url=f'https://{host}:2083/execute/Fileman/{func}'
    enc=urllib.parse.urlencode(params).encode(); last=None
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
old_css=get_file('assets/css/pdp-related-mobile-balance.css')
save_file(f'header.php.bak-related-mobile-fit-{stamp}',header)
save_file(f'assets/css/pdp-related-mobile-balance.css.bak-related-mobile-fit-{stamp}',old_css)
print('Backups:',stamp)

css=r'''/* GRAMISS_PDP_RELATED_MOBILE_FIT_V2 */
/* Mobile related cards: show the actual product clearly, preserve sculpted language, remove excess blank card height. */
@media (max-width:767px){
  body.single-product .related.products ul.products>li.product{
    height:auto!important;
    min-height:0!important;
    aspect-ratio:auto!important;
    padding:0 0 78px!important;
    overflow:hidden!important;
    background:#fff!important;
  }

  body.single-product .related.products ul.products>li.product>a.woocommerce-LoopProduct-link,
  body.single-product .related.products ul.products>li.product>a.woocommerce-loop-product__link,
  body.single-product .related.products ul.products>li.product picture{
    display:block!important;
    height:auto!important;
    min-height:0!important;
    background:#fff!important;
  }

  body.single-product .related.products ul.products>li.product img,
  body.single-product .related.products ul.products>li.product picture img{
    display:block!important;
    width:100%!important;
    height:clamp(250px,68vw,310px)!important;
    min-height:0!important;
    max-height:none!important;
    margin:0!important;
    padding:10px 10px 2px!important;
    box-sizing:border-box!important;
    object-fit:contain!important;
    object-position:center top!important;
    background:#fff!important;
    transform:none!important;
    scale:none!important;
    translate:none!important;
  }

  body.single-product .related.products ul.products>li.product>a.woocommerce-LoopProduct-link::after,
  body.single-product .related.products ul.products>li.product>a.woocommerce-loop-product__link::after{
    width:92%!important;
    height:82px!important;
    border-top-right-radius:44px!important;
    background:#fff!important;
  }

  body.single-product .related.products ul.products>li.product .woocommerce-loop-product__title{
    left:12px!important;
    bottom:38px!important;
    width:calc(92% - 24px)!important;
    margin:0!important;
    font-size:11.5px!important;
    line-height:1.45!important;
    white-space:normal!important;
    display:-webkit-box!important;
    -webkit-line-clamp:2!important;
    -webkit-box-orient:vertical!important;
    overflow:hidden!important;
  }

  body.single-product .related.products ul.products>li.product .price{
    left:12px!important;
    bottom:11px!important;
    width:calc(92% - 24px)!important;
    margin:0!important;
    font-size:11.5px!important;
    line-height:1.35!important;
  }
}
'''
save_file('assets/css/pdp-related-mobile-balance.css',css)

# Bump only this already-live stylesheet so mobile browsers do not reuse V1.
if 'pdp-related-mobile-balance.css?v=20260817-1' in header:
    header=header.replace('pdp-related-mobile-balance.css?v=20260817-1','pdp-related-mobile-balance.css?v=20260817-2')
elif 'pdp-related-mobile-balance.css?v=20260817-2' not in header:
    raise RuntimeError('Could not locate the existing mobile balance loader; refusing blind header edit')
save_file('header.php',header)

live_h=get_file('header.php'); live_css=get_file('assets/css/pdp-related-mobile-balance.css')
checks={
    'v2 marker':'GRAMISS_PDP_RELATED_MOBILE_FIT_V2' in live_css,
    'mobile only':'@media (max-width:767px)' in live_css,
    'no crop scale':'transform:none!important' in live_css and 'scale(1.14)' not in live_css,
    'contain image':'object-fit:contain!important' in live_css,
    'usable image height':'height:clamp(250px,68vw,310px)!important' in live_css,
    'compact card':'min-height:0!important' in live_css and 'padding:0 0 78px!important' in live_css,
    'white canvas':'background:#fff!important' in live_css,
    'cache bust':'pdp-related-mobile-balance.css?v=20260817-2' in live_h,
}
for label,ok in checks.items(): print(('PASS' if ok else 'FAIL')+': '+label)
if not all(checks.values()): raise SystemExit('Mobile related fit verification failed')
print('LIVE PDP RELATED MOBILE FIT V2 DEPLOYED AND VERIFIED')
