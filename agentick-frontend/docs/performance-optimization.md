# Frontend Performance, Bundle Optimization & Hydration UX

Comprehensive performance optimization guide for `apps/studio` and `apps/web` on **Next.js 16.4.2** with React 19 (server) and **TanStack Redact** (`@tanstack/redact/next`, browser runtime).
Covers hybrid browser runtime optimization (`withRedact`), code splitting, bundle trimming, state preservation (`<Activity>`), hydration flash prevention, View Transitions, and Core Web Vitals.
Sources are the docs shipped with the package (`apps/studio/node_modules/next/dist/docs/01-app/`, written `DOCS/` below) and Vercel Engineering best practices (`vercel-react-best-practices`).
For server data fetching waterfalls and cache directives, see [data-fetching.md](data-fetching.md).
For Playwright `instant()` regression testing, see [advanced-patterns.md](advanced-patterns.md).

---

## 1. Code Splitting & Lazy Loading (`lazy-loading.md`)

Server Components are automatically code-split by route. For Client Components and heavy external libraries, use explicit lazy loading patterns to reduce Initial JavaScript Execution time and improve Largest Contentful Paint (LCP) and Interaction to Next Paint (INP).

### 1.1 Dynamic Client Components (`next/dynamic`)
Use `next/dynamic` (composite of `React.lazy()` and `<Suspense>`) to split heavy client components into independent bundle chunks:

```tsx
'use client'
import dynamic from 'next/dynamic'
import { Skeleton } from '@workspace/ui/components/skeleton'

// 1. Loaded in a separate bundle, rendered with skeleton while downloading
const CaseKanbanBoard = dynamic(
  () => import('@/features/cases/components/case-kanban-board'),
  {
    loading: () => <Skeleton className="h-[500px] w-full" />,
  }
)

// 2. Disable SSR entirely for browser-only components
// (Canvas, Leaflet maps, WebGL, or window/document dependencies)
const InteractiveChart = dynamic(
  () => import('@/components/shared/canvas-chart'),
  {
    ssr: false,
    loading: () => <Skeleton className="h-[300px] w-full" />,
  }
)
```

> [!IMPORTANT]
> The `{ ssr: false }` option is **only valid inside Client Components**. If called inside a Server Component, Next.js throws a build error (`DOCS/02-guides/lazy-loading.md`).

### 1.2 Interaction-Based Dynamic Library Imports
Do not import large utilities (Excel exporters, PDF generators, fuzzy search) at the top of a file. Import them dynamically **inside the user interaction handler**:

```tsx
'use client'

export function ExportButton({ records }: { records: unknown[] }) {
  const handleExport = async () => {
    // 250 KB xlsx library is only downloaded when the user actually clicks
    const { utils, writeFile } = await import('xlsx')
    const worksheet = utils.json_to_sheet(records)
    const workbook = utils.book_new()
    utils.book_append_sheet(workbook, worksheet, 'Data')
    writeFile(workbook, 'export.xlsx')
  }

  return <button onClick={handleExport}>Export to Excel</button>
}
```

### 1.3 Offloading Heavy Compute to Server Components
Do not ship markdown parsers or code syntax highlighters (Prism, highlight.js) to the client bundle. Move the transformation to a Server Component using Shiki or markdown processors, shipping only static HTML (`DOCS/02-guides/package-bundling.md`):

```tsx
// features/docs/components/code-snippet.tsx (Server Component)
import { codeToHtml } from 'shiki'

export async function CodeSnippet({ code, lang }: { code: string; lang: string }) {
  // Shiki runs entirely on server: 0 KB shipped to client bundle
  const html = await codeToHtml(code, {
    lang,
    theme: 'github-dark',
  })

  return <div dangerouslySetInnerHTML={{ __html: html }} />
}
```

---

## 2. Package Bundling & Tree-Shaking Optimization

