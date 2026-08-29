# Codex Execution Plan — Gramiss SEO Foundation

Read `docs/GRAMISS-SEO-BIBLE.md` first. Treat it as mandatory policy.

## Rule 0
Do not mutate production product data during discovery or dry-run tasks. Never invent price, stock, material, size, color, brand, SKU, GTIN/MPN or product identity.

## Phase A — Catalog integrity dry-run
Generate a report for PUBLISHED products only containing:
- product ID / name / type
- duplicate or near-duplicate titles
- missing parent SKU
- missing variation SKU
- missing variation price
- variation stock anomalies
- category assignments and obvious title/category contradictions
- missing short descriptions
- image alt gaps
- Rank Math title/description/canonical explicit-meta gaps

Known baseline: 48 published products, 159 variations across all product posts.

Do not fix prices automatically. Flag variation IDs 213 and 346 prominently because the 2026-08-29 audit found missing prices on published products.

## Phase B — Metadata proposal dry-run
For each published product, produce proposals only (no writes):
- SEO title
- Meta description derived only from verified existing product fields/attributes
- Image alt proposal list
- Short-description proposal derived only from existing product facts

Avoid keyword stuffing. Do not claim materials/brands/features that are not already stored as verified product data.

## Phase C — Taxonomy review
Produce a separate review list rather than auto-changing ambiguous taxonomy.
Known candidates from baseline:
- product 355: title says long-sleeve while assigned to short-sleeve category
- products 296/307/320: duplicate/near-duplicate names, likely need verified color/material differentiation
- products 359/366: duplicate name, likely need verified differentiation
- fitted-cap/snapback overlaps must be reviewed, not blindly normalized

## Phase D — URL migration planning
Current WordPress `permalink_structure` is empty. Published products therefore use `?product=...` URLs.
Before any mutation:
1. enumerate every published product/category current URL
2. define final URL structure
3. generate old->new mapping
4. identify redirect mechanism
5. verify no redirect chains
6. verify canonical targets
7. verify sitemap targets
8. verify internal links
9. prepare rollback

Do not change slugs or permalink settings until the migration plan is approved.

## Phase E — Safe write batches
After dry-run approval, split writes into small reversible batches:
1. catalog integrity fields with authoritative values
2. image alt metadata
3. Rank Math metadata / templates
4. short descriptions
5. taxonomy corrections
6. URL migration as its own isolated deployment

Each batch must include:
- backup or reversible mapping
- pre/post counts
- IDs changed
- exact fields changed
- validation checks
- no unrelated theme/UI changes

## Phase F — Technical SEO foundation
After URL migration:
- robots.txt
- sitemap
- canonical verification
- noindex utility pages
- OG/social previews
- Organization/WebSite/Breadcrumb schema where appropriate
- Product schema validation without duplicate competing Product markup
- Shop/category H1 cleanup
- category indexation decisions

## Output style
Return machine-readable CSV/JSON where useful plus a concise human summary. Never hide skipped/ambiguous records; flag them for review.
