import { Skeleton } from "@workspace/ui/components/skeleton"

// Not random widths (Math.random is not allowed while prerendering); sizes follow the real content.

/** Same grid as `CardGrid`, so the page does not jump when the cards arrive. */
export function CardGridSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: count }, (_, index) => (
        <Skeleton key={index} className="h-32 rounded-xl" />
      ))}
    </div>
  )
}

/** Title plus the label / value rows of `Spec`. */
export function SummarySkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-3">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-64" />
      </div>
      <div className="flex max-w-xl flex-col gap-3">
        {Array.from({ length: rows }, (_, index) => (
          <Skeleton key={index} className="h-5" />
        ))}
      </div>
    </div>
  )
}
