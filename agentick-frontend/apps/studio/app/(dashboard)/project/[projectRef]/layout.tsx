import { Suspense } from "react"
import { notFound } from "next/navigation"

import { getProject } from "@/features/workspace/queries"

/** Renders nothing: only turns an unknown id into `notFound()`. */
async function ProjectGate({
  params,
}: {
  params: Promise<{ projectRef: string }>
}) {
  const { projectRef } = await params
  if (!(await getProject(projectRef))) notFound()
  return null
}

/**
 * Every page under `/project/<ref>`. The gate sits next to `children`, not around them, so the existence
 * check runs in parallel with the page's own reads instead of delaying them (docs/data-fetching.md §4.2).
 * Access is checked by the queries themselves. Status stays 200: the shell has already streamed.
 */
export default function ProjectLayout({
  params,
  children,
}: {
  params: Promise<{ projectRef: string }>
  children: React.ReactNode
}) {
  return (
    <>
      <Suspense fallback={null}>
        <ProjectGate params={params} />
      </Suspense>
      {children}
    </>
  )
}
