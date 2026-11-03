# Keycloak Auth Provider & Docker Stack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Docker Compose Keycloak 26 + PostgreSQL stack (`d:\Dev_Projects\keycloak-idp`) with an auto-imported `studio` realm, and integrate `AUTH_PROVIDER=keycloak` as a third first-class provider in `@workspace/auth` and `apps/studio`.

**Architecture:** `@workspace/auth` gains a `keycloak` module using `jose` (`createRemoteJWKSet` + `jwtVerify`) for zero-network-call local JWT verification, split `httpOnly` cookies (`{cookieName}.{access,refresh,id,pkce}`) to stay under the 4KB browser limit, OIDC Authorization Code Flow with PKCE (`S256`) + `state` CSRF verification, transparent refresh in `proxy.ts`, and server-side RP-Initiated logout. `apps/studio` branches `/sign-in` and `/sign-up` UI cleanly when `AUTH_PROVIDER=keycloak` while keeping `better-auth` and `supabase` untouched.

**Tech Stack:** Keycloak 26.0, PostgreSQL 17, Next.js 16.4 (`cacheComponents: true`), TypeScript 5, `jose`, Vitest, Zod v4, Turborepo.

**Spec:** `d:\Dev_Projects\next-mono-base\docs\superpowers\specs\2026-10-27-keycloak-provider-design.md`

## Global Constraints

- `getSession()` in `packages/auth/src/keycloak/server.ts` MUST call `await io()` from `next/cache` before reading `cookies()` or checking JWT expiration so Next.js 16.4 Cache Components prerendering suspends cleanly.
- Server Components cannot mutate cookies; token refresh happens only in `proxy.ts` (`updateSession`) and `refreshSession()` (called from Server Actions).
- Tokens MUST be split into separate cookies (`${cookieName}.access`, `${cookieName}.refresh`, `${cookieName}.id`, `${cookieName}.pkce`) so no single cookie approaches the 4096-byte limit.
- `features/*/components/**` and `components/**` in `apps/studio` MUST NOT import `@workspace/auth/config`, `@workspace/auth/server`, or `@/lib/auth` (enforced by ESLint).
- `pnpm check`, `pnpm test`, and `pnpm build` must pass without errors or warnings.

## Review Focus

1. **Multi-role users in Keycloak (`default-roles-studio` + `admin`):** Keycloak assigns every user the default realm role (`customer` / `default-roles-studio`) alongside elevated roles (`admin`, `editor`). Role resolution must pick the highest privilege (`admin` > `editor` > `customer`) rather than `roles[0]`.
2. **State mismatch or missing PKCE cookie on `/auth/callback`:** If a user replays a callback URL, tampers with `?state=`, or has an expired `.pkce` cookie, `exchangeCode(code, state)` must reject and delete any leftover `.pkce` cookie before throwing.
3. **Malformed or tampered `.pkce` cookie JSON:** If the `${cookieName}.pkce` cookie value is invalid JSON or missing required string fields (`state`, `codeVerifier`, `redirectUri`), `exchangeCode` must fail safely instead of crashing with an unhandled syntax error.
4. **Refresh token rotation when `refresh_token` is omitted in Keycloak response:** If a refresh response returns a new `access_token` without rotating `refresh_token`, the existing `refresh_token` must be preserved rather than overwritten with `undefined`.
5. **Backchannel logout when Keycloak server is unreachable:** `signOut()` must always delete local cookies (`.access`, `.refresh`, `.id`, `.pkce`) in a `finally` block even if `POST /protocol/openid-connect/logout` fails with a network or 5xx error.

---

### Task 1: Standalone Keycloak Docker Stack (`d:\Dev_Projects\keycloak-idp`)

**Files:**
- Create: `d:/Dev_Projects/keycloak-idp/docker-compose.yml`
- Create: `d:/Dev_Projects/keycloak-idp/.env.example`
- Create: `d:/Dev_Projects/keycloak-idp/.env`
- Create: `d:/Dev_Projects/keycloak-idp/realms/studio-realm.json`
- Create: `d:/Dev_Projects/keycloak-idp/README.md`

**Interfaces:**
- Produces: Running Keycloak OIDC server at `http://localhost:8080/realms/studio` with client `studio-app` (`secret: "studio-dev-client-secret-at-least-32-chars"`), redirect URI `http://localhost:3001/auth/callback`, roles `admin`, `editor`, `customer`, and seeded users `admin@next-mono-base.local`, `editor@next-mono-base.local`, `customer@next-mono-base.local` (password `Password123!`).

