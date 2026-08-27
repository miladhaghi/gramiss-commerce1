from pathlib import Path
import runpy
import urllib.request

commit = 'f2a3a515a664906a7ddd14910715d584b090578e'
base = f'https://raw.githubusercontent.com/miladhaghi/gramiss-commerce1/{commit}/deploy/cart-desktop-v1/'
out = Path('deploy/cart-desktop-v1')
out.mkdir(parents=True, exist_ok=True)
for name in ('cart-desktop-v1.css', 'cart-desktop-v1.js', 'deploy.py'):
    with urllib.request.urlopen(base + name, timeout=90) as response:
        (out / name).write_bytes(response.read())
runpy.run_path(str(out / 'deploy.py'), run_name='__main__')
