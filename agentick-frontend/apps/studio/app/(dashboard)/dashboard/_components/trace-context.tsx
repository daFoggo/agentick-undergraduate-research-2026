"use client"

import {
  createContext,
  use,
  useCallback,
  useEffect,
  useEffectEvent,
  useMemo,
  useState,
} from "react"

import {
  flattenSpans,
  parentIds,
  TRACE,
  visibleSpans,
  type Span,
} from "./trace-data"

/**
 * State for one open trace, lifted out of the tree and the detail pane so the siblings share it
 * (composition: the provider is the only place that knows how selection and expansion are
 * stored). It mounts with the sheet and goes away with it. `J` / `K` step through the visible
 * spans, like the Previous / Next buttons.
 *
 * Performance: the context value is memoized and its actions are stable, so a consumer re-renders
 * only when selection or expansion really changes; the key listener is attached once.
 */
type TraceState = {
  selected: Span
  select: (id: string) => void
  step: (delta: -1 | 1) => void
  expanded: ReadonlySet<string>
  toggleNode: (id: string) => void
  allExpanded: boolean
  toggleAll: () => void
}

const TraceContext = createContext<TraceState | null>(null)

export function useTrace() {
  const state = use(TraceContext)
  if (!state) throw new Error("Trace parts must sit inside TraceProvider")
  return state
}

const ALL_SPANS = flattenSpans(TRACE)
const PARENTS = parentIds(TRACE)

function isTyping(target: EventTarget | null) {
  return (
    target instanceof HTMLElement &&
    (target.isContentEditable ||
      /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))
  )
}

export function TraceProvider({ children }: { children: React.ReactNode }) {
  const [selectedId, setSelectedId] = useState(TRACE.id)
  const [expanded, setExpanded] = useState<ReadonlySet<string>>(
    () => new Set(PARENTS)
  )
  const selected = useMemo(
    () => ALL_SPANS.find((span) => span.id === selectedId) ?? TRACE,
    [selectedId]
  )
  const allExpanded = PARENTS.every((id) => expanded.has(id))

  const step = useCallback(
    (delta: -1 | 1) => {
      const list = visibleSpans(TRACE, expanded)
      const index = list.findIndex((span) => span.id === selectedId)
      const next = list[Math.min(list.length - 1, Math.max(0, index + delta))]
      if (next) setSelectedId(next.id)
    },
    [expanded, selectedId]
  )

  const toggleNode = useCallback((id: string) => {
    setExpanded((current) => {
      const next = new Set(current)
      if (!next.delete(id)) next.add(id)
      return next
    })
  }, [])

  const toggleAll = useCallback(() => {
    setExpanded(allExpanded ? new Set() : new Set(PARENTS))
  }, [allExpanded])

  // `useEffectEvent` reads the latest `step` without re-attaching the listener on every render.
  const onKeyDown = useEffectEvent((event: KeyboardEvent) => {
    if (event.defaultPrevented || event.metaKey || event.ctrlKey) return
    if (isTyping(event.target)) return
    if (event.key === "j") step(1)
    if (event.key === "k") step(-1)
  })
  useEffect(() => {
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  const value = useMemo<TraceState>(
    () => ({
      selected,
      select: setSelectedId,
      step,
      expanded,
      toggleNode,
      allExpanded,
      toggleAll,
    }),
    [selected, step, expanded, toggleNode, allExpanded, toggleAll]
  )

  return <TraceContext value={value}>{children}</TraceContext>
}
