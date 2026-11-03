import "server-only"

import { ApiError } from "@/lib/errors"

import {
  OrgSchema,
  ProjectSchema,
  slugify,
  type CreateOrgInput,
  type CreateProjectInput,
  type Org,
  type Project,
} from "./schemas"

/**
 * The only place that talks to the backend. It is a MOCK: an in-memory store seeded with demo
 * data, so every query and action above it is real. To go live, replace the bodies with
 * `apiFetch` (FastAPI) or `createDataClient` + `unwrap` (Supabase); keep the signatures, the Zod
 * parsing and the errors (`ApiError` 4xx = expected, returned to the form as a message).
 * The `_token` argument is the user's access token, unused by the mock.
 */
type Db = { orgs: Org[]; projects: Project[] }

const SEED: Db = {
  orgs: [
    { slug: "acme", name: "Acme Inc", plan: "Pro", members: 8 },
    { slug: "globex", name: "Globex", plan: "Free", members: 3 },
    { slug: "initech", name: "Initech", plan: "Team", members: 14 },
  ],
  projects: [
    {
      ref: "web-app",
      name: "Web app",
      orgSlug: "acme",
      status: "active",
      region: "ap-southeast-1",
      createdAt: "2026-01-12",
    },
    {
      ref: "api",
      name: "API",
      orgSlug: "acme",
      status: "active",
      region: "ap-southeast-1",
      createdAt: "2026-02-03",
    },
    {
      ref: "analytics",
      name: "Analytics",
      orgSlug: "acme",
      status: "paused",
      region: "us-east-1",
      createdAt: "2026-04-21",
    },
    {
      ref: "mobile",
      name: "Mobile",
      orgSlug: "globex",
      status: "active",
      region: "eu-west-1",
      createdAt: "2026-03-08",
    },
    {
      ref: "landing",
      name: "Landing",
      orgSlug: "globex",
      status: "paused",
      region: "eu-west-1",
      createdAt: "2026-05-30",
    },
    {
      ref: "billing",
      name: "Billing",
      orgSlug: "initech",
      status: "active",
      region: "us-east-1",
      createdAt: "2025-11-17",
    },
    {
      ref: "internal-tools",
      name: "Internal tools",
      orgSlug: "initech",
      status: "active",
      region: "us-east-1",
      createdAt: "2025-12-02",
    },
    {
      ref: "data-warehouse",
      name: "Data warehouse",
      orgSlug: "initech",
      status: "active",
      region: "us-west-2",
      createdAt: "2026-06-14",
    },
  ],
}

// On globalThis so dev hot reloads keep what was created.
const globalForDb = globalThis as { __workspaceMock?: Db }
const db = (globalForDb.__workspaceMock ??= structuredClone(SEED))

export async function fetchOrgs(_token: string): Promise<Org[]> {
  return OrgSchema.array().parse(db.orgs)
}

export async function fetchProjects(_token: string): Promise<Project[]> {
  return ProjectSchema.array().parse(db.projects)
}

export async function insertOrg(
  _token: string,
  input: CreateOrgInput
): Promise<Org> {
  const slug = slugify(input.name)
  if (slug.length < 3)
    throw new ApiError(422, "Use letters or numbers in the name")
  if (db.orgs.some((org) => org.slug === slug)) {
    throw new ApiError(409, "An organization with this name already exists")
  }
  const org = OrgSchema.parse({
    slug,
    name: input.name,
    plan: "Free",
    members: 1,
  })
  db.orgs.push(org)
  return org
}

export async function insertProject(
  _token: string,
  orgSlug: string,
  input: CreateProjectInput
): Promise<Project> {
  if (!db.orgs.some((org) => org.slug === orgSlug)) {
    throw new ApiError(404, "Organization not found")
  }
  const ref = slugify(input.name)
  if (ref.length < 3)
    throw new ApiError(422, "Use letters or numbers in the name")
  if (db.projects.some((project) => project.ref === ref)) {
    throw new ApiError(409, "A project with this name already exists")
  }
  const project = ProjectSchema.parse({
    ref,
    name: input.name,
    orgSlug,
    status: "active",
    region: input.region,
    createdAt: new Date().toISOString().slice(0, 10),
  })
  db.projects.push(project)
  return project
}
