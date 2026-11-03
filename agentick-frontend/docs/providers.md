# Providers: Better Auth + FastAPI, Supabase, Keycloak, or FastAPI OAuth2

`apps/studio` is built to run on one of four **stacks**, chosen by a single env var. Pages, queries, actions, cache,
components and the DAL do not know which one is active.

| `AUTH_PROVIDER` | Identity | Data and business rules | Schema lives in |
| :--- | :--- | :--- | :--- |
| `better-auth` | Better Auth inside Next (`/api/auth/*`), EdDSA JWT | FastAPI (`your FastAPI backend`) through `apiFetch` | `your FastAPI backend/migrations` (Alembic) |
| `supabase` | Supabase Auth (GoTrue), ES256 JWT, cookies via `@supabase/ssr` | PostgREST + RLS + SQL functions through `createDataClient` | `packages/db/supabase/migrations` (Supabase CLI) |
| `keycloak` | Standalone Keycloak 26 OIDC server, RS256 JWT | FastAPI or PostgREST through `Session.accessToken` (Bearer) | Realm export in `d:\Dev_Projects\keycloak-idp\realms` |
| `fastapi-oauth` | `your FastAPI backend` is the IdP itself (OAuth2 password flow), HS256 JWT | Same FastAPI backend, same request (`Session.accessToken`) | `your FastAPI backend/migrations` (Alembic, `users` table) |

**Current state.** A project built on the base can run on `supabase` (hosted project, foundation schema only; the studio
uses it through `packages/auth` and `packages/db`). All stacks stay in the base: switching `AUTH_PROVIDER` still works
for a project that wants Better Auth + FastAPI, Keycloak, or pure FastAPI OAuth2. History below is the base's: the Supabase **foundation**
stays in the base (§1) so a new project can start on Supabase without setup work. The original Supabase data path (schema, RLS, SQL functions, pgTAP tests, the
`server.supabase.ts` files, the calendar hook) was built, passed parity on both stacks, then removed; it is kept in
commit `91c11f0` as a complete reference (§2.3). With today's code, `AUTH_PROVIDER=supabase` signs users in but feature
data still goes to FastAPI, which does not know Supabase users: it is not runnable end-to-end until §2.2 or §2.3 is done.

Not supported on purpose (each would double the test matrix): switching at runtime, a generic repository layer, mixing an
identity with the other data path without the backend work in §8.

## 1. The Supabase foundation (kept in the base)

Paths relative to `apps/studio/`.

| Piece | Files | What it gives a new project |
| :--- | :--- | :--- |
| Config | `packages/auth/src/config.ts`, `.env.example`, `turbo.json` env | `AUTH_PROVIDER` union; the `supabase` branch needs only URL + publishable key |
| Identity | `packages/auth/src/supabase/{server,proxy}.ts`, `packages/auth/src/server.ts`, `packages/auth/src/proxy.ts` | `getClaims()` (local JWT check), `getUser()` for fresh checks, token refresh only in the proxy, `scope: "local"` sign-out, OAuth start |
| OAuth callback | `app/auth/callback/route.ts` | `exchangeCodeForSession`; Better Auth's `/api/auth/*` answers 404 on this stack |
| Data client | `@workspace/db/server`, `packages/db/src/database.types.ts` (placeholder) | `createDataClient(accessToken)`: requests run as the user so RLS applies; `unwrap` throws `DataError`. A rejected token (`PGRST301` / `PGRST303`) is not handled inside the package: the app's feature `server.ts` maps it to `endRejectedSession()` (`lib/http.ts`) |
| Errors | `lib/errors.ts` | `DataError` + `isExpectedDataError` cover both paths; actions return rule errors as values |
| Calendar seam | `Session.calendar`, `AuthProvider.refreshSession`, `getCalendar()`, `refreshSessionClaims()` | A provider that puts timezone / week start / adoption date in the token saves a settings read per page (§5) |
| CLI project | `supabase/config.toml`, `supabase/.gitignore` | Local stack settings, ES256 signing keys path, hook block (commented) |
| CSP | `next.config.ts` | `form-action` adds the Supabase origin on this stack |
| ESLint | `eslint.config.js` | Only `server.ts` may import `server.api` / `server.supabase`; components import no `server.*` |

