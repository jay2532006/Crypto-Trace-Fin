// @ts-nocheck
import React from "react";
import type { Case } from "../../types";
import { Badge } from "./Badge";
import { formatInr, formatWallet } from "../../utils/formatters";

interface HeroCaseBannerProps {
  activeCase: Case;
  onOpenTrace?: () => void;
  onCopyWallet?: (address: string) => void;
}

export function HeroCaseBanner({ activeCase, onOpenTrace, onCopyWallet }: HeroCaseBannerProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    void navigator.clipboard.writeText(activeCase.reported_wallet);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
    onCopyWallet?.(activeCase.reported_wallet);
  };

  return (
    <section className="hero active-investigation-brief" aria-labelledby="active-investigation-title">
      <div className="hero-copy">
        <div className="tag"><span>Active Investigation · SIH 26183</span></div>
        <div className="creator">
          <span className="thumb">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true">
              <path d="M12 3L20 7.5V13C20 17.5 16.5 21 12 22C7.5 21 4 17.5 4 13V7.5L12 3Z" fill="url(#hero-crest-grad)" />
              <path d="M9 12L11 14L15 10" stroke="#08090B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <defs><linearGradient id="hero-crest-grad" x1="4" y1="3" x2="20" y2="22"><stop stopColor="#6FD7BC" /><stop offset="1" stopColor="#1C8A72" /></linearGradient></defs>
            </svg>
          </span>
          <span className="name">{activeCase.source_badge} · {activeCase.complaint_id || activeCase.case_id}</span>
        </div>
        <h1 id="active-investigation-title">{activeCase.fraud_type.replace(/_/g, " ")}</h1>
        <p>Investigating suspect wallet on {activeCase.primary_chain.toUpperCase()} reported from {activeCase.state}. Reported amount: <strong>{formatInr(activeCase.fraud_amount_inr)}</strong>.</p>
        <div className="hero-meta-strip">
          <Badge tone={activeCase.source_badge}>{activeCase.source_badge}</Badge>
          <Badge tone={activeCase.primary_chain}>{activeCase.primary_chain}</Badge>
          <span className="badge neutral">DETERMINISTIC CASE</span>
          <span className="hero-wallet mono">{formatWallet(activeCase.reported_wallet)}</span>
        </div>
        <div className="mint"><button onClick={onOpenTrace}><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" /><path d="M12 7V12L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>Launch Bounded Trace · Explore Flow Graph</button></div>
      </div>

      <div className="hero-art">
        <button className="sharebtn" aria-label="Copy reported wallet address" title={copied ? "Address copied" : "Copy suspect wallet address"} onClick={handleCopy}>
          {copied ? <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M20 6L9 17L4 12" stroke="#6FD7BC" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" /></svg> : <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" strokeWidth="1.8" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" strokeWidth="1.8" /></svg>}
        </button>
        <svg className="pixart" viewBox="0 0 280 280" aria-label="Abstract deterministic fund-flow preview">
          <defs>
            <radialGradient id="art-glow" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor="#37B394" stopOpacity="0.22" /><stop offset="60%" stopColor="#E8B24B" stopOpacity="0.07" /><stop offset="100%" stopColor="#08090B" stopOpacity="0" /></radialGradient>
            <linearGradient id="art-shield" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#37B394" /><stop offset="50%" stopColor="#E8B24B" /><stop offset="100%" stopColor="#DE7040" /></linearGradient>
          </defs>
          <circle cx="140" cy="140" r="130" fill="url(#art-glow)" /><circle cx="140" cy="140" r="110" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="1.5" /><circle cx="140" cy="140" r="85" fill="none" stroke="rgba(55,179,148,0.2)" strokeWidth="1.5" strokeDasharray="5 7" /><circle cx="140" cy="140" r="60" fill="none" stroke="rgba(232,178,75,0.25)" strokeWidth="1.5" />
          <circle cx="140" cy="80" r="6" fill="#6FD7BC" /><circle cx="190" cy="120" r="5" fill="#E8B24B" /><circle cx="180" cy="180" r="6" fill="#37B394" /><circle cx="100" cy="175" r="5" fill="#DE7040" /><circle cx="90" cy="115" r="6" fill="#6FD7BC" />
          <line x1="140" y1="80" x2="190" y2="120" stroke="#37B394" strokeWidth="1.5" strokeOpacity="0.6" /><line x1="190" y1="120" x2="180" y2="180" stroke="#E8B24B" strokeWidth="1.5" strokeOpacity="0.6" /><line x1="180" y1="180" x2="100" y2="175" stroke="#DE7040" strokeWidth="1.5" strokeOpacity="0.6" strokeDasharray="3 4" /><line x1="100" y1="175" x2="90" y2="115" stroke="#37B394" strokeWidth="1.5" strokeOpacity="0.6" /><line x1="90" y1="115" x2="140" y2="80" stroke="#6FD7BC" strokeWidth="1.5" strokeOpacity="0.6" />
          <polygon points="140,105 165,140 140,175 115,140" fill="#121417" stroke="url(#art-shield)" strokeWidth="2.5" /><circle cx="140" cy="140" r="8" fill="#6FD7BC" /><circle cx="140" cy="140" r="14" fill="none" stroke="#37B394" strokeWidth="1" strokeOpacity="0.7" />
        </svg>
      </div>
    </section>
  );
}
