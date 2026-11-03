import "server-only"

import { cacheLife, cacheTag } from "next/cache"

import { requirePermission } from "@/lib/dal"

import { fetchOrgs, fetchProjects } from "./server"

/** One tag per user: creating an organization or project expires it (`updateTag` in actions). */
export const workspaceTag = (userId: string) => `workspace:${userId}`

/**
 * Everything the signed-in user can see, in one backend round trip pair. Per-user and token-bound,
 * so `"use cache: private"` (browser only, never stored on the server). The smaller reads below
 * derive from it: layouts, breadcrumbs and pages in one request share this single fill.
 */
export async function getWorkspace() {
  "use cache: private"
  cacheLife({ stale: 300, revalidate: 300, expire: 3600 })
  // Authorizes next to the data (layouts never do): every route that reads the workspace passes here.
  const { userId, accessToken } = await requirePermission("account:view")
  cacheTag(workspaceTag(userId))
  const [orgs, projects] = await Promise.all([
    fetchOrgs(accessToken),
    fetchProjects(accessToken),
  ])
  return { orgs, projects }
}

/** `undefined` when it does not exist: the caller decides (`notFound()` in a gate). */
export async function getOrg(slug: string) {
  return (await getWorkspace()).orgs.find((org) => org.slug === slug)
}

export async function getProject(ref: string) {
  return (await getWorkspace()).projects.find((project) => project.ref === ref)
}

export async function getProjectsOf(orgSlug: string) {
  return (await getWorkspace()).projects.filter(
    (project) => project.orgSlug === orgSlug
  )
}
