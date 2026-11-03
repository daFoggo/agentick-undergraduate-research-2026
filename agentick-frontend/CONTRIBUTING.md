# Contributing

## Setup

- Node: see `.nvmrc`. Package manager: pnpm, pinned via `packageManager` in `package.json`.
- `pnpm install`, then `pnpm dev`.

## Conventions

- Run tasks through `turbo run <task>` (root scripts already do); use `--filter=<name>` for one package.
- Install a dependency in the package that uses it (`pnpm add x --filter studio`); the root only holds repo tooling (`turbo`, `prettier`).
- Internal deps use `workspace:*`. Shared code goes in `packages/`, never in an app.
- Packages expose entrypoints via `exports`; avoid barrel `index.ts` files.
- No root `tsconfig.json`; each package extends `@workspace/typescript-config`.
- Env files live in each app (`apps/studio/.env*`), not the root. Env vars that affect
  builds must be declared in `turbo.json` (`env`/`globalEnv`); `NEXT_PUBLIC_*` is inferred for Next.js.
- App code is feature-based: see `apps/studio/features/README.md`. `app/` only composes features; feature boundaries are enforced by ESLint (warnings fail `pnpm lint` via `--max-warnings 0`).
- Extract code into `packages/` only when a second consumer exists, it has a different deploy target, or it is published; otherwise keep it in the app.
- Before pushing: `pnpm check`.

## Tests, commits, CI

- Unit tests use Vitest (`pnpm test`, or `pnpm turbo run test --filter=@workspace/ui`).
- E2E specs (Playwright, `apps/studio/e2e`) run with `pnpm --filter studio test:e2e` against a running app (`BASE_URL`). The instant navigation gate is separate: `pnpm --filter studio test:e2e:instant` needs a production build and server started with `EXPOSE_TESTING_API=1`; see `docs/advanced-patterns.md` §1.4. It is a local gate, CI does not run it.
- Commit messages follow Conventional Commits, enforced by commitlint via a husky `commit-msg` hook.
- CI runs `lint typecheck test build` with `--affected` on a full-history checkout.
  `next build` needs the Supabase public values, so CI takes `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` from repository variables (public values; set with `gh variable set`).
- Only pnpm is allowed (`only-allow` in `preinstall`).
