/** Split cookie names to ensure each token stays well below the 4096-byte browser limit. */
export type KeycloakCookieNames = {
  access: string
  refresh: string
  id: string
  pkce: string
}

export type PkcePayload = {
  state: string
  codeVerifier: string
  redirectUri: string
}

export function getKeycloakCookieNames(baseName: string): KeycloakCookieNames {
  return {
    access: `${baseName}.access`,
    refresh: `${baseName}.refresh`,
    id: `${baseName}.id`,
    pkce: `${baseName}.pkce`,
  }
}

export function parsePkceCookie(raw: string | undefined): PkcePayload | null {
  if (!raw) return null
  try {
    const data = JSON.parse(raw) as Partial<PkcePayload>
    if (
      typeof data.state === "string" &&
      typeof data.codeVerifier === "string" &&
      typeof data.redirectUri === "string"
    ) {
      return {
        state: data.state,
        codeVerifier: data.codeVerifier,
        redirectUri: data.redirectUri,
      }
    }
    return null
  } catch {
    return null
  }
}

export function tokenCookieOptions(maxAgeSeconds: number) {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/" as const,
    maxAge: maxAgeSeconds,
  }
}
