// @ts-nocheck
import React from "react";
import type { Case } from "../types";
import { mockApi } from "../services/mockApi";
import { HeroCaseBanner } from "../components/common/HeroCaseBanner";
import { Badge } from "../components/common/Badge";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";
import { HalyardMetricCards } from "../components/common/HalyardMetricCards";
import { formatInr, formatTechnicalId } from "../utils/formatters";

interface OverviewViewProps {
  activeCase: Case;
  onNavigate: (route: string) => void;
  openTransaction: (txHash: string) => Promise<void>;
  uiMode?: "halyard" | "kestrel" | "classic";
}

export function OverviewView({ activeCase, onNavigate, openTransaction }: OverviewViewProps) {
  const [cases, setCases] = React.useState<any>(null);
  const [txs, setTxs] = React.useState<any>(null);
  const [alerts, setAlerts] = React.useState<any>(null);
  const [status, setStatus] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([
      mockApi.getCases(),
      mockApi.getTransactions({ limit: 6 }),
      mockApi.getAlerts(),
      mockApi.getSystemStatus()
    ])
      .then(([casesRes, txRes, alertsRes, statusRes]) => {
        if (!active) return;
        setCases(casesRes.data);
        setTxs(txRes.data);
        setAlerts(alertsRes.data);
        setStatus(statusRes.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load overview data.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, []);

  if (loading) return <SkeletonLoader text="Loading investigator command center..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div className="view-stack overview-view">
      <div className="page-heading">
        <div>
          <h1>Investigator Command Center</h1>
          <p>Identify the active case, review its trace condition, and move directly into the next forensic action.</p>
        </div>
        <div className="page-heading-meta">
          <span className="context-chip">Window: <strong>24 Hours</strong></span>
          <span className="context-chip context-chip-accent">Active Case: <strong>{activeCase.case_id}</strong></span>
        </div>
      </div>

      <HeroCaseBanner activeCase={activeCase} onOpenTrace={() => onNavigate("investigations")} />

      <HalyardMetricCards
        tracedAmount={formatInr(720500)}
        hopDepth={4}
        vaspCount={3}
        alertsCount={alerts?.length || 18}
      />

      <section>
        <div className="sec-head">
          <div>
            <h2>Forensic Modules</h2>
            <p>Direct paths into graph tracing, attribution, cross-chain review, and preservation.</p>
          </div>
          <button className="link-btn" onClick={() => onNavigate("investigations")}>Open Full Workstation →</button>
        </div>

        <div className="kestrel-grid-4 capability-register">
          <button type="button" className="card card-action" onClick={() => onNavigate("typologies")}>
            <div className="thumb">
              <svg viewBox="0 0 320 200" aria-hidden="true">
                <defs><linearGradient id="grad-mule" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#1C2E2A" /><stop offset="1" stopColor="#08090B" /></linearGradient></defs>
                <rect width="320" height="200" fill="url(#grad-mule)" />
                <circle cx="160" cy="90" r="32" fill="#37B394" fillOpacity="0.2" stroke="#37B394" strokeWidth="2" />
                <circle cx="90" cy="140" r="16" fill="#14171D" stroke="#6FD7BC" strokeWidth="1.5" />
                <circle cx="230" cy="140" r="16" fill="#14171D" stroke="#6FD7BC" strokeWidth="1.5" />
                <line x1="90" y1="140" x2="140" y2="105" stroke="#6FD7BC" strokeWidth="2" strokeDasharray="3 4" />
                <line x1="230" y1="140" x2="180" y2="105" stroke="#6FD7BC" strokeWidth="2" strokeDasharray="3 4" />
                <text x="160" y="95" textAnchor="middle" fill="#6FD7BC" fontSize="11" fontWeight="700">AGGREGATOR</text>
              </svg>
            </div>
            <div className="card-body">
              <div className="card-meta"><Badge tone="india">India Pattern</Badge><Badge tone="amber">Medium</Badge></div>
              <h3>Mule network</h3>
              <span>Multi-victim aggregation pattern with explicit behavioral correlation.</span>
              <span className="card-action-label">View typology →</span>
            </div>
          </button>

          <button type="button" className="card card-action" onClick={() => onNavigate("vasp")}>
            <div className="thumb">
              <svg viewBox="0 0 320 200" aria-hidden="true">
                <defs><linearGradient id="grad-vasp" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#2E2818" /><stop offset="1" stopColor="#08090B" /></linearGradient></defs>
                <rect width="320" height="200" fill="url(#grad-vasp)" />
                <path d="M40 130 H280" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <rect x="70" y="80" width="34" height="50" rx="4" fill="#E8B24B" /><rect x="120" y="60" width="34" height="70" rx="4" fill="#DE7040" /><rect x="170" y="40" width="34" height="90" rx="4" fill="#37B394" /><rect x="220" y="55" width="34" height="75" rx="4" fill="#6FD7BC" />
              </svg>
            </div>
            <div className="card-body">
              <div className="card-meta"><Badge tone="green">Score 0.82</Badge><Badge tone="blue">v1.2 Policy</Badge></div>
              <h3>VASP attribution</h3>
              <span>Review normalized candidate-cluster evidence and its confidence band.</span>
              <span className="card-action-label">Review attribution →</span>
            </div>
          </button>

          <button type="button" className="card card-action" onClick={() => onNavigate("cross-chain")}>
            <div className="thumb">
              <svg viewBox="0 0 320 200" aria-hidden="true">
                <defs><linearGradient id="grad-xchain" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#1A2433" /><stop offset="1" stopColor="#08090B" /></linearGradient></defs>
                <rect width="320" height="200" fill="url(#grad-xchain)" />
                <circle cx="80" cy="100" r="26" fill="#121417" stroke="#4F9FD1" strokeWidth="2" /><text x="80" y="104" textAnchor="middle" fill="#4F9FD1" fontSize="10" fontWeight="700">ETH</text>
                <circle cx="240" cy="100" r="26" fill="#121417" stroke="#9D7BFF" strokeWidth="2" /><text x="240" y="104" textAnchor="middle" fill="#9D7BFF" fontSize="10" fontWeight="700">POLY</text>
                <path d="M110 100 Q160 60 210 100" fill="none" stroke="#6FD7BC" strokeWidth="2" strokeDasharray="4 4" />
                <rect x="140" y="65" width="40" height="18" rx="4" fill="#0B0C0E" stroke="#37B394" /><text x="160" y="77" textAnchor="middle" fill="#6FD7BC" fontSize="8" fontWeight="700">BRIDGE</text>
              </svg>
            </div>
            <div className="card-body">
              <div className="card-meta"><Badge tone="purple">Cross-Chain</Badge><Badge tone="green">Bridge Proven</Badge></div>
              <h3>Cross-chain provenance</h3>
              <span>Compare direct bridge events with heuristic movement correlations.</span>
              <span className="card-action-label">Inspect bridge evidence →</span>
            </div>
          </button>

          <button type="button" className="card card-action" onClick={() => onNavigate("supervisor")}>
            <div className="thumb">
              <svg viewBox="0 0 320 200" aria-hidden="true">
                <defs><linearGradient id="grad-sup" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#251F2E" /><stop offset="1" stopColor="#08090B" /></linearGradient></defs>
                <rect width="320" height="200" fill="url(#grad-sup)" />
                <path d="M160 50 L220 80 V130 C220 160 160 180 160 180 C160 180 100 160 100 130 V80 Z" fill="#14171D" stroke="#E8B24B" strokeWidth="2" />
                <path d="M145 115 L155 125 L175 105" stroke="#6FD7BC" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div className="card-body">
              <div className="card-meta"><Badge tone="green">Supervisor Gated</Badge><Badge tone="neutral">Section 91 CrPC</Badge></div>
              <h3>Preservation workflow</h3>
              <span>Draft a preservation request with supervisor authorization and audit context.</span>
              <span className="card-action-label">Open preservation →</span>
            </div>
          </button>
        </div>
      </section>

      <div className="kestrel-grid-3 evidence-layout">
        <section className="kestrel-panel evidence-table">
          <div className="kestrel-panel-head">
            <div>
              <h2>Recent Streaming Activity</h2>
              <p>Newest replayed transactions from the fixture queue</p>
            </div>
            <button className="link-btn" onClick={() => onNavigate("transactions")}>View All →</button>
          </div>

          <div className="table-wrap">
            <div className="table-head grid-tx"><span>Time</span><span>Chain</span><span>Hash</span><span>From → To</span><span>Asset</span><span>Value</span><span>Finality</span></div>
            {txs?.map((tx: any) => (
              <button key={tx.tx_hash} className="table-row grid-tx" onClick={() => void openTransaction(tx.tx_hash)}>
                <span className="table-muted">{tx.timestamp.slice(11, 19)}</span>
                <Badge tone={tx.chain_id}>{tx.chain_id}</Badge>
                <span className="mono text-accent">{formatTechnicalId(tx.tx_hash)}</span>
                <span className="mono table-technical">{formatTechnicalId(tx.from_address, 8, 4)} → {formatTechnicalId(tx.to_address, 8, 4)}</span>
                <span>{tx.amount_native} {tx.asset}</span>
                <strong className="text-gold">{formatInr(tx.value_inr)}</strong>
                <Badge tone="green">{tx.finality}</Badge>
              </button>
            ))}
          </div>
        </section>

        <section className="kestrel-panel provider-panel">
          <div className="kestrel-panel-head">
            <div>
              <h2>Simulated Chain Providers</h2>
              <p>Fixture-mode RPC network states</p>
            </div>
          </div>
          <div className="provider-list">
            {status?.chains && Object.entries(status.chains).map(([chain, item]: any) => (
              <div className="provider-row" key={chain}>
                <div className="inline-cluster"><Badge tone={chain}>{chain}</Badge><span>Block</span></div>
                <strong className="mono">#{item.last_block}</strong>
                <Badge tone="green">{item.status}</Badge>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
