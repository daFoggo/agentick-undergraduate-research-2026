import { describe, expect, it } from "vitest"

import { cn } from "./utils.js"

describe("cn", () => {
  it("joins class names and drops falsy values", () => {
    expect(cn("a", false, "b")).toBe("a b")
  })
})
