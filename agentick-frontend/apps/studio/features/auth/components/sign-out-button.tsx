"use client"

import { useTransition } from "react"

import { Button } from "@workspace/ui/components/button"

export function SignOutButton({ action }: { action: () => Promise<void> }) {
  const [pending, startTransition] = useTransition()
  return (
    <Button
      variant="outline"
      size="lg"
      disabled={pending}
      onClick={() => startTransition(() => action())}
    >
      {pending ? "Signing out…" : "Sign out"}
    </Button>
  )
}
