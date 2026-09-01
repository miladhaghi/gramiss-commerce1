# GRAMISS PRODUCT INTAKE V1

Status: Active operating contract
Companion files:

- `docs/GRAMISS-PRODUCT-ENTRY-STANDARD-V1.md`
- `config/gramiss-product-entry-schema-v1.json`
- `.ops/validate-product-intake-v1.py`
- `.ops/product-prepublish-gate-v1.py`
- `.github/workflows/product-prepublish-gate-v1.yml`

## Purpose

The intake layer prevents incomplete or invented product data from reaching WooCommerce. It is deliberately separate from the live Product Gate:

1. **Intake validation** checks the proposed product payload before any WordPress/WooCommerce write.
2. **Pre-publish Gate** checks the actual WooCommerce product record after it has been created/configured but before it is considered ready.
3. **Post-publish Gate** checks the public result: HTTP, metadata, robots, canonical, Product schema and Product Sitemap membership.

## Required operating sequence

### A. Build the intake payload

The payload must contain only merchant/authoritative product facts.

Minimum fields:

- `name`
- `slug`
- `product_type`
- `primary_category_slug`
- `parent_sku`
- `full_description`
- `short_description`
- `index_intent`
- at least one image with alt text and exactly one featured designation

Variable products additionally require:

- reusable attributes
- at least one variation-defining attribute
- complete variations
- unique variation SKU for every variation
- authoritative price for every variation
- stock state for every variation
- exact attribute combination for every variation

Simple products additionally require:

- authoritative price
- stock state

If `index_intent` is `noindex`, `noindex_reason` is mandatory.

## Example structure

The example below shows structure only. Values are placeholders and must not be copied into a real product unless they are true for that product.

```json
{
  "name": "<verified product name>",
  "slug": "<stable-product-slug>",
  "product_type": "variable",
  "primary_category_slug": "<existing-category-slug>",
  "secondary_category_slugs": [],
  "parent_sku": "<authoritative parent SKU>",
  "full_description": "<verified product description>",
  "short_description": "<verified concise buying/search summary>",
  "index_intent": "index",
  "images": [
    {
      "source": "<local-or-authorized-image-source>",
      "alt": "<accurate visible product/view description>",
      "featured": true
    }
  ],
  "attributes": [
    {
      "taxonomy": "pa_color",
      "values": ["<verified color>"],
      "visible": true,
      "variation": true
    },
    {
      "taxonomy": "pa_size",
      "values": ["<verified size>"],
      "visible": true,
      "variation": true
    }
  ],
  "variations": [
    {
      "sku": "<authoritative variation SKU>",
      "price": "<authoritative price>",
      "stock_status": "instock",
      "manage_stock": false,
      "attributes": {
        "pa_color": "<verified color>",
        "pa_size": "<verified size>"
      }
    }
  ]
}
```

## Local/CI intake validation

```bash
python3 .ops/validate-product-intake-v1.py path/to/product.json
```

Exit behavior:

- exit `0`: structurally ready for the next stage;
- exit `2`: blocking intake defects exist.

The validator checks, among other things:

- required fields;
- slug stability basics;
- category presence;
- parent SKU presence;
- one featured image + non-empty alt text;
- simple/variable requirements;
- variation SKU uniqueness;
- variation price presence/validity;
- stock state;
- stock quantity when managed;
- variation attribute completeness and duplicate combinations;
- mandatory reason for `noindex`.

It **cannot** establish whether a commercial fact is true. Truthfulness still depends on the merchant/authoritative product source.

## Live Pre-Publish Gate

Dedicated workflow:

`Gramiss Product Pre-Publish Gate V1`

Inputs:

- `product_id`
- `mode`: `prepublish` or `postpublish`
- `index_intent`: `index` or `noindex`
- `report_only`: false for a real blocking gate; true only for diagnosis

### Pre-publish checks

The live WooCommerce record is checked for:

- identity and slug;
- product type;
- category;
- parent SKU;
- full + short descriptions;
- featured image and alt completeness;
- stock state;
- simple price or variable-product variation integrity;
- variation attributes;
- unique variation SKUs;
- variation prices;
- duplicate-title warning;
- intended indexation state supplied to the gate.

### Post-publish checks

For an indexable product:

- HTTP 200;
- public title present;
- public meta description present;
- `index` robots state;
- self-canonical;
- exactly one Product schema;
- canonical URL present in Product Sitemap.

For an intentional noindex product:

- HTTP 200;
- `noindex` rendered;
- excluded from Product Sitemap;
- exactly one Product schema;
- canonical behavior surfaced for explicit review.

Every live gate run also verifies protected Home/Looks file hashes before and after the check.

## Validation proof from legacy catalogue

The V1 implementation was tested in read-only/report mode against known live defects:

- Product `49`: correctly blocked on missing parent SKU and missing variation SKUs `50` and `52`.
- Product `210`: correctly blocked on missing parent SKU, missing short description and missing variation price `213`.
- Product `62`: correctly surfaced missing parent SKU, missing short description, empty variation set under its variable-product state, and warned that its intentional/legacy noindex page has no canonical.

These tests demonstrate that the gate detects existing catalogue defects without mutating product data.

## Important boundary

Passing this pipeline means the data structure and public SEO behavior meet the Gramiss contract. It does **not** authorize the system to invent:

- SKU values;
- price;
- stock;
- material composition;
- brand/authenticity;
- category intent;
- product naming facts.

Those values must come from an authoritative source before intake validation begins.
