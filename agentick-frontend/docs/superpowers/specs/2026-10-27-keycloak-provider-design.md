# Keycloak Auth Provider & Standalone Docker Stack Design

- **Date:** 2026-10-27
- **Status:** Draft (Pending Approval)
- **Repositories:**
  - `d:\Dev_Projects\keycloak-idp` (New standalone Docker Compose project for Keycloak)
  - `d:\Dev_Projects\next-mono-base` (Monorepo integration for `AUTH_PROVIDER=keycloak`)

---

## 1. Intent and Why

`next-mono-base` is architected around a strict provider seam (`@workspace/auth` and `apps/studio/lib/dal.ts`) that currently supports two stacks selected via `AUTH_PROVIDER`:
1. `better-auth` (Self-hosted Better Auth + PostgreSQL + FastAPI)
2. `supabase` (Supabase Auth + PostgREST/RLS)

The goal of this project is to add **`keycloak`** as a third first-class identity provider in the base repository, backed by a standalone Docker project (`d:\Dev_Projects\keycloak-idp`), following Keycloak's official documentation and OAuth 2.1 / OpenID Connect (OIDC) best practices. Switching `AUTH_PROVIDER` between `better-auth`, `supabase`, and `keycloak` must require only changing environment variables, with zero cross-provider interference.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
1. **Standalone Keycloak Docker Project (`d:\Dev_Projects\keycloak-idp`):**
   - Run `quay.io/keycloak/keycloak:26.0` backed by `postgres:17-alpine` on host port `8080` so state persists across container restarts.
   - Automatically provision a complete `studio` realm on first startup using `--import-realm` (`realms/studio-realm.json`).
   - Pre-configure the confidential OIDC client (`studio-app`), PKCE (`S256`), realm roles (`admin`, `editor`, `customer`), protocol mappers for `role` and `calendar` claims, and three pre-seeded test users (`admin@next-mono-base.local`, `editor@next-mono-base.local`, `customer@next-mono-base.local`).
2. **Standards-Compliant OIDC in `@workspace/auth` (`packages/auth/src/keycloak/`):**
   - Implement `AuthProvider` (`server.ts`) and `updateSession` (`proxy.ts`) using OIDC Authorization Code Flow with PKCE (`S256`) and `state` CSRF protection.
   - Validate Access Tokens locally with `jose` (`createRemoteJWKSet` + `jwtVerify`) against Keycloak's JWKS endpoint (`/protocol/openid-connect/certs`) with zero network calls per page request when the token is valid.
   - Refresh expiring tokens transparently in `proxy.ts` via `grant_type=refresh_token` and propagate refreshed cookies across redirects via `redirectWithSession`.
   - Perform server-side RP-Initiated / Backchannel Logout against Keycloak's `/protocol/openid-connect/logout` endpoint on `signOut()`.
3. **Provider-Aware Auth UI in `apps/studio`:**
   - Keep existing Email/Password forms untouched for `better-auth` and `supabase`.
   - Render OIDC redirect actions ("Continue with Keycloak" on `/sign-in`, "Create account with Keycloak" on `/sign-up`) when `AUTH_PROVIDER=keycloak`, plus the existing Demo Login button if `DEMO_AUTH` is enabled.
4. **Full Verification & Documentation:**
   - Unit tests for Keycloak JWT/JWKS verification, role resolution, multi-cookie management, PKCE/state validation, and proxy refresh.
   - Update `docs/authentication.md`, `docs/providers.md`, `apps/studio/.env.example`, `apps/studio/next.config.ts` (CSP `form-action`), and `turbo.json`.

### Non-Goals
- Modifying existing `better-auth` or `supabase` runtime logic.
- Implementing SAML 2.0 or deprecated OAuth 2.0 Resource Owner Password Credentials (ROPC / Direct Access Grants).
- Using the browser-only `keycloak-js` SPA adapter.

