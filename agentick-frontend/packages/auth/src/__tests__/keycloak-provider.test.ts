import { NextRequest } from "next/server"
import { beforeEach, describe, expect, it, vi } from "vitest"

const cookieJar = vi.hoisted(() => new Map<string, string>())

vi.mock("server-only", () => ({}))

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

  it("rejects exchangeCode when state is mismatched or missing and cleans up pkce cookie", async () => {
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

    // Test missing/null state parameter
    cookieJar.set(
      "nmb-studio-auth.pkce",
      JSON.stringify({
        state: "expected-state",
        codeVerifier: "verifier-1",
        redirectUri: "http://localhost:3001/auth/callback",
      })
    )
    await expect(
      provider.oauth!.exchangeCode("code-123", null)
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

  it("short-circuits in updateSession when no tokens are present", async () => {
    const { updateSession } = await import("../keycloak/proxy")
    const req = new NextRequest("http://localhost:3001/dashboard")
    const result = await updateSession(req, { cookieName: "nmb-studio-auth" })
    expect(result.isAuthenticated).toBe(false)
    expect(result.role).toBeNull()
  })

  it("refreshes expiring access token in proxy and preserves refresh_token if not rotated", async () => {
    const jwksModule = await import("../keycloak/jwks")
    vi.spyOn(jwksModule, "verifyKeycloakJwt").mockResolvedValue({
      userId: "u-editor",
      role: "editor",
      name: "Editor User",
      email: "editor@next-mono-base.local",
    })

    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: "fresh-access-token",
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
      "fresh-access-token"
    )
    expect(result.response.cookies.get("nmb-studio-auth.refresh")?.value).toBe(
      "existing-refresh-token"
    )
  })
})
