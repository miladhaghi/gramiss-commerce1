import hashlib,json,os,re,ssl,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p);r=urllib.request.Request(u+'?'+d);r.add_header('Authorization',f'cpanel {user}:{token}')
 with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
 q=o.get('result') if isinstance(o.get('result'),dict) else o
 if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
 return q.get('data')
def read(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
front=read('front-page.php');sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
for f in ['index.php','page.php','footer.php']:
 c=read(f);print('\n===== '+f+' '+str(len(c))+' =====\n'+c)
style=read('style.css');print('\n===== style.css bytes '+str(len(style))+' first 8000 =====\n'+style[:8000])
fn=read('functions.php').splitlines();print('\n===== functions.php relevant =====')
for i,line in enumerate(fn,1):
 if re.search(r'enqueue|register_nav|theme_support|body_class|wp_head|wp_footer|template|stylesheet',line,re.I):print(f'{i}: {line}')
h=read('header.php').splitlines();print('\n===== header.php structural =====')
for i,line in enumerate(h,1):
 if re.search(r'<body|<header|</header>|<main|site-header|g1-|gramiss|wp_head|body_class',line,re.I):print(f'{i}: {line}')
print('END READ ONLY EDITORIAL THEME INSPECT V1');print('HOME SHA PRESERVED',sha)