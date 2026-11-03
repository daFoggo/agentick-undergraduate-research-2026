import { describe, expect, it } from "vitest"

import {
  hasPermission,
  isStaff,
  parseRole,
  permissionsOf,
} from "../permissions"

describe("parseRole", () => {
  it("accepts the three known roles", () => {
    expect(parseRole("customer")).toBe("customer")
    expect(parseRole("editor")).toBe("editor")
    expect(parseRole("admin")).toBe("admin")
  })

  it("falls back to customer for missing, unknown or differently-cased values", () => {
    for (const value of [
      undefined,
      null,
      "",
      "Admin",
      "member",
      "owner",
      1,
      {},
    ]) {
      expect(parseRole(value)).toBe("customer")
    }
  })
})

describe("isStaff", () => {
  it("is false for customers and true for editors and admins", () => {
    expect(isStaff("customer")).toBe(false)
    expect(isStaff("editor")).toBe(true)
    expect(isStaff("admin")).toBe(true)
  })
})

describe("hasPermission", () => {
  it("gives customers only their account", () => {
    expect(hasPermission("customer", "account:view")).toBe(true)
    expect(hasPermission("customer", "admin:access")).toBe(false)
  })

  it("keeps settings and staff management for admins", () => {
    expect(hasPermission("editor", "content:manage")).toBe(true)
    expect(hasPermission("editor", "records:manage")).toBe(true)
    expect(hasPermission("editor", "staff:manage")).toBe(false)
    expect(hasPermission("editor", "settings:manage")).toBe(false)
    expect(hasPermission("admin", "staff:manage")).toBe(true)
    expect(hasPermission("admin", "settings:manage")).toBe(true)
  })

  it("gives admins everything editors have", () => {
    for (const permission of permissionsOf("editor")) {
      expect(hasPermission("admin", permission)).toBe(true)
    }
  })
})
