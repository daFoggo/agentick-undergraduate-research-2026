"use client"

import * as PreviewLinkCardPrimitive from "@animate-ui/react/primitives/base-ui/preview-link-card"
import { cn } from "cn"

function PreviewLinkCard({
  ...props
}: PreviewLinkCardPrimitive.PreviewLinkCardProps) {
  return (
    <PreviewLinkCardPrimitive.PreviewLinkCard
      data-slot="preview-link-card"
      {...props}
    />
  )
}

function PreviewLinkCardTrigger({
  className,
  ...props
}: PreviewLinkCardPrimitive.PreviewLinkCardTriggerProps) {
  return (
    <PreviewLinkCardPrimitive.PreviewLinkCardTrigger
      data-slot="preview-link-card-trigger"
      className={cn("underline-offset-4 hover:underline", className)}
      {...props}
    />
  )
}

function PreviewLinkCardContent({
  className,
  side = "top",
  sideOffset = 8,
  align = "center",
  alignOffset = 0,
  children,
  ...props
}: PreviewLinkCardPrimitive.PreviewLinkCardPopupProps &
  Pick<
    PreviewLinkCardPrimitive.PreviewLinkCardPositionerProps,
    "align" | "alignOffset" | "side" | "sideOffset"
  >) {
  return (
    <PreviewLinkCardPrimitive.PreviewLinkCardPortal data-slot="preview-link-card-portal">
      <PreviewLinkCardPrimitive.PreviewLinkCardPositioner
        align={align}
        alignOffset={alignOffset}
        side={side}
        sideOffset={sideOffset}
        className="isolate z-50"
      >
        <PreviewLinkCardPrimitive.PreviewLinkCardPopup
          data-slot="preview-link-card-content"
          className={cn(
            "z-50 block overflow-hidden origin-(--transform-origin) rounded-lg bg-popover p-1.5 text-sm text-popover-foreground shadow-md ring-1 ring-foreground/10 outline-hidden",
            className
          )}
          {...props}
        >
          {children ?? <PreviewLinkCardImage />}
        </PreviewLinkCardPrimitive.PreviewLinkCardPopup>
      </PreviewLinkCardPrimitive.PreviewLinkCardPositioner>
    </PreviewLinkCardPrimitive.PreviewLinkCardPortal>
  )
}

function PreviewLinkCardImage({
  className,
  ...props
}: PreviewLinkCardPrimitive.PreviewLinkCardImageProps) {
  return (
    <PreviewLinkCardPrimitive.PreviewLinkCardImage
      data-slot="preview-link-card-image"
      className={cn("block rounded-md object-cover", className)}
      {...props}
    />
  )
}

const usePreviewLinkCard = PreviewLinkCardPrimitive.usePreviewLinkCard

export {
  PreviewLinkCard,
  PreviewLinkCardTrigger,
  PreviewLinkCardContent,
  PreviewLinkCardImage,
  usePreviewLinkCard,
}
