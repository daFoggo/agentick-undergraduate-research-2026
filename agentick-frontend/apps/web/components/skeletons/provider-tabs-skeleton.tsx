import { Skeleton } from "@workspace/ui/components/skeleton"

export function ProviderTabsSkeleton() {
  return (
    <div className="flex flex-col gap-4 rounded-xl border border-border/50 bg-muted/10 p-5">
      <div className="flex gap-2">
        <Skeleton className="h-8 w-24 rounded-lg" />
        <Skeleton className="h-8 w-28 rounded-lg" />
        <Skeleton className="h-8 w-24 rounded-lg" />
        <Skeleton className="h-8 w-32 rounded-lg" />
      </div>
      <div className="flex flex-col gap-3 pt-2">
        <Skeleton className="h-4 w-48" />
        <Skeleton className="h-32 w-full rounded-lg" />
        <div className="flex flex-col gap-2 pt-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      </div>
    </div>
  )
}
