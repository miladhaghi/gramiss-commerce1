from pathlib import Path
p=Path('.ops/legacy-shirts-batch7-facts.py')
s=p.read_text(encoding='utf-8')
repls={
'TARGETS=[296,307,320,325,330]':'TARGETS=[403,425,431,435,439]',
'gramiss-shirts-b7-facts-':'gramiss-sneakers-b9-facts-',
'GramissShirtsBatch7Facts/1.0':'GramissSneakersBatch9Facts/1.0',
"if(!in_array('پیراهن',$cats,true))":"if(!in_array('کتونی',$cats,true))",
'PASS LEGACY SHIRTS BATCH 7 FACTS':'PASS LEGACY SNEAKERS BATCH 9 FACTS'}
for old,new in repls.items():
 if s.count(old)!=1: raise SystemExit('batch9 facts anchor mismatch: '+old)
 s=s.replace(old,new)
exec(compile(s,'.ops/legacy-sneakers-batch9-facts.generated.py','exec'),{'__name__':'__main__'})
