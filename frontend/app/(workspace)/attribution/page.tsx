'use client';

import React, { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  Building2,
  Scale,
  ShieldCheck,
  ShieldAlert,
  Sliders,
  CheckCircle2,
  FileText,
  Mail,
  ExternalLink,
  Info,
  ChevronRight,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ConfidencePill } from '@/components/forensic/ConfidencePill';
import { UncertaintyBanner } from '@/components/forensic/UncertaintyBanner';

interface VaspRegistryEntry {
  key: string;
  name: string;
  vasp_id: string;
  legal_name: string;
  fiu_status: 'REGISTERED' | 'UNREGISTERED';
  jurisdiction: 'INDIA' | 'GLOBAL';
  nodal_email: string;
  portal_url: string;
}

const REGISTERED_VASPS: VaspRegistryEntry[] = [
  {
    key: 'WAZIRX',
    name: 'WazirX',
    vasp_id: 'VASP-IND-001',
    legal_name: 'Zanmai Labs Pvt Ltd',
    fiu_status: 'REGISTERED',
    jurisdiction: 'INDIA',
    nodal_email: 'nodal@wazirx.com',
    portal_url: 'https://wazirx.com/law-enforcement',
  },
  {
    key: 'COINDCX',
    name: 'CoinDCX',
    vasp_id: 'VASP-IND-002',
    legal_name: 'Neblio Technologies Pvt Ltd',
    fiu_status: 'REGISTERED',
    jurisdiction: 'INDIA',
    nodal_email: 'compliance@coindcx.com',
    portal_url: 'https://coindcx.com/compliance',
  },
  {
    key: 'ZEBPAY',
    name: 'ZebPay',
    vasp_id: 'VASP-IND-003',
    legal_name: 'Awlencan Innovations India Ltd',
    fiu_status: 'REGISTERED',
    jurisdiction: 'INDIA',
    nodal_email: 'nodal@zebpay.com',
    portal_url: 'https://zebpay.com/in/legal',
  },
  {
    key: 'BINANCE',
    name: 'Binance',
    vasp_id: 'VASP-GLOBAL-001',
    legal_name: 'Binance Holdings Ltd',
    fiu_status: 'REGISTERED',
    jurisdiction: 'GLOBAL',
    nodal_email: 'lea-india@binance.com',
    portal_url: 'https://kodexglobal.com',
  },
];

function AttributionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialVasp = searchParams?.get('vasp') || 'WAZIRX';

  const [selectedVaspKey, setSelectedVaspKey] = useState<string>(initialVasp.toUpperCase());

  // Interactive Scoring Simulator States
  const [hopCount, setHopCount] = useState<number>(1);
  const [isExactMatch, setIsExactMatch] = useState<boolean>(true);
  const [mixerDetected, setMixerDetected] = useState<boolean>(false);
  const [recentDays, setRecentDays] = useState<number>(2);
  const [dataCompleteness, setDataCompleteness] = useState<number>(95);

  const selectedVasp =
    REGISTERED_VASPS.find((v) => v.key === selectedVaspKey) || REGISTERED_VASPS[0];

  // Execute 6-Step Scoring sequence identically to backend AdaptiveVASPScorer
  // Step 1: Base
  const baseScore = 50.0;
  // Step 2: Single hop override
  const isSingleHop = hopCount === 1;
  const singleHopBoost = isSingleHop ? 20.0 : 0.0;
  // Step 3a: Jurisdiction
  const isIndian = selectedVasp.jurisdiction === 'INDIA';
  const isFiuReg = selectedVasp.fiu_status === 'REGISTERED';
  const jurisdictionVal = isIndian && isFiuReg ? 15.0 : isFiuReg ? 8.0 : 0.0;
  // Step 3b: Hop Decay
  const hopPenalty = Math.max(0.0, (hopCount - 1) * 8.0);
  // Step 3c: Hot Wallet Pattern Match
  let matchStrength = isExactMatch ? 35.0 : 15.0;
  // Step 3d: Mixer Penalty
  const mixerWeight = mixerDetected ? -30.0 : 0.0;
  // Step 3e: Recent Activity
  const recentBoost = recentDays <= 7 ? 10.0 : 0.0;
  // Step 4: Conflict Resolution
  let conflictPenalty = 0.0;
  if (mixerDetected && matchStrength > 20.0) {
    matchStrength = 10.0;
    conflictPenalty = -10.0;
  }
  // Step 5 & 6: Clamp & Renormalize
  const rawScore =
    baseScore +
    singleHopBoost +
    jurisdictionVal -
    hopPenalty +
    matchStrength +
    mixerWeight +
    recentBoost +
    conflictPenalty;

  const clampedScore = Math.max(5, Math.min(95, Math.round(rawScore)));

  // Label & Confidence Band
  let labelType: 'VERIFIED' | 'INFERRED' | 'UNRESOLVED' = 'UNRESOLVED';
  let confidenceBand: 'HIGH' | 'MEDIUM' | 'LOW' = 'LOW';

  if (isFiuReg && isExactMatch && !mixerDetected && hopCount <= 2) {
    labelType = 'VERIFIED';
    confidenceBand = 'HIGH';
  } else if (clampedScore >= 60 && !mixerDetected) {
    labelType = 'INFERRED';
    confidenceBand = hopCount > 1 ? 'MEDIUM' : 'HIGH';
  } else {
    labelType = 'UNRESOLVED';
    confidenceBand = 'LOW';
  }

  // Data completeness cap
  if (dataCompleteness < 70 && confidenceBand === 'HIGH') {
    confidenceBand = 'MEDIUM';
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-navy-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Adaptive VASP Attribution Engine
            </h1>
            <Badge variant="navy">Algorithmic Transparency</Badge>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Dynamic 6-step multi-factor attribution sequence mapping on-chain clusters to registered reporting entities.
          </p>
        </div>

        {/* Selected VASP Switcher */}
        <div className="flex items-center gap-2">
          {REGISTERED_VASPS.map((vasp) => (
            <button
              key={vasp.key}
              onClick={() => setSelectedVaspKey(vasp.key)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
                selectedVaspKey === vasp.key
                  ? 'bg-blue-600 border-blue-400 text-white shadow-md'
                  : 'bg-navy-900 border-navy-700 text-slate-300 hover:bg-navy-800'
              }`}
            >
              {vasp.name}
            </button>
          ))}
        </div>
      </div>

      {/* VASP Profile Overview Card */}
      <Card className="border-blue-500/30">
        <CardContent className="p-5">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2.5">
                <Building2 className="h-6 w-6 text-blue-400" />
                <h2 className="text-xl font-bold text-white">{selectedVasp.name}</h2>
                <Badge variant={selectedVasp.fiu_status === 'REGISTERED' ? 'success' : 'danger'}>
                  FIU-IND {selectedVasp.fiu_status}
                </Badge>
                <Badge variant="navy">{selectedVasp.jurisdiction}</Badge>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Legal Entity: <span className="text-slate-200">{selectedVasp.legal_name}</span> | ID:{' '}
                <span className="text-blue-300">{selectedVasp.vasp_id}</span>
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="primary"
                onClick={() =>
                  router.push(
                    `/legal-notices?vasp=${encodeURIComponent(selectedVasp.name)}`
                  )
                }
                className="text-xs flex items-center gap-1.5"
              >
                <FileText className="h-3.5 w-3.5" />
                Draft Section 91 Notice
              </Button>
              <a
                href={selectedVasp.portal_url}
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg bg-navy-800 border border-navy-700 text-slate-300 hover:text-white transition-colors"
                title="Open Law Enforcement Portal"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Simulator & Live Score Deck */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Scenario Controls */}
        <div className="lg:col-span-5 space-y-4">
          <Card>
            <CardHeader className="border-b border-navy-800 pb-3">
              <div className="flex items-center gap-2">
                <Sliders className="h-4 w-4 text-blue-400" />
                <CardTitle className="text-sm">Attribution Scenario Controls</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-4 space-y-4 text-xs">
              {/* Hop Count */}
              <div className="space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400 font-semibold uppercase">Hop Distance</span>
                  <span className="font-mono text-white font-bold">{hopCount} Hop(s)</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={hopCount}
                  onChange={(e) => setHopCount(Number(e.target.value))}
                  className="w-full accent-blue-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">
                  {hopCount === 1
                    ? 'Direct 1-Hop: Activates Single-Hop Structural Override (+20)'
                    : `Multi-hop path: Incurs hop decay penalty of -${hopPenalty} pts`}
                </span>
              </div>

              {/* Exact Hot Wallet Match Toggle */}
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-navy-900 border border-navy-800">
                <div>
                  <span className="text-slate-200 font-semibold block">Exact Hot Wallet Match</span>
                  <span className="text-[10px] text-slate-400">
                    Matches verified cold/hot cluster signature
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={isExactMatch}
                  onChange={(e) => setIsExactMatch(e.target.checked)}
                  className="h-4 w-4 accent-blue-500 rounded cursor-pointer"
                />
              </div>

              {/* Mixer Interaction Toggle */}
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-navy-900 border border-navy-800">
                <div>
                  <span className="text-slate-200 font-semibold block">Mixer Interaction</span>
                  <span className="text-[10px] text-slate-400">
                    Privacy pool boundary traversed along path
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={mixerDetected}
                  onChange={(e) => setMixerDetected(e.target.checked)}
                  className="h-4 w-4 accent-amber-500 rounded cursor-pointer"
                />
              </div>

              {/* Recent Activity Days */}
              <div className="space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400 font-semibold uppercase">Cluster Recency</span>
                  <span className="font-mono text-white font-bold">{recentDays} Day(s) Ago</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="30"
                  value={recentDays}
                  onChange={(e) => setRecentDays(Number(e.target.value))}
                  className="w-full accent-blue-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">
                  {recentDays <= 7 ? 'Recent (< 7d): +10 boost applied' : 'Older than 7d: No recency boost'}
                </span>
              </div>

              {/* Data Completeness */}
              <div className="space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400 font-semibold uppercase">Data Completeness</span>
                  <span className="font-mono text-white font-bold">{dataCompleteness}%</span>
                </div>
                <input
                  type="range"
                  min="40"
                  max="100"
                  value={dataCompleteness}
                  onChange={(e) => setDataCompleteness(Number(e.target.value))}
                  className="w-full accent-emerald-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">
                  {dataCompleteness < 70
                    ? 'Below 70%: Enforces mandatory confidence ceiling at MEDIUM'
                    : 'Reliable forensic sample'}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Live Mathematical Output & 6-Step Breakdown */}
        <div className="lg:col-span-7 space-y-4">
          {/* Top Score Banner */}
          <div className="grid grid-cols-3 gap-4">
            <Card className="border-blue-500/40 bg-gradient-to-b from-navy-900 to-navy-950">
              <CardContent className="p-4 text-center">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Attribution Score
                </span>
                <div className="text-3xl font-extrabold font-mono text-blue-400 mt-1">
                  {clampedScore}
                  <span className="text-sm text-slate-500 font-sans ml-1">/ 100</span>
                </div>
              </CardContent>
            </Card>

            <Card className="border-blue-500/40 bg-gradient-to-b from-navy-900 to-navy-950">
              <CardContent className="p-4 text-center">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Confidence Band
                </span>
                <div className="mt-2 flex justify-center">
                  <ConfidencePill level={confidenceBand} />
                </div>
              </CardContent>
            </Card>

            <Card className="border-blue-500/40 bg-gradient-to-b from-navy-900 to-navy-950">
              <CardContent className="p-4 text-center">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Judicial Classification
                </span>
                <div className="mt-2">
                  <Badge
                    variant={
                      labelType === 'VERIFIED'
                        ? 'success'
                        : labelType === 'INFERRED'
                        ? 'warning'
                        : 'default'
                    }
                  >
                    {labelType}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {mixerDetected && (
            <UncertaintyBanner
              level="HIGH"
              title="Mixer Penalty Active"
              description="A mixer boundary penalty (-30) was applied. Attribution confidence is clamped and conflict resolution suppresses exact cluster matches."
            />
          )}

          {/* 6-Step Walkthrough Table */}
          <Card>
            <CardHeader className="border-b border-navy-800 pb-3">
              <CardTitle className="text-sm font-bold tracking-wide">
                Deterministic 6-Step Calculation Sequence
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0 overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-navy-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-navy-800">
                  <tr>
                    <th className="py-2.5 px-4">Step</th>
                    <th className="py-2.5 px-4">Evaluator Rule</th>
                    <th className="py-2.5 px-4 text-right">Contribution</th>
                    <th className="py-2.5 px-4">Reasoning</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-navy-800 text-slate-300">
                  <tr>
                    <td className="py-2.5 px-4 font-mono font-bold text-blue-400">Step 1</td>
                    <td className="py-2.5 px-4 font-medium">Load Versioned Policy</td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-300">+50.0</td>
                    <td className="py-2.5 px-4 text-slate-400">
                      Standard policy: <code className="text-blue-300">policy_v1_india_kyc</code>
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-4 font-mono font-bold text-blue-400">Step 2</td>
                    <td className="py-2.5 px-4 font-medium">Single-Hop Override</td>
                    <td className="py-2.5 px-4 text-right font-mono text-emerald-400">
                      {isSingleHop ? '+20.0' : '0.0'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {isSingleHop
                        ? 'Direct transfer to VASP eliminates intermediary drift'
                        : 'Multi-hop path requires clustering heuristic'}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-4 font-mono font-bold text-blue-400">Step 3a</td>
                    <td className="py-2.5 px-4 font-medium">Exchange Jurisdiction</td>
                    <td className="py-2.5 px-4 text-right font-mono text-emerald-400">
                      +{jurisdictionVal.toFixed(1)}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {selectedVasp.jurisdiction} ({selectedVasp.fiu_status})
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-4 font-mono font-bold text-blue-400">Step 3b</td>
                    <td className="py-2.5 px-4 font-medium">Hop Decay Penalty</td>
                    <td className="py-2.5 px-4 text-right font-mono text-red-400">
                      -{hopPenalty.toFixed(1)}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      Mathematical confidence decay across {hopCount} hops
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-4 font-mono font-bold text-blue-400">Step 3c</td>
                    <td className="py-2.5 px-4 font-medium">Hot Wallet Signature</td>
                    <td className="py-2.5 px-4 text-right font-mono text-emerald-400">
                      +{matchStrength.toFixed(1)}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {isExactMatch ? 'Exact known hot wallet match' : 'Behavioral cluster match'}
                    </td>
                  </tr>
                  {mixerDetected && (
                    <tr>
                      <td className="py-2.5 px-4 font-mono font-bold text-amber-400">Step 3d</td>
                      <td className="py-2.5 px-4 font-medium text-amber-300">Mixer Penalty</td>
                      <td className="py-2.5 px-4 text-right font-mono text-red-400">-30.0</td>
                      <td className="py-2.5 px-4 text-amber-400/90">
                        Zero-knowledge mixer break penalizes attribution
                      </td>
                    </tr>
                  )}
                  <tr>
                    <td className="py-2.5 px-4 font-mono font-bold text-blue-400">Step 3e</td>
                    <td className="py-2.5 px-4 font-medium">Cluster Recency</td>
                    <td className="py-2.5 px-4 text-right font-mono text-emerald-400">
                      +{recentBoost.toFixed(1)}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {recentDays <= 7 ? 'Active within past 7 days' : 'Stale cluster pattern'}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-4 font-mono font-bold text-emerald-400">Step 5/6</td>
                    <td className="py-2.5 px-4 font-semibold text-white">Clamped Composite</td>
                    <td className="py-2.5 px-4 text-right font-mono font-bold text-blue-300">
                      {clampedScore}
                    </td>
                    <td className="py-2.5 px-4 text-slate-300 font-semibold">
                      Normalized in bound [5, 95]
                    </td>
                  </tr>
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function AttributionPage() {
  return (
    <React.Suspense fallback={<div className="p-8 text-center text-slate-400">Loading VASP Attribution Matrix...</div>}>
      <AttributionContent />
    </React.Suspense>
  );
}
