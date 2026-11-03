export interface ArchitectureChapter {
  number: string
  badge: string
  title: string
  desc: string
  meta: string
}

export const ARCHITECTURE_CHAPTERS: readonly ArchitectureChapter[] = [
  {
    number: "01",
    badge: "Monorepo",
    title: "Next.js 16.4 App Router with PPR & Cache Components",
    desc: "Turborepo + pnpm workspaces keeping applications next to shared packages for UI, auth, db, and patterns with zero transpilation boilerplate.",
    meta: "Turbopack",
  },
  {
    number: "02",
    badge: "Auth Seam",
    title: "Multi-Stack Authentication Seam",
    desc: "Native support for Keycloak 26 OIDC, Better Auth, Supabase, or pure FastAPI OAuth2 behind one @workspace/auth seam. Switch via AUTH_PROVIDER without touching application code.",
    meta: "Zero lock-in",
  },
  {
    number: "03",
    badge: "Data Layer",
    title: "Decoupled Data Access Layer (DAL)",
    desc: "Strict server-only boundaries, per-user caching with 'use cache', connection pooling for PostgreSQL, and zero client token exposure.",
    meta: "Server-only",
  },
  {
    number: "04",
    badge: "Client State",
    title: "Zustand Client-Only State",
    desc: "Minimal, shared client state without React Context cascade re-renders, with optional persistent storage across navigation.",
    meta: "Zero bloat",
  },
  {
    number: "05",
    badge: "Validation",
    title: "TanStack Form & Zod Schema Contracts",
    desc: "Headless type-safe forms and runtime validation at every network boundary, form mutation, and server action. Strict TypeScript contracts from database to UI.",
    meta: "Type-safe",
  },
  {
    number: "06",
    badge: "Design",
    title: "Base-Nova Design System",
    desc: "zinc neutral palette, dark mode default, Animate UI v2 spring physics, and ready-made dashboard shells with collapsible rails and detail sheets.",
    meta: "Tailwind v4",
  },
  {
    number: "07",
    badge: "Security",
    title: "Continuous Security Audit & Invariant Ledgers",
    desc: "Built-in automated audit skill with 10-unit deterministic coverage ledgers, multi-hunter invariant verification, token-bound tenant isolation, and fail-fast production secret validation.",
    meta: "Audit-ready",
  },
] as const
