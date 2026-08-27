import hashlib, json, os, ssl, time, urllib.parse, urllib.request
from pathlib import Path

host=os.environ['CPANEL_HOST']; user=os.environ['CPANEL_USER']; token=os.environ['CPANEL_TOKEN']
theme_root=os.environ['THEME_ROOT'].strip('/'); healthy=os.environ.get('HEALTHY_HOME_SHA','')
site_root=theme_root.split('/wp-content/themes/')[0]
plugin_root=site_root+'/wp-content/plugins/gramiss-card-transfer'
ctx=ssl._create_unverified_context(); stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime())

def call(fn,params,post=False):
    url=f'https://{host}:2083/execute/Fileman/{fn}'; data=urllib.parse.urlencode(params).encode(); last=None
    for attempt in range(1,5):
        try:
            req=urllib.request.Request(url if post else url+'?'+data.decode(),data=data if post else None,method='POST' if post else 'GET')
            req.add_header('Authorization',f'cpanel {user}:{token}')
            if post:req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req,context=ctx,timeout=90) as r: obj=json.loads(r.read().decode('utf-8','replace'))
            result=obj.get('result') if isinstance(obj.get('result'),dict) else obj
            if not isinstance(result,dict) or result.get('status')!=1: raise RuntimeError(str(result))
            return result.get('data')
        except Exception as exc:
            last=exc; print(f'Attempt {attempt}/4 {fn}: {exc}')
            if attempt<4: time.sleep(attempt*2)
    raise last

def read_file(directory,name):
    data=call('get_file_content',{'dir':directory,'file':name,'from_charset':'_DETECT_','to_charset':'utf-8'})
    if isinstance(data,dict):
        for key in ('content','file_content','data'):
            if isinstance(data.get(key),str): return data[key]
    if isinstance(data,str): return data
    raise RuntimeError('Cannot read '+directory+'/'+name)

def save_file(directory,name,content):
    call('save_file_content',{'dir':directory,'file':name,'content':content,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)

def public_get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'GramissCardTransfer/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(req,context=ctx,timeout=90) as r: return r.status,r.read(),r.geturl()

front=read_file(theme_root,'front-page.php'); front_sha=hashlib.sha256(front.encode()).hexdigest(); print('LIVE_HOME_SHA',front_sha)
if healthy and front_sha!=healthy: raise SystemExit('ABORT: Home baseline mismatch; nothing changed')

src=Path('deploy/card-transfer-gateway-v1')
files={
    'gramiss-card-transfer.php':(src/'gramiss-card-transfer.php').read_text(encoding='utf-8'),
    'assets/card-transfer.css':(src/'assets/card-transfer.css').read_text(encoding='utf-8'),
    'assets/card-transfer.js':(src/'assets/card-transfer.js').read_text(encoding='utf-8'),
}
if 'Plugin Name: Gramiss Card Transfer' not in files['gramiss-card-transfer.php'] or 'GRAMISS_CARD_TRANSFER_V1' not in files['assets/card-transfer.css'] or 'GRAMISS_CARD_TRANSFER_V1' not in files['assets/card-transfer.js']:
    raise SystemExit('ABORT: candidate plugin assets invalid')

# This cPanel Fileman build has no mkdir endpoint. Create the plugin tree through a one-time PHP file in WordPress root.
mkdir_probe='gramiss-card-transfer-mkdir-'+stamp+'.php'
mkdir_php=r'''<?php
$dir=__DIR__.'/wp-content/plugins/gramiss-card-transfer/assets';
$ok=is_dir($dir) || @mkdir($dir,0755,true);
header('Content-Type: text/plain; charset=utf-8');
echo ($ok && is_dir($dir)) ? 'OK' : 'FAIL';
@unlink(__FILE__);
'''
save_file(site_root,mkdir_probe,mkdir_php)
status,body,_=public_get('https://gramiss.ir/'+mkdir_probe+'?t='+str(int(time.time())))
if status!=200 or body.strip()!=b'OK': raise SystemExit('ABORT: could not create plugin directory; nothing written')
print('PASS PLUGIN DIRECTORY READY')

backups={}
for rel in files:
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=plugin_root if not parent else plugin_root+'/'+parent
    try:
        old=read_file(directory,name); backups[rel]=old
        save_file(directory,name+'.bak-'+stamp,old)
    except Exception:
        backups[rel]=None

def rollback(reason):
    for rel,old in backups.items():
        if old is None: continue
        parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=plugin_root if not parent else plugin_root+'/'+parent
        try: save_file(directory,name,old)
        except Exception as exc: print('ROLLBACK WRITE ERROR',rel,exc)
    raise SystemExit('ROLLED BACK: '+reason)

for rel,content in files.items():
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=plugin_root if not parent else plugin_root+'/'+parent
    save_file(directory,name,content)

for rel,content in files.items():
    parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel); directory=plugin_root if not parent else plugin_root+'/'+parent
    if read_file(directory,name)!=content: rollback('plugin write mismatch '+rel)
