import type { Metadata } from "next"
import Link from "next/link"
import { IconArrowLeft, IconShieldCheck, IconClock, IconFileCheck } from "@tabler/icons-react"

import { Button } from "@workspace/ui/components/button"
import { AppLogo } from "@workspace/ui-patterns/app-logo"
import { ThemeToggle } from "@workspace/ui-patterns/theme-toggle"

import { CONTAINER } from "@/config/layout"
import { SIGN_IN_HREF, SIGN_UP_HREF } from "@/config/site"

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Privacy Policy and personal data protection principles for Next Mono Base.",
}

export default function PrivacyPolicyPage() {
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
                <IconShieldCheck className="size-3.5 text-emerald-500" />
                Compliance Standard 2026
              </span>
              <span className="font-mono text-xs text-muted-foreground">
                Effective: January 1, 2026
              </span>
            </div>
            <h1 className="text-3xl font-medium tracking-tight text-foreground sm:text-4xl">
              Privacy Policy &amp; Data Protection
            </h1>
            <p className="text-base text-muted-foreground leading-relaxed">
              This Privacy Policy explains how Next Mono Base (&ldquo;we&rdquo;, &ldquo;us&rdquo;, or &ldquo;our&rdquo;)
              collects, processes, protects, and retains your personal data in accordance with applicable data
              protection laws, including the Personal Data Protection Law (Law No. 91/2025/QH15) and Decree No. 356/2025/ND-CP,
              as well as international standards (GDPR and CCPA).
            </p>
          </div>

          {/* Section 1: Data Controller */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">1. Data Controller and Contact Information</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Next Mono Base operates as the data controller for personal data processed through our website and studio dashboard.
              If you have any questions, requests, or concerns regarding your privacy or this policy, you may reach our Data Protection Officer (DPO) at:
            </p>
            <div className="rounded-lg border border-border/50 bg-muted/20 p-4 font-mono text-xs text-foreground/90">
              <p>Organization: Next Mono Base Engineering</p>
              <p>Email: privacy@next-mono-base.local</p>
              <p>Support: security@next-mono-base.local</p>
            </div>
          </section>

          {/* Section 2: Data We Collect */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">2. Categories of Personal Data Collected</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              We collect only the minimum necessary data to provide secure authentication, workspace organization, and developer services:
            </p>
            <ul className="list-disc space-y-2 pl-5 text-sm text-muted-foreground leading-relaxed">
              <li>
                <strong className="text-foreground font-medium">Account &amp; Profile Information:</strong> Full name, email address,
                and securely hashed passwords (argon2/bcrypt). We never store plaintext passwords.
              </li>
              <li>
                <strong className="text-foreground font-medium">Authentication &amp; Session Identifiers:</strong> Access tokens,
                session cookies (<code className="font-mono text-xs">nmb-studio-auth.access</code>, <code className="font-mono text-xs">SameSite=Lax</code>),
                and IP addresses required for session binding and defense against token theft.
              </li>
              <li>
                <strong className="text-foreground font-medium">Workspace &amp; Project Metadata:</strong> Organization slugs,
                project identifiers, and audit logs of configuration changes.
              </li>
            </ul>
          </section>

          {/* Section 3: Purposes and Legal Grounds */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">3. Purposes and Legal Bases for Processing</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              In compliance with Article 9 of Law No. 91/2025/QH15 and GDPR Article 6, we process data only on clear legal grounds:
            </p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-border/50 bg-muted/10 p-4">
                <span className="font-medium text-xs text-foreground uppercase tracking-wider font-mono">Performance of Contract</span>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                  Provisioning user accounts, authenticating sessions across Keycloak/Supabase/Better Auth, and managing workspace resources.
                </p>
              </div>
              <div className="rounded-lg border border-border/50 bg-muted/10 p-4">
                <span className="font-medium text-xs text-foreground uppercase tracking-wider font-mono">Explicit Consent</span>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                  Affirmatively provided when registering an account. Silence or pre-ticked checkboxes are never deemed consent.
                </p>
              </div>
              <div className="rounded-lg border border-border/50 bg-muted/10 p-4">
                <span className="font-medium text-xs text-foreground uppercase tracking-wider font-mono">Legitimate Interests</span>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                  Protecting systems from denial-of-service, enforcing rate limits, preventing CSRF attacks, and detecting security breaches.
                </p>
              </div>
              <div className="rounded-lg border border-border/50 bg-muted/10 p-4">
                <span className="font-medium text-xs text-foreground uppercase tracking-wider font-mono">Statutory Compliance</span>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                  Adhering to cybersecurity recordkeeping, regulatory investigations, and lawful audit requirements.
                </p>
              </div>
            </div>
          </section>

          {/* Section 4: Cross-Border Transfers */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">4. Cross-Border Data Transfers</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              When utilizing cloud-hosted infrastructure (such as AWS, Vercel, Supabase, or external OAuth providers),
              personal data may be transferred to or processed on secure servers located outside Vietnam. In accordance with
              Article 20 of Law No. 91/2025/QH15, we enforce strict standard contractual clauses (SCCs) and robust cryptographic
              safeguards ensuring transferred data receives the same level of legal protection as domestic processing.
            </p>
          </section>

          {/* Section 5: Cookies and Tracking */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">5. Cookies and Technical Tracking</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              We do not employ invasive third-party advertising or behavioral profiling cookies. We only use strictly necessary technical cookies:
            </p>
            <ul className="list-disc space-y-1.5 pl-5 text-sm text-muted-foreground leading-relaxed">
              <li>Session authentication cookies tagged with <code className="font-mono text-xs">HttpOnly</code>, <code className="font-mono text-xs">Secure</code>, and <code className="font-mono text-xs">SameSite=Lax</code>.</li>
              <li>User theme preference stored in client-side storage (<code className="font-mono text-xs">theme</code>).</li>
            </ul>
          </section>

          {/* Section 6: User Rights & Concrete SLA (Key compliance item) */}
          <section className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <IconClock className="size-4 text-primary" />
              <h2 className="text-xl font-medium text-foreground">6. Your Rights and Statutory Response Timelines</h2>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Under Article 4 of Law No. 91/2025/QH15 and Decree No. 356/2025/ND-CP, you hold fundamental rights over your data.
              We commit to the following concrete response service-level agreements (SLAs):
            </p>
            <div className="flex flex-col divide-y divide-border/40 rounded-lg border border-border/50 bg-muted/10 font-mono text-xs">
              <div className="flex items-center justify-between p-3.5">
                <span className="text-foreground">Acknowledgement of Receipt</span>
                <span className="font-medium text-emerald-600 dark:text-emerald-400">Within 2 business days</span>
              </div>
              <div className="flex items-center justify-between p-3.5">
                <span className="text-foreground">Right to Access, Inspect &amp; Correct Data</span>
                <span className="font-medium text-emerald-600 dark:text-emerald-400">Within 10 business days</span>
              </div>
              <div className="flex items-center justify-between p-3.5">
                <span className="text-foreground">Withdrawal of Consent &amp; Restriction of Processing</span>
                <span className="font-medium text-emerald-600 dark:text-emerald-400">Within 15 business days</span>
              </div>
              <div className="flex items-center justify-between p-3.5">
                <span className="text-foreground">Right to Erasure (Complete Account Deletion)</span>
                <span className="font-medium text-emerald-600 dark:text-emerald-400">Within 20 business days</span>
              </div>
            </div>
          </section>

          {/* Section 7: Account Deletion */}
          <section className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <IconFileCheck className="size-4 text-primary" />
              <h2 className="text-xl font-medium text-foreground">7. Account Deletion and Data Retention</h2>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              You may initiate account deletion directly from your Studio Dashboard Settings under the &ldquo;Danger Zone&rdquo; section,
              or by submitting a written request to <code className="font-mono text-xs">privacy@next-mono-base.local</code>. Upon confirmation,
              all personal data, active tokens, and workspace associations will be irreversibly purged within 20 business days.
            </p>
          </section>

          {/* Section 8: AI Transparency & Processing (Law 134/2025/QH15) */}
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-medium text-foreground">8. AI Transparency and Automated Processing</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              In compliance with Vietnam&apos;s Law on Artificial Intelligence (Law No. 134/2025/QH15) and Decree No. 142/2026/ND-CP:
            </p>
            <ul className="list-disc space-y-1.5 pl-5 text-sm text-muted-foreground leading-relaxed">
              <li>
                <strong className="text-foreground">AI Role &amp; Disclosure:</strong> Any AI-powered telemetry analysis, code assistance,
                or automated reporting tools are explicitly labeled. Interactive AI features identify themselves as automated systems and not human operators.
              </li>
              <li>
                <strong className="text-foreground">Human-in-the-Loop:</strong> Critical system administration, account lifecycle terminations,
                and security revocations always require explicit human operator confirmation and are never delegated to unmonitored autonomous models.
              </li>
              <li>
                <strong className="text-foreground">Training Data Safeguards:</strong> Customer workspace telemetry and user credentials are never used
                for public AI model training or shared with external model vendors without explicit affirmative consent.
              </li>
            </ul>
          </section>
        </article>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-10">
        <div className={`${CONTAINER} flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between text-xs font-mono text-muted-foreground`}>
          <div className="flex items-center gap-3">
            <span>© 2026 Next Mono Base</span>
            <span>·</span>
            <Link href="/terms" className="transition-colors hover:text-foreground">
              Terms of Service
            </Link>
            <span>·</span>
            <span className="text-foreground font-medium">Privacy Policy</span>
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
