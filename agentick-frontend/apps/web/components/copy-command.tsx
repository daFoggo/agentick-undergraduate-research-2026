"use client"

import { IconTerminal } from "@tabler/icons-react"
import { CopyButton } from "@workspace/ui/components/animate-ui/buttons/copy"

export function CopyCommand({ command }: { command: string }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-border/50 bg-muted/20 px-3 py-1 font-mono text-xs text-muted-foreground transition-all duration-150 hover:border-border hover:bg-muted/30">
      <IconTerminal className="size-3.5 text-muted-foreground" />
      <span className="select-all text-foreground/90 font-medium">{command}</span>
      <CopyButton
        content={command}
        variant="ghost"
        size="icon"
        className="size-6 text-muted-foreground hover:text-foreground hover:bg-transparent"
      />
    </div>
  )
}
