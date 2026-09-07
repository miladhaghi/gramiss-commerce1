#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import re

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

for path in ['template-parts/home-looks.php','front-page.php']:
    text = mod.read(path)
    print('FILE', path)
    for line in text.splitlines():
        if re.search(r'look|webp|png|jpg|jpeg|image|src=', line, re.I):
            print(line[:1200])
