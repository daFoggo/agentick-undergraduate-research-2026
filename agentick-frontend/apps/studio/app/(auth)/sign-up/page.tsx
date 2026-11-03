import type { Metadata } from "next"

import { SignUpForm } from "@/features/auth/components/sign-up-form"
import { SocialAuthButtons } from "@/features/auth/components/social-auth-buttons"

import { SIGN_IN_PATH } from "@/config/routes"
import {
  signUpAction,
  signInWithGoogleAction,
  signUpWithKeycloakAction,
} from "@/features/auth/actions"
import { getActiveAuthProvider } from "@/lib/auth"

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

export const metadata: Metadata = { title: "Sign up" }

export default function SignUpPage() {
  const activeProvider = getActiveAuthProvider()

  return (
    <>
      <AuthAside>
        <AuthPitch title="Start from a solid Next.js base.">
          A modular monorepo starter with pluggable auth, clean data layers, and Claude AI conventions.
        </AuthPitch>
        <StackShowcase />
      </AuthAside>
      <AuthMain>
        <AuthHeader>
          <AuthSwitch prompt="Already have an account?" href={SIGN_IN_PATH}>
            Sign in
          </AuthSwitch>
        </AuthHeader>
        <AuthBody>
          <AuthHeading eyebrow="Sign up" title="Create an account">
            Create an account to get started.
          </AuthHeading>
          <div className="flex flex-col gap-4">
            <SignUpForm action={signUpAction} />
            <SocialAuthButtons
              activeProvider={activeProvider}
              mode="sign-up"
              hasDemo={false}
              keycloakAction={signUpWithKeycloakAction}
              googleAction={signInWithGoogleAction}
            />
          </div>
        </AuthBody>
      </AuthMain>
    </>
  )
}
