# GRAMISS HANDOFF — 2026-08-31

This file is the durable continuation point for a new ChatGPT conversation.

## User / project expectations

- Project: **Gramiss** — main business project, WordPress + WooCommerce Persian RTL fashion e-commerce platform.
- Assistant role expected by user: act as Chief Architect / implementation partner, inspect source, change code, deploy, verify production, then report.
- When user says `انجام بده`, they expect actual implementation, not snippets or generic instructions.
- Keep replies in Persian, compact, practical and action-oriented.
- Never claim visual perfection before screenshot verification.
- Protect already-finished Home/PDP/Cart/Checkout work from unrelated deployments.

---

# Repository / deployment

Repository:
- `miladhaghi/gramiss-commerce1`

Production theme:
- `public_html/wp-content/themes/gramiss-theme-next`

Main operational deployment branch / known good ref:
- `ops/home-looks-enable-final`
- known stable SHA: `9b1297c48d3782d9a6395d1c3b9b0af56aab1569`

Reusable workflow:
- `.github/workflows/cpanel-home-looks-enable-final.yml`

Known workflow run used for deployments:
- run id: `33021042610`

Important deployment pattern that already works:
1. Prepare candidate script/commit on a feature branch.
2. Temporarily force `ops/home-looks-enable-final` to candidate commit.
3. Rerun known workflow job.
4. Confirm checkout step actually checked out the candidate commit.
5. Restore `ops/home-looks-enable-final` back to stable SHA `9b1297c...` while deployment script continues.
6. Wait for job completion and inspect logs.
7. Restore/clean feature branch afterward if temporary deploy script was one-off.

cPanel access is performed from GitHub Actions with secrets. No direct cPanel browser control is assumed.

Protected Home SHA:
- `0e5b79e88279812dbb20a7728061cee3ec00c79b6ef1894c3049d42856b795a7`

Any deployment touching site files must verify this Home SHA remains unchanged unless the task explicitly targets Home.

---

# Finished / protected frontend areas

## Home / GRAMISS LOOKS
Live and polished.

Production files:
- `template-parts/home-looks.php`
- `assets/css/home-looks.css`
- `assets/js/home-looks.js`
- `assets/images/home/gramiss-look-01.webp`
- `assets/images/home/gramiss-look-02.webp`

Do not disturb Home Hero/front-page for SEO/product tasks.

## PDP mobile
Mobile PDP enhancements are live and accepted enough to move on.

## Cart desktop
Branch:
- `ops/cart-desktop-v1`

Latest summary/trust-rail polish live.

## Mobile Cart
Branch:
- `ops/cart-mobile-v2`

Must remain intact.

## Mobile Checkout
Branch:
- `ops/checkout-mobile-v1`

Important files:
- `deploy/checkout-mobile-v1/checkout-mobile-v1.css`
- `deploy/checkout-mobile-v1/checkout-mobile-v1.js`
- `deploy/checkout-mobile-v1/checkout-mobile-v1-bootstrap.js`
- `deploy/checkout-mobile-v1/checkout-mobile-v21.css`

Mobile checkout must remain untouched byte-for-byte by desktop/SEO work.

## Checkout Desktop V1
Branch:
- `ops/checkout-desktop-v1`

Base/source desktop deployment commit:
- `681201203ce308d37c8c3b3fe0dbdc6b51a96cac`

Production files:
- `deploy/checkout-desktop-v1/checkout-desktop-v1.css`
- `deploy/checkout-desktop-v1/checkout-desktop-v1.js`

Desktop checkout has branded Hero/progress/coupon accordion/two-column form/sticky summary/payment styling/CTA.

### Latest checkout microfix already deployed successfully
User screenshot showed:
1. Coupon `+` optically off-center.
2. Summary total price clipped at leading digit.

Microfix deployment commit used temporarily:
- `519249c255ed41fff9282e614c83cc055417ed2e`

Successful job:
- `98629560619`
- run id `33021042610`

Production CSS after microfix:
- public length: `17312`
- SHA256: `2b55435521cda3470df4c17d39115ed43aaaef3d288694d39a39569ca5303efd`

Log confirmed:
- LiteSpeed purge 200
- public CSS 200
- Home SHA preserved
- `LIVE CHECKOUT DESKTOP MICROFIX DEPLOYED`

