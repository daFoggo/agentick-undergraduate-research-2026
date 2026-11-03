import { NextRequest } from "next/server"
import { describe, expect, it } from "vitest"

import { hasBetterAuthSession } from "../better-auth/session-cookie"

function request(cookie?: string, authorization?: string) {
  const headers = new Headers()
  if (cookie) headers.set("cookie", cookie)
  if (authorization) headers.set("authorization", authorization)
  return new NextRequest("http://localhost:3000/account", { headers })
}

describe("hasBetterAuthSession", () => {
  it("finds the app's own session cookie", () => {
    expect(
      hasBetterAuthSession(
        request("nmb-web-auth.session_token=a"),
        "nmb-web-auth"
      )
    ).toBe(true)
  })

  it("finds the secure variant used in production", () => {
    expect(
      hasBetterAuthSession(
        request("__Secure-nmb-web-auth.session_token=a"),
        "nmb-web-auth"
      )
    ).toBe(true)
  })

  it("ignores another app's cookie on the same host", () => {
    expect(
      hasBetterAuthSession(
        request("nmb-admin-auth.session_token=a"),
        "nmb-web-auth"
      )
    ).toBe(false)
    expect(
      hasBetterAuthSession(
        request("better-auth.session_token=a"),
        "nmb-web-auth"
      )
    ).toBe(false)
  })

  it("accepts a bearer header", () => {
    expect(
      hasBetterAuthSession(request(undefined, "Bearer t"), "nmb-web-auth")
    ).toBe(true)
  })

  it("is false without cookie or header", () => {
    expect(hasBetterAuthSession(request(), "nmb-web-auth")).toBe(false)
  })
})
