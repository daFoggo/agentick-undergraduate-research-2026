"use client"

import Link from "next/link"
import { IconSelector } from "@tabler/icons-react"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@workspace/ui/components/dropdown-menu"

import type { Crumb } from "@/config/navigation"

import { NavIcon } from "@/components/layout/sidebar/nav-icons"

/** A breadcrumb that is a menu (switch organization, switch project). The current entry is the label. */
export function CrumbMenu({ crumb }: { crumb: Crumb }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-1 rounded-md transition-colors duration-150 hover:text-foreground aria-expanded:text-foreground">
        {crumb.icon ? <NavIcon name={crumb.icon} /> : null}
        {crumb.label}
        <IconSelector aria-hidden className="size-4" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        {crumb.options?.map((option) => (
          <DropdownMenuItem
            key={option.href}
            render={<Link href={option.href} />}
          >
            {option.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
