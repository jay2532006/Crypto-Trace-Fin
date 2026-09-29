// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { Case, Transaction, Wallet } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { TabsNav } from "../components/layout/TabsNav";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";

interface WalletsViewProps {
  activeCase: Case;
  openTransaction: (txHash: string) => Promise<void>;
}

export function WalletsView({ activeCase, openTransaction }: WalletsViewProps) {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([
      mockApi.getWallet(activeCase.reported_wallet),
      mockApi.getTransactions({ query: activeCase.reported_wallet.slice(0, 8) })
    ])
      .then(([wRes, txRes]) => {
        if (!active) return;
        setWallet(wRes.data);
        setTransactions(txRes.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load wallet data.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, [activeCase.reported_wallet]);

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "transactions", label: "Transactions", counter: transactions.length },
    { id: "fund_flow", label: "Fund Flow" },
    { id: "behavior", label: "Behavioral Typology" },
    { id: "counterparties", label: "Counterparties" },
    { id: "evidence", label: "Evidence" }
  ];

  if (loading) return <SkeletonLoader text="Loading wallet dossier..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="sec-head">
        <div>
          <h2>Target Wallet Dossier</h2>
          <p>Forensic profiling and behavioral history for investigated onchain addresses</p>
        </div>
        <Badge tone={wallet?.risk_tier === "HIGH" ? "red" : "green"}>{wallet?.risk_tier} RISK</Badge>
      </div>

      <div className="kestrel-grid-3">
        {/* Wallet Profile Card */}
        <div>
          <div className="kestrel-panel" style={{ height: "100%" }}>
            <div className="kestrel-panel-head">
              <div>
                <h2>Identity & Classification</h2>
                <p>Onchain address metadata</p>
              </div>
              <Badge tone="partial">{wallet?.coverage} COVERAGE</Badge>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{
                padding: "16px",
                borderRadius: "var(--r-md)",
                background: "var(--elev-2)",
                border: "1px solid var(--line)"
              }}>
                <span style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-3)", letterSpacing: "0.08em" }}>
                  Suspect Address
                </span>
                <p className="mono" style={{ margin: "6px 0 0", fontSize: "13px", color: "var(--accent-2)", wordBreak: "break-all" }}>
                  {wallet?.address}
                </p>
              </div>

              <dl className="drawer-dl" style={{ display: "grid", gridTemplateColumns: "110px 1fr", gap: "10px", margin: 0, fontSize: "13px" }}>
                <dt style={{ color: "var(--text-3)" }}>Chain</dt>
                <dd style={{ margin: 0 }}><Badge tone={wallet?.chain}>{wallet?.chain}</Badge></dd>

                <dt style={{ color: "var(--text-3)" }}>Classification</dt>
                <dd style={{ margin: 0, color: "var(--text)" }}>{wallet?.type.replace(/_/g, " ")}</dd>

                <dt style={{ color: "var(--text-3)" }}>Status</dt>
                <dd style={{ margin: 0, color: "var(--text)" }}>{wallet?.status.replace(/_/g, " ")}</dd>

                <dt style={{ color: "var(--text-3)" }}>Risk Tier</dt>
                <dd style={{ margin: 0 }}><Badge tone="red">{wallet?.risk_tier}</Badge></dd>
              </dl>
            </div>
          </div>
        </div>

        {/* Behavior Metrics & Tabs */}
        <div style={{ gridColumn: "span 2" }}>
          <div className="kestrel-panel">
            <div className="kestrel-panel-head">
              <div>
                <h2>Activity & Forensic Analysis</h2>
                <p>Telemetry recorded across investigation bounds</p>
              </div>
            </div>

            {/* Quick Metrics */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px", marginBottom: "20px" }}>
              <div style={{ padding: "14px", borderRadius: "var(--r-md)", background: "var(--elev-2)", border: "1px solid var(--line)" }}>
                <span style={{ display: "block", fontSize: "11px", color: "var(--text-3)", marginBottom: "4px" }}>First Activity</span>
                <strong style={{ fontSize: "15px", color: "var(--text)" }}>2026-09-14</strong>
              </div>
              <div style={{ padding: "14px", borderRadius: "var(--r-md)", background: "var(--elev-2)", border: "1px solid var(--line)" }}>
                <span style={{ display: "block", fontSize: "11px", color: "var(--text-3)", marginBottom: "4px" }}>Last Activity</span>
                <strong style={{ fontSize: "15px", color: "var(--gold)" }}>2026-09-16</strong>
              </div>
              <div style={{ padding: "14px", borderRadius: "var(--r-md)", background: "var(--elev-2)", border: "1px solid var(--line)" }}>
                <span style={{ display: "block", fontSize: "11px", color: "var(--text-3)", marginBottom: "4px" }}>Inbound Traced</span>
                <strong style={{ fontSize: "15px", color: "var(--accent-2)" }}>₹2,31,400</strong>
              </div>
              <div style={{ padding: "14px", borderRadius: "var(--r-md)", background: "var(--elev-2)", border: "1px solid var(--line)" }}>
                <span style={{ display: "block", fontSize: "11px", color: "var(--text-3)", marginBottom: "4px" }}>Outbound Traced</span>
                <strong style={{ fontSize: "15px", color: "var(--red)" }}>₹2,17,000</strong>
              </div>
            </div>

            {/* Sub-Navigation Tabs */}
            <TabsNav
              tabs={tabs}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />

            <div style={{ marginTop: "16px" }}>
              {activeTab === "overview" && (
                <p style={{ color: "var(--text-2)", fontSize: "13.5px", lineHeight: "1.6" }}>
                  This wallet was flagged in connection with complaint <strong>{activeCase.complaint_id}</strong>. Rapid-hop distribution was detected within 45 minutes of fund receipt, dispersing assets to secondary intermediate addresses before consolidation at an aggregation node.
                </p>
              )}

              {activeTab === "transactions" && (
                <div className="table-wrap">
                  <div className="table-head grid-tx">
                    <span>Time</span>
                    <span>Chain</span>
                    <span>Hash</span>
                    <span>From → To</span>
                    <span>Asset</span>
                    <span>Value</span>
                    <span>Finality</span>
                  </div>
                  {transactions.slice(0, 5).map((tx) => (
                    <button
                      key={tx.tx_hash}
                      className="table-row grid-tx"
                      onClick={() => openTransaction(tx.tx_hash)}
                    >
                      <span style={{ color: "var(--text-3)" }}>{tx.timestamp.replace("T", " ").slice(11, 19)}</span>
                      <Badge tone={tx.chain_id}>{tx.chain_id}</Badge>
                      <span className="mono" style={{ color: "var(--accent-2)" }}>{tx.tx_hash.slice(0, 10)}...</span>
                      <span className="mono" style={{ fontSize: "12px", color: "var(--text-2)" }}>
                        {tx.from_address} → {tx.to_address}
                      </span>
                      <span>{tx.amount_native} {tx.asset}</span>
                      <strong style={{ color: "var(--gold)" }}>₹{tx.value_inr.toLocaleString("en-IN")}</strong>
                      <Badge tone="green">{tx.finality}</Badge>
                    </button>
                  ))}
                </div>
              )}

              {activeTab === "fund_flow" && (
                <div style={{ padding: "20px", background: "var(--elev-2)", borderRadius: "var(--r-md)", textAlign: "center", color: "var(--text-3)" }}>
                  Fund flow graph for this specific node is rendered inside the Investigation Workstation.
                </div>
              )}

              {activeTab === "behavior" && (
                <div style={{ padding: "16px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px", color: "var(--text-2)", lineHeight: "1.5" }}>
                  <strong>Typology Trigger:</strong> Identified as Origin Node in MULE_NETWORK aggregation pattern. Rapid fan-out structure satisfies criteria under rule version <code>RULE-INDIA-MULE-2026.01</code>.
                </div>
              )}

              {activeTab === "counterparties" && (
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "10px 14px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px" }}>
                    <span className="mono">0xA431...B821 (Intermediary 1)</span>
                    <strong style={{ color: "var(--gold)" }}>₹48,200</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "10px 14px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px" }}>
                    <span className="mono">0xB921...C441 (Intermediary 2)</span>
                    <strong style={{ color: "var(--gold)" }}>₹48,900</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "10px 14px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px" }}>
                    <span className="mono">0xC211...D739 (Intermediary 3)</span>
                    <strong style={{ color: "var(--gold)" }}>₹48,700</strong>
                  </div>
                </div>
              )}

              {activeTab === "evidence" && (
                <div style={{ padding: "16px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px" }}>
                  <span>Anchored Manifest: </span>
                  <span className="mono" style={{ color: "var(--accent-2)" }}>MAN-2026-184721-01</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
