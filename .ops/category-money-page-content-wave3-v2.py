from pathlib import Path

src_path = Path('.ops/category-money-page-content-wave3.py')
src = src_path.read_text(encoding='utf-8')
old = """        if len(strip_markup(stored)) < 300:\n            errors.append(str(tid) + ' stored copy thin')\n        if strip_markup(copy[tid])[:80] not in strip_markup(stored):\n            errors.append(str(tid) + ' stored copy mismatch')\n"""
new = """        stored_text = strip_markup(stored)\n        expected_text = strip_markup(copy[tid])\n        public_text = after['seo_text']\n        if len(stored_text) < 300:\n            errors.append(str(tid) + ' stored copy thin')\n        hm = re.search(r'<h2\\b[^>]*>(.*?)</h2>', copy[tid], re.I | re.S)\n        expected_heading = strip_markup(hm.group(1)) if hm else expected_text[:50]\n        if expected_heading not in stored_text or expected_heading not in public_text:\n            errors.append(str(tid) + ' semantic heading mismatch')\n        expected_links = {norm(html.unescape(u)) for u in re.findall(r'href=[\\\"\\\']([^\\\"\\\']+)', copy[tid], re.I) if 'gramiss.ir' in u}\n        actual_links = {norm(u) for u in after['internal_links']}\n        if not expected_links.issubset(actual_links):\n            errors.append(str(tid) + ' expected links missing')\n"""
if src.count(old) != 1:
    raise SystemExit('FAIL PATCH TARGET COUNT ' + str(src.count(old)))
patched = src.replace(old, new, 1)
compile(patched, str(src_path) + ':semantic-v2', 'exec')
print('PASS WAVE3 V2 SOURCE PATCH/COMPILE')
exec(compile(patched, str(src_path) + ':semantic-v2', 'exec'), {'__name__': '__main__', '__file__': str(src_path)})
