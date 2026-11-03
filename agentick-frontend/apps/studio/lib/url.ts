/**
 * Joins a base URL (which may carry a path such as `/api/v1`) with a relative path.
 * `new URL("auth/sign-in", "https://host/api/v1")` would drop `v1`, so the base is
 * forced to end with a slash first.
 */
export function apiUrl(base: string, path: string): URL {
  const normalizedBase = base.endsWith("/") ? base : `${base}/`
  return new URL(path.replace(/^\//, ""), normalizedBase)
}
