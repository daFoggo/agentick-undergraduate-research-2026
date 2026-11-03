import type { Metadata } from "next"
import { Suspense } from "react"

import { PageHead } from "@/components/layout/page-head"
import { SummarySkeleton } from "@/features/workspace/components/skeletons"
import { Spec } from "@/features/workspace/components/spec"
import { getOrg, getProject } from "@/features/workspace/queries"

export const metadata: Metadata = { title: "Project overview" }

async function ProjectSummary({
  params,
}: {
  params: Promise<{ projectRef: string }>
}) {
  const { projectRef } = await params
  const project = await getProject(projectRef)
  if (!project) return null
  const org = await getOrg(project.orgSlug)
  return (
    <>
      <PageHead label="Project" title={project.name}>
        Project-wide summary.
      </PageHead>
      <Spec
        rows={[
          ["Ref", project.ref],
          ["Organization", org?.name ?? project.orgSlug],
          ["Plan", org?.plan ?? "none"],
          ["Status", project.status],
          ["Region", project.region],
          ["Created", project.createdAt],
        ]}
      />
    </>
  )
}

export default function ProjectOverviewPage({
  params,
}: {
  params: Promise<{ projectRef: string }>
}) {
  return (
    <Suspense fallback={<SummarySkeleton rows={6} />}>
      <ProjectSummary params={params} />
    </Suspense>
  )
}