- [ ] **Step 1: Create `.env.example`, `.env`, and `docker-compose.yml` in `d:\Dev_Projects\keycloak-idp`**

Configure `postgres:17-alpine` (`keycloak_pgdata` volume, healthcheck) and `quay.io/keycloak/keycloak:26.0` (`command: start-dev --import-realm`, port `127.0.0.1:8080:8080`, volume `./realms:/opt/keycloak/data/import:ro`, admin `admin`/`admin`).

- [ ] **Step 2: Create `d:\Dev_Projects\keycloak-idp\realms\studio-realm.json` and `README.md`**

Define realm `studio` with:
- `registrationAllowed: true`, `registrationEmailAsUsername: true`, `loginWithEmailAllowed: true`, `resetPasswordAllowed: true`
- Roles: `customer`, `editor`, `admin`; default realm role `customer`
- Confidential client `studio-app` (`secret: "studio-dev-client-secret-at-least-32-chars"`, `standardFlowEnabled: true`, `directAccessGrantsEnabled: false`, `redirectUris: ["http://localhost:3001/auth/callback"]`, `webOrigins: ["http://localhost:3001"]`, `attributes: { "pkce.code.challenge.method": "S256", "post.logout.redirect.uris": "http://localhost:3001/*" }`)
- Protocol mappers on `studio-app` for user realm roles (`roles` claim in ID & Access token) and user attributes (`timezone`, `week_start`, `adopted_on`)
- 3 seeded users (`admin@next-mono-base.local`, `editor@next-mono-base.local`, `customer@next-mono-base.local` with password `Password123!`).

- [ ] **Step 3: Boot the Docker stack and verify OIDC Discovery & JWKS endpoints**

Run: `docker compose -f d:\Dev_Projects\keycloak-idp\docker-compose.yml up -d`
Then poll `http://localhost:8080/realms/studio/.well-known/openid-configuration` until HTTP 200.
Expected: JSON with `"issuer": "http://localhost:8080/realms/studio"` and `"jwks_uri": "http://localhost:8080/realms/studio/protocol/openid-connect/certs"`.

---

### Task 2: Keycloak Config, Cookies, JWKS & OIDC Helpers (`packages/auth`)

**Files:**
- Modify: `packages/auth/package.json`
- Modify: `packages/auth/src/types.ts`
- Modify: `packages/auth/src/config.ts`
- Create: `packages/auth/src/keycloak/cookies.ts`
- Create: `packages/auth/src/keycloak/jwks.ts`
- Create: `packages/auth/src/keycloak/oidc.ts`
- Test: `packages/auth/src/__tests__/keycloak-jwks-oidc.test.ts`

