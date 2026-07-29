export const dynamic = "force-dynamic";

export function GET() {
  const commerceMode =
    process.env.NEXT_PUBLIC_COMMERCE_MODE === "medusa" ? "medusa" : "demo";

  return Response.json(
    {
      status: "ok",
      service: "gramiss-storefront",
      commerceMode,
      backendConfigured: Boolean(
        process.env.NEXT_PUBLIC_MEDUSA_BACKEND_URL?.trim(),
      ),
      publishableKeyConfigured: Boolean(
        process.env.NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY?.trim(),
      ),
      timestamp: new Date().toISOString(),
    },
    {
      status: 200,
      headers: {
        "Cache-Control": "no-store, max-age=0",
      },
    },
  );
}
