import dynamic from "next/dynamic"

import { CountingNumber } from "@workspace/ui/components/animate-ui/numbers/counting-number"
import { StackGridSkeleton } from "@/components/skeletons/stack-grid-skeleton"

const StackGrid = dynamic(
  () => import("@workspace/ui-patterns/stack-grid").then((m) => m.StackGrid),
  {
    loading: () => <StackGridSkeleton />,
  }
)

export function EcosystemSection() {
  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col gap-2 border-t border-border/40 pt-8 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-1">
          <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            Supported Ecosystem
          </span>
          <h2 className="text-2xl font-normal tracking-tight text-foreground sm:text-3xl">
            Integrated technologies across 5 tiers
          </h2>
        </div>
        <div className="flex items-center gap-1.5 font-mono text-xs text-muted-foreground">
          <CountingNumber number={16} />
          <span>technologies ·</span>
          <CountingNumber number={4} />
          <span>auth providers · Zero lock-in</span>
        </div>
      </div>

      <div className="mx-auto w-full max-w-4xl">
        <StackGrid />
      </div>
    </section>
  )
}
