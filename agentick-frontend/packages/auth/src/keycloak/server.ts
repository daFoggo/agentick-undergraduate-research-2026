import "server-only"

import { io } from "next/cache"
import { cookies } from "next/headers"

import { authConfig } from "../config"
import type {
  AuthOptions,
  AuthProvider,
  Credentials,
  OAuthProvider,
  Session,
  SignUpInput,
  SignUpResult,
} from "../types"
import {
  getKeycloakCookieNames,
  parsePkceCookie,
  tokenCookieOptions,
} from "./cookies"
import { verifyKeycloakJwt } from "./jwks"
import {
  buildAuthorizationUrl,
  createPkceChallenge,
  exchangeAuthorizationCode,
  fetchKeycloakUserInfo,
  logoutKeycloakSession,
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

export function createKeycloakProvider(options: AuthOptions): AuthProvider {
  const cookieNames = getKeycloakCookieNames(options.cookieName)
  const oidcConfig = getOidcConfig()

  return {
    async getSession(): Promise<Session | null> {
      await io()
      const cookieStore = await cookies()
      const accessToken = cookieStore.get(cookieNames.access)?.value
      if (!accessToken) return null

      const claims = await verifyKeycloakJwt(accessToken, oidcConfig.issuer)
      if (!claims) return null

      return {
        userId: claims.userId,
        accessToken,
        role: claims.role,
        name: claims.name,
        email: claims.email,
        calendar: claims.calendar,
      }
    },

    async verifySessionFresh(): Promise<Session | null> {
      await io()
      const session = await this.getSession()
      if (!session) return null

      const userInfo = await fetchKeycloakUserInfo(
        oidcConfig,
        session.accessToken
      )
      if (!userInfo) return null

      return session
    },

    async refreshSession(): Promise<void> {
      const cookieStore = await cookies()
      const refreshToken = cookieStore.get(cookieNames.refresh)?.value
      if (!refreshToken) return

      try {
        const tokens = await refreshKeycloakTokens(oidcConfig, refreshToken)
        const accessMaxAge = tokens.expires_in || 300
        const refreshMaxAge = tokens.refresh_expires_in || 30 * 24 * 3600

        cookieStore.set(
          cookieNames.access,
          tokens.access_token,
          tokenCookieOptions(accessMaxAge)
        )
        if (tokens.refresh_token) {
          cookieStore.set(
            cookieNames.refresh,
            tokens.refresh_token,
            tokenCookieOptions(refreshMaxAge)
          )
        }
        if (tokens.id_token) {
          cookieStore.set(
            cookieNames.id,
            tokens.id_token,
            tokenCookieOptions(refreshMaxAge)
          )
        }
      } catch (err) {
        console.error("[keycloak] refreshSession error:", err)
      }
    },

    async signIn(_credentials: Credentials): Promise<void> {
      throw new Error(
        "Direct email/password login is not available on this stack. Please use the Keycloak SSO button below."
      )
    },

    async signUp(_input: SignUpInput): Promise<SignUpResult> {
      throw new Error(
        "Direct registration is not available on this stack. Please use the Keycloak SSO button below."
      )
    },

    async signOut(): Promise<void> {
      const cookieStore = await cookies()
      const refreshToken = cookieStore.get(cookieNames.refresh)?.value

      try {
        if (refreshToken) {
          await logoutKeycloakSession(oidcConfig, refreshToken)
        }
      } catch (err) {
        console.warn("[keycloak] logout error:", err)
      } finally {
        cookieStore.delete(cookieNames.access)
        cookieStore.delete(cookieNames.refresh)
        cookieStore.delete(cookieNames.id)
        cookieStore.delete(cookieNames.pkce)
      }
    },

    isExpectedError(error: unknown): boolean {
      return (
        error instanceof Error &&
        (error.message.includes("Keycloak") ||
          error.message.includes("not available on this stack"))
      )
    },

    oauth: {
      async start(
        provider: OAuthProvider,
        redirectTo: string
      ): Promise<string> {
        const cookieStore = await cookies()
        const pkce = createPkceChallenge()

        cookieStore.set(
          cookieNames.pkce,
          JSON.stringify({
            state: pkce.state,
            codeVerifier: pkce.codeVerifier,
            redirectUri: redirectTo,
          }),
          {
            httpOnly: true,
            sameSite: "lax",
            secure: process.env.NODE_ENV === "production",
            path: "/",
            maxAge: 600,
          }
        )

        const mode =
          provider === "keycloak-register"
            ? "register"
            : provider === "google"
              ? "google"
              : "login"

        return buildAuthorizationUrl(oidcConfig, {
          mode,
          redirectUri: redirectTo,
          state: pkce.state,
          codeChallenge: pkce.codeChallenge,
        })
      },

      async exchangeCode(code: string, state?: string | null): Promise<void> {
        const cookieStore = await cookies()
        const rawPkce = cookieStore.get(cookieNames.pkce)?.value
        cookieStore.delete(cookieNames.pkce)

        const pkce = parsePkceCookie(rawPkce)
        if (!pkce) {
          throw new Error("Invalid or expired PKCE state session.")
        }

        if (!state || state !== pkce.state) {
          throw new Error("State mismatch: possible CSRF attempt.")
        }

        const tokens = await exchangeAuthorizationCode(oidcConfig, {
          code,
          codeVerifier: pkce.codeVerifier,
          redirectUri: pkce.redirectUri,
        })

        const accessMaxAge = tokens.expires_in || 300
        const refreshMaxAge = tokens.refresh_expires_in || 30 * 24 * 3600

        cookieStore.set(
          cookieNames.access,
          tokens.access_token,
          tokenCookieOptions(accessMaxAge)
        )

        if (tokens.refresh_token) {
          cookieStore.set(
            cookieNames.refresh,
            tokens.refresh_token,
            tokenCookieOptions(refreshMaxAge)
          )
        }

        if (tokens.id_token) {
          cookieStore.set(
            cookieNames.id,
            tokens.id_token,
            tokenCookieOptions(refreshMaxAge)
          )
        }
      },
    },
  }
}
