import pathlib
import re

SRC = pathlib.Path('.ops/category-money-page-content-wave1.py')
OUT = pathlib.Path('.ops/category-money-page-content-wave1.generated-v2.py')
EXPECTED_BLOB_SHA = '96c0f536894f4242b0083c9a6673b9700bb9ac18'

import hashlib
raw = SRC.read_bytes()
blob_header = b'blob ' + str(len(raw)).encode('ascii') + b'\0'
blob_sha = hashlib.sha1(blob_header + raw).hexdigest()
if blob_sha != EXPECTED_BLOB_SHA:
    raise SystemExit(f'FAIL SOURCE DRIFT expected={EXPECTED_BLOB_SHA} got={blob_sha}')

text = raw.decode('utf-8')

old = "term_description( $term, 'product_cat' )"
new = "term_description( $term->term_id, 'product_cat' )"
if text.count(old) != 1:
    raise SystemExit(f'FAIL term_description patch count={text.count(old)}')
text = text.replace(old, new, 1)

old = "mb_strlen(wp_strip_all_tags($fresh->description))"
new = "(function_exists('mb_strlen') ? mb_strlen(wp_strip_all_tags($fresh->description), 'UTF-8') : strlen(wp_strip_all_tags($fresh->description)))"
if text.count(old) != 1:
    raise SystemExit(f'FAIL mb_strlen patch count={text.count(old)}')
text = text.replace(old, new, 1)

pattern = re.compile(r"def restore_terms\(pre\):.*?\n\n\nsitemap_urls =", re.S)
match = pattern.search(text)
if not match:
    raise SystemExit('FAIL restore_terms block not found')

replacement = r"""def restore_terms(pre):
    import base64
    terms = pre.get('terms', {})
    payload = {
        slug: base64.b64encode(
            terms.get(slug, {}).get('description', '').encode('utf-8')
        ).decode('ascii')
        for slug in TARGET_SLUGS
    }
    pairs = ','.join("'%s'=>'%s'" % (slug, encoded) for slug, encoded in payload.items())
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:14]
    name = 'gramiss-category-wave1-restore-' + nonce + '.php'
    php = f'''<?php
header('Content-Type: application/json; charset=utf-8');
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
@unlink(__FILE__);
$copy=array({pairs});
$out=[];
foreach($copy as $slug=>$encoded){{
    $description=base64_decode($encoded, true);
    if($description===false){{ $out[$slug]='base64_decode_failed'; continue; }}
    $t=get_term_by('slug',$slug,'product_cat');
    if(!$t){{ $out[$slug]='missing'; continue; }}
    $r=wp_update_term($t->term_id,'product_cat',['description'=>$description]);
    $out[$slug]=is_wp_error($r)?$r->get_error_message():'ok';
}}
echo wp_json_encode($out,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
?>'''
    save_public(name, php)
    status, raw, _ = get(BASE + '/' + name + '?t=' + str(int(time.time())), 180)
    body = raw.decode('utf-8', 'replace')
    print('RESTORE_TERMS', status, body[:1000])
    if status != 200:
        raise RuntimeError('restore terms HTTP ' + str(status))
    result = json.loads(body)
    errors = [slug + ':' + str(result.get(slug)) for slug in TARGET_SLUGS if result.get(slug) != 'ok']
    if errors:
        raise RuntimeError('restore terms failed ' + ' | '.join(errors))


sitemap_urls ="""

text = text[:match.start()] + replacement + text[match.end():]

for forbidden in [
    "json.dumps(payload, ensure_ascii=False).replace",
    "term_description( $term, 'product_cat' )",
    "mb_strlen(wp_strip_all_tags($fresh->description))",
]:
    if forbidden in text:
        raise SystemExit('FAIL forbidden legacy pattern remains: ' + forbidden)

required = [
    'base64_decode($encoded, true)',
    "term_description( $term->term_id, 'product_cat' )",
    "function_exists('mb_strlen')",
    'GRAMISS_CATEGORY_SEO_COPY_V1',
    'GRAMISS_CATEGORY_SEO_COPY_CSS_V1',
    'CRITICAL ROLLBACK FAILURE',
]
for token in required:
    if token not in text:
        raise SystemExit('FAIL required token missing: ' + token)

compile(text, str(OUT), 'exec')
OUT.write_text(text, encoding='utf-8')
print('PASS PREPARE CATEGORY MONEY PAGE CONTENT WAVE 1 V2', OUT, hashlib.sha256(text.encode()).hexdigest())