Feature branch was restored to source commit `681201...` afterward.

If user later sends screenshot, inspect the two microfix areas; do not overclaim before screenshot confirmation.

---

# Card-to-card payment gateway

Branch:
- `ops/card-transfer-gateway-v1`

Plugin:
- `deploy/card-transfer-gateway-v1/gramiss-card-transfer.php`

Gateway ID:
- `gramiss_card_transfer`

Gateway is active/registered.

Bank/card destination details are intentionally NOT populated in code/chat. User should configure them in WooCommerce settings.

Checkout selector:
- `.payment_method_gramiss_card_transfer`
- input value: `gramiss_card_transfer`

---

# SEO work completed before current handoff

User said almost everything is ready and only articles/SEO remain, while products are being added gradually.

Strategy agreed:
1. Technical SEO foundation first.
2. Product SEO foundation and standardized future product behavior.
3. Product data QA.
4. Then category landing pages / article architecture / content clusters.

Important SEO caution:
- Inspect existing Rank Math behavior before adding duplicate schema/canonical/meta logic.
- Do not assume Yoast/RankMath behavior; verify live output.
- User is Persian-market oriented; natural Persian taxonomy/content, no keyword stuffing.

---

# Product SEO Foundation V1 — DEPLOYED + VERIFIED

Feature branch:
- `ops/seo-product-foundation-v1`

Initial write commit:
- `389a3e6839ce1b9ab93af0573bb8ca7de702507e`

Verify-only commit:
- `ddb2471ee2c36c02fc9f6c0b2efa05a28e1b4b8d`

Dedicated workflow:
- `.github/workflows/seo-product-foundation-v1.yml`

Successful verification run:
- run id `33381869965`
- job `99455838294`
- conclusion `success`

Key verified state:
- Published products: `48`
- Gallery images: `91`
- Missing Alt IDs after fix: `[]`
- All current parent product SKUs empty: `48` (intentionally NOT auto-generated)
- Products with empty price: IDs `[62, 68]`
- Product title template: `خرید %title% %sep% %sitename%`
- Rank Math knowledge graph type: `company`
- MU plugin exists and verified
- Product SEO foundation MU plugin SHA at that point:
  `a719f2d27d4d6632b520df9d056dd74458343d36dc333d1f0a9b582ad3a426f1`

### What Product SEO Foundation V1 changed

- Filled **139 product image Alts** (featured + gallery).
- Added automation so future product image Alts can be generated/synced safely.
- Changed global product title template to prepend `خرید`.
- Changed Rank Math knowledge graph setting to `company`.
- Product Schema already existed from Rank Math; it was not duplicated.
- WooCommerce display currency remains `IRT` (Toman).
- Product JSON-LD converts schema price only to standards-compatible `IRR` by multiplying Toman by 10.
- This does NOT change displayed/store prices.

Examples verified live:
- `1500000 IRT` store price => `15000000 IRR` JSON-LD
- `4800000 IRT` => `48000000 IRR` JSON-LD

Verified sample product pages all had:
- HTTP 200
- title `خرید ... - Gramiss`
- valid description
- canonical
- index/follow
- Product + Offer schema
- `priceCurrency: IRR`
- no extra Person node on product pages

Home was preserved.

Sitemap index remained:
- `page-sitemap.xml`
- `product-sitemap.xml`
- `product_cat-sitemap.xml`

---

# Product Data QA V1 — audits completed, final write RETRY pending

Current working feature branch:
- `ops/seo-product-data-qa-v1`

Created from SEO Product Foundation branch.

Dedicated workflow:
- `.github/workflows/seo-product-data-qa-v1.yml`

## Audit commit / run

Audit branch commit:
- `3d8d5876c418e54f3da107f6a33d63e6f9fabb1a`

Audit run:
- `33382202539`
- job `99456881749`
- success

Initial Product Data QA stats:
- products: `48`
- simple: `3`
- variable: `45`
- parent SKU empty: `48`
- parent price empty: `2`
- short description empty: `47`
- thin content under 60 chars: `2`
- SEO title over 60: `0`
- taxonomy flags: `7`
- slug flags: `0` in first automated heuristic (but later manual targeted inspection found typo slugs)
- variable products with zero variations: `2`
- variation price empty: `2`
- variation SKU empty: `10`

