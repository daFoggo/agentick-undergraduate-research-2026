import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

import { SIGN_IN_PATH } from "@/config/routes"
import { getAuthProvider } from "@/lib/auth"
import { publicEnv } from "@/lib/env.public"

/**
 * Landing point when the backend rejects a token the session still holds (for
 * example the user was deactivated). Server Components cannot clear cookies,
 * so they redirect here; clearing the session also prevents a redirect loop.
 */
export async function GET(request: NextRequest) {
  const secFetchSite = request.headers.get("sec-fetch-site")
  const targetUrl = new URL(SIGN_IN_PATH, publicEnv.NEXT_PUBLIC_APP_URL)

  // Prevent cross-site logout / login CSRF denial of service
  if (secFetchSite === "cross-site") {
    return NextResponse.redirect(targetUrl)
  }

  try {
    await (await getAuthProvider()).signOut()
  } catch {
    // Even if provider sign-out fails we still send the user to sign-in.
  }
  return NextResponse.redirect(targetUrl)
}
