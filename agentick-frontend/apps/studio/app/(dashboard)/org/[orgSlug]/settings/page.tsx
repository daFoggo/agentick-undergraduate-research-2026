import type { Metadata } from "next"
import { Suspense } from "react"
import { IconAlertTriangle, IconDownload, IconShieldCheck, IconTrash } from "@tabler/icons-react"

import { Button } from "@workspace/ui/components/button"
import { PageHead } from "@/components/layout/page-head"
import { SummarySkeleton } from "@/features/workspace/components/skeletons"
import { getOrg } from "@/features/workspace/queries"

export const metadata: Metadata = { title: "Organization settings" }

async function SettingsContent({
  params,
}: {
  params: Promise<{ orgSlug: string }>
}) {
  const { orgSlug } = await params
  const org = await getOrg(orgSlug)
  if (!org) return null

  return (
    <div className="flex flex-col gap-8">
      <PageHead label="Organization" title="Settings">
        Organization settings, compliance, data portability, and deletion.
      </PageHead>

      {/* General Settings */}
      <div className="flex flex-col gap-4 rounded-lg border border-border/50 bg-muted/10 p-6">
        <h3 className="text-base font-medium text-foreground">Organization Overview</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 font-mono text-xs">
          <div>
            <span className="text-muted-foreground">Name</span>
            <p className="mt-1 text-sm font-medium text-foreground">{org.name}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Slug</span>
            <p className="mt-1 text-sm font-medium text-foreground">{org.slug}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Current Plan</span>
            <p className="mt-1 text-sm font-medium text-foreground">{org.plan}</p>
          </div>
        </div>
      </div>

      {/* Data Privacy & Portability (PDPL 91/2025 & GDPR Compliance) */}
      <div className="flex flex-col gap-4 rounded-lg border border-border/50 bg-muted/10 p-6">
        <div className="flex items-center gap-2">
          <IconShieldCheck className="size-5 text-emerald-500 shrink-0" />
          <h3 className="text-base font-medium text-foreground">Data Privacy &amp; Portability</h3>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          In accordance with the Personal Data Protection Law (Law No. 91/2025/QH15, Decree No. 356/2025/ND-CP) and GDPR,
          you hold the right to export all workspace configurations, audit logs, and member records in a portable JSON format.
        </p>
        <div className="flex items-center gap-3 pt-2">
          <Button variant="outline" size="sm" className="gap-2">
            <IconDownload className="size-4" />
            <span>Export Organization Data (JSON)</span>
          </Button>
        </div>
      </div>

      {/* Danger Zone: Account & Organization Deletion (ACCOUNT_DELETE Requirement) */}
      <div className="flex flex-col gap-4 rounded-lg border border-destructive/30 bg-destructive/5 p-6">
        <div className="flex items-center gap-2">
          <IconAlertTriangle className="size-5 text-destructive shrink-0" />
          <h3 className="text-base font-medium text-destructive">Danger Zone: Erasure &amp; Deletion</h3>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Requesting organization or account deletion initiates an irreversible data purge.
          All projects, active tokens, and member permissions will be scheduled for permanent removal within the statutory
          20 business-day erasure timeline.
        </p>
        <div className="flex items-center gap-3 pt-2">
          <Button variant="destructive" size="sm" className="gap-2">
            <IconTrash className="size-4" />
            <span>Request Complete Erasure</span>
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function OrganizationSettingsPage({
  params,
}: {
  params: Promise<{ orgSlug: string }>
}) {
  return (
    <Suspense fallback={<SummarySkeleton />}>
      <SettingsContent params={params} />
    </Suspense>
  )
}
