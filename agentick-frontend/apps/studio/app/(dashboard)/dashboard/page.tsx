import type { Metadata } from "next"
import { Suspense } from "react"

import { PageHead } from "@/components/layout/page-head"
import { requirePermission } from "@/lib/dal"

import { TraceSheet } from "./_components/trace-sheet"

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
      <section className="flex flex-col gap-3">
        <span className="font-mono text-xs tracking-wider text-muted-foreground uppercase">
          Detail sheet
        </span>
        <p className="max-w-2xl text-muted-foreground">
          A record opens in a sheet instead of a fixed column. Remove this demo
          when you add your own.
        </p>
        <div>
          <TraceSheet />
        </div>
      </section>
    </>
  )
}
