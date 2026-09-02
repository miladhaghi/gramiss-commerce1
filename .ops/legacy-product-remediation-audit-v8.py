from pathlib import Path
p=Path('.ops/legacy-product-remediation-audit-v5.py')
s=p.read_text(encoding='utf-8')
old="293:'شلوار جین کارگو زاپ؛ برای این مدل سایزهای M و XL تعریف شده است.'}"
new="""293:'شلوار جین کارگو زاپ؛ برای این مدل سایزهای M و XL تعریف شده است.',
359:'شلوار پارچه‌ای بگ ریزشی؛ برای این مدل سایزهای M و L تعریف شده است.',
366:'شلوار پارچه‌ای فول‌بگ ریزشی؛ برای این مدل سایزهای M، L، XL، 2XL و 3XL تعریف شده است.',
296:'پیراهن آستین بلند پارچه سیلک هلویی و آبی‌طوسی؛ گزینه‌های رنگ ثبت‌شده آبی آسمانی و نارنجی هستند و سایزهای M، L، XL و 2XL برای این مدل تعریف شده است.',
307:'پیراهن آستین بلند پارچه سیلک قهوه‌ای و کرم؛ برای این مدل رنگ‌های قهوه‌ای و کرم و سایزهای L، XL و 2XL تعریف شده است.',
320:'پیراهن آستین بلند پارچه سیلک گرم‌دار؛ برای این مدل سایزهای XL و 2XL تعریف شده است.',
325:'پیراهن آستین کوتاه کرپ؛ برای این مدل سایزهای M، L، XL و 2XL تعریف شده است.',
330:'پیراهن لینن آستین کوتاه سرمه‌ای؛ برای این مدل سایزهای M و XL تعریف شده است.',
347:'پیراهن آستین کوتاه لینن قهوه‌ای؛ برای این مدل سایزهای M و 2XL تعریف شده است.',
350:'پیراهن سیلک آستین کوتاه آبی؛ برای این مدل سایزهای L، XL و 2XL تعریف شده است.',
355:'پیراهن آستین بلند ماچایی پارچه سیلک؛ برای این مدل سایزهای M و L تعریف شده است.'}"""
if s.count(old)!=1: raise SystemExit('v8 expected-anchor mismatch')
s=s.replace(old,new)
old_count="if d.get('empty_excerpt')!=24:errs.append('empty_excerpt')"
new_count="if d.get('empty_excerpt')!=14:errs.append('empty_excerpt')"
if s.count(old_count)!=1: raise SystemExit('v8 count-anchor mismatch')
s=s.replace(old_count,new_count)
s=s.replace("GramissLegacyRemediationAuditV5/1.0","GramissLegacyRemediationAuditV8/1.0")
s=s.replace("gramiss-remediation-audit-v5-","gramiss-remediation-audit-v8-")
s=s.replace("PASS LEGACY PRODUCT REMEDIATION AUDIT V5","PASS LEGACY PRODUCT REMEDIATION AUDIT V8")
exec(compile(s,'.ops/legacy-product-remediation-audit-v8.generated.py','exec'),{'__name__':'__main__'})
