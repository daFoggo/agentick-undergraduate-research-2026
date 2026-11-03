import {
  IconBox,
  IconLink,
  IconMessageCircle,
  IconTool,
} from "@tabler/icons-react"

import type { SpanKind } from "./trace-data"

const KIND_ICON = {
  agent: IconBox,
  chain: IconLink,
  llm: IconMessageCircle,
  tool: IconTool,
} as const satisfies Record<SpanKind, unknown>

/** The span kind as a small icon tile, used in the sheet header and the detail pane header. */
export function KindTile({ kind }: { kind: SpanKind }) {
  const Icon = KIND_ICON[kind]
  return (
    <span className="flex size-6 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
      <Icon aria-hidden className="size-4" />
    </span>
  )
}

export function KindIcon({ kind }: { kind: SpanKind }) {
  const Icon = KIND_ICON[kind]
  return <Icon aria-hidden />
}