Duplicates found:
- exact title `پیراهن آستین بلند پارچه سیلک` IDs `[296, 307, 320]`
- exact title `شلوار پارچه ای بگ ریزشی` IDs `[359, 366]`
- same description IDs `[330, 344]`

Known data issues:
- Product `62`: no price, no variations, thin description, fitted-cap + snapback overlap.
- Product `68`: no price, no variations, thin description, fitted-cap + snapback overlap.
- Product `210`: one variation missing price.
- Product `344`: one variation missing price and title typo `پراهن`.
- Product `355`: title says long-sleeve but category was short-sleeve.
- Product `84`: slug typo starts with `ملاه` instead of `کلاه`.

## Targeted conflict audit

Targeted inspection commit:
- `781feca8fe7fa41823d026a3a57f5bd885a14fd3`

Run:
- `33382302733`
- job `99457187680`
- success

Important verified product evidence:

### Fitted caps
Product 49 is correctly only in `fitted-cap` and has size-based variations.

Products 62/68/80/84/87 had `fitted-cap + snapback-cap + hat` even though product data/title/size behavior indicates fitted cap. This justified removing erroneous `snapback-cap` relationship from these products.

62 / 68:
- type variable
- zero variations
- no price
- should not be indexed until completed

### Product 210
- `تیشرت باکس دو تکه سنگشور طرح We live in hell`
- size XL variation ID `213` has empty price
- size M variation ID `214` price `4800000`
- do NOT copy/guess price automatically without user/product data certainty.

### Duplicate silk shirts
ID 296:
- colors orange + sky-blue
- description explicitly says peach / blue-gray
- media filenames support Holo / AA
- price `3800000`

ID 307:
- colors brown + cream
- price `3800000`

ID 320:
- description says warmer fabric / single color
- media/SKU contains `Makhmali`
- price `3900000`

This supports unique names instead of three identical titles.

### Linen shirts
ID 330:
- media/SKU indicates navy (`Sormeii`)

ID 344:
- media/SKU indicates blue (`Abi`)
- title typo `پراهن`
- L variation ID `346` missing price

### Product 355
- `پیراهن آستین بلند ماچایی پارچه سیلک`
- description confirms long sleeve
- was wrongly assigned to `short-sleeve-shirt`
- should use `long-sleeve-shirt`

### Pants 359 / 366
ID 359:
- description: drapey bag fit
- title can be normalized `شلوار پارچه‌ای بگ ریزشی`

ID 366:
- description explicitly says `فول بگ`
- title can be `شلوار پارچه‌ای فول بگ ریزشی`

---

# Product Data QA guarded fix attempt — ROLLED BACK SAFELY

Fix commit:
- `5f8b6968232ee9f0a37ad30430bf4783ec5e3d6d`

Run:
- `33382775243`
- job `99458638001`
- conclusion `failure` ONLY because verifier logic had one incorrect assumption.

The write itself succeeded and live checks showed the intended changes were valid, then guardrail rolled them back because verifier required canonical on noindex pages 62/68.

## Intended/validated changes from that batch

### Titles
- 296 => `پیراهن آستین بلند پارچه سیلک هلویی و آبی‌طوسی`
- 307 => `پیراهن آستین بلند پارچه سیلک قهوه‌ای و کرم`
- 320 => `پیراهن آستین بلند پارچه سیلک گرم‌دار`
- 330 => `پیراهن لینن آستین کوتاه سرمه‌ای`
- 344 => `پیراهن لینن آستین کوتاه آبی`
- 359 => `شلوار پارچه‌ای بگ ریزشی`
- 366 => `شلوار پارچه‌ای فول بگ ریزشی`

### Slugs / redirects
- 84 typo slug corrected from `ملاه...` to `کلاه...`
- 296 slug normalized to silk/color-specific slug
- 320 `...-2` duplicate-ish slug replaced with warm-silk slug
- 344 typo slug replaced with blue linen shirt slug

All four old URLs were observed returning **301** to the new URLs before rollback.

### Taxonomy
- Remove `snapback-cap` from fitted-cap products 62/68/80/84/87.
- Keep generic `hat` where already present.
- Move product 355 from `short-sleeve-shirt` to `long-sleeve-shirt`.

