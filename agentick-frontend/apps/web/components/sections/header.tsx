import { Button } from "@workspace/ui/components/button"
import { AppLogo } from "@workspace/ui-patterns/app-logo"
import { ThemeToggle } from "@workspace/ui-patterns/theme-toggle"

import { CONTAINER } from "@/config/layout"
import { SIGN_IN_HREF, SIGN_UP_HREF } from "@/config/site"

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className={`${CONTAINER} flex h-14 items-center justify-between`}>
        <AppLogo />
        <nav className="flex items-center gap-2">
          <ThemeToggle />
          <Button
            variant="ghost"
            size="sm"
            render={<a href={SIGN_IN_HREF} />}
            nativeButton={false}
          >
            Sign in
          </Button>
          <Button
            size="sm"
            render={<a href={SIGN_UP_HREF} />}
            nativeButton={false}
          >
            Open Studio
          </Button>
        </nav>
      </div>
    </header>
  )
}
