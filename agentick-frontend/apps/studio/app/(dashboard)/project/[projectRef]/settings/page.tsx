import type { Metadata } from "next"

import { PageHead } from "@/components/layout/page-head"

export const metadata: Metadata = { title: "Project settings" }

export default function ProjectSettingsPage() {
  return (
    <PageHead label="Project" title="Settings">
      Project name, keys and danger zone.
    </PageHead>
  )
}