### 2.1 `optimizePackageImports` (Zero Barrel Overhead)
Large icon and utility libraries can degrade HMR performance and client bundle size when imported via barrel exports.
In Next.js 16+, major packages (`lucide-react`, `date-fns`, `lodash-es`, `react-icons/*`, `recharts`, `rxjs`) are **already optimized by default** (`DOCS/03-api-reference/05-config/01-next-config-js/optimizePackageImports.md`).
For any additional heavy third-party packages not in the default list, configure `experimental.optimizePackageImports` in `next.config.ts` to automatically rewrite imports into direct module paths:

```ts
// apps/studio/next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  experimental: {
    // Only needed for packages NOT already on Next.js default optimization list
    optimizePackageImports: ['@radix-ui/react-icons', 'my-custom-icon-library'],
  },
}

export default nextConfig
```

### 2.2 Server External Packages
Opt server-only binary dependencies (e.g. `sharp`, `sqlite3`, database drivers) out of bundling via `serverExternalPackages`:

```ts
// apps/studio/next.config.ts
const nextConfig: NextConfig = {
  serverExternalPackages: ['pino', 'sharp'],
}
```

### 2.3 Turbopack Bundle Analyzer
Analyze client and server bundle graphs with Turbopack's native analyzer:

```bash
# Run interactive visualizer
pnpm --filter=studio next analyze

# Output diagnostics report to .next/diagnostics/analyze
pnpm --filter=studio next analyze --output
```

### 2.4 Hybrid Browser Runtime with TanStack Redact (`@tanstack/redact/next`)

Both `apps/studio` and `apps/web` wrap their Next.js configuration with `withRedact` from `@tanstack/redact/next`:

```ts
// apps/studio/next.config.ts & apps/web/next.config.ts
import type { NextConfig } from 'next'
import { withRedact } from '@tanstack/redact/next'

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  // ...
}

export default process.env.DISABLE_REDACT === '1'
  ? nextConfig
  : withRedact(nextConfig)
```

#### Architecture & Rules
- **Server-Side (Native React 19.3):** Next.js keeps upstream `react` and `react-dom` on the server to execute React Server Components (RSC), Flight streaming, `"use cache"`, Partial Prerendering (PPR), and Server Actions.
- **Browser-Side (TanStack Redact):** Turbopack (and Webpack when `--webpack` is passed) uses browser-only loader rules on the resolved React entry files (`react`, `react-dom`, `scheduler`, and `next/dist/compiled/react-experimental`) to replace the client runtime with Redact's synchronous rendering engine.
- **Keep Standard Imports:** Always keep `react` and `react-dom` installed and continue importing from `'react'`, `'react-dom'`, and `'next/*'`. **Never** set `jsxImportSource` to Redact in `tsconfig.json` because the server requires React's JSX runtime.
- **A/B Benchmarking Escape Hatch:** Pass `DISABLE_REDACT=1` at build or dev time (`DISABLE_REDACT=1 pnpm build`) to bypass `withRedact` and run native React 19.3 in the browser.

#### Measured Client Bundle Reduction (`next@16.4.2` Turbopack Production Build)

| Metric | `apps/web` (React 19.3) | `apps/web` (`withRedact`) | Delta (`web`) | `apps/studio` (React 19.3) | `apps/studio` (`withRedact`) | Delta (`studio`) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **DOM Runtime Chunk (Raw)** | 229,843 B | 77,561 B | **-152,282 B (-66.3%)** | 235,404 B | 86,105 B | **-149,299 B (-63.4%)** |
| **DOM Runtime Chunk (Gzip)** | 71,830 B | 30,013 B | **-41,817 B (-58.2%)** | 73,579 B | 32,060 B | **-41,519 B (-56.4%)** |
| **DOM Runtime Chunk (Brotli)** | 61,456 B | 26,908 B | **-34,548 B (-56.2%)** | 62,968 B | 28,514 B | **-34,454 B (-54.7%)** |
| **Total Client `.js` Chunks (Raw)** | 840,887 B | 710,789 B | **-130,098 B (-15.5%)** | 1,441,582 B | 1,304,575 B | **-137,007 B (-9.5%)** |
| **Total Client `.js` Chunks (Gzip)** | 270,275 B | 235,235 B | **-35,040 B (-13.0%)** | 475,933 B | 440,402 B | **-35,531 B (-7.5%)** |
| **Total Client `.js` Chunks (Brotli)** | 234,731 B | 206,046 B | **-28,685 B (-12.2%)** | 417,204 B | 387,924 B | **-29,280 B (-7.0%)** |
| **Turbopack Compile Time** | 5.0 s | 4.1 s | **-0.9 s (-18.0%)** | 8.8 s | 7.7 s | **-1.1 s (-12.5%)** |

