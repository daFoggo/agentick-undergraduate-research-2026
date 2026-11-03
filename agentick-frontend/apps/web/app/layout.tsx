import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { GeistSerif } from "geist/font/serif"
import { GeistPixelGrid, GeistPixelSquare } from "geist/font/pixel"

import "@workspace/ui/globals.css"
import { ThemeProvider } from "@workspace/ui-patterns/theme-provider"
import { cn } from "@workspace/ui/lib/utils"
import { publicEnv } from "@/lib/env.public"

export const metadata: Metadata = {
  // Makes relative canonicals (`/some/path`) absolute.
  metadataBase: new URL(publicEnv.NEXT_PUBLIC_APP_URL),
  title: {
    default: "Next Mono Base",
    template: "%s | Next Mono Base",
  },
  description:
    "A Next.js monorepo base: auth, data, UI kit and conventions ready to build on.",
}

// Map Geist's own variables onto the theme tokens the UI kit reads.
const FONT_VARS = {
  "--font-sans": "var(--font-geist-sans)",
  "--font-mono": "var(--font-geist-mono)",
  "--font-serif": "var(--font-geist-serif)",
  "--font-pixel-square": "var(--font-geist-pixel-square)",
  "--font-pixel-grid": "var(--font-geist-pixel-grid)",
} as React.CSSProperties

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      style={FONT_VARS}
      className={cn(
        "antialiased",
        "font-sans",
        GeistSans.variable,
        GeistMono.variable,
        GeistSerif.variable,
        GeistPixelSquare.variable,
        GeistPixelGrid.variable
      )}
    >
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
