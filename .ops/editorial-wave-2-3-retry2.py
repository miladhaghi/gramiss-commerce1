from pathlib import Path
src=Path('.ops/editorial-wave-2-3.py').read_text(encoding='utf-8')

old="$a1=get_page_by_path($slug1,OBJECT,'post');"
new="$a1_posts=get_posts(['post_type'=>'post','post_status'=>'publish','numberposts'=>2,'orderby'=>'ID','order'=>'ASC']);$a1=count($a1_posts)===1?$a1_posts[0]:null;"
if src.count(old)!=2: raise SystemExit(f'PATCH_GUARD a1 lookup count={src.count(old)}')
src=src.replace(old,new)

old_cond="if(!$a1 || $a1->post_status!=='publish' || $a2_existing || $a3_existing || !$cat || !$blog || $blog->post_title!=='مجله Gramiss' || $published!==1){"
new_cond="if(!$a1 || $a1->post_status!=='publish' || strpos($a1->post_title,'تیشرت باکسی')===false || $a2_existing || $a3_existing || !$cat || !$blog || $blog->post_title!=='مجله Gramiss' || $published!==1){"
if old_cond not in src: raise SystemExit('PATCH_GUARD baseline condition missing')
src=src.replace(old_cond,new_cond,1)

old_meta="foreach($meta as $id=>$mm){foreach($mm as $k=>$v)update_post_meta($id,$k,$v);update_post_meta($id,'rank_math_robots',['index','follow']);update_post_meta($id,'rank_math_rich_snippet','article');update_post_meta($id,'rank_math_snippet_article_type','BlogPosting');}"
new_meta="foreach($meta as $id=>$mm){foreach($mm as $k=>$v)update_post_meta($id,$k,$v);delete_post_meta($id,'rank_math_robots');delete_post_meta($id,'rank_math_rich_snippet');delete_post_meta($id,'rank_math_snippet_article_type');}"
if old_meta not in src: raise SystemExit('PATCH_GUARD RankMath meta block missing')
src=src.replace(old_meta,new_meta,1)

old_verify="    if row.get('focus')!=focus: errors.append(key+' focus keyword db mismatch')\n    if row.get('schema')!='BlogPosting': errors.append(key+' schema db mismatch')\n    if 'index' not in row.get('robots',[]) or 'follow' not in row.get('robots',[]): errors.append(key+' robots db mismatch')"
new_verify="    if row.get('focus')!=focus: errors.append(key+' focus keyword db mismatch')\n    if row.get('schema'): errors.append(key+' unexpected legacy schema override')\n    if row.get('robots'): errors.append(key+' unexpected per-post robots override')"
if old_verify not in src: raise SystemExit('PATCH_GUARD Python db verify block missing')
src=src.replace(old_verify,new_verify,1)

exec(compile(src,'.ops/editorial-wave-2-3-retry2.py','exec'))
