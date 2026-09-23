"use client";

import * as React from "react";
import { AlertCircle, RefreshCw, Home } from "lucide-react";
import { Button } from "@/components/ui/Button";
import Link from "next/link";
import { logger } from "@/lib/logger";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const [incidentId] = React.useState(
    () => "INC-" + Math.random().toString(36).substring(2, 8).toUpperCase()
  );

  React.useEffect(() => {
    logger.error("Unhandled UI Runtime Exception caught by Error Boundary", error, {
      action: "error_boundary_catch",
      metadata: { incidentId, digest: error.digest },
    });
  }, [error, incidentId]);

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-slate-50 dark:bg-[#070F1E]">
      <div className="max-w-md w-full bg-white dark:bg-[#0D1B2A] border border-slate-200 dark:border-slate-800 rounded-xl p-8 shadow-xl text-center space-y-5">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-100 dark:bg-red-950/60 text-red-600">
          <AlertCircle className="h-8 w-8" />
        </div>

        <div className="space-y-2">
          <h2 className="text-xl font-bold font-display text-[#062B6F] dark:text-white">
            Application Error Encountered
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            The investigation platform encountered an unexpected error. Technical telemetry has been recorded in the local audit buffer.
          </p>
        </div>

        <div className="bg-slate-100 dark:bg-slate-900/80 rounded-lg p-3 text-left space-y-1 font-mono text-xs">
          <div className="text-slate-500 text-[10px] uppercase font-sans font-bold">Incident Reference:</div>
          <div className="text-cyan-600 dark:text-cyan-400 font-bold">{incidentId}</div>
          <div className="text-slate-600 dark:text-slate-400 text-[11px] truncate">{error.message}</div>
        </div>

        <div className="flex items-center justify-center gap-3 pt-2">
          <Button onClick={() => reset()} variant="secondary" size="sm" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            <span>Retry Action</span>
          </Button>
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="gap-2">
              <Home className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
