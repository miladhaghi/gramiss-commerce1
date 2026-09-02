from pathlib import Path
p=Path('.ops/legacy-shirts-batch7-facts.py')
s=p.read_text(encoding='utf-8')
repls={
'TARGETS=[296,307,320,325,330]':'TARGETS=[347,350,355]',
'gramiss-shirts-b7-facts-':'gramiss-shirts-b8-facts-',
'GramissShirtsBatch7Facts/1.0':'GramissShirtsBatch8Facts/1.0',
'PASS LEGACY SHIRTS BATCH 7 FACTS':'PASS LEGACY SHIRTS BATCH 8 FACTS'}
for old,new in repls.items():
 if s.count(old)!=1: raise SystemExit('batch8 anchor mismatch: '+old)
 s=s.replace(old,new)
exec(compile(s,'.ops/legacy-shirts-batch8-facts.generated.py','exec'),{'__name__':'__main__'})
