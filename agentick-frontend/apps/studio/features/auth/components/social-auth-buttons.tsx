"use client"

import {
  IconBrandGoogle,
  IconShieldLock,
  IconSparkles,
} from "@tabler/icons-react"
import { useActionState } from "react"

import { Button } from "@workspace/ui/components/button"
import { Spinner } from "@workspace/ui/components/spinner"
import { toast } from "@workspace/ui/components/toast"

type SocialAuthButtonsProps = {
  activeProvider: "better-auth" | "supabase" | "keycloak" | "fastapi-oauth"
  mode?: "sign-in" | "sign-up"
  hasDemo?: boolean
  keycloakAction: () => Promise<void>
  googleAction?: () => Promise<void>
  demoAction?: (
    _previous: { error?: string },
    _formData: FormData
  ) => Promise<{ error?: string }>
}

export function SocialAuthButtons({
  activeProvider,
  mode = "sign-in",
  hasDemo = false,
  keycloakAction,
  googleAction,
  demoAction,
}: SocialAuthButtonsProps) {
  const isKeycloakActive = activeProvider === "keycloak"
  const isGoogleActive = false // Google OAuth is disabled by default in template

  const [_demoState, demoFormAction, demoPending] = useActionState(
    demoAction ?? (async () => ({})),
    {}
  )

  const handleKeycloakClick = () => {
    if (!isKeycloakActive) {
      toast.add({
        title: "Provider not configured",
        description: `Keycloak SSO is not enabled on this deployment (active: ${activeProvider}).`,
        type: "error",
      })
    }
  }

  const handleGoogleClick = () => {
    if (!isGoogleActive) {
      toast.add({
        title: "Provider not configured",
        description:
          "Google login is not enabled on this deployment. Please enable Google provider in config.",
        type: "error",
      })
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="relative my-2">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      {/* Keycloak SSO Button */}
      {isKeycloakActive ? (
        <form action={keycloakAction}>
          <Button
            type="submit"
            variant="outline"
            size="lg"
            className="w-full gap-2"
          >
            <IconShieldLock className="size-4 text-primary" />
            <span>
              {mode === "sign-up"
                ? "Create account with Keycloak"
                : "Continue with Keycloak SSO"}
            </span>
          </Button>
        </form>
      ) : (
        <Button
          type="button"
          variant="outline"
          size="lg"
          className="w-full gap-2 opacity-75 hover:opacity-100"
          onClick={handleKeycloakClick}
        >
          <IconShieldLock className="size-4 text-muted-foreground" />
          <span>Continue with Keycloak SSO</span>
        </Button>
      )}

      {/* Google Button */}
      {isGoogleActive && googleAction ? (
        <form action={googleAction}>
          <Button
            type="submit"
            variant="outline"
            size="lg"
            className="w-full gap-2"
          >
            <IconBrandGoogle className="size-4" />
            <span>Continue with Google</span>
          </Button>
        </form>
      ) : (
        <Button
          type="button"
          variant="outline"
          size="lg"
          className="w-full gap-2 opacity-75 hover:opacity-100"
          onClick={handleGoogleClick}
        >
          <IconBrandGoogle className="size-4 text-muted-foreground" />
          <span>Continue with Google</span>
        </Button>
      )}

      {/* Demo Sign-in Button */}
      {hasDemo && demoAction && mode === "sign-in" ? (
        <form action={demoFormAction} className="mt-1">
          <Button
            type="submit"
            variant="secondary"
            size="lg"
            className="w-full gap-2"
            disabled={demoPending}
          >
            {demoPending ? (
              <>
                <Spinner className="mr-2" />
                Entering demo…
              </>
            ) : (
              <>
                <IconSparkles className="size-4" />
                <span>Demo sign in (instant access)</span>
              </>
            )}
          </Button>
        </form>
      ) : null}
    </div>
  )
}
