import "server-only"

import { authConfig } from "./config"
import type { AuthOptions, AuthProvider } from "./types"

/** The active provider for one app, chosen once per deployment via `AUTH_PROVIDER` (docs/providers.md). */
export async function getAuthProvider(
  options: AuthOptions
): Promise<AuthProvider> {
  if (authConfig.AUTH_PROVIDER === "supabase") {
    return (await import("./supabase/server")).createSupabaseProvider(options)
  }
  if (authConfig.AUTH_PROVIDER === "keycloak") {
    return (await import("./keycloak/server")).createKeycloakProvider(options)
  }
  if (authConfig.AUTH_PROVIDER === "fastapi-oauth") {
    return (await import("./fastapi-oauth/server")).createFastApiOAuthProvider(
      options
    )
  }
  return (await import("./better-auth/server")).createBetterAuthProvider(
    options
  )
}
