export const DEMO_COOKIE = "nmb-web-demo"
export const DEMO_TTL_SECONDS = 7200

const MIN_SECRET_LENGTH = 32

type DemoClaims = { sub: string; role: "customer"; exp: number }

const encoder = new TextEncoder()
const decoder = new TextDecoder()

export function demoAuthSecret(): string | null {
  if (process.env.DEMO_AUTH !== "true") return null
  const secret = process.env.DEMO_AUTH_SECRET
  return secret && secret.length >= MIN_SECRET_LENGTH ? secret : null
}

function toBase64Url(bytes: Uint8Array): string {
  let binary = ""
  for (const byte of bytes) binary += String.fromCharCode(byte)
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")
}

function fromBase64Url(value: string): Uint8Array<ArrayBuffer> {
  const base64 = value.replace(/-/g, "+").replace(/_/g, "/")
  const binary = atob(base64.padEnd(Math.ceil(base64.length / 4) * 4, "="))
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  return bytes
}

function importKey(secret: string, usage: "sign" | "verify") {
  return crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    [usage]
  )
}

export async function createDemoToken(secret: string): Promise<string> {
  const claims: DemoClaims = {
    sub: "demo-student",
    role: "customer",
    exp: Math.floor(Date.now() / 1000) + DEMO_TTL_SECONDS,
  }
  const payload = toBase64Url(encoder.encode(JSON.stringify(claims)))
  const key = await importKey(secret, "sign")
  const signature = await crypto.subtle.sign(
    "HMAC",
    key,
    encoder.encode(payload)
  )
  return `${payload}.${toBase64Url(new Uint8Array(signature))}`
}

export async function verifyDemoToken(
  token: string | undefined,
  secret: string
): Promise<DemoClaims | null> {
  try {
    if (!token) return null
    const parts = token.split(".")
    if (parts.length !== 2) return null
    const [payload, signature] = parts as [string, string]
    const key = await importKey(secret, "verify")
    const valid = await crypto.subtle.verify(
      "HMAC",
      key,
      fromBase64Url(signature),
      encoder.encode(payload)
    )
    if (!valid) return null
    const claims: unknown = JSON.parse(decoder.decode(fromBase64Url(payload)))
    if (typeof claims !== "object" || claims === null) return null
    const { sub, role, exp } = claims as Record<string, unknown>
    if (
      typeof sub !== "string" ||
      role !== "customer" ||
      typeof exp !== "number" ||
      exp <= Math.floor(Date.now() / 1000)
    ) {
      return null
    }
    return { sub, role, exp }
  } catch {
    return null
  }
}

export async function readDemoSession(
  token: string | undefined
): Promise<DemoClaims | null> {
  const secret = demoAuthSecret()
  return secret ? verifyDemoToken(token, secret) : null
}
