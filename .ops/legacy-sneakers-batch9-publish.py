from pathlib import Path
import re
p=Path('.ops/legacy-shirts-batch7-publish.py')
s=p.read_text(encoding='utf-8')
new_targets="""TARGETS={403:{'title':'کتونی طرح ونس سرمه ای','excerpt':'کتونی طرح ونس سرمه‌ای؛ برای این مدل رنگ سرمه‌ای و سایزهای 41 و 42 تعریف شده است.'},425:{'title':'کتونی سبک ونس AMIRI کرم','excerpt':'کتونی سبک ونس AMIRI کرم؛ برای این مدل رنگ کرم و سایزهای 41، 42، 43، 44 و 45 تعریف شده است.'},431:{'title':'کتونی سبک ونس سفید','excerpt':'کتونی سبک ونس سفید؛ برای این مدل رنگ سفید و سایزهای 40، 43 و 45 تعریف شده است.'},435:{'title':'کتونی LVکرم- سفید مستر','excerpt':'کتونی LV کرم-سفید مستر؛ رنگ ثبت‌شده این مدل کرم است و سایزهای 40، 43 و 44 برای آن تعریف شده است.'},439:{'title':'کتونی سبک ونس D&G','excerpt':'کتونی سبک ونس D&G؛ برای این مدل رنگ سفید و سایزهای 40، 41، 44 و 45 تعریف شده است.'}}
def safe"""
s,n=re.subn(r'TARGETS=\{.*?\}\ndef safe',new_targets,s,count=1,flags=re.S)
if n!=1: raise SystemExit('batch9 targets anchor mismatch')
repls={
'GramissLegacyShirtsBatch7/1.0':'GramissLegacySneakersBatch9/1.0',
'gramiss-shirts-b7-':'gramiss-sneakers-b9-',
"if(!in_array('پیراهن',$cats,true))":"if(!in_array('کتونی',$cats,true))",
'PASS LEGACY SHIRTS SHORT DESCRIPTION BATCH 7':'PASS LEGACY SNEAKERS SHORT DESCRIPTION BATCH 9'}
for old,new in repls.items():
 if old not in s: raise SystemExit('batch9 publisher anchor mismatch: '+old)
 s=s.replace(old,new)
exec(compile(s,'.ops/legacy-sneakers-batch9-publish.generated.py','exec'),{'__name__':'__main__'})