---

## 3. Preserving UI State with React 19 `<Activity>`

In Next.js 16 with Cache Components enabled, navigating away from a page **does not unmount it immediately**. Next.js preserves up to 3 recent routes in the DOM using React's `<Activity mode="hidden">` (hidden via `display: none`) (`DOCS/02-guides/preserving-ui-state.md`).

### 3.1 What is Preserved Automatically
- Form input drafts and typed values.
- Scroll positions.
- Video/audio playback progress.
- Expanded accordion panels or sidebars.

### 3.2 Resetting Transient State on Navigation
While persistent state (drafts) should be kept, transient UI (dropdown popovers, action menus) should close when the user navigates away. Use the cleanup function of `useLayoutEffect`:

```tsx
'use client'
import { useState, useLayoutEffect } from 'react'

export function UserProfileDropdown() {
  const [isOpen, setIsOpen] = useState(false)

  // Fires synchronously before <Activity> hides the component
  useLayoutEffect(() => {
    return () => {
      setIsOpen(false)
    }
  }, [])

  return (
    <div>
      <button onClick={() => setIsOpen((prev) => !prev)}>Options</button>
      {isOpen && <DropdownMenuContent />}
    </div>
  )
}
```

### 3.3 Deliberate Subtree Reset via `bfcacheId`
To force a component subtree to reset on push/replace navigation while still preserving state on browser Back/Forward (bfcache), pass `bfcacheId` as a key:

```tsx
'use client'
import { useRouter } from 'next/navigation'

export function WizardForm() {
  const { bfcacheId } = useRouter()
  return <WizardContent key={bfcacheId} />
}
```

---

## 4. Preventing Flash Before Hydration

### 4.1 The Problem
Server rendering uses the server's locale and timezone (e.g. UTC, English). When the client hydrates with local user preferences (e.g. UTC+7, Vietnamese), calling `toLocaleDateString()` or formatting themes directly inside a Client Component results in:
1. **Hydration Mismatch Error**: Server HTML does not match client Virtual DOM.
2. **Visible Flash**: Content flickers from server format to client format.

### 4.2 The Synchronous Inline Script Pattern
To correct client-only state before the browser's first paint with **zero flash and zero hydration errors**, place a synchronous inline script right after the element and mark it with `suppressHydrationWarning` (`DOCS/02-guides/preventing-flash-before-hydration.md`):

```tsx
// app/cases/[id]/_components/case-timestamp.tsx (Server Component)
export function CaseTimestamp({ timestamp }: { timestamp: string }) {
  const id = `time-${Math.abs(hashString(timestamp))}`

  return (
    <div>
      <span id={id} suppressHydrationWarning>
        {new Date(timestamp).toUTCString()}
      </span>
      {/* Executes synchronously during HTML parsing before browser paint */}
      <script
        dangerouslySetInnerHTML={{
          __html: `document.getElementById("${id}").textContent = new Date("${timestamp}").toLocaleString()`,
        }}
      />
    </div>
  )
}
```

---

## 5. Declarative View Transitions (`view-transitions.md`)

React 19 native View Transitions integrate with the browser's View Transitions API. Navigations in Next.js App Router automatically trigger transitions without heavy motion libraries (`DOCS/02-guides/view-transitions.md`).

### 5.1 Shared Element Morphing (Thumbnail to Hero)
Give the shared element on both pages the same transition `name`:

