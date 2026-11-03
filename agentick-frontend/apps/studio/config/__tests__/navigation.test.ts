import { describe, expect, it } from "vitest"

import {
  breadcrumbTrail,
  filterNav,
  fillHref,
  NAV_SCOPES,
  resolveScope,
  sectionsFor,
  type Workspace,
} from "../navigation"

const workspace: Workspace = {
  orgs: [
    { slug: "acme", name: "Acme Inc" },
    { slug: "globex", name: "Globex" },
  ],
  projects: [
    { ref: "web-app", name: "Web app", orgSlug: "acme" },
    { ref: "api", name: "API", orgSlug: "acme" },
    { ref: "mobile", name: "Mobile", orgSlug: "globex" },
  ],
}

describe("resolveScope", () => {
  it("picks the scope by URL prefix and reads its param", () => {
    expect(resolveScope(NAV_SCOPES, "/org/acme/settings")).toMatchObject({
      scope: { id: "organization" },
      params: { orgSlug: "acme" },
    })
    expect(resolveScope(NAV_SCOPES, "/project/web-app")).toMatchObject({
      scope: { id: "project" },
      params: { projectRef: "web-app" },
    })
  })

  it("falls back to the global scope", () => {
    expect(resolveScope(NAV_SCOPES, "/dashboard")?.scope.id).toBe("global")
    expect(resolveScope(NAV_SCOPES, "/org")?.scope.id).toBe("global")
  })
})

describe("sectionsFor / fillHref", () => {
  it("fills :params in hrefs and encodes the values", () => {
    expect(fillHref("/org/:orgSlug/x", { orgSlug: "a b" })).toBe("/org/a%20b/x")
    const hrefs = sectionsFor(NAV_SCOPES, "/project/web-app")
      .flatMap((s) => s.entries)
      .map((e) => ("href" in e ? e.href : ""))
    expect(hrefs).toContain("/project/web-app/database")
    expect(hrefs.join()).not.toContain(":")
  })
})

describe("filterNav", () => {
  it("drops links the role cannot open, keeping the scope list intact", () => {
    const none = filterNav(NAV_SCOPES, () => false)
    expect(none).toHaveLength(NAV_SCOPES.length)
    expect(none.every((scope) => scope.sections.length === 0)).toBe(true)
  })
})

describe("breadcrumbTrail", () => {
  it("reads like a path on global pages", () => {
    const crumbs = breadcrumbTrail(
      "/dashboard/organizations",
      NAV_SCOPES,
      workspace
    )
    expect(crumbs.map((c) => c.label)).toEqual(["dashboard", "organizations"])
  })

  it("starts with an organization menu in an organization", () => {
    const crumbs = breadcrumbTrail("/org/acme/projects", NAV_SCOPES, workspace)
    expect(crumbs.map((c) => c.label)).toEqual(["Acme Inc", "projects"])
    expect(crumbs[0]?.options?.map((o) => o.href)).toEqual([
      "/org/acme",
      "/org/globex",
    ])
  })

  it("adds the organization of a project and lists only its siblings", () => {
    const crumbs = breadcrumbTrail(
      "/project/web-app/database",
      NAV_SCOPES,
      workspace
    )
    expect(crumbs.map((c) => c.label)).toEqual([
      "Acme Inc",
      "Web app",
      "database",
    ])
    expect(crumbs[1]?.options?.map((o) => o.label)).toEqual(["Web app", "API"])
  })

  it("shows the id when the name is unknown", () => {
    const crumbs = breadcrumbTrail("/org/ghost", NAV_SCOPES, workspace)
    expect(crumbs[0]?.label).toBe("ghost")
  })
})
