"use client"

import {
  CountingNumber as CountingNumberPrimitive,
  type CountingNumberProps,
} from "@animate-ui/react/primitives/texts/counting-number"
import { cn } from "cn"

function CountingNumber({ className, ...props }: CountingNumberProps) {
  return (
    <CountingNumberPrimitive
      data-slot="counting-number"
      className={cn("tabular-nums", className)}
      {...props}
    />
  )
}

export { CountingNumber, type CountingNumberProps }
