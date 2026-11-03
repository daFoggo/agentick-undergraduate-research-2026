import { Suspense } from "react"
import Link from "next/link"

import { SidebarInset, SidebarProvider } from "@workspace/ui/components/sidebar"
import { Skeleton } from "@workspace/ui/components/skeleton"

import {
  AppSidebar,
  AppSidebarBody,
  AppSidebarSection,
} from "@/components/layout/sidebar/app-sidebar"
import { ColumnHeader } from "@/components/layout/column-header"
import { MainHeaderStart } from "@/components/layout/header/main-header-start"
import { ThemeToggle } from "@workspace/ui-patterns/theme-toggle"
import { Stagger } from "@/components/shared/stagger"
import { AppLogo } from "@workspace/ui-patterns/app-logo"
import { DASHBOARD_PATH } from "@/config/routes"

import { DashboardCrumbs } from "./_components/crumbs"
import { SessionAccount, SessionNav } from "./_components/session-nav"

/**
 * Dashboard shell (design system §8): sidebar column + main column, each a ColumnHeader over a
 * scrolling body. The static frame prerenders; session-dependent parts stream in <Suspense>.
 * No authorization here: pages call `requirePermission` next to their data. Detail views open
 * as sheets from the page itself (components/shared/detail-sheet.tsx), so the shell holds no
 * panel state.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <SidebarProvider>
      <AppSidebar>
        {/*
          `px-3` puts the mark at the same x in the 256px sidebar and the 48px rail, so collapsing
          never moves it. The wordmark never wraps or shrinks: the narrowing sidebar just clips it.
        */}
        <ColumnHeader className="overflow-hidden px-3">
          <Link href={DASHBOARD_PATH} className="shrink-0">
            <AppLogo textClassName="whitespace-nowrap group-data-[collapsible=icon]:invisible" />
          </Link>
        </ColumnHeader>
        <AppSidebarBody>
          {/* One AppSidebarSection per nav section (config/navigation.ts). */}
          <Suspense fallback={<NavSkeleton />}>
            <SessionNav />
          </Suspense>
          <AppSidebarSection label="Account" pinned>
            <Suspense fallback={<Skeleton className="h-8" />}>
              <SessionAccount />
            </Suspense>
          </AppSidebarSection>
        </AppSidebarBody>
      </AppSidebar>
      <SidebarInset>
        <div className="flex h-svh min-w-0 flex-col">
          <ColumnHeader>
            <MainHeaderStart>
              <Suspense fallback={null}>
                <DashboardCrumbs />
              </Suspense>
            </MainHeaderStart>
            <ThemeToggle className="ml-auto" />
          </ColumnHeader>
          <div className="no-scrollbar flex-1 overflow-y-auto">
            <Stagger className="flex flex-col gap-8 px-4 pt-10 pb-14 sm:px-8">
              {children}
            </Stagger>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

// Not SidebarMenuSkeleton: its random widths (Math.random) are not allowed while prerendering.
function NavSkeleton() {
  return (
    <div className="flex flex-col gap-2">
      <Skeleton className="h-6" />
      <Skeleton className="h-6" />
      <Skeleton className="h-6" />
    </div>
  )
}
