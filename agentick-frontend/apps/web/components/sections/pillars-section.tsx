import { PILLARS } from "@/config/pillars"

export function PillarsSection() {
  return (
    <section className="flex flex-col gap-8">
      <div className="flex flex-col gap-1 border-t border-border/40 pt-10">
        <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          Core Principles
        </span>
        <h2 className="text-2xl font-normal tracking-tight text-foreground sm:text-3xl">
          Engineered for production reliability
        </h2>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {PILLARS.map((pillar) => (
          <div
            key={pillar.title}
            className="group flex flex-col gap-3.5 rounded-lg border border-border/50 bg-muted/10 p-6 transition-all duration-150 hover:border-border hover:bg-muted/25"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <pillar.icon className="size-5 text-muted-foreground transition-colors group-hover:text-foreground shrink-0" />
                <h3 className="font-medium text-base text-foreground">
                  {pillar.title}
                </h3>
              </div>
              <span className="inline-flex rounded-full border border-border/60 bg-muted/40 px-2.5 py-0.5 font-mono text-xs text-foreground/80">
                {pillar.badge}
              </span>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {pillar.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
