"use client"

import { IconChevronRight } from "@tabler/icons-react"

import { Button } from "@workspace/ui/components/button"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@workspace/ui/components/collapsible"

import { KindIcon } from "./span-kind"
import { useTrace } from "./trace-context"
import { TRACE, type Span } from "./trace-data"

/**
 * Interactive span tree, built the way shadcn's File Tree is: a node with children is a
 * Collapsible (the chevron toggles it), every node is a ghost Button (click selects it).
 * Hover is `bg-muted`, the selected row a `bg-primary/10` tint, so the two never look alike.
 */
export function SpanTree() {
  return (
    <div className="flex flex-col">
      <SpanNode span={TRACE} />
    </div>
  )
}

function SpanRow({ span }: { span: Span }) {
  const { selected, select } = useTrace()
  const current = selected.id === span.id
  return (
    <Button
      variant="ghost"
      size="sm"
      aria-current={current ? "true" : undefined}
      data-current={current || undefined}
      onClick={() => select(span.id)}
      className="min-w-0 flex-1 justify-start font-mono data-current:bg-primary/10 data-current:hover:bg-primary/15"
    >
      <KindIcon kind={span.kind} />
      <span className="truncate">{span.name}</span>
      <span className="ml-auto text-xs text-muted-foreground tabular-nums">
        {span.time}
      </span>
    </Button>
  )
}

function SpanNode({ span }: { span: Span }) {
  const { expanded, toggleNode } = useTrace()
  if (!span.children?.length) {
    return (
      <div className="flex items-center gap-1">
        {/* Same width as the chevron, so leaves line up with their siblings. */}
        <span aria-hidden className="size-6 shrink-0" />
        <SpanRow span={span} />
      </div>
    )
  }
  return (
    <Collapsible
      open={expanded.has(span.id)}
      onOpenChange={() => toggleNode(span.id)}
    >
      <div className="flex items-center gap-1">
        {/* The ghost Button paints `aria-expanded` as a hover surface; an open node is not hovered. */}
        <CollapsibleTrigger
          render={
            <Button
              variant="ghost"
              size="icon-xs"
              className="aria-expanded:bg-transparent aria-expanded:hover:bg-muted"
            />
          }
          aria-label={`Toggle ${span.name}`}
        >
          <IconChevronRight
            aria-hidden
            className="group-data-panel-open/button:rotate-90 motion-safe:transition-transform motion-safe:duration-200"
          />
        </CollapsibleTrigger>
        <SpanRow span={span} />
      </div>
      <CollapsibleContent>
        <div className="ml-3 flex flex-col border-l pl-1">
          {span.children.map((child) => (
            <SpanNode key={child.id} span={child} />
          ))}
        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}
