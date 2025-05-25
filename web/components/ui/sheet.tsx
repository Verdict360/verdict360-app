import * as React from "react"
import { cn } from "@/lib/utils"

const Sheet = ({ children, open, onOpenChange }: { 
  children: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}) => {
  return <div>{children}</div>
}

const SheetTrigger = React.forwardRef
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { asChild?: boolean }
>(({ className, children, ...props }, ref) => (
  <button
    ref={ref}
    className={cn("", className)}
    {...props}
  >
    {children}
  </button>
))
SheetTrigger.displayName = "SheetTrigger"

const SheetContent = React.forwardRef
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { side?: "left" | "right" | "top" | "bottom" }
>(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "fixed inset-y-0 left-0 z-50 h-full w-3/4 border-r bg-background p-6 shadow-lg transition ease-in-out sm:max-w-sm",
      className
    )}
    {...props}
  >
    {children}
  </div>
))
SheetContent.displayName = "SheetContent"

export {
  Sheet,
  SheetTrigger,
  SheetContent,
}
