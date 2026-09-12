"use client";

import * as React from "react";
import { X } from "lucide-react";
import { APP_NAME, APP_TAGLINE, NAV_ITEMS } from "@/lib/constants";
import { useApp } from "@/lib/app-context";
import { cn } from "@/lib/utils";
import { BrandMark } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";

function SidebarInner({ onNavigate }: { onNavigate?: () => void }) {
  const { activeSection, scrollToSection, backendStatus, backendVersion, apiBaseUrl } = useApp();

  return (
    <div className="flex h-full flex-col bg-slate-900 text-slate-100">
      <div className="flex items-center gap-3 px-5 py-5">
        <BrandMark size={40} />
        <div className="min-w-0">
          <p className="truncate text-sm font-bold tracking-tight">{APP_NAME}</p>
          <p className="text-[11px] leading-tight text-slate-400">{APP_TAGLINE}</p>
        </div>
      </div>

      <nav className="mt-1 flex-1 space-y-1 px-3" aria-label="Main navigation">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = activeSection === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                scrollToSection(item.sectionId);
                onNavigate?.();
              }}
              className={cn(
                "group flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-violet-600/90 text-white shadow-md shadow-violet-900/30"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white",
              )}
            >
              <Icon
                className={cn(
                  "h-[18px] w-[18px] shrink-0",
                  active ? "text-white" : "text-slate-400 group-hover:text-slate-200",
                )}
              />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="space-y-4 px-5 pb-5">
        <div className="rounded-lg border border-slate-800 bg-slate-800/50 p-3">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "h-2 w-2 rounded-full",
                backendStatus === "online" && "bg-emerald-400 shadow-[0_0_6px] shadow-emerald-400/60",
                backendStatus === "offline" && "bg-red-400",
                backendStatus === "checking" && "bg-amber-400",
              )}
            />
            <span className="text-xs font-semibold">
              {backendStatus === "online" && "Backend connected"}
              {backendStatus === "offline" && "Backend offline"}
              {backendStatus === "checking" && "Checking backend…"}
            </span>
          </div>
          {backendVersion && <p className="mt-1 text-[11px] text-slate-400">API v{backendVersion}</p>}
          <p className="mt-0.5 truncate text-[11px] text-slate-500" title={apiBaseUrl}>
            {apiBaseUrl}
          </p>
        </div>
        <p className="text-center text-[11px] text-slate-500">
          © {new Date().getFullYear()} {APP_NAME}. All rights reserved.
        </p>
      </div>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 lg:block">
      <SidebarInner />
    </aside>
  );
}

export function MobileNav({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <div
      className={cn(
        "fixed inset-0 z-50 lg:hidden",
        open ? "pointer-events-auto" : "pointer-events-none",
      )}
      aria-hidden={!open}
    >
      <div
        className={cn(
          "absolute inset-0 bg-slate-950/50 backdrop-blur-[2px] transition-opacity",
          open ? "opacity-100" : "opacity-0",
        )}
        onClick={onClose}
      />
      <div
        className={cn(
          "absolute inset-y-0 left-0 w-72 max-w-[85%] shadow-2xl transition-transform duration-200",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <SidebarInner onNavigate={onClose} />
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="absolute left-[calc(288px+12px)] top-4 hidden h-8 w-8 text-slate-100"
        onClick={onClose}
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}