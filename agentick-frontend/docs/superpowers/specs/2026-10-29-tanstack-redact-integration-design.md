# TanStack Redact Integration & Base Showcase Update — Design Specification

- **Date:** 2026-10-29
- **Status:** Draft (Pending Approval)
- **Scope:** `apps/studio`, `apps/web`, `packages/ui-patterns`, `docs/`, `README.md`

---

## 1. Intent and Why

`next-mono-base` is a production-grade Next.js 16.4 monorepo starter (`apps/studio` dashboard and `apps/web` marketing landing page) built on a **Server-First** architecture (`cacheComponents: true`, `partialPrefetching: true`, React Server Components, and Server Actions).

Because data fetching, caching, and business logic already live on the server, the browser only needs to hydrate interactive islands, forms, and UI primitives. Integrating **TanStack Redact** (`@tanstack/redact/next`) lets Next.js keep native **React 19.3 on the server** (for RSC, Flight payloads, `"use cache"`, and Server Actions) while replacing the heavy concurrent-scheduler client runtime in the browser with Redact's lightweight **synchronous rendering engine** (~27.9 KB gzip full client runtime vs. ~69.2 KB gzip in React 19.3).

We will also measure the exact before/after client bundle footprint on both apps in this monorepo and update the base introduction (`StackGrid`, landing page sections, FAQ, and docs) to showcase TanStack Redact with its official `svgl` icon and real measured metrics.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
1. **Standards-Compliant Next.js Integration (`@tanstack/redact/next`):**
   - Add `@tanstack/redact` (`^0.2.3`) to `apps/studio/package.json` and `apps/web/package.json` while keeping `react@19.3.0` and `react-dom@19.3.0` installed.
   - Wrap `nextConfig` with `withRedact` from `@tanstack/redact/next` in both `apps/studio/next.config.ts` and `apps/web/next.config.ts` (enabled by default, with `process.env.DISABLE_REDACT === "1"` opt-out for A/B benchmarking and debugging).
   - Keep all component imports (`react`, `react-dom`, `next/*`) and `tsconfig.json` (`jsxImportSource`) untouched as required by the official Next.js adapter documentation.
2. **Quantitative Before/After Benchmarking:**
   - Measure both `apps/web` and `apps/studio` production builds (`next build` with Turbopack) before and after enabling `withRedact`:
     - Total client JS size across `.next/static/chunks/*.js` (raw bytes & gzip bytes).
     - Largest framework/runtime chunk sizes (raw & gzip).
     - Build duration and full verification pass (`pnpm check`: ESLint, TypeScript, Vitest).
3. **Base Introduction & Showcase Updates:**
   - **`packages/ui-patterns`**:
     - Add `IconTanstack` (official SVG from `svgl.app` using `fill="currentColor"`) to `packages/ui-patterns/src/stack-icons.tsx`.
     - Add `{ name: "TanStack Redact", category: "frontend", Icon: IconTanstack }` to `STACK_ITEMS` in `packages/ui-patterns/src/stack-grid.tsx`, expanding the grid to **16 technologies** arranged in `grid-cols-2 sm:grid-cols-4` (4×4 on desktop, 2×8 on mobile—eliminating the odd 15th orphan cell on 2-column mobile layouts).
   - **`apps/web` Landing Page (`apps/web/app/page.tsx` & `apps/web/components/architecture-faq.tsx`)**:
     - Update the Supported Ecosystem counter from `15` to `16` technologies.
     - Update `ARCHITECTURE_CHAPTERS` and `PILLARS` to highlight the **Hybrid React Server + TanStack Redact Browser Runtime** architecture and include the measured client bundle reduction.
     - Add an FAQ entry in `apps/web/components/architecture-faq.tsx` explaining how `@tanstack/redact/next` works alongside Next.js 16.4 Cache Components and RSC.
   - **Documentation (`README.md` & `docs/performance-optimization.md`)**:
     - Document the `withRedact` setup, compatibility guarantees (`use()`, `<Suspense>`, `<Activity>`, `useActionState`), synchronous rendering trade-offs, A/B toggle (`DISABLE_REDACT=1`), and measured bundle savings in `docs/performance-optimization.md` and `README.md`.

