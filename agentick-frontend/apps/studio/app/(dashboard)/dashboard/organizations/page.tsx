import type { Metadata } from "next"
import { Suspense } from "react"

import { PageHead } from "@/components/layout/page-head"
import { CreateOrgDialog } from "@/features/workspace/components/create-dialogs"
import { CardGridSkeleton } from "@/features/workspace/components/skeletons"
import {
  CardGrid,
  OrgCard,
} from "@/features/workspace/components/workspace-cards"
import { getWorkspace } from "@/features/workspace/queries"

export const metadata: Metadata = { title: "Organizations" }

async function OrgList() {
  const { orgs, projects } = await getWorkspace()
  return (
    <CardGrid>
      {orgs.map((org) => (
        <OrgCard
          key={org.slug}
          org={org}
          projects={projects.filter((p) => p.orgSlug === org.slug).length}
        />
      ))}
    </CardGrid>
  )
}

export default function OrganizationsPage() {
  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <PageHead label="Workspace" title="Organizations">
          Open an organization to switch the sidebar to its menu.
        </PageHead>
        <CreateOrgDialog />
      </div>
      <Suspense fallback={<CardGridSkeleton />}>
        <OrgList />
      </Suspense>
    </>
  )
}
