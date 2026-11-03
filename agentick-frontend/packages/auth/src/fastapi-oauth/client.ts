export type FastApiTokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
}

/** Thrown for a 4xx the backend returned (wrong password, duplicate email, ...): safe to show in a form. */
export class FastApiAuthError extends Error {
  constructor(
    readonly status: number,
    message: string
  ) {
    super(message)
    this.name = "FastApiAuthError"
  }
}

/** `base` may or may not carry a path; forced to end with `/` so `new URL` doesn't drop it. */
function url(base: string, path: string): string {
  const normalizedBase = base.endsWith("/") ? base : `${base}/`
  return new URL(path.replace(/^\//, ""), normalizedBase).toString()
}

async function parseErrorDetail(res: Response): Promise<string> {
  const body = await res.json().catch(() => undefined)
  if (body && typeof body === "object" && "detail" in body) {
    const { detail } = body as { detail: unknown }
    if (typeof detail === "string") return detail
    if (Array.isArray(detail) && detail[0] && typeof detail[0] === "object") {
      const first = detail[0] as { msg?: unknown }
      if (typeof first.msg === "string") return first.msg
    }
  }
  return `Request failed with status ${res.status}`
}

export async function registerUser(
  apiBaseUrl: string,
  input: { email: string; password: string; name: string }
): Promise<void> {
  const res = await fetch(url(apiBaseUrl, "/api/v1/auth/register"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  })
  if (!res.ok) {
    throw new FastApiAuthError(res.status, await parseErrorDetail(res))
  }
}

export async function loginUser(
  apiBaseUrl: string,
  credentials: { email: string; password: string }
): Promise<FastApiTokenResponse> {
  const res = await fetch(url(apiBaseUrl, "/api/v1/auth/token"), {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      username: credentials.email,
      password: credentials.password,
    }),
  })
  if (!res.ok) {
    throw new FastApiAuthError(res.status, await parseErrorDetail(res))
  }
  return (await res.json()) as FastApiTokenResponse
}

export async function refreshTokens(
  apiBaseUrl: string,
  refreshToken: string
): Promise<FastApiTokenResponse> {
  const res = await fetch(url(apiBaseUrl, "/api/v1/auth/refresh"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
  if (!res.ok) {
    throw new FastApiAuthError(res.status, await parseErrorDetail(res))
  }
  return (await res.json()) as FastApiTokenResponse
}
