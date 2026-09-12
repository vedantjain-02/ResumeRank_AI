"use client";

import * as React from "react";
import { Menu, RefreshCw } from "lucide-react";
import { PAGE_META } from "@/lib/constants";
import { useApp } from "@/lib/app-context";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function AppHeader({ onMenu }: { onMenu: () => void }) {
  const { activeSection, backendStatus, backendVersion, refreshAll } = useApp();
  const [refreshing, setRefreshing] = React.useState(false);
  const meta = PAGE_META[activeSection] ?? PAGE_META.dashboard;

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    try {
      await refreshAll();
    } finally {
      setRefreshing(false);
    }
  }, [refreshAll]);

  return (
    <header className="sticky top-0 z-30 border-b bg-background/85 backdrop-blur">
      <div className="flex h-16 items-center gap-3 px-4 sm:px-6">
        <Button variant="ghost" size="icon" className="lg:hidden" onClick={onMenu} aria-label="Open menu">
          <Menu className="h-5 w-5" />
        </Button>

        <div className="min-w-0 flex-1">
          <h1 className="truncate text-base font-bold tracking-tight text-slate-900">{meta.title}</h1>
          <p className="hidden truncate text-xs text-muted-foreground sm:block">{meta.description}</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 sm:flex">
            <span
              className={cn(
                "h-2 w-2 rounded-full",
                backendStatus === "online" && "bg-emerald-500",
                backendStatus === "offline" && "bg-red-500",
                backendStatus === "checking" && "bg-amber-400",
              )}
            />
            <span className="text-xs font-medium text-muted-foreground">
              {backendStatus === "online" && (
                <>
                  API{" "}
                  <Badge variant="success" className="font-mono">
                    v{backendVersion}
                  </Badge>
                </>
              )}
              {backendStatus === "offline" && "Backend unreachable"}
              {backendStatus === "checking" && "Checking…"}
            </span>
          </div>
          <Button variant="outline" size="sm" onClick={onRefresh} disabled={refreshing}>
            <RefreshCw className={cn("h-3.5 w-3.5", refreshing && "animate-spin")} />
            Refresh
          </Button>
        </div>
      </div>
    </header>
  );
}