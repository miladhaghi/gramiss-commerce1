# Gramiss staging deployment

This is the deployment runbook for the current Gramiss commerce repository.

## Recommended staging architecture

Use Medusa Cloud for the backend and Admin. Deploy the Next.js storefront either in the same Medusa Cloud project or externally if storefront hosting is unavailable for the account.

Repository paths:

- Backend root: `apps/backend`
- Storefront root: `apps/storefront`
- Production branch: `main`

Suggested staging URLs:

- Storefront: `staging.gramiss.ir`
- Backend and Admin: `api-staging.gramiss.ir`
- Medusa Admin path: `/app`

## Backend environment

Set these values in the backend hosting dashboard. Never commit real values to GitHub.

```env
NODE_ENV=production
DATABASE_URL=<managed-by-host>
REDIS_URL=<managed-by-host-if-required>
MEDUSA_CLOUD=true
STORE_CORS=https://staging.gramiss.ir
ADMIN_CORS=https://api-staging.gramiss.ir
AUTH_CORS=https://staging.gramiss.ir,https://api-staging.gramiss.ir
JWT_SECRET=<at-least-32-random-characters>
COOKIE_SECRET=<at-least-32-random-characters>
```

When self-hosting instead of Medusa Cloud, set `MEDUSA_CLOUD=false` and provide `REDIS_URL`.

## Storefront environment

Start in demo mode until the backend is live and a publishable API key exists.

```env
NEXT_PUBLIC_SITE_URL=https://staging.gramiss.ir
NEXT_PUBLIC_COMMERCE_MODE=demo
NEXT_PUBLIC_MEDUSA_BACKEND_URL=https://api-staging.gramiss.ir
NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY=
NEXT_PUBLIC_ROBOTS_INDEX=false
NEXT_PUBLIC_SOCIAL_IMAGE=/assets/hero-stage.png
```

After the backend, region, sales channel, and publishable API key are ready:

```env
NEXT_PUBLIC_COMMERCE_MODE=medusa
NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY=<publishable-key>
```

Redeploy the storefront after changing public environment variables.

## Health checks

- Storefront: `GET /api/health`
- Backend: `GET /health`
- Admin: `/app`

Both health endpoints must return HTTP 200 before product migration begins.

## Deployment order

1. Deploy `apps/backend`.
2. Open the backend health endpoint.
3. Create the first Admin user.
4. Create the Iran region and sales channel.
5. Create a publishable API key.
6. Deploy `apps/storefront` in demo mode.
7. Add the backend URL and publishable key to the storefront.
8. Switch the storefront to `NEXT_PUBLIC_COMMERCE_MODE=medusa`.
9. Import only verified products, prices, variants, and stock.
10. Keep robots indexing disabled until the final domain passes QA.

## Required staging verification

- Backend and storefront health checks return 200.
- Admin login works.
- Storefront loads without JavaScript errors.
- CORS allows the staging storefront and Admin only.
- No secrets exist in the repository or browser storage.
- No real payment provider is enabled before its callback and verification flow is tested.
- Cart, stock, order creation, payment callback, and duplicate callback handling pass QA before launch.
