"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export const Sheet = ({ children, open, onOpenChange }: {
  children: React.ReactNode
  open?: boolean
  onOpenChange?: (open: boolean) => void
}) => {
  return (
    <div>
      {React.Children.map(children, child => 
        React.isValidElement(child) 
          ? React.cloneElement(child as React.ReactElement, { open, onOpenChange })
          : child
      )}
    </div>
  )
}

export const SheetTrigger = ({ className, children, onOpenChange, ...props }: any) => (
  <button
    className={cn("", className)}
    onClick={() => onOpenChange?.(true)}
    {...props}
  >
    {children}
  </button>
)

export const SheetContent = ({ className, children, open, onOpenChange, side = "left", ...props }: any) => (
  open ? (
    <>
      <div 
        className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
        onClick={() => onOpenChange?.(false)}
      />
      <div
        className={cn(
          "fixed z-50 gap-4 bg-background p-6 shadow-lg transition ease-in-out",
          side === "left" && "inset-y-0 left-0 h-full w-3/4 border-r sm:max-w-sm",
          side === "right" && "inset-y-0 right-0 h-full w-3/4 border-l sm:max-w-sm",
          side === "top" && "inset-x-0 top-0 border-b",
          side === "bottom" && "inset-x-0 bottom-0 border-t",
          className
        )}
        {...props}
      >
        {children}
      </div>
    </>
  ) : null
)
