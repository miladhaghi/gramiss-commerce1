# Gramiss Commerce Migration

## Current mode

The storefront defaults to `NEXT_PUBLIC_COMMERCE_MODE=demo`. This preserves the
approved UI and current local browser state while the real commerce backend is
being configured.

## Target mode

Set `NEXT_PUBLIC_COMMERCE_MODE=medusa` only after all of these exist:

1. A deployed Medusa backend.
2. A publishable API key assigned to the intended sales channel.
3. Store CORS configured for the storefront URL.
4. A region, currency, shipping options, and product variants.
5. Working payment and fulfillment providers.

## Replacement map

| Current source | Production source |
|---|---|
| `app/shop/shop-data.ts` | Medusa `/store/products` |
| `app/lib/catalog.ts` | Medusa products, categories, collections |
| `app/hooks/use-gramiss-store.ts` cart | Medusa cart API |
| demo auth | Medusa customer auth |
| `app/lib/demo-orders.ts` | Medusa customer order API |
| checkout draft | Medusa cart + payment collection |
| local inventory | Medusa inventory module |

## Safety

Do not switch production to Medusa mode until the checkout callback, order
creation, inventory update, retry behavior, and idempotency have been tested.
