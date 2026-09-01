import argparse,hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request

BASE='https://gramiss.ir'
EXPECTED_PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'
PROTECTED={
 'front-page.php':'0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7',
 'template-parts/home-looks.php':'3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d',
 'assets/css/home-looks.css':'98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0',
 'assets/js/home-looks.js':'6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2'
}
VALID_STOCK={'instock','outofstock','onbackorder'}


def words(s):
 return len([x for x in re.split(r'\s+',str(s or '').strip()) if x])

def norm_url(u):
 if not u:return ''
 p=urllib.parse.urlsplit(urllib.parse.unquote(u));path=p.path.rstrip('/')+'/'
 return urllib.parse.urlunsplit((p.scheme.lower(),p.netloc.lower(),path,'',''))

def evaluate_product(d,index_intent='index',mode='prepublish'):
 blockers=[];warnings=[]
 def block(code,detail=''):blockers.append({'code':code,'detail':detail})
 def warn(code,detail=''):warnings.append({'code':code,'detail':detail})
 if not d.get('exists'):block('product_not_found');return blockers,warnings
 title=str(d.get('title') or '').strip();slug=str(d.get('slug') or '').strip();ptype=str(d.get('type') or '').strip()
 if not title:block('title_missing')
 if not slug:block('slug_missing')
 if ptype not in {'simple','variable','grouped','external'}:block('product_type_invalid',ptype)
 cats=d.get('categories') or []
 if not cats:block('category_missing')
 if not str(d.get('sku') or '').strip():block('parent_sku_missing')
 if int(d.get('description_words') or 0)<=0:block('description_missing')
 if int(d.get('short_description_words') or 0)<=0:block('short_description_missing')
 if not int(d.get('featured_image') or 0):block('featured_image_missing')
 empty_alt=[x for x in (d.get('images') or []) if not str(x.get('alt') or '').strip()]
 if empty_alt:block('image_alt_missing',','.join(str(x.get('id')) for x in empty_alt))
 stock=str(d.get('stock_status') or '')
 if stock not in VALID_STOCK:block('stock_status_invalid',stock)
 if d.get('manage_stock') and d.get('stock_quantity') is None:block('stock_quantity_missing')
 if ptype=='simple':
  if not str(d.get('price') or '').strip():block('simple_price_missing')
 if ptype=='variable':
  attrs=d.get('attributes') or []
  if not any(bool(a.get('variation')) for a in attrs):block('variation_attribute_missing')
  vs=d.get('variations') or []
  if not vs:block('variations_missing')
  seen_sku={}
  for v in vs:
   vid=str(v.get('id'))
   sku=str(v.get('sku') or '').strip()
   if not sku:block('variation_sku_missing',vid)
   elif sku in seen_sku:block('variation_sku_duplicate',f'{seen_sku[sku]},{vid}:{sku}')
   else:seen_sku[sku]=vid
   if not str(v.get('price') or '').strip():block('variation_price_missing',vid)
   vst=str(v.get('stock_status') or '')
   if vst not in VALID_STOCK:block('variation_stock_status_invalid',f'{vid}:{vst}')
   if v.get('manage_stock') and v.get('stock_quantity') is None:block('variation_stock_quantity_missing',vid)
   if not (v.get('attributes') or {}):block('variation_attributes_missing',vid)
 dup=d.get('duplicate_titles') or []
 if dup:warn('duplicate_title_review',','.join(str(x) for x in dup))
 if index_intent not in {'index','noindex'}:block('index_intent_invalid',index_intent)
 if mode=='postpublish':
  pub=d.get('public') or {}
  if d.get('status')!='publish':block('postpublish_requires_published_status',str(d.get('status')))
  if int(pub.get('status') or 0)!=200:block('public_http_not_200',str(pub.get('status')))
  if not str(pub.get('title') or '').strip():block('public_title_missing')
  if not str(pub.get('description') or '').strip():block('public_meta_description_missing')
  robots=str(pub.get('robots') or '').lower()
  if index_intent=='index':
   if 'noindex' in robots or 'index' not in robots:block('public_not_indexable',robots)
   if norm_url(pub.get('canonical'))!=norm_url(d.get('url')):block('canonical_not_self',str(pub.get('canonical') or ''))
   if not pub.get('in_product_sitemap'):block('product_sitemap_missing')
  else:
   if 'noindex' not in robots:block('public_noindex_missing',robots)
   if pub.get('in_product_sitemap'):block('noindex_product_in_sitemap')
   if not str(pub.get('canonical') or '').strip():warn('noindex_canonical_review','canonical absent; deliberate review required')
  if int(pub.get('product_schema_count') or 0)!=1:block('product_schema_count_invalid',str(pub.get('product_schema_count')))
 return blockers,warnings


