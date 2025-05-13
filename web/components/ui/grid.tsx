import { cn } from "@/lib/utils";

interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  cols?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: "none" | "sm" | "md" | "lg";
}

export function Grid({
  children,
  className,
  cols = { xs: 1, sm: 2, md: 3, lg: 4 },
  gap = "md",
  ...props
}: GridProps) {
  return (
    <div
      className={cn(
        "grid",
        {
          "grid-cols-1": cols.xs === 1,
          "grid-cols-2": cols.xs === 2,
          "grid-cols-3": cols.xs === 3,
          "grid-cols-4": cols.xs === 4,
          "sm:grid-cols-1": cols.sm === 1,
          "sm:grid-cols-2": cols.sm === 2,
          "sm:grid-cols-3": cols.sm === 3,
          "sm:grid-cols-4": cols.sm === 4,
          "md:grid-cols-1": cols.md === 1,
          "md:grid-cols-2": cols.md === 2,
          "md:grid-cols-3": cols.md === 3,
          "md:grid-cols-4": cols.md === 4,
          "lg:grid-cols-1": cols.lg === 1,
          "lg:grid-cols-2": cols.lg === 2,
          "lg:grid-cols-3": cols.lg === 3,
          "lg:grid-cols-4": cols.lg === 4,
          "xl:grid-cols-1": cols.xl === 1,
          "xl:grid-cols-2": cols.xl === 2,
          "xl:grid-cols-3": cols.xl === 3,
          "xl:grid-cols-4": cols.xl === 4,
          "gap-0": gap === "none",
          "gap-2": gap === "sm",
          "gap-4": gap === "md",
          "gap-6": gap === "lg",
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
