"use client"

import { Fragment } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@workspace/ui/components/breadcrumb"

import {
  breadcrumbTrail,
  type NavScope,
  type Workspace,
} from "@/config/navigation"

import { CrumbMenu } from "@/components/layout/header/crumb-menu"
import { NavIcon } from "@/components/layout/sidebar/nav-icons"

/** Renders `breadcrumbTrail`; below sm only the current page stays visible. */
export function DashboardBreadcrumb({
  scopes,
  workspace,
}: {
  scopes: NavScope[]
  workspace: Workspace
}) {
  const pathname = usePathname()
  const crumbs = breadcrumbTrail(pathname, scopes, workspace)
  return (
    <Breadcrumb className="min-w-0 font-mono">
      <BreadcrumbList className="flex-nowrap">
        {crumbs.map((crumb, index) => {
          if (index === crumbs.length - 1) {
            return (
              <BreadcrumbItem key={index} className="min-w-0">
                <BreadcrumbPage className="truncate">
                  {crumb.label}
                </BreadcrumbPage>
              </BreadcrumbItem>
            )
          }
          return (
            <Fragment key={index}>
              <BreadcrumbItem className="max-sm:hidden">
                {crumb.options ? (
                  <CrumbMenu crumb={crumb} />
                ) : crumb.href ? (
                  <BreadcrumbLink render={<Link href={crumb.href} />}>
                    {crumb.icon ? <NavIcon name={crumb.icon} /> : null}
                    {crumb.label}
                  </BreadcrumbLink>
                ) : (
                  crumb.label
                )}
              </BreadcrumbItem>
              <BreadcrumbSeparator className="text-muted-foreground/50 max-sm:hidden">
                /
              </BreadcrumbSeparator>
            </Fragment>
          )
        })}
      </BreadcrumbList>
    </Breadcrumb>
  )
}
