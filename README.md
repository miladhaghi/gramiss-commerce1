# Gramiss Commerce

Production migration workspace for the approved Gramiss storefront.

## Current status

- Next.js storefront builds successfully in GitHub Actions.
- Medusa backend builds successfully in GitHub Actions.
- Storefront is still in demo commerce mode by default.
- Real products, carts, customers, orders, payments, and inventory are not connected yet.

## Structure

- `apps/storefront`: independent Next.js storefront.
- `apps/backend`: Medusa backend and Admin.
- `docker-compose.yml`: local PostgreSQL and Redis services.
- `docs/STAGING-DEPLOYMENT.md`: staging deployment runbook.
- `docs/DEPLOYMENT-CHECKLIST.md`: release checklist.

## Local infrastructure

```bash
docker compose up -d
```

## Storefront

Install and run the storefront independently to avoid dependency conflicts with the backend Admin packages:

```bash
npm install --prefix apps/storefront
cp apps/storefront/.env.example apps/storefront/.env.local
npm run --prefix apps/storefront dev
```

Storefront health check:

```text
http://localhost:3000/api/health
```

## Backend

```bash
npm install --prefix apps/backend
cp apps/backend/.env.example apps/backend/.env
npm run --prefix apps/backend db:migrate
npm run --prefix apps/backend dev
```

Backend health check:

```text
http://localhost:9000/health
```

Medusa Admin:

```text
http://localhost:9000/app
```

## Verification

```bash
npm run --prefix apps/storefront lint
npm run --prefix apps/storefront typecheck
npm run --prefix apps/storefront build
npm run --prefix apps/backend build
```

The storefront remains in demo mode until a deployed Medusa backend, region, sales channel, and publishable API key are available.
