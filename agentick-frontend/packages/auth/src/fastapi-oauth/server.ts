import "server-only"

import { io } from "next/cache"
import { cookies } from "next/headers"

import { authConfig } from "../config"
import type {
  AuthOptions,
  AuthProvider,
  Credentials,
  Session,
  SignUpInput,
  SignUpResult,
} from "../types"
import {
  FastApiAuthError,
  type FastApiTokenResponse,
  loginUser,
  refreshTokens,
  registerUser,
} from "./client"
import { getFastApiCookieNames, tokenCookieOptions } from "./cookies"
import { verifyFastApiJwt } from "./jwt"

function getFastApiConfig() {
  if (authConfig.AUTH_PROVIDER !== "fastapi-oauth") {
    return {
      apiBaseUrl: "http://localhost:11030",
      jwtSecretKey: "change-me-to-a-random-64-char-secret",
    }
  }
  return {
    apiBaseUrl: authConfig.API_BASE_URL,
    jwtSecretKey: authConfig.JWT_SECRET_KEY,
  }
}

/** Seconds left on a token's `exp` claim, or a safe default if it has none. */
function maxAgeFromExp(exp: number | undefined, fallbackSeconds: number): number {
  if (!exp) return fallbackSeconds
  return Math.max(1, exp - Math.floor(Date.now() / 1000))
}

const REFRESH_TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7

export function createFastApiOAuthProvider(options: AuthOptions): AuthProvider {
  const cookieNames = getFastApiCookieNames(options.cookieName)
  const { apiBaseUrl, jwtSecretKey } = getFastApiConfig()

  async function sessionFromAccessToken(accessToken: string | undefined): Promise<Session | null> {
    if (!accessToken) return null
    const claims = await verifyFastApiJwt(accessToken, jwtSecretKey)
    if (!claims) return null
    return {
      userId: claims.userId,
      accessToken,
      role: claims.role,
      name: claims.name,
      email: claims.email,
    }
  }

  /** Sets both cookies, sizing each `maxAge` from the token's own `exp` claim. */
  async function setSessionCookies(
    cookieStore: Awaited<ReturnType<typeof cookies>>,
    tokens: FastApiTokenResponse
  ): Promise<void> {
    const accessClaims = await verifyFastApiJwt(tokens.access_token, jwtSecretKey)
    cookieStore.set(
      cookieNames.access,
      tokens.access_token,
      tokenCookieOptions(maxAgeFromExp(accessClaims?.exp, 60 * 30))
    )
    cookieStore.set(
      cookieNames.refresh,
      tokens.refresh_token,
      tokenCookieOptions(REFRESH_TOKEN_MAX_AGE_SECONDS)
    )
  }

  return {
    async getSession(): Promise<Session | null> {
      // Better Auth checks token expiry against Date.now(), which must not run during prerender;
      // io() suspends only during prerender and resolves inside "use cache: private".
      await io()
      const cookieStore = await cookies()
      return sessionFromAccessToken(cookieStore.get(cookieNames.access)?.value)
    },

    async verifySessionFresh(): Promise<Session | null> {
      await io()
      const cookieStore = await cookies()
      const refreshToken = cookieStore.get(cookieNames.refresh)?.value
      if (!refreshToken) return null

      // Unlike getSession, this asks the backend to mint a fresh token: a deactivated
      // user is rejected here even if their still-unexpired access token looks valid.
      try {
        const tokens = await refreshTokens(apiBaseUrl, refreshToken)
        await setSessionCookies(cookieStore, tokens)
        return sessionFromAccessToken(tokens.access_token)
      } catch (error) {
        if (error instanceof FastApiAuthError) return null
        throw error
      }
    },

    async refreshSession(): Promise<void> {
      const cookieStore = await cookies()
      const refreshToken = cookieStore.get(cookieNames.refresh)?.value
      if (!refreshToken) return

      try {
        const tokens = await refreshTokens(apiBaseUrl, refreshToken)
        await setSessionCookies(cookieStore, tokens)
      } catch (err) {
        console.error("[fastapi-oauth] refreshSession error:", err)
      }
    },

    async signIn(credentials: Credentials): Promise<void> {
      const tokens = await loginUser(apiBaseUrl, credentials)
      const cookieStore = await cookies()
      await setSessionCookies(cookieStore, tokens)
    },

    async signUp(input: SignUpInput): Promise<SignUpResult> {
      await registerUser(apiBaseUrl, input)
      // The backend has no email verification step: the new account can sign in right away.
      await this.signIn(input)
      return "signed-in"
    },

    async signOut(): Promise<void> {
      // Stateless JWTs: there is no server-side revoke. Signing out only clears the
      // cookies the browser sends; a still-unexpired token presented directly to the
      // backend (not through this cookie) would remain valid until it expires.
      const cookieStore = await cookies()
      cookieStore.delete(cookieNames.access)
      cookieStore.delete(cookieNames.refresh)
    },

    isExpectedError(error: unknown): boolean {
      return error instanceof FastApiAuthError && error.status >= 400 && error.status < 500
    },
  }
}
