import dynamic from "next/dynamic"

import { FaqSkeleton } from "@/components/skeletons/faq-skeleton"

const ArchitectureFaq = dynamic(
  () =>
    import("@/components/architecture-faq").then((m) => m.ArchitectureFaq),
  {
    loading: () => <FaqSkeleton />,
  }
)

export function FaqSection() {
  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col gap-2 border-t border-border/40 pt-10">
        <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          Frequently Asked Questions
        </span>
        <h2 className="text-2xl font-normal tracking-tight text-foreground sm:text-3xl">
          Architectural decisions &amp; FAQ
        </h2>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Common questions about provider seams, caching strategies, and monorepo workflows.
        </p>
      </div>

      <ArchitectureFaq />
    </section>
  )
}
