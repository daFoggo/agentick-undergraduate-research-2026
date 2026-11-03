import { describe, expect, it, vi } from "vitest"

vi.mock("server-only", () => ({}))

import { ApiError } from "@/lib/errors"

import { CreateProjectSchema, slugify } from "../schemas"
import { fetchOrgs, fetchProjects, insertOrg, insertProject } from "../server"

describe("slugify", () => {
  it("lowercases, strips accents and joins with dashes", () => {
    expect(slugify("Internal tools!")).toBe("internal-tools")
    expect(slugify("  Công ty Việt  ")).toBe("cong-ty-viet")
  })
})

describe("CreateProjectSchema", () => {
  it("rejects short names and unknown regions", () => {
    expect(
      CreateProjectSchema.safeParse({ name: "ab", region: "us-east-1" }).success
    ).toBe(false)
    expect(
      CreateProjectSchema.safeParse({ name: "Web", region: "mars-1" }).success
    ).toBe(false)
    expect(
      CreateProjectSchema.safeParse({ name: "Web", region: "us-east-1" })
        .success
    ).toBe(true)
  })
})

describe("mock backend", () => {
  it("returns Zod-parsed seed data", async () => {
    expect((await fetchOrgs("t")).map((o) => o.slug)).toContain("acme")
    expect((await fetchProjects("t")).length).toBeGreaterThan(0)
  })

  it("creates an organization and rejects a duplicate with an expected 409", async () => {
    const org = await insertOrg("t", { name: "Umbrella Corp" })
    expect(org).toMatchObject({
      slug: "umbrella-corp",
      plan: "Free",
      members: 1,
    })
    await expect(
      insertOrg("t", { name: "Umbrella Corp" })
    ).rejects.toMatchObject({
      status: 409,
    })
  })

  it("creates a project in an existing organization only", async () => {
    const project = await insertProject("t", "acme", {
      name: "Docs site",
      region: "eu-west-1",
    })
    expect(project).toMatchObject({
      ref: "docs-site",
      orgSlug: "acme",
      status: "active",
    })
    const error = await insertProject("t", "ghost", {
      name: "Nope",
      region: "eu-west-1",
    }).catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(404)
  })
})
