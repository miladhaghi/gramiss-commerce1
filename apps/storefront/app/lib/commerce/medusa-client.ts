import { assertMedusaConfigured, commerceConfig } from "./config";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

export class MedusaRequestError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly details?: unknown,
  ) {
    super(message);
    this.name = "MedusaRequestError";
  }
}

export async function medusaRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  assertMedusaConfigured();

  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  headers.set("x-publishable-api-key", commerceConfig.medusaPublishableKey);

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(
    `${commerceConfig.medusaBackendUrl}${path.startsWith("/") ? path : `/${path}`}`,
    {
      ...options,
      headers,
      credentials: "include",
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
    },
  );

  const text = await response.text();
  const payload = text ? safeJsonParse(text) : null;

  if (!response.ok) {
    throw new MedusaRequestError(
      extractMessage(payload) || `Medusa request failed with ${response.status}.`,
      response.status,
      payload,
    );
  }

  return payload as T;
}

function safeJsonParse(value: string): unknown {
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function extractMessage(payload: unknown): string | null {
  if (
    payload &&
    typeof payload === "object" &&
    "message" in payload &&
    typeof payload.message === "string"
  ) {
    return payload.message;
  }

  return null;
}
