// @ts-nocheck
import React from "react";
import type { Chain, Transaction } from "../../types";
import { Badge } from "../common/Badge";
import { formatInr, formatTechnicalId } from "../../utils/formatters";

interface RapidFlowStripProps {
  rows: Transaction[];
  activeIndex: number;
  onOpen: (txHash: string) => Promise<void>;
  onSelect?: (index: number) => void;
  large?: boolean;
  isPlaying?: boolean;
}

export function RapidFlowStrip({ rows, activeIndex, onOpen, onSelect, large = false, isPlaying = false }: RapidFlowStripProps) {
  const visible = rows.slice(0, large ? 8 : 6);
  const active = rows.length ? rows[activeIndex % rows.length] : null;
  const chains: Chain[] = ["ethereum", "polygon", "tron", "bitcoin"];
  const chainStats = chains.map((chain) => {
    const chainRows = rows.filter((row) => row.chain_id === chain);
    const value = chainRows.reduce((sum, row) => sum + row.value_inr, 0);
    return { chain, count: chainRows.length, value, sample: chainRows[0] };
  });
  const maxChainValue = Math.max(1, ...chainStats.map((c) => c.value));

  return (
    <section className="rapid-flow">
      <div className="flow-head">
        <div>
          <span className="section-kicker">Rapid Transaction Streaming Flow</span>
          <h3>
            {active ? (
              <><strong className="text-accent">{active.chain_id.toUpperCase()}</strong> · <span className="mono">{formatTechnicalId(active.tx_hash, 7, 5)}</span> · <strong className="text-gold">{formatInr(active.value_inr)}</strong></>
            ) : "No fixture transactions available"}
          </h3>
        </div>
        <div className="flow-status">
          <span className="badge neutral">FIXTURE STREAM</span>
          <span className={`badge ${isPlaying ? "green" : "amber"}`}>{isPlaying ? "REPLAY PLAYING" : "REPLAY PAUSED"}</span>
        </div>
      </div>

      <div className="flow-lane" aria-label="Replayed transaction sequence">
        {visible.map((tx, index) => {
          const isActive = active?.tx_hash === tx.tx_hash;
          return (
            <button
              key={tx.tx_hash}
              className={`flow-chip ${isActive ? "active" : ""}`}
              onClick={() => { onSelect?.(index); void onOpen(tx.tx_hash); }}
              title={`Inspect ${tx.tx_hash}`}
            >
              <span className="flow-dot" />
              <span className="mono">{formatTechnicalId(tx.tx_hash, 7, 5)}</span>
              <strong>{tx.asset}</strong>
              <small>hop {tx.hop}</small>
            </button>
          );
        })}
      </div>

      <div className="flow-visual-grid">
        {chainStats.map((item) => (
          <button
            key={item.chain}
            className={`chain-flow ${active?.chain_id === item.chain ? "active" : ""}`}
            onClick={() => item.sample && void onOpen(item.sample.tx_hash)}
            disabled={!item.sample}
          >
            <div className="flow-row-head">
              <Badge tone={item.chain}>{item.chain}</Badge>
              <strong>{item.count} txs</strong>
            </div>
            <div className="chain-bar"><i style={{ width: `${Math.max(8, (item.value / maxChainValue) * 100)}%` }} /></div>
            <div className="flow-row-meta"><span>{formatInr(item.value)}</span><span>{isPlaying ? "Replay active" : "Snapshot"}</span></div>
          </button>
        ))}
      </div>
    </section>
  );
}
