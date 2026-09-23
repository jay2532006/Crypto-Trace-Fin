'use client';

import React, { useState } from 'react';
import {
  ShieldAlert,
  Network,
  Shuffle,
  GitFork,
  Clock,
  Percent,
  CheckCircle2,
  AlertTriangle,
  Play,
  FileText,
  HelpCircle,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ConfidencePill } from '@/components/forensic/ConfidencePill';
import { UncertaintyBanner } from '@/components/forensic/UncertaintyBanner';
import { formatCrypto } from '@/lib/utils';

export default function TypologiesPage() {
  // Live Simulator state for MULE_NETWORK testing
  const [simHops, setSimHops] = useState(4);
  const [simTimeMinutes, setSimTimeMinutes] = useState(25);
  const [simTolerancePct, setSimTolerancePct] = useState(8);
  const [simAmount, setSimAmount] = useState(50000);

  // Evaluate Mule Rule
  const isMuleDetected = simHops >= 3 && simTimeMinutes <= 60 && simTolerancePct <= 15;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-navy-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Cryptocurrency Laundering Typologies
            </h1>
            <Badge variant="navy">I4C / NCRP Heuristics</Badge>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Standardised behavioral pattern rules derived from Indian cybercrime syndicate modus operandi.
          </p>
        </div>
      </div>

      {/* Primary Innovation Alert */}
      <div className="p-4 rounded-xl border border-blue-500/40 bg-gradient-to-r from-blue-950/40 via-navy-900 to-navy-950 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <Network className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white text-sm">
                Rule ID: MULE_NETWORK (Version 1.0)
              </span>
              <Badge variant="success">Active in Production</Badge>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Detects synchronized single-in / single-out layering networks across intermediary mules.
              Enforces a strict confidence ceiling of <strong className="text-amber-400">MEDIUM</strong> to
              prevent overclaiming heuristic correlations in formal affidavits.
            </p>
          </div>
        </div>
        <ConfidencePill level="MEDIUM" label="Capped at Medium" />
      </div>

      {/* Grid of Typology Rule Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: MULE_NETWORK */}
        <Card className="border-navy-700/80">
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Network className="h-5 w-5 text-purple-400" />
                <CardTitle className="text-sm">Mule Network Peeling Chain</CardTitle>
              </div>
              <Badge variant="navy">Domestic Syndicate</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-4 text-xs">
            <p className="text-slate-300">
              Identifies organized ring structures where illicit funds are quickly tunneled through
              purchased or rented third-party accounts before reaching domestic KYC off-ramps.
            </p>

            <div className="grid grid-cols-3 gap-2 py-2 border-y border-navy-800">
              <div className="p-2 rounded bg-navy-900">
                <span className="text-[10px] text-slate-500 block uppercase">Min Wallets</span>
                <span className="text-sm font-bold font-mono text-white">≥ 3 Hops</span>
              </div>
              <div className="p-2 rounded bg-navy-900">
                <span className="text-[10px] text-slate-500 block uppercase">Max Hop Delay</span>
                <span className="text-sm font-bold font-mono text-emerald-400">&lt; 60 Mins</span>
              </div>
              <div className="p-2 rounded bg-navy-900">
                <span className="text-[10px] text-slate-500 block uppercase">Fee Tolerance</span>
                <span className="text-sm font-bold font-mono text-blue-400">± 15%</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-800/60 text-[11px] text-amber-200">
              <div className="flex items-center gap-1.5 font-semibold mb-1">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                Mandatory Uncertainty Disclosure (PRD FR-008)
              </div>
              Intermediary addresses are behavioral correlations. Investigators must confirm beneficial
              ownership through Section 91 notices prior to initiating bank account freeze requests.
            </div>
          </CardContent>
        </Card>

        {/* Card 2: MIXER_BOUNDARY */}
        <Card className="border-navy-700/80">
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shuffle className="h-5 w-5 text-amber-400" />
                <CardTitle className="text-sm">Mixer Boundary Barrier</CardTitle>
              </div>
              <Badge variant="warning">Obfuscation Protocol</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-4 text-xs">
            <p className="text-slate-300">
              Flags interactions with non-custodial privacy pools (Tornado Cash, Railgun, Cryptonote mixers)
              where unspent UTXO or zero-knowledge cryptographic mixing breaks ledger lineage.
            </p>

            <div className="grid grid-cols-2 gap-2 py-2 border-y border-navy-800">
              <div className="p-2 rounded bg-navy-900">
                <span className="text-[10px] text-slate-500 block uppercase">Attribution Impact</span>
                <span className="text-xs font-bold text-red-400">Hard Confidence Cap (LOW)</span>
              </div>
              <div className="p-2 rounded bg-navy-900">
                <span className="text-[10px] text-slate-500 block uppercase">Graph Representation</span>
                <span className="text-xs font-bold text-amber-400">Dashed Orange Edge</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-red-950/30 border border-red-800/60 text-[11px] text-red-200">
              <div className="flex items-center gap-1.5 font-semibold mb-1">
                <ShieldAlert className="h-3.5 w-3.5 text-red-400 shrink-0" />
                Judicial Admissibility Notice
              </div>
              Funds exiting a mixer pool cannot be proven beyond reasonable doubt to belong to the suspect
              seed without auxiliary off-chain telemetry, timestamp proximity, or exchange deposit match.
            </div>
          </CardContent>
        </Card>

        {/* Card 3: PEELING_CHAIN */}
        <Card className="border-navy-700/80">
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <GitFork className="h-5 w-5 text-blue-400" />
                <CardTitle className="text-sm">Peeling Chain Dispersion</CardTitle>
              </div>
              <Badge variant="navy">UTXO / Balance Shaving</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-4 text-xs">
            <p className="text-slate-300">
              A sequence of transactions where a large sum is repeatedly split: one small output goes to an
              intermediate cashout wallet or merchant, while the vast majority continues down the trunk.
            </p>
            <div className="space-y-1.5 text-slate-400">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-blue-400" />
                <span>Trunk preservation ratio: &gt; 80% per hop</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-blue-400" />
                <span>Repeated 3+ times to exhaust tracking tools</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-blue-400" />
                <span>Typical in Ransomware & Large Scam extractions</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Card 4: RAPID_DISPERSAL */}
        <Card className="border-navy-700/80">
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-emerald-400" />
                <CardTitle className="text-sm">High-Velocity Dispersal</CardTitle>
              </div>
              <Badge variant="success">Time-Critical</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-4 text-xs">
            <p className="text-slate-300">
              Fan-out dispersal of stolen tokens across multiple liquidity pools or decentralized bridges
              within 15 minutes of the initial exploit, aimed at front-running law enforcement freeze actions.
            </p>
            <div className="space-y-1.5 text-slate-400">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Velocity threshold: &lt; 900 seconds</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Multi-bridge fan-out (Stargate, Across, Hop)</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Triggers highest priority Section 91 Emergency Notice</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Interactive Typology Evaluator / Simulator */}
      <Card className="border-blue-500/30">
        <CardHeader className="bg-navy-900/60 border-b border-navy-800 pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-blue-400" />
              <CardTitle className="text-sm">Interactive Mule Network Evaluator</CardTitle>
            </div>
            <span className="text-xs text-slate-400">Simulate parameters to verify rule boundaries</span>
          </div>
        </CardHeader>
        <CardContent className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Input 1: Hop count */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400 font-semibold uppercase">Sequential Hops</span>
                <span className="font-mono text-white font-bold">{simHops} Wallets</span>
              </div>
              <input
                type="range"
                min="1"
                max="8"
                value={simHops}
                onChange={(e) => setSimHops(Number(e.target.value))}
                className="w-full accent-blue-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-slate-500">Threshold: ≥ 3 wallets</span>
            </div>

            {/* Input 2: Time Difference */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400 font-semibold uppercase">Hop Delay</span>
                <span className="font-mono text-white font-bold">{simTimeMinutes} Mins</span>
              </div>
              <input
                type="range"
                min="5"
                max="120"
                step="5"
                value={simTimeMinutes}
                onChange={(e) => setSimTimeMinutes(Number(e.target.value))}
                className="w-full accent-emerald-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-slate-500">Threshold: &lt; 60 minutes</span>
            </div>

            {/* Input 3: Value Conservation Tolerance */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400 font-semibold uppercase">Fee Loss Tolerance</span>
                <span className="font-mono text-white font-bold">±{simTolerancePct}%</span>
              </div>
              <input
                type="range"
                min="1"
                max="30"
                value={simTolerancePct}
                onChange={(e) => setSimTolerancePct(Number(e.target.value))}
                className="w-full accent-purple-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-slate-500">Threshold: ≤ 15% fee variance</span>
            </div>

            {/* Result Box */}
            <div className="flex flex-col justify-center p-3 rounded-lg border bg-navy-950/80">
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                Evaluation Output
              </span>
              <div className="mt-1 flex items-center justify-between">
                {isMuleDetected ? (
                  <span className="text-sm font-bold text-purple-400 flex items-center gap-1.5">
                    <CheckCircle2 className="h-4 w-4 text-purple-400" />
                    MULE_NETWORK
                  </span>
                ) : (
                  <span className="text-sm font-bold text-slate-500 flex items-center gap-1.5">
                    <AlertTriangle className="h-4 w-4 text-slate-500" />
                    Negative
                  </span>
                )}
                {isMuleDetected && <ConfidencePill level="MEDIUM" label="Capped: MEDIUM" />}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
