// @ts-nocheck
import React from "react";
import type { AttributionAssessment } from "../../types";
import { Badge } from "../common/Badge";

export function AttributionTrace({ attribution }: { attribution: AttributionAssessment }) {
  const sum = Object.values(attribution.final_weights).reduce((acc, item) => acc + item, 0);

  return (
    <div className="attribution-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <Badge tone="green">{attribution.confidence_band}</Badge>
          <span className="mono" style={{ fontSize: "12px", color: "var(--accent-2)" }}>{attribution.policy_version}</span>
        </div>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <span style={{ fontSize: "13px", color: "var(--text-3)" }}>
            Normalized Vector Sum: <strong style={{ color: "var(--accent-2)" }}>{sum.toFixed(2)}</strong>
          </span>
          <strong style={{ fontSize: "16px", color: "var(--gold)" }}>Score: {attribution.score.toFixed(2)}</strong>
        </div>
      </div>

      <div>
        <h4 style={{ margin: "0 0 10px", fontSize: "13.5px", color: "var(--text-2)" }}>
          Normalized Attribution Weight Dimensions
        </h4>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {Object.entries(attribution.final_weights).map(([name, value]) => (
            <div key={name} className="weight-row">
              <span style={{ color: "var(--text)", textTransform: "capitalize" }}>
                {name.replace(/_/g, " ")}
              </span>
              <div style={{
                height: "6px",
                background: "rgba(255, 255, 255, 0.08)",
                borderRadius: "999px",
                overflow: "hidden"
              }}>
                <div style={{
                  height: "100%",
                  width: `${Math.round(value * 100)}%`,
                  background: "linear-gradient(90deg, var(--accent), var(--accent-2))",
                  borderRadius: "999px"
                }} />
              </div>
              <strong className="mono" style={{ textAlign: "right", color: "var(--text)" }}>
                {value.toFixed(2)}
              </strong>
            </div>
          ))}
        </div>
      </div>

      <details style={{
        marginTop: "12px",
        background: "var(--elev-2)",
        border: "1px solid var(--line)",
        borderRadius: "var(--r-md)",
        padding: "14px 16px"
      }}>
        <summary style={{ cursor: "pointer", fontWeight: 600, color: "var(--text-2)", fontSize: "13.5px" }}>
          AdaptiveVASPScorer Deterministic Execution Trace ({attribution.scoring_metadata.steps.length} Steps)
        </summary>
        <ol style={{ margin: "14px 0 0", paddingLeft: "20px", fontSize: "13px", color: "var(--text-2)", lineHeight: "1.7" }}>
          {attribution.scoring_metadata.steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
        <div style={{
          marginTop: "12px",
          paddingTop: "12px",
          borderTop: "1px solid var(--line)",
          fontSize: "12px",
          color: "var(--text-3)"
        }}>
          <span>Fired Modifiers: <strong>{attribution.fired_modifiers.join(", ")}</strong></span>
          <span style={{ marginLeft: "14px" }}>Cross-Chain Bridge in Path: <strong>{String(attribution.scoring_metadata.path_contains_bridge)}</strong></span>
        </div>
      </details>
    </div>
  );
}
