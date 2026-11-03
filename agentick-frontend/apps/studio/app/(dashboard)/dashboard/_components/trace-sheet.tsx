import { Button } from "@workspace/ui/components/button"
import {
  Sheet,
  SheetDescription,
  SheetTitle,
  SheetTrigger,
} from "@workspace/ui/components/sheet"

import { CopyButton } from "@/components/shared/copy-button"
import {
  DetailSheetClose,
  DetailSheetContent,
  DetailSheetHeader,
  DetailSheetList,
  DetailSheetMain,
  DetailSheetPaneBody,
  DetailSheetPaneHeader,
  DetailSheetSplit,
} from "@/components/shared/detail-sheet"

import { SpanDetail } from "./span-detail"
import { KindTile } from "./span-kind"
import { SpanTree } from "./span-tree"
import { TraceProvider } from "./trace-context"
import { flattenSpans, TRACE } from "./trace-data"
import { CopyLinkButton, ExpandAllButton, TraceStepper } from "./trace-nav"

/**
 * A page-owned demo of the detail sheet. Three header tiers: the sheet (close, trace, copy,
 * previous / next), each pane (spans with expand all, the selected span), then the content. The
 * sheet opens fitting its content and is resized by dragging its left edge. Selection lives in
 * TraceProvider inside the sheet, so nothing is wired into the header or the shell.
 */
export function TraceSheet() {
  return (
    <Sheet>
      <SheetTrigger render={<Button size="lg" />}>Open trace</SheetTrigger>
      <DetailSheetContent>
        <TraceProvider>
          <DetailSheetHeader>
            <DetailSheetClose />
            <KindTile kind={TRACE.kind} />
            <SheetTitle className="truncate font-mono text-sm">
              {TRACE.name}
            </SheetTitle>
            <CopyButton value={TRACE.id} label="Copy trace id" />
            <CopyLinkButton />
            <div className="ml-auto">
              <TraceStepper />
            </div>
          </DetailSheetHeader>
          <SheetDescription className="sr-only">
            Spans and details of one agent run
          </SheetDescription>
          <DetailSheetSplit>
            <DetailSheetList>
              <DetailSheetPaneHeader>
                <span className="font-mono text-xs tracking-wider text-muted-foreground uppercase">
                  Spans ({flattenSpans(TRACE).length})
                </span>
                <div className="ml-auto">
                  <ExpandAllButton />
                </div>
              </DetailSheetPaneHeader>
              <DetailSheetPaneBody className="gap-0 p-2">
                <SpanTree />
              </DetailSheetPaneBody>
            </DetailSheetList>
            <DetailSheetMain>
              <SpanDetail />
            </DetailSheetMain>
          </DetailSheetSplit>
        </TraceProvider>
      </DetailSheetContent>
    </Sheet>
  )
}
