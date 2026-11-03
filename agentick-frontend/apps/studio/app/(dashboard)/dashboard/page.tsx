import type { Metadata } from "next"
import { Suspense } from "react"

import { PageHead } from "@/components/layout/page-head"
import { requirePermission } from "@/lib/dal"

export const metadata: Metadata = { title: "Overview" }

async function Guard() {
  await requirePermission("account:view")
  return null
}

export default function DashboardPage() {
  return (
    <>
      <Suspense fallback={null}>
        <Guard />
      </Suspense>
      <PageHead label="Workspace" title="Overview">
        This is your dashboard. Add sections in config/navigation.ts and pages
        under app/(dashboard).
      </PageHead>
    </>
  )
}
