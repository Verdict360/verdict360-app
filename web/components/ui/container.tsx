import { cn } from "@/lib/utils";

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg" | "xl" | "full";
  gutter?: boolean;
}

export function Container({
  children,
  className,
  size = "lg",
  gutter = true,
  ...props
}: ContainerProps) {
  return (
    <div
      className={cn(
        "mx-auto w-full",
        {
          "max-w-screen-sm": size === "sm",
          "max-w-screen-md": size === "md",
          "max-w-screen-lg": size === "lg",
          "max-w-screen-xl": size === "xl",
          "max-w-none": size === "full",
          "px-4 sm:px-6 lg:px-8": gutter,
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
