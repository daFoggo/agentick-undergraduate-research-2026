"use server"

import { cookies } from "next/headers"
import { updateTag } from "next/cache"
import { redirect } from "next/navigation"

import { SignInSchema, SignUpSchema } from "@workspace/auth/schemas"
import type { SignInState, SignUpState } from "./types"

import {
  DASHBOARD_PATH,
  OAUTH_CALLBACK_PATH,
  SIGN_IN_PATH,
} from "@/config/routes"
import { getAuthProvider, type SignUpResult } from "@/lib/auth"
import { SESSION_TAG } from "@/lib/dal"
import {
  DEMO_COOKIE,
  DEMO_TTL_SECONDS,
  createDemoToken,
  demoAuthSecret,
} from "@/lib/demo-session"
import { getErrorMessage } from "@/lib/errors"
import { publicEnv } from "@/lib/env.public"

export async function signInAction(
  _previous: SignInState,
  formData: FormData
): Promise<SignInState> {
  const values = { email: String(formData.get("email") ?? "") }
  const parsed = SignInSchema.safeParse({
    email: values.email,
    password: formData.get("password"),
  })
  if (!parsed.success) {
    return {
      error: parsed.error.issues[0]?.message ?? "Invalid data",
      values,
    }
  }

  const provider = await getAuthProvider()
  try {
    await provider.signIn(parsed.data)
  } catch (error) {
    if (!provider.isExpectedError(error)) {
      console.error("[signInAction] unexpected error:", error)
      return {
        error: "Could not reach the sign-in server. Please try again later.",
        values,
      }
    }
    return { error: getErrorMessage(error, "Could not sign in"), values }
  }

  // getSession() is "use cache: private" and only reruns for a new cookie once its tag
  // is invalidated — without this, the dashboard can keep rendering the signed-out shell.
  updateTag(SESSION_TAG)
  // redirect() throws, so it must stay outside the try/catch.
  redirect(DASHBOARD_PATH)
}

export async function signUpAction(
  _previous: SignUpState,
  formData: FormData
): Promise<SignUpState> {
  const values = {
    name: String(formData.get("name") ?? ""),
    email: String(formData.get("email") ?? ""),
  }
  const parsed = SignUpSchema.safeParse({
    ...values,
    password: formData.get("password"),
    confirmPassword: formData.get("confirmPassword"),
  })
  if (!parsed.success) {
    return {
      error: parsed.error.issues[0]?.message ?? "Invalid data",
      values,
    }
  }

  const { confirmPassword: _, ...signUpData } = parsed.data

  const provider = await getAuthProvider()
  let result: SignUpResult
  try {
    result = await provider.signUp(signUpData)
  } catch (error) {
    if (!provider.isExpectedError(error)) {
      console.error("[signUpAction] unexpected error:", error)
      return {
        error: "Could not reach the sign-in server. Please try again later.",
        values,
      }
    }
    return {
      error: getErrorMessage(error, "Could not create the account"),
      values,
    }
  }

  if (result === "confirm-email") return { confirmEmail: true }
  updateTag(SESSION_TAG)
  redirect(DASHBOARD_PATH)
}

export async function signInWithGoogleAction(): Promise<void> {
  const provider = await getAuthProvider()
  let url: string | undefined
  try {
    url = await provider.oauth?.start(
      "google",
      `${publicEnv.NEXT_PUBLIC_APP_URL}${OAUTH_CALLBACK_PATH}`
    )
  } catch (error) {
    if (!provider.isExpectedError(error)) throw error
  }
  redirect(url ?? `${SIGN_IN_PATH}?error=oauth`)
}

export async function signInWithKeycloakAction(): Promise<void> {
  const provider = await getAuthProvider()
  let url: string | undefined
  try {
    url = await provider.oauth?.start(
      "keycloak",
      `${publicEnv.NEXT_PUBLIC_APP_URL}${OAUTH_CALLBACK_PATH}`
    )
  } catch (error) {
    if (!provider.isExpectedError(error)) throw error
  }
  redirect(url ?? `${SIGN_IN_PATH}?error=oauth`)
}

export async function signUpWithKeycloakAction(): Promise<void> {
  const provider = await getAuthProvider()
  let url: string | undefined
  try {
    url = await provider.oauth?.start(
      "keycloak-register",
      `${publicEnv.NEXT_PUBLIC_APP_URL}${OAUTH_CALLBACK_PATH}`
    )
  } catch (error) {
    if (!provider.isExpectedError(error)) throw error
  }
  redirect(url ?? `${SIGN_IN_PATH}?error=oauth`)
}

export async function demoSignInAction(
  _previous: { error?: string },
  _formData: FormData
): Promise<{ error?: string }> {
  const secret = demoAuthSecret()
  if (!secret) return { error: "Demo login is disabled." }

  const cookieStore = await cookies()
  cookieStore.set(DEMO_COOKIE, await createDemoToken(secret), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: DEMO_TTL_SECONDS,
  })
  updateTag(SESSION_TAG)
  redirect(DASHBOARD_PATH)
}

export async function signOutAction(): Promise<void> {
  const provider = await getAuthProvider()
  await provider.signOut()
  updateTag(SESSION_TAG)
  redirect(SIGN_IN_PATH)
}
