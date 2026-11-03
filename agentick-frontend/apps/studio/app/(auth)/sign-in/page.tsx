import type { Metadata } from "next"
import { Suspense } from "react"

import { FormError } from "@/features/auth/components/form-error"
import { SignInForm } from "@/features/auth/components/sign-in-form"
import { SocialAuthButtons } from "@/features/auth/components/social-auth-buttons"

import { SIGN_UP_PATH } from "@/config/routes"
import {
  demoSignInAction,
  signInAction,
  signInWithGoogleAction,
  signInWithKeycloakAction,
} from "@/features/auth/actions"
import { getActiveAuthProvider } from "@/lib/auth"
import { demoAuthSecret } from "@/lib/demo-session"

import {
  AuthAside,
  AuthBody,
  AuthHeader,
  AuthHeading,
  AuthMain,
  AuthPitch,
  AuthSwitch,
} from "../_components/auth-frame"
import { StackShowcase } from "../_components/stack-showcase"

export const metadata: Metadata = { title: "Sign in" }

async function OAuthError({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>
}) {
  const { error } = await searchParams
  if (!error) return null
  return (
    <FormError message="Sign-in with the provider failed. Please try again." />
  )
}

export default function SignInPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>
}) {
  const activeProvider = getActiveAuthProvider()
  const hasDemo = demoAuthSecret() !== null

  return (
    <>
      <AuthAside>
        <AuthPitch title="Pick up where you left off.">
          Next.js 16 monorepo starter with pluggable auth (Keycloak, Better Auth, or Supabase).
        </AuthPitch>
        <StackShowcase />
      </AuthAside>
      <AuthMain>
        <AuthHeader>
          <AuthSwitch prompt="No account?" href={SIGN_UP_PATH}>
            Sign up
          </AuthSwitch>
        </AuthHeader>
        <AuthBody>
          <AuthHeading eyebrow="Sign in" title="Welcome back">
            Sign in to your account.
          </AuthHeading>
          <div className="flex flex-col gap-4">
            <Suspense>
              <OAuthError searchParams={searchParams} />
            </Suspense>
            <SignInForm action={signInAction} />
            <SocialAuthButtons
              activeProvider={activeProvider}
              mode="sign-in"
              hasDemo={hasDemo}
              keycloakAction={signInWithKeycloakAction}
              googleAction={signInWithGoogleAction}
              demoAction={demoSignInAction}
            />
          </div>
        </AuthBody>
      </AuthMain>
    </>
  )
}
