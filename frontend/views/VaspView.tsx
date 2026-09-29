// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { AttributionAssessment, VASPCluster } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { AttributionTrace } from "../components/vasp/AttributionTrace";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";

interface VaspViewProps {
  setDrawer: (drawer: any) => void;
}

export function VaspView({ setDrawer }: VaspViewProps) {
  const [candidates, setCandidates] = useState<VASPCluster[]>([]);
  const [attribution, setAttribution] = useState<AttributionAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([
      mockApi.getVaspCandidates(),
      mockApi.getAttribution()
    ])
      .then(([vRes, aRes]) => {
        if (!active) return;
        setCandidates(vRes.data);
        setAttribution(aRes.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load VASP intelligence.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, []);

  if (loading) return <SkeletonLoader text="Loading VASP clusters and attribution engine..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="sec-head">
        <div>
          <h2>VASP Attribution Intelligence</h2>
          <p>Verified, inferred, and unresolved exchange clusters with AdaptiveVASPScorer policy weights</p>
        </div>
        <Badge tone="green">Policy v1.2 Active</Badge>
      </div>

      <div className="kestrel-grid-3">
        {/* VASP Candidates Panel */}
        <div>
          <div className="kestrel-panel" style={{ height: "100%", display: "flex", flexDirection: "column", gap: "16px" }}>
            <div className="kestrel-panel-head">
              <div>
                <h2>Candidate Clusters</h2>
                <p>Identified deposit/hot wallet proximity</p>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {candidates.map((candidate) => (
                <button
                  key={candidate.candidate_id}
                  onClick={() => setDrawer({ kind: "vasp", candidate })}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "14px",
                    borderRadius: "var(--r-md)",
                    background: "var(--elev-2)",
                    border: "1px solid var(--line)",
                    textAlign: "left",
                    transition: "all 0.2s var(--ease)"
                  }}
                >
                  <div>
                    <strong style={{ display: "block", fontSize: "14px", color: "var(--text)" }}>{candidate.name}</strong>
                    <span className="mono" style={{ fontSize: "11px", color: "var(--text-3)" }}>
                      {candidate.address.slice(0, 10)}...{candidate.address.slice(-6)}
                    </span>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <Badge tone={candidate.label_status.toLowerCase()}>{candidate.label_status}</Badge>
                    <span style={{ display: "block", fontSize: "11px", color: "var(--accent-2)", marginTop: "4px" }}>
                      {Math.round(candidate.confidence * 100)}% · Hop {candidate.hop_distance}
                    </span>
                  </div>
                </button>
              ))}
            </div>

            <div style={{
              marginTop: "auto",
              padding: "12px 14px",
              borderRadius: "var(--r-md)",
              background: "rgba(232, 178, 75, 0.08)",
              border: "1px solid rgba(232, 178, 75, 0.25)",
              fontSize: "12px",
              color: "var(--gold)",
              lineHeight: 1.45
            }}>
              <strong>Evidentiary Guardrail:</strong> Inferred clustering reflects probabilistic proximity, not cryptographic ownership proof.
            </div>
          </div>
        </div>

        {/* AdaptiveVASPScorer Deep Dive */}
        <div style={{ gridColumn: "span 2" }}>
          <div className="kestrel-panel">
            <div className="kestrel-panel-head">
              <div>
                <h2>AdaptiveVASPScorer Trace</h2>
                <p>Deterministic scoring pipeline with dynamic contextual modifiers</p>
              </div>
              <Badge tone="blue">LEGAL COMPLIANT</Badge>
            </div>

            {attribution && <AttributionTrace attribution={attribution} />}
          </div>
        </div>
      </div>
    </div>
  );
}
