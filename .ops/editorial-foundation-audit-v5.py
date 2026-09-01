import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

HOST = os.environ["CPANEL_HOST"]
USER = os.environ["CPANEL_USER"]
TOKEN = os.environ["CPANEL_TOKEN"]
THEME_ROOT = os.environ["THEME_ROOT"].strip("/")
HEALTHY_HOME_SHA = os.environ.get("HEALTHY_HOME_SHA", "")
CTX = ssl._create_unverified_context()
BASE = "https://gramiss.ir"

EXPECTED_PRODUCT_SHA = "70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3"
EXPECTED_PRODUCT_CAT_SHA = "75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4"
EXPECTED_IDS = [453,459,460,463,464,467,468,471,472,482,483,487,488,492,493]
EXPECTED_TITLES = {
    453:"تیشرت باکسی چیست و چه تفاوتی با اورسایز دارد؟",
    459:"راهنمای انتخاب سایز تیشرت باکسی مردانه؛ اندازه‌گیری و فیت مناسب",
    460:"تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ کدام فیت مناسب شماست؟",
    463:"پارچه لینن چیست؟ راهنمای شناخت، چروک و انتخاب لباس لینن",
    464:"شست‌وشوی پیراهن لینن مردانه؛ راهنمای خشک‌کردن و اتوکشی",
    467:"استایل با پیراهن لینن مردانه؛ شلوار، کفش و ترکیب رنگ",
    468:"با شلوار بگ مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و قد شلوار",
    471:"راهنمای خرید تیشرت مردانه؛ فیت، اندازه، پارچه، دوخت و چاپ",
    472:"راهنمای خرید شلوار جین مردانه؛ فیت، قد، پارچه و جزئیات",
    482:"راهنمای انتخاب سایز کتانی مردانه؛ اندازه‌گیری پا برای خرید آنلاین",
    483:"راهنمای خرید کتانی مردانه برای استفاده روزمره؛ سایز، رویه و زیره",
    487:"راهنمای انتخاب سایز پیراهن مردانه؛ سرشانه، سینه، قد و آستین",
    488:"تمیز کردن کتانی سفید بدون آسیب؛ راهنمای رویه، بند و خشک‌کردن",
    492:"شلوار کارگو مردانه چیست و چه تفاوتی با شلوار بگ دارد؟",
    493:"راهنمای انتخاب سایز کلاه فیت کپ؛ اندازه‌گیری دور سر بدون حدس",
}
EXPECTED_COUNTS = {"fit-size-guide":7,"fabric-care":3,"style-guide":2,"buying-guide":3}
EXPECTED_FOCUS = {492:"شلوار کارگو مردانه چیست",493:"انتخاب سایز کلاه فیت کپ"}
EXPECTED_META = {
    492:("شلوار کارگو مردانه چیست؟ تفاوت کارگو و بگ","شلوار کارگو مردانه را از روی ساختار، جیب‌ها و فیت بشناسید و تفاوت آن با شلوار بگ و راسته را برای انتخاب دقیق‌تر در خرید آنلاین بررسی کنید."),
    493:("انتخاب سایز کلاه فیت کپ؛ اندازه‌گیری دور سر","برای انتخاب سایز کلاه فیت کپ، دور سر را درست اندازه بگیرید و عدد را با جدول همان مدل مقایسه کنید؛ بدون تکیه بر جدول‌های تبدیل عمومی."),
}
PROTECTED_EXPECTED = {
    "front-page.php":"0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7",
    "template-parts/home-looks.php":"3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d",
    "assets/css/home-looks.css":"98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0",
    "assets/js/home-looks.js":"6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2",
}


def cpanel(function, params, post=False):
    url=f"https://{HOST}:2083/execute/Fileman/{function}"
    encoded=urllib.parse.urlencode(params).encode()
    last=None
    for attempt in range(1,5):
        try:
            req=urllib.request.Request(url if post else url+"?"+encoded.decode(),data=encoded if post else None,method="POST" if post else "GET")
            req.add_header("Authorization",f"cpanel {USER}:{TOKEN}")
            if post:req.add_header("Content-Type","application/x-www-form-urlencoded")
            with urllib.request.urlopen(req,context=CTX,timeout=90) as response:
                payload=json.loads(response.read().decode("utf-8","replace"))
            result=payload.get("result") if isinstance(payload.get("result"),dict) else payload
            if not isinstance(result,dict) or result.get("status")!=1:raise RuntimeError(str(result))
            return result.get("data")
        except Exception as exc:
            last=exc;print("CPANEL_RETRY",function,attempt,exc)
            if attempt<4:time.sleep(attempt*2)
    raise last


