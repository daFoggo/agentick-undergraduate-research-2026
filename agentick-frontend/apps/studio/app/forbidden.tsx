import Link from "next/link"
import { IconArrowRight } from "@tabler/icons-react"

import { buttonVariants } from "@workspace/ui/components/button-variants"

import { HOME_PATH } from "@/config/routes"

/**
 * Rendered by `forbidden()` (403), e.g. from `requirePermission` in lib/dal.ts. It renders inside
 * the layouts of the route that threw, so it carries no page frame.
 */
export default function Forbidden() {
  return (
    <div className="flex flex-col items-start gap-5">
      <span className="text-xs font-semibold tracking-widest text-foreground uppercase">
        403 · No access
      </span>
      <h1 className="text-5xl leading-tight font-normal tracking-tighter max-sm:text-4xl">
        You do not have access to this page.
      </h1>
      <p className="max-w-2xl text-muted-foreground">
        Your account has not been granted access to this page. Contact an
        administrator if you think this is a mistake.
      </p>
      <Link
        href={HOME_PATH}
        className={buttonVariants({ size: "lg", className: "group" })}
      >
        Back to home
        <IconArrowRight
          data-icon="inline-end"
          aria-hidden
          className="motion-safe:transition-transform motion-safe:duration-200 motion-safe:ease-out motion-safe:group-hover:translate-x-1"
        />
      </Link>
    </div>
  )
}
