import type { Permission } from "@workspace/auth/permissions"

import {
  DASHBOARD_PATH,
  ORG_PATH,
  ORGANIZATIONS_PATH,
  PROJECT_PATH,
} from "@/config/routes"

/**
 * Semantic icon names, resolved to Tabler icons in `components/layout/nav-icons.tsx`. Names (not
 * components) because `entries` cross from a Server Component to the client `NavTree`.
 */
export type NavIconName =
  "overview" | "organizations" | "projects" | "database" | "settings"

export type NavLink = {
  title: string
  /** May hold `:param` placeholders (see `NavScope.param`), filled from the URL. */
  href: string
  icon: NavIconName
  permission: Permission
  /** Short mono text on the right, e.g. "due". Set at render time, not in the config. */
  badge?: string
  /**
   * Per-link prefetching (`<Link prefetch>`) for pages that read `searchParams`: URL data is not
   * in the shared App Shell, so without it their data waits for the click. Costs one server call per link.
   */
  prefetch?: true
}
/** A collapsible group inside a section; the tree stays at most two levels deep. */
export type NavGroup = { title: string; items: NavLink[] }
export type NavEntry = NavLink | NavGroup
/** One labelled block of the sidebar. Add sections freely; empty ones are hidden. */
export type NavSection = { label: string; entries: NavEntry[] }

/**
 * One sidebar menu, chosen by the URL like Supabase's Studio. A scope with a `prefix` owns every
 * path under `<prefix>/<param value>`; the scope without one is the fallback. Plain data, so a
 * Server Component can filter it and hand it to the client.
 */
export type NavScope = {
  id: string
  prefix?: string
  /** Name of the URL segment after `prefix`, used as `:param` in hrefs. */
  param?: string
  sections: NavSection[]
}

/** `permission` only hides links; each page still calls `requirePermission`. */
export const NAV_SCOPES: NavScope[] = [
  {
    id: "global",
    sections: [
      {
        label: "Workspace",
        entries: [
          {
            title: "Overview",
            href: DASHBOARD_PATH,
            icon: "overview",
            permission: "account:view",
          },
          {
            title: "Organizations",
            href: ORGANIZATIONS_PATH,
            icon: "organizations",
            permission: "account:view",
          },
        ],
      },
    ],
  },
  {
    id: "organization",
    prefix: ORG_PATH,
    param: "orgSlug",
    sections: [
      {
        label: "Organization",
        entries: [
          {
            title: "Overview",
            href: `${ORG_PATH}/:orgSlug`,
            icon: "overview",
            permission: "account:view",
          },
          {
            title: "Projects",
            href: `${ORG_PATH}/:orgSlug/projects`,
            icon: "projects",
            permission: "account:view",
          },
          {
            title: "Settings",
            href: `${ORG_PATH}/:orgSlug/settings`,
            icon: "settings",
            permission: "account:view",
          },
        ],
      },
    ],
  },
  {
    id: "project",
    prefix: PROJECT_PATH,
    param: "projectRef",
    sections: [
      {
        label: "Project",
        entries: [
          {
            title: "Overview",
            href: `${PROJECT_PATH}/:projectRef`,
            icon: "overview",
            permission: "account:view",
          },
          {
            title: "Database",
            href: `${PROJECT_PATH}/:projectRef/database`,
            icon: "database",
            permission: "account:view",
          },
          {
            title: "Settings",
            href: `${PROJECT_PATH}/:projectRef/settings`,
            icon: "settings",
            permission: "account:view",
          },
        ],
      },
    ],
  },
]

export type ResolvedScope = {
  scope: NavScope
  /** URL values by `param` name, e.g. `{ orgSlug: "acme" }`. */
  params: Record<string, string>
}

/** The scope a pathname belongs to (the fallback when no prefix matches) and its URL params. */
export function resolveScope(
  scopes: NavScope[],
  pathname: string
): ResolvedScope | undefined {
  for (const scope of scopes) {
    if (!scope.prefix || !scope.param) continue
    if (!pathname.startsWith(`${scope.prefix}/`)) continue
    const value = pathname.slice(scope.prefix.length + 1).split("/")[0]
    if (value) {
      return { scope, params: { [scope.param]: decodeURIComponent(value) } }
    }
  }
  const fallback = scopes.find((scope) => !scope.prefix)
  return fallback && { scope: fallback, params: {} }
}

