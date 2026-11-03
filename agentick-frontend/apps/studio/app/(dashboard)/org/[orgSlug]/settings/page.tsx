import type { Metadata } from "next"

import { PageHead } from "@/components/layout/page-head"

export const metadata: Metadata = { title: "Organization settings" }

export default function OrganizationSettingsPage() {
  return (
    <PageHead label="Organization" title="Settings">
      Organization name, members and billing.
    </PageHead>
  )
}