## 2. Running each stack

### 2.1 Better Auth + FastAPI
1. `apps/studio/.env.local`: the `better-auth` block of `.env.example`.
2. `docker compose up -d` in `your FastAPI backend` (Postgres on host port 5433, API on 8000).
3. `pnpm --filter studio dev`.

### 2.2 A new project on Supabase (from this base)
Commands run from `packages/db` with `pnpm exec` (the Supabase CLI and `supabase/` live there).
1. Create the project in the region closest to **where Next will be deployed** (and to users): every data call is one
   network round trip (§5). `.env.local`: `AUTH_PROVIDER=supabase`, `NEXT_PUBLIC_SUPABASE_URL`,
   `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`. Never a secret or `service_role` key.
2. `supabase login` (or `SUPABASE_ACCESS_TOKEN`, a scoped token), `supabase link --project-ref <ref>`.
3. Schema: `supabase migration new <name>`, write the SQL (rules in §4), `supabase db push`,
   `supabase db advisors --linked`, then `supabase gen types typescript --linked > packages/db/src/database.types.ts`.
4. Feature data: a project with one stack writes `features/<x>/server.ts` directly with `createDataClient` + `unwrap`.
   A repo that keeps both stacks uses the selector: `server.ts` picks `server.api.ts` or `server.supabase.ts` and types
   the second as `typeof api`, so `tsc` fails when they drift (example: `git show 91c11f0:apps/studio/features/goals/server.ts`).
5. Auth settings: site URL and `<app>/auth/callback` as a redirect URL, in the dashboard or with `supabase config push`.
   `config push` writes **every** property `config.toml` declares, including local-only ones (email rate limit, MFA
   off): to push one block, run it with `--workdir <dir>` whose `supabase/config.toml` declares only that block, and
   preview with `supabase config diff`.
6. `pnpm --filter studio dev`; then the parity checklist (§7) for the flows the project has.

### 2.3 Back on Supabase
Everything is in commit `91c11f0`:
1. For each feature: `git mv features/<x>/server.ts features/<x>/server.api.ts`, then
   `git checkout 91c11f0 -- features/<x>/server.ts features/<x>/server.supabase.ts`.
2. `git checkout 91c11f0 -- supabase/migrations supabase/tests supabase/seed.sql packages/db/src/database.types.ts`.
3. `supabase db push`, then enable the hook (uncomment `[auth.hook.custom_access_token]`; push only that block as in
   §2.2.5). Push the migrations first: an enabled hook whose function is missing blocks every sign-in.
4. `e2e/parity.spec.ts` on both stacks (8/8 each at `91c11f0`).

### 2.4 Keycloak IDP
1. In `d:\Dev_Projects\keycloak-idp`: `docker compose up -d` (starts Keycloak 26 on port 8080 and Postgres 17; imports the `studio` realm).
2. `apps/studio/.env.local`: `AUTH_PROVIDER=keycloak`, `KEYCLOAK_ISSUER=http://localhost:8080/realms/studio`, `KEYCLOAK_CLIENT_ID=studio-app`, `KEYCLOAK_CLIENT_SECRET=studio-dev-client-secret-at-least-32-chars`.
3. `pnpm --filter studio dev`.

### 2.5 FastAPI OAuth2 (pure)
No Better Auth: the backend hashes passwords (`bcrypt`), stores its own `users` table, and issues/verifies its
own JWTs (`PyJWT`, HS256). There is no JWKS endpoint — issuer and verifier are the same service, so the frontend
verifies the signature with a secret it must be given, not a published public key.
1. `docker compose up -d` in `your FastAPI backend` (same backend as the `better-auth` stack).
2. `apps/studio/.env.local`: `AUTH_PROVIDER=fastapi-oauth`, `API_BASE_URL=http://localhost:11030`,
   `JWT_SECRET_KEY=<same value as the backend's own JWT_SECRET_KEY>`.
