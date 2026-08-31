import hashlib,html,json,os,re,ssl,urllib.parse,urllib.request,urllib.error
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p);r=urllib.request.Request(u+'?'+d);r.add_header('Authorization',f'cpanel {user}:{token}')
 with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
 q=o.get('result') if isinstance(o.get('result'),dict) else o
 if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
 return q.get('data')
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def get(u):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissContentRenderAudit/1.0','Cache-Control':'no-cache','Pragma':'no-cache'});op=urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
 try:
  with op.open(req,timeout=120) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def one(t,p):
 m=re.search(p,t,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def audit_page(label,u):
 s,b,f,h=get(u);t=b.decode('utf-8','replace');head=t.split('</head>',1)[0];h1=re.findall(r'<h1[^>]*>(.*?)</h1>',t,re.I|re.S);h2=re.findall(r'<h2[^>]*>(.*?)</h2>',t,re.I|re.S);clean=lambda x:re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',html.unescape(x))).strip();o={'status':s,'final':f,'title':one(head,r'<title[^>]*>(.*?)</title>'),'description':one(head,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':one(head,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':one(head,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)'),'h1':[clean(x) for x in h1[:3]],'h2':[clean(x) for x in h2[:8]],'article_tags':len(re.findall(r'<article\b',t,re.I)),'body_class':one(t,r'<body[^>]+class=["\']([^"\']+)')};print('PAGE',label,json.dumps(o,ensure_ascii=False));return o
front=read_theme('front-page.php');sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
for f in ['home.php','single.php','category.php']:
 c=read_theme(f);print('THEME_FILE',f,'BYTES',len(c),'SHA',hashlib.sha256(c.encode()).hexdigest());print('---'+f+' START---');print(c);print('---'+f+' END---')
for label,u in [('blog','https://gramiss.ir/%D9%88%D8%A8%D9%84%D8%A7%DA%AF/'),('style','https://gramiss.ir/category/style-guide/'),('buying','https://gramiss.ir/category/buying-guide/'),('fit','https://gramiss.ir/category/fit-size-guide/'),('fabric','https://gramiss.ir/category/fabric-care/')]:audit_page(label,u)
for label,u in [('post_sitemap','https://gramiss.ir/post-sitemap.xml'),('category_sitemap','https://gramiss.ir/category-sitemap.xml')]:
 s,b,f,h=get(u);t=b.decode('utf-8','replace');locs=re.findall(r'<loc>(.*?)</loc>',t,re.I);print('XML',label,'STATUS',s,'LOCS',locs);print('XML_RAW',label,t[:8000])
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('Home changed')
print('PASS CONTENT RENDER AUDIT V1');print('HOME SHA PRESERVED',sha)
