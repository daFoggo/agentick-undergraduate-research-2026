// Demo data: one agent run, shaped like the detail view of an LLM observability tool.
export type SpanKind = "agent" | "chain" | "llm" | "tool"

export type Message = {
  role: "Human" | "AI" | "Tool"
  /** Shown in a code block (tool calls and results) instead of prose. */
  code?: boolean
  text: string
}

export type Span = {
  id: string
  name: string
  kind: SpanKind
  time: string
  cost: string
  tokens?: number
  model?: string
  tags: string[]
  finishReason?: string
  messages: Message[]
  children?: Span[]
}

export const STARTED_AT = "26 Oct 2026, 8:00 PM"

export const TRACE: Span = {
  id: "chat_agent",
  name: "chat_agent",
  kind: "agent",
  time: "4.4s",
  cost: "<$0.01",
  tokens: 5998,
  tags: ["chat", "chat_agent", "start"],
  messages: [
    {
      role: "Human",
      text: "Starting a new case annotation. Trigger reason: this case is quite distinctive since we do not see any similar cases in the past.",
    },
    {
      role: "AI",
      text: "We observed microwave activity. What was it used for: reheating a meal, heating a drink, cooking or defrosting?",
    },
  ],
  children: [
    {
      id: "annotation-before",
      name: "AnnotationStateMiddleware.before",
      kind: "chain",
      time: "0.001s",
      cost: "$0",
      tags: ["middleware"],
      messages: [{ role: "Tool", code: true, text: '{ "status": "asked" }' }],
    },
    {
      id: "model-1",
      name: "model",
      kind: "chain",
      time: "2.5s",
      cost: "<$0.01",
      tags: ["model"],
      messages: [{ role: "Human", text: "Plan the next step for this case." }],
      children: [
        {
          id: "llm-1",
          name: "ChatOpenAI",
          kind: "llm",
          time: "2.5s",
          cost: "<$0.01",
          tokens: 2721,
          model: "gpt-4o-mini",
          tags: ["openai"],
          finishReason: "tool_calls",
          messages: [
            { role: "Human", text: "Plan the next step for this case." },
            { role: "AI", code: true, text: "get_case_context({})" },
          ],
        },
      ],
    },
    {
      id: "tools",
      name: "tools",
      kind: "chain",
      time: "0.03s",
      cost: "$0",
      tags: ["tools"],
      messages: [{ role: "Tool", text: "Running get_case_context." }],
      children: [
        {
          id: "tool-1",
          name: "get_case_context",
          kind: "tool",
          time: "0.02s",
          cost: "$0",
          tags: ["tool"],
          messages: [
            {
              role: "Tool",
              code: true,
              text: '{ "episodes": 2, "status": "asked", "t_start": "2026-10-26T12:15:00Z" }',
            },
          ],
        },
      ],
    },
    {
      id: "model-2",
      name: "model",
      kind: "chain",
      time: "1.8s",
      cost: "<$0.01",
      tags: ["model"],
      messages: [{ role: "Human", text: "Write the question for the user." }],
      children: [
        {
          id: "llm-2",
          name: "ChatOpenAI",
          kind: "llm",
          time: "1.8s",
          cost: "<$0.01",
          tokens: 3277,
          model: "gpt-4o-mini",
          tags: ["openai"],
          finishReason: "stop",
          messages: [
            { role: "Human", text: "Write the question for the user." },
            {
              role: "AI",
              text: "We observed microwave activity. What was it used for?",
            },
          ],
        },
      ],
    },
  ],
}

/** Every span, depth first. */
export function flattenSpans(span: Span): Span[] {
  return [span, ...(span.children ?? []).flatMap(flattenSpans)]
}

/** Spans in tree order, skipping the children of collapsed nodes. */
export function visibleSpans(
  span: Span,
  expanded: ReadonlySet<string>
): Span[] {
  if (!expanded.has(span.id)) return [span]
  return [
    span,
    ...(span.children ?? []).flatMap((c) => visibleSpans(c, expanded)),
  ]
}

/** Ids of every span that has children. */
export function parentIds(span: Span): string[] {
  return flattenSpans(span)
    .filter((s) => s.children?.length)
    .map((s) => s.id)
}
