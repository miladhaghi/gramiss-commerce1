from pathlib import Path
import re
p=Path('.ops/legacy-shirts-batch7-publish.py')
s=p.read_text(encoding='utf-8')
new_targets="""TARGETS={347:{'title':'پیراهن آستین کوتاه لینن قهوه ای','excerpt':'پیراهن آستین کوتاه لینن قهوه‌ای؛ برای این مدل سایزهای M و 2XL تعریف شده است.'},350:{'title':'پیراهن سیلک آستین کوتاه آبی','excerpt':'پیراهن سیلک آستین کوتاه آبی؛ برای این مدل سایزهای L، XL و 2XL تعریف شده است.'},355:{'title':'پیراهن آستین بلند ماچایی پارچه سیلک','excerpt':'پیراهن آستین بلند ماچایی پارچه سیلک؛ برای این مدل سایزهای M و L تعریف شده است.'}}
def safe"""
s,n=re.subn(r'TARGETS=\{.*?\}\ndef safe',new_targets,s,count=1,flags=re.S)
if n!=1: raise SystemExit('batch8 targets anchor mismatch')
for old,new in {
'gramiss-shirts-b7-':'gramiss-shirts-b8-',
'GramissLegacyShirtsBatch7/1.0':'GramissLegacyShirtsBatch8/1.0',
'PASS LEGACY SHIRTS SHORT DESCRIPTION BATCH 7':'PASS LEGACY SHIRTS SHORT DESCRIPTION BATCH 8'}.items():
 if old not in s: raise SystemExit('batch8 publisher anchor mismatch: '+old)
 s=s.replace(old,new)
exec(compile(s,'.ops/legacy-shirts-batch8-publish.generated.py','exec'),{'__name__':'__main__'})
