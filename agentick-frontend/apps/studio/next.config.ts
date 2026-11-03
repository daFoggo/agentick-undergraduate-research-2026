import type { NextConfig } from "next"
import { withRedact } from "@tanstack/redact/next"

const isDev = process.env.NODE_ENV === "development"
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  ? new URL(process.env.NEXT_PUBLIC_SUPABASE_URL)
  : null

/**
 * Content-Security-Policy without nonces: nonces force dynamic rendering of every page
 * and are incompatible with Partial Prerendering (docs: guides/content-security-policy).
 */
function contentSecurityPolicy(): string {
  const formActions = ["'self'", "https://accounts.google.com"]
  // Supabase OAuth sends the browser to the project's auth server before Google.
  if (
    process.env.AUTH_PROVIDER === "supabase" &&
    process.env.NEXT_PUBLIC_SUPABASE_URL
  ) {
    formActions.push(new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).origin)
  }

  // Keycloak OIDC sends the browser to the Keycloak realm auth endpoint.
  const keycloakIssuer =
    process.env.KEYCLOAK_ISSUER || "http://localhost:8080/realms/studio"
  if (process.env.AUTH_PROVIDER === "keycloak") {
    formActions.push(new URL(keycloakIssuer).origin)
  }

  const supabaseOrigin = process.env.NEXT_PUBLIC_SUPABASE_URL
    ? new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).origin
    : null

  const directives = [
    "default-src 'self'",
    `script-src 'self' 'unsafe-inline'${isDev ? " 'unsafe-eval'" : ""}`,
    "style-src 'self' 'unsafe-inline'",
    `img-src 'self' blob: data:${supabaseOrigin ? ` ${supabaseOrigin}` : ""}`,
    "font-src 'self'",
    `connect-src 'self'${supabaseOrigin ? ` ${supabaseOrigin}` : ""}${isDev ? " ws: wss:" : ""}`,
    "object-src 'none'",
    "base-uri 'self'",
    `form-action ${formActions.join(" ")}`,
    "frame-ancestors 'none'",
  ]
  // Upgrading to https would break http://localhost during development.
  if (!isDev) directives.push("upgrade-insecure-requests")
  return directives.join("; ")
}

// Turbopack compiles workspace packages (e.g. @workspace/ui) automatically,
// so `transpilePackages` is not needed here.
const nextConfig: NextConfig = {
  // Recommended for all new apps from Next.js 16.4 (default in create-next-app).
  cacheComponents: true,
  partialPrefetching: true,
  // Enables forbidden() / forbidden.tsx, used by requirePermission() in lib/dal.ts.
  experimental: {
    authInterrupts: true,
    optimizePackageImports: ["@tabler/icons-react"],
    // Ships the instant() testing API only in a dedicated test build (EXPOSE_TESTING_API=1); never set in deploys.
    exposeTestingApiInProductionBuild: process.env.EXPOSE_TESTING_API === "1",
  },
  images: {
    // The protocol and port follow the Supabase URL (http for the local stack).
    remotePatterns: supabaseUrl
      ? [
          {
            protocol: supabaseUrl.protocol === "http:" ? "http" : "https",
            hostname: supabaseUrl.hostname,
            ...(supabaseUrl.port ? { port: supabaseUrl.port } : {}),
            pathname: "/storage/v1/object/public/media/**",
          },
        ]
      : [],
    // The local Supabase stack lives on 127.0.0.1, which the optimizer blocks by default.
    ...(isDev ? { dangerouslyAllowLocalIP: true } : {}),
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "Content-Security-Policy", value: contentSecurityPolicy() },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ]
  },
}

export default process.env.DISABLE_REDACT === "1"
  ? nextConfig
  : withRedact(nextConfig)