### Anti-Goals
- Making network calls to Keycloak on every Server Component render (`getSession()` must verify JWTs locally via cached JWKS).
- Storing all tokens in a single browser cookie that could exceed the 4096-byte browser cookie limit and silently fail.
- Breaking `pnpm check`, `pnpm test`, or `pnpm build` under any `AUTH_PROVIDER`.

---

## 3. Constraints

1. **Next.js 16.4 Cache Components (`cacheComponents: true`):**
   - `getSession()` in `apps/studio/lib/dal.ts` runs inside `"use cache: private"`. Any clock-based JWT check must call `await io()` from `next/cache` before reading `cookies()` or checking `Date.now()` so prerendering suspends cleanly without blocking partial prefetching.
   - Server Components cannot set or delete cookies. Token refresh must happen exclusively in `proxy.ts`, and login/logout cookie mutations must happen in Server Actions or Route Handlers.
2. **Cookie Size Limit (4096 bytes):**
   - Keycloak tokens (`access_token`, `refresh_token`, `id_token`) are RS256-signed JWTs averaging 1.1–1.8 KB each. They must be stored in separate `httpOnly` cookies prefixed by `AuthOptions.cookieName`.
3. **Content Security Policy (CSP):**
   - `apps/studio/next.config.ts` restricts `form-action`. Because `<OAuthButton>` submits a `<form>` to a Server Action that redirects (`303`) to the Keycloak server, `new URL(process.env.KEYCLOAK_ISSUER).origin` must be added to `form-action` when `AUTH_PROVIDER=keycloak`.
4. **ESLint Architectural Boundaries:**
   - `features/*/components/**` and `components/**` in `apps/studio` are forbidden from importing `@workspace/auth/config`, `@workspace/auth/server`, or `@/lib/auth`. Provider branching for UI must happen in `app/(auth)/sign-in/page.tsx` and `app/(auth)/sign-up/page.tsx` (or via props passed from `app/`).

---

## 4. Approaches Considered

### Approach 1 (Selected): Direct OIDC Endpoints + `jose` JWKS + Split HttpOnly Cookies
- **Description:** Use `jose` (`createRemoteJWKSet` + `jwtVerify`) for local RS256/ES256 JWT verification and Node's built-in `node:crypto` / Web Crypto API + `fetch` for Keycloak's deterministic OIDC endpoints (`/protocol/openid-connect/{auth,registrations,token,userinfo,logout,certs}`). Store tokens in split `httpOnly` cookies (`{cookieName}.access`, `{cookieName}.refresh`, `{cookieName}.id`, `{cookieName}.pkce`).
- **Trade-offs:** Requires ~150 lines of clean OIDC protocol code in `packages/auth/src/keycloak/`, in exchange for zero discovery round-trips, full control over Next.js `NextRequest`/`NextResponse` cookie propagation in `proxy.ts`, and only one lightweight dependency (`jose`).

### Approach 2: `openid-client` Discovery + `jose`
- **Description:** Use `openid-client` to dynamically fetch `/.well-known/openid-configuration` and manage OIDC flows.
- **Trade-offs:** Saves manual URL construction but adds cold-start network latency to fetch discovery metadata, requires workarounds for HTTP localhost (`allowInsecureRequests`), and still requires custom cookie splitting and `jose` verification.

---

## 5. Detailed Design

### 5.1 Standalone Docker Project (`d:\Dev_Projects\keycloak-idp`)

Directory layout:
```text
d:\Dev_Projects\keycloak-idp\
├── docker-compose.yml
├── .env
├── .env.example
├── README.md
└── realms\
    └── studio-realm.json
```

#### `docker-compose.yml`
- **`postgres` service:**
  - Image: `postgres:17-alpine`
  - Volume: `keycloak_pgdata:/var/lib/postgresql/data`
  - Healthcheck: `pg_isready -U ${POSTGRES_USER:-keycloak} -d ${POSTGRES_DB:-keycloak}`
