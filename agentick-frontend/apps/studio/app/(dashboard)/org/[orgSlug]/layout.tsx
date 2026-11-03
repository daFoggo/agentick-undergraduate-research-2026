import { Suspense } from "react"
import { notFound } from "next/navigation"

import { getOrg } from "@/features/workspace/queries"

/** Renders nothing: only turns an unknown id into `notFound()`. */
async function OrgGate({ params }: { params: Promise<{ orgSlug: string }> }) {
  const { orgSlug } = await params
  if (!(await getOrg(orgSlug))) notFound()
  return null
}

/**
 * Every page under `/org/<slug>`. The gate sits next to `children`, not around them, so the existence
 * check runs in parallel with the page's own reads instead of delaying them (docs/data-fetching.md §4.2).
 * Access is checked by the queries themselves. Status stays 200: the shell has already streamed.
 */
export default function OrgLayout({
  params,
  children,
}: {
  params: Promise<{ orgSlug: string }>
  children: React.ReactNode
}) {
  return (
    <>
      <Suspense fallback={null}>
        <OrgGate params={params} />
      </Suspense>
      {children}
    </>
  )
}