Before rollback the DB verify showed:
- `snapback-cap` count became `0`
- `fitted-cap` count `6`
- `short-sleeve-shirt` count `5`
- `long-sleeve-shirt` count `4`

### Incomplete product indexability
Products 62 and 68 should automatically become:
- `noindex, follow`
while they are published but incomplete (no priced variations / no usable price).

Once completed later, automation should remove only the auto-generated noindex and allow indexing again.

Rank Math behavior observed:
- on these noindex pages it intentionally omitted canonical.
- That is why the first verifier falsely failed.

### Sitemap behavior observed before rollback
- product sitemap effectively had `46` indexable products
- product category sitemap `20`
- sitemap index healthy

### Important: rollback succeeded
Log explicitly showed:
- `ROLLBACK 200 b'ROLLED_BACK'`

Therefore current production after this failed run should be treated as reverted to the pre-Product-Data-QA-write state, while Product SEO Foundation V1 remains live.

No half-written product-data fix should be assumed active now.

---

# Exact current continuation point

The NEXT action is **NOT** another audit from scratch.

The next action is:

1. Fix the Product Data QA verifier so products 62/68 require:
   - HTTP 200
   - `noindex`
   - canonical is NOT required for those two
2. Re-run the exact same guarded Product Data QA batch from commit `5f8b696...` with corrected verifier.
3. Confirm:
   - redirects 84/296/320/344 are 301
   - updated URLs return 200
   - titles unique
   - category mappings correct
   - image Alts resynced to new titles only where they were auto-managed
   - 62/68 noindex
   - 62/68 omitted from product sitemap
   - product sitemap = 46 indexable products (assuming no product inventory changed meanwhile)
   - product category sitemap healthy
   - Home SHA still exact healthy SHA
   - Product SEO MU plugin remains valid
4. Only after successful green verification move to Content / Article SEO.

## Prepared but not committed retry assets

At the very end of the previous chat, corrected retry content was prepared as Git blobs but NOT attached to a commit/ref yet:
- blob SHA: `0a1ea218a53fd11f89972aa4d29264ade3c0d575`
- blob SHA: `d0fb6ad33e4a88715ff6e0cefd7eaa92c32d761c`

These blobs may expire/be garbage-collected if never referenced, so do not rely on them blindly. It is safer in the new chat to fetch the current branch script at commit `5f8b696...`, patch verifier logic explicitly, commit it, and run the dedicated Product Data QA workflow.

Current durable handoff branch:
- `ops/gramiss-handoff-2026-08-31`

Current working branch to continue Product QA:
- `ops/seo-product-data-qa-v1`
- known head at handoff: `5f8b6968232ee9f0a37ad30430bf4783ec5e3d6d`

---

# What NOT to auto-fix

Do NOT fabricate or infer these without reliable product data / user input:
- parent SKUs
- missing SKU values generally
- missing price on product 62/68
- missing variation price on product 210 XL
- missing variation price on product 344 L
- missing variations for products 62/68
- product copy/content claims not supported by existing data/assets

Do not automatically copy sibling variation prices merely because they look likely.

---

# After Product Data QA passes

Next project phase is Article / SEO architecture.

Recommended order already agreed:

1. Category landing page SEO architecture
   - T-shirt
   - Pants
   - Sneakers
   - Bag
   - Cap
   - Socks
   - Shirt, etc. based on actual live taxonomy
2. Build strong category intros/helpful buyer guidance rather than empty product grids.
3. Build 10–15 high-quality first-wave articles, interconnected.
4. Topic clusters around real commercial decisions, e.g.:
   - boxy vs oversize
   - how to choose fit
   - fabric durability
   - sizing
   - styling combinations
   - care/washing
   - occasion-based choices
5. Internal linking from articles -> category -> product and product/category -> relevant educational content.
6. Avoid thin SEO filler / keyword stuffing.

The user is adding products gradually, so article/category architecture should not depend on all inventory being completed first.

---

# New-chat quick command

If the user opens a new chat, they can simply say:

`ادامه پروژه Gramiss رو از فایل .ops/GRAMISS_HANDOFF_2026-08-31.md روی branch ops/gramiss-handoff-2026-08-31 ادامه بده. اول Product Data QA retry رو کامل کن.`

The assistant should then fetch this file, inspect the current working branch, and continue from the Product Data QA retry without making the user explain previous work again.