- **`keycloak` service:**
  - Image: `quay.io/keycloak/keycloak:26.0`
  - Command: `start-dev --import-realm`
  - Ports: `8080:8080`
  - Environment:
    - `KC_DB=postgres`
    - `KC_DB_URL=jdbc:postgresql://postgres:5432/${POSTGRES_DB:-keycloak}`
    - `KC_DB_USERNAME=${POSTGRES_USER:-keycloak}`
    - `KC_DB_PASSWORD=${POSTGRES_PASSWORD:-keycloak}`
    - `KC_BOOTSTRAP_ADMIN_USERNAME=${KEYCLOAK_ADMIN:-admin}`
    - `KC_BOOTSTRAP_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD:-admin}`
    - `KC_HTTP_ENABLED=true`
    - `KC_HOSTNAME_STRICT=false`
    - `KC_HEALTH_ENABLED=true`
  - Volumes: `./realms:/opt/keycloak/data/import:ro`
  - Depends on `postgres` (`service_healthy`).

#### `realms/studio-realm.json`
- **Realm:** `studio` (`enabled: true`, `registrationAllowed: true`, `registrationEmailAsUsername: true`, `loginWithEmailAllowed: true`, `resetPasswordAllowed: true`, `rememberMe: true`).
- **Realm Roles:**
  - `customer` (added to `defaultRoles` of the realm so newly registered users automatically receive `customer`)
  - `editor`
  - `admin`
- **Client (`studio-app`):**
  - `clientId`: `"studio-app"`
  - `secret`: `"studio-dev-client-secret-at-least-32-chars"`
  - `publicClient`: `false` (Confidential client)
  - `standardFlowEnabled`: `true` (Authorization Code Flow)
  - `directAccessGrantsEnabled`: `false` (Disabled per OAuth 2.1 best practice)
  - `redirectUris`: `["http://localhost:3001/auth/callback"]`
  - `webOrigins`: `["http://localhost:3001"]`
  - `attributes`:
    - `"pkce.code.challenge.method"`: `"S256"`
    - `"post.logout.redirect.uris"`: `"http://localhost:3001/*"`
  - **Protocol Mappers on `studio-app`:**
    1. `realm-roles-mapper` (`oidc-usermodel-realm-role-mapper`): maps user realm roles into claim `roles` (multivalued array in both ID Token and Access Token) alongside standard `realm_access.roles`.
    2. `timezone-mapper`, `week-start-mapper`, `adopted-on-mapper` (`oidc-usermodel-attribute-mapper`): maps optional user attributes `timezone` (String), `week_start` (int), `adopted_on` (String) into the Access Token for the `Session.calendar` seam.
- **Pre-seeded Users:**
  1. `admin@next-mono-base.local` / `Password123!` (`firstName: "Admin"`, `lastName: "User"`, `emailVerified: true`, realmRoles: `["admin", "customer"]`)
  2. `editor@next-mono-base.local` / `Password123!` (`firstName: "Editor"`, `lastName: "User"`, `emailVerified: true`, realmRoles: `["editor", "customer"]`)
  3. `customer@next-mono-base.local` / `Password123!` (`firstName: "Customer"`, `lastName: "User"`, `emailVerified: true`, realmRoles: `["customer"]`)

---

### 5.2 Environment & Config Seam (`packages/auth/src/config.ts` & `turbo.json`)

Extend `authSchema` in `packages/auth/src/config.ts`:
```ts
  z.object({
    AUTH_PROVIDER: z.literal("keycloak"),
    KEYCLOAK_ISSUER: z.url(), // e.g. http://localhost:8080/realms/studio
    KEYCLOAK_CLIENT_ID: z.string().min(1),
    KEYCLOAK_CLIENT_SECRET: z.string().min(1),
  }),
```
Add `KEYCLOAK_ISSUER`, `KEYCLOAK_CLIENT_ID`, and `KEYCLOAK_CLIENT_SECRET` to `turbo.json` (`tasks.build.env`) and `apps/studio/.env.example`.

Update `packages/auth/src/server.ts` and `packages/auth/src/proxy.ts` to dispatch to `./keycloak/server` and `./keycloak/proxy` when `authConfig.AUTH_PROVIDER === "keycloak"`.

---

