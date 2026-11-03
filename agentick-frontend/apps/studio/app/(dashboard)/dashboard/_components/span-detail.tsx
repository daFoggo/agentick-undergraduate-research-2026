"use client"

import {
  IconCalendar,
  IconChevronRight,
  IconClock,
  IconCoin,
  IconHash,
  IconRobot,
  IconTag,
  IconTool,
  IconUser,
} from "@tabler/icons-react"

import { Badge } from "@workspace/ui/components/badge"
import { Button } from "@workspace/ui/components/button"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@workspace/ui/components/collapsible"
import { SlidingNumber } from "@workspace/ui/components/animate-ui/numbers/sliding-number"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@workspace/ui/components/tabs"

import { CopyButton } from "@/components/shared/copy-button"
import {
  DetailSheetPaneBody,
  DetailSheetPaneHeader,
} from "@/components/shared/detail-sheet"

import { KindTile } from "./span-kind"
import { useTrace } from "./trace-context"
import { STARTED_AT, type Message } from "./trace-data"

const LABEL = "font-mono text-xs tracking-wider text-muted-foreground uppercase"

const ROLE_ICON = {
  Human: IconUser,
  AI: IconRobot,
  Tool: IconTool,
} as const satisfies Record<Message["role"], unknown>

/** Tier 2 and 3 of the right pane: the selected span's header, meta, tags and tabs. */
export function SpanDetail() {
  const { selected } = useTrace()
  const details = [
    ["Kind", selected.kind],
    ["Model", selected.model ?? "none"],
    [
      "Tokens",
      selected.tokens ? <SlidingNumber number={selected.tokens} /> : "none",
    ],
    ["Duration", selected.time],
    ["Cost", selected.cost],
    ["Started", STARTED_AT],
  ] as const

  return (
    <>
      <DetailSheetPaneHeader>
        <KindTile kind={selected.kind} />
        <span className="truncate font-mono text-sm">{selected.name}</span>
        <CopyButton value={selected.id} label="Copy span id" />
        <Badge variant="secondary" className="ml-auto">
          {selected.kind}
        </Badge>
      </DetailSheetPaneHeader>
      <DetailSheetPaneBody>
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-muted-foreground">
            <Meta icon={IconCalendar}>{STARTED_AT}</Meta>
            <Meta icon={IconClock}>{selected.time}</Meta>
            {selected.tokens ? (
              <Meta icon={IconHash}>
                <SlidingNumber number={selected.tokens} />
              </Meta>
            ) : null}
            <Meta icon={IconCoin}>{selected.cost}</Meta>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <IconTag aria-hidden className="size-4 text-muted-foreground" />
            {selected.tags.map((tag) => (
              <Badge key={tag} variant="secondary">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
        <Tabs defaultValue="messages">
          <TabsList>
            <TabsTrigger value="messages">Messages</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="feedback">Feedback scores</TabsTrigger>
          </TabsList>
          <TabsContent value="messages" className="pt-5">
            {/* `overflow-hidden` clips the square header background to the rounded border. */}
            <section className="flex flex-col overflow-hidden rounded-xl border">
              <div className="flex h-10 items-center justify-between border-b bg-card pr-1 pl-4">
                <span className={LABEL}>LLM messages</span>
                <CopyButton
                  value={selected.messages.map((m) => m.text).join("\n\n")}
                  label="Copy all messages"
                />
              </div>
              <div className="flex flex-col gap-1 p-2">
                {selected.messages.map((message, index) => (
                  <MessageItem key={index} message={message} />
                ))}
                {selected.finishReason ? (
                  <p className="flex gap-3 px-2 pt-2 text-muted-foreground">
                    <span>Finish reason</span>
                    <span className="font-mono">{selected.finishReason}</span>
                  </p>
                ) : null}
              </div>
            </section>
          </TabsContent>
          <TabsContent value="details" className="pt-5">
            <dl className="flex flex-col gap-3">
              {details.map(([term, value]) => (
                <div key={term} className="flex gap-3">
                  <dt className={`w-24 shrink-0 ${LABEL}`}>{term}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
          </TabsContent>
          <TabsContent value="feedback" className="pt-5">
            <p className="text-muted-foreground">No feedback scores yet.</p>
          </TabsContent>
        </Tabs>
      </DetailSheetPaneBody>
    </>
  )
}

function Meta({
  icon: Icon,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>
  children: React.ReactNode
}) {
  return (
    <span className="flex items-center gap-1.5 text-sm">
      <Icon aria-hidden className="size-4" />
      {children}
    </span>
  )
}

/** One message: a collapsible with a role tile and label; tool calls and results show as code. */
function MessageItem({ message }: { message: Message }) {
  const Icon = ROLE_ICON[message.role]
  return (
    <Collapsible defaultOpen>
      <CollapsibleTrigger
        render={
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start aria-expanded:bg-transparent aria-expanded:hover:bg-muted"
          />
        }
      >
        <IconChevronRight
          aria-hidden
          className="group-data-panel-open/button:rotate-90 motion-safe:transition-transform motion-safe:duration-200"
        />
        <span className="flex size-5 items-center justify-center rounded-md bg-muted">
          <Icon aria-hidden className="size-3" />
        </span>
        {message.role}
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="ml-4 flex flex-col gap-2 border-l py-2 pl-4">
          {message.code ? (
            <pre className="overflow-x-auto rounded-lg bg-muted p-3 font-mono text-xs whitespace-pre-wrap">
              {message.text}
            </pre>
          ) : (
            <p>{message.text}</p>
          )}
        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}
