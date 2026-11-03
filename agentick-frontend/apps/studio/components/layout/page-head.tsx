/** Page head of a dashboard page: mono label, title, one-line description. */
export function PageHead({
  label,
  title,
  children,
}: {
  label: string
  title: string
  children?: React.ReactNode
}) {
  return (
    <header className="flex flex-col gap-3">
      <span className="font-mono text-xs tracking-wider text-muted-foreground uppercase">
        {label}
      </span>
      <div className="flex items-center gap-2">
        <h1 className="text-3xl leading-tight font-medium md:text-4xl">
          {title}
        </h1>
      </div>
      {children ? (
        <p className="max-w-2xl text-muted-foreground">{children}</p>
      ) : null}
    </header>
  )
}
