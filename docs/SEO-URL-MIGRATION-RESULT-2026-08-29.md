# Gramiss SEO URL Migration — Production Result

Date: 2026-08-29
Status: SUCCESS

## Production changes
- WordPress permalink structure changed from empty/query mode to `/%postname%/`.
- WooCommerce product base remains `product`.
- WooCommerce product-category base remains `product-category`.
- Native hierarchical product-category paths are preserved.
- Standard WordPress front-controller rewrite block installed inside the existing `# BEGIN WordPress` / `# END WordPress` marker only.
- Existing LiteSpeed blocks outside the WordPress marker were preserved.
- A guarded MU-plugin map was installed for exact legacy query redirects:
  - `?product={legacy-slug}` -> 301 -> current pretty product permalink
  - `?product_cat={legacy-slug}` -> 301 -> current hierarchical category permalink

## Validation
- Published products: 48
- Active non-empty product categories: 21
- Generated WordPress rewrite rules: 203
- Representative product pretty URLs: HTTP 200
- Representative top-level category URLs: HTTP 200
- Representative child category hierarchical URLs: HTTP 200
- Legacy product query URLs: direct HTTP 301 to pretty product targets
- Legacy category query URLs: direct HTTP 301 to pretty category targets
- Shop: HTTP 200
- Cart: HTTP 200
- Checkout: resolves safely (empty-cart request redirects to Cart, HTTP 200 final)
- Account: HTTP 200
- Home `front-page.php` SHA preserved exactly

## SEO endpoint state immediately after migration
- `/robots.txt`: HTTP 200
- `/wp-sitemap.xml`: HTTP 200
- `/sitemap_index.xml`: HTTP 404 (Rank Math sitemap layer still needs configuration/review)

## Safety / rollback
The first migration attempt correctly auto-rolled back when the WordPress rewrite marker remained empty. A read-only diagnostic confirmed LiteSpeed/mod_rewrite were available and `.htaccess` was writable. The successful migration then used a two-phase WordPress bootstrap plus an exact marker-only rewrite patch.

A pre-change `.htaccess` backup and a migration manifest were created on production. No product names, product slugs, prices, stock, attributes, variations, categories or product content were changed by this migration.

## Deferred URL cleanup
Do not combine these with the permalink migration. Handle later as isolated redirect-backed edits:
- product 84 apparent slug typo
- product 296 title/slug mismatch review
- product 320 `-2` suffix and duplicate visible titles 296/307/320
- duplicate visible titles 359/366
- category 217 language/slug consistency review
- product 355 taxonomy contradiction review
