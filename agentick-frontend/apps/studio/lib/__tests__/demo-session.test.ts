import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  createDemoToken,
  DEMO_TTL_SECONDS,
  demoAuthSecret,
  readDemoSession,
  verifyDemoToken,
} from "../demo-session"

const SECRET = "s".repeat(32)
const enc = new TextEncoder()

function b64url(bytes: Uint8Array | string) {
  const data = typeof bytes === "string" ? enc.encode(bytes) : bytes
  let bin = ""
  for (const b of data) bin += String.fromCharCode(b)
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")
}

async function signed(claims: unknown, secret = SECRET) {
  const payload = b64url(JSON.stringify(claims))
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  )
  const mac = await crypto.subtle.sign("HMAC", key, enc.encode(payload))
  return `${payload}.${b64url(new Uint8Array(mac))}`
}

describe("demo session", () => {
  beforeEach(() => {
    vi.stubEnv("DEMO_AUTH", "true")
    vi.stubEnv("DEMO_AUTH_SECRET", SECRET)
  })
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.useRealTimers()
  })

  it("round-trips a valid token", async () => {
    const claims = await verifyDemoToken(await createDemoToken(SECRET), SECRET)
    expect(claims).toMatchObject({ sub: "demo-student", role: "customer" })
  })

  it("rejects a tampered payload", async () => {
    const [, mac] = (await createDemoToken(SECRET)).split(".") as [
      string,
      string,
    ]
    const forged = b64url(
      JSON.stringify({ sub: "x", role: "customer", exp: 9999999999 })
    )
    expect(await verifyDemoToken(`${forged}.${mac}`, SECRET)).toBeNull()
  })

  it("rejects a tampered MAC", async () => {
    const [payload, mac] = (await createDemoToken(SECRET)).split(".") as [
      string,
      string,
    ]
    const flipped = (mac[0] === "A" ? "B" : "A") + mac.slice(1)
    expect(await verifyDemoToken(`${payload}.${flipped}`, SECRET)).toBeNull()
  })

  it("rejects an expired token", async () => {
    vi.useFakeTimers({ toFake: ["Date"] })
    const token = await createDemoToken(SECRET)
    vi.setSystemTime(Date.now() + (DEMO_TTL_SECONDS + 1) * 1000)
    expect(await verifyDemoToken(token, SECRET)).toBeNull()
  })

  it("rejects a token signed with another secret", async () => {
    const token = await createDemoToken("o".repeat(32))
    expect(await verifyDemoToken(token, SECRET)).toBeNull()
  })

  it("rejects a correctly signed token with the wrong role", async () => {
    const exp = Math.floor(Date.now() / 1000) + 60
    expect(
      await verifyDemoToken(
        await signed({ sub: "a", role: "admin", exp }),
        SECRET
      )
    ).toBeNull()
  })

  it("is off unless DEMO_AUTH is true with a 32+ char secret", async () => {
    const token = await createDemoToken(SECRET)
    vi.stubEnv("DEMO_AUTH", "false")
    expect(demoAuthSecret()).toBeNull()
    expect(await readDemoSession(token)).toBeNull()
    vi.stubEnv("DEMO_AUTH", "")
    expect(demoAuthSecret()).toBeNull()
    vi.stubEnv("DEMO_AUTH", "true")
    vi.stubEnv("DEMO_AUTH_SECRET", "short")
    expect(demoAuthSecret()).toBeNull()
    expect(await readDemoSession(token)).toBeNull()
  })

  it("never throws on garbage input", async () => {
    const garbage = [
      undefined,
      "",
      ".",
      "a.b.c",
      "%%%.%%%",
      "!!!!.@@@@",
      `${b64url("not json")}.${b64url("zz")}`,
      await signed("a string"),
      await signed(null),
      await signed({ sub: 1, role: "customer", exp: "x" }),
    ]
    for (const token of garbage) {
      await expect(verifyDemoToken(token, SECRET)).resolves.toBeNull()
    }
  })
})
