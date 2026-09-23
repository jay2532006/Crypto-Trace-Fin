import * as React from "react";
import { AlertTriangle } from "lucide-react";

interface UncertaintyBannerProps {
  note?: string;
  description?: string;
  title?: string;
  ruleTitle?: string;
  level?: string;
}

export function UncertaintyBanner({
  note,
  description,
  title,
  ruleTitle,
  level,
}: UncertaintyBannerProps) {
  const displayTitle = title || ruleTitle || "Mandatory Uncertainty Disclosure (PRD §9)";
  const displayNote =
    description ||
    note ||
    "Automated typology heuristic. Intermediate addresses may represent non-custodial aggregators or automated payment processors. Field corroboration and lawful Section 91 KYC disclosure required before judicial freezing.";

  const isHigh = (level || "").toUpperCase() === "HIGH";

  return (
    <div
      className={`rounded-lg border p-3.5 text-xs ${
        isHigh
          ? "border-red-800 bg-red-950/30 text-red-200"
          : "border-[#E5A33D]/40 bg-amber-500/10 text-amber-900 dark:text-amber-200"
      }`}
    >
      <div className="flex items-start gap-2.5">
        <AlertTriangle
          className={`h-4 w-4 flex-shrink-0 mt-0.5 ${
            isHigh ? "text-red-400" : "text-[#E5A33D]"
          }`}
        />
        <div className="space-y-1">
          <p
            className={`font-bold uppercase tracking-wide text-[11px] ${
              isHigh ? "text-red-400" : "text-[#E5A33D]"
            }`}
          >
            {displayTitle}
          </p>
          <p className="leading-relaxed opacity-95 text-slate-200">{displayNote}</p>
        </div>
      </div>
    </div>
  );
}
