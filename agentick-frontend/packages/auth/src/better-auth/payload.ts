/**
 * Role vocabulary stored by Better Auth and sent to the base's FastAPI backend: `member` | `admin`. The apps read
 * it through `parseRole`, where `member` (unknown to them) becomes `customer`.
 */
export const BETTER_AUTH_DEFAULT_ROLE = "member"

/** Claims of the JWT minted for FastAPI. */
export function jwtPayload(user: {
  role?: string
  name: string
  email: string
}) {
  return {
    role: user.role ?? BETTER_AUTH_DEFAULT_ROLE,
    name: user.name,
    email: user.email,
  }
}
