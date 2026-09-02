from pathlib import Path
p=Path('.ops/legacy-shirts-batch7-facts.py')
s=p.read_text(encoding='utf-8')
repls={
'TARGETS=[296,307,320,325,330]':'TARGETS=[80,84,87]',
'gramiss-shirts-b7-facts-':'gramiss-hats-b10-facts-',
'GramissShirtsBatch7Facts/1.0':'GramissHatsBatch10Facts/1.0',
"if(!in_array('پیراهن',$cats,true))":"if(!in_array('کلاه',$cats,true))",
'PASS LEGACY SHIRTS BATCH 7 FACTS':'PASS LEGACY HATS BATCH 10 FACTS'}
for old,new in repls.items():
 if s.count(old)!=1: raise SystemExit('batch10 facts anchor mismatch: '+old)
 s=s.replace(old,new)
# For simple hats, require an actual product price even though parent SKU is intentionally not a blocker.
old="if($p->post_status!=='publish')$o['errors'][]='status:'.$id;if(trim((string)$p->post_excerpt)!=='')$o['errors'][]='excerpt:'.$id;"
new="if($p->post_status!=='publish')$o['errors'][]='status:'.$id;if(trim((string)$p->post_excerpt)!=='')$o['errors'][]='excerpt:'.$id;if(trim((string)$wc->get_price())==='')$o['errors'][]='parent_price:'.$id;"
if s.count(old)!=1: raise SystemExit('batch10 price guard anchor mismatch')
s=s.replace(old,new)
exec(compile(s,'.ops/legacy-hats-batch10-facts.generated.py','exec'),{'__name__':'__main__'})
