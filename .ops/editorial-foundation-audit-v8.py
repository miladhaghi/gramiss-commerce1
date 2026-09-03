#!/usr/bin/env python3
"""Gramiss Editorial Foundation Audit V8.

V7 remains the historical 2026-09-02 audit. V8 reuses its verified editorial
logic and updates only the product/product-category sitemap invariants that were
legitimately changed by owner-authorized catalogue/indexability work on
2026-09-03. Exact guards fail closed if V7 itself changes unexpectedly.
"""
from pathlib import Path

base = Path(__file__).with_name('editorial-foundation-audit-v7.py')
source = base.read_text(encoding='utf-8')

replacements = {
    "PRODUCT_SHA='70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3'":
        "PRODUCT_SHA='05e81da96bcc57927bf8d2b467866a1236e9ea0307e1c3902519136294e805bf'",
    "PCAT_SHA='75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4'":
        "PCAT_SHA='e56e71dfe5a97014bb645c3726b916c1883c87eb2e21b5eab8cc4598942c13bf'",
    "len(prod_u)!=47": "len(prod_u)!=49",
    "len(pc_u)!=20": "len(pc_u)!=21",
}

for old, new in replacements.items():
    count = source.count(old)
    if count != 1:
        raise SystemExit(f'REFUSE editorial audit V7 drift: expected one match for {old!r}, found {count}')
    source = source.replace(old, new, 1)

print('GRAMISS_EDITORIAL_AUDIT_V8_BASELINE product=49 product_cat=21')
exec(compile(source, str(base), 'exec'), {'__name__': '__main__'})
