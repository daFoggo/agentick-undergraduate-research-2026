import { createRemoteJWKSet, jwtVerify } from "jose"

import { parseRole, type Role } from "../permissions"
import type { Calendar } from "../types"

export type VerifiedKeycloakClaims = {
  userId: string
  role: Role
  name: string | null
  email: string | null
  calendar?: Calendar
  exp?: number
}

export type VerifyKeycloakOptions = {
  clientId?: string
  expectedAudience?: string | string[]
  jwksOverride?: Parameters<typeof jwtVerify>[1]
}

const jwksCache = new Map<string, ReturnType<typeof createRemoteJWKSet>>()

export function getIssuerJwks(issuer: string) {
  let jwks = jwksCache.get(issuer)
  if (!jwks) {
    const certsUrl = new URL(
      `${issuer.replace(/\/+$/, "")}/protocol/openid-connect/certs`
    )
    jwks = createRemoteJWKSet(certsUrl)
    jwksCache.set(issuer, jwks)
  }
  return jwks
}

export function resolveKeycloakRole(
  claims: Record<string, unknown>,
  clientId?: string
): Role {
  const roleCandidates = new Set<string>()

  if (typeof claims.role === "string") {
    roleCandidates.add(claims.role)
  }

  if (Array.isArray(claims.roles)) {
    for (const r of claims.roles) {
      if (typeof r === "string") roleCandidates.add(r)
    }
  }

  const realmAccess = claims.realm_access as { roles?: unknown } | undefined
  if (realmAccess && Array.isArray(realmAccess.roles)) {
    for (const r of realmAccess.roles) {
      if (typeof r === "string") roleCandidates.add(r)
    }
  }

  if (clientId) {
    const resourceAccess = claims.resource_access as
      | Record<string, { roles?: unknown }>
      | undefined
    const clientRoles = resourceAccess?.[clientId]?.roles
    if (Array.isArray(clientRoles)) {
      for (const r of clientRoles) {
        if (typeof r === "string") roleCandidates.add(r)
      }
    }
  }

  // Privilege hierarchy: admin > editor > customer
  if (roleCandidates.has("admin")) return "admin"
  if (roleCandidates.has("editor")) return "editor"
  if (roleCandidates.has("customer")) return "customer"

  for (const candidate of roleCandidates) {
    const parsed = parseRole(candidate)
    if (parsed !== "customer") return parsed
  }

  return "customer"
}

function extractCalendar(
  claims: Record<string, unknown>
): Calendar | undefined {
  const { timezone, week_start: weekStart, adopted_on: adoptedOn } = claims
  return typeof timezone === "string" &&
    typeof weekStart === "number" &&
    typeof adoptedOn === "string"
    ? { timezone, weekStart, adoptedOn }
    : undefined
}

export async function verifyKeycloakJwt(
  token: string,
  issuer: string,
  optionsOrJwks?: VerifyKeycloakOptions | Parameters<typeof jwtVerify>[1]
): Promise<VerifiedKeycloakClaims | null> {
  try {
    const options: VerifyKeycloakOptions =
      typeof optionsOrJwks === "function" ||
      (optionsOrJwks && "keys" in (optionsOrJwks as object))
        ? { jwksOverride: optionsOrJwks as Parameters<typeof jwtVerify>[1] }
        : ((optionsOrJwks as VerifyKeycloakOptions) ?? {})

    const jwks = options.jwksOverride ?? getIssuerJwks(issuer)
    const { payload } = await jwtVerify(token, jwks, {
      issuer,
      ...(options.expectedAudience
        ? { audience: options.expectedAudience }
        : {}),
    })

    if (!payload.sub) return null

    // Enforce token type: Keycloak access tokens must have typ 'Bearer' if typ is present
    if (payload.typ && payload.typ !== "Bearer") {
      return null
    }

    // Enforce authorized party (azp) binding to client_id if present
    if (
      options.clientId &&
      typeof payload.azp === "string" &&
      payload.azp !== options.clientId
    ) {
      return null
    }

    const role = resolveKeycloakRole(
      payload as Record<string, unknown>,
      options.clientId
    )
    const name =
      (typeof payload.name === "string" && payload.name) ||
      (typeof payload.preferred_username === "string" &&
        payload.preferred_username) ||
      null
    const email = typeof payload.email === "string" ? payload.email : null
    const calendar = extractCalendar(payload as Record<string, unknown>)

    return {
      userId: payload.sub,
      role,
      name,
      email,
      calendar,
      exp: payload.exp,
    }
  } catch {
    return null
  }
}