3. `pnpm --filter studio dev`.
No social login: the backend doesn't implement any, so `SocialAuthButtons` shows both buttons disabled on this stack.

## 3. The seams (the only code that knows the provider)

| Seam | Files | Rule |
| :--- | :--- | :--- |
| Config | `packages/auth/src/config.ts` | Discriminated union on `AUTH_PROVIDER`; each stack lists only its own env vars |
| Identity | `packages/auth/src/{better-auth,supabase,keycloak,fastapi-oauth}/` | Implements `AuthProvider` (`types.ts`) + proxy `updateSession`; picked in `packages/auth/src/server.ts` and `packages/auth/src/proxy.ts` |
| Feature data | `features/<x>/server.ts` (+ `server.api.ts` / `server.supabase.ts` when both exist) | Returns the same Zod-parsed DTOs on every path; nothing else calls a backend |
| Errors | `lib/errors.ts` | `isExpectedDataError` covers `ApiError` (4xx) and `DataError` (rule/constraint codes); a rejected token ends the session on both paths |
| Calendar in the token | `Session.calendar`, `AuthProvider.refreshSession`, `getCalendar()` (`features/settings/queries.ts`) | Optional: without it `getCalendar()` falls back to the settings read |
| OAuth callback | `app/auth/callback/route.ts` | Only Supabase and Keycloak use it; Better Auth handles its own callback |
| CSP | `next.config.ts` | `form-action` adds the Supabase / Keycloak origin only on those stacks |

## 4. Developing on each provider

Both stacks:
- Backend calls live only in `features/<x>/server*.ts` and the DAL; components never import them (ESLint).
- `server*.ts` throws (`ApiError` / `DataError`); actions return `isExpectedDataError` cases as values (message without
  the `XX-n:` prefix, `rule` from `ruleOf`) and rethrow the rest. A failed read throws; it never becomes `[]`.
- A token the backend rejects, or a user deleted while the token lives, calls `endRejectedSession()` (→ `/auth/expired`).
- Data that changes a token claim (`calendar`): the action calls `refreshSessionClaims()` after the write.

Supabase specifically (Supabase skill: `.agents/skills/supabase`):
- Every table in `public`: RLS on, explicit `grant`s (new projects do not expose tables to the Data API), policies
  `to authenticated` with the ownership check in `using` **and** `with check` for updates.
- Rules that span rows or must not be bypassed go in SQL (`check`, triggers, RPCs). `security definer` only in the
  `private` schema, with an `auth.uid()` check, `set search_path = ''`, `execute` revoked from `public`/`anon`.
- Roles from `app_metadata` (never `user_metadata`). `getClaims()` for identity, `getUser()` before sensitive actions,
  `getSession()` only to forward the token. Tokens are refreshed only in `proxy.ts`.
- After each migration: `db push`, `db advisors --linked`, `gen types`. pgTAP (`supabase test db`) needs the local CLI
  stack; this project works on the cloud project only.

FastAPI specifically: the API contract is `your FastAPI backend`'s OpenAPI (`/openapi.json`); regenerate `lib/api/schema.d.ts`
after it changes. Business rules are enforced in the service layer and mirrored in `features/<x>/rules.ts` for the UI.

## 5. Latency: what was measured and what to do

Measured on Supabase cloud (ap-south-1) from Vietnam, production build:
- Postgres time per query ~0.06 ms (`supabase inspect db calls --linked`); the network round trip ~150 ms. A page costs
  its number of **sequential** round trips, not its number of queries. Indexes and query tuning do not help at this size.
- Pages read settings (timezone) before the today-keyed reads: two round trips in a row, hard load ~630 ms.
- Timezone, week start and adoption date in the JWT (hook) + the goal read started alongside the rest: ~315 ms on all six
  dashboard pages, the same as local FastAPI. The floor is React's Suspense reveal, not data.

