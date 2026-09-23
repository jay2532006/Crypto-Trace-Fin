"use client";

import * as React from "react";
import { Bug, X, Copy, Check, RefreshCw, Trash2, Activity } from "lucide-react";
import { useDebugStore } from "@/stores/debug-store";
import { useAuthStore } from "@/stores/auth-store";
import { usePathname } from "next/navigation";

export function DebugPanel() {
  const { isOpen, toggleOpen, activeTab, setActiveTab, logs, refreshLogs, clearLogs } = useDebugStore();
  const { session } = useAuthStore();
  const pathname = usePathname();
  const [copied, setCopied] = React.useState(false);

  React.useEffect(() => {
    refreshLogs();
  }, [refreshLogs, isOpen]);

  if (process.env.NEXT_PUBLIC_ENABLE_DEBUG_PANEL !== "true") {
    return null;
  }

  const handleCopyReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      route: pathname,
      userRole: session?.role || "ANONYMOUS",
      unit: session?.unit || "N/A",
      logCount: logs.length,
      recentLogs: logs.slice(0, 20),
    };
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          onClick={toggleOpen}
          className="fixed bottom-4 right-4 z-40 flex items-center gap-2 rounded-full bg-[#062B6F] px-3.5 py-2 text-xs font-semibold text-white shadow-lg hover:bg-[#082B63] transition-all border border-[#1F66B8]/40"
          title="Open Developer & Forensics Debug Panel"
        >
          <Bug className="h-4 w-4 text-[#E5A33D]" />
          <span>Debug Console</span>
          {logs.length > 0 && (
            <span className="flex h-4 w-4 items-center justify-center rounded-full bg-[#1F66B8] text-[10px]">
              {logs.length}
            </span>
          )}
        </button>
      )}

      {/* Floating Debug Drawer */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 z-50 flex h-[480px] w-[540px] flex-col rounded-xl border border-slate-700 bg-slate-900 text-slate-100 shadow-2xl overflow-hidden font-mono text-xs">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950 px-4 py-2.5">
            <div className="flex items-center gap-2 font-bold text-slate-200">
              <Bug className="h-4 w-4 text-[#E5A33D]" />
              <span className="font-sans text-xs tracking-wide">CryptoTrace Telemetry & Debug Console</span>
            </div>
            <div className="flex items-center gap-1.5">
              <button
                onClick={handleCopyReport}
                className="flex items-center gap-1 rounded bg-slate-800 px-2 py-1 text-[11px] text-slate-300 hover:bg-slate-700"
                title="Copy sanitized JSON diagnostic report"
              >
                {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copied ? "Copied" : "Diagnostic"}</span>
              </button>
              <button onClick={refreshLogs} className="rounded p-1 text-slate-400 hover:text-white" title="Refresh logs">
                <RefreshCw className="h-3.5 w-3.5" />
              </button>
              <button onClick={clearLogs} className="rounded p-1 text-slate-400 hover:text-red-400" title="Clear logs">
                <Trash2 className="h-3.5 w-3.5" />
              </button>
              <button onClick={toggleOpen} className="rounded p-1 text-slate-400 hover:text-white" title="Close">
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Subheader Context */}
          <div className="grid grid-cols-3 border-b border-slate-800 bg-slate-900/90 px-4 py-2 text-[11px] text-slate-400 font-sans">
            <div>
              Route: <span className="font-mono text-cyan-400">{pathname}</span>
            </div>
            <div>
              Role: <span className="font-bold text-emerald-400">{session?.role || "GUEST"}</span>
            </div>
            <div>
              Service: <span className="text-slate-300">FastAPI :8765</span>
            </div>
          </div>

          {/* Logs View */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-[#070F1E]">
            {logs.length === 0 ? (
              <div className="flex h-full items-center justify-center text-slate-500 font-sans text-xs">
                No telemetry events logged yet. Perform actions to capture logs.
              </div>
            ) : (
              logs.map((log, index) => {
                const badgeColor =
                  log.level === "ERROR" || log.level === "FATAL"
                    ? "bg-red-950 text-red-400 border-red-800"
                    : log.level === "WARN"
                    ? "bg-amber-950 text-amber-400 border-amber-800"
                    : log.level === "INFO"
                    ? "bg-blue-950 text-blue-300 border-blue-800"
                    : "bg-slate-800 text-slate-400 border-slate-700";

                return (
                  <div
                    key={index}
                    className="rounded border border-slate-800/80 bg-slate-900/60 p-2 text-[11px] space-y-1 hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-center justify-between text-[10px]">
                      <span className={`px-1.5 py-0.5 rounded border font-bold ${badgeColor}`}>{log.level}</span>
                      <span className="text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className="text-slate-200 font-semibold">{log.message}</div>
                    {(log.endpoint || log.durationMs || log.requestId) && (
                      <div className="flex flex-wrap gap-2 text-[10px] text-slate-400">
                        {log.endpoint && <span>URI: {log.endpoint}</span>}
                        {log.durationMs !== undefined && <span className="text-amber-300">{log.durationMs}ms</span>}
                        {log.httpStatus && <span className="text-cyan-300">HTTP {log.httpStatus}</span>}
                        {log.requestId && <span className="text-slate-500">ID: {log.requestId}</span>}
                      </div>
                    )}
                    {log.error && (
                      <div className="rounded bg-red-950/40 p-1.5 text-red-300 font-mono text-[10px]">
                        {log.error.name}: {log.error.message}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </>
  );
}