**Interfaces:**
- Consumes: `parseRole`, `Role` from `packages/auth/src/permissions.ts`; `Calendar`, `Session` from `packages/auth/src/types.ts`
- Produces:
  - `packages/auth/src/types.ts`:
    - `export type OAuthProvider = "google" | "keycloak" | "keycloak-register"`
    - `oauth?: { start(provider: OAuthProvider, redirectTo: string): Promise<string>; exchangeCode(code: string, state?: string | null): Promise<void> }`
  - `packages/auth/src/config.ts`:
    - `AUTH_PROVIDER: "keycloak"` union member with `KEYCLOAK_ISSUER: string`, `KEYCLOAK_CLIENT_ID: string`, `KEYCLOAK_CLIENT_SECRET: string`
  - `packages/auth/src/keycloak/cookies.ts`:
    - `export type KeycloakCookieNames = { access: string; refresh: string; id: string; pkce: string }`
    - `export type PkcePayload = { state: string; codeVerifier: string; redirectUri: string }`
    - `export function getKeycloakCookieNames(baseName: string): KeycloakCookieNames`
    - `export function parsePkceCookie(raw: string | undefined): PkcePayload | null`
    - `export function tokenCookieOptions(maxAgeSeconds: number): { httpOnly: true; sameSite: "lax"; secure: boolean; path: "/"; maxAge: number }`
  - `packages/auth/src/keycloak/jwks.ts`:
    - `export type VerifiedKeycloakClaims = { userId: string; role: Role; name: string | null; email: string | null; calendar?: Calendar; exp?: number }`
    - `export function resolveKeycloakRole(claims: Record<string, unknown>): Role`
    - `export function verifyKeycloakJwt(token: string, issuer: string, jwks?: ReturnType<typeof createRemoteJWKSet>): Promise<VerifiedKeycloakClaims | null>`
  - `packages/auth/src/keycloak/oidc.ts`:
    - `export type KeycloakOidcConfig = { issuer: string; clientId: string; clientSecret: string }`
    - `export type KeycloakTokenResponse = { access_token: string; refresh_token?: string; id_token?: string; expires_in: number; refresh_expires_in?: number }`
    - `export function getKeycloakEndpoints(issuer: string): { auth: string; registrations: string; token: string; userinfo: string; logout: string; certs: string }`
    - `export function createPkceChallenge(): { state: string; codeVerifier: string; codeChallenge: string }`
    - `export function buildAuthorizationUrl(config: KeycloakOidcConfig, params: { mode: "login" | "register" | "google"; redirectUri: string; state: string; codeChallenge: string }): string`
    - `export function exchangeAuthorizationCode(config: KeycloakOidcConfig, params: { code: string; codeVerifier: string; redirectUri: string }): Promise<KeycloakTokenResponse>`
    - `export function refreshKeycloakTokens(config: KeycloakOidcConfig, refreshToken: string): Promise<KeycloakTokenResponse>`
    - `export function fetchKeycloakUserInfo(config: KeycloakOidcConfig, accessToken: string): Promise<Record<string, unknown> | null>`
    - `export function logoutKeycloakSession(config: KeycloakOidcConfig, refreshToken: string): Promise<void>`

- [ ] **Step 1: Install `jose` in `@workspace/auth`**

Run: `pnpm --filter @workspace/auth add jose`

- [ ] **Step 2: Write the failing unit tests in `packages/auth/src/__tests__/keycloak-jwks-oidc.test.ts`**

