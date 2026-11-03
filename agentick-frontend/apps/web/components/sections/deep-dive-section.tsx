import { ARCHITECTURE_CHAPTERS } from "@/config/chapters"

export function DeepDiveSection() {
  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col gap-1 border-t border-border/40 pt-10">
        <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          Deep Dive
        </span>
        <h2 className="text-2xl font-normal tracking-tight text-foreground sm:text-3xl">
          Architecture at a glance
        </h2>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Every decision is intentional: modular seams, strict typing, and zero unnecessary runtime dependencies.
        </p>
      </div>

      <div className="flex flex-col divide-y divide-border/40 border-y border-border/40">
        {ARCHITECTURE_CHAPTERS.map((item) => (
          <div
            key={item.number}
            className="group flex flex-col sm:flex-row sm:items-start gap-3 sm:gap-6 py-5 transition-colors hover:bg-muted/15 px-3 -mx-3 rounded-sm"
          >
            <div className="flex items-center gap-2.5 shrink-0 sm:min-w-44">
              <span className="font-mono text-xs text-muted-foreground tabular-nums">
                {item.number}
              </span>
              <span className="inline-flex rounded-full border border-border/60 bg-muted/40 px-2.5 py-0.5 font-mono text-xs text-foreground/80">
                {item.badge}
              </span>
            </div>
            <div className="flex flex-1 flex-col gap-1.5 min-w-0">
              <h4 className="text-sm font-medium text-foreground">
                {item.title}
              </h4>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {item.desc}
              </p>
            </div>
            <span className="font-mono text-xs text-muted-foreground shrink-0 hidden md:block pt-0.5">
              {item.meta}
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}
