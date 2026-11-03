import type { PostgrestError } from "@supabase/supabase-js"

/** Postgres error codes that mean "the request was rejected", as opposed to a bug or an outage. */
const EXPECTED_PG_CODES = new Set(["23505", "23514", "23503", "P0001", "42501"])

/** Error from a Supabase (PostgREST) call: `code` is the Postgres or PostgREST code. */
export class DataError extends Error {
  constructor(
    readonly code: string,
    message: string
  ) {
    super(message)
    this.name = "DataError"
  }

  /** A rule violation the user can act on (duplicate, check, RLS), safe to show in a form. */
  get expected(): boolean {
    return EXPECTED_PG_CODES.has(this.code)
  }
}

/** The request was understood and rejected. Actions return it as a value; anything else is rethrown. */
export function isExpectedDataError(error: unknown): error is DataError {
  return error instanceof DataError && error.expected
}

export function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) return error.message
  return fallback
}

/** Returns `data` or throws: a failed request never becomes an empty result. */
export function unwrap<T>(result: {
  data: T | null
  error: Pick<PostgrestError, "code" | "message"> | null
}): T {
  if (result.error) {
    throw new DataError(result.error.code, result.error.message)
  }
  return result.data as T
}
