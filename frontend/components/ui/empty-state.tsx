import * as React from "react";
import { Icon, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
  compact?: boolean;
}

export function EmptyState({
  icon: IconComponent,
  title,
  description,
  action,
  compact,
  className,
  ...props
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-dashed bg-slate-50/60 text-center",
        compact ? "px-4 py-6" : "px-6 py-12",
        className,
      )}
      {...props}
    >
      {IconComponent && (
        <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-primary/10 text-primary">
          <IconComponent className="h-5 w-5" />
        </div>
      )}
      <h3 className={cn("font-semibold text-slate-800", compact ? "text-sm" : "text-base")}>{title}</h3>
      {description && (
        <p className={cn("mt-1 max-w-md text-muted-foreground", compact ? "text-xs" : "text-sm")}>
          {description}
        </p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}