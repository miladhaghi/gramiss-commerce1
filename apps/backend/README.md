# Gramiss Backend

Medusa v2 backend scaffold for Gramiss.

## Local prerequisites

- Node.js 22 LTS
- PostgreSQL 16
- Redis 7

From the repository root:

```bash
docker compose up -d
cp apps/backend/.env.example apps/backend/.env
npm install
npm --workspace @gramiss/backend run db:migrate
npm --workspace @gramiss/backend run dev
```

Backend and Admin run at `http://localhost:9000`.

## First admin user

```bash
npm --workspace @gramiss/backend run user -- -e you@example.com -p "strong-password"
```

## Health check

```bash
curl http://localhost:9000/health
```

## Catalog migration

`data/gramiss-catalog.json` contains the current demo catalog extracted from the
approved storefront. It is migration input, not yet a production seed. Prices,
stock, SKU, images, variation inventory and legal product information must be
confirmed before import.
