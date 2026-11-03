import { StackGrid } from "@workspace/ui-patterns/stack-grid"

/** Decorative stack overview for the auth rail: clean bento grid of supported technologies. */
export function StackShowcase() {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-1">
        <span className="font-mono text-xs tracking-wider text-muted-foreground uppercase">
          Supported stack &amp; integrations
        </span>
        <p className="text-xs text-muted-foreground">
          Next.js 16 + TanStack Redact base with pluggable auth providers and modular services.
        </p>
      </div>
      <StackGrid variant="compact" />
    </div>
  )
}
