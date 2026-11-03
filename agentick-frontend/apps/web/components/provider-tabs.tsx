"use client"

import { useState } from "react"
import { IconTerminal2 } from "@tabler/icons-react"
import { motion } from "motion/react"
import { CopyButton } from "@workspace/ui/components/animate-ui/buttons/copy"

type ProviderKey = "keycloak" | "better-auth" | "supabase"

interface ProviderInfo {
  name: string
  badge: string
  envSnippet: string
  features: string[]
}

const PROVIDERS: Record<ProviderKey, ProviderInfo> = {
  keycloak: {
    name: "Keycloak 26",
    badge: "Enterprise OIDC",
    envSnippet: `AUTH_PROVIDER="keycloak"
KEYCLOAK_ISSUER="http://localhost:8080/realms/studio"
KEYCLOAK_CLIENT_ID="studio-app"
KEYCLOAK_CLIENT_SECRET="studio-dev-client-secret"`,
    features: [
      "PKCE S256 with split cookies under 4KB",
      "Offline RS256 JWT verification via public JWKS",
      "Single sign-on & standalone Docker stack",
    ],
  },
  "better-auth": {
    name: "Better Auth",
    badge: "TypeScript Native",
    envSnippet: `AUTH_PROVIDER="better-auth"
BETTER_AUTH_SECRET="your-32-character-random-secret"
BETTER_AUTH_URL="http://localhost:3001"`,
    features: [
      "Lightweight TypeScript authentication framework",
      "Direct PostgreSQL connection via @workspace/db",
      "Session management with cookie fallback",
    ],
  },
  supabase: {
    name: "Supabase",
    badge: "Postgres BaaS",
    envSnippet: `AUTH_PROVIDER="supabase"
NEXT_PUBLIC_SUPABASE_URL="https://your-ref.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"`,
    features: [
      "Supabase Auth & GoTrue SSR cookies integration",
      "Row Level Security (RLS) policies enforcement",
      "PostgreSQL, Storage, and Realtime channels",
    ],
  },
}

export function ProviderTabs() {
  const [active, setActive] = useState<ProviderKey>("keycloak")
  const current = PROVIDERS[active]

  return (
    <div className="flex flex-col overflow-hidden rounded-lg border border-border/50 bg-muted/10">
      {/* Header with animated spring tab switcher */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/40 bg-muted/20 px-4 py-3">
        <div className="flex items-center gap-2">
          <IconTerminal2 className="size-4 text-muted-foreground" />
          <span className="font-mono text-xs text-muted-foreground">
            .env.local switch
          </span>
        </div>

        <div className="flex items-center gap-1 rounded-md border border-border/40 bg-background/80 p-1">
          {(Object.keys(PROVIDERS) as ProviderKey[]).map((key) => {
            const isSelected = active === key
            return (
              <button
                key={key}
                type="button"
                onClick={() => setActive(key)}
                className={`relative rounded px-3 py-1 font-mono text-xs transition-colors duration-150 outline-none ${
                  isSelected
                    ? "text-background font-medium"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {isSelected && (
                  <motion.div
                    layoutId="active-provider-pill"
                    className="absolute inset-0 rounded bg-foreground"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
                <span className="relative z-10">{PROVIDERS[key].name}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Code snippet display with Animate UI spring CopyButton */}
      <div className="relative p-5 font-mono text-xs">
        <div className="absolute top-4 right-4">
          <CopyButton
            content={current.envSnippet}
            variant="ghost"
            size="icon"
            className="size-7 rounded border border-border/40 bg-background/70 text-muted-foreground hover:bg-background hover:text-foreground"
          />
        </div>

        <pre className="overflow-x-auto text-foreground/90 leading-relaxed font-mono pr-12">
          <code>{current.envSnippet}</code>
        </pre>
      </div>

      {/* Unified DAL Query callout */}
      <div className="border-t border-border/40 bg-muted/25 px-5 py-3.5">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center rounded-full border border-border/60 bg-background px-2.5 py-0.5 font-mono text-xs text-foreground/80">
              Unified DAL
            </span>
            <span className="font-mono text-xs text-muted-foreground">
              Application code stays identical:
            </span>
          </div>
          <code className="font-mono text-xs text-foreground bg-background px-2.5 py-1 rounded border border-border/40 self-start sm:self-auto">
            const session = await getSession()
          </code>
        </div>
      </div>
    </div>
  )
}
