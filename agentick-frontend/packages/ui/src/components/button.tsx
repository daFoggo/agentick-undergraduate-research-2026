"use client"

import { Button as ButtonPrimitive } from "@base-ui/react/button"
import { type VariantProps } from "class-variance-authority"
import { cn } from "cn"

import { buttonVariants } from "@workspace/ui/components/button-variants"

function unwrapLazyRender(
  render: ButtonPrimitive.Props["render"]
): ButtonPrimitive.Props["render"] {
  if (
    typeof render === "object" &&
    render !== null &&
    "_init" in render &&
    typeof (render as { _init?: unknown })._init === "function" &&
    "_payload" in render
  ) {
    return (
      render as {
        _init: (payload: unknown) => ButtonPrimitive.Props["render"]
        _payload: unknown
      }
    )._init((render as { _payload: unknown })._payload)
  }
  return render
}

function Button({
  className,
  variant = "default",
  size = "default",
  render,
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      render={unwrapLazyRender(render)}
      {...props}
    />
  )
}

export { Button, buttonVariants }
