import * as React from "react";
import { cn } from "@/lib/utils";

export const Badge = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
        className
      )}
      {...props}
    />
  )
);
Badge.displayName = "Badge";