Rules:
1. Deploy Next in the database's region; choose the region by where Next runs. This alone turns 150 ms into a few ms.
2. Count sequential awaits that hit the network. Start every independent read before the first `await`
   ([data-fetching §4.2](data-fetching.md#42-parallel-and-sequential-reads)).
3. A per-user value most pages need first and that rarely changes belongs in the token: a Custom Access Token Hook
   (Supabase) adds the claim; the provider exposes it on `Session`; the action that changes it refreshes the token. The
   e2e test must fail when the refresh is removed (`parity.spec.ts`: "changing the timezone moves Today at once").
4. A not-found check need not run first: start the dependent reads, mark them handled (`reads.catch(() => {})`), check
   the entity, then `await` the reads. Trade-off on FastAPI: the refused read is logged as a server error on that 404.
5. Measure before and after in the same conditions: A/B the same build with a switch, check that the server on the port
   is the one you started.

## 6. Behaviour that differs (documented, not hidden)

| | `better-auth` | `supabase` |
| :--- | :--- | :--- |
| "Today" | Python (`core/clock.py`, D11) | SQL `private.today_for()` using `user_settings.timezone` |
| Timezone names | Python `zoneinfo` | Postgres `pg_timezone_names`; checked in `validate_timezone` (TM-2) |
| Revocation delay | ≤ 5 min (cookie cache) | ≤ JWT expiry (1 h default); `verifySessionFresh` asks the server |
| Role source | `user.role` column → JWT claim | `app_metadata.role` (never `user_metadata`) |
| Email confirmation | Off (Q2) | Project setting; `signUp` returns `confirm-email` when on |
| Deleted user with a live token | API 401 → `/auth/expired` | Missing settings row → treated as an ended session |
| Timezone, week start for "today" | Settings read (API, ~5 ms locally) | JWT claims from the hook. Saving settings refreshes the token at once; another device sees the change at its next refresh (≤ 1 h) |

## 7. Parity checklist

Automated in `apps/studio/e2e/parity.spec.ts`: switch `AUTH_PROVIDER`, restart `next dev`, run it again.

- Sign up → Today, timezone synced from the browser; sign out → sign in; wrong password keeps the email.
- Goal → habit from the goal page → full / minimum / undo → reload keeps it; streak updates.
- Back-date day −3 allowed; −4 refused (AC-5).
- `#slug` task → done → "Add to log?" → activity on the goal; pet +1.
- 4th active goal refused (GL-3).
- Weekly review with a pause and two focus tasks (RV-3, RV-4).
- Preferences: timezone (browser list), week start, pet name persist.
- Changing the timezone moves Today at once (the token claims are refreshed).
- Another user's ids: nothing readable, nothing writable.
- Session ended on the server → next navigation reaches sign-in without a loop.

## 8. Adding another stack, or mixing

Implement `AuthProvider` + `updateSession` in `packages/auth/src/<name>/`, the feature data per §2.2.4, extend the config union and
`.env.example`, then run §7. If only the identity changes (e.g. Supabase Auth with FastAPI), skip the data files: point
FastAPI's `AUTH_JWKS_URL` / `AUTH_ISSUER` / `AUTH_AUDIENCE` at the provider (Supabase:
`https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`, issuer `https://<ref>.supabase.co/auth/v1`, audience
`authenticated`) and make FastAPI accept users it did not create (today `get_existing_user` returns 401 for them).

## 9. History

Built in `91c11f0`: one switch for the whole stack; Supabase stack restored from `520fc96^` instead of rewritten; schema
pushed to a cloud project; three never-run pgTAP files fixed (50/50); advisors clean; PostgREST probed with real tokens
(13/13: AC-5, GL-3, cross-user read/update/delete/RPC refused, anon and forged tokens refused); parity 8/8 on both
stacks; the latency work of §5. The next commit kept only the foundation (§1).
