import { DashboardBreadcrumb } from "@/components/layout/header/dashboard-breadcrumb"
import { NAV_SCOPES } from "@/config/navigation"
import { getWorkspace } from "@/features/workspace/queries"
import { requirePermission } from "@/lib/dal"

/** Breadcrumb for the dashboard; sends the client only the names for the ids in the URL. */
export async function DashboardCrumbs() {
  await requirePermission("account:view")
  const { orgs, projects } = await getWorkspace()
  return (
    <DashboardBreadcrumb
      scopes={NAV_SCOPES}
      workspace={{
        orgs: orgs.map(({ slug, name }) => ({ slug, name })),
        projects: projects.map(({ ref, name, orgSlug }) => ({
          ref,
          name,
          orgSlug,
        })),
      }}
    />
  )
}
