// frontend/components/forensic/TimeToActionBanner.tsx
import * as React from "react";
import { Clock, AlertTriangle, ShieldCheck, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import type { RecoveryAssessment } from "@/types/domain";

interface TimeToActionBannerProps {
  recovery?: RecoveryAssessment | null;
  elapsedHours?: number;
}

export function TimeToActionBanner({
  recovery,
  elapsedHours = 2.5,
}: TimeToActionBannerProps) {
  if (!recovery) {
    return null;
  }

  const isEligible = recovery.display_tier === "eligible";
  const actionWindow = recovery.action_window_hours || 0;
  const isUrgent = actionWindow > 0 && actionWindow < 6;
  const isModerate = actionWindow >= 6 && actionWindow <= 24;

  if (!isEligible) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 text-xs text-slate-300 shadow-md space-y-1.5">
        <div className="flex items-center gap-2 text-slate-400 font-bold uppercase tracking-wider text-[11px]">
          <AlertCircle className="h-4 w-4 text-amber-400" />
          <span>Heuristic Recovery Estimate ? Case Ineligible</span>
          <Badge variant="outline" className="text-[10px] border-slate-600 text-slate-400">
            INELIGIBLE
          </Badge>
        </div>
        <p className="text-slate-400 leading-relaxed pl-6 text-[11px]">
          {recovery.calculation_basis || "Case does not meet minimum actionable financial value threshold ($120 USD) or fund path crossed cryptographic obfuscation boundaries."}
        </p>
      </div>
    );
  }

  const deadline = new Date();
  deadline.setHours(deadline.getHours() + actionWindow);

  return (
    <div
      className={`rounded-xl border p-4 shadow-xl backdrop-blur transition-all ${
        isUrgent
          ? "border-red-500/50 bg-gradient-to-r from-red-950/40 via-red-900/20 to-slate-900 text-red-200"
          : isModerate
          ? "border-amber-500/50 bg-gradient-to-r from-amber-950/40 via-amber-900/20 to-slate-900 text-amber-200"
          : "border-blue-500/50 bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-900 text-blue-200"
      }`}
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded-lg border ${
              isUrgent
                ? "bg-red-600/20 border-red-500/50 text-red-400 animate-pulse"
                : isModerate
                ? "bg-amber-600/20 border-amber-500/50 text-amber-400"
                : "bg-blue-600/20 border-blue-500/50 text-blue-400"
            }`}
          >
            <Clock className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-wider font-semibold opacity-80">
                Action Window & Freeze Priority
              </span>
              <Badge
                className={`text-[10px] font-bold ${
                  isUrgent ? "bg-red-600 text-white" : isModerate ? "bg-amber-600 text-white" : "bg-blue-600 text-white"
                }`}
              >
                {isUrgent ? "CRITICAL ACTION REQUIRED" : isModerate ? "ACTIVE WINDOW" : "STANDARD WINDOW"}
              </Badge>
            </div>
            <h4 className="text-sm font-bold text-white tracking-tight mt-0.5">
              Estimated Action Window: <span className="font-mono text-cyan-300 font-extrabold">{actionWindow} Hours</span> ? Section 91 Freeze Request Recommended Now
            </h4>
          </div>
        </div>

        <div className="text-right text-xs space-y-0.5">
          <span className="text-[11px] text-slate-400 font-mono block">
            Target Requisition Deadline: <span className="text-white font-bold">{deadline.toLocaleTimeString()} ({deadline.toLocaleDateString()})</span>
          </span>
          <span className="text-[10px] opacity-75">
            Recovery Urgency Score: <span className="font-bold text-white font-mono">{recovery.recovery_score}/100</span>
          </span>
        </div>
      </div>
    </div>
  );
}
