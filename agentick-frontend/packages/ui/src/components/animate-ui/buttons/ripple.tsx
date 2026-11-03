"use client"

import * as React from "react"
import {
  RippleButton as RippleButtonPrimitive,
  RippleButtonRipples as RippleButtonRipplesPrimitive,
  type RippleButtonProps as RippleButtonPrimitiveProps,
  type RippleButtonRipplesProps,
} from "@animate-ui/react/primitives/buttons/ripple"
import { type VariantProps } from "class-variance-authority"
import { cn } from "cn"

import { buttonVariants } from "@workspace/ui/components/button"

type RippleButtonProps = Omit<
  RippleButtonPrimitiveProps,
  "asChild" | "children"
> &
  VariantProps<typeof buttonVariants> & {
    children?: React.ReactNode
  }

function RippleButton({
  className,
  variant = "default",
  size = "default",
  children,
  ...props
}: RippleButtonProps) {
  return (
    <RippleButtonPrimitive
      data-slot="ripple-button"
      className={cn(
        "relative overflow-hidden",
        buttonVariants({ variant, size, className })
      )}
      {...props}
    >
      {children}
      <RippleButtonRipples />
    </RippleButtonPrimitive>
  )
}

function RippleButtonRipples({
  color = "currentColor",
  className,
  ...props
}: RippleButtonRipplesProps) {
  return (
    <RippleButtonRipplesPrimitive
      color={color}
      className={cn("pointer-events-none opacity-20", className)}
      {...props}
    />
  )
}

export {
  RippleButton,
  RippleButtonRipples,
  type RippleButtonProps,
  type RippleButtonRipplesProps,
}