```ts
import { exportJWK, generateKeyPair, SignJWT } from "jose"
import { createLocalJWKSet } from "jose"
import { describe, expect, it } from "vitest"

import {
  getKeycloakCookieNames,
  parsePkceCookie,
} from "../keycloak/cookies"
import { resolveKeycloakRole, verifyKeycloakJwt } from "../keycloak/jwks"
import {
  buildAuthorizationUrl,
  createPkceChallenge,
  getKeycloakEndpoints,
} from "../keycloak/oidc"

describe("keycloak cookies & PKCE parsing", () => {
  it("derives split cookie names from the app cookie prefix", () => {
    expect(getKeycloakCookieNames("nmb-studio-auth")).toEqual({
      access: "nmb-studio-auth.access",
      refresh: "nmb-studio-auth.refresh",
      id: "nmb-studio-auth.id",
      pkce: "nmb-studio-auth.pkce",
    })
  })

  it("returns null for malformed or incomplete PKCE cookie payloads", () => {
    expect(parsePkceCookie(undefined)).toBeNull()
    expect(parsePkceCookie("not-json")).toBeNull()
    expect(parsePkceCookie(JSON.stringify({ state: "s" }))).toBeNull()
    expect(
      parsePkceCookie(
        JSON.stringify({
          state: "s1",
          codeVerifier: "v1",
          redirectUri: "http://localhost:3001/auth/callback",
        })
      )
    ).toEqual({
      state: "s1",
      codeVerifier: "v1",
      redirectUri: "http://localhost:3001/auth/callback",
    })
  })
})

describe("resolveKeycloakRole & verifyKeycloakJwt", () => {
  it("picks highest privilege when default realm roles coexist with admin/editor", () => {
    expect(
      resolveKeycloakRole({
        realm_access: { roles: ["default-roles-studio", "customer", "admin"] },
      })
    ).toBe("admin")
    expect(
      resolveKeycloakRole({
        roles: ["customer", "editor"],
      })
    ).toBe("editor")
    expect(resolveKeycloakRole({})).toBe("customer")
  })

  it("verifies a signed RS256 token and extracts claims and calendar", async () => {
    const { publicKey, privateKey } = await generateKeyPair("RS256")
    const jwk = await exportJWK(publicKey)
    jwk.kid = "k1"
    jwk.alg = "RS256"
    jwk.use = "sig"
    const jwks = createLocalJWKSet({ keys: [jwk] })
    const issuer = "http://localhost:8080/realms/studio"

    const token = await new SignJWT({
      email: "admin@next-mono-base.local",
      name: "Admin User",
      realm_access: { roles: ["customer", "admin"] },
      timezone: "Asia/Ho_Chi_Minh",
      week_start: 1,
      adopted_on: "2026-01-01",
    })
      .setProtectedHeader({ alg: "RS256", kid: "k1" })
      .setSubject("user-123")
      .setIssuer(issuer)
      .setIssuedAt()
      .setExpirationTime("5m")
      .sign(privateKey)

    const verified = await verifyKeycloakJwt(token, issuer, jwks)
    expect(verified).toMatchObject({
      userId: "user-123",
      role: "admin",
      name: "Admin User",
      email: "admin@next-mono-base.local",
      calendar: {
        timezone: "Asia/Ho_Chi_Minh",
        weekStart: 1,
        adoptedOn: "2026-01-01",
      },
    })
  })
})

describe("OIDC URL builder", () => {
  it("builds login, registration, and google idp hint URLs with S256 PKCE", () => {
    const pkce = createPkceChallenge()
    const cfg = {
      issuer: "http://localhost:8080/realms/studio",
      clientId: "studio-app",
      clientSecret: "secret",
    }
    const loginUrl = new URL(
      buildAuthorizationUrl(cfg, {
        mode: "login",
        redirectUri: "http://localhost:3001/auth/callback",
        state: pkce.state,
        codeChallenge: pkce.codeChallenge,
      })
    )
    expect(loginUrl.pathname).toBe(
      "/realms/studio/protocol/openid-connect/auth"
    )
    expect(loginUrl.searchParams.get("code_challenge_method")).toBe("S256")

    const regUrl = new URL(
      buildAuthorizationUrl(cfg, {
        mode: "register",
        redirectUri: "http://localhost:3001/auth/callback",
        state: pkce.state,
        codeChallenge: pkce.codeChallenge,
      })
    )
    expect(regUrl.pathname).toBe(
      "/realms/studio/protocol/openid-connect/registrations"
    )

    expect(getKeycloakEndpoints(cfg.issuer).certs).toBe(
      "http://localhost:8080/realms/studio/protocol/openid-connect/certs"
    )
  })
})
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pnpm --filter @workspace/auth test`
Expected: FAIL with module not found (`../keycloak/cookies`, `../keycloak/jwks`, `../keycloak/oidc`).

- [ ] **Step 4: Update `packages/auth/src/types.ts`, `packages/auth/src/config.ts`, and implement `cookies.ts`, `jwks.ts`, and `oidc.ts`**

Implement the exact interfaces listed above. In `resolveKeycloakRole`, collect strings from `claims.role`, `claims.roles`, and `claims.realm_access.roles`, returning `"admin"` if present, else `"editor"` if present, else `parseRole(...)`.

- [ ] **Step 5: Run tests and typecheck in `@workspace/auth`**

Run: `pnpm --filter @workspace/auth test && pnpm --filter @workspace/auth typecheck`
Expected: PASS.

---

### Task 3: Keycloak Server Provider & Proxy Refresh (`packages/auth`)

**Files:**
- Create: `packages/auth/src/keycloak/server.ts`
- Create: `packages/auth/src/keycloak/proxy.ts`
- Modify: `packages/auth/src/server.ts`
- Modify: `packages/auth/src/proxy.ts`
- Test: `packages/auth/src/__tests__/keycloak-provider.test.ts`

**Interfaces:**
- Consumes: Task 2 modules (`cookies.ts`, `jwks.ts`, `oidc.ts`, `config.ts`, `types.ts`)
- Produces:
  - `packages/auth/src/keycloak/server.ts`: `export function createKeycloakProvider(options: AuthOptions): AuthProvider`
  - `packages/auth/src/keycloak/proxy.ts`: `export async function updateSession(request: NextRequest, options: AuthOptions): Promise<ProxyAuthResult>`

- [ ] **Step 1: Write the failing tests in `packages/auth/src/__tests__/keycloak-provider.test.ts`**

