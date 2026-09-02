from pathlib import Path
import re
p=Path('.ops/legacy-shirts-batch7-publish.py')
s=p.read_text(encoding='utf-8')
new_targets="""TARGETS={80:{'title':'کلاه فیت کپ NY','excerpt':'کلاه فیت کپ NY؛ اندازه‌های ثبت‌شده برای این مدل 57.7 و 58.7 سانتی‌متر هستند.'},84:{'title':'کلاه فیت کپ مشکی نارنجی NY','excerpt':'کلاه فیت کپ مشکی نارنجی NY؛ اندازه ثبت‌شده برای این مدل 58.7 سانتی‌متر است.'},87:{'title':'کلاه فیت کپ NY طرح فرشته گل سرخ','excerpt':'کلاه فیت کپ NY طرح فرشته گل سرخ؛ اندازه ثبت‌شده برای این مدل 58.7 سانتی‌متر است.'}}
def safe"""
s,n=re.subn(r'TARGETS=\{.*?\}\ndef safe',new_targets,s,count=1,flags=re.S)
if n!=1: raise SystemExit('batch10 targets anchor mismatch')
repls={
'GramissLegacyShirtsBatch7/1.0':'GramissLegacyHatsBatch10/1.0',
'gramiss-shirts-b7-':'gramiss-hats-b10-',
"if(!in_array('پیراهن',$cats,true))":"if(!in_array('کلاه',$cats,true))",
"if($mode==='apply'&&empty($o['errors']))foreach($targets as $sid=>$cfg){$r=wp_update_post(['ID'=>(int)$sid,'post_excerpt'=>$cfg['excerpt']],true);if(is_wp_error($r))$o['errors'][]='update:'.$sid;}":"if($mode==='apply'&&empty($o['errors'])){global $wpdb;foreach($targets as $sid=>$cfg){$r=$wpdb->update($wpdb->posts,['post_excerpt'=>$cfg['excerpt']],['ID'=>(int)$sid],['%s'],['%d']);if($r===false)$o['errors'][]='update:'.$sid;clean_post_cache((int)$sid);}}",
"if($mode==='rollback')foreach($targets as $sid=>$cfg){$r=wp_update_post(['ID'=>(int)$sid,'post_excerpt'=>array_key_exists($sid,$old)?(string)$old[$sid]:''],true);if(is_wp_error($r))$o['errors'][]='rollback:'.$sid;}":"if($mode==='rollback'){global $wpdb;foreach($targets as $sid=>$cfg){$v=array_key_exists($sid,$old)?(string)$old[$sid]:'';$r=$wpdb->update($wpdb->posts,['post_excerpt'=>$v],['ID'=>(int)$sid],['%s'],['%d']);if($r===false)$o['errors'][]='rollback:'.$sid;clean_post_cache((int)$sid);}}",
'PASS LEGACY SHIRTS SHORT DESCRIPTION BATCH 7':'PASS LEGACY HATS SHORT DESCRIPTION BATCH 10'}
for old,new in repls.items():
 if old not in s: raise SystemExit('batch10 publisher anchor mismatch: '+old)
 s=s.replace(old,new)
# Simple hats have no variations; require their actual WooCommerce product price.
old="if(is_array($robots)&&in_array('noindex',$robots,true))$o['errors'][]='noindex:'.$id;foreach($vars as $v){"
new="if(is_array($robots)&&in_array('noindex',$robots,true))$o['errors'][]='noindex:'.$id;if(trim((string)$wc->get_price())==='')$o['errors'][]='parent_price:'.$id;foreach($vars as $v){"
if s.count(old)!=1: raise SystemExit('batch10 price guard anchor mismatch')
s=s.replace(old,new)
if 'wp_update_post' in s: raise SystemExit('unsafe wp_update_post remains in batch10 generated publisher')
exec(compile(s,'.ops/legacy-hats-batch10-publish.generated.py','exec'),{'__name__':'__main__'})
