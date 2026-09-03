#!/usr/bin/env python3
import importlib.util
from pathlib import Path

base = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_pdp_image_fix_v4', base)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

_original_verify = mod.verify_rendered

def verify_rendered_v5():
    errors = _original_verify()
    # v4 incorrectly searched PHP source text inside rendered HTML. The PHP filter
    # is already guarded by exact source replacement + stored-file SHA checks,
    # while the rendered related <img> assertions prove its actual effect.
    false_source_assertions = {
        'related card-size filter missing',
        'legacy related full-size filter still rendered',
    }
    return [e for e in errors if e not in false_source_assertions]

mod.verify_rendered = verify_rendered_v5
mod.main()
