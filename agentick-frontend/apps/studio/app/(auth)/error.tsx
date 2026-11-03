"use client"

import { useEffect } from "react"
import Link from "next/link"

import { Button } from "@workspace/ui/components/button"

export default function AuthError({
  error,
  retry,
}: {
  error: Error & { digest?: string }
  retry: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center gap-6 text-center">
      <h1 className="text-3xl leading-tight font-normal tracking-tight">
        Something went wrong
      </h1>
      <p className="max-w-sm text-sm text-muted-foreground">
        We could not process your sign-in request right now. Please try again.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Button size="lg" onClick={() => retry()}>
          Try again
        </Button>
        <Button
          size="lg"
          variant="outline"
          render={<Link href="/" />}
          nativeButton={false}
        >
          Back to home
        </Button>
      </div>
    </div>
  )
}
