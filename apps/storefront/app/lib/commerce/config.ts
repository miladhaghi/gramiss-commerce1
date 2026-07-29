import type { CommerceMode } from "./types";

function normalizeMode(value: string | undefined): CommerceMode {
  return value === "medusa" ? "medusa" : "demo";
}

export const commerceConfig = {
  mode: normalizeMode(process.env.NEXT_PUBLIC_COMMERCE_MODE),
  medusaBackendUrl:
    process.env.NEXT_PUBLIC_MEDUSA_BACKEND_URL?.replace(/\/$/, "") ||
    "http://localhost:9000",
  medusaPublishableKey:
    process.env.NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY?.trim() || "",
} as const;

export function assertMedusaConfigured(): void {
  if (!commerceConfig.medusaPublishableKey) {
    throw new Error(
      "NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY is required when NEXT_PUBLIC_COMMERCE_MODE=medusa.",
    );
  }
}
