"use client"

import { useEffect } from "react"

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <html lang="en">
      <body
        style={{
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          margin: 0,
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "1rem",
          padding: "1.5rem",
          textAlign: "center",
          background: "rgb(250, 250, 250)",
          color: "rgb(24, 24, 27)",
        }}
      >
        <h1 style={{ fontSize: "1.25rem", fontWeight: 600, margin: 0 }}>
          Something went wrong
        </h1>
        <p
          style={{
            fontSize: "0.875rem",
            margin: 0,
            opacity: 0.75,
            maxWidth: "24rem",
          }}
        >
          A critical error occurred. Please reload the page or try again.
        </p>
        <button
          type="button"
          onClick={() => reset()}
          style={{
            cursor: "pointer",
            borderRadius: "0.375rem",
            padding: "0.5rem 1rem",
            fontSize: "0.875rem",
            fontWeight: 500,
            background: "rgb(24, 24, 27)",
            color: "rgb(255, 255, 255)",
            border: "none",
          }}
        >
          Try again
        </button>
      </body>
    </html>
  )
}
