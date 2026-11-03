# Mutations & Invalidation (Server Actions)

## 1. When to Use
Use when writing, updating, or deleting data and revalidating cached UI.

## 2. Standard 5-Step Action Flow
1. **Authenticate**: `verifySession()` (Server Actions are public HTTP endpoints).
2. **Validate**: `Schema.safeParse(Object.fromEntries(formData))`. Use Zod even when the input is a single id (`z.string().min(1)`): Server Action arguments are untrusted client input, so a `typeof` check is not enough.
3. **Write**: Call backend via feature `server.ts`.
4. **Invalidate**: `updateTag(tag)` (expires now, re-renders in the same round trip).
5. **Return DTO**: Return minimal state `{ success: true }` or expected error.

## 3. Canonical Pattern

```ts
// features/<domain>/actions.ts  ("use server" is the first line of the file; keep it when adding actions)
"use server"
export async function updateItemAction(_prev: State, formData: FormData): Promise<State> {
  const session = await verifySession()
  const parsed = UpdateItemSchema.safeParse(Object.fromEntries(formData))
  if (!parsed.success) return { error: parsed.error.issues[0]?.message }

  try {
    await patchItem(session.accessToken, parsed.data)
  } catch (error) {
    if (isExpectedApiError(error)) return { error: error.message }
    throw error // Unexpected errors bubble to error.tsx
  }

  updateTag(`items:${session.userId}`)
  return { saved: true }
}
```

## 4. Client Integration
Use `useActionState(action, initial)` for form handling and `useOptimistic` for instant UI feedback before server confirmation.

## 5. Never Do
- ❌ **Never catch-all without rethrowing**: `redirect()` works by throwing. Broad `catch` blocks break redirects.
- ❌ **Never mutate during render**: Cookie writes and revalidation belong in Server Actions, not Server Components.
- ❌ **Never use Server Actions to read data**: Actions run sequentially (one at a time) per client.

## 6. Source of Truth (Deep Dive)
- Full mutation rules & error classification: [docs/data-fetching.md §8](../../../../docs/data-fetching.md#8-mutations)
- Post-response background logging (`after()`): [docs/advanced-patterns.md §5.1](../../../../docs/advanced-patterns.md#51-non-blocking-work-with-after)
