import { SignJWT } from "jose"
import { describe, expect, it } from "vitest"

import { mapFastApiRole, verifyFastApiJwt } from "../fastapi-oauth/jwt"

const SECRET = "test-secret-at-least-32-characters-long"
const secretKey = new TextEncoder().encode(SECRET)

async function signToken(claims: Record<string, unknown>, expInSeconds = 3600) {
  return new SignJWT({ type: "access", ...claims })
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(String(claims.sub ?? "42"))
    .setExpirationTime(Math.floor(Date.now() / 1000) + expInSeconds)
    .sign(secretKey)
}

describe("mapFastApiRole", () => {
  it("maps the backend's admin role through", () => {
    expect(mapFastApiRole("admin")).toBe("admin")
  })

  it("maps member, and anything unrecognized, to the least-privileged role", () => {
    expect(mapFastApiRole("member")).toBe("customer")
    expect(mapFastApiRole(undefined)).toBe("customer")
    expect(mapFastApiRole("something-else")).toBe("customer")
  })
})

describe("verifyFastApiJwt", () => {
  it("returns claims for a validly signed access token", async () => {
    const token = await signToken({
      sub: "42",
      role: "admin",
      name: "Jane",
      email: "jane@example.com",
    })
    const claims = await verifyFastApiJwt(token, SECRET)
    expect(claims).toMatchObject({
      userId: "42",
      role: "admin",
      name: "Jane",
      email: "jane@example.com",
    })
  })

  it("rejects a token signed with a different secret", async () => {
    const token = await signToken({ sub: "42" })
    const claims = await verifyFastApiJwt(token, "a-different-secret-at-least-32-chars")
    expect(claims).toBeNull()
  })

  it("rejects an expired token", async () => {
    const token = await signToken({ sub: "42" }, -60)
    const claims = await verifyFastApiJwt(token, SECRET)
    expect(claims).toBeNull()
  })

  it("rejects a refresh token presented as an access token", async () => {
    const token = await new SignJWT({ type: "refresh" })
      .setProtectedHeader({ alg: "HS256" })
      .setSubject("42")
      .setExpirationTime(Math.floor(Date.now() / 1000) + 3600)
      .sign(secretKey)
    const claims = await verifyFastApiJwt(token, SECRET)
    expect(claims).toBeNull()
  })

  it("defaults role, name and email when the token carries none", async () => {
    const token = await signToken({ sub: "42" })
    const claims = await verifyFastApiJwt(token, SECRET)
    expect(claims).toMatchObject({ role: "customer", name: null, email: null })
  })
})
