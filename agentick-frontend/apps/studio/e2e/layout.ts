import { expect, type Page } from "@playwright/test"

/** The page must not scroll sideways: nothing wider than the viewport. */
export async function expectNoHorizontalScroll(page: Page) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - window.innerWidth
  )
  expect(overflow).toBeLessThanOrEqual(0)
}
