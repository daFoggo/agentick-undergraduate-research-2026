import { jwtVerify } from "jose"

import type { Role } from "../permissions"

export type VerifiedFastApiClaims = {
  userId: string
  role: Role
  name: string | null
  email: string | null
  exp?: number
}

/**
 * The backend's role vocabulary (`member` | `admin`) mapped onto the frontend's
 * (`customer` | `editor` | `admin`), the same convention Better Auth's `jwtPayload`
 * uses: an unrecognized or missing value becomes the least-privileged role.
 */
export function mapFastApiRole(value: unknown): Role {
  return value === "admin" ? "admin" : "customer"
}

const secretKeyCache = new Map<string, Uint8Array>()

function getSecretKey(secret: string): Uint8Array {
  let key = secretKeyCache.get(secret)
  if (!key) {
    key = new TextEncoder().encode(secret)
    secretKeyCache.set(secret, key)
  }
  return key
}

/**
 * Verifies the HS256 signature locally with the shared secret — no network call, the
 * same property Better Auth (EdDSA/JWKS) and Keycloak (RS256/JWKS) give this package,
 * just without a public-key fetch since issuer and verifier share one secret.
 */
export async function verifyFastApiJwt(
  token: string,
  secret: string
): Promise<VerifiedFastApiClaims | null> {
  try {
    const { payload } = await jwtVerify(token, getSecretKey(secret), {
      algorithms: ["HS256"],
    })
    if (!payload.sub || payload.type !== "access") return null

    return {
      userId: payload.sub,
      role: mapFastApiRole(payload.role),
      name: typeof payload.name === "string" ? payload.name : null,
      email: typeof payload.email === "string" ? payload.email : null,
      exp: payload.exp,
    }
  } catch {
    return null
  }
}
