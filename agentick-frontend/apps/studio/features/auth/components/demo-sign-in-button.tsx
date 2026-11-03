"use client"

import { useActionState } from "react"

import { Button } from "@workspace/ui/components/button"
import { Spinner } from "@workspace/ui/components/spinner"

import { FormError } from "./form-error"
import type { DemoSignInState, FormAction } from "../types"

export function DemoSignInButton({
  action,
}: {
  action: FormAction<DemoSignInState>
}) {
  const [state, formAction, pending] = useActionState(action, {})

  return (
    <form action={formAction} className="flex flex-col gap-4">
      <FormError message={state.error} />
      <Button
        type="submit"
        variant="outline"
        size="lg"
        className="w-full"
        disabled={pending}
      >
        {pending ? <Spinner className="mr-2" /> : null}
        Demo login
      </Button>
    </form>
  )
}