def read_theme(relative):
    directory,name=relative.rsplit("/",1) if "/" in relative else ("",relative)
    data=cpanel("get_file_content",{"dir":THEME_ROOT if not directory else THEME_ROOT+"/"+directory,"file":name,"from_charset":"_DETECT_","to_charset":"utf-8"})
    if isinstance(data,dict):
        for key in ("content","file_content","data"):
            if isinstance(data.get(key),str):return data[key]
    return data if isinstance(data,str) else ""


def save_public(name,content):
    return cpanel("save_file_content",{"dir":"public_html","file":name,"content":content,"from_charset":"UTF-8","to_charset":"UTF-8","fallback":"0"},True)


def safe_url(url):
    parts=urllib.parse.urlsplit(url)
    path=urllib.parse.quote(urllib.parse.unquote(parts.path),safe="/%:@")
    query=urllib.parse.quote(urllib.parse.unquote(parts.query),safe="=&%:@,+")
    return urllib.parse.urlunsplit((parts.scheme,parts.netloc,path,query,parts.fragment))


def get(url,timeout=180):
    url=safe_url(url)
    last=None
    for attempt in range(1,5):
        req=urllib.request.Request(url,headers={"User-Agent":"GramissEditorialAuditV5/1.0","Cache-Control":"no-cache","Pragma":"no-cache"})
        try:
            with urllib.request.urlopen(req,context=CTX,timeout=timeout) as response:return response.status,response.read(),response.geturl(),dict(response.headers)
        except urllib.error.HTTPError as exc:return exc.code,exc.read(),exc.geturl(),dict(exc.headers)
        except Exception as exc:
            last=exc;print("HTTP_RETRY",attempt,url,exc)
            if attempt<4:time.sleep(attempt*2)
    raise last


def html_value(text,pattern):
    m=re.search(pattern,text,re.I|re.S)
    return re.sub(r"\s+"," ",m.group(1)).strip() if m else ""


