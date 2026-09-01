"""Read-only public audit for the live Gramiss editorial foundation.

This script deliberately uses only public HTTP endpoints. It never authenticates,
uploads a probe, changes WordPress, or writes a local report file.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


BASE = "https://gramiss.ir"
EXPECTED_IDS = [453, 459, 460, 463, 464, 467, 468, 471, 472]
EXPECTED_TITLES = {
    453: "تیشرت باکسی چیست و چه تفاوتی با اورسایز دارد؟",
    459: "راهنمای انتخاب سایز تیشرت باکسی مردانه؛ اندازه‌گیری و فیت مناسب",
    460: "تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ کدام فیت مناسب شماست؟",
    463: "پارچه لینن چیست؟ راهنمای شناخت، چروک و انتخاب لباس لینن",
    464: "شست‌وشوی پیراهن لینن مردانه؛ راهنمای خشک‌کردن و اتوکشی",
    467: "استایل با پیراهن لینن مردانه؛ شلوار، کفش و ترکیب رنگ",
    468: "با شلوار بگ مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و قد شلوار",
    471: "راهنمای خرید تیشرت مردانه؛ فیت، اندازه، پارچه، دوخت و چاپ",
    472: "راهنمای خرید شلوار جین مردانه؛ فیت، قد، پارچه و جزئیات",
}
EXPECTED_CATEGORIES = {
    "fit-size-guide": 3,
    "fabric-care": 2,
    "style-guide": 2,
    "buying-guide": 2,
}
EXPECTED_PRODUCT_SITEMAP_SHA = (
    "70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3"
)
CTX = ssl.create_default_context()


def request(url: str, timeout: int = 90) -> tuple[int, bytes, str, dict[str, str]]:
    parsed = urllib.parse.urlsplit(url)
    wire_url = urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc.encode("idna").decode("ascii"),
            urllib.parse.quote(urllib.parse.unquote(parsed.path), safe="/%:@"),
            urllib.parse.quote_plus(
                urllib.parse.unquote_plus(parsed.query), safe="=&,:"
            ),
            "",
        )
    )
    req = urllib.request.Request(
        wire_url,
        headers={
            "User-Agent": "GramissEditorialPublicAuditV3/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    last: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as response:
                return (
                    response.status,
                    response.read(),
                    response.geturl(),
                    dict(response.headers),
                )
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), exc.geturl(), dict(exc.headers)
        except Exception as exc:  # pragma: no cover - network dependent
            last = exc
            if attempt < 3:
                time.sleep(attempt * 2)
    raise RuntimeError(f"request failed: {url}: {last}")


def get_json(url: str) -> object:
    status, raw, _, _ = request(url)
    if status != 200:
        raise RuntimeError(f"JSON endpoint returned {status}: {url}")
    return json.loads(raw.decode("utf-8", "replace"))


def norm(url: str) -> str:
    parsed = urllib.parse.urlsplit(html.unescape(url))
    path = urllib.parse.unquote(parsed.path or "/")
    path = re.sub(r"/+", "/", path)
    if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
        path += "/"
    host = (parsed.hostname or "").lower()
    scheme = parsed.scheme.lower() or "https"
    return urllib.parse.urlunsplit((scheme, host, path, "", ""))


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta_description = ""
        self.canonical = ""
        self.robots = ""
        self.h1: list[str] = []
        self.h2: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.article_links: list[tuple[str, str]] = []
        self.article_text: list[str] = []
        self._capture: str | None = None
        self._capture_text: list[str] = []
        self._link_href = ""
        self._link_text: list[str] = []
        self._article_depth = 0
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "article":
            self._article_depth += 1
        if tag in {"title", "h1", "h2"}:
            self._capture = tag
            self._capture_text = []
        if tag == "meta":
            name = attr.get("name", "").lower()
            if name == "description":
                self.meta_description = attr.get("content", "").strip()
            elif name == "robots":
                self.robots = attr.get("content", "").strip()
        if tag == "link" and "canonical" in attr.get("rel", "").lower().split():
            self.canonical = attr.get("href", "").strip()
        if tag == "a":
            self._link_href = attr.get("href", "").strip()
            self._link_text = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"title", "h1", "h2"} and self._capture == tag:
            value = re.sub(r"\s+", " ", " ".join(self._capture_text)).strip()
            if tag == "title":
                self.title = value
            elif tag == "h1" and value:
                self.h1.append(value)
            elif tag == "h2" and value:
                self.h2.append(value)
            self._capture = None
            self._capture_text = []
        if tag == "a" and self._link_href:
            text = re.sub(r"\s+", " ", " ".join(self._link_text)).strip()
            row = (self._link_href, text)
            self.links.append(row)
            if self._article_depth:
                self.article_links.append(row)
            self._link_href = ""
            self._link_text = []
        if tag == "article" and self._article_depth:
            self._article_depth -= 1
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if not value:
            return
        if self._capture:
            self._capture_text.append(value)
        if self._link_href:
            self._link_text.append(value)
        if self._article_depth and not self._skip_depth:
            self.article_text.append(value)


def parse_page(raw: bytes) -> tuple[PageParser, str]:
    text = raw.decode("utf-8", "replace")
    parser = PageParser()
    parser.feed(text)
    return parser, text


def sitemap(path: str) -> tuple[int, list[str]]:
    status, raw, _, _ = request(f"{BASE}/{path}?audit={int(time.time())}")
    urls = [
        html.unescape(value.decode("utf-8", "replace").strip())
        for value in re.findall(rb"<loc>(.*?)</loc>", raw, re.I)
    ]
    return status, urls


def public_posts() -> list[dict[str, object]]:
    include = ",".join(str(post_id) for post_id in EXPECTED_IDS)
    fields = "id,status,slug,link,title,categories"
    url = (
        f"{BASE}/wp-json/wp/v2/posts?include={include}&per_page=100"
        f"&_fields={urllib.parse.quote(fields, safe=',')}"
    )
    data = get_json(url)
    return data if isinstance(data, list) else []


def public_categories() -> dict[int, dict[str, object]]:
    slugs = ",".join(EXPECTED_CATEGORIES)
    fields = "id,count,link,name,slug"
    url = (
        f"{BASE}/wp-json/wp/v2/categories?slug={slugs}&per_page=100"
        f"&_fields={urllib.parse.quote(fields, safe=',')}"
    )
    data = get_json(url)
    if not isinstance(data, list):
        return {}
    return {int(row["id"]): row for row in data if isinstance(row, dict) and "id" in row}


def internal_urls(links: list[tuple[str, str]], base_url: str) -> list[tuple[str, str]]:
    output: list[tuple[str, str]] = []
    for href, anchor in links:
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urllib.parse.urljoin(base_url, href)
        if urllib.parse.urlsplit(absolute).hostname in {"gramiss.ir", "www.gramiss.ir"}:
            output.append((norm(absolute.replace("www.gramiss.ir", "gramiss.ir")), anchor))
    return output


def main() -> int:
    errors: list[str] = []
    posts = public_posts()
    categories = public_categories()
    posts_by_id = {int(row["id"]): row for row in posts}
    category_by_slug = {str(row["slug"]): row for row in categories.values()}

    if set(posts_by_id) != set(EXPECTED_IDS):
        errors.append(f"public REST post IDs drift: {sorted(posts_by_id)}")

    article_urls = {
        post_id: norm(str(posts_by_id[post_id]["link"]))
        for post_id in EXPECTED_IDS
        if post_id in posts_by_id
    }
    article_url_set = set(article_urls.values())
    category_urls = {
        slug: norm(str(row.get("link", "")))
        for slug, row in category_by_slug.items()
    }
    category_url_set = set(category_urls.values())

    article_results: dict[int, dict[str, object]] = {}
    all_contextual_targets: set[str] = set()
    for post_id in EXPECTED_IDS:
        post = posts_by_id.get(post_id)
        if not post:
            continue
        expected_title = EXPECTED_TITLES[post_id]
        rest_title = html.unescape(str((post.get("title") or {}).get("rendered", "")))
        url = article_urls[post_id]
        status, raw, final, _ = request(f"{url}?audit={int(time.time())}")
        page, source = parse_page(raw)
        contextual = internal_urls(page.article_links or page.links, final)
        targets = {target for target, _ in contextual if target != url}
        all_contextual_targets.update(targets)
        editorial_targets = sorted(targets & article_url_set)
        category_targets = sorted(targets & category_url_set)
        commerce_targets = sorted(
            target
            for target in targets
            if target not in article_url_set
            and target not in category_url_set
            and target != norm(f"{BASE}/وبلاگ/")
            and not urllib.parse.urlsplit(target).path.startswith("/wp-content/")
        )
        category_ids = {int(value) for value in post.get("categories", [])}
        assigned_slugs = sorted(
            str(categories[value]["slug"]) for value in category_ids if value in categories
        )
        robots = page.robots.lower()
        word_count = len(re.findall(r"[\w\u0600-\u06ff]+", " ".join(page.article_text)))
        has_blogposting = bool(re.search(r'"@type"\s*:\s*"BlogPosting"', source, re.I))
        has_product = bool(re.search(r'"@type"\s*:\s*"Product"', source, re.I))
        row = {
            "status": status,
            "final": norm(final),
            "rest_title": rest_title,
            "meta_title": page.title,
            "meta_description": page.meta_description,
            "canonical": page.canonical,
            "robots": page.robots,
            "h1": page.h1,
            "h2": page.h2,
            "article_word_count": word_count,
            "blogposting": has_blogposting,
            "product_schema": has_product,
            "categories": assigned_slugs,
            "editorial_targets": editorial_targets,
            "category_targets": category_targets,
            "commerce_targets": commerce_targets,
        }
        article_results[post_id] = row
        if status != 200:
            errors.append(f"article {post_id} HTTP {status}")
        if norm(final) != url:
            errors.append(f"article {post_id} final URL drift")
        if rest_title != expected_title or expected_title not in page.h1:
            errors.append(f"article {post_id} H1/title drift")
        if word_count < 700:
            errors.append(f"article {post_id} body appears thin ({word_count} words)")
        if len(page.h2) < 8:
            errors.append(f"article {post_id} H2 structure is thin ({len(page.h2)})")
        if not page.title or not page.meta_description:
            errors.append(f"article {post_id} metadata missing")
        if norm(page.canonical) != url:
            errors.append(f"article {post_id} canonical mismatch")
        if "noindex" in robots or "index" not in robots or "follow" not in robots:
            errors.append(f"article {post_id} robots mismatch")
        if not has_blogposting or has_product:
            errors.append(f"article {post_id} schema mismatch")
        if len(assigned_slugs) != 1 or assigned_slugs[0] not in EXPECTED_CATEGORIES:
            errors.append(f"article {post_id} category mismatch: {assigned_slugs}")
        if not editorial_targets:
            errors.append(f"article {post_id} has no contextual editorial link")

    incoming = {post_id: [] for post_id in EXPECTED_IDS}
    id_by_url = {url: post_id for post_id, url in article_urls.items()}
    for source_id, row in article_results.items():
        for target in row["editorial_targets"]:
            target_id = id_by_url.get(str(target))
            if target_id:
                incoming[target_id].append(source_id)
    for post_id, sources in incoming.items():
        if not sources:
            errors.append(f"article {post_id} has no incoming editorial link")

    category_results: dict[str, dict[str, object]] = {}
    for slug, expected_count in EXPECTED_CATEGORIES.items():
        row = category_by_slug.get(slug)
        if not row:
            errors.append(f"category missing: {slug}")
            continue
        url = category_urls[slug]
        status, raw, final, _ = request(f"{url}?audit={int(time.time())}")
        page, _ = parse_page(raw)
        links = {target for target, _ in internal_urls(page.links, final)}
        visible_articles = sorted(links & article_url_set)
        robots = page.robots.lower()
        result = {
            "status": status,
            "final": norm(final),
            "rest_count": int(row.get("count", -1)),
            "visible_articles": visible_articles,
            "canonical": page.canonical,
            "robots": page.robots,
        }
        category_results[slug] = result
        if status != 200 or norm(final) != url:
            errors.append(f"category {slug} HTTP/final URL mismatch")
        if int(row.get("count", -1)) != expected_count or len(visible_articles) != expected_count:
            errors.append(f"category {slug} count mismatch")
        if norm(page.canonical) != url:
            errors.append(f"category {slug} canonical mismatch")
        if "noindex" in robots or "index" not in robots or "follow" not in robots:
            errors.append(f"category {slug} robots mismatch")

    blog_url = norm(f"{BASE}/وبلاگ/")
    blog_status, blog_raw, blog_final, _ = request(f"{blog_url}?audit={int(time.time())}")
    blog_page, _ = parse_page(blog_raw)
    blog_links = {target for target, _ in internal_urls(blog_page.links, blog_final)}
    blog_articles = sorted(blog_links & article_url_set)
    blog_robots = blog_page.robots.lower()
    blog_result = {
        "status": blog_status,
        "final": norm(blog_final),
        "canonical": blog_page.canonical,
        "robots": blog_page.robots,
        "visible_articles": blog_articles,
    }
    if blog_status != 200 or norm(blog_final) != blog_url:
        errors.append("blog root HTTP/final URL mismatch")
    if norm(blog_page.canonical) != blog_url:
        errors.append("blog root canonical mismatch")
    if "noindex" in blog_robots or "index" not in blog_robots or "follow" not in blog_robots:
        errors.append("blog root robots mismatch")
    if set(blog_articles) != article_url_set:
        errors.append(f"blog root exposes {len(blog_articles)} of {len(article_url_set)} articles")

    post_status, post_urls = sitemap("post-sitemap.xml")
    category_status, category_sitemap_urls = sitemap("category-sitemap.xml")
    product_status, product_urls = sitemap("product-sitemap.xml")
    product_cat_status, product_cat_urls = sitemap("product_cat-sitemap.xml")
    # Keep this checksum byte-for-byte compatible with Audit V2. Decoding the
    # sitemap URLs before hashing would create a false drift signal.
    product_sha = hashlib.sha256("\n".join(sorted(product_urls)).encode()).hexdigest()
    post_normalized = {norm(value) for value in post_urls}
    category_normalized = {norm(value) for value in category_sitemap_urls}
    if post_status != 200 or len(post_urls) != 10:
        errors.append(f"post sitemap mismatch: status={post_status} count={len(post_urls)}")
    if not article_url_set.issubset(post_normalized) or blog_url not in post_normalized:
        errors.append("post sitemap is missing editorial URLs")
    if category_status != 200 or len(category_sitemap_urls) != 4:
        errors.append(
            f"category sitemap mismatch: status={category_status} count={len(category_sitemap_urls)}"
        )
    if not category_url_set.issubset(category_normalized):
        errors.append("category sitemap is missing editorial category URLs")
    if product_status != 200 or len(product_urls) != 47:
        errors.append(f"product sitemap mismatch: status={product_status} count={len(product_urls)}")
    if product_sha != EXPECTED_PRODUCT_SITEMAP_SHA:
        errors.append(f"product sitemap SHA drift: {product_sha}")

    broken_targets: list[dict[str, object]] = []
    for target in sorted(all_contextual_targets):
        status, _, final, _ = request(f"{target}?audit={int(time.time())}")
        if status >= 400:
            broken_targets.append({"target": target, "status": status, "final": final})
    if broken_targets:
        errors.append(f"broken contextual internal links: {len(broken_targets)}")

    report = {
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "articles": article_results,
        "incoming_editorial_links": incoming,
        "categories": category_results,
        "blog": blog_result,
        "sitemaps": {
            "post": {"status": post_status, "count": len(post_urls), "urls": post_urls},
            "category": {
                "status": category_status,
                "count": len(category_sitemap_urls),
                "urls": category_sitemap_urls,
            },
            "product": {
                "status": product_status,
                "count": len(product_urls),
                "sha256": product_sha,
            },
            "product_cat": {
                "status": product_cat_status,
                "count": len(product_cat_urls),
                "urls": product_cat_urls,
            },
        },
        "broken_contextual_targets": broken_targets,
        "errors": errors,
        "result": "PASS" if not errors else "FAIL",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
