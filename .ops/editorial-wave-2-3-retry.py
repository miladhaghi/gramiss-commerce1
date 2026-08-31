from pathlib import Path
src=Path('.ops/editorial-wave-2-3.py').read_text(encoding='utf-8')
old="$a1=get_page_by_path($slug1,OBJECT,'post');"
new="$a1_posts=get_posts(['post_type'=>'post','post_status'=>'publish','numberposts'=>2,'orderby'=>'ID','order'=>'ASC']);$a1=count($a1_posts)===1?$a1_posts[0]:null;"
if src.count(old)!=2:
    raise SystemExit(f'PATCH_GUARD a1 lookup count={src.count(old)}')
src=src.replace(old,new)
old_cond="if(!$a1 || $a1->post_status!=='publish' || $a2_existing || $a3_existing || !$cat || !$blog || $blog->post_title!=='مجله Gramiss' || $published!==1){"
new_cond="if(!$a1 || $a1->post_status!=='publish' || strpos($a1->post_title,'تیشرت باکسی')===false || $a2_existing || $a3_existing || !$cat || !$blog || $blog->post_title!=='مجله Gramiss' || $published!==1){"
if old_cond not in src:
    raise SystemExit('PATCH_GUARD baseline condition missing')
src=src.replace(old_cond,new_cond,1)
exec(compile(src,'.ops/editorial-wave-2-3-retry.py','exec'))
