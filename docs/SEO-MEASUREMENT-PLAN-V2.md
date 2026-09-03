# Gramiss SEO Measurement Plan V2

Date: 2026-09-03
Status: ACTIVE — POST-FOUNDATION MEASUREMENT MODE

## 1. Starting point

The initial SEO foundation is complete and the known legacy remediation queue is closed.

Current verified baseline:
- 19 editorial articles.
- 21/21 product-category money pages pass the production read-only audit.
- 49 URLs in Product Sitemap.
- 21 URLs in Product Category Sitemap.
- 0 known legacy product blockers.
- Product Intake / Pre-Publish Gate remains the contract for new catalogue entries.
- Home / Gramiss Looks protected implementation remains unchanged by SEO work.

Current checkpoint:
`docs/SEO-FOUNDATION-CHECKPOINT-2026-09-03.md`

## 2. Search Console state

The owner-authorized Google Search Console property is active and the Performance report is available.

At activation time, query/impression/click observations are not yet sufficient for optimization decisions. This is a measurement waiting state, not an SEO failure.

Do not infer demand, rankings, CTR problems, or content gaps from a zero/near-zero early dataset.

## 3. What to do while data accumulates

Allowed work:
- keep permanent read-only SEO audits green;
- investigate real Search Console indexing/crawl errors if they appear;
- protect sitemap/canonical/robots invariants;
- run the Product Intake gate for new products;
- fix only concrete catalogue or technical defects supported by authoritative data.

Do not:
- publish articles just to increase page count;
- rewrite working titles/meta without query/impression evidence;
- create competing category/article URLs for guessed keywords;
- invent search volume or rank estimates;
- change indexability merely to make a sitemap count match an assumption.

## 4. First useful measurement cycle

Once Search Console contains meaningful observations:

1. Export or inspect a consistent reliable window.
2. Map meaningful queries to their current Gramiss owner URLs.
3. Separate commercial category/product queries from informational editorial queries.
4. Flag striking-distance pages with impressions and plausible ranking upside.
5. Flag CTR opportunities only where impressions are meaningful for the current position/query context.
6. Check cannibalization: multiple Gramiss URLs competing for the same narrow intent.
7. Identify relevant unexpected queries that belong on an existing owner page.
8. Create a new URL only for a true uncovered intent.
9. Apply a small guarded batch of changes.
10. Re-measure against a comparable later window.

## 5. Priority model

Prioritize in this order when real data exists:

### P0 — Crawl/index integrity
Broken indexability, canonical, sitemap, robots, schema, HTTP, or serious coverage issues.

### P1 — Existing demand close to value
Queries/pages already earning meaningful impressions where a focused change may improve qualified discovery.

### P2 — CTR and intent alignment
High-enough impression pages where title/meta can better represent the actual page and query intent.

### P3 — Internal authority and query expansion
Improve internal linking or page coverage for relevant queries already associated with an existing owner URL.

### P4 — New content
Only after evidence shows a commercially useful intent no existing Gramiss page can own cleanly.

## 6. Category strategy

The 21 current indexable category pages are deliberate money pages and must remain useful commerce destinations.

When Search Console data arrives, specifically check:
- whether parent categories earn broad commercial queries;
- whether subcategories earn distinct narrow commercial queries;
- whether editorial pages support category discovery through internal links;
- whether two categories are competing for the same query intent.

New WooCommerce terms are not automatically SEO landing pages. Before allowing a new category baseline, verify real inventory, distinct intent, one H1, useful copy, title/meta, self canonical, indexability, and sitemap inclusion.

## 7. Product strategy

New products follow Product Intake V1. Never invent SKU, price, material, authenticity, stock or other commercial facts.

For existing products, search-performance edits should be evidence-driven. Product titles and descriptions should not be churned only for keyword variation.

## 8. Editorial strategy

The 19-article initial foundation is complete.

New editorial URLs are data-triggered. Prefer improving an existing owner article when new queries belong to its current intent. Avoid creating near-duplicate posts that split impressions and authority.

## 9. Data privacy

The GitHub repository is public.

Never commit:
- raw Search Console exports;
- OAuth tokens or Google credentials;
- verification tokens;
- private analytics exports;
- customer/order data.

Safe analysis paths include direct conversation upload, private Drive/Sheet access, or local/private analysis. The public repo may contain analyzer code and non-sensitive aggregate conclusions only.

## 10. Baseline drift policy

Current verified URL-set baselines:
- Product Sitemap: 49 URLs, SHA256 `05e81da96bcc57927bf8d2b467866a1236e9ea0307e1c3902519136294e805bf`.
- Product Category Sitemap: 21 URLs, SHA256 `e56e71dfe5a97014bb645c3726b916c1883c87eb2e21b5eab8cc4598942c13bf`.

A future mismatch means **investigate**, not automatically revert. Legitimate owner catalogue edits can change counts. Accept a new invariant only after the new/removed URLs are identified and their SEO intent is verified.

## 11. Operating loop

`Measure -> diagnose -> prioritize -> small guarded change -> verify -> measure again`

The target is qualified organic discovery and commerce outcomes, not page count, content volume, or a cosmetic SEO score.
