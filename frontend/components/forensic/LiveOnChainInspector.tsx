'use client';

import React, { useState } from 'react';
import {
  Activity,
  Search,
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  TrendingUp,
  RefreshCw,
  GitFork,
  Check,
  Copy,
  Layers,
  AlertCircle,
  Database,
  Lock,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { AddressBadge } from '@/components/forensic/AddressBadge';
import { apiClient } from '@/lib/api-client';
import { formatAddress, formatCrypto, formatINR, formatUSD, formatDateTime } from '@/lib/utils';
import type { GraphNode, GraphEdge } from '@/types/domain';

export const VERIFIED_TEST_WALLETS = [
  {
    name: 'Vitalik Buterin (ETH)',
    address: '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
    chain: 'ETH',
    role: 'Founder / Active High Net Worth',
    tag: 'Etherscan V2',
  },
  {
    name: 'Binance Hot Wallet (ETH)',
    address: '0x28c6c06298d514db089934071355e5743bf21d60',
    chain: 'ETH',
    role: 'VASP Institutional Gateway',
    tag: 'Etherscan V2',
  },
  {
    name: 'Official USDT Contract (TRON)',
    address: 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
    chain: 'TRON',
    role: 'Tether TRC-20 Token Master',
    tag: 'TronGrid Mainnet',
  },
  {
    name: 'Satoshi Nakamoto Genesis (BTC)',
    address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    chain: 'BTC',
    role: 'Historic Genesis Node',
    tag: 'Blockstream Esplora',
  },
  {
    name: 'WazirX Incident Cluster (ETH)',
    address: '0x0cbe050f75bc8f8c2d6c0d249eff12d71a28169b',
    chain: 'ETH',
    role: 'Hackathon Benchmark Wallet',
    tag: 'Etherscan V2',
  },
];

interface LiveOnChainInspectorProps {
  onLoadTransactionsIntoGraph?: (nodes: GraphNode[], edges: GraphEdge[], suspectAddress: string) => void;
  onExecuteTrace?: (address: string, chain: string) => void;
}

export function LiveOnChainInspector({
  onLoadTransactionsIntoGraph,
  onExecuteTrace,
}: LiveOnChainInspectorProps) {
  const [address, setAddress] = useState('0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045');
  const [chain, setChain] = useState<'ETH' | 'BTC' | 'TRON' | 'POLYGON'>('ETH');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveData, setLiveData] = useState<any>(null);

  const fetchLiveOnChainData = async (targetAddr?: string, targetChain?: string) => {
    const qAddr = targetAddr || address;
    const qChain = targetChain || chain;
    if (!qAddr.trim()) {
      setError('Please provide a valid blockchain wallet or contract address.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.get<any>(
        `/api/live/${encodeURIComponent(qAddr.trim())}?chain=${qChain}`
      );
      setLiveData(res.data);
    } catch (err: any) {
      console.error('Failed to fetch live on-chain data:', err);
      setError(
        err.response?.data?.detail?.message ||
          err.response?.data?.detail ||
          'Failed to query upstream live blockchain explorer API. Check network and API keys.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (preset: typeof VERIFIED_TEST_WALLETS[0]) => {
    setAddress(preset.address);
    setChain(preset.chain as any);
    fetchLiveOnChainData(preset.address, preset.chain);
  };

  const handleLoadIntoGraph = () => {
    if (!liveData || !onLoadTransactionsIntoGraph) return;

    const bc = liveData.blockchain_data || {};
    const txs: any[] = bc.recent_txs || [];
    const rootAddr = liveData.address || address;

    // Build Nodes
    const nodeMap = new Map<string, GraphNode>();
    nodeMap.set(rootAddr.toLowerCase(), {
      id: rootAddr,
      label: formatAddress(rootAddr),
      address: rootAddr,
      type: 'SUSPECT',
      balance: bc.balance_eth ?? bc.balance_btc ?? bc.trx_balance ?? 0,
      depth: 0,
      risk_score: liveData.aml_check?.is_sanctioned ? 1.0 : 0.25,
    });

    // Build Edges and Counterparty Nodes
    const edges: GraphEdge[] = [];
    txs.forEach((tx, idx) => {
      const fromAddr = tx.from || rootAddr;
      const toAddr = tx.to || 'Unknown Counterparty';

      [fromAddr, toAddr].forEach((addr) => {
        if (addr && !nodeMap.has(addr.toLowerCase())) {
          nodeMap.set(addr.toLowerCase(), {
            id: addr,
            label: formatAddress(addr),
            address: addr,
            type: addr.toLowerCase() === rootAddr.toLowerCase() ? 'SUSPECT' : 'INTERMEDIARY',
            depth: 1,
            risk_score: 0.15,
          });
        }
      });

      edges.push({
        id: `live-edge-${idx}-${tx.hash?.slice(0, 10) || idx}`,
        source: fromAddr,
        target: toAddr,
        amount: tx.value_eth ?? tx.value_btc ?? tx.value_trx ?? 0,
        token: chain,
        tx_hash: tx.hash,
        is_mixer_boundary: false,
      });
    });

    onLoadTransactionsIntoGraph(Array.from(nodeMap.values()), edges, rootAddr);
  };

  const bc = liveData?.blockchain_data || {};
  const aml = liveData?.aml_check || {};
  const txs: any[] = bc.recent_txs || [];
  const balanceDisplay =
    bc.balance_eth !== undefined
      ? `${bc.balance_eth} ETH`
      : bc.balance_btc !== undefined
      ? `${bc.balance_btc} BTC`
      : bc.trx_balance !== undefined
      ? `${bc.trx_balance} TRX (USDT: ${bc.usdt_trc20_balance ?? 0})`
      : 'N/A';

  const inrDisplay =
    bc.balance_inr !== undefined
      ? formatINR(bc.balance_inr)
      : bc.total_inr !== undefined
      ? formatINR(bc.total_inr)
      : null;

  const usdDisplay =
    bc.balance_usd !== undefined
      ? formatUSD(bc.balance_usd)
      : bc.total_usd !== undefined
      ? formatUSD(bc.total_usd)
      : null;

  return (
    <Card className="border-emerald-600/30 bg-gradient-to-b from-navy-950 to-navy-900 shadow-xl">
      <CardHeader className="border-b border-navy-800 pb-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <CardTitle className="text-base font-bold text-white flex items-center gap-2">
                <span>Live On-Chain Data & Fund Flow Inspector</span>
                <Badge variant="success" className="text-[10px] uppercase font-mono tracking-wider">
                  Real Explorer Gateway
                </Badge>
              </CardTitle>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Query live balances, confirmed block transactions, and OFAC sanctions in real-time from Etherscan V2, TronGrid, and Blockstream.
            </p>
          </div>

          {/* 1-Click Test Wallets */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] text-slate-400 font-semibold mr-1 hidden sm:inline">
              1-Click Live Test Wallets:
            </span>
            {VERIFIED_TEST_WALLETS.map((w, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectPreset(w)}
                disabled={loading}
                className="text-[11px] px-2.5 py-1 rounded border border-navy-700 bg-navy-900/90 hover:bg-emerald-950 hover:border-emerald-600 text-slate-300 hover:text-emerald-300 transition-all font-medium"
                title={`${w.name} - ${w.role}`}
              >
                {w.name.split(' ')[0]} ({w.chain})
              </button>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-4 sm:p-5 space-y-5">
        {/* Search Input Bar */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
          <div className="md:col-span-7 space-y-1">
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-300">
              Target Wallet Address / Smart Contract
            </label>
            <div className="relative">
              <Input
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="0x... or 1A1z... or TR7N..."
                className="font-mono text-xs pr-10"
              />
              {address && (
                <button
                  type="button"
                  onClick={() => setAddress('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          <div className="md:col-span-2 space-y-1">
            <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-300">
              Chain
            </label>
            <select
              value={chain}
              onChange={(e) => setChain(e.target.value as any)}
              className="w-full h-10 px-3 rounded-lg border border-navy-700 bg-navy-900 text-slate-200 text-xs font-medium focus:ring-1 focus:ring-emerald-500 outline-none"
            >
              <option value="ETH">Ethereum (ETH)</option>
              <option value="TRON">TRON (TRX / USDT)</option>
              <option value="BTC">Bitcoin (BTC)</option>
              <option value="POLYGON">Polygon (POL)</option>
            </select>
          </div>

          <div className="md:col-span-3 flex gap-2">
            <Button
              variant="primary"
              onClick={() => fetchLiveOnChainData()}
              isLoading={loading}
              className="w-full text-xs font-semibold flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-500"
            >
              <Search className="h-3.5 w-3.5" />
              FETCH LIVE DATA
            </Button>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Live Data Summary Cards */}
        {liveData && (
          <div className="space-y-4 animate-fade-in">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {/* Live Balance Card */}
              <div className="p-3.5 rounded-lg bg-navy-900 border border-navy-800">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Live On-Chain Balance
                </span>
                <div className="text-lg font-bold font-mono text-emerald-400 mt-0.5 truncate">
                  {balanceDisplay}
                </div>
                {inrDisplay && (
                  <div className="text-xs font-medium text-slate-300 mt-1 flex items-center gap-1">
                    <span>? {inrDisplay}</span>
                    <span className="text-[10px] text-slate-400 font-mono">({usdDisplay})</span>
                  </div>
                )}
                <div className="text-[10px] text-emerald-400/80 mt-1 flex items-center gap-1">
                  <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span>Spot rate via CoinGecko</span>
                </div>
              </div>

              {/* Transactions Discovered */}
              <div className="p-3.5 rounded-lg bg-navy-900 border border-navy-800">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Confirmed Transactions
                </span>
                <div className="text-lg font-bold font-mono text-white mt-0.5">
                  {txs.length} Recorded
                </div>
                <div className="text-xs text-slate-400 mt-1 truncate">
                  Counterparties: <span className="text-blue-400 font-semibold font-mono">{bc.counterparties?.length || 0} Wallets</span>
                </div>
                {bc.explorer_url && (
                  <a
                    href={bc.explorer_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[10px] text-blue-400 hover:text-blue-300 mt-1 inline-flex items-center gap-1 font-mono"
                  >
                    <span>View on Official Explorer</span>
                    <ExternalLink className="h-2.5 w-2.5" />
                  </a>
                )}
              </div>

              {/* AML / Sanctions Screening */}
              <div className="p-3.5 rounded-lg bg-navy-900 border border-navy-800">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  US OFAC SDN Screening
                </span>
                <div className="mt-1 flex items-center gap-2">
                  {aml.is_sanctioned ? (
                    <Badge variant="danger" className="text-xs py-0.5">
                      <ShieldAlert className="h-3 w-3 mr-1" />
                      SANCTION HIT
                    </Badge>
                  ) : (
                    <Badge variant="success" className="text-xs py-0.5">
                      <ShieldCheck className="h-3 w-3 mr-1" />
                      CLEAR / NO MATCH
                    </Badge>
                  )}
                </div>
                {aml.provenance_hash && (
                  <div className="text-[10px] text-slate-400 mt-1.5 font-mono truncate" title={`SHA-256 Provenance: ${aml.provenance_hash}`}>
                    SHA: {aml.provenance_hash.slice(0, 16)}...
                  </div>
                )}
              </div>

              {/* Load to Graph Action Card */}
              <div className="p-3.5 rounded-lg bg-gradient-to-br from-blue-950/60 to-navy-900 border border-blue-800/60 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-300 block">
                    Fund Flow Action
                  </span>
                  <div className="text-xs text-slate-300 mt-1">
                    Stream live transactions into interactive Cytoscape canvas.
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleLoadIntoGraph}
                    disabled={txs.length === 0}
                    className="w-full text-xs font-semibold py-1.5 bg-blue-600 hover:bg-blue-500 gap-1.5"
                  >
                    <GitFork className="h-3.5 w-3.5" />
                    Load Into Graph
                  </Button>
                  {onExecuteTrace && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onExecuteTrace(address, chain)}
                      className="text-xs py-1.5 border-emerald-600/60 text-emerald-300 hover:bg-emerald-950"
                      title="Execute deep multi-hop trace on this wallet"
                    >
                      Deep Trace
                    </Button>
                  )}
                </div>
              </div>
            </div>

            {/* Confirmed Transactions Table */}
            {txs.length > 0 ? (
              <div className="rounded-lg border border-navy-800 overflow-hidden">
                <div className="bg-navy-900/90 px-4 py-2.5 border-b border-navy-800 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-emerald-400" />
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Latest Confirmed On-Chain Transactions ({txs.length})
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">
                    Source: {bc.source || '?? LIVE'}
                  </span>
                </div>
                <div className="overflow-x-auto max-h-72">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-navy-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-navy-800 text-[11px]">
                      <tr>
                        <th className="py-2 px-3">Tx Hash</th>
                        <th className="py-2 px-3">From</th>
                        <th className="py-2 px-3">To</th>
                        <th className="py-2 px-3">Value</th>
                        <th className="py-2 px-3">Status / Age</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-navy-800 font-mono text-slate-300 text-[11px]">
                      {txs.slice(0, 10).map((tx, idx) => {
                        const hash = tx.hash || '';
                        const val = tx.value_eth ?? tx.value_btc ?? tx.value_trx ?? 0;
                        const explorerBase =
                          chain === 'ETH'
                            ? 'https://etherscan.io/tx/'
                            : chain === 'BTC'
                            ? 'https://blockstream.info/tx/'
                            : chain === 'TRON'
                            ? 'https://tronscan.org/#/transaction/'
                            : 'https://polygonscan.com/tx/';

                        return (
                          <tr key={idx} className="hover:bg-navy-800/50 transition-colors">
                            <td className="py-2 px-3">
                              <div className="flex items-center gap-1.5">
                                <a
                                  href={`${explorerBase}${hash}`}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="text-blue-400 hover:text-blue-300 underline font-mono flex items-center gap-1"
                                  title={hash}
                                >
                                  <span>{formatAddress(hash, 6)}</span>
                                  <ExternalLink className="h-2.5 w-2.5 shrink-0" />
                                </a>
                              </div>
                            </td>
                            <td className="py-2 px-3">
                              <AddressBadge address={tx.from || address} chain={chain} />
                            </td>
                            <td className="py-2 px-3">
                              <AddressBadge address={tx.to || 'Contract'} chain={chain} />
                            </td>
                            <td className="py-2 px-3 font-semibold text-emerald-400">
                              {formatCrypto(val, chain)}
                            </td>
                            <td className="py-2 px-3 text-slate-400">
                              <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950/70 border border-emerald-800 text-emerald-300">
                                CONFIRMED
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-navy-900/60 border border-navy-800 text-center text-xs text-slate-400">
                No recent transactions returned for this address on {chain}.
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