```ts
import { exportJWK, generateKeyPair, SignJWT, createLocalJWKSet } from "jose"
import { NextRequest } from "next/server"
import { beforeEach, describe, expect, it, vi } from "vitest"

const cookieJar = vi.hoisted(() => new Map<string, string>())

vi.mock("next/cache", () => ({
  io: async () => {},
}))

vi.mock("next/headers", () => ({
  cookies: async () => ({
    get: (name: string) => {
      const val = cookieJar.get(name)
      return val !== undefined ? { name, value: val } : undefined
    },
    set: (name: string, value: string) => {
      cookieJar.set(name, value)
    },
    delete: (name: string) => {
      cookieJar.delete(name)
    },
  }),
}))

describe("Keycloak AuthProvider & Proxy", () => {
  beforeEach(() => {
    cookieJar.clear()
    vi.restoreAllMocks()
  })

  it("rejects exchangeCode when state mismatches and cleans up pkce cookie", async () => {
    const { createKeycloakProvider } = await import("../keycloak/server")
    cookieJar.set(
      "nmb-studio-auth.pkce",
      JSON.stringify({
        state: "expected-state",
        codeVerifier: "verifier-1",
        redirectUri: "http://localhost:3001/auth/callback",
      })
    )
    const provider = createKeycloakProvider({ cookieName: "nmb-studio-auth" })
    await expect(
      provider.oauth!.exchangeCode("code-123", "wrong-state")
    ).rejects.toThrow(/state/i)
    expect(cookieJar.has("nmb-studio-auth.pkce")).toBe(false)
  })

  it("always clears local cookies on signOut even when Keycloak logout endpoint fails", async () => {
    const { createKeycloakProvider } = await import("../keycloak/server")
    cookieJar.set("nmb-studio-auth.access", "acc")
    cookieJar.set("nmb-studio-auth.refresh", "ref")
    cookieJar.set("nmb-studio-auth.id", "id")
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("ECONNREFUSED"))

    const provider = createKeycloakProvider({ cookieName: "nmb-studio-auth" })
    await provider.signOut()

    expect(cookieJar.has("nmb-studio-auth.access")).toBe(false)
    expect(cookieJar.has("nmb-studio-auth.refresh")).toBe(false)
    expect(cookieJar.has("nmb-studio-auth.id")).toBe(false)
  })

  it("refreshes expiring access token in proxy and preserves refresh_token if not rotated", async () => {
    const { publicKey, privateKey } = await generateKeyPair("RS256")
    const jwk = await exportJWK(publicKey)
    jwk.kid = "k1"
    jwk.alg = "RS256"
    const jwksModule = await import("../keycloak/jwks")
    vi.spyOn(jwksModule, "getIssuerJwks").mockReturnValue(
      createLocalJWKSet({ keys: [jwk] })
    )

    const issuer = "http://localhost:8080/realms/studio"
    const freshToken = await new SignJWT({
      email: "editor@next-mono-base.local",
      realm_access: { roles: ["editor"] },
    })
      .setProtectedHeader({ alg: "RS256", kid: "k1" })
      .setSubject("u-editor")
      .setIssuer(issuer)
      .setExpirationTime("5m")
      .sign(privateKey)

    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: freshToken,
          expires_in: 300,
        }),
        { status: 200, headers: { "content-type": "application/json" } }
      )
    )

    const { updateSession } = await import("../keycloak/proxy")
    const req = new NextRequest("http://localhost:3001/dashboard")
    req.cookies.set("nmb-studio-auth.refresh", "existing-refresh-token")

    const result = await updateSession(req, { cookieName: "nmb-studio-auth" })
    expect(result.isAuthenticated).toBe(true)
    expect(result.role).toBe("editor")
    expect(result.response.cookies.get("nmb-studio-auth.access")?.value).toBe(
      freshToken
    )
    expect(result.response.cookies.get("nmb-studio-auth.refresh")?.value).toBe(
      "existing-refresh-token"
    )
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pnpm --filter @workspace/auth test`
Expected: FAIL with module not found (`../keycloak/server`, `../keycloak/proxy`).

- [ ] **Step 3: Implement `packages/auth/src/keycloak/server.ts`, `packages/auth/src/keycloak/proxy.ts`, and wire `packages/auth/src/{server,proxy}.ts`**

