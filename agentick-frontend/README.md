# next-mono-base

Next.js 16.4 + TanStack Redact + Turborepo + pnpm monorepo base with shadcn/ui (`base-nova` + Animate UI) and pluggable tri-stack authentication (`keycloak` | `better-auth` | `supabase`).

## Structure

```
apps/
  web/                    Next.js landing page (runnable, public, withRedact browser runtime)
  studio/                 Next.js dashboard: sign-in, organizations, projects (runnable, withRedact browser runtime)
packages/
  ui/                     @workspace/ui — shared shadcn/ui components, styles
  auth/                   @workspace/auth — Keycloak / Better Auth / Supabase providers behind AUTH_PROVIDER
  ui-patterns/            @workspace/ui-patterns — pieces both apps share: ThemeProvider, ThemeToggle, AppLogo, StackGrid
  db/                     @workspace/db — Supabase & PostgreSQL clients, types, migrations
  eslint-config/          @workspace/eslint-config
  typescript-config/      @workspace/typescript-config
```

`apps/` holds things that run; `packages/` holds everything shared. Packages are
scoped `@workspace/*`, declared with `workspace:*`, and never nested or imported via `../`.

## Commands

```bash
pnpm install
pnpm dev                          # all apps: web (landing) on :3000, studio (dashboard) on :3001
pnpm turbo run dev --filter=studio   # one app
pnpm build
pnpm check                        # lint + typecheck
```

## Adding shadcn components

```bash
pnpm dlx shadcn@latest add button -c apps/studio
```

Components land in `packages/ui/src/components`; import with
`import { Button } from "@workspace/ui/components/button"`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions.
