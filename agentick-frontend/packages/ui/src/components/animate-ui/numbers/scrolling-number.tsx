"use client"

import {
  ScrollingNumber as ScrollingNumberPrimitive,
  ScrollingNumberContainer as ScrollingNumberContainerPrimitive,
  ScrollingNumberHighlight as ScrollingNumberHighlightPrimitive,
  ScrollingNumberItems as ScrollingNumberItemsPrimitive,
  useScrollingNumber,
  type ScrollingNumberContainerProps,
  type ScrollingNumberContextType,
  type ScrollingNumberDirection,
  type ScrollingNumberHighlightProps,
  type ScrollingNumberItemsProps,
  type ScrollingNumberProps,
} from "@animate-ui/react/primitives/texts/scrolling-number"
import { cn } from "cn"

function ScrollingNumberContainer({
  className,
  ...props
}: ScrollingNumberContainerProps) {
  return (
    <ScrollingNumberContainerPrimitive
      data-slot="scrolling-number-container"
      className={cn("tabular-nums", className)}
      {...props}
    />
  )
}

function ScrollingNumber(props: ScrollingNumberProps) {
  return <ScrollingNumberPrimitive data-slot="scrolling-number" {...props} />
}

function ScrollingNumberItems(props: ScrollingNumberItemsProps) {
  return (
    <ScrollingNumberItemsPrimitive
      data-slot="scrolling-number-items"
      {...props}
    />
  )
}

function ScrollingNumberHighlight(props: ScrollingNumberHighlightProps) {
  return (
    <ScrollingNumberHighlightPrimitive
      data-slot="scrolling-number-highlight"
      {...props}
    />
  )
}

export {
  ScrollingNumber,
  ScrollingNumberContainer,
  ScrollingNumberHighlight,
  ScrollingNumberItems,
  useScrollingNumber,
  type ScrollingNumberContainerProps,
  type ScrollingNumberContextType,
  type ScrollingNumberDirection,
  type ScrollingNumberHighlightProps,
  type ScrollingNumberItemsProps,
  type ScrollingNumberProps,
}
