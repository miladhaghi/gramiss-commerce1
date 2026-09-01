from pathlib import Path
p=Path('.ops/legacy-product-remediation-audit-v5.py')
s=p.read_text(encoding='utf-8')
old="293:'شلوار جین کارگو زاپ؛ برای این مدل سایزهای M و XL تعریف شده است.'}"
new="293:'شلوار جین کارگو زاپ؛ برای این مدل سایزهای M و XL تعریف شده است.',\n359:'شلوار پارچه‌ای بگ ریزشی؛ برای این مدل سایزهای M و L تعریف شده است.',\n366:'شلوار پارچه‌ای فول‌بگ ریزشی؛ برای این مدل سایزهای M، L، XL، 2XL و 3XL تعریف شده است.'}"
if s.count(old)!=1: raise SystemExit('v6 expected-anchor mismatch')
s=s.replace(old,new)
old_count="if d.get('empty_excerpt')!=24:errs.append('empty_excerpt')"
new_count="if d.get('empty_excerpt')!=22:errs.append('empty_excerpt')"
if s.count(old_count)!=1: raise SystemExit('v6 count-anchor mismatch')
s=s.replace(old_count,new_count)
s=s.replace("PASS LEGACY PRODUCT REMEDIATION AUDIT V5","PASS LEGACY PRODUCT REMEDIATION AUDIT V6")
exec(compile(s,'.ops/legacy-product-remediation-audit-v6.generated.py','exec'),{'__name__':'__main__'})