"use client";

import * as React from "react";
import { Sparkles } from "lucide-react";
import { Toaster } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppProvider } from "@/lib/app-context";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <TooltipProvider delayDuration={300}>
      <AppProvider>
        {children}
        <Toaster
          position="top-right"
          richColors
          closeButton
          toastOptions={{ style: { fontSize: "13.5px" } }}
        />
      </AppProvider>
    </TooltipProvider>
  );
}

export function BrandMark({ size = 38 }: { size?: number }) {
  return (
    <div
      className="flex items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 text-white shadow-lg shadow-violet-600/30"
      style={{ width: size, height: size }}
    >
      <Sparkles style={{ width: size * 0.52, height: size * 0.52 }} />
    </div>
  );
}