import { createElement } from "react"
import { renderToStaticMarkup } from "react-dom/server"
import { describe, expect, it } from "vitest"

import RootError from "../error"
import AuthError from "../(auth)/error"
import NotFound from "../not-found"
import GlobalError from "../global-error"

describe("boundaries", () => {
  it("root error renders English copy and retry button", () => {
    const html = renderToStaticMarkup(
      createElement(RootError, {
        error: new Error("test"),
        retry: () => {},
      })
    )
    expect(html).toContain("Something went wrong")
    expect(html).toContain("Try again")
  })

  it("auth error renders English copy and retry button", () => {
    const html = renderToStaticMarkup(
      createElement(AuthError, {
        error: new Error("test"),
        retry: () => {},
      })
    )
    expect(html).toContain("Something went wrong")
    expect(html).toContain("Try again")
  })

  it("not-found renders English copy and links home", () => {
    const html = renderToStaticMarkup(createElement(NotFound))
    expect(html).toContain("Page not found")
    expect(html).toContain('href="/"')
  })

  it("global error renders English copy, lang=en, and retry button", () => {
    const html = renderToStaticMarkup(
      createElement(GlobalError, {
        error: new Error("test"),
        reset: () => {},
      })
    )
    expect(html).toContain('lang="en"')
    expect(html).toContain("Something went wrong")
    expect(html).toContain("Try again")
    expect(html).not.toContain("Application error")
    expect(html.includes("dark" + ":")).toBe(false)
    expect(html).not.toContain("text-gray-500")
  })
})
