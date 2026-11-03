"use client"

import {
  SlidingNumber as SlidingNumberPrimitive,
  type SlidingNumberProps,
} from "@animate-ui/react/primitives/texts/sliding-number"
import { cn } from "cn"

function SlidingNumber({ className, ...props }: SlidingNumberProps) {
  return (
    <SlidingNumberPrimitive
      data-slot="sliding-number"
      className={cn("tabular-nums", className)}
      {...props}
    />
  )
}

export { SlidingNumber, type SlidingNumberProps }
