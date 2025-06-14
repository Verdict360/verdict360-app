"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronDown } from "lucide-react"

export const Select = ({ children, value, onValueChange }: {
  children: React.ReactNode
  value?: string
  onValueChange?: (value: string) => void
}) => {
  const [isOpen, setIsOpen] = React.useState(false)
  const [selectedValue, setSelectedValue] = React.useState(value || "")

  const handleValueChange = (newValue: string) => {
    setSelectedValue(newValue)
    onValueChange?.(newValue)
    setIsOpen(false)
  }

  return (
    <div className="relative">
      {React.Children.map(children, child => 
        React.isValidElement(child) 
          ? React.cloneElement(child as React.ReactElement, { 
              isOpen, 
              setIsOpen, 
              selectedValue, 
              onValueChange: handleValueChange 
            })
          : child
      )}
    </div>
  )
}

export const SelectValue = ({ placeholder }: { placeholder?: string }) => (
  <span className="text-sm">{placeholder}</span>
)

export const SelectTrigger = ({ className, children, isOpen, setIsOpen, ...props }: any) => (
  <button
    type="button"
    className={cn(
      "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    onClick={() => setIsOpen?.(!isOpen)}
    {...props}
  >
    {children}
    <ChevronDown className="h-4 w-4 opacity-50" />
  </button>
)

export const SelectContent = ({ className, children, isOpen, ...props }: any) => (
  isOpen ? (
    <div
      className={cn(
        "absolute z-50 w-full mt-1 bg-popover border rounded-md shadow-lg max-h-60 overflow-auto",
        className
      )}
      {...props}
    >
      {children}
    </div>
  ) : null
)

export const SelectItem = ({ className, children, value, onValueChange, ...props }: any) => (
  <div
    className={cn(
      "relative flex cursor-pointer select-none items-center rounded-sm py-2 px-3 text-sm outline-none hover:bg-accent hover:text-accent-foreground",
      className
    )}
    onClick={() => onValueChange?.(value)}
    {...props}
  >
    {children}
  </div>
)

export const SelectGroup = ({ children }: { children: React.ReactNode }) => (
  <div>{children}</div>
)

export const SelectLabel = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("py-1.5 pl-8 pr-2 text-sm font-semibold", className)}
    {...props}
  >
    {children}
  </div>
)

export const SelectSeparator = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("-mx-1 my-1 h-px bg-muted", className)}
    {...props}
  />
)
