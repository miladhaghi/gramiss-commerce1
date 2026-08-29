# Gramiss SEO URL Contract V1

Status: migration contract for SEO Foundation V1
Validated against production: 2026-08-29

## Objective
Move the live WooCommerce catalog from query URLs to stable pretty canonical URLs with the smallest possible first-migration surface.

## Final structure
- WordPress post/page permalink structure: `/%postname%/`
- Product URL: `/product/{existing-product-slug}/`
- Product category URL uses WooCommerce native hierarchical taxonomy routing:
  - top-level: `/product-category/{category-slug}/`
  - child: `/product-category/{parent-slug}/{child-slug}/`
  - deeper descendants continue the same hierarchy
- Product base stays `product`
- Product category base stays `product-category`

## First-migration slug rule
Do NOT rename published product/category slugs during the permalink migration.
Preserve the existing slug exactly, then fix verified bad/duplicate/awkward slugs in a later isolated redirect-backed batch.

Reason: changing the rewrite architecture and 48 individual slugs at the same time increases migration risk and makes rollback/diagnosis harder.

## Redirect rule
- Exact legacy `?product={old-slug}` URLs -> HTTP 301 -> mapped pretty product canonical.
- Exact legacy `?product_cat={old-slug}` URLs -> HTTP 301 -> the current native WooCommerce hierarchical category canonical.
- No redirect chains.
- Redirect mappings are retained long-term.
- Unknown query values are not redirected to Home.

## Canonical/index rules
- Pretty product/category URL becomes the self-referencing canonical after migration.
- Draft products are excluded.
- Cart, checkout, account, internal search and thin filter/sort/facet combinations are not index candidates.

## Production dry-run result
- Published products mapped: 48
- Active non-empty product categories mapped: 21
- Product URL collisions: 0
- Category URL collisions: 0
- WordPress current permalink structure before migration: empty
- Web server: LiteSpeed
- `.htaccess`: present, WordPress block present

## Deferred review (not blocking the first permalink migration)
- Product 320 has a numeric `-2` slug suffix.
- Products 296/307/320 share the same visible product title and need verified differentiation later.
- Products 359/366 share the same visible product title and need verified differentiation later.
- Category 217 uses a Persian/percent-encoded slug while most catalog category slugs are Latin.
- Product 84 has an apparent typo in its current slug (`ملاه` vs product title `کلاه`); preserve during migration, correct later with its own 301.
- Product 296 has a slug that does not cleanly match its visible title; review later using verified product identity.
- Product 355 title/category contradiction remains a taxonomy-review item and must not be auto-corrected during URL migration.

## Migration invariants
1. Backup current permalink options and `.htaccess` before write.
2. Preserve all product IDs, variation IDs, prices, stock, attributes, categories and content.
3. Install a guarded legacy-query redirect layer before/with permalink activation.
4. Flush rewrite rules.
5. Verify representative products/categories and WooCommerce system pages.
6. Verify legacy query URLs return direct 301 to the pretty target.
7. Roll back permalink option, rewrite rules, redirect layer and `.htaccess` if pretty routes fail.
8. No Home/theme/UI mutation is allowed.
