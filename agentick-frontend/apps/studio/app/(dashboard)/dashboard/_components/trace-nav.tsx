"use client"

import {
  IconChevronLeft,
  IconChevronRight,
  IconFold,
  IconFoldDown,
  IconLink,
} from "@tabler/icons-react"

import { Button } from "@workspace/ui/components/button"
import { ButtonGroup } from "@workspace/ui/components/button-group"
import { Kbd } from "@workspace/ui/components/kbd"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@workspace/ui/components/tooltip"

import { CopyButton } from "@/components/shared/copy-button"

import { useTrace } from "./trace-context"

function StepButton({
  label,
  hotkey,
  onClick,
  children,
}: {
  label: string
  hotkey: string
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Button
            variant="outline"
            size="icon-sm"
            aria-label={label}
            aria-keyshortcuts={hotkey}
            onClick={onClick}
          />
        }
      >
        {children}
      </TooltipTrigger>
      <TooltipContent side="bottom">
        {label} <Kbd>{hotkey.toUpperCase()}</Kbd>
      </TooltipContent>
    </Tooltip>
  )
}

/** Previous / Next span as one button group in the sheet header; `K` and `J` do the same. */
export function TraceStepper() {
  const { step } = useTrace()
  return (
    <ButtonGroup>
      <StepButton label="Previous span" hotkey="k" onClick={() => step(-1)}>
        <IconChevronLeft />
      </StepButton>
      <StepButton label="Next span" hotkey="j" onClick={() => step(1)}>
        <IconChevronRight />
      </StepButton>
    </ButtonGroup>
  )
}

/** Copies the page URL. A client part, because the value is read from `window` at click time. */
export function CopyLinkButton() {
  return (
    <CopyButton
      value={() => window.location.href}
      label="Copy link"
      icon={IconLink}
    />
  )
}

/** Expands or collapses every node of the span tree (list pane header). */
export function ExpandAllButton() {
  const { allExpanded, toggleAll } = useTrace()
  const Icon = allExpanded ? IconFold : IconFoldDown
  return (
    <Button variant="ghost" size="icon-sm" onClick={toggleAll}>
      <Icon />
      <span className="sr-only">
        {allExpanded ? "Collapse all spans" : "Expand all spans"}
      </span>
    </Button>
  )
}
