import { Skeleton } from "@workspace/ui/components/skeleton"

export function MonorepoMapSkeleton() {
  return (
    <div className="flex flex-col gap-4 rounded-xl border border-border/50 bg-muted/10 p-5">
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-36" />
        <Skeleton className="h-4 w-20" />
      </div>
      <div className="flex flex-col gap-3 pt-2">
        <div className="grid grid-cols-2 gap-3">
          <Skeleton className="h-24 w-full rounded-lg" />
          <Skeleton className="h-24 w-full rounded-lg" />
        </div>
        <Skeleton className="h-28 w-full rounded-lg" />
      </div>
    </div>
  )
}
