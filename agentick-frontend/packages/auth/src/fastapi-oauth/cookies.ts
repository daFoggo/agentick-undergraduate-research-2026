/** Split cookie names, matching the keycloak provider's convention. */
export type FastApiCookieNames = {
  access: string
  refresh: string
}

export function getFastApiCookieNames(baseName: string): FastApiCookieNames {
  return {
    access: `${baseName}.access`,
    refresh: `${baseName}.refresh`,
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
