// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { ReportView } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";

export function ReportsView() {
  const [report, setReport] = useState<ReportView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    mockApi.getReport()
      .then((res) => {
        if (!active) return;
        setReport(res.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to generate investigation report.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, []);

  const downloadReportJson = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cryptotrace-investigation-${report.case.case_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <SkeletonLoader text="Compiling multi-source investigation report..." />;
  if (error) return <ErrorNotice message={error} />;
  if (!report) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="sec-head">
        <div>
          <h2>Comprehensive Investigation Dossier</h2>
          <p>Exportable court-admissible summary for Indian Law Enforcement & Judiciary</p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <button className="btn-secondary" onClick={() => window.print()}>
            Print / Save PDF
          </button>
          <button className="btn-primary" onClick={downloadReportJson}>
            Export JSON Dossier
          </button>
        </div>
      </div>

      <div className="kestrel-panel" style={{ display: "flex", flexDirection: "column", gap: "22px" }}>
        {/* Header Ribbon */}
        <div style={{
          padding: "16px 20px",
          borderRadius: "var(--r-md)",
          background: "var(--elev-2)",
          border: "1px solid var(--line)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}>
          <div>
            <h3 style={{ margin: "0", fontSize: "16px" }}>{report.case.case_id} Forensic Summary</h3>
            <span style={{ fontSize: "12px", color: "var(--text-3)" }}>
              Generated for Indian Law Enforcement Authority · SIH 26183
            </span>
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            <Badge tone="green">AUDIT ANCHORED</Badge>
            <span className="badge neutral">COURT ADMISSIBLE DRAFT</span>
          </div>
        </div>

        {/* Section 1: Case Details */}
        <div>
          <h4 style={{ margin: "0 0 8px", fontSize: "14px", color: "var(--accent-2)" }}>1. Case Identification</h4>
          <div style={{ padding: "14px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px" }}>
            <p style={{ margin: "0 0 6px" }}>
              <strong>Case ID:</strong> {report.case.case_id} ({report.case.source_badge}) · <strong>Complaint:</strong> {report.case.complaint_id}
            </p>
            <p style={{ margin: "0 0 6px" }}>
              <strong>Fraud Classification:</strong> {report.case.fraud_type} · <strong>Reported Amount:</strong> ₹{report.case.fraud_amount_inr.toLocaleString("en-IN")}
            </p>
            <p style={{ margin: 0 }}>
              <strong>Reported Address:</strong> <span className="mono">{report.case.reported_wallet}</span> ({report.case.primary_chain})
            </p>
          </div>
        </div>

        {/* Section 2: Trace Summary */}
        <div>
          <h4 style={{ margin: "0 0 8px", fontSize: "14px", color: "var(--accent-2)" }}>2. Bounded Fund-Flow Trace Receipt</h4>
          <div style={{ padding: "14px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px" }}>
            <p style={{ margin: 0 }}>
              Traced <strong>{report.trace.node_count} nodes</strong> and <strong>{report.trace.edge_count} edges</strong> up to depth <strong>{report.trace.max_depth_reached} hops</strong>.
              Termination reason: <code>{report.trace.termination_reason}</code>. Data coverage status: <strong>{report.trace.coverage}</strong>.
            </p>
          </div>
        </div>

        {/* Section 3: Typologies */}
        <div>
          <h4 style={{ margin: "0 0 8px", fontSize: "14px", color: "var(--accent-2)" }}>3. Algorithmic Typology Findings</h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {report.typologies.map((t) => (
              <div key={t.finding_id} style={{ padding: "10px 14px", background: "var(--elev-2)", borderRadius: "var(--r-sm)", fontSize: "13px", display: "flex", justifyContent: "space-between" }}>
                <span><strong>{t.pattern_type}</strong> (Rule: {t.rule_version})</span>
                <Badge tone={t.confidence === "HIGH" ? "red" : "amber"}>Confidence {t.confidence}</Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Section 4: VASP Attribution & Recovery */}
        <div>
          <h4 style={{ margin: "0 0 8px", fontSize: "14px", color: "var(--accent-2)" }}>4. VASP Intelligence & Recovery Probability</h4>
          <div style={{ padding: "14px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px" }}>
            <p style={{ margin: "0 0 6px" }}>
              <strong>Top Candidate:</strong> {report.vasps[0]?.name} ({report.vasps[0]?.label_status}) with attribution confidence {(report.vasps[0]?.confidence * 100).toFixed(0)}%.
            </p>
            <p style={{ margin: "0 0 6px" }}>
              <strong>Risk Score:</strong> {report.risk.risk_tier} {report.risk.risk_score}/100.
            </p>
            <p style={{ margin: 0 }}>
              <strong>Heuristic Recovery Estimate:</strong> {Math.round(report.recovery.recovery_score * 100)}% with {report.recovery.action_window_hours}h critical window ({report.recovery.disclaimer}).
            </p>
          </div>
        </div>

        {/* Section 5: Recommendations */}
        <div>
          <h4 style={{ margin: "0 0 8px", fontSize: "14px", color: "var(--accent-2)" }}>5. Advisory Recommendations</h4>
          <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "13px", color: "var(--text-2)", lineHeight: "1.7" }}>
            {report.recommendations.map((rec) => (
              <li key={rec.recommendation_id}>
                <strong>{rec.title}:</strong> {rec.reason}
              </li>
            ))}
          </ul>
        </div>

        {/* Section 6: Evidence Manifest */}
        <div>
          <h4 style={{ margin: "0 0 8px", fontSize: "14px", color: "var(--accent-2)" }}>6. Anchored Evidence Manifest</h4>
          <div style={{ padding: "14px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "12.5px" }}>
            <p style={{ margin: 0 }}>
              Manifest ID <span className="mono">{report.evidence.manifest_id}</span> ({report.evidence.integrity_status}) contains <strong>{report.evidence.items.length} cryptographically sealed artifacts</strong> hashed with {report.evidence.hash_algorithm}.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
