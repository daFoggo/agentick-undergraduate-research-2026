/** Label / value rows of one record (`dl`, no card). */
export function Spec({ rows }: { rows: (readonly [string, string])[] }) {
  return (
    <dl className="flex max-w-xl flex-col gap-3">
      {rows.map(([term, value]) => (
        <div key={term} className="flex gap-3">
          <dt className="w-32 shrink-0 font-mono text-xs tracking-wider text-muted-foreground uppercase">
            {term}
          </dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  )
}
