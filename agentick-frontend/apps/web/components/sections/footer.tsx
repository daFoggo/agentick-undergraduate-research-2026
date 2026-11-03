import Link from "next/link"

import { CONTAINER } from "@/config/layout"
import { REPO_URL, SIGN_IN_HREF } from "@/config/site"

export function Footer() {
  return (
    <footer className="border-t border-border/40 py-10">
      <div className={`${CONTAINER} flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between text-xs font-mono text-muted-foreground`}>
        <div className="flex flex-wrap items-center gap-3">
          <span>© 2026 Next Mono Base</span>
          <span>·</span>
          <span>MIT License</span>
          <span>·</span>
          <Link href="/terms" className="transition-colors hover:text-foreground">
            Terms
          </Link>
          <span>·</span>
          <Link href="/privacy" className="transition-colors hover:text-foreground">
            Privacy
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-foreground"
          >
            GitHub
          </a>
          <a
            href={SIGN_IN_HREF}
            className="transition-colors hover:text-foreground"
          >
            Studio Dashboard
          </a>
        </div>
      </div>
    </footer>
  )
}
