import { Skeleton } from "@workspace/ui/components/skeleton"

export function FaqSkeleton() {
  return (
    <div className="flex flex-col divide-y divide-border/40 border-t border-border/40">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex flex-col gap-2 py-4">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
        </div>
      ))}
    </div>
  )
}
