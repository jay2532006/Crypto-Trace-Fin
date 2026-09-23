"use client";

import * as React from "react";
import { Check, Copy } from "lucide-react";
import { formatAddress } from "@/lib/utils";

interface HashDisplayProps {
  hash: string;
  sliceLen?: number;
  label?: string;
  copyable?: boolean;
  showCopy?: boolean;
}

export function HashDisplay({
  hash,
  sliceLen = 8,
  label,
  copyable = true,
  showCopy = true,
}: HashDisplayProps) {
  const isCopyable = copyable && showCopy;
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    if (!isCopyable || !hash) return;
    navigator.clipboard.writeText(hash);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <span className="inline-flex items-center gap-1.5 font-mono text-xs bg-slate-100 dark:bg-slate-800/80 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700 select-all">
      {label && <span className="text-[10px] text-slate-500 font-sans font-semibold uppercase">{label}:</span>}
      <span className="text-slate-800 dark:text-slate-200" title={hash}>
        {formatAddress(hash, sliceLen)}
      </span>
      {copyable && (
        <button
          onClick={handleCopy}
          className="text-slate-400 hover:text-[#1F66B8] dark:hover:text-cyan-400 transition-colors"
          title="Copy full hash to clipboard"
        >
          {copied ? <Check className="h-3 w-3 text-emerald-500" /> : <Copy className="h-3 w-3" />}
        </button>
      )}
    </span>
  );
}
