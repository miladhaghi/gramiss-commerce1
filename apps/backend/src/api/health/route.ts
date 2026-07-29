import type {
  MedusaRequest,
  MedusaResponse,
} from "@medusajs/framework/http"

export const GET = (_req: MedusaRequest, res: MedusaResponse) => {
  res.setHeader("Cache-Control", "no-store, max-age=0")
  res.status(200).json({
    status: "ok",
    service: "gramiss-backend",
    environment: process.env.NODE_ENV || "development",
    version: process.env.npm_package_version || "unknown",
    timestamp: new Date().toISOString(),
  })
}
