"use client"

import * as React from "react"
import * as AvatarGroupPrimitive from "@animate-ui/react/primitives/avatar-group"
import { cn } from "cn"

type AvatarGroupProps = AvatarGroupPrimitive.AvatarGroupProps

function AvatarGroup({
  className,
  invertOverlap = true,
  sideOffset = 12,
  ...props
}: AvatarGroupProps) {
  return (
    <AvatarGroupPrimitive.AvatarGroup
      data-slot="animate-avatar-group"
      invertOverlap={invertOverlap}
      sideOffset={sideOffset}
      className={cn(
        "flex items-center -space-x-2 *:data-[slot=avatar]:ring-2 *:data-[slot=avatar]:ring-background",
        className
      )}
      {...props}
    />
  )
}

type AvatarGroupTooltipProps = Omit<
  AvatarGroupPrimitive.AvatarGroupTooltipProps,
  "asChild" | "children"
> & {
  children?: React.ReactNode
}

function AvatarGroupTooltip({
  className,
  children,
  ...props
}: AvatarGroupTooltipProps) {
  return (
    <AvatarGroupPrimitive.AvatarGroupTooltip
      data-slot="animate-avatar-group-tooltip"
      className={cn(
        "z-50 inline-flex w-fit max-w-xs items-center gap-1.5 rounded-md bg-foreground px-3 py-1.5 text-xs text-background",
        className
      )}
      {...props}
    >
      <AvatarGroupTooltipArrow />
      {children}
    </AvatarGroupPrimitive.AvatarGroupTooltip>
  )
}

type AvatarGroupTooltipArrowProps =
  AvatarGroupPrimitive.AvatarGroupTooltipArrowProps

function AvatarGroupTooltipArrow({
  className,
  ...props
}: AvatarGroupTooltipArrowProps) {
  return (
    <AvatarGroupPrimitive.AvatarGroupTooltipArrow
      data-slot="animate-avatar-group-tooltip-arrow"
      className={cn("size-2.5 fill-foreground", className)}
      {...props}
    />
  )
}

export {
  AvatarGroup,
  AvatarGroupTooltip,
  AvatarGroupTooltipArrow,
  type AvatarGroupProps,
  type AvatarGroupTooltipProps,
  type AvatarGroupTooltipArrowProps,
}
