"use client"

import { useState } from "react"
import { IconCheck, IconCopy } from "@tabler/icons-react"

import {
  CopyButton as AnimateCopyButton,
  CopyButtonIcon,
} from "@workspace/ui/components/animate-ui/buttons/copy"

/**
 * Icon button that copies `value` (a string, or a function run at click time, e.g. the current
 * URL). Built on Animate UI's `CopyButton` for spring press feedback and blur/scale icon swap.
 */
export function CopyButton({
  value,
  label,
  icon: Icon = IconCopy,
}: {
  value: string | (() => string)
  label: string
  icon?: React.ComponentType<{ className?: string }>
}) {
  const [copied, setCopied] = useState(false)
  const staticContent = typeof value === "string" ? value : ""

  return (
    <AnimateCopyButton
      variant="ghost"
      size="icon-sm"
      content={staticContent}
      copied={typeof value === "function" ? copied : undefined}
      onCopiedChange={setCopied}
      delay={1500}
      aria-label={copied ? "Copied" : label}
      onClick={
        typeof value === "function"
          ? () => {
              void navigator.clipboard.writeText(value()).then(() => {
                setCopied(true)
                setTimeout(() => setCopied(false), 1500)
              })
            }
          : undefined
      }
    >
      <CopyButtonIcon icon={<Icon />} copiedIcon={<IconCheck />} />
      <span className="sr-only">{copied ? "Copied" : label}</span>
    </AnimateCopyButton>
  )
}
