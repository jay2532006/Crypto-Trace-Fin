// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { CrossChainLink, RecoveryEstimate, RiskAssessment } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";

export function CrossChainView() {
  const [links, setLinks] = useState<CrossChainLink[]>([]);
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [recovery, setRecovery] = useState<RecoveryEstimate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([
      mockApi.getCrossChain(),
      mockApi.getRisk(),
      mockApi.getRecovery()
    ])
      .then(([lRes, rRes, recRes]) => {
        if (!active) return;
        setLinks(lRes.data);
        setRisk(rRes.data);
        setRecovery(recRes.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load cross-chain intelligence.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, []);

  if (loading) return <SkeletonLoader text="Tracing cross-chain hops and bridge protocols..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="sec-head">
        <div>
          <h2>Cross-Chain & Risk Intelligence</h2>
          <p>Bridge provenance verification, heuristic correlations, and Heuristic Recovery Estimate</p>
        </div>
        <Badge tone="purple">Multi-Chain Protocol Engine</Badge>
      </div>

      <div className="kestrel-grid-3">
        {/* Cross-Chain Links */}
        <div style={{ gridColumn: "span 2" }}>
          <div className="kestrel-panel">
            <div className="kestrel-panel-head">
              <div>
                <h2>Cross-Chain Movements</h2>
                <p>Distinguishing cryptographic bridge contracts from heuristic timing correlations</p>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {links.map((link) => {
                const isBridge = link.relationship === "PROVEN_BRIDGE";
                return (
                  <article
                    key={link.link_id}
                    style={{
                      padding: "16px 18px",
                      borderRadius: "var(--r-md)",
                      background: "var(--elev-2)",
                      border: "1px solid var(--line)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "10px"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <Badge tone={isBridge ? "green" : "heuristic"}>
                          {isBridge ? "PROVEN BRIDGE CONTRACT" : "HEURISTIC CORRELATION"}
                        </Badge>
                        <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text)" }}>
                          {link.from_chain.toUpperCase()} → {link.to_chain.toUpperCase()}
                        </span>
                      </div>
                      <span className="mono" style={{ fontSize: "11px", color: "var(--accent-2)" }}>
                        Δ {link.timestamp_delta_minutes}m time delta
                      </span>
                    </div>

                    <div className="mono" style={{ fontSize: "12px", color: "var(--text-2)", wordBreak: "break-all" }}>
                      {link.from_address} <span style={{ color: "var(--accent)" }}>→</span> {link.to_address}
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--text-3)" }}>
                      <span>Value Correlation: <strong style={{ color: "var(--gold)" }}>{link.value_correlation}</strong></span>
                      <span>Evidence Strength: <strong>{link.evidence_strength}</strong></span>
                      <span>Uncertainty: <strong style={{ color: link.uncertainty ? "var(--ember)" : "var(--accent-2)" }}>{String(link.uncertainty)}</strong></span>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </div>

        {/* Risk Assessment */}
        <div>
          <div className="kestrel-panel" style={{ height: "100%" }}>
            <div className="kestrel-panel-head">
              <div>
                <h2>Risk Assessment</h2>
                <p>Independent risk scoring engine</p>
              </div>
            </div>

            {risk && (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                <div style={{
                  padding: "16px",
                  borderRadius: "var(--r-md)",
                  background: "rgba(224, 82, 82, 0.1)",
                  border: "1px solid rgba(224, 82, 82, 0.3)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}>
                  <div>
                    <span style={{ fontSize: "11px", color: "var(--red)", textTransform: "uppercase", fontWeight: 700 }}>
                      Risk Level
                    </span>
                    <h3 style={{ margin: "2px 0 0", fontSize: "20px", color: "var(--red)" }}>
                      {risk.risk_tier} · {risk.risk_score}/100
                    </h3>
                  </div>
                  <Badge tone="red">{risk.risk_tier}</Badge>
                </div>

                <span className="mono" style={{ fontSize: "11.5px", color: "var(--text-3)" }}>
                  Rule Engine: {risk.rule_version}
                </span>

                <div>
                  <h4 style={{ margin: "0 0 10px", fontSize: "13px", color: "var(--text-2)" }}>Contributing Risk Factors</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    {risk.factors.map((factor) => (
                      <div key={factor.name} style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px" }}>
                          <span>{factor.name}</span>
                          <strong className="mono" style={{ color: "var(--gold)" }}>{(factor.weight * 100).toFixed(0)}%</strong>
                        </div>
                        <div style={{ height: "4px", background: "rgba(255, 255, 255, 0.08)", borderRadius: "999px", overflow: "hidden" }}>
                          <div style={{ height: "100%", width: `${factor.weight * 100}%`, background: "var(--ember)" }} />
                        </div>
                        <small style={{ fontSize: "10.5px", color: "var(--text-3)" }}>Evidence: {factor.evidence.join(", ")}</small>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Heuristic Recovery Estimate Banner / Details */}
      <div className="kestrel-panel">
        <div className="kestrel-panel-head">
          <div>
            <h2>Heuristic Recovery Estimate</h2>
            <p>Victim fund recovery eligibility based on exchange cooperation & trail velocity</p>
          </div>
          <Badge tone="amber">NOT A STATISTICAL PROBABILITY</Badge>
        </div>

        {recovery && (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "14px" }}>
              <div style={{ padding: "16px", borderRadius: "var(--r-md)", background: "var(--elev-2)", border: "1px solid var(--line)" }}>
                <span style={{ fontSize: "11px", color: "var(--text-3)", textTransform: "uppercase" }}>Recovery Probability</span>
                <strong style={{ display: "block", fontSize: "24px", color: "var(--gold)", margin: "4px 0" }}>
                  {Math.round(recovery.recovery_score * 100)}%
                </strong>
                <Badge tone="amber">{recovery.display_tier}</Badge>
              </div>

              <div style={{ padding: "16px", borderRadius: "var(--r-md)", background: "var(--elev-2)", border: "1px solid var(--line)" }}>
                <span style={{ fontSize: "11px", color: "var(--text-3)", textTransform: "uppercase" }}>Action Window</span>
                <strong style={{ display: "block", fontSize: "24px", color: "var(--red)", margin: "4px 0" }}>
                  {recovery.action_window_hours} Hours
                </strong>
                <span style={{ fontSize: "12px", color: "var(--text-3)" }}>Urgency tier: CRITICAL</span>
              </div>

              <div style={{ padding: "16px", borderRadius: "var(--r-md)", background: "var(--elev-2)", border: "1px solid var(--line)" }}>
                <span style={{ fontSize: "11px", color: "var(--text-3)", textTransform: "uppercase" }}>Top Attribution Confidence</span>
                <strong style={{ display: "block", fontSize: "24px", color: "var(--accent-2)", margin: "4px 0" }}>
                  {(recovery.top_candidate_confidence * 100).toFixed(0)}%
                </strong>
                <span style={{ fontSize: "12px", color: "var(--text-3)" }}>Satisfies qualification threshold</span>
              </div>
            </div>

            {/* Parameter Meters */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px" }}>
              {(["value_ratio", "exchange_cooperation", "time_urgency", "path_clarity"] as const).map((key) => (
                <div key={key} style={{ padding: "12px", background: "var(--elev-2)", borderRadius: "var(--r-md)", border: "1px solid var(--line)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px" }}>
                    <span style={{ textTransform: "capitalize", color: "var(--text-2)" }}>{key.replace(/_/g, " ")}</span>
                    <strong className="mono" style={{ color: "var(--accent-2)" }}>{recovery[key].toFixed(2)}</strong>
                  </div>
                  <meter min={0} max={1} value={recovery[key]} style={{ width: "100%", height: "6px" }} />
                </div>
              ))}
            </div>

            <div style={{
              padding: "12px 16px",
              borderRadius: "var(--r-md)",
              background: "rgba(232, 178, 75, 0.08)",
              border: "1px solid rgba(232, 178, 75, 0.25)",
              color: "var(--gold)",
              fontSize: "12px"
            }}>
              <strong>Administrator Disclaimer:</strong> {recovery.disclaimer} Exchange cooperation parameter ({recovery.exchange_cooperation}) was reviewed on {recovery.cooperation_last_reviewed} from source: {recovery.cooperation_source}.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
