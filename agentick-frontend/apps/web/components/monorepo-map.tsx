import { IconBox, IconLayersLinked, IconTerminal } from "@tabler/icons-react"
import { CountingNumber } from "@workspace/ui/components/animate-ui/numbers/counting-number"

const PACKAGES = [
  {
    path: "apps/studio",
    type: "app",
    role: "Production dashboard with Next.js 16.4, PPR & Cache Components",
    tag: "Next.js 16",
  },
  {
    path: "apps/web",
    type: "app",
    role: "Landing page and public-facing marketing entrypoint",
    tag: "Next.js 16",
  },
  {
    path: "packages/auth",
    type: "package",
    role: "Unified auth seam for Keycloak, Better Auth, and Supabase",
    tag: "@workspace/auth",
  },
  {
    path: "packages/db",
    type: "package",
    role: "PostgreSQL database access, migrations & connection pooling",
    tag: "@workspace/db",
  },
  {
    path: "packages/ui",
    type: "package",
    role: "Zinc base-nova theme tokens, shadcn components & Animate UI",
    tag: "@workspace/ui",
  },
  {
    path: "packages/ui-patterns",
    type: "package",
    role: "Shared composite widgets: AppLogo, ThemeToggle, StackGrid",
    tag: "@workspace/ui-patterns",
  },
] as const

export function MonorepoMap() {
  return (
    <div className="flex flex-col overflow-hidden rounded-lg border border-border/50 bg-muted/10">
      <div className="flex items-center justify-between border-b border-border/40 bg-muted/20 px-4 py-3">
        <div className="flex items-center gap-2">
          <IconLayersLinked className="size-4 text-muted-foreground" />
          <span className="font-mono text-xs font-medium text-foreground">
            Turborepo Workspace Topology
          </span>
        </div>
        <span className="font-mono text-xs text-muted-foreground">
          pnpm-workspace.yaml
        </span>
      </div>

      <div className="divide-y divide-border/40 font-mono text-xs">
        {PACKAGES.map((pkg) => (
          <div
            key={pkg.path}
            className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 sm:gap-4 p-3.5 transition-colors hover:bg-muted/20"
          >
            <div className="flex items-center gap-2.5">
              <IconBox className="size-3.5 text-muted-foreground shrink-0" />
              <span className="font-medium text-foreground">{pkg.path}</span>
            </div>
            <p className="text-muted-foreground text-xs flex-1 leading-normal">
              {pkg.role}
            </p>
            <span className="inline-flex w-fit items-center rounded border border-border/60 bg-background/80 px-2 py-0.5 text-xs text-muted-foreground shrink-0 self-start sm:self-auto">
              {pkg.tag}
            </span>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between border-t border-border/40 bg-muted/20 px-4 py-2.5 text-xs font-mono text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <IconTerminal className="size-3.5" />
          <span>pnpm check</span>
        </div>
        <div className="flex items-center gap-1">
          <CountingNumber number={16} />
          <span>parallel tasks cached in ~14ms</span>
        </div>
      </div>
    </div>
  )
}
