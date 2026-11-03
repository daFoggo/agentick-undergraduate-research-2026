# Interactive Lists, Filters & Pagination

## 1. When to Use
Use when implementing search, multi-select filters, sort orders, and paginated tables without adding client state libraries.

## 2. Core Pattern: The URL is the State

| Feature | Component | How it works |
| :--- | :--- | :--- |
| **Filters** | `<Form action="...">` (`next/form`) | Submits via GET. Updates URL params automatically. |
| **Pagination & Sorting** | `<Link href="?page=2">` | Standard Server Component Link. Renders without client JS. |
| **Pending State** | `useFormStatus` or `data-pending` | CSS or spinner active while transition is in flight. |

## 3. Canonical Pattern

```tsx
// app/(dashboard)/<domain>/page.tsx
export default function Page({ searchParams }: PageProps) {
  return (
    <>
      <ItemFilters /> {/* GET <Form> from next/form */}
      <Suspense fallback={<ItemTableSkeleton />}>
        {searchParams.then((sp) => <ItemTable searchParams={sp} />)}
      </Suspense>
    </>
  )
}
```

While navigation to new search params is in flight, React automatically keeps the old UI mounted on screen (equivalent to "keep previous data").

## 4. Never Do
- ❌ **Never install TanStack Query / SWR for simple table filtering**: Server Components + searchParams stream faster and ship less JS.
- ❌ **Never `await searchParams` at page top-level**: Always read inside the `<Suspense>` boundary.

## 5. Source of Truth (Deep Dive)
- Interactive table pattern: [docs/data-fetching.md §7.2](../../../../docs/data-fetching.md#72-interactive-lists-and-forms-without-a-client-data-library)
- When client library is justified (SWR): [docs/data-fetching.md §7.3](../../../../docs/data-fetching.md#73-when-a-client-data-library-would-be-justified)
