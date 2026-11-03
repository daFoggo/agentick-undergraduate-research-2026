import type { Page } from "@playwright/test"

/**
 * Console noise that is not an app bug: `next start` over http://localhost prefetches links to pages
 * that are not built yet (/blog, /ve-chung-toi, /lien-he, /gio-hang answer 404), and the CSP
 * `upgrade-insecure-requests` makes some sub-requests fail with ERR_SSL_PROTOCOL_ERROR on plain http.
 * Anything else (hydration errors such as React #418 included) must fail the test.
 */
const KNOWN_NOISE = [/ERR_SSL_PROTOCOL_ERROR/]

export function collectConsoleErrors(page: Page): string[] {
  const errors: string[] = []
  const keep = (text: string, url = "") => {
    if (!KNOWN_NOISE.some((re) => re.test(`${text} ${url}`))) errors.push(text)
  }
  page.on("console", (m) => {
    if (m.type() === "error") keep(m.text(), m.location().url)
  })
  page.on("pageerror", (e) => keep(e.message))
  return errors
}
