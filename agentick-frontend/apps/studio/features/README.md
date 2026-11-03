# features/

One folder per business domain (vertical slice). A feature owns its UI, data access,
validation and mutations, and knows nothing about routes.

```
features/<name>/
  components/   UI shared across pages or around the feature
  server.ts     "server-only": the only backend calls (FastAPI via lib/http, or PostgREST via @workspace/db/server).
                A repo that keeps both stacks splits it (docs/providers.md §2.2):
    server.api.ts       FastAPI via lib/http (AUTH_PROVIDER=better-auth)
    server.supabase.ts  PostgREST + RLS via @workspace/db/server (AUTH_PROVIDER=supabase)
  queries.ts    reads for Server Components (auth via lib/dal, "use cache" here)
  actions.ts    "use server": mutations (validate with Zod, verify session first)
  schemas.ts    Zod schemas + types, usable on client and server
  __tests__/
```

Create only the files a feature needs.

## Reference Implementation

- **`features/auth`**: Complete vertical slice implementation demonstrating authentication actions (`signInAction`, `signUpAction`, `signOutAction`), schema validation and session handling. Its forms in `components/` hold no logic: each takes the Server Action as an `action` prop. Its forms live in `packages/auth-ui` and receive these actions as props.

- **`features/workspace`**: organizations and projects (the `/org/<slug>` and `/project/<ref>` scopes). A read + write slice
  over a mock `server.ts`: `queries.ts` with a per-user `"use cache: private"` read, `actions.ts` creating records with
  `updateTag` + `redirect`, create dialogs using `useActionState`, and tests of the mock backend. Swap `server.ts` to go live.

## Rules (enforced in `eslint.config.js`)

- `features/*` never imports `app/` and never imports another feature (compose in `app/`).
- Same-feature imports are relative; cross-layer imports use `@/`.
- `components/` never imports `server.ts`, `server.*.ts`, `queries.ts`, `lib/dal` or `lib/http`.
- When both stacks exist, only `server.ts` imports `server.api.ts` / `server.supabase.ts`; it types the Supabase module
  as `typeof api`, so a function missing or different on one path fails `tsc`.
- No barrel `index.ts`; import the file you need.

See [docs/project-structure.md](../../../docs/project-structure.md) for the complete architecture guide and package extraction rules.
