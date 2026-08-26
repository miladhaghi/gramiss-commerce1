import os
import pathlib
import urllib.request

os.environ.setdefault('PUBLIC_ROOT', 'public_html')
base = 'https://raw.githubusercontent.com/miladhaghi/gramiss-commerce1/ops/pdp-mobile-ux-v1/deploy/pdp-mobile-v1/'
root = pathlib.Path('deploy/pdp-mobile-v1')
root.mkdir(parents=True, exist_ok=True)
for name in ('product-mobile-v1.css', 'product-mobile-v1.js', 'deploy.py'):
    data = urllib.request.urlopen(base + name, timeout=60).read()
    (root / name).write_bytes(data)
code = (root / 'deploy.py').read_text(encoding='utf-8')
exec(compile(code, str(root / 'deploy.py'), 'exec'))
