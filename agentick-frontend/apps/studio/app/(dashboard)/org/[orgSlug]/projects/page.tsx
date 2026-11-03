import type { Metadata } from "next"
import { Suspense } from "react"

import { PageHead } from "@/components/layout/page-head"
import { CreateProjectDialog } from "@/features/workspace/components/create-dialogs"
import { CardGridSkeleton } from "@/features/workspace/components/skeletons"
import {
  CardGrid,
  ProjectCard,
} from "@/features/workspace/components/workspace-cards"
import { getProjectsOf } from "@/features/workspace/queries"

export const metadata: Metadata = { title: "Projects" }

async function ProjectList({
  params,
}: {
  params: Promise<{ orgSlug: string }>
}) {
  const { orgSlug } = await params
  return (
    <CardGrid>
      {(await getProjectsOf(orgSlug)).map((project) => (
        <ProjectCard key={project.ref} project={project} />
      ))}
    </CardGrid>
  )
}

async function NewProject({
  params,
}: {
  params: Promise<{ orgSlug: string }>
}) {
  return <CreateProjectDialog orgSlug={(await params).orgSlug} />
}

export default function ProjectsPage({
  params,
}: {
  params: Promise<{ orgSlug: string }>
}) {
  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <PageHead label="Organization" title="Projects">
          Open a project to switch the sidebar to its menu.
        </PageHead>
        <Suspense fallback={null}>
          <NewProject params={params} />
        </Suspense>
      </div>
      <Suspense fallback={<CardGridSkeleton />}>
        <ProjectList params={params} />
      </Suspense>
    </>
  )
}
