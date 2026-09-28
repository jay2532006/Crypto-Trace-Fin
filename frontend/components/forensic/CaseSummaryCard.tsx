import { Button } from "@/components/ui/Button";
// frontend/components/forensic/CaseSummaryCard.tsx
import * as React from "react";
import { Building2, ShieldCheck, ChevronDown, ChevronUp, Info, Scale, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { ConfidencePill } from "@/components/forensic/ConfidencePill";
import type { AttributionScore, ScoringStep } from "@/types/domain";

interface CaseSummaryCardProps {
  attribution?: AttributionScore | null;
  hopDistance?: number;
  caseId?: string;
  dataCompletenessPct?: number;
}

export function CaseSummaryCard({
  attribution,
  hopDistance = 1,
  caseId,
  dataCompletenessPct = 100,
}: CaseSummaryCardProps) {
  const [accordionOpen, setAccordionOpen] = React.useState(false);

  if (!attribution) {
    return null;
  }

  const isVerified = attribution.label_type === "VERIFIED";
  const isInferred = attribution.label_type === "INFERRED";
  const isUnresolved = attribution.label_type === "UNRESOLVED";

  return (
    <div className="rounded-xl border border-slate-800 bg-gradient-to-r from-slate-900/90 via-[#062B6F]/20 to-slate-900/90 p-5 shadow-xl backdrop-blur space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* VASP Profile */}
        <div className="flex items-center gap-3.5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600/20 border border-blue-500/40 text-blue-400">
            <Building2 className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                Attributed Destination Entity
              </span>
              <Badge 
                className={`text-[10px] font-bold ${
                  isVerified 
                    ? "bg-emerald-600 text-white" 
                    : isInferred 
                    ? "bg-amber-600 text-white" 
                    : "bg-slate-700 text-slate-300"
                }`}
              >
                {attribution.label_type}
              </Badge>
            </div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              {attribution.vasp_name || "Unresolved Off-Ramp"}
            </h3>
            <p className="text-xs text-slate-400">
              Nodal Contact: <span className="font-mono text-cyan-300">{attribution.nodal_officer_email || "compliance@exchange.com"}</span> | FIU Status: <span className="text-emerald-400 font-semibold">{attribution.fiu_status || "REGISTERED"}</span>
            </p>
          </div>
        </div>

        {/* Metrics & Confidence Band */}
        <div className="flex items-center gap-4 flex-wrap md:flex-nowrap">
          <div className="text-right">
            <span className="text-[10px] text-slate-400 block font-mono">Attribution Confidence</span>
            <div className="mt-0.5">
              <ConfidencePill confidence={attribution.confidence_band} />
            </div>
          </div>

          <div className="h-9 w-px bg-slate-800 hidden md:block" />

          <div className="text-right">
            <span className="text-[10px] text-slate-400 block font-mono">Forensic Hop Distance</span>
            <span className="text-sm font-bold text-white font-mono">{hopDistance} Hops</span>
          </div>

          <div className="h-9 w-px bg-slate-800 hidden md:block" />

          <div className="text-right">
            <span className="text-[10px] text-slate-400 block font-mono">Data Completeness</span>
            <span className={`text-sm font-bold font-mono ${dataCompletenessPct < 70 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {dataCompletenessPct.toFixed(1)}%
            </span>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setAccordionOpen(!accordionOpen)}
            className="text-xs border-slate-700 hover:bg-slate-800 text-slate-300 ml-2"
          >
            {accordionOpen ? (
              <>Less <ChevronUp className="h-3.5 w-3.5 ml-1" /></>
            ) : (
              <>Scoring Steps ({attribution.scoring_steps?.length || 0}) <ChevronDown className="h-3.5 w-3.5 ml-1" /></>
            )}
          </Button>
        </div>
      </div>

      {/* Expandable 6-Step Scoring Accordion */}
      {accordionOpen && attribution.scoring_steps && (
        <div className="pt-4 border-t border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Scale className="h-4 w-4 text-blue-400" />
              AdaptiveVASPScorer (PRD 6-Step Mathematical Audit Breakdown)
            </span>
            <span className="text-[11px] font-mono text-slate-400">
              Policy: {attribution.policy_version} | Final Score: {attribution.score}/100
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {attribution.scoring_steps.map((step: any, idx: number) => (
              <div key={idx} className="rounded-lg border border-slate-800 bg-black/40 p-2.5 space-y-1 text-xs">
                <div className="flex items-center justify-between font-mono text-[10px]">
                  <span className="font-semibold text-cyan-300 truncate">{step.step_name}</span>
                  <span className={step.output_contribution >= 0 ? "text-emerald-400" : "text-red-400"}>
                    {step.output_contribution >= 0 ? `+${step.output_contribution.toFixed(1)}` : step.output_contribution.toFixed(1)}
                  </span>
                </div>
                <p className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
                  {step.reasoning}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
