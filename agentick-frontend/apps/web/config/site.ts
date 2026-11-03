import { publicEnv } from "@/lib/env.public"

/** Absolute link into the dashboard app (apps/studio), which owns sign-in and every signed-in page. */
export function studioHref(path: string): string {
  return new URL(path, publicEnv.NEXT_PUBLIC_STUDIO_URL).toString()
}

export const REPO_URL = "https://github.com/daFoggo/next-mono-base"

export const SIGN_IN_HREF = studioHref("/sign-in")
export const SIGN_UP_HREF = studioHref("/sign-up")
