# GRAMISS SEO BIBLE

Status: Working source of truth
Baseline audit: 2026-08-29
Current checkpoint: 2026-09-02
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
Current production uses WordPress pretty permalinks with `/%postname%/`.

Canonical product URLs use:

`/product/<stable-product-slug>/`

Product categories preserve native WooCommerce hierarchical paths under `/product-category/`.

Legacy query URLs are redirect-backed to the pretty canonical URLs through the guarded migration map. Do not change an indexed product slug casually. Any future product URL change requires an explicit old->new map, permanent redirect, self-canonical verification, sitemap refresh and internal-link verification.

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

## Product-entry authority — V1

New products are governed by the dedicated product-entry stack rather than ad-hoc WooCommerce entry:

- `docs/GRAMISS-PRODUCT-ENTRY-STANDARD-V1.md` — human-readable source of truth
- `config/gramiss-product-entry-schema-v1.json` — machine-readable intake contract
- `.ops/validate-product-intake-v1.py` — pre-WooCommerce payload validator
- `.ops/product-prepublish-gate-v1.py` — live WooCommerce pre/post-publish gate
- `.github/workflows/product-prepublish-gate-v1.yml` — manual strict/report workflow
- `docs/GRAMISS-PRODUCT-INTAKE-V1.md` — operating procedure

Required sequence for new inventory:

1. authoritative product facts -> intake payload;
2. intake validator PASS;
3. WooCommerce product creation/configuration;
4. pre-publish Gate PASS;
5. publish;
6. post-publish Gate PASS.

Legacy catalogue debt does not weaken the requirements for newly entered products.

## 2026-09-02 product remediation checkpoint

Guarded legacy short-description remediation is complete for the current safe/indexable product inventory. The detailed operational record is preserved in `docs/PRODUCT-LEGACY-REMEDIATION-V1-CHECKPOINT.md`.

Current verified state:

- Published products: 48
- Products with verified short descriptions: 41
- Remaining empty short descriptions: 6
- Safe/indexable products still eligible for automated short-description remediation: 0
- Product Sitemap: 47 URLs, unchanged; SHA `70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3`
- Product category sitemap: 20 URLs, unchanged; SHA `75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4`
- Home / Gramiss Looks protected files remained unchanged through the remediation workflow
- Product `62` and product `68` remain explicit legacy `noindex` products and remain outside the indexable remediation set

The four indexable products that still have empty short descriptions are intentionally blocked by missing authoritative WooCommerce variation data:

- product `97` — missing variation SKUs on `108`, `109`, `110`, `111`, `112`; parent/master SKU also missing
- product `141` — missing variation SKUs on `144`, `145`, `146`; parent/master SKU also missing
- product `210` — variation `213` has no price; parent/master SKU also missing
- product `344` — variation `346` has no price; parent/master SKU also missing

The two other remaining empty-description products are intentionally noindex:

- product `62` — کلاه فیت کپ GIANTS نارنجی
- product `68` — کلاه فیت کپ BOSTON

Do not manufacture SKU or price data to clear these blockers, and do not add SEO copy to noindex products merely to make the remediation counter reach zero. Revisit these six only when authoritative product data or an intentional indexability decision changes.

The remediation publisher used guarded, reversible, excerpt-only writes. Final verification required HTTP 200, expected meta description, self-canonical, index/follow for remediated products, exactly one Product schema, unchanged sitemap membership/checksums and exact protected UI hashes.

Parent/master SKU debt remains a broader catalog-data issue and was not auto-filled. Variation SKU/price gaps elsewhere in the catalogue remain governed by the Product Entry contract and authoritative-data rule even when a product already has a short description.

## 2026-09-01 current production product state

Read-only Product Entry Readiness Audit V1 and Product Indexability Diagnosis V1 confirmed:

- Published products: 48
- Draft/non-public products: 8
- Published variable products: 45
- Published simple products: 3
- Published variations: 149
- All 48 published product pages: HTTP 200
- Product schema: exactly one Product object on every published product page
- Published product image-alt gaps: 0
- Published products missing featured image: 0
- Published products missing full description: 0
- Published products missing short description: 47
- Published parent/master SKU missing: 48
- Published variation SKU missing: 10
- Published variation price missing: 2
- Out-of-stock published variations: 5
- Product `62` and product `68`: explicit legacy `noindex, follow`, no rendered canonical, intentionally excluded by Rank Math from Product Sitemap under their current state
- Product Sitemap: 47 URLs = 45 indexable products + `/shop/`
- Product Sitemap checksum remained protected during the editorial/content work

Known authoritative-data blockers still requiring merchant/source data:

- variation `213` under product `210`: no price
- variation `346` under product `344`: no price
- product `49`: variation SKUs missing on variations `50` and `52`
- additional variation-SKU gaps remain in the published catalogue, including products `97` and `141`
- parent/master SKU convention/data is not yet populated across the published catalogue

These values must not be guessed from sibling products or generated arbitrarily.

## 2026-08-29 historical production baseline
WooCommerce product posts: 56
Published products: 48
Draft/non-public products: 8
Total variations found: 159
Active SEO plugin: Rank Math
WordPress permalink_structure at that baseline: empty
WooCommerce product base: product
WooCommerce category base: product-category

Catalog issues detected across all 56 product posts at that baseline:
- Parent SKU missing: 56
- Product description missing: 4
- Short description missing: 55
- Featured image missing: 8 (primarily drafts)
- Empty image alt values: 139
- Products with at least one empty image alt: 48
- Products without category: 5 (draft-side issues observed)
- Query-style product URLs: 48 (the published catalog at that time)
- Explicit per-product SEO title meta missing: 56
- Explicit per-product SEO description meta missing: 56
- Explicit per-product SEO canonical meta missing: 56
- Variation SKU missing: 14 total (includes draft variations)
- Variation price missing: 6 total (includes draft variations)
- Out-of-stock variations: 5

The historical alt/URL findings above have since been remediated or migrated where noted by the 2026-09-01 current-state section. Do not treat historical counts as current production defects.

### Human-review candidates (do not auto-correct blindly)
- Duplicate/near-duplicate product names exist, including products 296/307/320 and 359/366; likely variants/colors/materials must be differentiated using verified facts.
- Product 355 is named as long-sleeve but is assigned to a short-sleeve category; review required.
- Some product/category naming and slugs contain apparent typos or inconsistent transliteration. Preserve print/brand wording when intentional; only correct verified mistakes.
- Some products have overlapping category assignments that may be intentional or mistaken; review taxonomy before bulk normalization.
- Product category 217 language/slug consistency remains a review item, not an automatic rename.

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
- Product-intake structural validation
- Pre/post-publish product gate checks

Requires human/authoritative confirmation before write:
- Price
- Stock
- Material
- SKU values when the authoritative SKU convention/source is unavailable
- Product identity/brand claims
- Category changes where intent is ambiguous
- Product-name corrections that may alter printed model/design names
- URL changes after publication/indexing

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
- New products pass the Gramiss Product Intake + Pre-Publish + Post-Publish contract
- Search Console / measurement layer ready for post-migration monitoring
