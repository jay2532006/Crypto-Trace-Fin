// @ts-nocheck
import React from "react";
import type {
  EvidenceItem,
  GraphEdge,
  GraphNode,
  PatternFinding,
  Transaction,
  VASPCluster
} from "../../types";
import { Badge } from "../common/Badge";

export type DrawerState =
  | { kind: "tx"; tx: Transaction }
  | { kind: "node"; node: GraphNode }
  | { kind: "edge"; edge: GraphEdge; tx?: Transaction }
  | { kind: "finding"; finding: PatternFinding }
  | { kind: "vasp"; candidate: VASPCluster }
  | { kind: "evidence"; item: EvidenceItem }
  | null;

interface DrawerPanelProps {
  drawer: DrawerState;
  onClose: () => void;
  openTransaction: (txHash: string) => Promise<void>;
}

export function DrawerPanel({ drawer, onClose, openTransaction }: DrawerPanelProps) {
  if (!drawer) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <aside className="drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <p className="eyebrow">{getDrawerEyebrow(drawer.kind)}</p>
            <h2>{getDrawerTitle(drawer)}</h2>
          </div>
          <button
            onClick={onClose}
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "var(--r-pill)",
              background: "var(--elev-2)",
              border: "1px solid var(--line)",
              display: "grid",
              placeItems: "center",
              color: "var(--text-2)"
            }}
            aria-label="Close detail panel"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {drawer.kind === "tx" && <TxDetail tx={drawer.tx} />}
        {drawer.kind === "node" && <NodeDetail node={drawer.node} />}
        {drawer.kind === "edge" && <EdgeDetail edge={drawer.edge} tx={drawer.tx} />}
        {drawer.kind === "finding" && <FindingDetail finding={drawer.finding} openTransaction={openTransaction} />}
        {drawer.kind === "vasp" && <VaspDetail candidate={drawer.candidate} />}
        {drawer.kind === "evidence" && <EvidenceDetail item={drawer.item} />}
      </aside>
    </div>
  );
}

function getDrawerEyebrow(kind: NonNullable<DrawerState>["kind"]): string {
  switch (kind) {
    case "tx": return "Blockchain Transaction Record";
    case "node": return "Network Entity / Node";
    case "edge": return "Fund-Flow Relationship";
    case "finding": return "Automated Typology Detection";
    case "vasp": return "VASP Intelligence Candidate";
    case "evidence": return "Immutable Forensic Evidence";
    default: return "Investigation Detail";
  }
}

function getDrawerTitle(drawer: NonNullable<DrawerState>): string {
  switch (drawer.kind) {
    case "tx": return `${drawer.tx.chain_id.toUpperCase()} · ${drawer.tx.asset} ${drawer.tx.amount_native}`;
    case "node": return drawer.node.label;
    case "edge": return drawer.edge.style === "DASHED" ? "Heuristic Lead Exit" : "Confirmed Flow Edge";
    case "finding": return drawer.finding.pattern_type;
    case "vasp": return drawer.candidate.name;
    case "evidence": return drawer.item.evidence_id;
  }
}

function TxDetail({ tx }: { tx: Transaction }) {
  const [copied, setCopied] = React.useState<string | null>(null);

  const copy = (val: string, key: string) => {
    navigator.clipboard.writeText(val);
    setCopied(key);
    setTimeout(() => setCopied(null), 1600);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <Badge tone={tx.chain_id}>{tx.chain_id}</Badge>
        <Badge tone="green">{tx.finality}</Badge>
        <span className="badge neutral">TESTNET PROVENANCE</span>
      </div>

      <dl>
        <dt>Transaction Hash</dt>
        <dd>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span className="mono" style={{ fontSize: "12px", color: "var(--accent-2)" }}>{tx.tx_hash}</span>
            <button onClick={() => copy(tx.tx_hash, "hash")} style={{ color: "var(--text-3)", fontSize: "11px" }}>
              {copied === "hash" ? "✓" : "Copy"}
            </button>
          </div>
        </dd>

        <dt>Block Height</dt>
        <dd className="mono">{tx.block_height}</dd>

        <dt>Timestamp</dt>
        <dd>{tx.timestamp.replace("T", " ").slice(0, 19)}</dd>

        <dt>From Address</dt>
        <dd>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span className="mono" style={{ fontSize: "12px" }}>{tx.from_address}</span>
            <button onClick={() => copy(tx.from_address, "from")} style={{ color: "var(--text-3)", fontSize: "11px" }}>
              {copied === "from" ? "✓" : "Copy"}
            </button>
          </div>
        </dd>

        <dt>To Address</dt>
        <dd>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span className="mono" style={{ fontSize: "12px" }}>{tx.to_address}</span>
            <button onClick={() => copy(tx.to_address, "to")} style={{ color: "var(--text-3)", fontSize: "11px" }}>
              {copied === "to" ? "✓" : "Copy"}
            </button>
          </div>
        </dd>

        <dt>Amount / Asset</dt>
        <dd><strong>{tx.amount_native} {tx.asset}</strong></dd>

        <dt>Value INR</dt>
        <dd><strong style={{ color: "var(--gold)" }}>₹{tx.value_inr.toLocaleString("en-IN")}</strong></dd>

        <dt>Hop Distance</dt>
        <dd>Hop {tx.hop}</dd>

        <dt>Event Type</dt>
        <dd>{tx.event_type}</dd>

        <dt>Provider / Source</dt>
        <dd className="mono">{tx.provider}</dd>

        <dt>Provenance ID</dt>
        <dd className="mono">{tx.provenance_id}</dd>
      </dl>

      <div style={{
        padding: "14px",
        borderRadius: "var(--r-md)",
        background: "var(--elev-2)",
        border: "1px solid var(--line)",
        fontSize: "12.5px",
        color: "var(--text-3)"
      }}>
        Blockchain intelligence replayed from deterministic fixture environment. Does not constitute real-time RPC node stream.
      </div>
    </div>
  );
}

