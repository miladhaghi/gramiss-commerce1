import argparse,json,re,sys

VALID_STOCK={'instock','outofstock','onbackorder'}


def nonempty(v):return isinstance(v,str) and bool(v.strip())
def price_ok(v):
 try:return str(v).strip()!='' and float(str(v).replace(',','.'))>=0
 except Exception:return False

def validate(d):
 blockers=[];warnings=[]
 def block(code,detail=''):blockers.append({'code':code,'detail':detail})
 def warn(code,detail=''):warnings.append({'code':code,'detail':detail})
 if not isinstance(d,dict):return [{'code':'root_not_object','detail':''}],[]
 required=['name','slug','product_type','primary_category_slug','parent_sku','full_description','short_description','index_intent','images']
 for k in required:
  if k not in d:block('required_field_missing',k)
 if not nonempty(d.get('name')):block('name_missing')
 slug=str(d.get('slug') or '').strip()
 if not slug:block('slug_missing')
 elif re.search(r'\s',slug) or '/' in slug:block('slug_invalid',slug)
 ptype=d.get('product_type')
 if ptype not in {'simple','variable'}:block('product_type_invalid',str(ptype))
 if not nonempty(d.get('primary_category_slug')):block('primary_category_missing')
 sec=d.get('secondary_category_slugs',[])
 if not isinstance(sec,list):block('secondary_categories_not_list')
 elif len(sec)!=len(set(sec)):block('secondary_category_duplicate')
 if d.get('primary_category_slug') in sec:warn('primary_category_repeated_as_secondary',str(d.get('primary_category_slug')))
 parent_sku=str(d.get('parent_sku') or '').strip()
 if not parent_sku:block('parent_sku_missing')
 if not nonempty(d.get('full_description')):block('full_description_missing')
 short=str(d.get('short_description') or '').strip()
 if not short:block('short_description_missing')
 elif len(short)>190:warn('short_description_long',str(len(short)))
 intent=d.get('index_intent')
 if intent not in {'index','noindex'}:block('index_intent_invalid',str(intent))
 if intent=='noindex' and len(str(d.get('noindex_reason') or '').strip())<3:block('noindex_reason_missing')
 images=d.get('images')
 if not isinstance(images,list) or not images:block('images_missing')
 else:
  featured=0
  for i,img in enumerate(images):
   if not isinstance(img,dict):block('image_invalid',str(i));continue
   if not nonempty(img.get('alt')):block('image_alt_missing',str(i))
   if not (isinstance(img.get('attachment_id'),int) and img.get('attachment_id',0)>0) and not nonempty(img.get('source')):block('image_source_missing',str(i))
   if img.get('featured') is True:featured+=1
  if featured!=1:block('featured_image_designation_invalid',str(featured))
 attrs=d.get('attributes',[])
 if attrs is None:attrs=[]
 if not isinstance(attrs,list):block('attributes_not_list');attrs=[]
 amap={}
 for i,a in enumerate(attrs):
  if not isinstance(a,dict):block('attribute_invalid',str(i));continue
  tax=str(a.get('taxonomy') or '').strip();vals=a.get('values')
  if not tax:block('attribute_taxonomy_missing',str(i));continue
  if tax in amap:block('attribute_taxonomy_duplicate',tax)
  if not isinstance(vals,list) or not vals or any(not nonempty(v) for v in vals):block('attribute_values_invalid',tax);vals=[]
  elif len(vals)!=len(set(vals)):block('attribute_values_duplicate',tax)
  amap[tax]={'values':set(vals),'variation':a.get('variation') is True}
 if ptype=='simple':
  if not price_ok(d.get('price')):block('simple_price_invalid')
  if d.get('stock_status') not in VALID_STOCK:block('simple_stock_status_invalid',str(d.get('stock_status')))
  if d.get('manage_stock') is True and not isinstance(d.get('stock_quantity'),int):block('simple_stock_quantity_missing')
  if d.get('variations'):block('simple_product_has_variations')
 if ptype=='variable':
  if not any(a.get('variation') for a in amap.values()):block('variation_attribute_missing')
  vs=d.get('variations')
  if not isinstance(vs,list) or not vs:block('variations_missing');vs=[]
  skus={};combos={}
  for i,v in enumerate(vs):
   if not isinstance(v,dict):block('variation_invalid',str(i));continue
   sku=str(v.get('sku') or '').strip()
   if not sku:block('variation_sku_missing',str(i))
   elif sku==parent_sku:block('variation_sku_equals_parent',sku)
   elif sku in skus:block('variation_sku_duplicate',f'{skus[sku]},{i}:{sku}')
   else:skus[sku]=i
   if not price_ok(v.get('price')):block('variation_price_invalid',sku or str(i))
   if v.get('stock_status') not in VALID_STOCK:block('variation_stock_status_invalid',sku or str(i))
   if v.get('manage_stock') is True and not isinstance(v.get('stock_quantity'),int):block('variation_stock_quantity_missing',sku or str(i))
   va=v.get('attributes')
   if not isinstance(va,dict) or not va:block('variation_attributes_missing',sku or str(i));continue
   for tax,value in va.items():
    if tax not in amap:block('variation_unknown_attribute',f'{sku}:{tax}')
    elif not amap[tax]['variation']:block('variation_uses_nonvariation_attribute',f'{sku}:{tax}')
    elif value not in amap[tax]['values']:block('variation_attribute_value_invalid',f'{sku}:{tax}={value}')
   expected={k for k,x in amap.items() if x['variation']}
   if set(va)!=expected:block('variation_attribute_set_incomplete',f'{sku}:{sorted(set(va))}!={sorted(expected)}')
   combo=tuple(sorted(va.items()))
   if combo in combos:block('variation_combination_duplicate',f'{combos[combo]},{i}')
   else:combos[combo]=i
 warn('verified_facts_required','All commercial/material/brand facts must come from an authoritative product source; this validator cannot verify truthfulness.')
 return blockers,warnings


