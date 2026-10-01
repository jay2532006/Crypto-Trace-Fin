// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { PatternFinding } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";

interface TypologiesViewProps {
  setDrawer: (drawer: any) => void;
  openTransaction: (txHash: string) => Promise<void>;
}

export function TypologiesView({ setDrawer, openTransaction }: TypologiesViewProps) {
  const [typologies, setTypologies] = useState<PatternFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    mockApi.getTypologies()
      .then((res) => {
        if (!active) return;
        setTypologies(res.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load typologies.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, []);

  if (loading) return <SkeletonLoader text="Analyzing typology patterns and mule networks..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="sec-head">
        <div>
          <h2>Typology Detection Intelligence</h2>
          <p>Deterministic behavioral findings with rule versions, evidence references, and explicit uncertainty disclaimers</p>
        </div>
        <Badge tone="india">India Mule Network Rules Active</Badge>
      </div>

      <div className="kestrel-grid-2">
        {typologies.map((finding) => (
          <article
            key={finding.finding_id}
            className="card"
            style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "14px" }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <strong style={{ fontSize: "16px", color: "var(--text)" }}>{finding.pattern_type}</strong>
                {finding.india_specific && <Badge tone="india">India Fraud Pattern</Badge>}
              </div>
              <Badge tone={finding.confidence === "HIGH" ? "red" : "amber"}>
                Confidence: {finding.confidence}
              </Badge>
            </div>

            <span className="mono" style={{ fontSize: "12px", color: "var(--text-3)" }}>
              Rule: {finding.rule_version} · Coverage: {finding.data_coverage}
            </span>

            {finding.pattern_type === "MULE_NETWORK" && (
              <div style={{
                padding: "14px",
                borderRadius: "var(--r-md)",
                background: "var(--elev-2)",
                border: "1px solid var(--line)",
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "10px",
                fontSize: "12.5px"
              }}>
                <div>
                  <span style={{ color: "var(--text-3)" }}>Victim Wallets:</span>
                  <strong style={{ display: "block", color: "var(--text)" }}>{finding.victim_wallet_count} linked complaints</strong>
                </div>
                <div>
                  <span style={{ color: "var(--text-3)" }}>Aggregated USD:</span>
                  <strong style={{ display: "block", color: "var(--gold)" }}>${finding.total_value_aggregated_usd?.toLocaleString("en-US")}</strong>
                </div>
                <div style={{ gridColumn: "span 2" }}>
                  <span style={{ color: "var(--text-3)" }}>Consolidation Aggregator:</span>
                  <span className="mono" style={{ display: "block", color: "var(--accent-2)", fontSize: "11.5px" }}>
                    {finding.aggregation_address}
                  </span>
                </div>
              </div>
            )}

            <div>
              <span style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "var(--text-3)", textTransform: "uppercase", marginBottom: "6px" }}>
                Supporting Evidence References
              </span>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {(finding.evidence_references || []).map((ref) => (
                  <button
                    key={ref}
                    onClick={() => openTransaction(ref)}
                    className="mono"
                    style={{
                      padding: "4px 10px",
                      borderRadius: "var(--r-pill)",
                      background: "var(--elev-2)",
                      border: "1px solid var(--line)",
                      fontSize: "11.5px",
                      color: "var(--accent-2)"
                    }}
                  >
                    {ref} ↗
                  </button>
                ))}
              </div>
            </div>

            <p style={{
              margin: "0",
              padding: "10px 12px",
              borderRadius: "var(--r-sm)",
              background: "rgba(255, 255, 255, 0.03)",
              fontSize: "12px",
              color: "var(--text-3)",
              lineHeight: "1.45"
            }}>
              {finding.uncertainty_note || "Deterministic rule-based pattern extraction. Confidence score reflects behavioral correlation, not individual guilt."}
            </p>

            <div style={{ marginTop: "auto", display: "flex", justifyContent: "flex-end" }}>
              <button
                className="btn-secondary"
                style={{ height: "36px", fontSize: "12.5px" }}
                onClick={() => setDrawer({ kind: "finding", finding })}
              >
                Inspect Forensic Dossier
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
