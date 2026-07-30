# Gramiss Railway staging

This is the no-card staging path for the Gramiss monorepo.

## Services

Create one Railway project with four services:

1. `Postgres` database
2. `Redis` database
3. `gramiss-backend` from GitHub repository `miladhaghi/gramiss-commerce1`
4. `gramiss-storefront` from the same repository

## Backend service

Source repository: `miladhaghi/gramiss-commerce1`

Config file path:

```text
/deploy/railway-backend.json
```

Variables:

```dotenv
NODE_ENV=production
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
STORE_CORS=https://${{gramiss-storefront.RAILWAY_PUBLIC_DOMAIN}}
ADMIN_CORS=https://${{gramiss-backend.RAILWAY_PUBLIC_DOMAIN}}
AUTH_CORS=https://${{gramiss-storefront.RAILWAY_PUBLIC_DOMAIN}},https://${{gramiss-backend.RAILWAY_PUBLIC_DOMAIN}}
MEDUSA_BACKEND_URL=https://${{gramiss-backend.RAILWAY_PUBLIC_DOMAIN}}
JWT_SECRET=<generate-a-random-64-character-value>
COOKIE_SECRET=<generate-a-different-random-64-character-value>
```

Generate a public domain for the backend service. Health endpoint:

```text
/health
```

Admin will be available at:

```text
https://<backend-domain>/app
```

## Storefront service

Source repository: `miladhaghi/gramiss-commerce1`

Config file path:

```text
/deploy/railway-storefront.json
```

First deploy in demo mode:

```dotenv
NEXT_PUBLIC_SITE_URL=https://${{gramiss-storefront.RAILWAY_PUBLIC_DOMAIN}}
NEXT_PUBLIC_COMMERCE_MODE=demo
NEXT_PUBLIC_MEDUSA_BACKEND_URL=https://${{gramiss-backend.RAILWAY_PUBLIC_DOMAIN}}
NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY=
NEXT_PUBLIC_ROBOTS_INDEX=false
NEXT_PUBLIC_SOCIAL_IMAGE=/assets/hero-stage.png
```

Generate a public domain for the storefront service. Health endpoint:

```text
/api/health
```

## Activate real commerce mode

After the backend is live:

1. Open the Medusa Admin at `/app`.
2. Create the first admin user.
3. Create a Publishable API Key.
4. Add the key to the storefront variable `NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY`.
5. Change `NEXT_PUBLIC_COMMERCE_MODE` from `demo` to `medusa`.
6. Redeploy the storefront.

## Staging rules

- Keep `NEXT_PUBLIC_ROBOTS_INDEX=false`.
- Do not add real payment keys.
- Do not connect the main domain yet.
- Do not use staging for real customer orders.
- Before production, move to a paid plan with adequate memory, backups, and uptime.
