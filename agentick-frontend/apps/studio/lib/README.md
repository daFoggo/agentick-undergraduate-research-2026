# lib/

App infrastructure, not tied to one feature. Server-only modules start with `import "server-only"`.

- `env.ts` / `env.public.ts`: validated env (server-only / browser-safe).
- `http.ts`: backend `fetch` wrapper (only feature `server.api.ts` files import it). A `401` on a token ends the session
  (`endRejectedSession`; Supabase feature code calls it for `PGRST301` / `PGRST303` from `@workspace/db/server`).
- `errors.ts`: `ApiError`, `DataError` (from `@workspace/db/errors`), `isExpectedDataError` (backend `4xx` or an expected Postgres code: return from
  actions as a value), `ruleOf`, `getErrorMessage`.
- Supabase data path: `createDataClient(accessToken)` (RLS as the user) and `unwrap` live in `@workspace/db/server`;
  generated types in `@workspace/db/types` (`pnpm --filter @workspace/db db:types`).
- `dal.ts`: Data Access Layer: `getSession` (`"use cache: private"`, one read per request), `verifySession`,
  `refreshSessionClaims` (after a write that changes a token claim). Call next to the data.
- `auth.ts`: `getAuthProvider()`, the `@workspace/auth` provider bound to this app's cookie (`config/auth.ts`).
  **One provider per deployment** via `AUTH_PROVIDER=better-auth|supabase` (docs/providers.md). The adapters
  (`better-auth/`, `supabase/`), the auth env (`@workspace/auth/config`) and the proxy refresh
  (`@workspace/auth/proxy`, the **only** place that refreshes tokens) live in `packages/auth`.
