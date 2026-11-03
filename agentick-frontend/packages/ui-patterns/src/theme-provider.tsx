"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

import { AnimateUIProvider } from "@workspace/ui/provider"

/** Light first (a furniture store reads on white); dark is complete and follows the system. */
function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="light"
      enableSystem
      disableTransitionOnChange
      {...props}
    >
      <AnimateUIProvider>{children}</AnimateUIProvider>
    </NextThemesProvider>
  )
}

export { ThemeProvider }