/** Fills `:param` placeholders in an href. */
export function fillHref(href: string, params: Record<string, string>) {
  return href.replace(/:(\w+)/g, (match, name: string) =>
    name in params ? encodeURIComponent(params[name]!) : match
  )
}

/** Sections of the pathname's scope with real hrefs. */
export function sectionsFor(
  scopes: NavScope[],
  pathname: string
): NavSection[] {
  const resolved = resolveScope(scopes, pathname)
  if (!resolved) return []
  const { scope, params } = resolved
  const fill = (link: NavLink): NavLink => ({
    ...link,
    href: fillHref(link.href, params),
  })
  return scope.sections.map((section) => ({
    ...section,
    entries: section.entries.map((entry) =>
      "items" in entry
        ? { ...entry, items: entry.items.map(fill) }
        : fill(entry)
    ),
  }))
}

/**
 * Keeps the links `can` allows and drops groups or sections left empty. Takes a predicate so
 * this module stays free of auth code and is safe to import from client components.
 */
export function filterNav(
  scopes: NavScope[],
  can: (permission: Permission) => boolean
): NavScope[] {
  return scopes.map((scope) => ({
    ...scope,
    sections: scope.sections.flatMap((section) => {
      const entries = section.entries.flatMap<NavEntry>((entry) => {
        if (!("items" in entry)) return can(entry.permission) ? [entry] : []
        const items = entry.items.filter((item) => can(item.permission))
        return items.length ? [{ ...entry, items }] : []
      })
      return entries.length ? [{ ...section, entries }] : []
    }),
  }))
}

export function navLinks(sections: NavSection[]): NavLink[] {
  return sections.flatMap((section) =>
    section.entries.flatMap((entry) =>
      "items" in entry ? entry.items : [entry]
    )
  )
}

export type CrumbOption = { label: string; href: string }
export type Crumb = {
  label: string
  icon?: NavIconName
  href?: string
  /** Makes the crumb a menu that jumps to a sibling (another organization or project). */
  options?: CrumbOption[]
}

/** Names the breadcrumb shows for ids in the URL; the server loads them. */
export type Workspace = {
  orgs: { slug: string; name: string }[]
  projects: { ref: string; name: string; orgSlug: string }[]
}

/**
 * Breadcrumb from the URL. Global pages read like a path (`dashboard / organizations`). Scoped pages
 * start with menus: `Acme ▾ / overview` in an organization, `Acme ▾ / Web app ▾ / database` in a
 * project (its organization comes from the data). The last crumb is the page, named by the nav.
 */
export function breadcrumbTrail(
  pathname: string,
  scopes: NavScope[],
  workspace: Workspace
): Crumb[] {
  const resolved = resolveScope(scopes, pathname)
  if (!resolved) return []
  const { scope, params } = resolved
  const links = navLinks(sectionsFor(scopes, pathname))
  const page = links.find((link) => link.href === pathname)?.title
  const segments = pathname.split("/").filter(Boolean)

  if (!scope.prefix) {
    const crumbs: Crumb[] = segments.map((segment, index) => {
      const href = `/${segments.slice(0, index + 1).join("/")}`
      return {
        label: segment,
        href: links.some((link) => link.href === href) ? href : undefined,
      }
    })
    if (page && page.toLowerCase() !== segments.at(-1)) {
      crumbs.push({ label: page.toLowerCase() })
    }
    return crumbs
  }

  const project = workspace.projects.find((p) => p.ref === params.projectRef)
  const orgSlug = params.orgSlug ?? project?.orgSlug
  const crumbs: Crumb[] = []
  if (orgSlug) {
    crumbs.push({
      label: workspace.orgs.find((o) => o.slug === orgSlug)?.name ?? orgSlug,
      icon: "organizations",
      href: `${ORG_PATH}/${encodeURIComponent(orgSlug)}`,
      options: workspace.orgs.map((o) => ({
        label: o.name,
        href: `${ORG_PATH}/${encodeURIComponent(o.slug)}`,
      })),
    })
  }
  if (params.projectRef) {
    crumbs.push({
      label: project?.name ?? params.projectRef,
      icon: "projects",
      href: `${PROJECT_PATH}/${encodeURIComponent(params.projectRef)}`,
      options: workspace.projects
        .filter((p) => p.orgSlug === orgSlug)
        .map((p) => ({
          label: p.name,
          href: `${PROJECT_PATH}/${encodeURIComponent(p.ref)}`,
        })),
    })
  }
  crumbs.push({ label: (page ?? segments.at(-1) ?? "").toLowerCase() })
  return crumbs
}
