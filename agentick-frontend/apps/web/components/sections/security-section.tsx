import { IconShieldCheck } from "@tabler/icons-react"

export function SecuritySection() {
  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col gap-2 border-t border-border/40 pt-10 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <IconShieldCheck className="size-4 text-foreground/80" />
            <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
              Security &amp; Invariants
            </span>
          </div>
          <h2 className="text-2xl font-normal tracking-tight text-foreground sm:text-3xl">
            Continuous security audit &amp; verified defenses
          </h2>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-border/60 bg-muted/40 px-3 py-1 text-foreground/85">
            <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
            10/10 Coverage Units Verified
          </span>
        </div>
      </div>

      <p className="max-w-2xl text-sm text-muted-foreground leading-relaxed">
        Every boundary is continuously inspected using dedicated security audit skills. Deterministic coverage ledgers verify least-privilege DAL permissions, token-bound tenant isolation, and zero credential leakage.
      </p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="flex flex-col gap-2 rounded-lg border border-border/50 bg-muted/10 p-5 transition-colors hover:bg-muted/20">
          <span className="font-mono text-2xl font-normal text-foreground">0</span>
          <span className="font-medium text-sm text-foreground">Live High / Critical Flaws</span>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Zero unauthenticated RCE, zero SQL injection, pinned search_path = &apos;&apos; on PostgreSQL routines, and zero client credential leakage.
          </p>
        </div>

        <div className="flex flex-col gap-2 rounded-lg border border-border/50 bg-muted/10 p-5 transition-colors hover:bg-muted/20">
          <span className="font-mono text-2xl font-normal text-foreground">100%</span>
          <span className="font-medium text-sm text-foreground">Fail-Fast Production Secrets</span>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Development placeholder secrets are rejected at boot in production builds. Active auth providers require explicit cryptographically secure secrets.
          </p>
        </div>

        <div className="flex flex-col gap-2 rounded-lg border border-border/50 bg-muted/10 p-5 transition-colors hover:bg-muted/20">
          <span className="font-mono text-2xl font-normal text-foreground">Strict</span>
          <span className="font-medium text-sm text-foreground">Multi-Tenant &amp; Claim Binding</span>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Server stores enforce caller-token tenant isolation with 403 Forbidden rejection, and Keycloak JWTs bind azp, typ, and client-scoped roles.
          </p>
        </div>
      </div>
    </section>
  )
}
