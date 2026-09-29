// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { SystemStatus } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";

export function SystemStatusView() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    mockApi.getSystemStatus()
      .then((res) => {
        if (!active) return;
        setStatus(res.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load system status.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, []);

  if (loading) return <SkeletonLoader text="Testing RPC nodes and indexer cluster..." />;
  if (error) return <ErrorNotice message={error} />;
  if (!status) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="sec-head">
        <div>
          <h2>System Health & Ingestion Pipeline</h2>
          <p>Real-time simulated telemetry across RPC nodes, indexers, and analytical microservices</p>
        </div>
        <span className="badge green">
          <span style={{ display: "inline-block", width: 5, height: 5, borderRadius: "50%", background: "currentColor", marginRight: 3 }} />
          ALL SYSTEMS OPERATIONAL
        </span>
      </div>

      <div className="kestrel-grid-3">
        {/* Chain Providers Grid */}
        <div style={{ gridColumn: "span 2" }}>
          <div className="kestrel-panel">
            <div className="kestrel-panel-head">
              <div>
                <h2>Blockchain RPC Nodes</h2>
                <p>Node synchronization status</p>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
              {Object.entries(status.chains).map(([chain, info]) => (
                <div
                  key={chain}
                  style={{
                    padding: "16px",
                    borderRadius: "var(--r-md)",
                    background: "var(--elev-2)",
                    border: "1px solid var(--line)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Badge tone={chain}>{chain}</Badge>
                    <Badge tone="green">{info.status}</Badge>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "var(--text-3)", marginTop: "4px" }}>
                    <span>Block Height</span>
                    <strong className="mono" style={{ color: "var(--text)" }}>#{info.last_block}</strong>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Pipeline Microservices */}
        <div>
          <div className="kestrel-panel" style={{ height: "100%" }}>
            <div className="kestrel-panel-head">
              <div>
                <h2>Ingestion Engine</h2>
                <p>8-Stage microservice status</p>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {Object.entries(status.pipeline).map(([service, state]) => (
                <div
                  key={service}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "10px 12px",
                    borderRadius: "var(--r-sm)",
                    background: "var(--elev-2)",
                    fontSize: "12.5px"
                  }}
                >
                  <span style={{ fontWeight: 600, color: "var(--text)" }}>{service.toUpperCase()}</span>
                  <Badge tone={state === "SIMULATED" ? "fixture" : "green"}>{state}</Badge>
                </div>
              ))}
            </div>

            <div style={{
              marginTop: "16px",
              padding: "10px 12px",
              borderRadius: "var(--r-sm)",
              background: "rgba(255, 255, 255, 0.03)",
              fontSize: "11px",
              color: "var(--text-3)"
            }}>
              Fixture mode replay. No external network requests are executed.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
