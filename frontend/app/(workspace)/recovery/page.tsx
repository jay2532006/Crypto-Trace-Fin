'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  TrendingUp,
  Clock,
  Building2,
  GitCommit,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Sliders,
  Info,
  Scale,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { formatCrypto, formatINR, formatUSD } from '@/lib/utils';

export default function RecoveryPage() {
  const router = useRouter();

  // Interactive Assessment Simulation State
  const [tracedAmountINR, setTracedAmountINR] = useState<number>(250000);
  const [elapsedHours, setElapsedHours] = useState<number>(14);
  const [hopCount, setHopCount] = useState<number>(2);
  const [isFiuRegistered, setIsFiuRegistered] = useState<boolean>(true);
  const [attributionConfidence, setAttributionConfidence] = useState<'HIGH' | 'MEDIUM' | 'LOW'>('HIGH');
  const [dataCompleteness, setDataCompleteness] = useState<number>(92);
  const [mixerDetected, setMixerDetected] = useState<boolean>(false);

  // Convert INR to USD (approx ₹83 per USD)
  const tracedAmountUSD = tracedAmountINR / 83;
  const MIN_VALUE_USD = 120; // PRD threshold

  // PRD FR-016 Eligibility Boundary Gating
  const ineligibilityReasons: string[] = [];
  if (hopCount <= 0) {
    ineligibilityReasons.push('Zero-hop trace is invalid for recovery scoring per PRD FR-016.');
  }
  if (tracedAmountUSD < MIN_VALUE_USD) {
    ineligibilityReasons.push(
      `Traced value (${formatINR(tracedAmountINR)}) is below minimum actionable threshold (₹10,000 / $120 USD).`
    );
  }
  if (dataCompleteness < 70) {
    ineligibilityReasons.push(
      `Data completeness (${dataCompleteness}%) is below reliable threshold (70%).`
    );
  }
  if (attributionConfidence === 'LOW') {
    ineligibilityReasons.push(
      "Attribution candidate with 'LOW' confidence is invalid for recovery scoring per PRD FR-016."
    );
  }
  if (mixerDetected) {
    ineligibilityReasons.push(
      'Mixer interaction detected along corridor. Cryptographic break prevents recovery estimation.'
    );
  }

  const isEligible = ineligibilityReasons.length === 0;

  // 4 Factor Scoring (when eligible)
  // 1. Cooperation
  const cooperationScore = isFiuRegistered ? 35 : 20;

  // 2. Elapsed Time Decay (< 24h = 30, 24-48h = 15, > 48h = 5)
  let timeScore = 5;
  let actionWindowHours = 6;
  if (elapsedHours <= 24) {
    timeScore = 30;
    actionWindowHours = Math.max(6, Math.round(36 - elapsedHours));
  } else if (elapsedHours <= 48) {
    timeScore = 15;
    actionWindowHours = Math.max(2, Math.round(48 - elapsedHours));
  } else {
    timeScore = 5;
    actionWindowHours = 0;
  }

  // 3. Hop Distance (1 hop = 25, 2-3 hops = 15, >3 = 5)
  let hopScore = 5;
  if (hopCount === 1) hopScore = 25;
  else if (hopCount <= 3) hopScore = 15;

  // 4. Path Clarity
  const clarityScore = dataCompleteness >= 85 ? 10 : 5;

  const totalRecoveryScore = isEligible
    ? Math.min(95, Math.max(10, cooperationScore + timeScore + hopScore + clarityScore))
    : 0;

  const displayTier = !isEligible
    ? 'ineligible'
    : totalRecoveryScore >= 50
    ? 'eligible'
    : 'moderate';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-navy-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Heuristic Recovery Estimate
            </h1>
            <Badge variant="navy">PRD FR-016 Gated</Badge>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Victim-impact operational assessment, time-urgency decay, and Section 91 triage prioritization.
          </p>
        </div>

        {isEligible && (
          <Button
            variant="primary"
            onClick={() =>
              router.push(
                `/legal-notices?action=preservation&urgency=emergency&amount=${tracedAmountINR}`
              )
            }
            className="flex items-center gap-2 text-xs"
          >
            <FileText className="h-3.5 w-3.5" />
            Generate Emergency Section 91 Notice
          </Button>
        )}
      </div>

      {/* Primary KPI & Gauge Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Score Card */}
        <Card
          className={`border-2 ${
            !isEligible
              ? 'border-red-800 bg-red-950/20'
              : totalRecoveryScore >= 50
              ? 'border-emerald-500/50 bg-emerald-950/20'
              : 'border-amber-500/50 bg-amber-950/20'
          }`}
        >
          <CardContent className="p-5 text-center">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Heuristic Recovery Score
            </span>
            <div className="mt-2 flex items-baseline justify-center gap-1 font-mono">
              <span
                className={`text-5xl font-extrabold ${
                  !isEligible
                    ? 'text-red-400'
                    : totalRecoveryScore >= 50
                    ? 'text-emerald-400'
                    : 'text-amber-400'
                }`}
              >
                {isEligible ? totalRecoveryScore : 0}
              </span>
              <span className="text-lg text-slate-500 font-sans">/ 100</span>
            </div>
            <div className="mt-3 flex justify-center">
              <Badge
                variant={
                  displayTier === 'eligible'
                    ? 'success'
                    : displayTier === 'moderate'
                    ? 'warning'
                    : 'danger'
                }
              >
                {displayTier.toUpperCase()} TIER
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Action Window Card */}
        <Card className="border-navy-700/80">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Action Window (Golden Hours)
              </span>
              <Clock className="h-4 w-4 text-amber-400" />
            </div>
            <div className="mt-2 font-mono">
              <div className="text-3xl font-bold text-white">
                {isEligible ? `${actionWindowHours}h` : '0h'}
                <span className="text-xs font-sans text-slate-400 ml-2 font-normal">Remaining</span>
              </div>
            </div>
            <div className="mt-3 w-full bg-navy-900 rounded-full h-2 overflow-hidden border border-navy-800">
              <div
                className="bg-amber-400 h-full transition-all duration-500"
                style={{
                  width: `${Math.min(100, Math.max(5, (actionWindowHours / 36) * 100))}%`,
                }}
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-2">
              Time elapsed since incident: <strong className="text-slate-200">{elapsedHours} hours</strong>
            </p>
          </CardContent>
        </Card>

        {/* Traced Value Card */}
        <Card className="border-navy-700/80">
          <CardContent className="p-5">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Actionable Fraud Volume
            </span>
            <div className="text-2xl font-bold font-mono text-blue-400 mt-2">
              {formatINR(tracedAmountINR)}
            </div>
            <div className="text-xs font-mono text-slate-400 mt-0.5">
              ~ {formatUSD(tracedAmountUSD)}
            </div>
            <div className="mt-3 text-[11px] text-slate-400 flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
              <span>Exceeds minimum threshold (₹10,000 INR)</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Ineligibility Banner if Triggered */}
      {!isEligible && (
        <div className="p-4 rounded-xl border border-red-800 bg-red-950/40 space-y-2">
          <div className="flex items-center gap-2 text-red-300 font-bold text-sm">
            <AlertTriangle className="h-4 w-4 text-red-400" />
            PRD FR-016 Ineligibility Barrier Triggered
          </div>
          <p className="text-xs text-red-200">
            The Heuristic Recovery Estimate is marked <strong>INELIGIBLE</strong> for this case because:
          </p>
          <ul className="list-disc list-inside text-xs text-red-300/90 space-y-1">
            {ineligibilityReasons.map((reason, idx) => (
              <li key={idx}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Simulator & Factor Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Scenario Controls */}
        <div className="lg:col-span-5 space-y-4">
          <Card>
            <CardHeader className="border-b border-navy-800 pb-3">
              <div className="flex items-center gap-2">
                <Sliders className="h-4 w-4 text-blue-400" />
                <CardTitle className="text-sm">Simulation Parameters</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-4 space-y-4 text-xs">
              {/* Traced Amount */}
              <div className="space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400 font-semibold uppercase">Reported Fraud Amount</span>
                  <span className="font-mono text-white font-bold">{formatINR(tracedAmountINR)}</span>
                </div>
                <input
                  type="range"
                  min="5000"
                  max="1000000"
                  step="5000"
                  value={tracedAmountINR}
                  onChange={(e) => setTracedAmountINR(Number(e.target.value))}
                  className="w-full accent-blue-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">Threshold: ≥ ₹10,000 INR ($120 USD)</span>
              </div>

              {/* Elapsed Hours */}
              <div className="space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400 font-semibold uppercase">Elapsed Hours</span>
                  <span className="font-mono text-white font-bold">{elapsedHours} Hours</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="72"
                  value={elapsedHours}
                  onChange={(e) => setElapsedHours(Number(e.target.value))}
                  className="w-full accent-amber-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">
                  Critical window: &lt; 24h (+30 pts), 24-48h (+15 pts), &gt; 48h (+5 pts)
                </span>
              </div>

              {/* Hop Count */}
              <div className="space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400 font-semibold uppercase">Discovered Hops</span>
                  <span className="font-mono text-white font-bold">{hopCount} Hops</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="5"
                  value={hopCount}
                  onChange={(e) => setHopCount(Number(e.target.value))}
                  className="w-full accent-blue-500 h-2 bg-navy-800 rounded-lg cursor-pointer"
                />
              </div>

              {/* FIU Status Toggle */}
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-navy-900 border border-navy-800">
                <div>
                  <span className="text-slate-200 font-semibold block">FIU-IND Reporting Entity</span>
                  <span className="text-[10px] text-slate-400">
                    Destination VASP registered with FIU-IND (+35 pts)
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={isFiuRegistered}
                  onChange={(e) => setIsFiuRegistered(e.target.checked)}
                  className="h-4 w-4 accent-blue-500 rounded cursor-pointer"
                />
              </div>

              {/* Mixer Toggle */}
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-navy-900 border border-navy-800">
                <div>
                  <span className="text-slate-200 font-semibold block">Mixer Interaction</span>
                  <span className="text-[10px] text-slate-400">
                    Triggers immediate ineligibility barrier
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={mixerDetected}
                  onChange={(e) => setMixerDetected(e.target.checked)}
                  className="h-4 w-4 accent-amber-500 rounded cursor-pointer"
                />
              </div>

              {/* Attribution Confidence */}
              <div className="space-y-1.5">
                <span className="text-slate-400 font-semibold uppercase">Attribution Confidence</span>
                <select
                  value={attributionConfidence}
                  onChange={(e) => setAttributionConfidence(e.target.value as any)}
                  className="w-full h-9 px-3 rounded-lg border border-navy-700 bg-navy-900 text-slate-200 text-xs font-medium outline-none"
                >
                  <option value="HIGH">HIGH (Verified Hot Wallet)</option>
                  <option value="MEDIUM">MEDIUM (Heuristic Cluster)</option>
                  <option value="LOW">LOW (Ineligible State)</option>
                </select>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 4 Factor Breakdown */}
        <div className="lg:col-span-7 space-y-4">
          {/* Visual Factor Distribution Chart (Phase 7.2 Win Plan) */}
          <Card className="p-4 bg-navy-950/80 border-navy-800">
            <CardHeader className="p-0 pb-3">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center justify-between">
                <span>Multi-Factor Urgency Distribution</span>
                <span className="text-blue-400 font-mono text-[11px]">Composite: {isEligible ? totalRecoveryScore : 0}/100</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0 space-y-3">
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 flex items-center gap-1.5"><Building2 className="h-3.5 w-3.5 text-blue-400" /> Exchange Cooperation</span>
                  <span className="font-mono font-bold text-blue-400">{isEligible ? cooperationScore : 0}/35 pts</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
                  <div className="bg-blue-500 h-full rounded-full transition-all duration-500" style={{ width: `${isEligible ? (cooperationScore / 35) * 100 : 0}%` }} />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 flex items-center gap-1.5"><Clock className="h-3.5 w-3.5 text-amber-400" /> Time Urgency Decay ({elapsedHours}h)</span>
                  <span className="font-mono font-bold text-amber-400">{isEligible ? timeScore : 0}/30 pts</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
                  <div className="bg-amber-500 h-full rounded-full transition-all duration-500" style={{ width: `${isEligible ? (timeScore / 30) * 100 : 0}%` }} />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 flex items-center gap-1.5"><GitCommit className="h-3.5 w-3.5 text-purple-400" /> Path Simplicity ({hopCount} hops)</span>
                  <span className="font-mono font-bold text-purple-400">{isEligible ? hopScore : 0}/25 pts</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
                  <div className="bg-purple-500 h-full rounded-full transition-all duration-500" style={{ width: `${isEligible ? (hopScore / 25) * 100 : 0}%` }} />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 flex items-center gap-1.5"><TrendingUp className="h-3.5 w-3.5 text-emerald-400" /> Attribution Confidence ({attributionConfidence})</span>
                  <span className="font-mono font-bold text-emerald-400">{isEligible ? (attributionConfidence === "HIGH" ? 10 : 5) : 0}/10 pts</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
                  <div className="bg-emerald-500 h-full rounded-full transition-all duration-500" style={{ width: `${isEligible ? (attributionConfidence === "HIGH" ? 100 : 50) : 0}%` }} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="border-b border-navy-800 pb-3">
              <CardTitle className="text-sm font-bold tracking-wide">
                Operational Factor Weighting Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0 overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-navy-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-navy-800">
                  <tr>
                    <th className="py-2.5 px-4">Factor</th>
                    <th className="py-2.5 px-4">Current Value</th>
                    <th className="py-2.5 px-4 text-right">Points</th>
                    <th className="py-2.5 px-4">Impact</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-navy-800 text-slate-300">
                  <tr>
                    <td className="py-3 px-4 font-semibold flex items-center gap-1.5">
                      <Building2 className="h-4 w-4 text-blue-400" />
                      Exchange Cooperation
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">
                      {isFiuRegistered ? 'FIU-IND Domestic' : 'Global Offshore'}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-emerald-400 font-bold">
                      +{cooperationScore}
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      Compliance responsiveness under Section 91 CrPC
                    </td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-semibold flex items-center gap-1.5">
                      <Clock className="h-4 w-4 text-amber-400" />
                      Time Urgency Decay
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">{elapsedHours}h Elapsed</td>
                    <td className="py-3 px-4 text-right font-mono text-emerald-400 font-bold">
                      +{timeScore}
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      Off-ramp velocity decay before final fiat cashing
                    </td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-semibold flex items-center gap-1.5">
                      <GitCommit className="h-4 w-4 text-purple-400" />
                      Hop Dispersion
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">{hopCount} Hops</td>
                    <td className="py-3 px-4 text-right font-mono text-emerald-400 font-bold">
                      +{hopScore}
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      Distance to destination cold/hot vault
                    </td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-semibold flex items-center gap-1.5">
                      <TrendingUp className="h-4 w-4 text-emerald-400" />
                      Data Completeness
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">{dataCompleteness}%</td>
                    <td className="py-3 px-4 text-right font-mono text-emerald-400 font-bold">
                      +{clarityScore}
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      Unbroken transaction graph confidence
                    </td>
                  </tr>
                </tbody>
              </table>
            </CardContent>
          </Card>

          {/* Statutory Disclaimer Box */}
          <div className="p-4 rounded-xl border border-navy-700 bg-navy-900/60 space-y-1.5 text-xs text-slate-400">
            <div className="flex items-center gap-2 text-slate-200 font-semibold">
              <Scale className="h-4 w-4 text-blue-400" />
              Statutory Law Enforcement Disclaimer (PRD Standard)
            </div>
            <p>
              The <strong>Heuristic Recovery Estimate</strong> is an operational triage score engineered to
              help investigating officers allocate resources effectively and meet the 24-48 hour window for
              Section 91 CrPC notices.
            </p>
            <p className="text-[11px] text-slate-500 italic">
              This score is heuristic and does NOT represent a mathematical probability, financial guarantee,
              or court warranty of restitution.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