### 5.3 OIDC Endpoints, Cookies, and JWKS (`packages/auth/src/keycloak/`)

Files to create in `packages/auth/src/keycloak/`:
- `cookies.ts`:
  - Cookie names derived from `options.cookieName` (e.g. `nmb-studio-auth`):
    - `${cookieName}.access` (`httpOnly: true`, `sameSite: "lax"`, `secure: isProd`, `path: "/"`, `maxAge`: token `expires_in`)
    - `${cookieName}.refresh` (`httpOnly: true`, `sameSite: "lax"`, `secure: isProd`, `path: "/"`, `maxAge`: `refresh_expires_in` or 30 days)
    - `${cookieName}.id` (`httpOnly: true`, `sameSite: "lax"`, `secure: isProd`, `path: "/"`, `maxAge`: `refresh_expires_in` or 30 days)
    - `${cookieName}.pkce` (`httpOnly: true`, `sameSite: "lax"`, `secure: isProd`, `path: "/"`, `maxAge: 600` — stores JSON `{ state, codeVerifier, redirectTo }`)
- `jwks.ts`:
  - Uses `createRemoteJWKSet(new URL(`${issuer}/protocol/openid-connect/certs`))` cached per issuer URL in module scope.
  - `verifyKeycloakJwt(token, issuer)`: calls `jwtVerify(token, jwks, { issuer })` and extracts:
    - `userId`: `payload.sub`
    - `role`: highest-privilege role from `payload.roles` or `payload.realm_access?.roles` or `payload.role` (`admin` > `editor` > `customer`, fallback `customer` via `parseRole`).
    - `name`: `payload.name ?? payload.preferred_username ?? null`
    - `email`: `payload.email ?? null`
    - `calendar`: extracted if `timezone`, `week_start`, and `adopted_on` claims are present.
- `oidc.ts`:
  - Deterministic Keycloak OIDC endpoints derived from `KEYCLOAK_ISSUER`:
    - `authEndpoint`: `${issuer}/protocol/openid-connect/auth`
    - `registrationsEndpoint`: `${issuer}/protocol/openid-connect/registrations`
    - `tokenEndpoint`: `${issuer}/protocol/openid-connect/token`
    - `userinfoEndpoint`: `${issuer}/protocol/openid-connect/userinfo`
    - `logoutEndpoint`: `${issuer}/protocol/openid-connect/logout`
  - PKCE helpers: `generateCodeVerifier()`, `generateCodeChallenge(verifier)` (`S256`), `generateState()`.
  - `exchangeAuthorizationCode({ code, codeVerifier, redirectUri })` -> `POST /token` (`grant_type=authorization_code`).
  - `refreshTokenGrant(refreshToken)` -> `POST /token` (`grant_type=refresh_token`).
  - `fetchUserInfo(accessToken)` -> `GET /userinfo` (used by `verifySessionFresh()`).
  - `revokeAndLogout(refreshToken)` -> `POST /logout` (`client_id`, `client_secret`, `refresh_token`).
- `server.ts` (`createKeycloakProvider(options)`):
  - `getSession()`: `await io()`, reads `${cookieName}.access`, verifies via `verifyKeycloakJwt()`. Returns `Session | null`. Never mutates cookies.
  - `verifySessionFresh()`: calls `getSession()`, then confirms with `fetchUserInfo(session.accessToken)` that the session has not been revoked in Keycloak Admin Console. Returns `null` if Keycloak returns `401`.
  - `refreshSession()`: exchanges `${cookieName}.refresh` via `refreshTokenGrant()` and writes updated cookies (used when user claims change in a Server Action).
  - `signIn()` / `signUp()`: throws an error indicating Keycloak uses the OIDC redirect flow (`oauth.start`).
  - `signOut()`: reads `${cookieName}.refresh`, calls `revokeAndLogout(refreshToken)` (best-effort, catches network errors), and deletes `${cookieName}.access`, `${cookieName}.refresh`, `${cookieName}.id`, and `${cookieName}.pkce`.
  - `oauth.start(provider, redirectTo)`:
    - Supports `"keycloak"` (login at `/auth`), `"keycloak-register"` (registration at `/registrations`), and `"google"` (passes `kc_idp_hint=google` to `/auth`).
    - Generates `state` and `codeVerifier`, writes `${cookieName}.pkce` cookie, and returns the authorization URL with `client_id`, `response_type=code`, `scope=openid profile email`, `redirect_uri`, `state`, `code_challenge`, `code_challenge_method=S256`.
  - `oauth.exchangeCode(code, state)`:
    - Reads and deletes `${cookieName}.pkce` cookie.
    - Verifies `state` matches the cookie's `state` (throws on mismatch or missing cookie).
    - Exchanges `code` + `codeVerifier` for tokens and sets `${cookieName}.access`, `${cookieName}.refresh`, and `${cookieName}.id`.
