"use client"

import { useTransition } from "react"

import { DropdownMenuItem } from "@workspace/ui/components/dropdown-menu"

export function SignOutMenuItem({ action }: { action: () => Promise<void> }) {
  const [pending, startTransition] = useTransition()
  return (
    <DropdownMenuItem
      disabled={pending}
      // Keep the menu open while the action runs; it redirects to sign-in when done.
      closeOnClick={false}
      onClick={() => startTransition(() => action())}
    >
      {pending ? "Signing out…" : "Sign out"}
    </DropdownMenuItem>
  )
}
