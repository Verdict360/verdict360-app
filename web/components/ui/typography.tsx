import { cn } from "@/lib/utils";

interface HeadingProps extends React.HTMLAttributes<HTMLHeadingElement> {
  as?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
  size?: "xs" | "sm" | "md" | "lg" | "xl" | "2xl" | "3xl";
}

export function Heading({
  as: Component = "h2",
  size = "lg",
  className,
  children,
  ...props
}: HeadingProps) {
  return (
    <Component
      className={cn(
        "font-heading leading-tight tracking-tight",
        {
          "text-xl md:text-2xl lg:text-3xl": size === "3xl",
          "text-lg md:text-xl lg:text-2xl": size === "2xl",
          "text-base md:text-lg lg:text-xl": size === "xl",
          "text-sm md:text-base lg:text-lg": size === "lg",
          "text-xs md:text-sm lg:text-base": size === "md",
          "text-xs md:text-xs lg:text-sm": size === "sm",
          "text-xs": size === "xs",
        },
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

interface TextProps extends React.HTMLAttributes<HTMLParagraphElement> {
  size?: "xs" | "sm" | "md" | "lg";
  as?: "p" | "span" | "div";
}

export function Text({
  as: Component = "p",
  size = "md",
  className,
  children,
  ...props
}: TextProps) {
  return (
    <Component
      className={cn(
        "leading-normal",
        {
          "text-xs": size === "xs",
          "text-sm": size === "sm",
          "text-base": size === "md",
          "text-lg": size === "lg",
        },
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

export function LegalCitation({
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "font-mono text-xs md:text-sm bg-muted px-1 py-0.5 rounded-sm",
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
