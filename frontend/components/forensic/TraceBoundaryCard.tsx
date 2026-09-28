// frontend/components/forensic/TraceBoundaryCard.tsx
import * as React from "react";
import { ShieldAlert, AlertOctagon, HelpCircle, CheckCircle2, Lock } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface BoundaryEvent {
  kind: string;
  name: string;
  address: string;
  hop_number: number;
  deposit_amount: number;
  asset: string;
  why_stopped: string;
  search_window_seconds: number;
}

interface PartialRecommendation {
  boundary_type: string;
  mixer_name: string;
  mixer_address: string;
  deposit_tx_hash?: string;
  deposit_amount: number;
  asset: string;
  pre_mixer_freeze_targets: string[];
  evidentiary_summary: string;
  payout_candidates: Array<{
    tx_hash: string;
    recipient: string;
    amount: number;
    asset: string;
    time_delta_seconds: number;
    relationship_label: string;
    confidence: number;
    disclaimer: string;
  }>;
  off_chain_actions: string[];
  disclaimer: string;
}

interface TraceBoundaryCardProps {
  boundaryEvents?: BoundaryEvent[];
  partialRecommendation?: PartialRecommendation | null;
  terminationReason?: string;
}

export function TraceBoundaryCard({
  boundaryEvents = [],
  partialRecommendation,
  terminationReason,
}: TraceBoundaryCardProps) {
  if (!boundaryEvents.length && terminationReason !== "MIXER_BOUNDARY_HIT") {
    return null;
  }

  const primaryBoundary = boundaryEvents[0] || {
    name: "Tornado Cash Pool",
    address: "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",
    kind: "MIXER",
    hop_number: 1,
    deposit_amount: 30.0,
    asset: "ETH",
    why_stopped: "Fund flow beyond this point is cryptographically obfuscated. Onward addresses cannot be attributed to the depositor.",
  };

  return (
    <div className="rounded-xl border border-red-500/40 bg-gradient-to-b from-red-950/40 to-slate-900/90 p-5 shadow-2xl backdrop-blur space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-600/20 border border-red-500/50 text-red-400">
            <Lock className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-red-200">
                Trace Terminated ? Cryptographic Privacy Horizon
              </h3>
              <Badge variant="destructive" className="bg-red-600 text-white font-mono text-[10px]">
                MIXER BOUNDARY HIT
              </Badge>
            </div>
            <p className="text-xs text-red-300/80 mt-0.5">
              Protocol: <span className="font-semibold text-white">{primaryBoundary.name}</span> ({primaryBoundary.address.slice(0, 10)}...{primaryBoundary.address.slice(-6)})
            </p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-[11px] font-mono text-slate-400 block">Boundary Hop #{primaryBoundary.hop_number}</span>
          <span className="text-xs font-bold text-amber-400">{primaryBoundary.deposit_amount} {primaryBoundary.asset} Deposited</span>
        </div>
      </div>

      <div className="rounded-lg border border-red-900/60 bg-black/40 p-3.5 text-xs text-slate-300 leading-relaxed">
        <div className="flex items-start gap-2 text-red-400 font-semibold mb-1">
          <AlertOctagon className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <span>Forensic Limitation Disclosure (PRD Strict Admissibility Standard):</span>
        </div>
        <p className="pl-6 text-slate-300">
          {primaryBoundary.why_stopped} Unlike naive commercial explorers that guess onward outputs, CryptoTrace LEA stops tracing at zero-knowledge boundaries to preserve evidentiary admissibility in Indian courts.
        </p>
      </div>

      {partialRecommendation && (
        <div className="space-y-3 pt-2 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-emerald-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-300">
              Immediate Officer Actionable Recommendations
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="rounded-lg bg-slate-800/60 border border-slate-700 p-3 space-y-2">
              <span className="font-bold text-amber-300 flex items-center gap-1.5 text-[11px] uppercase">
                1. Urgent Pre-Mixer Freezing Targets
              </span>
              <p className="text-slate-400 text-[11px]">
                Lodge immediate BNSS ?91 freeze notices on verified pre-mixer feeder wallets:
              </p>
              <div className="space-y-1">
                {partialRecommendation.pre_mixer_freeze_targets.length > 0 ? (
                  partialRecommendation.pre_mixer_freeze_targets.map((tgt, i) => (
                    <code key={i} className="block text-[11px] bg-slate-900/80 px-2 py-1 rounded text-cyan-300 font-mono">
                      {tgt}
                    </code>
                  ))
                ) : (
                  <span className="text-slate-500 italic text-[11px]">Direct suspect deposit</span>
                )}
              </div>
            </div>

            <div className="rounded-lg bg-slate-800/60 border border-slate-700 p-3 space-y-2">
              <span className="font-bold text-cyan-300 flex items-center gap-1.5 text-[11px] uppercase">
                2. Off-Chain Subpoenas & Telemetry
              </span>
              <ul className="space-y-1 text-slate-300 text-[11px] list-disc pl-4">
                {partialRecommendation.off_chain_actions.slice(0, 3).map((act, i) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>
          </div>

          {partialRecommendation.payout_candidates && partialRecommendation.payout_candidates.length > 0 && (
            <div className="rounded-lg border border-amber-600/30 bg-amber-950/20 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                  <HelpCircle className="h-3.5 w-3.5" />
                  Heuristic Exit Candidates (+14,400s Window) ? LEAD ONLY
                </span>
                <Badge variant="outline" className="text-[10px] border-amber-500/50 text-amber-300">
                  Confidence: ? 0.25 (LEAD)
                </Badge>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-[11px] text-left">
                  <thead>
                    <tr className="text-slate-400 border-b border-amber-600/20">
                      <th className="pb-1">Heuristic Output Address</th>
                      <th className="pb-1">Amount</th>
                      <th className="pb-1">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {partialRecommendation.payout_candidates.map((c, i) => (
                      <tr key={i} className="text-slate-300">
                        <td className="py-1 font-mono text-cyan-400">{c.recipient}</td>
                        <td className="py-1 font-mono text-amber-200">{c.amount} {c.asset}</td>
                        <td className="py-1 text-amber-400 font-semibold">{c.relationship_label}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="text-[10px] text-amber-200/70 italic">
                Notice: Post-mixer linkages are heuristic correlations sharing pool liquidity. They must NOT be submitted as definitive proof.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
