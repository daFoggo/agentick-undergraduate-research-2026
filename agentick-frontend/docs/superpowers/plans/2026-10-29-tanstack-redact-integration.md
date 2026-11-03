# TanStack Redact Integration & Base Showcase Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate `@tanstack/redact/next` (`withRedact`) into both `apps/studio` and `apps/web`, measure before/after client bundle footprints, and update the base introduction (`StackGrid` with the `svgl` TanStack logo, landing page sections, FAQ, and docs) with measured metrics.

**Architecture:** Keep native React 19.3 on the server for React Server Components, Flight payloads, `"use cache"`, and Server Actions while swapping browser runtime entrypoints to TanStack Redact via `withRedact` in `next.config.ts` (with `DISABLE_REDACT=1` opt-out for reproducible A/B benchmarks). Expand `StackGrid` in `@workspace/ui-patterns` to 16 technologies (`grid-cols-2 sm:grid-cols-4`) with `IconTanstack`.

**Tech Stack:** Next.js 16.4.2, `@tanstack/redact` (`^0.2.3`), React 19.3.0, Turborepo, pnpm, Tailwind CSS v4.

**Spec:** `docs/superpowers/specs/2026-10-29-tanstack-redact-integration-design.md`

## Global Constraints

- `withRedact` supports stable Next.js 15.5 and 16.0 through 16.4 (`next@16.4.2` in both apps).
- Keep `react` and `react-dom` installed; do not modify component imports or `jsxImportSource` in `tsconfig.json`.
- Dependencies go in `apps/studio/package.json` and `apps/web/package.json`, never in root `package.json`.
- Design system: zero arbitrary Tailwind values (`-[...]`), minimum text size `text-xs`, adaptive monochrome SVG (`fill="currentColor"`).

## Review Focus

- `DISABLE_REDACT=1` environment variable must bypass `withRedact` cleanly so native React builds remain reproducible for A/B benchmarking.
- `StackGrid` with 16 items must render evenly in both `default` and `compact` variants (`grid-cols-2 sm:grid-cols-4` for default, `grid-cols-2 sm:grid-cols-4` for compact) without orphan cells.
- `IconTanstack` must use `fill="currentColor"` (no hardcoded `#121212` or `#fff`) so both light and dark themes work automatically.
- `pnpm check` (ESLint boundaries, TypeScript `tsc --noEmit`, Vitest unit tests) and `pnpm build` must pass with 0 errors and 0 warnings.

---

### Task 1: Measure Baseline Native React 19.3 Builds & Integrate `@tanstack/redact`

**Files:**
- Modify: `apps/web/package.json`
- Modify: `apps/studio/package.json`
- Modify: `apps/web/next.config.ts`
- Modify: `apps/studio/next.config.ts`

**Interfaces:**
- Produces: `withRedact(nextConfig)` integration in both apps and quantitative before/after client bundle measurements (raw bytes, gzip bytes, largest runtime chunk, and build duration).

- [x] **Step 1: Measure baseline production builds (`apps/web` and `apps/studio`) with native React 19.3**
  Run `pnpm turbo run build --force` and measure `.next/static/chunks/*.js` count, total raw bytes, total gzip bytes, and top runtime chunks for both `apps/web` and `apps/studio`.

- [x] **Step 2: Install `@tanstack/redact` in `apps/web` and `apps/studio`**
  Run `pnpm --filter web --filter studio add @tanstack/redact@^0.2.0`.

- [x] **Step 3: Wrap `nextConfig` with `withRedact` in `apps/web/next.config.ts` and `apps/studio/next.config.ts`**
  Import `{ withRedact } from "@tanstack/redact/next"` and export `process.env.DISABLE_REDACT === "1" ? nextConfig : withRedact(nextConfig)`.

- [x] **Step 4: Measure post-integration production builds with TanStack Redact & verify Redact runtime in emitted browser chunks**
  Run `pnpm turbo run build --force`, record the exact post-integration `.next/static/chunks/*.js` raw & gzip metrics for both apps, and verify that the browser chunks contain Redact's runtime while server bundles keep native React.

---

### Task 2: Add `IconTanstack` (from `svgl`) & Update `StackGrid` to 16 Items

**Files:**
- Modify: `packages/ui-patterns/src/stack-icons.tsx`
- Modify: `packages/ui-patterns/src/stack-grid.tsx`

**Interfaces:**
- Produces: `IconTanstack(props: SVGProps<SVGSVGElement>)` in `stack-icons.tsx` and 16-item `STACK_ITEMS` in `stack-grid.tsx`.

- [x] **Step 1: Add `IconTanstack` to `packages/ui-patterns/src/stack-icons.tsx`**
  Export `IconTanstack` using the `svgl.app` vector (`viewBox="0 0 64.04 83.84"`, `fill="currentColor"`).

- [x] **Step 2: Add `TanStack Redact` to `STACK_ITEMS` and update grid columns in `packages/ui-patterns/src/stack-grid.tsx`**
  Import `IconTanstack`, add `{ name: "TanStack Redact", category: "frontend", Icon: IconTanstack }` to `STACK_ITEMS` (16 items total), and update the grid container class to `grid-cols-2 sm:grid-cols-4`.

---

### Task 3: Update Landing Page, Architecture FAQ, and Documentation with Measured Results

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/components/architecture-faq.tsx`
- Modify: `docs/performance-optimization.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: `StackGrid` (16 items) from Task 2 and measured bundle savings from Task 1.

- [x] **Step 1: Update `apps/web/app/page.tsx`**
  Update `CountingNumber` from `15` to `16` technologies, update `ARCHITECTURE_CHAPTERS` and `PILLARS` to describe the Hybrid React 19 Server + TanStack Redact Browser Runtime architecture with the measured gzip reduction.

- [x] **Step 2: Add TanStack Redact FAQ item in `apps/web/components/architecture-faq.tsx`**
  Add an accordion item explaining how `withRedact` swaps the browser runtime to Redact while keeping React 19.3 on the server for RSC, Cache Components, and Server Actions.

- [x] **Step 3: Document TanStack Redact integration & benchmark table in `docs/performance-optimization.md` and `README.md`**
  Add a dedicated section in `docs/performance-optimization.md` with configuration details, compatibility matrix, `DISABLE_REDACT=1` A/B flag, and the measured before/after table for `apps/web` and `apps/studio`. Update `README.md` overview.

- [x] **Step 4: Run full monorepo verification (`pnpm check` and `pnpm build`)**
  Run `pnpm check` and `pnpm build` and verify exit code `0` across all workspace packages.
