"use client"

import * as React from "react"
import {
  CopyButton as CopyButtonPrimitive,
  CopyButtonIcon as CopyButtonIconPrimitive,
  useCopyButton,
  type CopyButtonContextType,
  type CopyButtonIconProps as CopyButtonIconPrimitiveProps,
  type CopyButtonProps as CopyButtonPrimitiveProps,
} from "@animate-ui/react/primitives/buttons/copy"
import { IconCheck, IconCopy } from "@tabler/icons-react"
import { type VariantProps } from "class-variance-authority"
import { cn } from "cn"

import { buttonVariants } from "@workspace/ui/components/button"

type CopyButtonProps = Omit<CopyButtonPrimitiveProps, "asChild" | "children"> &
  VariantProps<typeof buttonVariants> & {
    icon?: React.ReactNode
    copiedIcon?: React.ReactNode
    children?: React.ReactNode
  }

function CopyButton({
  className,
  variant = "outline",
  size = "icon",
  icon,
  copiedIcon,
  children,
  ...props
}: CopyButtonProps) {
  return (
    <CopyButtonPrimitive
      data-slot="copy-button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    >
      {children ?? <CopyButtonIcon icon={icon} copiedIcon={copiedIcon} />}
    </CopyButtonPrimitive>
  )
}

type CopyButtonIconProps = Omit<
  CopyButtonIconPrimitiveProps,
  "icon" | "copiedIcon"
> & {
  icon?: React.ReactNode
  copiedIcon?: React.ReactNode
}

function CopyButtonIcon({
  icon = <IconCopy />,
  copiedIcon = <IconCheck />,
  ...props
}: CopyButtonIconProps) {
  return (
    <CopyButtonIconPrimitive
      data-slot="copy-button-icon"
      icon={icon}
      copiedIcon={copiedIcon}
      {...props}
    />
  )
}

export {
  CopyButton,
  CopyButtonIcon,
  useCopyButton,
  type CopyButtonProps,
  type CopyButtonIconProps,
  type CopyButtonContextType,
}
