import { DataError } from "@workspace/db/errors"

/** Error thrown when the backend answers with a non-2xx status. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly body?: unknown
  ) {
    super(message)
    this.name = "ApiError"
  }
}

/** Supabase (PostgREST) errors come from `@workspace/db` (`unwrap`); one class for both paths. */
export { DataError }

/**
 * The request was understood and rejected (validation, conflict, rule) on either data path: a backend `4xx`
 * or an expected Postgres code. Actions return it as a value. Anything else, including Next's
 * `redirect()`/`notFound()` signals, must be rethrown.
 */
export function isExpectedDataError(
  error: unknown
): error is ApiError | DataError {
  if (error instanceof DataError) return error.expected
  return error instanceof ApiError && error.status >= 400 && error.status < 500
}

/** The spec rule that refused a write (e.g. `TM-2`), from the problem details or the message prefix. */
export function ruleOf(error: ApiError | DataError): string | undefined {
  if (
    error instanceof ApiError &&
    error.body &&
    typeof error.body === "object" &&
    "rule" in error.body
  ) {
    return String(error.body.rule)
  }
  return /^([A-Z]{2}-\d+):/.exec(error.message)?.[1]
}

export function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) return error.message
  return fallback
}
