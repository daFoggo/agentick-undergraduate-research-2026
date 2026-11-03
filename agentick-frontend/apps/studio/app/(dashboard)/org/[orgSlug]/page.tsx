import type { Metadata } from "next"
import { Suspense } from "react"

import { PageHead } from "@/components/layout/page-head"
import { SummarySkeleton } from "@/features/workspace/components/skeletons"
import { Spec } from "@/features/workspace/components/spec"
import { getOrg, getProjectsOf } from "@/features/workspace/queries"

export const metadata: Metadata = { title: "Organization overview" }

async function OrgSummary({
  params,
}: {
  params: Promise<{ orgSlug: string }>
}) {
  const { orgSlug } = await params
  const org = await getOrg(orgSlug)
  if (!org) return null
  const projects = await getProjectsOf(orgSlug)
  return (
    <>
      <PageHead label="Organization" title={org.name}>
        Organization-wide summary.
      </PageHead>
      <Spec
        rows={[
          ["Slug", org.slug],
          ["Plan", org.plan],
          ["Members", String(org.members)],
          ["Projects", String(projects.length)],
          [
            "Active",
            String(projects.filter((p) => p.status === "active").length),
          ],
        ]}
      />
    </>
  )
}

export default function OrgOverviewPage({
  params,
}: {
  params: Promise<{ orgSlug: string }>
}) {
  return (
    <Suspense fallback={<SummarySkeleton />}>
      <OrgSummary params={params} />
    </Suspense>
  )
}
