#!/usr/bin/env python3
"""Gramiss Category Money Page Audit V2.

V1 remains the historical 2026-09-02 audit. V2 deliberately reuses that audited
logic while changing only the five verified inventory invariants established on
2026-09-03 after products 62/68 became indexable and snapback became a complete
money page. Exact-match guards make future V1 drift fail closed.
"""
from pathlib import Path

base = Path(__file__).with_name('category-money-page-audit-v1.py')
source = base.read_text(encoding='utf-8')

replacements = {
    "PRODUCT_SHA = '70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'":
        "PRODUCT_SHA = '05e81da96bcc57927bf8d2b467866a1236e9ea0307e1c3902519136294e805bf'",
    "PCAT_SHA = '75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'":
        "PCAT_SHA = 'e56e71dfe5a97014bb645c3726b916c1883c87eb2e21b5eab8cc4598942c13bf'",
    "len(product_urls) != 47": "len(product_urls) != 49",
    "len(pcat_urls) != 20": "len(pcat_urls) != 21",
    "len(findings) != 20": "len(findings) != 21",
}

for old, new in replacements.items():
    count = source.count(old)
    if count != 1:
        raise SystemExit(f'REFUSE category audit V1 drift: expected one match for {old!r}, found {count}')
    source = source.replace(old, new, 1)

print('GRAMISS_CATEGORY_AUDIT_V2_BASELINE product=49 product_cat=21')
exec(compile(source, str(base), 'exec'), {'__name__': '__main__'})