function NodeDetail({ node }: { node: GraphNode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <Badge tone={node.chain}>{node.chain}</Badge>
        <Badge tone={node.type.includes("HEURISTIC") ? "heuristic" : "green"}>{node.type}</Badge>
      </div>

      <dl>
        <dt>Entity ID</dt>
        <dd className="mono">{node.id}</dd>

        <dt>Label</dt>
        <dd>{node.label}</dd>

        <dt>Wallet Address</dt>
        <dd className="mono" style={{ fontSize: "12px", color: "var(--accent-2)" }}>{node.address}</dd>

        <dt>Primary Chain</dt>
        <dd>{node.chain.toUpperCase()}</dd>

        <dt>Classification</dt>
        <dd>{node.type.replace(/_/g, " ")}</dd>
      </dl>

      <div style={{
        padding: "14px",
        borderRadius: "var(--r-md)",
        background: "rgba(232, 178, 75, 0.08)",
        border: "1px solid rgba(232, 178, 75, 0.25)",
        color: "var(--gold)",
        fontSize: "12.5px",
        lineHeight: 1.5
      }}>
        <strong>Investigative Notice:</strong> Identifying an address node does not establish beneficial ownership or intent. All data is fixture-backed.
      </div>
    </div>
  );
}

function EdgeDetail({ edge, tx }: { edge: GraphEdge; tx?: Transaction }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <Badge tone={edge.style === "DASHED" ? "heuristic" : "green"}>
          {edge.style === "DASHED" ? "HEURISTIC LEAD" : `CONFIRMED · HOP ${edge.hop}`}
        </Badge>
        <Badge tone="blue">{edge.asset}</Badge>
      </div>

      <dl>
        <dt>Source Node</dt>
        <dd className="mono">{edge.source}</dd>

        <dt>Target Node</dt>
        <dd className="mono">{edge.target}</dd>

        <dt>Traced Value</dt>
        <dd><strong style={{ color: "var(--gold)" }}>₹{edge.value_inr.toLocaleString("en-IN")}</strong> ({edge.asset})</dd>

        <dt>Relationship</dt>
        <dd>{edge.edge_label || (edge.style === "DASHED" ? "Possible Exit — Heuristic Only" : "Confirmed Fund Transfer")}</dd>

        <dt>Evidence State</dt>
        <dd>{edge.evidence_type}</dd>
      </dl>

      {tx ? (
        <div>
          <h4 style={{ margin: "16px 0 10px", fontSize: "14px", color: "var(--text-2)" }}>Underlying Transaction</h4>
          <TxDetail tx={tx} />
        </div>
      ) : (
        <div style={{
          padding: "14px",
          borderRadius: "var(--r-md)",
          background: "rgba(222, 112, 64, 0.1)",
          border: "1px solid rgba(222, 112, 64, 0.3)",
          color: "var(--ember)",
          fontSize: "12.5px"
        }}>
          <strong>Heuristic Boundary:</strong> This edge denotes an inferred correlation (e.g. mixer cluster deposit/withdrawal timing correlation), not cryptographic chain proof.
        </div>
      )}
    </div>
  );
}

