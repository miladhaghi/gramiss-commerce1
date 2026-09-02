from pathlib import Path
p=Path('.ops/legacy-product-remediation-audit-v6.py')
s=p.read_text(encoding='utf-8')
old="366:'شلوار پارچه‌ای فول‌بگ ریزشی؛ برای این مدل سایزهای M، L، XL، 2XL و 3XL تعریف شده است.'}"
new="366:'شلوار پارچه‌ای فول‌بگ ریزشی؛ برای این مدل سایزهای M، L، XL، 2XL و 3XL تعریف شده است.',\n296:'پیراهن آستین بلند پارچه سیلک هلویی و آبی‌طوسی؛ گزینه‌های رنگ ثبت‌شده آبی آسمانی و نارنجی هستند و سایزهای M، L، XL و 2XL برای این مدل تعریف شده است.',\n307:'پیراهن آستین بلند پارچه سیلک قهوه‌ای و کرم؛ برای این مدل رنگ‌های قهوه‌ای و کرم و سایزهای L، XL و 2XL تعریف شده است.',\n320:'پیراهن آستین بلند پارچه سیلک گرم‌دار؛ برای این مدل سایزهای XL و 2XL تعریف شده است.',\n325:'پیراهن آستین کوتاه کرپ؛ برای این مدل سایزهای M، L، XL و 2XL تعریف شده است.',\n330:'پیراهن لینن آستین کوتاه سرمه‌ای؛ برای این مدل سایزهای M و XL تعریف شده است.'}"
if s.count(old)!=1: raise SystemExit('v7 expected-anchor mismatch')
s=s.replace(old,new)
old_count="if d.get('empty_excerpt')!=22:errs.append('empty_excerpt')"
new_count="if d.get('empty_excerpt')!=17:errs.append('empty_excerpt')"
if s.count(old_count)!=1: raise SystemExit('v7 count-anchor mismatch')
s=s.replace(old_count,new_count)
s=s.replace("PASS LEGACY PRODUCT REMEDIATION AUDIT V6","PASS LEGACY PRODUCT REMEDIATION AUDIT V7")
exec(compile(s,'.ops/legacy-product-remediation-audit-v7.generated.py','exec'),{'__name__':'__main__'})
