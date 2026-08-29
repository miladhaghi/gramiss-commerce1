# Gramiss — Rank Math Bootstrap Diagnosis

Status: in progress

Known production state before this diagnosis:
- WordPress pretty permalinks enabled and verified.
- 48 published products and 21 active product categories resolve on pretty canonical URLs.
- Legacy query URLs redirect 301 to pretty URLs.
- `robots.txt` and WordPress native sitemap are reachable.
- Rank Math free plugin is active (`seo-by-rank-math/rank-math.php`, v1.0.276).
- Rank Math module settings include sitemap/rich-snippet/woocommerce.
- Rank Math frontend/sitemap runtime does not initialize.
- `RankMath\Admin\Registration` exists and reports `invalid=true`.
- `sitemap_index.xml` returns 404, while core `wp-sitemap.xml` returns 200.
- Rank Math OG/Twitter/description/schema output is absent on sampled frontend pages.

Goal of this batch:
1. determine the exact reason Registration is invalid from the installed production code/runtime;
2. fix only if the root cause is deterministic and reversible;
3. verify Rank Math frontend + sitemap bootstrap;
4. do not change product/catalog facts, Home UI, checkout/cart/PDP layouts, or permalink contract.
