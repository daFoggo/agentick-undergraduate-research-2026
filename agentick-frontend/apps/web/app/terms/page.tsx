import type { Metadata } from "next"
import Link from "next/link"
import { IconArrowLeft, IconScale, IconAlertTriangle } from "@tabler/icons-react"

import { Button } from "@workspace/ui/components/button"
import { AppLogo } from "@workspace/ui-patterns/app-logo"
import { ThemeToggle } from "@workspace/ui-patterns/theme-toggle"

import { CONTAINER } from "@/config/layout"
import { SIGN_IN_HREF, SIGN_UP_HREF } from "@/config/site"

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "Terms of Service and developer agreement for Next Mono Base.",
}

export default function TermsOfServicePage() {
  return (
    <>
      {/* Sticky navigation header */}
      <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-md">
        <div className={`${CONTAINER} flex h-14 items-center justify-between`}>
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="group flex items-center gap-1.5 font-mono text-xs text-muted-foreground transition-colors hover:text-foreground"
            >
              <IconArrowLeft className="size-4 transition-transform motion-safe:group-hover:-translate-x-0.5" />
              <span>Back</span>
            </Link>
            <AppLogo />
          </div>
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

      <main className={`${CONTAINER} py-12 sm:py-16`}>
        <article className="mx-auto flex max-w-3xl flex-col gap-10">
          {/* Header */}
          <div className="flex flex-col gap-3 border-b border-border/40 pb-8">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 rounded-full border border-border/60 bg-muted/40 px-2.5 py-0.5 font-mono text-xs text-foreground/80">
                <IconScale className="size-3.5 text-primary" />
                Legal Agreement
              </span>
              <span className="font-mono text-xs text-muted-foreground">
                Last updated: January 1, 2026
              </span>
            </div>
            <h1 className="text-3xl font-medium tracking-tight text-foreground sm:text-4xl">
              Terms of Service
            </h1>
            <p className="text-base text-muted-foreground leading-relaxed">
              These Terms of Service (&ldquo;Terms&rdquo;) govern your access to and use of Next Mono Base,
              including the web landing site, studio dashboard, and associated software packages. By creating
              an account or continuing to use our services, you agree to be bound by these Terms.
            </p>
          </div>

          {/* Section 1: Open Source & License */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">1. Open Source License and Codebase</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              The underlying Next Mono Base repository and architecture starter code are licensed under the MIT License.
              You are free to use, modify, and distribute the template code for personal or commercial projects, subject
              to the inclusion of the original copyright notice and permission notice.
            </p>
          </section>

          {/* Section 2: User Accounts */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">2. User Accounts and Security</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              When creating an account through our dashboard, you agree to:
            </p>
            <ul className="list-disc space-y-1.5 pl-5 text-sm text-muted-foreground leading-relaxed">
              <li>Provide accurate, current, and complete registration information.</li>
              <li>Maintain the confidentiality and security of your authentication credentials.</li>
              <li>Promptly notify us of any suspected breach of security or unauthorized access.</li>
              <li>Accept responsibility for all activities occurring under your account or credentials.</li>
            </ul>
          </section>

          {/* Section 3: Acceptable Use */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">3. Acceptable Use Policy</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              You agree not to misuse the platform or assist others in doing so. Specifically, you agree not to:
            </p>
            <div className="flex flex-col gap-2 rounded-lg border border-border/50 bg-muted/10 p-4 text-xs text-muted-foreground">
              <div className="flex items-start gap-2">
                <IconAlertTriangle className="size-4 shrink-0 text-amber-500 mt-0.5" />
                <span>Violate applicable local, national, or international regulations, including the Law on Cybersecurity and Personal Data Protection Law.</span>
              </div>
              <div className="flex items-start gap-2">
                <IconAlertTriangle className="size-4 shrink-0 text-amber-500 mt-0.5" />
                <span>Attempt to bypass authentication, reverse engineer rate limits, or probe security boundaries without explicit authorization.</span>
              </div>
              <div className="flex items-start gap-2">
                <IconAlertTriangle className="size-4 shrink-0 text-amber-500 mt-0.5" />
                <span>Engage in denial-of-service, automated credential scraping, or unauthorized cross-tenant data access.</span>
              </div>
            </div>
          </section>

          {/* Section 4: Multi-Tenant Workspace Rules */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">4. Multi-Tenant Workspace &amp; Resources</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Organizations and projects created within the Studio dashboard are isolated per user token and organization tenant.
              You maintain ownership of all project configurations and data created within your workspace. We reserve the right to
              suspend or prune demo resources that remain inactive for extended durations.
            </p>
          </section>

          {/* Section 5: Limitation of Liability */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">5. Limitation of Liability and Disclaimers</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              The software and services are provided &ldquo;AS IS&rdquo;, without warranty of any kind, express or implied.
              In no event shall Next Mono Base or its authors be liable for any direct, indirect, incidental, or consequential
              damages arising from the use or inability to use the software.
            </p>
          </section>

          {/* Section 6: Termination & Erasure */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">6. Termination and Account Erasure</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              You may terminate these Terms at any time by deleting your account from the Studio Settings. We reserve the right
              to suspend or terminate accounts that breach these Terms. Upon termination, data erasure will be carried out in
              accordance with our Privacy Policy.
            </p>
          </section>

          {/* Section 7: Governing Law */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">7. Governing Law</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              These Terms shall be governed by and construed in accordance with applicable laws, without giving effect to any
              principles of conflicts of law.
            </p>
          </section>
        </article>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-10">
        <div className={`${CONTAINER} flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between text-xs font-mono text-muted-foreground`}>
          <div className="flex items-center gap-3">
            <span>© 2026 Next Mono Base</span>
            <span>·</span>
            <span className="text-foreground font-medium">Terms of Service</span>
            <span>·</span>
            <Link href="/privacy" className="transition-colors hover:text-foreground">
              Privacy Policy
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <a href="https://github.com/daFoggo/next-mono-base" target="_blank" rel="noreferrer" className="transition-colors hover:text-foreground">
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </>
  )
}
