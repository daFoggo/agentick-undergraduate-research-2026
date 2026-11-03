import { describe, expect, it } from "vitest"

import {
  DataError,
  getErrorMessage,
  isExpectedDataError,
  unwrap,
} from "../errors"

describe("DataError", () => {
  it("treats rule violations as expected", () => {
    expect(new DataError("23505", "dup").expected).toBe(true)
    expect(new DataError("42501", "rls").expected).toBe(true)
  })

  it("treats auth and unknown errors as unexpected", () => {
    expect(new DataError("PGRST301", "jwt").expected).toBe(false)
  })
})

describe("isExpectedDataError", () => {
  it("rejects plain errors", () => {
    expect(isExpectedDataError(new Error("x"))).toBe(false)
  })

  it("accepts expected data errors", () => {
    expect(isExpectedDataError(new DataError("23514", "check"))).toBe(true)
  })
})

describe("getErrorMessage", () => {
  it("falls back when the message is empty", () => {
    expect(getErrorMessage(new Error(""), "fallback")).toBe("fallback")
  })
})

describe("unwrap", () => {
  it("returns data when there is no error", () => {
    expect(unwrap({ data: [1, 2], error: null })).toEqual([1, 2])
  })

  it("throws a DataError carrying the Postgres code", () => {
    const error = { code: "23505", message: "duplicate key" }
    expect(() => unwrap({ data: null, error })).toThrow(DataError)
    try {
      unwrap({ data: null, error })
    } catch (caught) {
      expect((caught as DataError).code).toBe("23505")
    }
  })
})
