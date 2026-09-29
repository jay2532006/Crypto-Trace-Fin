// @ts-nocheck
import React from "react";
import type { RecoveryEstimate, RiskAssessment } from "../../types";
import { formatWallet } from "../../utils/formatters";

interface KpiBannerProps {
  reportedWallet: string;
  caseId: string;
  recovery: RecoveryEstimate | null;
  risk: RiskAssessment | null;
  attributionBand?: string;
  traceCoverage?: string;
}

export function KpiBanner({
  reportedWallet,
  caseId,
  recovery,
  risk,
  attributionBand = "HIGH",
  traceCoverage = "PARTIAL"
}: KpiBannerProps) {
  const recoveryValue = recovery?.eligible ? `${Math.round(recovery.recovery_score * 100)}%` : "N/A";
  const recoveryWindow = recovery?.eligible ? `${recovery.action_window_hours}h window` : "Low attribution";
  const riskValue = risk ? `${risk.risk_tier} ${risk.risk_score}` : "HIGH 78";

  return (
    <section className="trace-register" aria-label="Trace condition register">
      <div className="trace-register-grid">
        <div className="trace-lead">
          <span className="trace-lead-icon" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="6" width="18" height="13" rx="2" stroke="currentColor" strokeWidth="1.8" />
              <path d="M16 10H20V15H16C14.8954 15 14 14.1046 14 13C14 11.8954 14.8954 11 16 11V10Z" fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="1.6" />
              <circle cx="17" cy="13" r="1" fill="currentColor" />
            </svg>
          </span>
          <div>
            <span className="trace-label">Lead suspect wallet</span>
            <strong className="trace-lead-value mono">{formatWallet(reportedWallet)}</strong>
            <span className="trace-subvalue">{caseId} · Lead Suspect Target</span>
          </div>
        </div>

        <TraceCell className="recovery" label="Recovery Estimate" value={recoveryValue} detail={recoveryWindow} />
        <TraceCell className="attribution" label="Attribution Band" value={attributionBand} detail="VASP heuristic band" />
        <TraceCell className="risk" label="Risk Assessment" value={riskValue} detail="High-risk typology" />
        <TraceCell className="coverage" label="Trace Coverage" value={traceCoverage} detail="Deterministic scope" />
      </div>
    </section>
  );
}

function TraceCell({ className, label, value, detail }: { className: string; label: string; value: string; detail: string }) {
  return (
    <div className={`trace-cell ${className}`}>
      <span className="trace-label">{label}</span>
      <strong className="trace-value">{value}</strong>
      <span className="trace-subvalue">{detail}</span>
    </div>
  );
}
