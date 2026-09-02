import html
import re
import ssl
import time
import urllib.parse
import urllib.request

URL = 'https://gramiss.ir/product-category/tshirt/'
CTX = ssl._create_unverified_context()

def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@'), p.query, p.fragment))

req = urllib.request.Request(safe_url(URL + '?t=' + str(int(time.time()))), headers={
    'User-Agent': 'GramissCategoryH1DiagnosticV1/1.0',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
})
with urllib.request.urlopen(req, context=CTX, timeout=120) as response:
    raw = response.read().decode('utf-8', 'replace')
    print('HTTP', response.status, response.geturl())

matches = list(re.finditer(r'<h1\b[^>]*>.*?</h1>', raw, re.I | re.S))
print('H1_COUNT', len(matches))
for i, match in enumerate(matches, 1):
    tag = re.sub(r'\s+', ' ', match.group(0)).strip()
    plain = re.sub(r'<[^>]+>', ' ', match.group(0))
    plain = re.sub(r'\s+', ' ', html.unescape(plain)).strip()
    before = re.sub(r'\s+', ' ', raw[max(0, match.start()-450):match.start()]).strip()
    after = re.sub(r'\s+', ' ', raw[match.end():match.end()+300]).strip()
    print('H1', i, 'TEXT=', plain)
    print('H1_TAG', i, tag)
    print('H1_BEFORE', i, before)
    print('H1_AFTER', i, after)
