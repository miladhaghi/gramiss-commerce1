#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import re
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FILES = [
    'header.php',
    'footer.php',
    'functions.php',
    'style.css',
    'assets/css/gramiss-1.css',
]
KEYWORDS = [
    'mobile', 'menu', 'hamburger', 'drawer', 'nav', 'footer',
    'Shop', 'Collections', 'Journal', 'Smart Guide', 'wp_footer', 'wp_nav_menu'
]

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def snippets(text, keywords, radius=700, limit=18):
    out=[]
    seen=[]
    low=text.lower()
    for kw in keywords:
        start=0
        needle=kw.lower()
        while len(out) < limit:
            idx=low.find(needle,start)
            if idx < 0: break
            a=max(0,idx-radius); b=min(len(text),idx+len(kw)+radius)
            if not any(abs(idx-s) < 300 for s in seen):
                out.append(text[a:b])
                seen.append(idx)
            start=idx+len(needle)
    return out

def main():
    # Directory inventory first.
    data = mod.api('list_files', {'dir': mod.ROOT, 'types': 'file|dir', 'limit': 500})
    print('THEME_LIST', json.dumps(data, ensure_ascii=False)[:18000])
    for rel in FILES:
        try:
            text=mod.read(rel)
        except Exception as exc:
            print('FILE_ERROR', rel, str(exc))
            continue
        print('\nFILE', rel, 'SHA', sha(text), 'BYTES', len(text.encode()))
        for i,snip in enumerate(snippets(text, KEYWORDS),1):
            safe=snip.replace('\x00','')
            print(f'--- {rel} SNIP {i} ---')
            print(safe)
            print(f'--- END {rel} SNIP {i} ---')

    status, home = mod.get(mod.BASE + '/?about-support-inspect=1', 120)
    print('HOME_HTTP', status, 'BYTES', len(home.encode()))
    # Rendered-nav snippets only; redact common sensitive value patterns.
    for kw in ['Smart Guide','Collections','Journal','mobile','footer']:
        m=re.search(r'.{0,900}'+re.escape(kw)+r'.{0,1200}',home,re.I|re.S)
        if m:
            text=m.group(0)
            text=re.sub(r'09\d{9}', '09XXXXXXXXX', text)
            text=re.sub(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', '[EMAIL]', text, flags=re.I)
            print('RENDERED',kw,text)

if __name__=='__main__':
    main()
