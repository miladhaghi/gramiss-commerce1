# Gramiss Google Search Console Activation Pack V1

Status: PRE-VERIFICATION READY
Checkpoint date: 2026-09-02
Production: https://gramiss.ir
Authoritative branch: `ops/seo-content-architecture-v1`

## Purpose

This checkpoint records the exact production state immediately before Google Search Console ownership verification. It is intended to make the activation step deterministic and to prevent unrelated SEO changes while ownership is being established.

## Verified production readiness

Authoritative GSC activation preflight passed on commit:

`2c784b25f4faacb56066b916deeb85082e1a738e`

Workflow:

`SEO Content Architecture V1`

Run:

`33642447093`

Verified state:

- Home: HTTP 200
- Home X-Robots-Tag: no noindex header
- robots.txt: HTTP 200
- robots.txt does not block `/` for `User-agent: *`
- robots.txt declares `https://gramiss.ir/sitemap_index.xml`
- sitemap index: HTTP 200 and valid `<sitemapindex>`
- sitemap index members: 5
  - `category-sitemap.xml`
  - `page-sitemap.xml`
  - `post-sitemap.xml`
  - `product-sitemap.xml`
  - `product_cat-sitemap.xml`
- post sitemap: HTTP 200, valid `<urlset>`, 20 URLs
- product sitemap: HTTP 200, valid `<urlset>`, 47 URLs
- product category sitemap: HTTP 200, valid `<urlset>`, 20 URLs
- Category Money Page audit: 20 PASS / 0 P0 / 0 P1 / 0 P2
- Editorial Foundation audit: 19 published editorial articles verified
- Product and product-category sitemap protected baselines remain unchanged
- Home / Gramiss Looks protected hashes remain unchanged

## Activation tooling

Read-only readiness check:

`.ops/gsc-activation-preflight-v1.py`

Guarded verification-file publisher:

`.ops/gsc-verification-file-publisher-v1.py`

The verification-file publisher is intentionally not auto-run. It accepts only a Google verification filename matching `google*.html` and requires the file body to be exactly:

`google-site-verification: <same-google-filename>`

It refuses arbitrary root-file writes and refuses to overwrite an existing verification filename with different content. After deployment it verifies both cPanel-stored content and the public HTTP response. On a failed post-write verification it attempts a guarded rollback.

## Required external authorization

The only missing input is the Google ownership artifact from the Google account that will own the Search Console property.

Preferred property for the first activation:

`https://gramiss.ir/` as a URL-prefix property.

Preferred verification method:

HTML file.

The required artifact is the exact `google*.html` file supplied by Google Search Console. Do not rename or edit it.

## Activation sequence after the Google file is supplied

1. Validate the Google filename and file body with the guarded publisher.
2. Re-run production SEO and GSC preflight guards.
3. Publish only the exact verification file into `public_html`.
4. Verify the public URL returns HTTP 200 and the exact Google body.
5. User clicks Verify in Google Search Console.
6. Keep the verification file in place while the property remains in use.
7. Submit `https://gramiss.ir/sitemap_index.xml` in Search Console; the sitemap index is the primary submission target and exposes its child sitemaps.
8. Record the verification/submission timestamp as the measurement baseline.
9. Begin observation before making data-driven SEO changes.

## Measurement policy after activation

- Do not store raw Search Console exports containing account/private context in this public repository.
- Analyze private exports locally/off-repo with `.ops/search-console-export-analyzer-v1.py`.
- Prioritize decisions by query/page impressions, CTR, average position and commercial intent rather than vanity traffic.
- Avoid reacting to the first few days of sparse data.
- Preserve the current SEO foundation unless Search Console reveals a verified issue or a deliberate growth experiment is approved.

## Current blocker

`GOOGLE_OWNERSHIP_ARTIFACT_REQUIRED`

No further production SEO mutation is required before that artifact exists.
