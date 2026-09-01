# Gramiss SEO Content Gap, Internal Links, and Article 10+ Roadmap

Date: 2026-09-01

Branch baseline: `ops/seo-content-architecture-v1`
Starting commit: `e3facfc775574f63cc87e731c3055e24bbc76a1f`

## Decision summary

The live editorial foundation passes. The strongest uncovered commercial-support
topic is sneakers: Gramiss has live `sneakers`, `casual-sneakers`, and
`walking-shoes` commerce archives and live products, but no editorial page owns
shoe sizing or sneaker buying-guide intent.

The selected first batch is:

1. Article 10 — shoe-size measurement for online sneaker buying.
2. Article 11 — a general men's everyday-sneaker buying guide.

These pages have separate intent boundaries. Article 10 owns measurement and
model-specific size-table comparison. Article 11 owns use case, product-page
evidence, construction details, colour, and comparison criteria. Neither page is
allowed to target the transactional category query `خرید کتانی مردانه` as its
primary intent; that query remains owned by the commerce archive.

Search-volume data: **UNKNOWN / NOT USED**. No volume estimate is inferred from
autocomplete, result counts, or competitor publication activity.

## Foundation evidence

The authoritative GitHub Actions run for Audit V2 passed on commit `e3facfc`.
A fresh public Audit V3 was also run on 2026-09-01 and returned `PASS`:

- all nine expected post IDs are published and return HTTP 200;
- live H1 and WordPress titles match;
- meaningful article body length is present (1,149–1,484 parsed words);
- each article has 12–16 H2 headings;
- Meta Title and Meta Description are present;
- canonical URLs are self-referencing;
- robots are `index, follow`;
- every article contains `BlogPosting` and no accidental `Product` schema;
- each article has one correct editorial category;
- no article is an editorial orphan;
- no contextual internal target returned an error;
- the blog root exposes all nine articles;
- the four populated editorial categories are HTTP 200, canonical, and
  index/follow with expected counts;
- Post Sitemap is HTTP 200 with 10 URLs;
- Category Sitemap is HTTP 200 with 4 URLs;
- Product Sitemap is HTTP 200 with 47 URLs and SHA-256
  `70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3`.

Audit V3 initially emitted a false Product Sitemap drift because it decoded URL
paths before hashing. Audit V2 hashes the sorted raw `<loc>` strings. V3 was
corrected to use the same byte-compatible method and then passed. Production was
not changed to satisfy the false assertion.

## Live commerce taxonomy used for decisions

The current `product_cat-sitemap.xml` exposes 20 indexable commerce archives.
The relevant supported paths are:

- T-shirts: `/product-category/tshirt/`, plus graphic, oversized, crew-neck,
  and polo children.
- Shirts: `/product-category/shirt/`, plus casual, short-sleeve, long-sleeve,
  linen, and a live Persian-slug fabric child.
- Pants: `/product-category/pants/`, plus jeans, fabric pants, and cargo pants.
- Sneakers: `/product-category/sneakers/`, plus casual sneakers and walking
  shoes.
- Hats: `/product-category/hat/` and `/product-category/hat/fitted-cap/`.

The public WooCommerce Store API confirms currently visible products in the
sneaker, T-shirt, shirt, pants, cargo, jeans, and hat families. Product facts not
present in that public data are not assumed. Bags and socks do not currently
appear in the indexable product-category sitemap, so their editorial expansion
is deferred until the commerce taxonomy is live and populated.

## Free SERP and query research

Sources were public search results, public competitor pages, Google Suggest, the
live Gramiss site, WordPress REST, WooCommerce Store API, and live sitemaps. No
paid API or keyword database was used. Search Console was not available in the
environment and was not treated as a blocker.

### Observed intent patterns