### Non-Goals
- Rewriting any existing React components, hooks, or imports to `@tanstack/redact`.
- Changing `jsxImportSource` in `tsconfig.json` (forbidden by `@tanstack/redact/next` docs because the server requires React's native JSX runtime).
- Using Vite-only feature-flag presets (`nano` preset does not apply to Next.js, which uses the full Redact client runtime).

### Anti-Goals
- Breaking Server Components, Flight serialization, `"use cache"`, `<Activity>`, or Animate UI / Motion primitives.
- Introducing arbitrary Tailwind values or violating `.agents/skills/design-system/SKILL.md` rules in `packages/ui-patterns` or `apps/web`.

---

## 3. Constraints

1. **Next.js Version Pinning in `@tanstack/redact/next`:**
   - `withRedact` validates `next/package.json` against `/^(?:15\.5|16\.[0-4])\.\d+$/`. Both apps use `next@16.4.2`, which passes validation cleanly.
2. **Monorepo Dependency Placement (`AGENTS.md`):**
   - Dependencies go in the package that uses them (`apps/studio` and `apps/web`), never in the workspace root.
3. **Design System Compliance (`docs/design-system.md`):**
   - No arbitrary Tailwind values (`-[...]`), minimum text size `text-xs`, hairline borders (`border-border/40`), and adaptive monochrome icons (`currentColor`) in `StackGrid`.

---

## 4. Approaches Considered

### Approach 1 (Selected): Default `withRedact` with `DISABLE_REDACT=1` A/B Toggle + 16-Item `StackGrid` (`4×4` Desktop / `2×8` Mobile)
- **Description:** Enable `withRedact(nextConfig)` by default in both `apps/studio` and `apps/web` with an environment variable escape hatch (`DISABLE_REDACT=1`) for reproducible A/B measurements. Expand `StackGrid` from 15 to 16 items (`grid-cols-2 sm:grid-cols-4`) using the `svgl` TanStack logo (`IconTanstack`).
- **Trade-offs:** Preserves all 15 existing stack items, makes the grid symmetric on both mobile (2 cols × 8 rows) and desktop (4 cols × 4 rows), and allows instant A/B build comparisons at any time.

### Approach 2: Hardcoded `withRedact` + 15-Item `StackGrid` Replacement
- **Description:** Wrap `withRedact(nextConfig)` unconditionally and replace one existing item in `StackGrid` to keep 15 items (`5×3`).
- **Trade-offs:** Drops an existing showcased technology and requires editing config files whenever comparing native React vs. Redact builds.

---

## 5. Detailed Design

### 5.1 Next.js Configuration (`apps/studio/next.config.ts` & `apps/web/next.config.ts`)
```ts
import { withRedact } from "@tanstack/redact/next"
// ...
export default process.env.DISABLE_REDACT === "1"
  ? nextConfig
  : withRedact(nextConfig)
```

### 5.2 Stack Icon & Grid (`packages/ui-patterns/src/stack-icons.tsx` & `stack-grid.tsx`)
- Add `IconTanstack` to `packages/ui-patterns/src/stack-icons.tsx` using the `svgl.app` vector (`viewBox="0 0 64.04 83.84"`, `fill="currentColor"`).
- Add `{ name: "TanStack Redact", category: "frontend", Icon: IconTanstack }` to `STACK_ITEMS` in `packages/ui-patterns/src/stack-grid.tsx`.
- Update `StackGrid` grid columns to `grid-cols-2 sm:grid-cols-4` so 16 items form 4 balanced rows of 4 on `sm+` viewports and 8 balanced rows of 2 on mobile viewports.

### 5.3 Landing Page & Documentation Updates
- Update `apps/web/app/page.tsx`:
  - `CountingNumber` in Supported Ecosystem: `15` $\rightarrow$ `16`.
  - Add/update chapter in `ARCHITECTURE_CHAPTERS` and pillar details with the measured client JS gzip savings.
- Update `apps/web/components/architecture-faq.tsx` with a dedicated Q&A on **Why TanStack Redact in the browser with React 19 on the server?**.
- Update `docs/performance-optimization.md` (new section on **Browser Runtime Optimization with TanStack Redact (`@tanstack/redact/next`)** with the benchmark table) and `README.md`.
