import hashlib,json,os,ssl,time,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();last=None
 for attempt in range(1,5):
  try:
   r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}')
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
   q=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
   return q.get('data')
  except Exception as exc:last=exc;print(f'Attempt {attempt}/4 {fn}: {exc}');time.sleep(attempt*2 if attempt<4 else 0)
 raise last
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
def get(u,timeout=180):
 r=urllib.request.Request(u,headers={'User-Agent':'GramissProductDataQAV1/1.0','Cache-Control':'no-cache','Pragma':'no-cache'})
 with urllib.request.urlopen(r,context=ctx,timeout=timeout) as z:return z.status,z.read(),z.geturl()
front=read_theme('front-page.php');sha=hashlib.sha256(front.encode()).hexdigest();print('LIVE_HOME_SHA',sha)
if healthy and sha!=healthy:raise SystemExit('ABORT Home mismatch')
st=str(int(time.time()));name='gramiss-product-data-qa-'+hashlib.sha256((st+sha).encode()).hexdigest()[:14]+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
if(!function_exists('wc_get_product')){http_response_code(409);echo wp_json_encode(['error'=>'WooCommerce unavailable']);exit;}
function g1_norm($s){$s=html_entity_decode(wp_strip_all_tags((string)$s),ENT_QUOTES|ENT_HTML5,'UTF-8');$s=str_replace(['ي','ك','‌'],['ی','ک',' '],$s);$s=mb_strtolower($s);$s=preg_replace('/[^\p{L}\p{N}]+/u',' ',trim($s));return trim(preg_replace('/\s+/u',' ',$s));}
function g1_words($s){$stop=['و','در','با','از','به','طرح','مردانه'];$w=array_values(array_filter(explode(' ',g1_norm($s)),fn($x)=>mb_strlen($x)>1&&!in_array($x,$stop,true)));return array_values(array_unique($w));}
function g1_ancestors($terms){$all=[];foreach($terms as $t){$all[$t->slug]=$t->name;foreach(get_ancestors($t->term_id,'product_cat','taxonomy') as $aid){$a=get_term($aid,'product_cat');if($a&&!is_wp_error($a))$all[$a->slug]=$a->name;}}return $all;}
function g1_slug_overlap($title,$slug){$tw=g1_words($title);$sw=g1_words(str_replace('-',' ',rawurldecode($slug)));if(!$tw)return 1;$hit=0;foreach($tw as $w)if(in_array($w,$sw,true))$hit++;return round($hit/count($tw),3);}
$ids=get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC','fields'=>'ids']);$rows=[];$title_groups=[];$norm_groups=[];$content_groups=[];$stats=['products'=>count($ids),'simple'=>0,'variable'=>0,'sku_empty'=>0,'price_empty'=>0,'short_empty'=>0,'thin_content_under_60'=>0,'seo_title_over_60'=>0,'taxonomy_flags'=>0,'slug_flags'=>0,'variable_no_variations'=>0,'variation_price_empty'=>0,'variation_sku_empty'=>0];
foreach($ids as $id){$p=wc_get_product($id);if(!$p)continue;$name=$p->get_name();$slug=get_post_field('post_name',$id);$terms=wp_get_post_terms($id,'product_cat');$assigned=[];foreach($terms as $t)$assigned[$t->slug]=$t->name;$family=g1_ancestors($terms);$flags=[];$n=g1_norm($name);
if(str_contains($n,'پراهن'))$flags[]='title_typo_پراهن';
if(str_contains($n,'آستین بلند')&&isset($assigned['short-sleeve-shirt']))$flags[]='title_long_sleeve_but_short_category';
if(str_contains($n,'آستین کوتاه')&&isset($assigned['long-sleeve-shirt']))$flags[]='title_short_sleeve_but_long_category';
if(str_contains($n,'لینن')&&!isset($family['linen-shirt']))$flags[]='linen_title_without_linen_category';
if(str_contains($n,'کارگو')&&!isset($family['cargo-pants']))$flags[]='cargo_title_without_cargo_category';
if(str_contains($n,'جین')&&!isset($family['jeans']))$flags[]='jeans_title_without_jeans_category';
if(str_contains($n,'فیت کپ')&&isset($assigned['snapback-cap']))$flags[]='fitted_cap_also_snapback';
if(str_contains($n,'تیشرت')&&!isset($family['tshirt']))$flags[]='tshirt_title_outside_tshirt_family';
if((str_contains($n,'پیراهن')||str_contains($n,'پراهن'))&&!isset($family['shirt']))$flags[]='shirt_title_outside_shirt_family';
if(str_contains($n,'شلوار')&&!isset($family['pants']))$flags[]='pants_title_outside_pants_family';
if(str_contains($n,'کتونی')&&!isset($family['sneakers']))$flags[]='sneaker_title_outside_sneaker_family';
if(str_contains($n,'کلاه')&&!isset($family['hat']))$flags[]='hat_title_outside_hat_family';
$overlap=g1_slug_overlap($name,$slug);$slug_flag=$overlap<0.5;$content=trim(wp_strip_all_tags($p->get_description()));$short=trim(wp_strip_all_tags($p->get_short_description()));$seo_title='خرید '.$name.' - Gramiss';$type=$p->get_type();$stats[$type]=($stats[$type]??0)+1;if($p->get_sku()==='')$stats['sku_empty']++;if($p->get_price()==='')$stats['price_empty']++;if($short==='')$stats['short_empty']++;if(mb_strlen($content)<60)$stats['thin_content_under_60']++;if(mb_strlen($seo_title)>60)$stats['seo_title_over_60']++;if($flags)$stats['taxonomy_flags']++;if($slug_flag)$stats['slug_flags']++;
$vars=[];$vsummary=['count'=>0,'published'=>0,'price_empty'=>0,'sku_empty'=>0,'stock_out'=>0,'attribute_empty'=>0,'price_min'=>null,'price_max'=>null];if($p->is_type('variable')){$children=$p->get_children();$vsummary['count']=count($children);if(!$children)$stats['variable_no_variations']++;$prices=[];foreach($children as $vid){$v=wc_get_product($vid);if(!$v)continue;if(get_post_status($vid)==='publish')$vsummary['published']++;$vp=$v->get_price();if($vp===''){$vsummary['price_empty']++;$stats['variation_price_empty']++;}else $prices[]=(float)$vp;if($v->get_sku()===''){$vsummary['sku_empty']++;$stats['variation_sku_empty']++;}if(!$v->is_in_stock())$vsummary['stock_out']++;$attrs=$v->get_attributes();if(!$attrs||in_array('',array_values($attrs),true))$vsummary['attribute_empty']++;$vars[]=['id'=>(int)$vid,'status'=>get_post_status($vid),'price'=>$vp,'stock'=>$v->get_stock_status(),'attrs'=>$attrs];}if($prices){$vsummary['price_min']=min($prices);$vsummary['price_max']=max($prices);}}
$title_groups[$name][]=(int)$id;$norm_groups[g1_norm($name)][]=(int)$id;$ch=md5(g1_norm($content));if($content!=='')$content_groups[$ch][]=(int)$id;
$rows[]=['id'=>(int)$id,'name'=>$name,'slug'=>$slug,'url'=>get_permalink($id),'type'=>$type,'price'=>$p->get_price(),'regular_price'=>$p->get_regular_price(),'sale_price'=>$p->get_sale_price(),'stock_status'=>$p->get_stock_status(),'sku'=>$p->get_sku(),'short_len'=>mb_strlen($short),'content_len'=>mb_strlen($content),'seo_title_len'=>mb_strlen($seo_title),'assigned_categories'=>$assigned,'family_categories'=>$family,'flags'=>$flags,'slug_overlap'=>$overlap,'slug_flag'=>$slug_flag,'variations'=>$vsummary,'variation_rows'=>$vars];}
$dupes=[];foreach($title_groups as $k=>$v)if(count($v)>1)$dupes[]=['type'=>'exact_title','value'=>$k,'ids'=>$v];foreach($norm_groups as $k=>$v)if(count($v)>1 && !in_array($v,array_column($dupes,'ids'),true))$dupes[]=['type'=>'normalized_title','value'=>$k,'ids'=>$v];foreach($content_groups as $k=>$v)if(count($v)>1)$dupes[]=['type'=>'same_description','value'=>$k,'ids'=>$v];
$issues=[];foreach($rows as $r){$why=[];if($r['price']==='')$why[]='missing_price';if($r['sku']==='')$why[]='missing_sku';if($r['short_len']===0)$why[]='missing_short_description';if($r['content_len']<60)$why[]='thin_description';if($r['seo_title_len']>60)$why[]='seo_title_over_60';if($r['flags'])$why=array_merge($why,$r['flags']);if($r['slug_flag'])$why[]='low_title_slug_overlap';if($r['type']==='variable'&&$r['variations']['price_empty']>0)$why[]='variation_missing_price';if($r['type']==='variable'&&$r['variations']['count']===0)$why[]='variable_without_variations';if($why)$issues[]=['id'=>$r['id'],'name'=>$r['name'],'slug'=>rawurldecode($r['slug']),'url'=>$r['url'],'price'=>$r['price'],'content_len'=>$r['content_len'],'seo_title_len'=>$r['seo_title_len'],'assigned_categories'=>$r['assigned_categories'],'flags'=>$why,'slug_overlap'=>$r['slug_overlap'],'variations'=>$r['variations']];}
echo wp_json_encode(['stats'=>$stats,'duplicates'=>$dupes,'issues'=>$issues,'rows'=>$rows],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''
save(name,php);s,b,u=get('https://gramiss.ir/'+name+'?t='+st);print('PROBE',s,u,'BYTES',len(b));data=json.loads(b.decode('utf-8','replace'));print('STATS',json.dumps(data.get('stats',{}),ensure_ascii=False,separators=(',',':')));print('DUPLICATES',json.dumps(data.get('duplicates',[]),ensure_ascii=False,separators=(',',':')))
for x in data.get('issues',[]):
 # Suppress universally-known missing SKU/short-desc from per-row noise unless something else is wrong.
 meaningful=[f for f in x.get('flags',[]) if f not in ('missing_sku','missing_short_description')]
 if meaningful:print('ISSUE',x['id'],json.dumps({**x,'flags':meaningful},ensure_ascii=False,separators=(',',':')))
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=sha:raise SystemExit('ABORT Home changed')
print('END READ ONLY PRODUCT DATA QA V1')
