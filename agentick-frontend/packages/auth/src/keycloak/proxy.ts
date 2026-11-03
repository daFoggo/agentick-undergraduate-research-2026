import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

import { authConfig } from "../config"
import type { AuthOptions, ProxyAuthResult } from "../types"
import {
  getKeycloakCookieNames,
  tokenCookieOptions,
} from "./cookies"
import { verifyKeycloakJwt } from "./jwks"
import {
  refreshKeycloakTokens,
  type KeycloakOidcConfig,
} from "./oidc"

function getOidcConfig(): KeycloakOidcConfig {
  if (authConfig.AUTH_PROVIDER !== "keycloak") {
    return {
      issuer: "http://localhost:8080/realms/studio",
      clientId: "studio-app",
      clientSecret: "studio-dev-client-secret-at-least-32-chars",
    }
  }
  return {
    issuer: authConfig.KEYCLOAK_ISSUER,
    clientId: authConfig.KEYCLOAK_CLIENT_ID,
    clientSecret: authConfig.KEYCLOAK_CLIENT_SECRET,
  }
}

export async function updateSession(
  request: NextRequest,
  options: AuthOptions
): Promise<ProxyAuthResult> {
  let response = NextResponse.next({ request })
  const cookieNames = getKeycloakCookieNames(options.cookieName)
  const oidcConfig = getOidcConfig()

  const accessToken = request.cookies.get(cookieNames.access)?.value
  const refreshToken = request.cookies.get(cookieNames.refresh)?.value

  // Short-circuit: if no tokens exist, avoid any processing
  if (!accessToken && !refreshToken) {
    return { response, isAuthenticated: false, role: null }
  }

  const nowSeconds = Math.floor(Date.now() / 1000)

  // 1. Try existing access token if it has more than 60s left
  if (accessToken) {
    const claims = await verifyKeycloakJwt(accessToken, oidcConfig.issuer)
    if (claims && (!claims.exp || claims.exp - nowSeconds > 60)) {
      return {
        response,
        isAuthenticated: true,
        role: claims.role,
      }
    }
  }

  // 2. Access token is missing or expiring soon: refresh using refreshToken
  if (!refreshToken) {
    return { response, isAuthenticated: false, role: null }
  }

  try {
    const tokens = await refreshKeycloakTokens(oidcConfig, refreshToken)
    const accessMaxAge = tokens.expires_in || 300
    const refreshMaxAge = tokens.refresh_expires_in || 30 * 24 * 3600
    const newRefreshToken = tokens.refresh_token || refreshToken

    // Update request cookies for downstream Server Components
    request.cookies.set(cookieNames.access, tokens.access_token)
    request.cookies.set(cookieNames.refresh, newRefreshToken)
    if (tokens.id_token) {
      request.cookies.set(cookieNames.id, tokens.id_token)
    }

    response = NextResponse.next({ request })

    // Update response cookies for browser
    response.cookies.set(
      cookieNames.access,
      tokens.access_token,
      tokenCookieOptions(accessMaxAge)
    )
    response.cookies.set(
      cookieNames.refresh,
      newRefreshToken,
      tokenCookieOptions(refreshMaxAge)
    )
    if (tokens.id_token) {
      response.cookies.set(
        cookieNames.id,
        tokens.id_token,
        tokenCookieOptions(refreshMaxAge)
      )
    }

    response.headers.set("Cache-Control", "private, no-store")

    const newClaims = await verifyKeycloakJwt(
      tokens.access_token,
      oidcConfig.issuer
    )

    if (!newClaims) {
      response.cookies.delete(cookieNames.access)
      response.cookies.delete(cookieNames.refresh)
      response.cookies.delete(cookieNames.id)
      return { response, isAuthenticated: false, role: null }
    }

    return {
      response,
      isAuthenticated: true,
      role: newClaims.role,
    }
  } catch (error) {
    console.error("[keycloak-proxy] token refresh failed:", error)
    response.cookies.delete(cookieNames.access)
    response.cookies.delete(cookieNames.refresh)
    response.cookies.delete(cookieNames.id)
    return { response, isAuthenticated: false, role: null }
  }
}