def self_test():
 good={'name':'تیشرت نمونه','slug':'tshirt-sample','product_type':'variable','primary_category_slug':'tshirt','secondary_category_slugs':['graphic-tshirt'],'parent_sku':'GR-TS-001','full_description':'توضیح تاییدشده محصول نمونه.','short_description':'توضیح کوتاه تاییدشده محصول نمونه.','index_intent':'index','images':[{'source':'sample-front.webp','alt':'نمای روبه‌روی تیشرت نمونه','featured':True}], 'attributes':[{'taxonomy':'pa_color','values':['black'],'visible':True,'variation':True},{'taxonomy':'pa_size','values':['m','l'],'visible':True,'variation':True}], 'variations':[{'sku':'GR-TS-001-BLK-M','price':'100','stock_status':'instock','manage_stock':False,'attributes':{'pa_color':'black','pa_size':'m'}},{'sku':'GR-TS-001-BLK-L','price':'100','stock_status':'instock','manage_stock':False,'attributes':{'pa_color':'black','pa_size':'l'}}]}
 b,w=validate(good);assert not b,(b,w)
 bad=json.loads(json.dumps(good,ensure_ascii=False));bad['parent_sku']='';bad['images'][0]['alt']='';bad['variations'][1]['sku']=bad['variations'][0]['sku'];bad['variations'][1]['price']=''
 b,_=validate(bad);codes={x['code'] for x in b};assert {'parent_sku_missing','image_alt_missing','variation_sku_duplicate','variation_price_invalid'}<=codes,codes
 print('PASS PRODUCT INTAKE VALIDATOR SELF TEST V1')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('file',nargs='?');ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
 if args.self_test:self_test();return
 if not args.file:raise SystemExit('intake JSON file required')
 with open(args.file,encoding='utf-8') as f:d=json.load(f)
 blockers,warnings=validate(d);result={'ok':not blockers,'blockers':blockers,'warnings':warnings};print(json.dumps(result,ensure_ascii=False,indent=2))
 if blockers:raise SystemExit(2)

if __name__=='__main__':main()
