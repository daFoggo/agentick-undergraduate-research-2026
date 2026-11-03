import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

import { authConfig } from "../config"
import type { AuthOptions, ProxyAuthResult } from "../types"
import { FastApiAuthError, refreshTokens } from "./client"
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

const REFRESH_TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7

export async function updateSession(
  request: NextRequest,
  options: AuthOptions
): Promise<ProxyAuthResult> {
  let response = NextResponse.next({ request })
  const cookieNames = getFastApiCookieNames(options.cookieName)
  const { apiBaseUrl, jwtSecretKey } = getFastApiConfig()

  const accessToken = request.cookies.get(cookieNames.access)?.value
  const refreshToken = request.cookies.get(cookieNames.refresh)?.value

  if (!accessToken && !refreshToken) {
    return { response, isAuthenticated: false, role: null }
  }

  const nowSeconds = Math.floor(Date.now() / 1000)

  // 1. The access token still has more than 60s left: verified locally, no network call.
  if (accessToken) {
    const claims = await verifyFastApiJwt(accessToken, jwtSecretKey)
    if (claims && (!claims.exp || claims.exp - nowSeconds > 60)) {
      return { response, isAuthenticated: true, role: claims.role }
    }
  }

  // 2. Missing or expiring soon: refresh using the refresh token.
  if (!refreshToken) {
    return { response, isAuthenticated: false, role: null }
  }

  try {
    const tokens = await refreshTokens(apiBaseUrl, refreshToken)
    const newClaims = await verifyFastApiJwt(tokens.access_token, jwtSecretKey)
    if (!newClaims) {
      response.cookies.delete(cookieNames.access)
      response.cookies.delete(cookieNames.refresh)
      return { response, isAuthenticated: false, role: null }
    }

    const accessMaxAge = newClaims.exp
      ? Math.max(1, newClaims.exp - nowSeconds)
      : 60 * 30

    request.cookies.set(cookieNames.access, tokens.access_token)
    request.cookies.set(cookieNames.refresh, tokens.refresh_token)
    response = NextResponse.next({ request })
    response.cookies.set(
      cookieNames.access,
      tokens.access_token,
      tokenCookieOptions(accessMaxAge)
    )
    response.cookies.set(
      cookieNames.refresh,
      tokens.refresh_token,
      tokenCookieOptions(REFRESH_TOKEN_MAX_AGE_SECONDS)
    )
    response.headers.set("Cache-Control", "private, no-store")

    return { response, isAuthenticated: true, role: newClaims.role }
  } catch (error) {
    if (!(error instanceof FastApiAuthError)) {
      console.error("[fastapi-oauth-proxy] token refresh failed:", error)
    }
    response.cookies.delete(cookieNames.access)
    response.cookies.delete(cookieNames.refresh)
    return { response, isAuthenticated: false, role: null }
  }
}
