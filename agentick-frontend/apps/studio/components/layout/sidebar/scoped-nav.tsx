"use client"

import { usePathname } from "next/navigation"

import { sectionsFor, type NavScope } from "@/config/navigation"

import { AppSidebarSection } from "@/components/layout/sidebar/app-sidebar"
import { NavTree } from "@/components/layout/sidebar/nav-tree"

/**
 * The sidebar menu of the current URL: picks the scope (global, organization, project, ...) from
 * the pathname and renders its sections. `scopes` come already filtered by role from the server.
 */
export function ScopedNav({ scopes }: { scopes: NavScope[] }) {
  const pathname = usePathname()
  return sectionsFor(scopes, pathname).map((section) => (
    <AppSidebarSection key={section.label} label={section.label}>
      <NavTree entries={section.entries} />
    </AppSidebarSection>
  ))
}
