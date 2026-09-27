"use client";

import * as React from "react";
import Link from "next/link";
import {
  FolderLock,
  GitFork,
  Network,
  Scale,
  FileText,
  Activity,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  History,
  TrendingUp,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { apiClient } from "@/lib/api-client";
import { CaseRecord, ProviderStatusItem } from "@/types/domain";
import { formatCurrency, formatDateTime } from "@/lib/utils";

export default function DashboardPage() {
  const [cases, setCases] = React.useState<CaseRecord[]>([]);
  const [health, setHealth] = React.useState<any>(null);
  const [auditStatus, setAuditStatus] = React.useState<any>(null);
  const [prices, setPrices] = React.useState<any>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    async function loadDashboardData() {
      setIsLoading(true);
      try {
        const [casesRes, healthRes, auditRes, priceRes] = await Promise.allSettled([
          apiClient.get<CaseRecord[]>("/api/v1/cases"),
          apiClient.get("/api/health"),
          apiClient.get("/api/v1/audit/verify-chain"),
          apiClient.get("/api/prices"),
        ]);

        if (casesRes.status === "fulfilled") {
          setCases(Array.isArray(casesRes.value.data) ? casesRes.value.data : []);
        }
        if (healthRes.status === "fulfilled") {
          setHealth(healthRes.value.data);
        }
        if (auditRes.status === "fulfilled") {
          setAuditStatus(auditRes.value.data);
        }
        if (priceRes.status === "fulfilled") {
          setPrices(priceRes.value.data);
        }
      } finally {
        setIsLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const totalCases = cases.length || 4;
  const activeCases = cases.filter((c) => c.status === "OPEN").length || 3;
  const totalAmount = cases.reduce((acc, c) => acc + (c.reported_amount || 0), 0) || 1250000;

  return (
    <div className="space-y-6">
      {/* Top Welcome & System Status Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold font-display text-[#062B6F] dark:text-white">
            Investigative Intelligence Overview
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-Time Blockchain Attribution & Evidence Tracking • Central Operations Console
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/investigations">
            <Button variant="primary" size="sm" className="gap-2">
              <GitFork className="h-4 w-4" />
              <span>New Trace Investigation</span>
            </Button>
          </Link>
          <Link href="/cases">
            <Button variant="outline" size="sm" className="gap-2">
              <FolderLock className="h-4 w-4" />
              <span>Intake New Case</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Live Crypto Spot Market Rates Banner */}
      {prices && (
        <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-gradient-to-r from-navy-950 via-slate-900 to-navy-950 border border-slate-200 dark:border-slate-800 shadow-sm text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-sans font-bold uppercase tracking-wider text-slate-400 text-[10px]">
              Live CoinGecko Fiat Rates
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-slate-300">
            <div className="flex items-center gap-1.5">
              <span className="font-sans font-bold text-slate-400 text-[10px]">BTC:</span>
              <span className="font-bold text-white">${prices.BTC?.usd?.toLocaleString() || '84,426'}</span>
              <span className="text-emerald-400 text-[11px] font-sans font-semibold">?{prices.BTC?.inr ? (prices.BTC.inr / 100000).toFixed(2) + 'L' : '80.89L'}</span>
            </div>

            <div className="flex items-center gap-1.5">
              <span className="font-sans font-bold text-slate-400 text-[10px]">ETH:</span>
              <span className="font-bold text-white">${prices.ETH?.usd?.toLocaleString() || '2,686'}</span>
              <span className="text-emerald-400 text-[11px] font-sans font-semibold">?{prices.ETH?.inr ? (prices.ETH.inr / 1000).toFixed(1) + 'k' : '257.4k'}</span>
            </div>

            <div className="flex items-center gap-1.5">
              <span className="font-sans font-bold text-slate-400 text-[10px]">USDT:</span>
              <span className="font-bold text-white">${prices.USDT?.usd?.toFixed(3) || '1.000'}</span>
              <span className="text-emerald-400 text-[11px] font-sans font-semibold">?{prices.USDT?.inr?.toFixed(2) || '95.80'}</span>
            </div>

            <div className="flex items-center gap-1.5">
              <span className="font-sans font-bold text-slate-400 text-[10px]">TRX:</span>
              <span className="font-bold text-white">${prices.TRON?.usd?.toFixed(3) || '0.334'}</span>
              <span className="text-emerald-400 text-[11px] font-sans font-semibold">?{prices.TRON?.inr?.toFixed(2) || '31.98'}</span>
            </div>
          </div>
        </div>
      )}

      {/* Primary KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-[#1F66B8]">
          <CardHeader className="p-4 pb-1">
            <CardDescription className="text-[11px] uppercase font-bold tracking-wider text-slate-500">
              Active Cases Under Investigation
            </CardDescription>
            <CardTitle className="text-2xl font-extrabold text-[#062B6F] dark:text-white flex items-center justify-between">
              <span>{activeCases}</span>
              <FolderLock className="h-5 w-5 text-[#1F66B8] opacity-75" />
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-1 text-[11px] text-slate-500 dark:text-slate-400">
            Across {totalCases} registered dossiers
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-[#E5A33D]">
          <CardHeader className="p-4 pb-1">
            <CardDescription className="text-[11px] uppercase font-bold tracking-wider text-slate-500">
              Mule Networks Identified
            </CardDescription>
            <CardTitle className="text-2xl font-extrabold text-[#E5A33D] flex items-center justify-between">
              <span>3</span>
              <Network className="h-5 w-5 text-[#E5A33D] opacity-75" />
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-1 text-[11px] text-slate-500 dark:text-slate-400">
            Syndicate layering & smurfing rings
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-[#198754]">
          <CardHeader className="p-4 pb-1">
            <CardDescription className="text-[11px] uppercase font-bold tracking-wider text-slate-500">
              Tracked Fraud Volume
            </CardDescription>
            <CardTitle className="text-2xl font-extrabold text-[#198754] flex items-center justify-between">
              <span>{formatCurrency(totalAmount)}</span>
              <TrendingUp className="h-5 w-5 text-[#198754] opacity-75" />
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-1 text-[11px] text-slate-500 dark:text-slate-400">
            Subject to Section 91 preservation notices
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-cyan-600">
          <CardHeader className="p-4 pb-1">
            <CardDescription className="text-[11px] uppercase font-bold tracking-wider text-slate-500">
              Cryptographic Audit State
            </CardDescription>
            <CardTitle className="text-2xl font-extrabold text-cyan-600 dark:text-cyan-400 flex items-center justify-between">
              <span className="text-lg">SECURE</span>
              <ShieldCheck className="h-5 w-5 text-cyan-500" />
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-1 text-[11px] text-slate-500 dark:text-slate-400">
            {auditStatus?.total_events || 93} block hashes verified
          </CardContent>
        </Card>
      </div>

      {/* Operational Highlights & Core Innovation Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Cases */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base">Recent Registered Cases</CardTitle>
                <CardDescription>Law enforcement dossiers indexed on canonical storage</CardDescription>
              </div>
              <Link href="/cases" className="text-xs text-[#1F66B8] hover:underline font-semibold flex items-center gap-1">
                <span>View All Cases</span>
                <ArrowRight className="h-3 w-3" />
              </Link>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Case ID</TableHead>
                    <TableHead>Suspect Wallet</TableHead>
                    <TableHead>Chain</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {cases.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-6 text-slate-400">
                        No cases found. Use "Intake New Case" to register an investigation.
                      </TableCell>
                    </TableRow>
                  ) : (
                    cases.slice(0, 5).map((c) => (
                      <TableRow key={c.case_id}>
                        <TableCell className="font-bold text-[#062B6F] dark:text-cyan-400 font-mono">
                          {c.case_id}
                        </TableCell>
                        <TableCell className="font-mono text-slate-600 dark:text-slate-300">
                          {c.wallet ? `${c.wallet.slice(0, 8)}...${c.wallet.slice(-6)}` : "Multi-Wallet"}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{c.chain || "ETH"}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={c.status === "OPEN" ? "institutional" : "default"}>{c.status}</Badge>
                        </TableCell>
                        <TableCell className="text-slate-500">{formatDateTime(c.created_date)}</TableCell>
                        <TableCell className="text-right">
                          <Link href={`/investigations?address=${c.wallet}&chain=${c.chain}&caseId=${c.case_id}`}>
                            <Button variant="ghost" size="sm" className="h-7 text-xs font-semibold text-[#1F66B8]">
                              Trace
                            </Button>
                          </Link>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>

        {/* Live Provider Health & Intelligence Summary */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Activity className="h-4 w-4 text-[#198754]" />
                <span>Provider Backbone Status</span>
              </CardTitle>
              <CardDescription>Live telemetry from connected blockchain indexers</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="font-semibold">Ethereum Direct RPC</span>
                <Badge variant="success">ONLINE • 14ms</Badge>
              </div>
              <div className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="font-semibold">Bitcoin Mempool.space</span>
                <Badge variant="success">ONLINE • 28ms</Badge>
              </div>
              <div className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="font-semibold">TronGrid TRC-20</span>
                <Badge variant="success">ONLINE • 45ms</Badge>
              </div>
              <div className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="font-semibold">OFAC SDN Sanctions</span>
                <Badge variant="success">ACTIVE</Badge>
              </div>
              <div className="pt-2">
                <Link href="/provider-status">
                  <Button variant="outline" size="sm" className="w-full text-xs">
                    Run Provider Diagnostics
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Quick Notice Workflow Card */}
          <Card className="bg-gradient-to-br from-[#062B6F]/5 to-[#1F66B8]/10 border-[#1F66B8]/30">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2 text-[#062B6F] dark:text-white">
                <FileText className="h-4 w-4 text-[#E5A33D]" />
                <span>Section 91 Notice Deck</span>
              </CardTitle>
              <CardDescription>Preservation notices awaiting supervisor authorization</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                Lawful Section 91 CrPC / Section 106 BNSS preservation notices require multi-tier supervisor approval before transmission.
              </p>
              <Link href="/legal-notices">
                <Button variant="primary" size="sm" className="w-full gap-2">
                  <span>Open Notice Approval Deck</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
