import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

import { SIGN_IN_PATH } from "@/config/routes"
import { getAuthProvider } from "@/lib/auth"

/**
 * Landing point when the backend rejects a token the session still holds (for
 * example the user was deactivated). Server Components cannot clear cookies,
 * so they redirect here; clearing the session also prevents a redirect loop.
 */
export async function GET(request: NextRequest) {
  try {
    await (await getAuthProvider()).signOut()
  } catch {
    // Even if provider sign-out fails we still send the user to sign-in.
  }
  return NextResponse.redirect(new URL(SIGN_IN_PATH, request.nextUrl.origin))
}
