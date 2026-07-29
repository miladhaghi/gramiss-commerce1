# Gramiss Storefront

Independent Next.js storefront extracted from the approved Gramiss ChatGPT
Sites source export.

## Requirements

- Node.js 22 LTS
- npm 10+

## Start locally

```bash
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Production build

```bash
npm run lint
npm run typecheck
npm run build
npm start
```

## Commerce modes

- `demo`: current local demo data and browser storage.
- `medusa`: real Medusa Store API. Do not enable until the backend,
  publishable API key, CORS, region, shipping and payment are configured.

See `docs/COMMERCE-MIGRATION.md`.
