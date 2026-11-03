# Client State (Zustand)

## 1. When to Use
Use when a feature needs client-only state shared by several distant client components (multi-step editor, audio player, canvas tool), or when asked to add Zustand, a store, `persist`, `devtools` or `immer`. Zustand is not installed by default: `pnpm --filter studio add zustand` (+ `immer` if used).

## 2. Decision Matrix

| State is… | Use |
| :--- | :--- |
| Server data | Server Components + `queries.ts` (never mirror into a store) |
| Filters, search, pagination, tab | URL search params |
| Local to one component or page | `useState` (Cache Components already preserves it across navigation) |
| Client-only, shared by distant client components | **Zustand store per provider** |

## 3. Canonical Pattern

```ts
// features/<x>/store.ts  (no "use client", no server imports)
import { createStore } from "zustand/vanilla"

export const createXStore = (initState: XState = defaultInitState) =>
  createStore<XStore>()((set, _get, store) => ({
    ...initState,
    increment: () => set((s) => ({ count: s.count + 1 })),
    reset: () => set(store.getInitialState()),
  }))
```

```tsx
// features/<x>/components/x-store-provider.tsx
"use client"
const Ctx = createContext<XStoreApi | null>(null)

export function XStoreProvider({ children, initState }: { children: React.ReactNode; initState?: XState }) {
  const [store] = useState(() => createXStore(initState))
  return <Ctx value={store}>{children}</Ctx>
}

export function useXStore<T>(selector: (s: XStore) => T): T {
  const store = use(Ctx)
  if (!store) throw new Error("useXStore must be used within XStoreProvider")
  return useStore(store, selector)
}
```

```tsx
// app/(dashboard)/<route>/page.tsx  -> compose; pass server or request values as initState
<XStoreProvider initState={{ count: 5 }}><Counter /></XStoreProvider>
```

Request-derived `initState` (cookie, session): resolve in an async Server Component inside `<Suspense>` and pass it to the provider.

## 4. Rules and Why

- **Factory + provider, never a module-level `create()` store.** A global store leaked between server requests (`global:4/5/6` vs `provider:6`).
- **Server Components never read the store.** The hook throws at runtime and fails `next build`; ESLint does not catch it.
- **One selector per value, or `useShallow` (`zustand/react/shallow`).** A selector returning a new object or function crashes the page in v5.
- **Update through `set`, never mutate.** `set` shallow-merges; `set(next, true)` replaces everything. Use `immer` for deep updates.
- **Middleware inline, on the combined store: `devtools(persist(immer(...)))`.** Extracting the creator into a variable loses the devtools typing.
- **Page-level stores survive navigation** (Cache Components uses `<Activity>`, up to 3 routes). Reset with an event handler, a data-derived key, or `key={useRouter().bfcacheId}` as a last resort. Key user-scoped stores by user id; reload on logout.
- **`persist` is hydration-safe** because `useStore` hydrates from `getInitialState()`; the persisted value appears one render later and overrides `initState` unless `merge` says otherwise. Use a Zod `PersistStorage`, `version` + `migrate`, `partialize`, and the user id in `name`.
- **`devtools` is optional**: it needs the Redux DevTools browser extension to show anything, works without it, and is off in production by default.
- **Tests**: fresh store per test via `createXStore()`; server render via `renderToString`. TSX in Vitest needs `oxc: { jsx: { runtime: "automatic" } }` in `vitest.config.ts`.

## 5. Never Do
- ❌ **Never `export const useXStore = create(...)`** at module level when the server can write to it.
- ❌ **Never copy server data or URL params into a store.**
- ❌ **Never import another feature's store**: compose in `app/` through props.
- ❌ **Never mount the provider in the root layout** unless the state is truly app-wide.

## 6. Source of Truth (Deep Dive)
- Full guide, evidence and verification limits: [docs/client-state.md](../../../../docs/client-state.md)
- Store placement and Client State Rules: [docs/project-structure.md §5](../../../../docs/project-structure.md#5-data-flow--state-management)
- Navigation state preservation: [docs/client-state.md §5.3](../../../../docs/client-state.md#53-state-outlives-navigation)
