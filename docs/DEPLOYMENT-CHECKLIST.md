# Deployment checklist

## GitHub

- Create a private repository named `gramiss-commerce`.
- Push this workspace to `main`.
- Protect `main` and require the CI workflow.
- Do not commit `.env` files.

## Backend

- Create Medusa Cloud project or a Node.js host.
- Add PostgreSQL and Redis if self-hosting.
- Configure production `DATABASE_URL`, CORS, JWT and cookie secrets.
- Create the first admin user.
- Create a region and sales channel.
- Create a publishable API key.
- Import only verified products and variants.

## Storefront

- Set `NEXT_PUBLIC_SITE_URL`.
- Set `NEXT_PUBLIC_MEDUSA_BACKEND_URL`.
- Set `NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY`.
- Keep `NEXT_PUBLIC_COMMERCE_MODE=demo` until integration tests pass.
- Keep `NEXT_PUBLIC_ROBOTS_INDEX=false` on staging.

## Payments

- Implement the selected Iranian payment provider.
- Verify request, redirect, callback and server-side payment verification.
- Test idempotency and duplicate callback handling.
- Never store card data.

## Launch

- Test stock, shipping, payment success/failure, account and order access.
- Back up the database.
- Point the domain only after staging passes.
- Set `NEXT_PUBLIC_ROBOTS_INDEX=true` only on the final domain.
