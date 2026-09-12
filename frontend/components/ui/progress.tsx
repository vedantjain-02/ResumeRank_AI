import * as React from "react";
import { cn } from "@/lib/utils";

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number | null;
  indicatorClassName?: string;
}

const DEFAULT_VARIANTS: Record<string, string> = {
  primary: "bg-primary",
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  destructive: "bg-red-500",
  sky: "bg-sky-500",
  violet: "bg-violet-500",
};

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, indicatorClassName = "bg-primary", style, ...props }, ref) => {
    const clamped = Math.max(0, Math.min(100, Number(value) || 0));
    const resolved =
      DEFAULT_VARIANTS[indicatorClassName] ?? indicatorClassName ?? DEFAULT_VARIANTS.primary;
    return (
      <div
        ref={ref}
        className={cn("relative h-2 w-full overflow-hidden rounded-full bg-slate-200/70", className)}
        style={style}
        {...props}
      >
        <div
          className={cn("h-full rounded-full transition-all duration-500", resolved)}
          style={{ width: `${clamped}%` }}
        />
      </div>
    );
  },
);
Progress.displayName = "Progress";

export { Progress };