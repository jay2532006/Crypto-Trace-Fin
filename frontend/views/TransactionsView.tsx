// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { Chain, Transaction } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { RapidFlowStrip } from "../components/graph/RapidFlowStrip";
import { EmptyState, SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";
import { formatDateTime, formatInr, formatTechnicalId } from "../utils/formatters";

interface TransactionsViewProps {
  openTransaction: (txHash: string) => Promise<void>;
}

export function TransactionsView({ openTransaction }: TransactionsViewProps) {
  const [chain, setChain] = useState<Chain | "all">("all");
  const [query, setQuery] = useState("");
  const [paused, setPaused] = useState(true);
  const [stage, setStage] = useState(0);
  const [activeIndex, setActiveIndex] = useState(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const stages = ["FETCH", "VALIDATE", "EXTRACT", "NORMALIZE", "DEDUPLICATE", "PERSIST", "COMMIT", "ADVANCE"];

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    mockApi.getTransactions({ chain, query })
      .then((res) => { if (active) setTransactions(res.data); })
      .catch((err) => { if (active) setError(err.message || "Failed to load transaction feed."); })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [chain, query]);

  useEffect(() => {
    if (paused || !transactions.length) return;
    const timer = window.setInterval(() => {
      setStage((current) => (current + 1) % stages.length);
      setActiveIndex((current) => (current + 1) % transactions.length);
    }, 1100);
    return () => window.clearInterval(timer);
  }, [paused, transactions.length, stages.length]);

  return (
    <div className="view-stack transactions-view">
      <div className="page-heading">
        <div>
          <h1>Transaction Ledger</h1>
          <p>Inspect normalized fixture transactions by chain, address, provider, and provenance.</p>
        </div>
        <div className="page-heading-meta"><span className="context-chip">Synthetic stream</span><Badge tone="green">Normalized feed</Badge></div>
      </div>

      <div className="toolbar-panel">
        <div className="toolbar">
          <select className="form-select" value={chain} onChange={(e) => setChain(e.target.value as Chain | "all")} aria-label="Filter transactions by chain">
            <option value="all">All Chains</option><option value="ethereum">Ethereum</option><option value="polygon">Polygon</option><option value="tron">Tron</option><option value="bitcoin">Bitcoin</option>
          </select>
          <input className="form-input transaction-search" placeholder="Filter by hash, address, or provider RPC..." value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Filter transactions" />
        </div>
        <button className={paused ? "btn-primary" : "btn-secondary"} onClick={() => setPaused((current) => !current)}>{paused ? "Start Stream Replay" : "Pause Stream Replay"}</button>
      </div>

      <section className="pipeline-section">
        <div className="pipeline-head"><span className="section-kicker">8-Stage Normalization Pipeline</span><span className="mono text-accent">{paused ? "Replay paused" : `Current stage: ${stages[stage]}`}</span></div>
        <div className="stream-pipeline">
          {stages.map((step, index) => <div key={step} className={`pipeline-stage ${!paused && index === stage ? "active" : !paused && index < stage ? "done" : ""}`}>{step}</div>)}
        </div>
      </section>

      <RapidFlowStrip rows={transactions} activeIndex={activeIndex} onOpen={openTransaction} isPlaying={!paused} />

      <section className="kestrel-panel">
        <div className="kestrel-panel-head"><div><h2>Replayed Transaction Ledger</h2><p>Showing {transactions.length} normalized transactions · Select a row to inspect full provenance.</p></div></div>
        {loading ? <SkeletonLoader text="Loading transaction ledger..." /> : error ? <ErrorNotice message={error} /> : transactions.length === 0 ? <EmptyState title="No transactions match this filter" description="Try another chain, hash, address, or provider." /> : (
          <div className="table-wrap">
            <div className="table-head grid-tx"><span>Time</span><span>Chain</span><span>Hash</span><span>From → To</span><span>Asset</span><span>Value</span><span>Finality</span></div>
            {transactions.map((tx) => {
              const isActive = transactions[activeIndex]?.tx_hash === tx.tx_hash && !paused;
              return (
                <button key={tx.tx_hash} className={`table-row grid-tx ${isActive ? "active-stream-row" : ""}`} onClick={() => void openTransaction(tx.tx_hash)}>
                  <span className="table-muted">{formatDateTime(tx.timestamp).slice(11, 19)}</span>
                  <Badge tone={tx.chain_id}>{tx.chain_id}</Badge>
                  <span className="mono text-accent">{formatTechnicalId(tx.tx_hash)}</span>
                  <span className="mono table-technical">{formatTechnicalId(tx.from_address, 8, 4)} → {formatTechnicalId(tx.to_address, 8, 4)}</span>
                  <span>{tx.amount_native} {tx.asset}</span>
                  <strong className="text-gold">{formatInr(tx.value_inr)}</strong>
                  <Badge tone="green">{tx.finality}</Badge>
                </button>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
