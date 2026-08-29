import hashlib,json,os,ssl,time,urllib.error,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,params,post=False):
 url=f'https://{host}:2083/execute/Fileman/{fn}';data=urllib.parse.urlencode(params).encode();req=urllib.request.Request(url if post else url+'?'+data.decode(),data=data if post else None,method='POST' if post else 'GET');req.add_header('Authorization',f'cpanel {user}:{token}');
 if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(req,context=ctx,timeout=90) as r:obj=json.loads(r.read().decode('utf-8','replace'))
 result=obj.get('result') if isinstance(obj.get('result'),dict) else obj
 if not isinstance(result,dict) or result.get('status')!=1:raise RuntimeError(str(result))
 return result.get('data')
def read_theme(rel):
 parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel);directory=root if not parent else root+'/'+parent;d=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'});
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(name,content):return call('save_file_content',{'dir':'public_html','file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'GramissRankMathDirectAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});
 try:
  with urllib.request.urlopen(req,context=ctx,timeout=120) as r:return r.status,r.read(),r.geturl(),dict(r.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),url,dict(e.headers)
front=read_theme('front-page.php');fsha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',fsha)
if healthy and fsha!=healthy:raise SystemExit('ABORT Home mismatch')
stamp=str(int(time.time()));probe='gramiss-rm-direct-'+hashlib.sha256((stamp+fsha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$s=(array)get_option('rank-math-options-sitemap',[]);$t=(array)get_option('rank-math-options-titles',[]);$g=(array)get_option('rank-math-options-general',[]);$sel=[];foreach($s as $k=>$v){if(stripos($k,'product')!==false||stripos($k,'page')!==false||stripos($k,'tax')!==false||stripos($k,'author')!==false||stripos($k,'exclude')!==false)$sel[$k]=$v;}$tsel=[];foreach($t as $k=>$v){if(stripos($k,'product_cat')!==false||stripos($k,'product_tag')!==false||stripos($k,'search')!==false||stripos($k,'author')!==false)$tsel[$k]=$v;}$gsel=[];foreach($g as $k=>$v){if(stripos($k,'facebook')!==false||stripos($k,'twitter')!==false||stripos($k,'opengraph')!==false||stripos($k,'head')!==false||stripos($k,'social')!==false)$gsel[$k]=$v;}$pages=[];foreach(['cart'=>'woocommerce_cart_page_id','checkout'=>'woocommerce_checkout_page_id','account'=>'woocommerce_myaccount_page_id','shop'=>'woocommerce_shop_page_id'] as $n=>$o){$id=(int)get_option($o);$pages[$n]=['id'=>$id,'url'=>get_permalink($id),'robots'=>get_post_meta($id,'rank_math_robots',true),'title'=>get_post_meta($id,'rank_math_title',true),'description'=>get_post_meta($id,'rank_math_description',true)];}echo wp_json_encode(['sitemap_selected'=>$sel,'sitemap_all_keys'=>array_keys($s),'title_selected'=>$tsel,'general_social'=>$gsel,'pages'=>$pages],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);'''
save(probe,php);st,b,f,h=get('https://gramiss.ir/'+probe+'?t='+stamp);print('PROBE',st,b.decode('utf-8','replace')[:12000])
urls=['https://gramiss.ir/?sitemap=1','https://gramiss.ir/index.php?sitemap=1','https://gramiss.ir/sitemap.xml','https://gramiss.ir/sitemap_index.xml','https://gramiss.ir/?sitemap=product','https://gramiss.ir/?sitemap=product_cat']
for url in urls:
 st,b,f,h=get(url);print('DIRECT',url,'STATUS',st,'FINAL',f,'BYTES',len(b),'CTYPE',h.get('Content-Type',''),'START',b[:240].decode('utf-8','replace').replace('\n',' '))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=fsha:raise SystemExit('ABORT Home changed')
print('END READ ONLY DIRECT SITEMAP TEST')