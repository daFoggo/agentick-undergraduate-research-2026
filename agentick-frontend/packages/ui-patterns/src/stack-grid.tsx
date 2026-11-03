import type { ComponentType, SVGProps } from "react"
import {
  IconBetterAuth,
  IconClaude,
  IconDocker,
  IconFastapi,
  IconKeycloak,
  IconNextjs,
  IconPnpm,
  IconPostgresql,
  IconRedis,
  IconSupabase,
  IconTailwind,
  IconTanstack,
  IconTurborepo,
  IconVercel,
  IconZod,
  IconZustand,
} from "./stack-icons"

export interface StackItem {
  name: string
  category: "foundation" | "frontend" | "auth" | "backend" | "platform"
  Icon: ComponentType<SVGProps<SVGSVGElement>>
  href?: string
}

/**
 * 16 primary technologies comprising the next-mono-base stack,
 * ordered logically across 5 cohesive architectural tiers:
 * 1. Monorepo & browser runtime: Next.js, TanStack, Turborepo, pnpm
 * 2. Frontend & state: Tailwind CSS, Zustand, Zod
 * 3. Tri-stack auth seam: Keycloak, Better Auth, Supabase
 * 4. Backend & database: PostgreSQL, FastAPI, Docker
 * 5. Platform, cache & AI: Vercel, Redis, Claude AI
 */
export const STACK_ITEMS: readonly StackItem[] = [
  // Tier 1: Foundation, Monorepo & Browser Runtime
  { name: "Next.js", category: "foundation", Icon: IconNextjs },
  { name: "TanStack", category: "frontend", Icon: IconTanstack },
  { name: "Turborepo", category: "foundation", Icon: IconTurborepo },
  { name: "pnpm", category: "foundation", Icon: IconPnpm },

  // Tier 2: Frontend, State & Contracts
  { name: "Tailwind CSS", category: "frontend", Icon: IconTailwind },
  { name: "Zustand", category: "frontend", Icon: IconZustand },
  { name: "Zod", category: "frontend", Icon: IconZod },

  // Tier 3: Tri-Stack Auth Seam
  { name: "Keycloak", category: "auth", Icon: IconKeycloak },
  { name: "Better Auth", category: "auth", Icon: IconBetterAuth },
  { name: "Supabase", category: "auth", Icon: IconSupabase },

  // Tier 4: Backend & Database
  { name: "PostgreSQL", category: "backend", Icon: IconPostgresql },
  { name: "FastAPI", category: "backend", Icon: IconFastapi },
  { name: "Docker", category: "backend", Icon: IconDocker },

  // Tier 5: Platform, Cache & AI Workflow
  { name: "Vercel", category: "platform", Icon: IconVercel },
  { name: "Redis", category: "platform", Icon: IconRedis },
  { name: "Claude AI", category: "platform", Icon: IconClaude },
] as const

export interface StackGridProps {
  /** "default" for landing pages / full sections; "compact" for sidebars / auth rails */
  variant?: "default" | "compact"
  className?: string
}

/**
 * Clean hairline-bordered tech stack grid matching the reference bento design:
 * - 4 columns of 4 rows on sm+ viewports (16 items total; 2x8 on mobile)
 * - Centered icons + brand names
 * - Subtle hover highlighting
 * - Full light/dark mode support
 */
export function StackGrid({
  variant = "default",
  className = "",
}: StackGridProps) {
  const isCompact = variant === "compact"

  return (
    <div
      className={`grid border-t border-l border-border/40 ${
        isCompact
          ? "grid-cols-2 sm:grid-cols-4"
          : "grid-cols-2 sm:grid-cols-4"
      } ${className}`}
    >
      {STACK_ITEMS.map((item) => (
        <div
          key={item.name}
          className={`group flex items-center justify-center border-r border-b border-border/40 transition-colors duration-150 hover:bg-muted/30 ${
            isCompact
              ? "gap-2 px-3 py-3 text-xs"
              : "gap-3 px-4 py-6 sm:px-6 sm:py-8"
          }`}
        >
          <item.Icon
            aria-hidden="true"
            className={`shrink-0 transition-transform duration-150 group-hover:scale-105 ${
              isCompact ? "size-4 sm:size-5" : "size-5 sm:size-6"
            }`}
          />
          <span
            className={`font-medium tracking-tight text-foreground/80 transition-colors duration-150 group-hover:text-foreground ${
              isCompact ? "text-xs" : "text-sm"
            }`}
          >
            {item.name}
          </span>
        </div>
      ))}
    </div>
  )
}