- `proxy.ts` (`updateSession(request, options)`):
  - Short-circuits immediately (`{ response, isAuthenticated: false, role: null }`) if neither `${cookieName}.access` nor `${cookieName}.refresh` is present on `request.cookies`.
  - If `${cookieName}.access` is present and valid (`exp > now + 60s`), returns `{ response, isAuthenticated: true, role }` with zero network calls.
  - If `${cookieName}.access` is missing or expiring within 60 seconds and `${cookieName}.refresh` exists:
    - Calls `refreshTokenGrant(refreshToken)`.
    - On success: updates both `request.cookies` and `response.cookies` with the new token cookies, sets `Cache-Control: private, no-store`, verifies the new access token, and returns `{ response, isAuthenticated: true, role }`.
    - On failure (expired/revoked refresh token): deletes the session cookies on `response.cookies` and returns `{ response, isAuthenticated: false, role: null }`.

---

### 5.4 Callback Route & Auth Pages in `apps/studio`

1. **`packages/auth/src/types.ts`:**
   - Widen `OAuthStartProvider` to `"google" | "keycloak" | "keycloak-register"`.
   - Update `oauth.exchangeCode(code: string, state?: string | null): Promise<void>`.
2. **`apps/studio/app/auth/callback/route.ts`:**
   - Pass `searchParams.get("state")` as the second argument: `await provider.oauth.exchangeCode(code, state)`.
3. **`apps/studio/features/auth/actions.ts`:**
   - Add `signInWithKeycloakAction()` (calls `provider.oauth?.start("keycloak", callbackUrl)`) and `signUpWithKeycloakAction()` (calls `provider.oauth?.start("keycloak-register", callbackUrl)`).
4. **`apps/studio/app/(auth)/sign-in/page.tsx` & `sign-up/page.tsx`:**
   - Read `authConfig.AUTH_PROVIDER` (or export `isKeycloakAuth()` from `@/lib/auth`).
   - When `AUTH_PROVIDER === "keycloak"`:
     - `/sign-in` renders `<OAuthButton action={signInWithKeycloakAction}>Continue with Keycloak</OAuthButton>` (plus `<DemoSignInButton>` if enabled).
     - `/sign-up` renders `<OAuthButton action={signUpWithKeycloakAction}>Create account with Keycloak</OAuthButton>`.
   - When `AUTH_PROVIDER` is `better-auth` or `supabase`:
     - Renders the existing `<SignInForm>` / `<SignUpForm>` unchanged.
5. **`apps/studio/next.config.ts`:**
   - When `process.env.AUTH_PROVIDER === "keycloak"` and `process.env.KEYCLOAK_ISSUER` is set, push `new URL(process.env.KEYCLOAK_ISSUER).origin` to `formActions` in `contentSecurityPolicy()`.

---

## 6. What Is Left to the Builder

- Exact file splitting or internal helper naming inside `packages/auth/src/keycloak/` as long as only `server.ts` and `proxy.ts` are imported by `packages/auth/src/{server,proxy}.ts`.
- Choosing the exact `jose` version compatible with Node 20+ / TypeScript 5 (`jose@^6`).
- Writing the `README.md` in `d:\Dev_Projects\keycloak-idp` with quick-start commands and test credentials table.