In `jwks.ts`, export `getIssuerJwks(issuer: string)` so `verifyKeycloakJwt` uses it by default and tests can stub it cleanly.
In `server.ts`, implement `createKeycloakProvider(options)` with `getSession`, `verifySessionFresh`, `refreshSession`, `signIn`, `signUp`, `signOut` (using `try ... finally` to always delete cookies), `isExpectedError`, and `oauth` (`start`, `exchangeCode`).
In `proxy.ts`, implement `updateSession(request, options)` with short-circuit when no cookies exist, fast path when `.access` has `exp > now + 60`, and refresh rotation via `refreshKeycloakTokens` when expiring or missing `.access` (preserving existing `refresh_token` if the token endpoint response omits `refresh_token`).
Update `packages/auth/src/server.ts` and `packages/auth/src/proxy.ts` to branch on `authConfig.AUTH_PROVIDER === "keycloak"`.

- [ ] **Step 4: Run tests, lint, and typecheck in `@workspace/auth`**

Run: `pnpm --filter @workspace/auth test && pnpm --filter @workspace/auth lint && pnpm --filter @workspace/auth typecheck`
Expected: PASS.

---

### Task 4: Studio App Integration, Auth UI, Callback, CSP & Docs (`apps/studio` & `docs/`)

**Files:**
- Modify: `turbo.json`
- Modify: `apps/studio/.env.example`
- Modify: `apps/studio/next.config.ts`
- Modify: `apps/studio/app/auth/callback/route.ts`
- Modify: `apps/studio/lib/auth.ts`
- Modify: `apps/studio/features/auth/actions.ts`
- Modify: `apps/studio/app/(auth)/sign-in/page.tsx`
- Modify: `apps/studio/app/(auth)/sign-up/page.tsx`
- Modify: `docs/authentication.md`
- Modify: `docs/providers.md`

**Interfaces:**
- Consumes: `@workspace/auth/config`, `@workspace/auth/server`, `@workspace/auth/proxy`, `@workspace/auth/types`
- Produces:
  - `apps/studio/lib/auth.ts`: `export function isKeycloakProvider(): boolean`
  - `apps/studio/features/auth/actions.ts`: `export async function signInWithKeycloakAction(): Promise<void>`, `export async function signUpWithKeycloakAction(): Promise<void>`

- [ ] **Step 1: Update `turbo.json`, `apps/studio/.env.example`, and `apps/studio/next.config.ts`**

Add `KEYCLOAK_ISSUER`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_CLIENT_SECRET` to `turbo.json` `tasks.build.env` and document Stack 3 (`AUTH_PROVIDER=keycloak`) in `apps/studio/.env.example`.
In `apps/studio/next.config.ts`, when `process.env.AUTH_PROVIDER === "keycloak"` and `process.env.KEYCLOAK_ISSUER` is set, push `new URL(process.env.KEYCLOAK_ISSUER).origin` to `formActions` in `contentSecurityPolicy()`.

- [ ] **Step 2: Update `apps/studio/app/auth/callback/route.ts`, `apps/studio/lib/auth.ts`, `apps/studio/features/auth/actions.ts`, and auth pages**

In `apps/studio/app/auth/callback/route.ts`: pass `searchParams.get("state")` to `await provider.oauth.exchangeCode(code, state)`.
In `apps/studio/lib/auth.ts`: export `isKeycloakProvider(): boolean` returning `authConfig.AUTH_PROVIDER === "keycloak"`.
In `apps/studio/features/auth/actions.ts`: add `signInWithKeycloakAction` (`provider.oauth?.start("keycloak", callbackUrl)`) and `signUpWithKeycloakAction` (`provider.oauth?.start("keycloak-register", callbackUrl)`).
In `apps/studio/app/(auth)/sign-in/page.tsx` and `sign-up/page.tsx`: when `isKeycloakProvider()` is true, render `<OAuthButton action={signInWithKeycloakAction}>Continue with Keycloak</OAuthButton>` (on sign-in) and `<OAuthButton action={signUpWithKeycloakAction}>Create account with Keycloak</OAuthButton>` (on sign-up); otherwise render `<SignInForm>` / `<SignUpForm>` unchanged.

- [ ] **Step 3: Update `docs/authentication.md` and `docs/providers.md`**

Document `keycloak` as the 3rd provider in the overview tables, architecture section, and running instructions (`d:\Dev_Projects\keycloak-idp`).

- [ ] **Step 4: Run full monorepo verification (`pnpm check`, `pnpm test`, `pnpm build`)**

Run: `pnpm check && pnpm test && pnpm build`
Expected: All workspace packages and apps pass lint, typecheck, format check, unit tests, and production build.
