"use client"

import { createContext, use, useRef, useState } from "react"
import { IconChevronsRight } from "@tabler/icons-react"

import { Button } from "@workspace/ui/components/button"
import { SheetClose, SheetContent } from "@workspace/ui/components/sheet"
import { cn } from "@workspace/ui/lib/utils"

/**
 * Detail sheet (design system §8): a record opened from a page, never a route. Compound parts over
 * one `Sheet`; the open state and the width stay in the sheet, so a page needs no provider and the
 * header no button. Three header tiers, each its own part:
 *
 *   <Sheet>
 *     <SheetTrigger render={<Button />}>Open</SheetTrigger>
 *     <DetailSheetContent>
 *       <DetailSheetHeader>            tier 1: the record (close, title, actions)
 *         <DetailSheetClose />
 *         …
 *       </DetailSheetHeader>
 *       <DetailSheetSplit>
 *         <DetailSheetList>
 *           <DetailSheetPaneHeader>…  tier 2: the pane (title, pane tools)
 *           <DetailSheetPaneBody>…    tier 3: content
 *         </DetailSheetList>
 *         <DetailSheetMain>…</DetailSheetMain>
 *       </DetailSheetSplit>
 *     </DetailSheetContent>
 *   </Sheet>
 *
 * The sheet opens fitting its content (42rem). Drag its left edge to resize (arrow keys work on the
 * focused handle, double click resets); the width is remembered. Below `sm` it is always full
 * width. The panes split on the sheet's own width (container query), not the viewport's.
 *
 * Resizing follows Opik's ResizableSidePanel: the drag writes a CSS variable on the element through
 * a ref, with no React state and no transition, and commits to localStorage on release.
 */
const DEFAULT_WIDTH = "42rem"
const MIN_WIDTH = 384
const KEY_STEP = 32
const WIDTH_VAR = "--detail-sheet-width"

function clampWidth(px: number) {
  return Math.round(Math.min(window.innerWidth - 64, Math.max(MIN_WIDTH, px)))
}

function readWidth(storageKey: string) {
  try {
    const value = Number(localStorage.getItem(storageKey))
    return value > 0 ? clampWidth(value) : null
  } catch {
    return null
  }
}

function writeWidth(storageKey: string, px: number | null) {
  try {
    if (px === null) localStorage.removeItem(storageKey)
    else localStorage.setItem(storageKey, String(px))
  } catch {
    // Private mode or blocked storage: the width just is not remembered.
  }
}

const DetailSheetContext = createContext<{
  storageKey: string
  onWidthCommit: (px: number | null) => void
} | null>(null)

function useDetailSheet() {
  const state = use(DetailSheetContext)
  if (!state)
    throw new Error("DetailSheet parts must sit inside DetailSheetContent")
  return state
}

export function DetailSheetContent({
  storageKey = "detail-sheet-width",
  className,
  children,
  ...props
}: Omit<React.ComponentProps<typeof SheetContent>, "showCloseButton"> & {
  /** localStorage key for the remembered width; give two sheets different keys to size them apart. */
  storageKey?: string
}) {
  // The sheet only mounts once opened, on the client, so storage can be read here.
  const [committedWidth, setCommittedWidth] = useState(() =>
    typeof window === "undefined" ? null : readWidth(storageKey)
  )
  return (
    <DetailSheetContext value={{ storageKey, onWidthCommit: setCommittedWidth }}>
      <SheetContent
        showCloseButton={false}
        style={
          {
            [WIDTH_VAR]:
              committedWidth === null ? DEFAULT_WIDTH : `${committedWidth}px`,
          } as React.CSSProperties
        }
        className={cn(
          "@container gap-0 overflow-hidden data-[side=right]:w-full data-[side=right]:sm:w-(--detail-sheet-width) data-[side=right]:sm:max-w-none",
          className
        )}
        {...props}
      >
        <DetailSheetResizeHandle />
        {children}
      </SheetContent>
    </DetailSheetContext>
  )
}

