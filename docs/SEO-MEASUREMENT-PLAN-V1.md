# Gramiss SEO Measurement Plan V1

Date: 2026-09-02
Status: Active after completion of the initial SEO foundation

## 1. Starting point

The build/foundation phase is complete and should no longer be treated as an endless publishing project.

Verified foundation:

- 19 editorial articles pass the permanent Editorial Foundation V7 audit.
- 20/20 product-category money pages pass with `P0=0 / P1=0 / P2=0`.
- Product Intake + Pre/Post-Publish Gate self-tests pass.
- 41 legacy published/indexable products received safe short-description remediation.
- 6 legacy products remain explicitly blocked by missing authoritative data or indexability decisions.
- Product Sitemap and Product Category Sitemap retain their protected URL-set checksums.
- Home / Gramiss Looks protected implementation remains unchanged by SEO work.

Final foundation checkpoint:

`docs/SEO-FOUNDATION-FINAL-CHECKPOINT-2026-09-02.md`

## 2. Current measurement readiness

Read-only Measurement Readiness Audit V1 found:

- Rank Math SEO is active.
- Rank Math `analytics` module is enabled.
- no Rank Math Search Console/Google OAuth token state was detected;
- no Rank Math analytics/Search Console data tables with imported rows were detected;
- imported analytics row count: `0`;
- no `google-site-verification` meta tag was detected on the public Home page at audit time.

Therefore, Gramiss currently has **no usable first-party Search Console query/impression dataset available to this automation**.

The absence of imported Rank Math data is not an SEO failure. It is a measurement/integration gap.

## 3. Do not substitute weak proxies for Search Console

Until first-party Search Console data exists:

- do not invent search volume;
- do not infer rankings from article quality;
- do not publish more content just because the content calendar has room;
- do not treat a third-party `site:` search result as equivalent to Google Search Console indexing coverage;
- do not pay for Semrush/Ahrefs merely to unblock this phase.

Public search-engine checks can be used only as a weak supplementary signal.

## 4. Required first-party measurement connection

Preferred path:

1. Create/confirm the correct Google Search Console property for `gramiss.ir`.
2. Complete Google ownership verification using an authorized Google account.
3. Submit/confirm the canonical XML sitemap(s) in Search Console.
4. Allow Google time to crawl/index the newly established foundation.
5. Export Performance data or connect Rank Math Analytics after the Google authorization step.

Google sign-in / ownership approval is an account-level action and must not be fabricated or bypassed by automation.

If a Search Console HTML verification token is supplied by the authorized property owner, Gramiss can add it through a guarded implementation. Never invent a verification token.

## 5. Data handling / privacy rule

The GitHub repository `miladhaghi/gramiss-commerce1` is public.

**Never commit raw Search Console exports, OAuth tokens, Google credentials, verification tokens, customer/order data, or private analytics exports to this repository.**

Safe ways to analyze Search Console data:

- upload an export directly to the ChatGPT conversation/File Library;
- export to a private Google Sheet/Drive file and use an authorized private connector;
- run the repository analyzer locally against a private local export.

The repository may contain analyzer code and aggregate/non-sensitive conclusions, but not private raw exports.

## 6. Minimum data window

Do not overreact to the first few days after major SEO changes.

Initial review windows:

- quick indexing/coverage check: after Search Console verification and sitemap submission;
- first directional performance review: when there is enough real impression data to distinguish pages/queries;
- deeper content/CTR review: compare consistent windows rather than one-day noise.

The decision criterion is sufficient observations, not an arbitrary promise that ranking must happen by a fixed date.

## 7. Core measurements

For each query/page combination where available:

- clicks;
- impressions;
- CTR;
- average position;
- page URL;
- query;
- date range;
- device/country only when useful for a specific diagnosis.

For the site as a whole also track:

- indexed vs excluded canonical pages;
- sitemap discovery/errors;
- crawl/indexing issues;
- organic landing-page engagement/conversion when first-party analytics becomes available.

## 8. Prioritization framework

Use real Search Console data to identify:

### A. Striking-distance pages
Pages/queries already receiving meaningful impressions around positions where a targeted content/internal-link/title improvement could plausibly move them higher.

### B. CTR opportunities
Pages with meaningful impressions whose CTR underperforms relative to their own rank/query context. Improve title/meta only after verifying intent alignment; never chase clickbait.

### C. Query expansion
Unexpected but relevant queries already showing impressions. Expand the existing owner page when the intent belongs there instead of creating a competing URL.

### D. Cannibalization signals
Multiple Gramiss URLs receiving impressions for the same narrow intent. Decide one primary owner before adding more content.

### E. True content gaps
Create a new article/landing page only when no existing Gramiss page can own the observed intent cleanly.

## 9. First measurement cycle after data exists

1. Export/query last available reliable Search Console window.
2. Map every meaningful query to its current Gramiss owner URL.
3. Flag striking-distance opportunities.
4. Flag high-impression CTR opportunities.
5. Check cannibalization.
6. Check whether category pages are earning commercial queries.
7. Check whether editorial pages are sending users toward relevant commerce archives.
8. Select a small batch of changes.
9. Apply guarded changes.
10. Re-measure in the next comparable window.

## 10. Content publishing policy after foundation

The 19-article foundation is complete.

New articles are now **data-triggered**, not cadence-triggered.

A new article requires at least one of:

- first-party query evidence;
- a clear SERP/content gap with commercial relevance and no cannibalization;
- a new product/category cluster entering the catalogue;
- a meaningful recurring customer question that deserves its own search owner.

Otherwise improve an existing page instead.

## 11. Product/category policy after foundation

New products follow Product Intake V1.

New product categories should not automatically become indexable money pages. They need:

- real inventory;
- distinct search/commerce intent;
- deliberate title/meta/canonical/indexation;
- useful bottom-of-grid category copy when the page is intentionally indexable;
- one H1;
- inclusion in category sitemap only when intended by the SEO architecture.

## 12. Current hard blockers requiring owner data/authorization

Measurement integration:

- authorized Google Search Console property/verification is not currently available to the automation.

Legacy catalogue:

- product 97 — missing variation SKU;
- product 141 — missing variation SKU;
- product 210 — missing variation price;
- product 344 — missing variation price;
- product 62 — business/indexation decision required;
- product 68 — business/indexation decision required.

These are explicit inputs, not reasons to guess.

## 13. Operating loop

From this checkpoint onward the SEO loop is:

`Measure -> diagnose -> prioritize -> small guarded change -> verify -> measure again`

The goal is qualified organic discovery and commerce outcomes, not maximum page count.