1. `راهنمای انتخاب سایز کفش مردانه` produces measurement-led editorial pages
   and store blogs. Results commonly cover measuring both feet, comparing the
   result with the model's own size table, and checking fit after delivery.
   Examples: [Saman Shoes](https://samanshoes.org/%D8%B1%D8%A7%D9%87%D9%86%D9%85%D8%A7%DB%8C-%D8%A7%D9%86%D8%AA%D8%AE%D8%A7%D8%A8-%D8%B3%D8%A7%DB%8C%D8%B2-%DA%A9%D9%81%D8%B4-%D8%AF%D8%B1-%D8%AE%D8%B1%DB%8C%D8%AF-%D8%A7%DB%8C%D9%86%D8%AA%D8%B1%D9%86/)
   and [Salimore](https://salimore.com/blog/men-shoe-size-guide).
2. `راهنمای خرید کتونی مردانه` is mixed informational/commercial. The results
   combine use case, size, upper/sole evidence, and product-category links. The
   opportunity is to avoid generic “best” claims and teach the reader how to
   evaluate only facts actually present on a product page. Examples:
   [Karkhaneh Mod](https://www.karkhanehmod.com/blog/guide-buy-walking-sneakers-daily-2025)
   and [Narka](https://narka.ir/guide/buying-snakrs/).
3. `تمیز کردن کتانی سفید` returns editorial and video results. Material-aware
   care and the manufacturer's label are the defensible angle; universal bleach,
   peroxide, machine-washing, temperature, or drying claims are unsafe. Example:
   [Salimore](https://salimore.com/blog/clean-white-sneakers-guide).
4. `انتخاب سایز پیراهن مردانه` has a clear measurement intent around a known
   good-fitting shirt, shoulder, chest, length, and sleeve. Example:
   [Salimore](https://salimore.com/blog/men-shirt-size-guide).
5. Cargo results are a mix of editorial explanations and ecommerce-category
   pages. Many pages combine definition, fit, purchase, and styling, leaving an
   opportunity to separate “cargo vs bag/straight” from “what to wear with
   cargo.” Examples: [Luxe Posh](https://www.luxeposh.ir/blog/mht52/men-cargo-pants)
   and [Cafe Style](https://cofestyle.com/what-to-wear-with-cargo-pants).
6. Hat-size results explain measuring head circumference and comparing it with
   the exact brand/model chart. The safer Gramiss angle must not publish a
   universal conversion table unless the live product data supplies it.
   Example: [Kolah Bazi](https://kolahbazi.com/mag/how-to-measure-head-for-hat-size).
7. Men's fabric-pants results are split between ecommerce archives, generic
   advertorials, and styling pages. Gramiss can offer a more evidence-led guide
   around fit, fall, rise, hem, and reference-garment comparison. Examples:
   [Suit Sepehri](https://suitsepehri.com/blog/mens-dress-pants-types/) and
   [Mozafaree](https://mozafaree.com/blog/how-to-measure-pants-size).

### Google Suggest observations

Google Suggest returned exact or close continuations for:

- `راهنمای انتخاب سایز کفش مردانه`;
- `راهنمای خرید کتونی مردانه`;
- `انتخاب سایز پیراهن مردانه`;
- `شلوار کارگو مردانه` with simple, black, cotton, cream, green, baggy, and
  military modifiers;
- `شلوار پارچه ای مردانه` with straight, sport, baggy, wide, classic, and
  semi-bag modifiers.

It returned no usable continuation for some longer care and fitted-cap seeds.
That absence is not interpreted as zero demand; those topics are ranked lower
because public evidence is weaker.

### SERP weaknesses Gramiss can exploit

- Many ranking pages mix several intents into one generic article.
- Some pages make unsupported health, durability, “best,” or fabric claims.
- Product/category links are often promotional rather than contextual.
- Several pages publish universal sizing rules without making the model-specific
  size table authoritative.
- Fresh competitor pages show active editorial competition, so a stale yearly
  buying-guide title is avoided and evergreen decision criteria are preferred.

## Current internal-link graph

Edges below include contextual article-to-article links only. Navigation, the
blog archive, category badges, Home, and Shop are excluded.

| Article | Outgoing editorial targets | Incoming sources | Topical commerce link |
|---|---|---|---|
| 01 / ID 453 | 02, 03 | 02, 03, 08 | Missing specific T-shirt category; Shop only |
| 02 / ID 459 | 03, 01, 08, 05, 04 | 01, 03, 08 | T-shirts |
| 03 / ID 460 | 02, 07, 01, 09 | 01, 02, 07, 09 | Pants |
| 04 / ID 463 | 06, 05 | 02, 05, 06 | Linen shirts |
| 05 / ID 464 | 04 | 02, 04, 06 | Linen shirts |
| 06 / ID 467 | 05, 04 | 04 | Linen shirts, sneakers, T-shirts |
| 07 / ID 468 | 03 | 03, 09 | Pants, sneakers, T-shirts |
| 08 / ID 471 | 02, 01 | 02 | T-shirts |
| 09 / ID 472 | 07, 03 | 03 | Pants, jeans |

### Link-audit findings

- No orphan exists. Every article has at least one incoming and one outgoing
  editorial link.
- Articles 06, 08, and 09 have only one incoming editorial source and are the
  weakest nodes. New pages should link to them where the context genuinely
  matches.
- Article 02 has five outgoing article links. It is the densest node but not yet
  excessive; future batches should not use it as the default bridge for every
  cluster.
- Article 01 lacks a topical `/product-category/tshirt/` link. The first guarded
  batch should add one short, marked, reversible commerce bridge without
  rewriting the article.
- The sneaker category is linked from style articles 06 and 07, but no editorial
  page currently explains sneaker sizing or purchase evaluation.
- Future Article 10 should receive a contextual link from Article 07. Future
  Article 11 should link to Articles 06 and 07, strengthening their incoming
  counts while preserving relevance.
- New cargo content should bridge from Articles 03, 07, and 09, not from every
  existing post.
- No large related-links block should be appended globally.

## Ranked Article 10+ roadmap

Scores are directional prioritisation scores out of 100. They combine business
relevance, intent fit, topical-authority contribution, internal-link potential,
money-page connection, SERP opportunity, cannibalisation safety, answer quality,
evergreen value, and uniqueness. They are not traffic forecasts.

### Article 10 — P0 — score 92

- Primary query: `انتخاب سایز کتانی مردانه`
- Secondary queries: `راهنمای انتخاب سایز کفش مردانه`, `اندازه گیری پا برای خرید اینترنتی کفش`, `سایز کتونی مردانه`
- Intent: informational with strong pre-purchase utility
- Cluster: `fit-size-guide`
- Title: `راهنمای انتخاب سایز کتانی مردانه؛ اندازه‌گیری پا برای خرید آنلاین`
- Slug: `انتخاب-سایز-کتانی-مردانه`
- Commerce target: sneakers, casual sneakers, walking shoes
- Link from: Article 07
- Link to: Articles 07 and 11; three sneaker commerce archives
- Cannibalisation: safe if it owns measurement only and defers model fit to the
  exact product size table
- SERP rationale: explicit sizing intent, mixed-quality store blogs, and a clear
  chance to be more conservative and actionable
- Why it should exist: size uncertainty is a direct obstacle between editorial
  discovery and the live sneaker catalogue

### Article 11 — P0 — score 89

- Primary query: `راهنمای خرید کتانی مردانه`
- Secondary queries: `راهنمای خرید کتونی روزمره مردانه`, `انتخاب کتانی برای استفاده روزمره`, `کفش روزمره یا پیاده روی`
- Intent: mixed informational/commercial
- Cluster: `buying-guide`
- Title: `راهنمای خرید کتانی مردانه برای استفاده روزمره؛ سایز، رویه و زیره`
- Slug: `راهنمای-خرید-کتانی-مردانه-روزمره`
- Commerce target: sneakers and casual sneakers; walking shoes only where the
  use case matches
- Link from: Article 07
- Link to: Articles 10, 06, and 07
- Cannibalisation: category owns transactional `خرید کتانی`; article owns the
  pre-purchase checklist
- SERP rationale: current results mix generic recommendations and sales copy;
  Gramiss can teach evidence-led comparison without “best” claims
- Why it should exist: it creates the missing supporting buying guide above the
  sneaker money pages

### Article 12 — P0 — score 87

- Primary query: `انتخاب سایز پیراهن مردانه`
- Secondary queries: `اندازه گیری پیراهن مردانه`, `سایز پیراهن برای خرید آنلاین`, `اندازه سرشانه و آستین پیراهن`
- Intent: informational/pre-purchase
- Cluster: `fit-size-guide`
- Title: `راهنمای انتخاب سایز پیراهن مردانه؛ سرشانه، سینه، قد و آستین`
- Slug: `انتخاب-سایز-پیراهن-مردانه`
- Commerce target: shirts, short-sleeve shirts, long-sleeve shirts
- Link from: Articles 04 and 06
- Link to: Articles 04, 05, and 06
- Cannibalisation: distinct from linen fabric/care/style pages
- SERP rationale: clear measurement intent and a live shirt catalogue with no
  general sizing owner
- Why it should exist: it expands beyond the already-covered linen subcluster

### Article 13 — P1 — score 84

- Primary query: `تمیز کردن کتانی سفید`
- Secondary queries: `شستن کتونی سفید`, `تمیز کردن کتانی سفید بدون آسیب`, `خشک کردن کتانی سفید`
- Intent: informational/care
- Cluster: `fabric-care`
- Title: `تمیز کردن کتانی سفید بدون آسیب؛ راهنمای رویه، بند و خشک‌کردن`
- Slug: `تمیز-کردن-کتانی-سفید`
- Commerce target: sneakers and casual sneakers
- Link from: Articles 10 and 11 after publication
- Link to: Article 11
- Cannibalisation: separate care intent; must not become another buying guide
- SERP rationale: visible Persian demand but many unsafe universal recipes
- Why it should exist: a label-first, material-aware answer can be safer and more
  useful than quick whitening hacks

### Article 14 — P1 — score 82

- Primary query: `شلوار کارگو مردانه چیست`
- Secondary queries: `تفاوت شلوار کارگو و بگ`, `شلوار شش جیب چیست`, `انواع شلوار کارگو مردانه`
- Intent: informational/mixed
- Cluster: `fit-size-guide`
- Title: `شلوار کارگو مردانه چیست و چه تفاوتی با شلوار بگ دارد؟`
- Slug: `شلوار-کارگو-مردانه-چیست`
- Commerce target: cargo pants and pants
- Link from: Articles 03 and 09
- Link to: Articles 03, 09, and 18
- Cannibalisation: Article 03 owns bag/semi-bag/full-bag; this page owns cargo
  construction and cargo-versus-bag distinctions
- SERP rationale: ranking pages often merge definition, buying, and styling;
  a focused comparison can answer the question faster
- Why it should exist: Gramiss has live cargo products but no supporting owner

### Article 15 — P1 — score 80

- Primary query: `انتخاب سایز کلاه فیت کپ`
- Secondary queries: `اندازه گیری سایز سر برای کلاه`, `سایز کلاه فیتد`, `تفاوت فیت کپ و اسنپ بک`
- Intent: informational/pre-purchase
- Cluster: `fit-size-guide`
- Title: `راهنمای انتخاب سایز کلاه فیت کپ؛ اندازه‌گیری دور سر بدون حدس`
- Slug: `انتخاب-سایز-کلاه-فیت-کپ`
- Commerce target: hats and fitted caps
- Link from: future cap-style content; no forced link from unrelated articles
- Link to: hat/fitted-cap commerce archives
- Cannibalisation: category remains transactional; article must not publish a
  universal conversion table without live model evidence
- SERP rationale: clear specialist intent with few broad menswear answers
- Why it should exist: Gramiss sells sized fitted caps and the decision needs
  more explanation than an adjustable cap

### Article 16 — P1 — score 79

- Primary query: `شستشوی تیشرت چاپی`
- Secondary queries: `شستن تیشرت چاپ دار`, `جلوگیری از خراب شدن چاپ تیشرت`, `اتو کردن تیشرت چاپی`
- Intent: informational/care
- Cluster: `fabric-care`
- Title: `شست‌وشوی تیشرت چاپی؛ محافظت از چاپ در شستن، خشک‌کردن و اتوکشی`
- Slug: `شستشوی-تیشرت-چاپی`
- Commerce target: graphic T-shirts and T-shirts
- Link from: Articles 01 and 08 where care context is present
- Link to: Article 08
- Cannibalisation: Article 08 owns purchase evaluation; this page owns care
- SERP rationale: Persian results are weaker than English care pages, but exact
  demand evidence is less strong than the P0 topics
- Why it should exist: the live catalogue is heavily connected to graphic tees

### Article 17 — P1 — score 77

- Primary query: `راهنمای خرید شلوار پارچه ای مردانه`
- Secondary queries: `شلوار پارچه ای مردانه بگ`, `افت پارچه شلوار`, `انتخاب قد شلوار پارچه ای`
- Intent: mixed informational/commercial
- Cluster: `buying-guide`
- Title: `راهنمای خرید شلوار پارچه‌ای مردانه؛ فیت، افت پارچه، فاق و قد`
- Slug: `راهنمای-خرید-شلوار-پارچه-ای-مردانه`
- Commerce target: fabric pants and pants
- Link from: Articles 03 and 07
- Link to: Articles 03, 07, and 09
- Cannibalisation: Article 09 owns jeans; Article 03 owns fit terminology; this
  page owns fabric-trouser purchase criteria
- SERP rationale: current results skew generic, formal, or advertorial
- Why it should exist: it supports Gramiss's live wide, drapey fabric trousers

### Article 18 — P2 — score 75

- Primary query: `با شلوار کارگو مردانه چی بپوشیم`
- Secondary queries: `استایل با شلوار کارگو مردانه`, `کفش مناسب شلوار کارگو`, `تیشرت با شلوار کارگو`
- Intent: informational/style
- Cluster: `style-guide`
- Title: `با شلوار کارگو مردانه چی بپوشیم؟ راهنمای تیشرت، کفش و حجم لباس`
- Slug: `با-شلوار-کارگو-مردانه-چی-بپوشیم`
- Commerce target: cargo pants, T-shirts, sneakers
- Link from: Articles 07 and 14
- Link to: Articles 03, 11, and 14
- Cannibalisation: keep it styling-only; Article 14 owns definition/comparison
- SERP rationale: results exist but many are gender-mixed or generic
- Why it should exist: it can connect three live commerce clusters contextually

### Article 19 — P2 — score 74

- Primary query: `پیراهن آستین کوتاه مردانه با چی بپوشیم`
- Secondary queries: `استایل پیراهن آستین کوتاه مردانه`, `پیراهن آستین کوتاه با شلوار جین`, `کفش مناسب پیراهن آستین کوتاه`
- Intent: informational/style
- Cluster: `style-guide`
- Title: `پیراهن آستین کوتاه مردانه را با چی بپوشیم؟ شلوار، کفش و لایه‌بندی`
- Slug: `استایل-پیراهن-آستین-کوتاه-مردانه`
- Commerce target: shirts, short-sleeve shirts, pants, sneakers
- Link from: Articles 06 and 12
- Link to: Articles 06, 09, 11, and 12
- Cannibalisation: broader than Article 06 but must avoid duplicating its
  linen-specific colour and care sections
- SERP rationale: strong generic and ecommerce pages, so priority is lower until
  the shirt-size owner exists
- Why it should exist: it expands the shirt cluster beyond linen while retaining
  a direct money-page connection

## Guarded publishing plan for Articles 10–11

Before mutation:

- confirm all existing IDs 453, 459, 460, 463, 464, 467, 468, 471, and 472 are
  published;
- confirm there are exactly nine published posts and category counts remain
  3/2/2/2;
- confirm both target slugs are absent;
- confirm sneaker commerce terms exist, are populated, HTTP 200, canonical, and
  index/follow;
- snapshot all four protected UI hashes;
- snapshot the exact sorted Product Sitemap URL list;
- confirm the Article 07 and Article 01 reversible markers are absent.

Mutation scope:

- create Articles 10 and 11;
- set only Rank Math title, description, and focus keyword;
- explicitly remove legacy per-post schema and robot overrides so global Article
  schema remains authoritative;
- add one marked contextual Article 07 → Articles 10/11 bridge;
- add one marked Article 01 → T-shirt commerce bridge;
- invalidate Rank Math sitemap storage and purge the relevant cache.

Post-mutation verification:

- verify both new live pages, metadata, canonical, robots, BlogPosting, absence
  of Product schema, categories, and links;
- verify the modified Article 01 and 07 markers and targets;
- verify all 11 article pages remain healthy;
- verify blog and category counts;
- verify Post Sitemap now has 12 URLs and Category Sitemap remains four URLs;
- require byte-identical Product Sitemap URL lists before/after;
- require byte-identical protected UI hashes before/after.

If any post-mutation assertion fails, delete only Articles 10 and 11, remove only
the two explicit marked blocks, invalidate sitemap/cache state, and re-check the
nine-article baseline.

## Wave 10-11 execution checkpoint

The guarded batch completed on 2026-09-01 through the dedicated SEO workflow.
The first attempt correctly rolled back because the verifier assumed all 11
cards would remain on Blog page 1; the public archive paginates after nine
cards. A separate public Audit V3 then proved the original nine-article state
was fully restored. The verifier was corrected to require both new cards on
page 1 and aggregate page 2 for the complete editorial set.

- Article 10: post 482, `انتخاب-سایز-کتانی-مردانه`
- Article 11: post 483, `راهنمای-خرید-کتانی-مردانه-روزمره`
- Published posts: 11
- Category counts: fit/size 4, fabric/care 2, style 2, buying 3
- Post Sitemap: 12 URLs
- Category Sitemap: 4 URLs
- Product Sitemap: 47 URLs; SHA-256 remained
  `70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3`
- Protected Home Looks and front-page file hashes remained byte-identical
- Both articles returned HTTP 200, canonical self-reference, index/follow,
  BlogPosting, and no Product schema
- Article 07 now links contextually to Articles 10 and 11
- Article 01 now has the missing contextual bridge to the live T-shirt archive
- Articles 12-19 remain planned only; no later roadmap item was published

The branch is returned to audit-only mode after this batch. The persistent
checkpoint validates the full 11-article set, paginated Blog archive, four
editorial archives, internal-link graph, Product Sitemap baseline, and protected
UI hashes on every later push to this branch.

## Wave 12-13 execution checkpoint

The guarded batch completed on 2026-09-01 through SEO Content Architecture V1
run `33506278268`. Both authenticated and public foundation audits passed before
the publisher step, and the publisher's complete Production verifier also
passed. The targeted freshness check confirmed the live shirt, short-sleeve
shirt, long-sleeve shirt, sneakers, and casual-sneakers archives; no conflicting
Gramiss owner was found. Current Persian results continue to emphasize garment
measurement for shirt sizing and a mix of useful and unsafe universal cleaning
recipes for white sneakers. Search volume remained `UNKNOWN / NOT USED`, and no
paid SEO data was used.

- Article 12: post 487, `انتخاب-سایز-پیراهن-مردانه`
- Article 13: post 488, `تمیز-کردن-کتانی-سفید`
- Published posts: 13
- Category counts: fit/size 5, fabric/care 3, style 2, buying 3
- Post Sitemap: 14 URLs
- Category Sitemap: 4 URLs
- Product Sitemap: the exact 47-URL set was preserved; SHA-256 remained
  `70c4ea579eda29df345086d38a50ad0e681532dd0138f7e7d4d46d541e4526b3`
- Product Category Sitemap: the exact 20-URL set was preserved; SHA-256 remained
  `75711e43ad0c892716fa2f7615fc9594d2165d71b150a0eab0722f7335f881c4`
- All four protected front-page/Home Looks hashes remained byte-identical
- Both new articles returned HTTP 200, canonical self-reference, index/follow,
  BlogPosting, and no Product schema
- Article 04 (post 463) and Article 06 (post 467) now link contextually to
  Article 12 through explicit Wave 12-13 markers
- Article 11 (post 483) now links contextually to Article 13 through an explicit
  Wave 12-13 marker; no forced link was added from Article 10
- The complete 13-article set is visible across the Blog root and page 2
- Contextual broken links: zero
- Rollback was not activated

The branch is returned to audit-only mode after this batch. The persistent
authenticated and public audits now validate the 13-article set, the three new
contextual bridges, paginated Blog coverage, editorial counts and sitemaps,
Product Sitemap integrity, and protected UI hashes on every later push.