def self_test():
 base={'exists':True,'status':'draft','title':'محصول تست','slug':'product-test','type':'variable','sku':'GR-T-001','price':'','stock_status':'instock','stock_quantity':None,'manage_stock':False,'description_words':80,'short_description_words':18,'featured_image':10,'images':[{'id':10,'alt':'نمای محصول تست'}],'categories':[{'id':1,'name':'تست'}],'attributes':[{'variation':True}],'variations':[{'id':101,'sku':'GR-T-001-BLK-M','price':'100','stock_status':'instock','stock_quantity':None,'manage_stock':False,'attributes':{'pa_color':'black','pa_size':'m'}}],'duplicate_titles':[]}
 b,w=evaluate_product(base,'index','prepublish')
 assert not b,(b,w)
 bad=json.loads(json.dumps(base,ensure_ascii=False));bad['sku']='';bad['short_description_words']=0;bad['variations'][0]['price']=''
 b,_=evaluate_product(bad,'index','prepublish');codes={x['code'] for x in b}
 assert {'parent_sku_missing','short_description_missing','variation_price_missing'}<=codes,codes
 post=json.loads(json.dumps(base,ensure_ascii=False));post.update({'status':'publish','url':'https://gramiss.ir/product/product-test/','public':{'status':200,'title':'خرید محصول تست - Gramiss','description':'توضیح تست','canonical':'https://gramiss.ir/product/product-test/','robots':'index, follow','product_schema_count':1,'in_product_sitemap':True}})
 b,_=evaluate_product(post,'index','postpublish');assert not b,b
 post['public']['product_schema_count']=2;b,_=evaluate_product(post,'index','postpublish');assert any(x['code']=='product_schema_count_invalid' for x in b),b
 print('PASS PRODUCT GATE SELF TEST V1')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--product-id',type=int);ap.add_argument('--index-intent',choices=['index','noindex'],default='index');ap.add_argument('--mode',choices=['prepublish','postpublish'],default='prepublish');ap.add_argument('--report-only',action='store_true');ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
 if args.self_test:self_test();return
 pid=args.product_id or int(os.environ.get('PRODUCT_ID','0') or 0)
 if pid<=0:raise SystemExit('PRODUCT_ID required')
 host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
 def api(fn,p,post=False):
  u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();last=None
  for n in range(4):
   try:
    r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}')
    if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
    with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
    q=o.get('result') if isinstance(o.get('result'),dict) else o
    if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
    return q.get('data')
   except Exception as e:last=e;time.sleep(n+1)
  raise last
 def theme(rel):
  d,n=rel.rsplit('/',1) if '/' in rel else ('',rel);x=api('get_file_content',{'dir':root if not d else root+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
  if isinstance(x,dict):
   for k in ('content','file_content','data'):
    if isinstance(x.get(k),str):return x[k]
  return x if isinstance(x,str) else ''
 def save(n,c):return api('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
 def safe(u):
  p=urllib.parse.urlsplit(u);return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
 def get(u,timeout=150):
  u=safe(u);last=None
  for n in range(4):
   try:
    r=urllib.request.Request(u,headers={'User-Agent':'GramissProductGateV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(r,context=ctx,timeout=timeout) as z:return z.status,z.read(),z.geturl()
   except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
   except Exception as e:last=e;time.sleep(n+1)
  raise last
 def meta(raw,pat):
  t=raw.decode('utf-8','replace').split('</head>',1)[0];m=re.search(pat,t,re.I|re.S);return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
 protected={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_PRE',json.dumps(protected,sort_keys=True))
 for p,h in PROTECTED.items():
  if protected[p]!=h:raise SystemExit('ABORT protected drift '+p)
 if healthy and protected['front-page.php']!=healthy:raise SystemExit('ABORT healthy home drift')
 nonce=hashlib.sha256((str(time.time())+str(pid)+protected['front-page.php']).encode()).hexdigest()[:14];name='gramiss-product-gate-'+nonce+'.php'
 php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$id=(int)($_GET['id']??0);$p=get_post($id);$o=['exists'=>false,'id'=>$id];
if($p && $p->post_type==='product'){$wc=wc_get_product($id);$o['exists']=true;$o['status']=$p->post_status;$o['title']=$p->post_title;$o['slug']=$p->post_name;$o['url']=$p->post_status==='publish'?get_permalink($id):null;$o['type']=$wc?$wc->get_type():'';$o['sku']=$wc?$wc->get_sku():'';$o['price']=$wc?$wc->get_price():'';$o['stock_status']=$wc?$wc->get_stock_status():'';$o['stock_quantity']=$wc?$wc->get_stock_quantity():null;$o['manage_stock']=$wc?$wc->get_manage_stock():false;$dw=trim(wp_strip_all_tags($p->post_content));$sw=trim(wp_strip_all_tags($p->post_excerpt));$o['description_words']=$dw===''?0:count(preg_split('/\s+/u',$dw,-1,PREG_SPLIT_NO_EMPTY));$o['short_description_words']=$sw===''?0:count(preg_split('/\s+/u',$sw,-1,PREG_SPLIT_NO_EMPTY));$o['featured_image']=(int)get_post_thumbnail_id($id);$imgs=[];$ids=[];if($o['featured_image'])$ids[]=$o['featured_image'];if($wc)foreach((array)$wc->get_gallery_image_ids() as $iid)$ids[]=(int)$iid;foreach(array_values(array_unique(array_filter($ids))) as $iid)$imgs[]=['id'=>$iid,'alt'=>(string)get_post_meta($iid,'_wp_attachment_image_alt',true)];$o['images']=$imgs;$cats=wp_get_post_terms($id,'product_cat',['fields'=>'all']);$o['categories']=array_map(fn($t)=>['id'=>(int)$t->term_id,'name'=>$t->name,'slug'=>$t->slug],$cats);$attrs=[];if($wc)foreach($wc->get_attributes() as $a)$attrs[]=['name'=>$a->get_name(),'variation'=>$a->get_variation(),'taxonomy'=>$a->is_taxonomy()];$o['attributes']=$attrs;$vars=[];if($wc && $wc->is_type('variable'))foreach($wc->get_children() as $vid){$v=wc_get_product($vid);if(!$v)continue;$vars[]=['id'=>(int)$vid,'sku'=>$v->get_sku(),'price'=>$v->get_price(),'stock_status'=>$v->get_stock_status(),'stock_quantity'=>$v->get_stock_quantity(),'manage_stock'=>$v->get_manage_stock(),'attributes'=>$v->get_attributes()];}$o['variations']=$vars;$dup=get_posts(['post_type'=>'product','post_status'=>['publish','draft','pending','private'],'numberposts'=>-1,'post__not_in'=>[$id],'s'=>$p->post_title,'fields'=>'ids']);$exact=[];foreach($dup as $did)if(trim(get_the_title($did))===trim($p->post_title))$exact[]=(int)$did;$o['duplicate_titles']=$exact;$o['seo']=['robots'=>get_post_meta($id,'rank_math_robots',true),'title'=>get_post_meta($id,'rank_math_title',true),'description'=>get_post_meta($id,'rank_math_description',true),'canonical'=>get_post_meta($id,'rank_math_canonical_url',true)];}
echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
 save(name,php);s,b,f=get(BASE+'/'+name+'?id='+str(pid)+'&t='+str(int(time.time())),240);print('PROBE',s,f)
 if s!=200:raise SystemExit('product gate probe failed')
 d=json.loads(b.decode('utf-8','replace'))
 if args.mode=='postpublish' and d.get('exists') and d.get('status')=='publish':
  u=d.get('url');st,raw,final=get(u+'?t='+str(int(time.time())),180);title=meta(raw,r'<title[^>]*>(.*?)</title>');desc=meta(raw,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)');canon=meta(raw,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)');robots=meta(raw,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)');txt=raw.decode('utf-8','replace');schemas=len(re.findall(r'"@type"\s*:\s*"Product"',txt,re.I));ss,sb,_=get(BASE+'/product-sitemap.xml?t='+str(int(time.time())),120);locs=[x.replace('&amp;','&') for x in re.findall(r'<loc>(.*?)</loc>',sb.decode('utf-8','replace'),re.I)];d['public']={'status':st,'final_url':final,'title':title,'description':desc,'canonical':canon,'robots':robots,'product_schema_count':schemas,'in_product_sitemap':norm_url(u) in {norm_url(x) for x in locs},'sitemap_http':ss}
 print('PRODUCT_GATE_INPUT',json.dumps({'id':pid,'mode':args.mode,'index_intent':args.index_intent,'status':d.get('status'),'title':d.get('title'),'url':d.get('url')},ensure_ascii=False,separators=(',',':')))
 blockers,warnings=evaluate_product(d,args.index_intent,args.mode);result={'ok':not blockers,'product_id':pid,'mode':args.mode,'index_intent':args.index_intent,'blockers':blockers,'warnings':warnings};print('PRODUCT_GATE_RESULT',json.dumps(result,ensure_ascii=False,separators=(',',':')))
 post={p:hashlib.sha256(theme(p).encode()).hexdigest() for p in PROTECTED};print('PROTECTED_POST',json.dumps(post,sort_keys=True))
 if post!=protected:raise SystemExit('ABORT protected changed during gate')
 if blockers and not args.report_only:raise SystemExit('FAIL PRODUCT PREPUBLISH GATE V1: '+','.join(x['code'] for x in blockers))
 print(('REPORT ONLY ' if args.report_only else 'PASS ')+'PRODUCT PREPUBLISH GATE V1')

if __name__=='__main__':main()
