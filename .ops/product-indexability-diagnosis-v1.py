import hashlib,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
HOST=os.environ['CPANEL_HOST'];USER=os.environ['CPANEL_USER'];TOKEN=os.environ['CPANEL_TOKEN'];ROOT=os.environ['THEME_ROOT'].strip('/');HEALTHY=os.environ.get('HEALTHY_HOME_SHA','');CTX=ssl._create_unverified_context();BASE='https://gramiss.ir'
def safe(u):
 p=urllib.parse.urlsplit(u);return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(urllib.parse.unquote(p.path),safe='/%:@'),urllib.parse.quote(urllib.parse.unquote(p.query),safe='=&%:@,+'),p.fragment))
def api(fn,p,post=False):
 u=f'https://{HOST}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {USER}:{TOKEN}')
 if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
 with urllib.request.urlopen(r,context=CTX,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
 q=o.get('result') if isinstance(o.get('result'),dict) else o
 if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
 return q.get('data')
def theme(rel):
 d,n=rel.rsplit('/',1) if '/' in rel else ('',rel);x=api('get_file_content',{'dir':ROOT if not d else ROOT+'/'+d,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(x,dict):
  for k in ('content','file_content','data'):
   if isinstance(x.get(k),str):return x[k]
 return x if isinstance(x,str) else ''
def save(n,c):return api('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u):
 u=safe(u);r=urllib.request.Request(u,headers={'User-Agent':'GramissProductIndexDiagnosis/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 try:
  with urllib.request.urlopen(r,context=CTX,timeout=120) as z:return z.status,z.read(),z.geturl()
 except urllib.error.HTTPError as e:return e.code,e.read(),e.geturl()
def val(t,p):
 m=re.search(p,t,re.I|re.S);return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def norm(u):return urllib.parse.unquote(u).split('?',1)[0].rstrip('/')+'/'
def sm():
 s,b,_=get(BASE+'/product-sitemap.xml?t='+str(int(time.time())));return s,[x.replace('&amp;','&') for x in re.findall(r'<loc>(.*?)</loc>',b.decode('utf-8','replace'),re.I)]
front=hashlib.sha256(theme('front-page.php').encode()).hexdigest();print('HOME',front)
if HEALTHY and front!=HEALTHY:raise SystemExit('ABORT home drift')
nonce=hashlib.sha256((str(time.time())+front).encode()).hexdigest()[:12];name='gramiss-product-index-diagnosis-'+nonce+'.php'
php=r'''<?php header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$o=[];$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);foreach($ids as $id){$p=get_post($id);$o[]=['id'=>(int)$id,'title'=>$p->post_title,'url'=>get_permalink($id),'excerpt_words'=>count(preg_split('/\s+/u',trim(wp_strip_all_tags($p->post_excerpt)),-1,PREG_SPLIT_NO_EMPTY)),'seo'=>['title'=>get_post_meta($id,'rank_math_title',true),'description'=>get_post_meta($id,'rank_math_description',true),'canonical'=>get_post_meta($id,'rank_math_canonical_url',true),'robots'=>get_post_meta($id,'rank_math_robots',true),'rich'=>get_post_meta($id,'rank_math_rich_snippet',true)]];}echo wp_json_encode($o,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save(name,php);s,b,_=get(BASE+'/'+name+'?t='+str(int(time.time())));rows=json.loads(b.decode('utf-8','replace'));ss,surls=sm();sset={norm(x) for x in surls};pub={norm(r['url']):r for r in rows};print('COUNTS',len(rows),len(surls));print('PUBLISHED_ONLY',json.dumps([{'id':r['id'],'title':r['title'],'url':r['url'],'seo':r['seo']} for u,r in pub.items() if u not in sset],ensure_ascii=False));print('SITEMAP_ONLY',json.dumps([u for u in surls if norm(u) not in pub],ensure_ascii=False))
summary={'public_title_blank':0,'public_description_blank':0,'canonical_bad':0,'noindex':0,'schema_bad':0}
for r in rows:
 st,raw,final=get(r['url']+'?t='+str(int(time.time())));txt=raw.decode('utf-8','replace');h=txt.split('</head>',1)[0];title=val(h,r'<title[^>]*>(.*?)</title>');desc=val(h,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)');canon=val(h,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)');robots=val(h,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)');schemas=len(re.findall(r'"@type"\s*:\s*"Product"',txt,re.I));summary['public_title_blank']+=0 if title else 1;summary['public_description_blank']+=0 if desc else 1;summary['canonical_bad']+=0 if norm(canon)==norm(r['url']) else 1;summary['noindex']+=1 if 'noindex' in robots.lower() else 0;summary['schema_bad']+=0 if schemas==1 else 1
 if r['id'] in (62,68) or not desc or 'noindex' in robots.lower():print('SEO_DIAG',json.dumps({'id':r['id'],'title':r['title'],'excerpt_words':r['excerpt_words'],'stored':r['seo'],'public':{'status':st,'title':title,'description':desc,'canonical':canon,'robots':robots,'product_schema_count':schemas}},ensure_ascii=False,separators=(',',':')))
print('SEO_PUBLIC_SUMMARY',json.dumps(summary,sort_keys=True));print('PASS PRODUCT INDEXABILITY DIAGNOSIS V1')