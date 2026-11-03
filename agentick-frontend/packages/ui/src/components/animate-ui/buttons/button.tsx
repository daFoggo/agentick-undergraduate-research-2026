"use client"

import {
  Button as ButtonPrimitive,
  type ButtonProps as ButtonPrimitiveProps,
} from "@animate-ui/react/primitives/buttons/button"
import { type VariantProps } from "class-variance-authority"
import { cn } from "cn"

import { buttonVariants } from "@workspace/ui/components/button"

type ButtonProps = ButtonPrimitiveProps & VariantProps<typeof buttonVariants>

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonProps) {
  return (
    <ButtonPrimitive
      data-slot="animate-button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants, type ButtonProps }
