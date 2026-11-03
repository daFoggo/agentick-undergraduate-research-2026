import Link from "next/link"

import { SidebarTrigger } from "@workspace/ui/components/sidebar"

import { AppLogo } from "@workspace/ui-patterns/app-logo"
import { DASHBOARD_PATH } from "@/config/routes"

/**
 * Left of the main header: the sidebar trigger (shadcn; Cmd/Ctrl+B works too). Below md the
 * sidebar is a Sheet, so the header also carries the logo; from md the sidebar shows it itself.
 */
export function MainHeaderStart({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-w-0 items-center gap-3">
      <SidebarTrigger className="-ml-1.5" />
      <Link href={DASHBOARD_PATH} className="shrink-0 md:hidden">
        <AppLogo />
      </Link>
      <span
        aria-hidden
        className="font-mono text-sm text-muted-foreground/50 md:hidden"
      >
        /
      </span>
      {children}
    </div>
  )
}
