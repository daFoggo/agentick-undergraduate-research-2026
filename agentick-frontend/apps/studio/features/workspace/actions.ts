"use server"

import { updateTag } from "next/cache"
import { redirect } from "next/navigation"

import { ORG_PATH, PROJECT_PATH } from "@/config/routes"
import { isExpectedDataError } from "@/lib/errors"
import { requirePermission } from "@/lib/dal"

import { workspaceTag } from "./queries"
import { CreateOrgSchema, CreateProjectSchema } from "./schemas"
import { insertOrg, insertProject } from "./server"

/** `values` echoes the fields back: React resets the form after an action finishes. */
export type CreateState = {
  error?: string
  values?: { name: string; region?: string }
}

/** Any signed-in user may create an organization (like Supabase); resources are then theirs to manage. */
export async function createOrgAction(
  _previous: CreateState,
  formData: FormData
): Promise<CreateState> {
  const session = await requirePermission("account:view")
  const values = { name: String(formData.get("name") ?? "") }
  const parsed = CreateOrgSchema.safeParse(values)
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message, values }
  }

  let slug: string
  try {
    slug = (await insertOrg(session.accessToken, parsed.data)).slug
  } catch (error) {
    if (isExpectedDataError(error)) return { error: error.message, values }
    throw error
  }
  updateTag(workspaceTag(session.userId))
  redirect(`${ORG_PATH}/${slug}`)
}

/** Bound to the organization: `createProjectAction.bind(null, orgSlug)`. */
export async function createProjectAction(
  orgSlug: string,
  _previous: CreateState,
  formData: FormData
): Promise<CreateState> {
  const session = await requirePermission("account:view")
  const values = {
    name: String(formData.get("name") ?? ""),
    region: String(formData.get("region") ?? ""),
  }
  const parsed = CreateProjectSchema.safeParse(values)
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message, values }
  }

  let ref: string
  try {
    ref = (await insertProject(session.accessToken, orgSlug, parsed.data)).ref
  } catch (error) {
    if (isExpectedDataError(error)) return { error: error.message, values }
    throw error
  }
  updateTag(workspaceTag(session.userId))
  redirect(`${PROJECT_PATH}/${ref}`)
}
