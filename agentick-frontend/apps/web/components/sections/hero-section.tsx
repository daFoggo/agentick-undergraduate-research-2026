import { IconArrowRight, IconBrandGithub } from "@tabler/icons-react"

import { Button } from "@workspace/ui/components/button"
import { CopyCommand } from "@/components/copy-command"
import { REPO_URL, SIGN_IN_HREF } from "@/config/site"

export function HeroSection() {
  return (
    <section className="flex flex-col gap-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center rounded-full border border-border/60 bg-muted/40 px-3 py-1 font-mono text-xs text-foreground/85">
            v0.1.0 · Next.js 16.4
          </span>
          <span className="font-mono text-xs text-muted-foreground">
            Turborepo Starter Base
          </span>
        </div>

        <CopyCommand command="git clone https://github.com/daFoggo/next-mono-base.git" />
      </div>

      <div className="flex flex-col gap-4">
        <h1 className="max-w-4xl text-4xl font-serif leading-[1.12] font-normal tracking-tight sm:text-5xl lg:text-6xl text-balance">
          Build on a solid, production-grade base.
        </h1>
        <p className="max-w-3xl text-lg leading-relaxed text-muted-foreground sm:text-xl font-normal">
          A modular Next.js 16.4 monorepo starter engineered with intentional architecture.
          Choose your preferred auth provider (Keycloak, Better Auth, Supabase, or FastAPI OAuth2),
          build with strict data access boundaries, and pair program with Claude AI under deterministic skill rules.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Button
          size="lg"
          render={<a href={SIGN_IN_HREF} />}
          nativeButton={false}
        >
          <span>Explore Studio Dashboard</span>
          <IconArrowRight className="size-4" />
        </Button>
        <Button
          size="lg"
          variant="outline"
          render={<a href={REPO_URL} target="_blank" rel="noreferrer" />}
          nativeButton={false}
        >
          <IconBrandGithub aria-hidden className="size-4" />
          <span>GitHub Repository</span>
        </Button>
      </div>
    </section>
  )
}
