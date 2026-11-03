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
