# GRAMISS SEO BIBLE

Status: Working source of truth
Baseline audit: 2026-08-29
Scope: WordPress + WooCommerce production at gramiss.ir

## Business objective
SEO exists to create qualified discovery and revenue, not vanity traffic. Decisions are evaluated through crawl/index health, impressions, CTR, product/category engagement, add-to-cart, checkout and organic revenue.

## Operating order
1. Product/catalog data integrity
2. URL + crawl/index foundation
3. Metadata/canonical/social/schema
4. Category money pages
5. Product-page enrichment
6. Keyword map + content clusters
7. Merchant/Search integrations
8. Measurement and continuous optimization

## Safety rules
- Never invent commercial facts: price, stock, color, size, material, brand, GTIN/MPN or SKU.
- Never bulk-change live URLs without an old->new map, permanent redirects, canonical verification, sitemap refresh and internal-link verification.
- Never create indexable filter/sort/cart/checkout/account/search pages by accident.
- Preserve WooCommerce product/variation relationships and native checkout behavior.
- All bulk mutations require a dry-run report and rollback/backup path.
- Draft products are excluded from SEO publishing work unless explicitly requested.

## Indexation policy
Index candidates:
- Home
- Shop / primary commerce landing pages
- Published product categories with real inventory/content
- Published products
- Editorial articles with unique search intent

Noindex candidates:
- Cart
- Checkout
- Account/auth
- Internal search result pages
- Wishlist/compare utility pages unless a future business case explicitly changes this
- Thin filter/sort/faceted combinations

## Product URL policy
Current production baseline uses query URLs because WordPress `permalink_structure` is empty.
Before migration, define the final stable structure and produce a full redirect map. Do not mass-edit product slugs independently of the migration.

## Product data contract
Every published product should ultimately have:
- Stable product ID
- Canonical product name
- Stable slug
- Product type
- Primary category + justified secondary categories
- Base/internal SKU policy
- Variation SKU for every sellable variation
- Price for every sellable variation
- Stock status/quantity
- Color/size attributes using global taxonomies where applicable
- Featured image + gallery
- Useful image alt text
- Product description containing only verified facts
- Short description / buying summary
- SEO title
- Meta description
- Canonical
- Social preview data
- Valid Product structured data (WooCommerce output must not be duplicated)

## 2026-08-29 production baseline
WooCommerce product posts: 56
Published products: 48
Draft/non-public products: 8
Total variations found: 159
Active SEO plugin: Rank Math
WordPress permalink_structure: empty
WooCommerce product base: product
WooCommerce category base: product-category

Catalog issues detected across all 56 product posts:
- Parent SKU missing: 56
- Product description missing: 4
- Short description missing: 55
- Featured image missing: 8 (primarily drafts)
- Empty image alt values: 139
- Products with at least one empty image alt: 48
- Products without category: 5 (draft-side issues observed)
- Query-style product URLs: 48 (the published catalog)
- Explicit per-product SEO title meta missing: 56
- Explicit per-product SEO description meta missing: 56
- Explicit per-product SEO canonical meta missing: 56
- Variation SKU missing: 14 total (includes draft variations)
- Variation price missing: 6 total (includes draft variations)
- Out-of-stock variations: 5

### Confirmed live-data issues requiring attention
- Published product variation 213 (product 210) has no price while sibling variation is priced.
- Published product variation 346 (product 344) has no price while sibling variation is priced.
- Published product 49 has 2 variation SKUs missing.
- Published product 97 has 5 variation SKUs missing.
- Published product 141 has 3 variation SKUs missing.
- All 48 published products have at least one product image with empty alt text.

### Human-review candidates (do not auto-correct blindly)
- Duplicate/near-duplicate product names exist, including products 296/307/320 and 359/366; likely variants/colors/materials must be differentiated using verified facts.
- Product 355 is named as long-sleeve but is assigned to a short-sleeve category; review required.
- Some product/category naming and slugs contain apparent typos or inconsistent transliteration. Preserve print/brand wording when intentional; only correct verified mistakes.
- Some products have overlapping category assignments that may be intentional or mistaken; review taxonomy before bulk normalization.

## Automation policy for Codex/scripts
Safe to automate after dry-run:
- Inventory/audit generation
- Missing-alt proposal generation
- SEO title/description proposal generation from verified fields
- Duplicate-title detection
- Taxonomy anomaly detection
- SKU-gap detection
- Price-gap detection (flag only unless price source is authoritative)
- Redirect-map generation
- Canonical/sitemap/robots QA
- Schema QA

Requires human/authoritative confirmation before write:
- Price
- Stock
- Material
- Product identity/brand claims
- Category changes where intent is ambiguous
- Product-name corrections that may alter printed model/design names
- URL migration final structure

## Definition of done for SEO Foundation V1
- Pretty permalink architecture enabled and verified
- Old product/category URLs permanently redirect to canonical URLs without chains
- robots.txt valid
- XML sitemap valid and contains only intended canonical pages
- Canonicals correct
- System/utility pages noindex
- One logical H1 per money page
- Rank Math global templates configured intentionally
- Product metadata and social previews populated via verified templates/data
- Product structured data validates without duplicate conflicting markup
- Published categories have deliberate index/noindex decisions
- Product images have useful alt strategy
- Search Console / measurement layer ready for post-migration monitoring
