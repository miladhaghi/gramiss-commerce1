import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request

HOST = os.environ["CPANEL_HOST"]
USER = os.environ["CPANEL_USER"]
TOKEN = os.environ["CPANEL_TOKEN"]
ROOT = os.environ["THEME_ROOT"].strip("/")
CTX = ssl._create_unverified_context()
STAMP = time.strftime("%Y%m%d-%H%M%S", time.gmtime())


def call(func, params, post=False):
    url = f"https://{HOST}:2083/execute/Fileman/{func}"
    encoded = urllib.parse.urlencode(params).encode()
    last = None
    for attempt in range(1, 6):
        try:
            req = urllib.request.Request(
                url if post else url + "?" + encoded.decode(),
                data=encoded if post else None,
                method="POST" if post else "GET",
            )
            req.add_header("Authorization", f"cpanel {USER}:{TOKEN}")
            if post:
                req.add_header("Content-Type", "application/x-www-form-urlencoded")
            with urllib.request.urlopen(req, context=CTX, timeout=75) as response:
                payload = json.loads(response.read().decode("utf-8"))
            result = payload.get("result") if isinstance(payload.get("result"), dict) else payload
            if not isinstance(result, dict) or result.get("status") != 1:
                raise RuntimeError(str(result.get("errors") if isinstance(result, dict) else "UAPI failed"))
            return result.get("data")
        except Exception as exc:
            last = exc
            print(f"Attempt {attempt}/5 failed for {func}: {exc}")
            if attempt < 5:
                time.sleep(attempt * 4)
    raise last


def get_file(rel):
    parent, name = rel.rsplit("/", 1) if "/" in rel else ("", rel)
    directory = ROOT if not parent else f"{ROOT}/{parent}"
    data = call(
        "get_file_content",
        {"dir": directory, "file": name, "from_charset": "_DETECT_", "to_charset": "utf-8"},
    )
    if isinstance(data, dict):
        for key in ("content", "file_content", "data"):
            if isinstance(data.get(key), str):
                return data[key]
    if isinstance(data, str):
        return data
    raise RuntimeError(f"Unexpected content for {rel}")


def save_file(rel, content):
    parent, name = rel.rsplit("/", 1) if "/" in rel else ("", rel)
    directory = ROOT if not parent else f"{ROOT}/{parent}"
    call(
        "save_file_content",
        {
            "dir": directory,
            "file": name,
            "content": content,
            "from_charset": "UTF-8",
            "to_charset": "UTF-8",
            "fallback": "0",
        },
        post=True,
    )


header = get_file("header.php")
gallery_rel = "assets/js/product-runtime-gallery-fix.js"
gallery = get_file(gallery_rel)

save_file(f"header.php.bak-mobilefix-{STAMP}", header)
save_file(f"assets/js/product-runtime-gallery-fix.js.bak-mobilefix-{STAMP}", gallery)
print("Backups created:", STAMP)

mobile_css = """/* GRAMISS_MOBILE_VIEWPORT_FIX_V1 */
@media (max-width: 860px){
  html,
  body{
    width:100%!important;
    max-width:100%!important;
    overflow-x:hidden!important;
    overflow-x:clip!important;
    overscroll-behavior-x:none!important;
  }
  body{
    margin-left:0!important;
    margin-right:0!important;
  }
  #page,
  .site,
  .site-content,
  #content,
  #primary,
  main.site-main{
    max-width:100%!important;
    min-width:0!important;
  }
  header,
  .site-header{
    max-width:100%!important;
  }
  img,
  svg,
  video,
  canvas{
    max-width:100%;
  }
}
"""
save_file("assets/css/mobile-viewport-fix.css", mobile_css)

marker_start = "<!-- GRAMISS MOBILE VIEWPORT FIX START -->"
marker_end = "<!-- GRAMISS MOBILE VIEWPORT FIX END -->"
loader = (
    marker_start
    + "\n"
    + '<link rel="stylesheet" id="gramiss-mobile-viewport-fix-css" '
    + 'href="<?php echo esc_url( get_stylesheet_directory_uri() . \'/assets/css/mobile-viewport-fix.css?v=20260817-2\' ); ?>" '
    + 'media="(max-width: 860px)">\n'
    + marker_end
)

if marker_start in header and marker_end in header:
    before, rest = header.split(marker_start, 1)
    _, after = rest.split(marker_end, 1)
    header = before + loader + after
elif "</head>" in header:
    header = header.replace("</head>", loader + "\n</head>", 1)
else:
    raise RuntimeError("header.php has no closing head tag; refusing blind injection")

needle = "      thumb.addEventListener('click',activate,true);\n      thumb.addEventListener('keydown',function(event){"
replacement = """      thumb.addEventListener('click',activate,true);

      var g3TouchStartX=0,g3TouchStartY=0,g3TouchMoved=false;
      thumb.addEventListener('touchstart',function(event){
        var touch=event.changedTouches&&event.changedTouches[0];
        if(!touch) return;
        g3TouchStartX=touch.clientX;
        g3TouchStartY=touch.clientY;
        g3TouchMoved=false;
      },{capture:true,passive:true});
      thumb.addEventListener('touchmove',function(event){
        var touch=event.changedTouches&&event.changedTouches[0];
        if(!touch) return;
        if(Math.abs(touch.clientX-g3TouchStartX)>10 || Math.abs(touch.clientY-g3TouchStartY)>10){
          g3TouchMoved=true;
        }
      },{capture:true,passive:true});
      thumb.addEventListener('touchend',function(event){
        if(g3TouchMoved) return;
        activate(event);
      },{capture:true,passive:false});

      thumb.addEventListener('keydown',function(event){"""

if "g3TouchStartX" not in gallery:
    if needle not in gallery:
        raise RuntimeError("Gallery thumbnail click signature not found; refusing blind patch")
    gallery = gallery.replace(needle, replacement, 1)

if "/* GRAMISS_PDP_GALLERY_SWITCH_V3 */" in gallery:
    gallery = gallery.replace(
        "/* GRAMISS_PDP_GALLERY_SWITCH_V3 */",
        "/* GRAMISS_PDP_GALLERY_SWITCH_V4_MOBILE_TAP */",
        1,
    )
elif "GRAMISS_PDP_GALLERY_SWITCH_V4_MOBILE_TAP" not in gallery:
    raise RuntimeError("Expected gallery version marker not found")

save_file(gallery_rel, gallery)

header = re.sub(
    r"product-runtime-gallery-fix\.js\?v=[0-9A-Za-z._-]+",
    "product-runtime-gallery-fix.js?v=20260817-4",
    header,
)
save_file("header.php", header)

live_header = get_file("header.php")
live_css = get_file("assets/css/mobile-viewport-fix.css")
live_gallery = get_file(gallery_rel)

checks = {
    "mobile CSS marker": "GRAMISS_MOBILE_VIEWPORT_FIX_V1" in live_css,
    "viewport overflow clamp": "overflow-x:clip!important" in live_css,
    "mobile CSS loader": "gramiss-mobile-viewport-fix-css" in live_header,
    "gallery v4 marker": "GRAMISS_PDP_GALLERY_SWITCH_V4_MOBILE_TAP" in live_gallery,
    "touch start handler": "g3TouchStartX" in live_gallery,
    "touch end activation": "thumb.addEventListener('touchend'" in live_gallery,
    "gallery cache bust": "product-runtime-gallery-fix.js?v=20260817-4" in live_header,
}

for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)

if not all(checks.values()):
    raise SystemExit("Mobile fix verification failed")

print("LIVE MOBILE VIEWPORT + PDP THUMB TAP FIX DEPLOYED AND VERIFIED")
