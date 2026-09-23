"use client";

import * as React from "react";
import { Copy, ExternalLink, Check } from "lucide-react";
import { formatAddress } from "@/lib/utils";

interface AddressBadgeProps {
  address: string;
  chain?: string;
  label?: string;
  className?: string;
}

export function AddressBadge({ address, chain = "ETH", label, className }: AddressBadgeProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const explorerUrl =
    chain === "BTC"
      ? `https://mempool.space/address/${address}`
      : chain === "TRON"
      ? `https://tronscan.org/#/address/${address}`
      : chain === "POLYGON"
      ? `https://polygonscan.com/address/${address}`
      : `https://etherscan.io/address/${address}`;

  return (
    <div className={`inline-flex items-center gap-1.5 font-mono text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded px-2 py-0.5 ${className || ""}`}>
      <span className="text-[10px] font-sans font-bold px-1 rounded bg-[#EAF3FC] text-[#062B6F] dark:bg-blue-950 dark:text-blue-300">
        {chain.toUpperCase()}
      </span>
      {label && <span className="font-sans font-semibold text-slate-500 text-[11px]">{label}:</span>}
      <span className="text-slate-800 dark:text-slate-200" title={address}>
        {formatAddress(address, 6)}
      </span>
      <button
        onClick={handleCopy}
        className="text-slate-400 hover:text-[#1F66B8] dark:hover:text-cyan-400 transition-colors ml-1"
        title="Copy full address"
      >
        {copied ? <Check className="h-3 w-3 text-emerald-500" /> : <Copy className="h-3 w-3" />}
      </button>
      <a
        href={explorerUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="text-slate-400 hover:text-[#1F66B8] dark:hover:text-cyan-400 transition-colors"
        title="View in public blockchain explorer"
      >
        <ExternalLink className="h-3 w-3" />
      </a>
    </div>
  );
}
