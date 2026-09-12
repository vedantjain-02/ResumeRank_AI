import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors focus:outline-none",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary/10 text-primary",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        outline: "text-foreground",
        success: "border-transparent bg-emerald-100 text-emerald-800",
        warning: "border-transparent bg-amber-100 text-amber-800",
        destructive: "border-transparent bg-red-100 text-red-700",
        info: "border-transparent bg-sky-100 text-sky-800",
        violet: "border-transparent bg-violet-100 text-violet-700",
        navy: "border-transparent bg-slate-800 text-slate-100",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export interface SelectBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  placeholder?: string;
}

function SelectBadge({ className, placeholder, children, ...props }: SelectBadgeProps) {
  return (
    <div
      className={cn(
        "flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm",
        className,
      )}
      {...props}
    >
      <span className={cn(children == null && "text-muted-foreground")}>{children || placeholder || "Select…"}</span>
      <ChevronDown className="h-4 w-4 text-muted-foreground" />
    </div>
  );
}

export { Badge, badgeVariants, SelectBadge };