```tsx
// 1. On Case Card (List Page: app/cases/page.tsx)
import { ViewTransition } from 'react'
import Image from 'next/image'
import Link from 'next/link'

export function CaseCard({ caseItem }: { caseItem: Case }) {
  return (
    <Link href={`/cases/${caseItem.id}`}>
      <ViewTransition name={`case-hero-${caseItem.id}`}>
        <Image src={caseItem.thumbnailUrl} alt={caseItem.title} width={300} height={200} />
      </ViewTransition>
      <h3>{caseItem.title}</h3>
    </Link>
  )
}

// 2. On Case Detail Page (app/cases/[id]/page.tsx)
export function CaseDetailHero({ caseItem }: { caseItem: Case }) {
  return (
    <ViewTransition name={`case-hero-${caseItem.id}`}>
      <Image src={caseItem.thumbnailUrl} alt={caseItem.title} width={1200} height={600} priority />
    </ViewTransition>
  )
}
```
The browser smoothly morphs the card's thumbnail into the hero banner during navigation.

---

## 6. Core Web Vitals & Asset Optimization

### 6.1 `next/image` Best Practices
- **LCP Hero Images**: Always add `priority` to images above the fold to eliminate LCP delay.
- **Responsive `sizes`**: Never omit `sizes` on images with `fill`. Without `sizes`, browsers download full-resolution desktop images on mobile phones.
  ```tsx
  <Image
    src="/hero.webp"
    alt="Dashboard banner"
    fill
    priority
    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
    className="object-cover"
  />
  ```
- **Placeholders**: Use `placeholder="blur"` with local images or generate lightweight `blurDataURL` to eliminate Cumulative Layout Shift (CLS).

### 6.2 `next/font` Zero-CLS Typography
Fonts configured via `next/font/google` or `next/font/local` are automatically self-hosted at build time.
`subsets` only picks which files are **preloaded**; every subset still gets its `@font-face` and loads on demand by
`unicode-range`. List only the subsets the UI renders on first paint (`latin` here): a preloaded subset the page never
uses triggers "preloaded but not used" warnings (Vietnamese user content still renders in the right font).
```ts
// apps/studio/app/fonts.ts
import { Inter, JetBrains_Mono } from 'next/font/google'

export const fontSans = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
})

export const fontMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})
```

### 6.3 Script Loading Strategies (`next/script`)
Control third-party execution via `strategy`:
- `strategy="beforeInteractive"`: Critical consent banners or security polyfills (injected into `<head>`).
- `strategy="afterInteractive"` (Default): Google Tag Manager, analytics.
- `strategy="lazyOnload"`: Live chat widgets, customer feedback modals, social widgets (loaded during idle time).
- `@next/third-parties`: Official zero-bundle wrappers (`<GoogleTagManager />`, `<GoogleAnalytics />`, `<YouTubeEmbed />`).

---

## 7. Performance Review Checklist

- [ ] **Heavy Components**: Complex editors, charts, and maps are lazy-loaded via `next/dynamic` (with `{ ssr: false }` where needed).
- [ ] **On-Demand Utilities**: Sheet/PDF export and heavy libraries are imported inside interaction callbacks (`await import(...)`).
- [ ] **Package Imports**: Icon and utility packages are declared under `experimental.optimizePackageImports`.
- [ ] **Hydration Flash**: Timezones, dates, and client themes use the synchronous inline script pattern with `suppressHydrationWarning`.
- [ ] **Transient UI**: Popovers, modals, and dropdown menus close upon navigation via `useLayoutEffect` cleanup.
- [ ] **Images**: Hero images have `priority` and explicit `sizes` definitions; no missing dimensions.
- [ ] **Sequential Round Trips**: Each page awaits the network as few times in a row as possible; independent reads start before the first `await`, and values needed first come from the session (`getCalendar()`). See [providers.md §5](providers.md#5-latency-what-was-measured-and-what-to-do).
- [ ] **Zero Barrel Files**: Deep imports are used everywhere (`@/features/<name>/components/...`) to protect bundle boundaries.