/** The grab area on the sheet's left edge. Drives the width of its parent, the sheet popup. */
function DetailSheetResizeHandle() {
  const { storageKey, onWidthCommit } = useDetailSheet()
  const width = useRef<number | null>(null)
  const dragging = useRef(false)

  function apply(element: HTMLElement, px: number) {
    width.current = clampWidth(px)
    element.parentElement?.style.setProperty(WIDTH_VAR, `${width.current}px`)
  }

  return (
    <div
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize sheet"
      tabIndex={0}
      onPointerDown={(event) => {
        event.currentTarget.setPointerCapture(event.pointerId)
        dragging.current = true
        event.currentTarget.dataset.resizing = "true"
      }}
      onPointerMove={(event) => {
        if (dragging.current)
          apply(event.currentTarget, window.innerWidth - event.clientX)
      }}
      onPointerUp={(event) => {
        dragging.current = false
        delete event.currentTarget.dataset.resizing
        if (width.current !== null) {
          writeWidth(storageKey, width.current)
          onWidthCommit(width.current)
        }
      }}
      onDoubleClick={(event) => {
        width.current = null
        event.currentTarget.parentElement?.style.setProperty(
          WIDTH_VAR,
          DEFAULT_WIDTH
        )
        writeWidth(storageKey, null)
        onWidthCommit(null)
      }}
      onKeyDown={(event) => {
        const sign =
          event.key === "ArrowLeft" ? 1 : event.key === "ArrowRight" ? -1 : 0
        if (!sign) return
        event.preventDefault()
        const current =
          event.currentTarget.parentElement?.getBoundingClientRect().width ?? 0
        apply(event.currentTarget, current + sign * KEY_STEP)
        if (width.current !== null) {
          writeWidth(storageKey, width.current)
          onWidthCommit(width.current)
        }
      }}
      className="absolute inset-y-0 left-0 z-10 w-1.5 cursor-col-resize touch-none transition-colors duration-150 outline-none hover:bg-primary/20 focus-visible:bg-primary/20 data-resizing:bg-primary/30 max-sm:hidden"
    />
  )
}

/** Tier 1: the record. Children flow left to right; put `ml-auto` on the first right-hand item. */
export function DetailSheetHeader({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "flex h-14 shrink-0 items-center gap-2 border-b px-3",
        className
      )}
      {...props}
    />
  )
}

/** `»` closes the sheet (it slides out to the right, like the sheet itself). */
export function DetailSheetClose() {
  return (
    <SheetClose render={<Button variant="ghost" size="icon-sm" />}>
      <IconChevronsRight />
      <span className="sr-only">Close</span>
    </SheetClose>
  )
}

/** Below the split width the panes stack and the sheet scrolls; above it they sit side by side. */
export function DetailSheetSplit({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "no-scrollbar flex min-h-0 flex-1 flex-col overflow-y-auto @xl:grid @xl:grid-cols-3 @xl:overflow-hidden",
        className
      )}
      {...props}
    />
  )
}

/** Left pane: the list of things inside the record (spans, files, steps). One third of the split. */
export function DetailSheetList({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "flex min-h-0 flex-col border-b @xl:col-span-1 @xl:border-r @xl:border-b-0",
        className
      )}
      {...props}
    />
  )
}

/** Right pane: the selected thing in detail. Two thirds of the split. */
export function DetailSheetMain({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      className={cn("flex min-h-0 flex-col @xl:col-span-2", className)}
      {...props}
    />
  )
}

/** Tier 2: header of one pane. */
export function DetailSheetPaneHeader({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "flex h-12 shrink-0 items-center gap-2 border-b bg-card px-4",
        className
      )}
      {...props}
    />
  )
}

/** Tier 3: scrolling content of one pane. */
export function DetailSheetPaneBody({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "no-scrollbar flex flex-1 flex-col gap-5 p-4 @xl:overflow-y-auto",
        className
      )}
      {...props}
    />
  )
}
