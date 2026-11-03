import dynamic from "next/dynamic"

import { ProviderTabsSkeleton } from "@/components/skeletons/provider-tabs-skeleton"
import { MonorepoMapSkeleton } from "@/components/skeletons/monorepo-map-skeleton"

const ProviderTabs = dynamic(
  () => import("@/components/provider-tabs").then((m) => m.ProviderTabs),
  {
    loading: () => <ProviderTabsSkeleton />,
  }
)

const MonorepoMap = dynamic(
  () => import("@/components/monorepo-map").then((m) => m.MonorepoMap),
  {
    loading: () => <MonorepoMapSkeleton />,
  }
)

export function SeamsTopologySection() {
  return (
    <section className="flex flex-col gap-8">
      <div className="flex flex-col gap-2 border-t border-border/40 pt-10 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-1">
          <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            Architecture in Action
          </span>
          <h2 className="text-2xl font-normal tracking-tight text-foreground sm:text-3xl">
            Pluggable seams &amp; workspace topology
          </h2>
        </div>
        <p className="max-w-md text-xs sm:text-sm text-muted-foreground leading-relaxed">
          Decoupled modules guarantee you can swap authentication or database engines without rewriting application components.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Bento Card 1: Interactive Auth Switcher with Animate UI */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-medium text-foreground">
              Pluggable Authentication Seam
            </span>
            <span className="font-mono text-xs text-muted-foreground">
              packages/auth
            </span>
          </div>
          <ProviderTabs />
        </div>

        {/* Bento Card 2: Turborepo Workspace Topology */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-medium text-foreground">
              Turborepo Package Graph
            </span>
            <span className="font-mono text-xs text-muted-foreground">
              pnpm workspaces
            </span>
          </div>
          <MonorepoMap />
        </div>
      </div>
    </section>
  )
}