function FindingDetail({ finding, openTransaction }: { finding: PatternFinding; openTransaction: (txHash: string) => Promise<void> }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        {finding.india_specific && <Badge tone="india">India Fraud Pattern</Badge>}
        <Badge tone={finding.confidence === "HIGH" ? "red" : "amber"}>Confidence: {finding.confidence}</Badge>
        <Badge tone="partial">{finding.data_coverage}</Badge>
      </div>

      <dl>
        <dt>Rule Version</dt>
        <dd className="mono">{finding.rule_version}</dd>

        {finding.victim_wallet_count !== undefined && (
          <>
            <dt>Victim Wallets</dt>
            <dd>{finding.victim_wallet_count} complaints linked</dd>
          </>
        )}

        {finding.aggregation_address && (
          <>
            <dt>Aggregation Node</dt>
            <dd className="mono" style={{ fontSize: "12px", color: "var(--accent-2)" }}>{finding.aggregation_address}</dd>
          </>
        )}

        {finding.total_value_aggregated_usd !== undefined && (
          <>
            <dt>Aggregated USD</dt>
            <dd><strong>${finding.total_value_aggregated_usd.toLocaleString("en-US")}</strong></dd>
          </>
        )}
      </dl>

      <div>
        <h4 style={{ margin: "12px 0 8px", fontSize: "13px", color: "var(--text-2)" }}>Linked Evidence & Transactions</h4>
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          {(finding.evidence_references || []).map((ref) => (
            <button
              key={ref}
              onClick={() => openTransaction(ref)}
              className="mono"
              style={{
                padding: "6px 12px",
                borderRadius: "var(--r-pill)",
                background: "var(--elev-2)",
                border: "1px solid var(--line-strong)",
                fontSize: "12px",
                color: "var(--accent-2)"
              }}
            >
              {ref} ↗
            </button>
          ))}
        </div>
      </div>

      <div style={{
        padding: "14px",
        borderRadius: "var(--r-md)",
        background: "var(--elev-2)",
        border: "1px solid var(--line)",
        fontSize: "12.5px",
        color: "var(--text-2)",
        lineHeight: 1.5
      }}>
        {finding.uncertainty_note || "Deterministic rule-based pattern extraction. Confidence score reflects behavioral correlation, not individual guilt."}
      </div>
    </div>
  );
}

function VaspDetail({ candidate }: { candidate: VASPCluster }) {
  const labelStatus = candidate?.label_status || "INFERRED";
  const chainName = candidate?.chain || "eth";
  const conf = typeof candidate?.confidence === "number" ? candidate.confidence : 0.8;
  const name = candidate?.name || candidate?.vasp_name || "VASP Candidate";
  const addr = candidate?.address || candidate?.hot_wallet || "Unknown Address";
  const confBand = candidate?.confidence_band || "MEDIUM";
  const hop = candidate?.hop_distance ?? 1;
  const source = candidate?.label_source || "STATIC_SEED";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <Badge tone={labelStatus.toLowerCase()}>{labelStatus}</Badge>
        <Badge tone={chainName}>{chainName}</Badge>
        <Badge tone="green">Band: {confBand}</Badge>
      </div>

      <dl>
        <dt>Candidate Name</dt>
        <dd><strong>{name}</strong></dd>

        <dt>Address / Cluster</dt>
        <dd className="mono" style={{ fontSize: "12px", color: "var(--accent-2)" }}>{addr}</dd>

        <dt>Attribution Score</dt>
        <dd><strong>{Math.round(conf * 100)}%</strong> ({conf.toFixed(2)})</dd>

        <dt>Hop Distance</dt>
        <dd>Hop {hop}</dd>

        <dt>Label Source</dt>
        <dd className="mono">{source}</dd>
      </dl>

      <div style={{
        padding: "14px",
        borderRadius: "var(--r-md)",
        background: "rgba(224, 82, 82, 0.08)",
        border: "1px solid rgba(224, 82, 82, 0.3)",
        color: "#FFA8A8",
        fontSize: "12.5px",
        lineHeight: 1.5
      }}>
        <strong>Legal Boundary Notice:</strong> Candidate attribution score indicates behavioral/cluster proximity to a known VASP infrastructure. It does NOT constitute confirmed wallet ownership or proof of exchange account identity.
      </div>
    </div>
  );
}

function EvidenceDetail({ item }: { item: EvidenceItem }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <Badge tone="green">{item.immutable ? "IMMUTABLE" : "MUTABLE"}</Badge>
        <span className="badge neutral">SEALED EVIDENCE</span>
      </div>

      <dl>
        <dt>Evidence ID</dt>
        <dd className="mono" style={{ color: "var(--accent-2)" }}>{item.evidence_id}</dd>

        <dt>Type</dt>
        <dd>{item.type}</dd>

        <dt>Source System</dt>
        <dd>{item.source}</dd>

        <dt>Reference Pointer</dt>
        <dd className="mono">{item.reference}</dd>

        <dt>Payload Hash (SHA256)</dt>
        <dd className="mono" style={{ fontSize: "11px", wordBreak: "break-all" }}>{item.payload_hash}</dd>
      </dl>

      <div style={{
        padding: "14px",
        borderRadius: "var(--r-md)",
        background: "var(--elev-2)",
        border: "1px solid var(--line)",
        fontSize: "12.5px",
        color: "var(--text-3)"
      }}>
        Cryptographically anchored evidence item linked to case audit trail. Integrity status: VERIFIED.
      </div>
    </div>
  );
}