def head(raw):
    text=raw.decode("utf-8","replace").split("</head>",1)[0]
    return {
        "title":html_value(text,r"<title[^>]*>(.*?)</title>"),
        "description":html_value(text,r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']*)"),
        "canonical":html_value(text,r"<link[^>]+rel=[\"']canonical[\"'][^>]+href=[\"']([^\"']+)"),
        "robots":html_value(text,r"<meta[^>]+name=[\"']robots[\"'][^>]+content=[\"']([^\"']+)"),
    }


def norm(url):return urllib.parse.unquote(url).split("?",1)[0].rstrip("/")+"/"


def sitemap(path):
    status,raw,_,_=get(BASE+"/"+path+"?t="+str(int(time.time())),120)
    urls=[x.replace("&amp;","&") for x in re.findall(r"<loc>(.*?)</loc>",raw.decode("utf-8","replace"),re.I)]
    return status,urls

errors=[]
protected={p:hashlib.sha256(read_theme(p).encode()).hexdigest() for p in PROTECTED_EXPECTED}
print("PROTECTED",json.dumps(protected,ensure_ascii=False,sort_keys=True))
for path,expected in PROTECTED_EXPECTED.items():
    if protected.get(path)!=expected:errors.append("protected drift "+path)
if HEALTHY_HOME_SHA and protected.get("front-page.php")!=HEALTHY_HOME_SHA:errors.append("healthy home mismatch")

nonce=hashlib.sha256((str(time.time())+protected.get("front-page.php","")).encode()).hexdigest()[:14]
probe="gramiss-editorial-foundation-audit-v5-"+nonce+".php"
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
$ids=[453,459,460,463,464,467,468,471,472,482,483,487,488,492,493];$posts=[];
foreach($ids as $id){$p=get_post($id);$posts[]=$p?['id'=>(int)$p->ID,'status'=>$p->post_status,'title'=>$p->post_title,'url'=>get_permalink($p),'cats'=>wp_get_post_categories($p->ID,['fields'=>'slugs']),'focus'=>get_post_meta($p->ID,'rank_math_focus_keyword',true),'content'=>$p->post_content]:['id'=>$id,'missing'=>true];}
$cats=[];foreach(['fit-size-guide','fabric-care','style-guide','buying-guide'] as $slug){$t=get_term_by('slug',$slug,'category');$cats[$slug]=$t?['id'=>(int)$t->term_id,'count'=>(int)$t->count,'url'=>get_term_link($t)]:null;}
$blog=get_post(22);echo wp_json_encode(['published'=>(int)wp_count_posts('post')->publish,'posts'=>$posts,'categories'=>$cats,'blog'=>$blog?['id'=>(int)$blog->ID,'title'=>$blog->post_title,'url'=>get_permalink($blog)]:null],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);?>'''
save_public(probe,php)
state_status,state_raw,_,_=get(BASE+"/"+probe+"?t="+str(int(time.time())),240)
try:state=json.loads(state_raw.decode("utf-8","replace")) if state_status==200 else {}
except Exception as exc:state={};errors.append("state json "+str(exc))
print("WP_STATE_STATUS",state_status,"PUBLISHED",state.get("published"))
if state_status!=200:errors.append("wp probe http")
if state.get("published")!=15:errors.append("published != 15")
if not state.get("blog") or state["blog"].get("title")!="مجله Gramiss":errors.append("blog state")
rows={int(x.get("id",0)):x for x in state.get("posts",[]) if isinstance(x,dict)}
for pid in EXPECTED_IDS:
    row=rows.get(pid)
    if not row:errors.append("missing post "+str(pid));continue
    if row.get("status")!="publish":errors.append("not publish "+str(pid))
    if row.get("title")!=EXPECTED_TITLES[pid]:errors.append("title drift "+str(pid))
    if not row.get("url"):errors.append("url missing "+str(pid))
    if pid in EXPECTED_FOCUS and row.get("focus")!=EXPECTED_FOCUS[pid]:errors.append("focus drift "+str(pid))
for slug,count in EXPECTED_COUNTS.items():
    cat=(state.get("categories") or {}).get(slug)
    if not cat:errors.append("missing category "+slug)
    elif int(cat.get("count",-1))!=count:errors.append("category count "+slug)

live_urls={pid:rows[pid]["url"] for pid in EXPECTED_IDS if pid in rows and rows[pid].get("url")}
for pid,url in live_urls.items():
    status,raw,final,_=get(url+"?t="+str(int(time.time())),180)
    text=raw.decode("utf-8","replace");metadata=head(raw)
    links={norm(x) for x in re.findall(r'href=["\']([^"\']+)',text,re.I) if "gramiss.ir" in x}
    h2=text.count("<h2>")
    print("ARTICLE",pid,status,"H2",h2,"BLOGPOSTING",bool(re.search(r'"@type"\s*:\s*"BlogPosting"',text,re.I)),"PRODUCT",bool(re.search(r'"@type"\s*:\s*"Product"',text,re.I)))
    if status!=200:errors.append("article http "+str(pid))
    if EXPECTED_TITLES[pid] not in text:errors.append("article title render "+str(pid))
    if norm(metadata.get("canonical",""))!=norm(url):errors.append("canonical "+str(pid))
    robots=metadata.get("robots","").lower()
    if "noindex" in robots or "index" not in robots:errors.append("robots "+str(pid))
    if not re.search(r'"@type"\s*:\s*"BlogPosting"',text,re.I):errors.append("BlogPosting "+str(pid))
    if re.search(r'"@type"\s*:\s*"Product"',text,re.I):errors.append("Product schema "+str(pid))
    if h2<8:errors.append("thin h2 "+str(pid))
    if pid in EXPECTED_META and (metadata.get("title"),metadata.get("description"))!=EXPECTED_META[pid]:errors.append("meta drift "+str(pid))
    if pid==492:
        for needed in [BASE+"/product-category/pants/",BASE+"/product-category/pants/cargo-pants/",live_urls[460],live_urls[472]]:
            if norm(needed) not in links:errors.append("492 missing link "+norm(needed))
    if pid==493:
        for needed in [BASE+"/product-category/hat/",BASE+"/product-category/hat/fitted-cap/",live_urls[487]]:
            if norm(needed) not in links:errors.append("493 missing link "+norm(needed))

for source,marker in [(460,'data-g1-wave="1415-cargo-from-03"'),(472,'data-g1-wave="1415-cargo-from-09"')]:
    content=rows.get(source,{}).get("content","")
    if marker not in content:errors.append("missing bridge marker "+str(source))
    if live_urls.get(492) and norm(live_urls[492]) not in {norm(x) for x in re.findall(r'href=["\']([^"\']+)',content,re.I) if "gramiss.ir" in x}:errors.append("missing bridge href "+str(source))

for slug,count in EXPECTED_COUNTS.items():
    url=state["categories"][slug]["url"] if (state.get("categories") or {}).get(slug) else ""
    if not url:continue
    status,raw,_,_=get(url+"?t="+str(int(time.time())),150);metadata=head(raw);text=raw.decode("utf-8","replace")
    print("CATEGORY",slug,status,"COUNT",count)
    if status!=200:errors.append("category http "+slug)
    if norm(metadata.get("canonical",""))!=norm(url):errors.append("category canonical "+slug)
    if "noindex" in metadata.get("robots","").lower():errors.append("category noindex "+slug)

blog=state.get("blog",{}).get("url","")
combined=""
if blog:
    for page in (1,2):
        url=blog if page==1 else blog.rstrip("/")+"/page/2/"
        status,raw,final,_=get(url+"?t="+str(int(time.time())),150);text=raw.decode("utf-8","replace")
        print("BLOG_PAGE",page,status,final)
        if status!=200:errors.append("blog page "+str(page))
        combined+="\n"+text
    for title in EXPECTED_TITLES.values():
        if title not in combined:errors.append("blog missing "+title[:30])
    status,raw,_,_=get(blog+"?t="+str(int(time.time())),150);metadata=head(raw)
    if norm(metadata.get("canonical",""))!=norm(blog):errors.append("blog canonical")
    if "noindex" in metadata.get("robots","").lower():errors.append("blog noindex")

post_status,post_urls=sitemap("post-sitemap.xml");post_norm={norm(x) for x in post_urls}
print("POST_SITEMAP",post_status,len(post_urls))
if post_status!=200 or len(post_urls)!=16:errors.append("post sitemap count")
for url in live_urls.values():
    if norm(url) not in post_norm:errors.append("post sitemap missing "+norm(url))
if blog and norm(blog) not in post_norm:errors.append("post sitemap missing blog")
cat_status,cat_urls=sitemap("category-sitemap.xml");print("CATEGORY_SITEMAP",cat_status,len(cat_urls))
if cat_status!=200 or len(cat_urls)!=4:errors.append("category sitemap count")
product_status,product_urls=sitemap("product-sitemap.xml");product_urls=sorted(product_urls);product_sha=hashlib.sha256("\n".join(product_urls).encode()).hexdigest();print("PRODUCT_SITEMAP",product_status,len(product_urls),product_sha)
if product_status!=200 or len(product_urls)!=47 or product_sha!=EXPECTED_PRODUCT_SHA:errors.append("product sitemap drift")
pc_status,pc_urls=sitemap("product_cat-sitemap.xml");pc_urls=sorted(pc_urls);pc_sha=hashlib.sha256("\n".join(pc_urls).encode()).hexdigest();print("PRODUCT_CAT_SITEMAP",pc_status,len(pc_urls),pc_sha)
if pc_status!=200 or len(pc_urls)!=20 or pc_sha!=EXPECTED_PRODUCT_CAT_SHA:errors.append("product cat sitemap drift")

print("ERRORS",json.dumps(errors,ensure_ascii=False))
if errors:raise SystemExit("AUDIT V5 FAILED: "+"; ".join(errors))
print("PASS EDITORIAL FOUNDATION AUDIT V5")
