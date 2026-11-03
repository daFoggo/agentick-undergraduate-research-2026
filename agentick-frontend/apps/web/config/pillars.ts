import type { ComponentType } from "react"
import {
  IconCpu,
  IconDatabase,
  IconLayersLinked,
  IconLock,
  IconPalette,
  IconShieldCheck,
  type TablerIcon,
} from "@tabler/icons-react"

export interface ArchitecturalPillar {
  icon: TablerIcon | ComponentType<{ className?: string }>
  title: string
  badge: string
  description: string
}

export const PILLARS: readonly ArchitecturalPillar[] = [
  {
    icon: IconLock,
    title: "Multi-Stack Auth Seam",
    badge: "Pluggable",
    description:
      "Enterprise Keycloak 26 with PKCE S256 & RS256 JWKS verification, Better Auth with direct DB pooling, Supabase Auth, or pure FastAPI OAuth2 JWTs. Switch providers via an environment variable with zero application code changes.",
  },
  {
    icon: IconDatabase,
    title: "Server-Only Data Access",
    badge: "Strict DAL",
    description:
      "Server actions, queries, and auth secrets reside in strict server-only boundaries. Per-user caching uses 'use cache' and cacheLife directives without ever leaking credentials to client bundles.",
  },
  {
    icon: IconPalette,
    title: "Zinc Base-Nova UI Kit",
    badge: "Design System",
    description:
      "Engineered on shadcn base-nova with Animate UI v2 spring physics, zero arbitrary Tailwind values, dark mode default, and a full dashboard shell with collapsible navigation and detail sheets.",
  },
  {
    icon: IconCpu,
    title: "TanStack, Zustand & Zod",
    badge: "Client & Forms",
    description:
      "TanStack headless primitives, Zustand client-only stores without React context re-render waterfalls, and Zod validation across all API parameters, form mutations, and server actions.",
  },
  {
    icon: IconShieldCheck,
    title: "Audited & Hardened Core",
    badge: "Hardened",
    description:
      "Formally audited with 10-unit coverage ledgers. Features token-bound multi-tenant isolation, fail-fast production secret guards, Keycloak azp/typ claims binding, and live DB role verification in PostgreSQL.",
  },
  {
    icon: IconLayersLinked,
    title: "AI-Native Coding Rules",
    badge: "Deterministic",
    description:
      "Strict AGENTS.md conventions, comprehensive docs/ architecture guides, and Antigravity/Claude AI skills ensure autonomous agents generate clean, compliant code without hallucinating patterns.",
  },
] as const
