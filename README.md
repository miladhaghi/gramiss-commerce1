# Gramiss Commerce

Production migration workspace for the approved Gramiss storefront.

## Structure

- `apps/storefront`: independent Next.js storefront.
- `apps/backend`: Medusa backend (generated in the next setup step).
- `docker-compose.yml`: local PostgreSQL and Redis services.

## Local infrastructure

```bash
docker compose up -d
```

## Storefront

```bash
npm install
cp apps/storefront/.env.example apps/storefront/.env.local
npm run dev:storefront
```

The storefront remains in demo commerce mode until the Medusa backend is ready.
