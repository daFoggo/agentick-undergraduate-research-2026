import {
  IconCpu,
  IconLayersLinked,
  IconLock,
  IconShieldCheck,
  IconSparkles,
} from "@tabler/icons-react"

export function AiWorkflowSection() {
  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col gap-2 border-t border-border/40 pt-10">
        <div className="flex items-center gap-2">
          <IconSparkles className="size-4 text-foreground/80" />
          <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            AI Pair Programming
          </span>
        </div>
        <h2 className="text-2xl font-normal tracking-tight text-foreground sm:text-3xl">
          Built for developers and AI agents
        </h2>
        <p className="max-w-2xl text-sm text-muted-foreground leading-relaxed">
          In the age of Claude, Antigravity, and autonomous coding assistants, clean conventions and deterministic boundaries matter more than ever.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="flex flex-col gap-2.5 rounded-lg border border-border/50 bg-muted/10 p-6 transition-colors hover:bg-muted/20">
          <div className="flex items-center gap-2">
            <IconShieldCheck className="size-4 text-muted-foreground shrink-0" />
            <span className="font-mono text-xs font-medium text-foreground">
              Deterministic AGENTS.md Rules
            </span>
          </div>
          <p className="text-xs sm:text-sm leading-relaxed text-muted-foreground">
            Context-aware rules in AGENTS.md instruct AI assistants on Next.js 16 breaking changes, Turbopack compiling, and monorepo guidelines before writing code.
          </p>
        </div>

        <div className="flex flex-col gap-2.5 rounded-lg border border-border/50 bg-muted/10 p-6 transition-colors hover:bg-muted/20">
          <div className="flex items-center gap-2">
            <IconLayersLinked className="size-4 text-muted-foreground shrink-0" />
            <span className="font-mono text-xs font-medium text-foreground">
              Single Source of Truth in docs/
            </span>
          </div>
          <p className="text-xs sm:text-sm leading-relaxed text-muted-foreground">
            Exhaustive architectural docs cover data fetching, authentication seams, Zustand client state, and design-system tokens so agents never hallucinate patterns.
          </p>
        </div>

        <div className="flex flex-col gap-2.5 rounded-lg border border-border/50 bg-muted/10 p-6 transition-colors hover:bg-muted/20">
          <div className="flex items-center gap-2">
            <IconLock className="size-4 text-muted-foreground shrink-0" />
            <span className="font-mono text-xs font-medium text-foreground">
              Strict ESLint Monorepo Boundaries
            </span>
          </div>
          <p className="text-xs sm:text-sm leading-relaxed text-muted-foreground">
            Custom ESLint rules enforce strict architectural boundaries: client components cannot import server-only modules, and workspace packages maintain clean dependency graphs.
          </p>
        </div>

        <div className="flex flex-col gap-2.5 rounded-lg border border-border/50 bg-muted/10 p-6 transition-colors hover:bg-muted/20">
          <div className="flex items-center gap-2">
            <IconCpu className="size-4 text-muted-foreground shrink-0" />
            <span className="font-mono text-xs font-medium text-foreground">
              One-Command Full Monorepo Check
            </span>
          </div>
          <p className="text-xs sm:text-sm leading-relaxed text-muted-foreground">
            Running pnpm check executes lint, typecheck, and Vitest across all 8 packages in parallel via Turborepo, providing instant verification for generated code.
          </p>
        </div>
      </div>
    </section>
  )
}
