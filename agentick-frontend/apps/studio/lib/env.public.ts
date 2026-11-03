import { z } from "zod"

/**
 * Browser-safe environment. Each `NEXT_PUBLIC_*` variable must be referenced
 * literally (`process.env.NEXT_PUBLIC_X`) so Next.js can inline it at build time.
 */
const publicSchema = z.object({
  NEXT_PUBLIC_APP_URL: z.url().default("http://localhost:3001"),
  /** The public landing page (apps/web); the auth pages link back to it. */
  NEXT_PUBLIC_LANDING_URL: z.url().default("http://localhost:3000"),
})

export const publicEnv = publicSchema.parse({
  NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  NEXT_PUBLIC_LANDING_URL: process.env.NEXT_PUBLIC_LANDING_URL,
})
