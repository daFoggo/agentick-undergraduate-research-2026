"use client"

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@workspace/ui/components/accordion"

const FAQS = [
  {
    id: "pluggable-auth",
    question: "How do I switch between Keycloak, Better Auth, and Supabase?",
    answer:
      "All three providers are normalized behind the unified AuthProvider interface in @workspace/auth. Set AUTH_PROVIDER in apps/studio/.env.local (e.g. keycloak, better-auth, or supabase). Server actions, proxy session refreshes, and getSession() calls remain 100% identical without changing any application code.",
  },
  {
    id: "tanstack-redact",
    question: "How does TanStack Redact work with Next.js 16 Server Components?",
    answer:
      "Both apps wrap next.config.ts with withRedact from @tanstack/redact/next. Next.js keeps native React 19.3 on the server for Server Components, Flight serialization, 'use cache', and Server Actions, while Turbopack swaps browser React/DOM entrypoints to Redact's synchronous runtime—cutting the client DOM runtime chunk by ~58% gzip (~35 KB total client JS saved) with zero changes to component imports.",
  },
  {
    id: "cache-components",
    question: "How does Next.js 16 Cache Components and Partial Prerendering (PPR) work?",
    answer:
      "apps/studio has cacheComponents and partialPrefetching enabled in next.config.ts. Dynamic runtime APIs (cookies(), headers(), searchParams) are isolated inside <Suspense> boundaries, allowing layouts and static shells to prerender instantly while data fetching uses 'use cache' and cacheLife directives for per-user and shared caching.",
  },
  {
    id: "data-access-layer",
    question: "What is the Data Access Layer (DAL) and why does it matter?",
    answer:
      "The DAL resides in features/*/queries.ts and lib/auth.ts. It guarantees strict server-only boundaries so that database credentials, JWT secrets, and Keycloak client secrets never leak into client bundles. Every mutation goes through validated Server Actions with Zod schemas.",
  },
  {
    id: "pruning-providers",
    question: "Can I use only one provider and prune the others if I don't need them?",
    answer:
      "Yes. Each provider is completely isolated in packages/auth/src/{keycloak,better-auth,supabase}/. If your team only uses Keycloak or Supabase, the other submodules remain inactive unless configured in your environment.",
  },
  {
    id: "ai-workflows",
    question: "How is this starter base optimized for Claude AI and coding agents?",
    answer:
      "The repository contains strict AGENTS.md rules, exhaustive docs/ architecture guides, and Antigravity/Claude AI skill definitions. AI agents automatically read these rules to generate code that adheres to monorepo boundaries, zero-shadow design system tokens, and strict type safety without hallucination.",
  },
]

export function ArchitectureFaq() {
  return (
    <Accordion className="border-t border-border/40">
      {FAQS.map((faq) => (
        <AccordionItem key={faq.id} value={faq.id} className="border-b border-border/40 py-1">
          <AccordionTrigger className="text-left font-medium text-sm text-foreground hover:no-underline">
            {faq.question}
          </AccordionTrigger>
          <AccordionContent className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
            {faq.answer}
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  )
}
