import type { Metadata } from "next"

import { PageHead } from "@/components/layout/page-head"

export const metadata: Metadata = { title: "Project database" }

export default function ProjectDatabasePage() {
  return (
    <PageHead label="Project" title="Database">
      Tables, queries and migrations of this project.
    </PageHead>
  )
}
