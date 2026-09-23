'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  Search,
  Sliders,
  ShieldAlert,
  ArrowRight,
  ExternalLink,
  Copy,
  Check,
  Building2,
  FileText,
  AlertTriangle,
  Play,
  RotateCcw,
  Layers,
  Activity,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { ConfidencePill } from '@/components/forensic/ConfidencePill';
import { AddressBadge } from '@/components/forensic/AddressBadge';
import { HashDisplay } from '@/components/forensic/HashDisplay';
import { UncertaintyBanner } from '@/components/forensic/UncertaintyBanner';
import { CytoscapeGraph } from '@/features/graph/CytoscapeGraph';
import { apiClient } from '@/lib/api-client';
import { formatAddress, formatCrypto, formatINR, formatUSD, formatDateTime } from '@/lib/utils';
import type { TraceResult, GraphNode, GraphEdge, HopNode } from '@/types/domain';

const PRESET_BENCHMARKS = [
  {
    name: 'WazirX Security Incident (ETH)',
    address: '0x0cbe050f75bc8f8c2d6c0d249eff12d71a28169b',
    chain: 'ETH',
    description: 'High-profile multi-stage laundering across decentralised liquidity pools.',
  },
  {
    name: 'Mule Syndicate Ring (USDT)',
    address: '0x71c8fb9284285741829e05e55099e0344d9f1091',
    chain: 'ETH',
    description: 'Rapid velocity peeling chain through 3+ intermediary mule accounts to VASP.',
  },
  {
    name: 'Tornado Mixer Boundary (ETH)',
    address: '0xd90e2f925da726b50c4ed8d0fb90ad053324f31b',
    chain: 'ETH',
    description: 'Privacy pool hop exhibiting cryptographic break in deterministic attribution.',
  },
];

function InvestigationsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialAddress = searchParams?.get('address') || '';

  const [address, setAddress] = useState(initialAddress);
  const [chain, setChain] = useState<'ETH' | 'BTC' | 'BSC' | 'POLYGON'>('ETH');
  const [maxHops, setMaxHops] = useState(5);
  const [mode, setMode] = useState<'DEMO' | 'LIVE'>('DEMO');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [traceData, setTraceData] = useState<TraceResult | null>(null);
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [copied, setCopied] = useState(false);

  // Auto-execute if query param exists
  useEffect(() => {
    if (initialAddress) {
      handleExecuteTrace(initialAddress);
    }
  }, [initialAddress]);

  const handleExecuteTrace = async (targetAddr?: string) => {
    const queryAddr = targetAddr || address;
    if (!queryAddr.trim()) {
      setError('Please input a suspect wallet or contract address.');
      return;
    }

    setLoading(true);
    setError(null);
    setSelectedNode(null);

    try {
      const response = await apiClient.post<any>('/api/v1/trace', {
        address: queryAddr.trim(),
        chain: chain,
        max_hops: maxHops,
        mode: mode,
      });

      const data = response.data;
      setTraceData(data);

      // Normalize Graph Nodes
      const nodes: GraphNode[] = (data.nodes || []).map((n: any) => ({
        id: n.id,
        label: n.label || formatAddress(n.id),
        address: n.id,
        type: (n.type || 'INTERMEDIARY').toUpperCase(),
        balance: n.balance,
        risk_score: n.risk_score || data.risk?.composite_risk_score,
        vasp_name: n.vasp_name || (n.type === 'vasp' ? data.attribution?.vasp_name : undefined),
        depth: n.depth,
      }));

      // Normalize Graph Edges
      const edges: GraphEdge[] = (data.edges || []).map((e: any, idx: number) => ({
        id: e.id || `edge-${idx}`,
        source: e.from || e.source,
        target: e.to || e.target,
        amount: e.amount || 0,
        token: e.asset || e.token || 'ETH',
        tx_hash: e.tx_hash,
        is_mixer_boundary: e.is_mixer_boundary || data.typologies?.includes('MIXER_BOUNDARY'),
      }));

      setGraphNodes(nodes);
      setGraphEdges(edges);
    } catch (err: any) {
      console.error('Trace execution failed:', err);
      setError(
        err.response?.data?.detail ||
          'Failed to execute trace query. Verify backend connectivity on port 8765.'
      );
    } finally {
      setLoading(false);
    }
  };

  const loadBenchmark = (b: typeof PRESET_BENCHMARKS[0]) => {
    setAddress(b.address);
    setChain(b.chain as any);
    handleExecuteTrace(b.address);
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const hasMixer = traceData?.typologies?.includes('MIXER_BOUNDARY');
  const hasMule = traceData?.typologies?.includes('MULE_NETWORK');

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-navy-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Forensic Trace & Attribution</h1>
            <Badge variant="navy">SIH-26183 Engine</Badge>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Deterministic multi-hop ledger traversal, typology inference, and VASP nodal identification.
          </p>
        </div>

        {/* Benchmark Presets Dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium hidden sm:inline">Benchmark Cases:</span>
          {PRESET_BENCHMARKS.map((b, idx) => (
            <button
              key={idx}
              onClick={() => loadBenchmark(b)}
              disabled={loading}
              className="text-xs px-2.5 py-1.5 rounded-lg border border-navy-700 bg-navy-900/60 hover:bg-navy-800 text-slate-300 hover:text-white transition-all text-left"
              title={b.description}
            >
              {b.name.split(' ')[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Query Configuration Deck */}
      <Card>
        <CardContent className="p-4 sm:p-5">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
            {/* Suspect Address Input */}
            <div className="md:col-span-6 space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                Suspect Address / Contract Hash
              </label>
              <div className="relative">
                <Input
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="0x... or Bitcoin Base58/Bech32 address"
                  className="font-mono text-xs pr-10"
                />
                <button
                  type="button"
                  onClick={() => setAddress('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs"
                >
                  Clear
                </button>
              </div>
            </div>

            {/* Blockchain Network */}
            <div className="md:col-span-2 space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                Network
              </label>
              <select
                value={chain}
                onChange={(e) => setChain(e.target.value as any)}
                className="w-full h-10 px-3 rounded-lg border border-navy-700 bg-navy-900 text-slate-200 text-xs font-medium focus:ring-1 focus:ring-blue-500 outline-none"
              >
                <option value="ETH">Ethereum (ETH)</option>
                <option value="BTC">Bitcoin (BTC)</option>
                <option value="BSC">BNB Chain (BSC)</option>
                <option value="POLYGON">Polygon (POL)</option>
              </select>
            </div>

            {/* Max Hops Slider */}
            <div className="md:col-span-2 space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold uppercase tracking-wider text-slate-300">Max Depth</span>
                <span className="font-mono text-blue-400 font-bold">{maxHops} Hops</span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                value={maxHops}
                onChange={(e) => setMaxHops(Number(e.target.value))}
                className="w-full accent-blue-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
              />
            </div>

            {/* Action Button */}
            <div className="md:col-span-2">
              <Button
                variant="primary"
                onClick={() => handleExecuteTrace()}
                isLoading={loading}
                className="w-full flex items-center justify-center gap-2 text-xs font-semibold tracking-wide"
              >
                <Play className="h-3.5 w-3.5 fill-current" />
                EXECUTE TRACE
              </Button>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 rounded-lg bg-red-950/50 border border-red-800 text-red-300 text-xs flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 shrink-0 text-red-400" />
              <span>{error}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Uncertainty & Forensic Boundary Disclosures */}
      {hasMixer && (
        <UncertaintyBanner
          level="HIGH"
          title="Mixer Boundary Incurred — Cryptographic Attribution Break"
          description="A privacy pool or mixer contract was identified in this trace chain. Downstream attribution links are heuristic hypotheses and cannot be represented as strict cryptographic certainty in court filings."
        />
      )}
      {hasMule && !hasMixer && (
        <UncertaintyBanner
          level="MEDIUM"
          title="Mule Syndicate Velocity Pattern Detected"
          description="Funds traversed >= 3 intermediary wallets with high turnover within 60 minutes. Presumptive intermediary nodes have been flagged for cooperative Section 91 preservation."
        />
      )}

      {/* Trace Results & Metrics Deck */}
      {traceData && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Discovered Hops
              </span>
              <div className="text-2xl font-bold font-mono text-white mt-1">
                {traceData.hops?.length || 0}
                <span className="text-xs text-slate-500 font-sans ml-1.5 font-normal">
                  ({traceData.nodes?.length || 0} Entities)
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Attributed Destination
              </span>
              <div className="text-lg font-bold text-blue-400 truncate mt-1 flex items-center gap-1.5">
                <Building2 className="h-4 w-4 shrink-0 text-blue-400" />
                {traceData.attribution?.vasp_name || 'No Direct VASP'}
              </div>
              <div className="mt-1">
                <ConfidencePill
                  level={traceData.attribution?.confidence_band || 'LOW'}
                  score={traceData.attribution?.score}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Risk Classification
              </span>
              <div className="text-2xl font-bold font-mono text-amber-400 mt-1">
                {traceData.risk?.composite_risk_score
                  ? `${Math.round(traceData.risk.composite_risk_score * 100)}%`
                  : 'N/A'}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Level: <span className="font-semibold text-slate-300">{traceData.risk?.risk_level || 'EVALUATED'}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Audit & Execution
              </span>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                {traceData.execution_time_ms ? `${traceData.execution_time_ms} ms` : 'Instant'}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Completeness: <span className="text-slate-300 font-mono">{traceData.data_completeness_pct}%</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Forensic Canvas & Inspection Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Graph Canvas */}
        <div className={selectedNode ? 'lg:col-span-8' : 'lg:col-span-12'}>
          <CytoscapeGraph
            nodes={graphNodes}
            edges={graphEdges}
            onNodeSelect={(node) => setSelectedNode(node)}
            height="580px"
          />
        </div>

        {/* Selected Node Inspector Drawer */}
        {selectedNode && (
          <div className="lg:col-span-4 space-y-4 animate-fade-in">
            <Card className="border-blue-500/40">
              <CardHeader className="bg-navy-900/80 border-b border-navy-800 pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        selectedNode.type === 'SUSPECT'
                          ? 'bg-red-500'
                          : selectedNode.type === 'VASP'
                          ? 'bg-blue-500'
                          : selectedNode.type === 'MIXER'
                          ? 'bg-amber-500'
                          : 'bg-purple-500'
                      }`}
                    />
                    <CardTitle className="text-sm">Entity Inspector</CardTitle>
                  </div>
                  <Badge variant="navy">{selectedNode.type}</Badge>
                </div>
              </CardHeader>
              <CardContent className="p-4 space-y-4 text-xs">
                {/* Address block */}
                <div>
                  <span className="text-slate-500 uppercase tracking-wider text-[10px] font-semibold">
                    Address
                  </span>
                  <div className="flex items-center justify-between mt-1 p-2 rounded-lg bg-navy-950 border border-navy-800 font-mono text-[11px] text-blue-300 break-all">
                    <span>{selectedNode.address}</span>
                    <button
                      onClick={() => handleCopy(selectedNode.address)}
                      className="p-1 hover:text-white transition-colors shrink-0 ml-2"
                      title="Copy Address"
                    >
                      {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5 text-slate-400" />}
                    </button>
                  </div>
                </div>

                {/* VASP / Label info if present */}
                {selectedNode.vasp_name && (
                  <div>
                    <span className="text-slate-500 uppercase tracking-wider text-[10px] font-semibold">
                      Identified VASP
                    </span>
                    <div className="mt-1 p-2 rounded-lg bg-blue-950/30 border border-blue-800 text-blue-200 font-medium flex items-center justify-between">
                      <span className="flex items-center gap-1.5">
                        <Building2 className="h-4 w-4 text-blue-400" />
                        {selectedNode.vasp_name}
                      </span>
                      <span className="text-[10px] text-blue-400 uppercase">FIU Registered</span>
                    </div>
                  </div>
                )}

                {/* Depth / Hop metrics */}
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-2.5 rounded-lg bg-navy-900 border border-navy-800">
                    <span className="text-slate-500 text-[10px] block">Graph Depth</span>
                    <span className="text-sm font-bold text-white font-mono">
                      {selectedNode.depth !== undefined ? `Hop ${selectedNode.depth}` : 'Root'}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-navy-900 border border-navy-800">
                    <span className="text-slate-500 text-[10px] block">Risk Score</span>
                    <span className="text-sm font-bold text-amber-400 font-mono">
                      {selectedNode.risk_score ? `${Math.round(selectedNode.risk_score * 100)}%` : 'Evaluated'}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="pt-2 border-t border-navy-800 space-y-2">
                  <Button
                    variant="primary"
                    className="w-full text-xs flex items-center justify-center gap-2"
                    onClick={() => {
                      router.push(
                        `/legal-notices?vasp=${encodeURIComponent(
                          selectedNode.vasp_name || 'Destination VASP'
                        )}&address=${encodeURIComponent(selectedNode.address)}`
                      );
                    }}
                  >
                    <FileText className="h-3.5 w-3.5" />
                    Draft Section 91 Notice
                  </Button>

                  <Button
                    variant="outline"
                    className="w-full text-xs flex items-center justify-center gap-2"
                    onClick={() => {
                      router.push(`/attribution?vasp=${encodeURIComponent(selectedNode.vasp_name || 'WAZIRX')}`);
                    }}
                  >
                    <Activity className="h-3.5 w-3.5 text-blue-400" />
                    View VASP Attribution Matrix
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Forensic Hop Ledger Table */}
      {traceData?.hops && traceData.hops.length > 0 && (
        <Card>
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-bold tracking-wide">
                Hop-by-Hop Cryptographic Ledger
              </CardTitle>
              <span className="text-xs text-slate-400 font-mono">
                {traceData.hops.length} Sequential Transactions
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-navy-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-navy-800">
                <tr>
                  <th className="py-2.5 px-4">Hop</th>
                  <th className="py-2.5 px-4">From Wallet</th>
                  <th className="py-2.5 px-4">To Wallet</th>
                  <th className="py-2.5 px-4">Volume</th>
                  <th className="py-2.5 px-4">Transaction Hash</th>
                  <th className="py-2.5 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800 text-slate-300 font-mono">
                {traceData.hops.map((hop: any, idx: number) => (
                  <tr key={idx} className="hover:bg-navy-900/50 transition-colors">
                    <td className="py-2.5 px-4 font-bold text-blue-400">#{hop.hop_number || idx + 1}</td>
                    <td className="py-2.5 px-4 font-sans">
                      <AddressBadge address={hop.from_address || hop.from} />
                    </td>
                    <td className="py-2.5 px-4 font-sans">
                      <AddressBadge address={hop.to_address || hop.to} />
                    </td>
                    <td className="py-2.5 px-4 text-emerald-400 font-bold">
                      {formatCrypto(hop.amount, hop.asset || 'ETH')}
                    </td>
                    <td className="py-2.5 px-4">
                      {hop.tx_hash ? (
                        <HashDisplay hash={hop.tx_hash} showCopy />
                      ) : (
                        <span className="text-slate-500 font-sans italic">Synthesised</span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 font-sans">
                      {hop.timestamp_epoch
                        ? formatDateTime(new Date(hop.timestamp_epoch * 1000).toISOString())
                        : 'Recent'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function InvestigationsPage() {
  return (
    <React.Suspense fallback={<div className="p-8 text-center text-slate-400">Loading Forensic Trace Canvas...</div>}>
      <InvestigationsContent />
    </React.Suspense>
  );
}