if hashlib.sha256(read_file(theme_root,'front-page.php').encode()).hexdigest()!=front_sha: rollback('Home changed during plugin deploy')

probe='gramiss-card-transfer-enable-'+stamp+'.php'
probe_php=r'''<?php
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';
$plugin='gramiss-card-transfer/gramiss-card-transfer.php';
if (!is_plugin_active($plugin)) {
  $result=activate_plugin($plugin);
  if (is_wp_error($result)) { http_response_code(500); echo json_encode(array('ok'=>false,'error'=>$result->get_error_message())); @unlink(__FILE__); exit; }
}
$registered=false;
if (function_exists('WC') && WC() && WC()->payment_gateways()) {
  $gateways=WC()->payment_gateways()->payment_gateways();
  $registered=isset($gateways['gramiss_card_transfer']);
}
$settings=get_option('woocommerce_gramiss_card_transfer_settings',array());
header('Content-Type: application/json; charset=utf-8');
echo wp_json_encode(array('ok'=>is_plugin_active($plugin),'registered'=>$registered,'enabled'=>isset($settings['enabled'])?$settings['enabled']:null,'configured'=>!empty($settings['card_number'])&&!empty($settings['card_holder'])));
@unlink(__FILE__);
'''
save_file(site_root,probe,probe_php)
try:
    status,body,_=public_get('https://gramiss.ir/'+probe+'?t='+str(int(time.time())))
    text=body.decode('utf-8','replace'); print('ACTIVATION',status,text)
    data=json.loads(text)
    if status!=200 or not data.get('ok') or not data.get('registered'): rollback('plugin activation/registration failed')
except Exception as exc: rollback('activation probe failed '+str(exc))

purge='gramiss-purge-card-transfer-'+stamp+'.php'
purge_php="<?php define('WP_USE_THEMES',false); require __DIR__.'/wp-load.php'; if(function_exists('do_action')){do_action('litespeed_purge_all');} echo 'OK'; @unlink(__FILE__);"
save_file(site_root,purge,purge_php)
try:
    status,body,_=public_get('https://gramiss.ir/'+purge+'?t='+str(int(time.time()))); print('PURGE',status,body.decode('utf-8','replace')[:80])
except Exception as exc: print('PURGE WARNING',exc)

for path,marker in (
    ('wp-content/plugins/gramiss-card-transfer/assets/card-transfer.css','GRAMISS_CARD_TRANSFER_V1'),
    ('wp-content/plugins/gramiss-card-transfer/assets/card-transfer.js','GRAMISS_CARD_TRANSFER_V1'),
):
    status,body,_=public_get('https://gramiss.ir/'+path+'?v='+stamp)
    ok=status==200 and marker.encode() in body
    print(('PASS' if ok else 'FAIL'),path,status,len(body))
    if not ok: rollback('public asset failed '+path)

status,body,_=public_get('https://gramiss.ir/?card_transfer_verify='+str(int(time.time())))
html=body.decode('utf-8','replace')
if status!=200 or 'g1-floating-hero' not in html or 'data-g1-looks' not in html: rollback('Home public verify failed')
print('PASS HOME PRESERVED')
print('LIVE GRAMISS CARD TRANSFER GATEWAY V1 DEPLOYED')
