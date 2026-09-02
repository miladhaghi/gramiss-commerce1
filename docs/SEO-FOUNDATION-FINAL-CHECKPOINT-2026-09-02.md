# Gramiss SEO Foundation — Final Checkpoint

Date: 2026-09-02
Branch: `ops/seo-content-architecture-v1`
Pre-checkpoint HEAD: `13f9f6609ef2ed8eaba304d49142a24a4ee69245`
Status: INITIAL SEO FOUNDATION COMPLETE, subject to the final permanent read-only workflow on this checkpoint commit.

## 1. Editorial foundation

- Published editorial articles: 19
- Magazine root: `/وبلاگ/`
- Editorial category counts:
  - `fit-size-guide`: 7
  - `fabric-care`: 4
  - `style-guide`: 4
  - `buying-guide`: 4
- Post Sitemap: 20 URLs (magazine root + 19 articles)
- Editorial Category Sitemap: 4 URLs
- Required public behavior for every article:
  - HTTP 200
  - self canonical
  - index/follow
  - BlogPosting schema
  - no Product schema
  - valid editorial internal links
- Authoritative audit: `.ops/editorial-foundation-audit-v7.py`

This completes the planned initial 19-article foundation. Do not continue publishing serial articles simply to increase article count. Future content should be driven by real search opportunity and Search Console data.

## 2. Product category / money-page foundation

All 20 URLs in `product_cat-sitemap.xml` are now passing the category money-page audit.

Final verified summary:

`{"P0":0,"P1":0,"P2":0,"PASS":20,"total":20}`

Required state now established across the 20 product categories:

- HTTP 200
- exactly one H1
- native WooCommerce duplicate page-title H1 removed from product-category archives
- visible Gramiss Premium Hero H1 retained
- index/follow
- self canonical
- useful SEO title + meta description
- category copy rendered after the product grid, not as a long default description before the hero
- contextual internal links to relevant editorial/commercial pages
- no Product Sitemap or Product Category Sitemap drift

Authoritative audit:

`.ops/category-money-page-audit-v1.py`

### H1 implementation note

WooCommerce 11.0.1 generated the native archive H1 from `woocommerce_content()`. The production theme now disables that native page title only for `is_product_category()` early enough in `woocommerce.php`, leaving the Gramiss premium H1 as the single H1.

Current protected category shell baselines:

- `woocommerce.php`
  - SHA256 `4f518fdbc1fdf84c2b4efb065af1129345d56fe121b2a67e8ab78a7e9719c21b`
- `assets/css/shop-premium-shell.css`
  - SHA256 `b20eba9bedbe2dc0f1115b4b63dd7deff1eaf6cb9dcfb17801d0e803eb8a21e2`

## 3. Product Intake Architecture V1

The new-product contract is active and is the required baseline for new catalogue entries.

Sources of truth:

- `docs/GRAMISS-PRODUCT-ENTRY-STANDARD-V1.md`
- `docs/GRAMISS-PRODUCT-INTAKE-V1.md`
- `config/gramiss-product-entry-schema-v1.json`
- `.ops/validate-product-intake-v1.py`
- `.ops/product-prepublish-gate-v1.py`

New products must not be published until the applicable gate requirements are satisfied, including verified identity, taxonomy/type, master SKU, variation SKUs, authoritative prices, stock state, attributes, media/alt, full + short description, indexation decision, canonical/schema/sitemap QA.

Do not invent SKU, price, material composition, brand/authenticity claims, taxonomy intent, or other unavailable commercial facts.

## 4. Legacy product remediation

Safely remediated published/indexable products: 41.

Remaining legacy blockers: 6. These are intentionally NOT auto-fixed.

1. Product 97 — missing variation SKU; authoritative SKU required.
2. Product 141 — missing variation SKU; authoritative SKU required.
3. Product 210 — variation 213 missing price; authoritative price required.
4. Product 344 — variation 346 missing price; authoritative price required.
5. Product 62 — published legacy `noindex, follow`; business/indexation decision required before changing.
6. Product 68 — published legacy `noindex, follow`; business/indexation decision required before changing.

These six items are not considered a failure of the initial SEO foundation because resolving them requires merchant/business source data rather than safe inference. They remain an explicit remediation queue.

## 5. Sitemap invariants

Product Sitemap:

- HTTP 200
- 47 URLs
- SHA256 of sorted URL set:
  `70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3`

Product Category Sitemap:

- HTTP 200
- 20 URLs
- SHA256 of sorted URL set:
  `75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4`

Do not change counts or URL sets merely to satisfy an assumption. Investigate legitimate concurrent catalogue work before treating a future checksum difference as regression.

## 6. Protected Home / Gramiss Looks baselines

SEO work must not modify these protected assets unless a separate explicitly authorized design task requires it:

- `front-page.php`
  `0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7`
- `template-parts/home-looks.php`
  `3966a35097d8d229b658b786031e95586a102201a21cf127a47f0b38ac3d364d`
- `assets/css/home-looks.css`
  `98e73735ac23de72de8350d38dd2170b8ca9f7d0fcb913156908ab701770dab0`
- `assets/js/home-looks.js`
  `6224befd75a768dea6feea70b40c42c3b54fca190d096db4c89079ccf44b6ec2`

## 7. Permanent workflow posture

Authoritative workflow:

`SEO Content Architecture V1`

Workflow ID: `346528545`

The permanent workflow is read-only with respect to editorial/category production content. It performs:

1. Product Intake / Pre-Publish Gate self-tests.
2. Editorial Foundation V7 audit.
3. Category Money Page audit with a hard requirement of `20 PASS / 0 P2 / 0 P1 / 0 P0`.

Temporary publisher and diagnostic workflows must remain manual (`workflow_dispatch`) rather than automatically publishing on every branch push.

Unrelated legacy cPanel workflows may still fail because of obsolete historical guards; they are not authoritative for SEO state.

## 8. Definition of initial SEO foundation complete

The initial foundation is complete when the final authoritative workflow on this checkpoint confirms:

- Product contract self-tests PASS.
- Editorial Foundation V7 PASS for 19 articles.
- Category Money Page Audit PASS for all 20 categories.
- Product Sitemap remains healthy.
- Product Category Sitemap remains healthy.
- protected Home/Looks hashes remain unchanged.

Once this is confirmed, the project changes from build mode to measurement/growth mode.

## 9. Operating mode after foundation

Do not continue mass-producing content.

Next SEO work should be driven by measurement:

- Google Search Console indexing/coverage status.
- queries and impressions by page.
- pages ranking near page one that can be improved.
- CTR opportunities from title/meta testing.
- content refresh based on observed query intent.
- new articles only when there is a real opportunity not already owned by an existing page.
- isolated resolution of the six legacy product blockers only after authoritative merchant data/decisions are available.

The correct long-term loop is:

`Measure -> diagnose -> prioritize -> small guarded change -> verify -> measure again`.
