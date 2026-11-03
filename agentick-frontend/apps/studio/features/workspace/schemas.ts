import { z } from "zod"

export const PLANS = ["Free", "Pro", "Team"] as const
export const REGIONS = [
  "ap-southeast-1",
  "us-east-1",
  "us-west-2",
  "eu-west-1",
] as const

const Slug = z
  .string()
  .min(3)
  .max(48)
  .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/)

const Name = z
  .string()
  .trim()
  .min(3, "Name must be at least 3 characters")
  .max(48, "Name must be at most 48 characters")

/** DTOs: what the UI reads (`server.ts` parses every response into these). */
export const OrgSchema = z.object({
  slug: Slug,
  name: z.string(),
  plan: z.enum(PLANS),
  members: z.number().int(),
})
export const ProjectSchema = z.object({
  ref: Slug,
  name: z.string(),
  orgSlug: Slug,
  status: z.enum(["active", "paused"]),
  region: z.enum(REGIONS),
  createdAt: z.string(),
})
export type Org = z.infer<typeof OrgSchema>
export type Project = z.infer<typeof ProjectSchema>

/** Form input. The slug / ref is derived from the name on the server, never trusted from the client. */
export const CreateOrgSchema = z.object({ name: Name })
export const CreateProjectSchema = z.object({
  name: Name,
  region: z.enum(REGIONS, "Pick a region"),
})
export type CreateOrgInput = z.infer<typeof CreateOrgSchema>
export type CreateProjectInput = z.infer<typeof CreateProjectSchema>

/** "Internal tools!" becomes "internal-tools". */
export function slugify(name: string): string {
  return name
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
}
