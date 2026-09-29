// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { EvidenceItem, EvidenceManifest } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";

interface EvidenceViewProps {
  setDrawer: (drawer: any) => void;
}

export function EvidenceView({ setDrawer }: EvidenceViewProps) {
  const [evidence, setEvidence] = useState<EvidenceManifest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    mockApi.getEvidence()
      .then((res) => {
        if (!active) return;
        setEvidence(res.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load evidence manifest.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, []);

  if (loading) return <SkeletonLoader text="Verifying SHA-256 cryptographic hashes..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="sec-head">
        <div>
          <h2>Forensic Evidence Manifest</h2>
          <p>Cryptographically hashed artifact records supporting chain-of-custody and legal filings</p>
        </div>
        <Badge tone="green">Chain of Custody Verified</Badge>
      </div>

      {evidence && (
        <div className="kestrel-panel">
          <div className="kestrel-panel-head">
            <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
              <Badge tone="green">{evidence.integrity_status}</Badge>
              <span className="mono" style={{ fontSize: "14px", fontWeight: 700, color: "var(--text)" }}>
                {evidence.manifest_id}
              </span>
              <span style={{ fontSize: "12px", color: "var(--text-3)" }}>
                Algorithm: <strong className="mono">{evidence.hash_algorithm}</strong>
              </span>
              <span className="badge neutral">SHA-256 SEALED</span>
            </div>
            <span style={{ fontSize: "12px", color: "var(--accent-2)" }}>
              {evidence.items.length} Sealed Evidence Items
            </span>
          </div>

          <div className="table-wrap">
            <div className="table-head grid-ev">
              <span>Evidence ID</span>
              <span>Type</span>
              <span>Source System</span>
              <span>Pointer Reference</span>
              <span>Payload Hash</span>
              <span>Immutable</span>
            </div>
            {evidence.items.map((item) => (
              <button
                key={item.evidence_id}
                className="table-row grid-ev"
                onClick={() => setDrawer({ kind: "evidence", item })}
              >
                <span className="mono" style={{ color: "var(--accent-2)" }}>{item.evidence_id}</span>
                <span>{item.type}</span>
                <span style={{ color: "var(--text-3)" }}>{item.source}</span>
                <span className="mono" style={{ fontSize: "12px" }}>{item.reference}</span>
                <span className="mono" style={{ fontSize: "11px", color: "var(--text-3)" }}>
                  {item.payload_hash.slice(0, 12)}...{item.payload_hash.slice(-6)}
                </span>
                <Badge tone="green">{String(item.immutable)}</Badge>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
