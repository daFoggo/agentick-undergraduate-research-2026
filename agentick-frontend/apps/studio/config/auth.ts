import type { AuthOptions } from "@workspace/auth/types"

/** The studio's own session cookie. */
export const AUTH_OPTIONS = {
  cookieName: "nmb-studio-auth",
} as const satisfies AuthOptions
