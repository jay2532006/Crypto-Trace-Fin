'use client';
// @ts-nocheck

import React, { useState, useEffect } from 'react';
import {
  Shield,
  Server,
  Lock,
  Terminal,
  Sliders,
  CheckCircle2,
  Save,
  RotateCcw,
  Zap,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/stores/auth-store';
import { useDebugStore } from '@/stores/debug-store';

interface UserSettings {
  defaultChain: 'ETH' | 'BTC' | 'TRON' | 'BNB' | 'POLYGON' | 'SOL';
  defaultMode: 'LIVE' | 'DEMO';
  aiProvider: 'gemini' | 'deterministic' | 'auto';
  autoScreenOFAC: boolean;
  autoDraftSection91: boolean;
  maxTraceHops: number;
}

const DEFAULT_SETTINGS: UserSettings = {
  defaultChain: 'ETH',
  defaultMode: 'LIVE',
  aiProvider: 'gemini',
  autoScreenOFAC: true,
  autoDraftSection91: true,
  maxTraceHops: 5,
};

export default function SettingsPage() {
  const { user } = useAuthStore();
  const { isDrawerOpen, toggleDrawer, clearLogs } = useDebugStore();

  const [settings, setSettings] = useState<UserSettings>(DEFAULT_SETTINGS);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('cryptotrace_user_settings');
      if (saved) {
        setSettings(JSON.parse(saved));
      }
    } catch {
      // Use defaults
    }
  }, []);

  const handleChange = <K extends keyof UserSettings>(key: K, value: UserSettings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = () => {
    try {
      localStorage.setItem('cryptotrace_user_settings', JSON.stringify(settings));
      setHasChanges(false);
      toast.success('Investigation preferences saved to secure local storage.');
    } catch {
      toast.error('Failed to save settings.');
    }
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
    setHasChanges(true);
    toast.success('Settings reset to default values.');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-navy-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">System & Security Settings</h1>
            <Badge variant="navy">Node Configuration</Badge>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            System deployment parameters, operator preferences, and runtime diagnostics.
          </p>
        </div>

        {hasChanges && (
          <div className="flex items-center gap-2">
            <Button variant="primary" onClick={handleSave} className="gap-2 text-xs">
              <Save className="h-3.5 w-3.5" /> Save Changes
            </Button>
            <Button variant="outline" onClick={handleReset} className="gap-2 text-xs">
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </Button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Investigation Runtime Preferences */}
        <Card className="border-navy-700/80 md:col-span-2">
          <CardHeader className="border-b border-navy-800 pb-3 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <Sliders className="h-4 w-4 text-cyan-400" />
              <CardTitle className="text-sm">Investigative Runtime Configuration</CardTitle>
            </div>
            <Badge variant="outline" className="border-cyan-500/40 text-cyan-300">
              Interactive
            </Badge>
          </CardHeader>
          <CardContent className="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 text-xs">
            <div>
              <label className="text-slate-300 font-semibold block mb-2">Default Blockchain Network</label>
              <select
                value={settings.defaultChain}
                onChange={(e) => handleChange('defaultChain', e.target.value as any)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="ETH">Ethereum (ETH / ERC-20)</option>
                <option value="BTC">Bitcoin (BTC / UTXO)</option>
                <option value="TRON">TRON (TRC-20 / USDT)</option>
                <option value="SOL">Solana (SOL / SPL)</option>
                <option value="POLYGON">Polygon PoS (MATIC)</option>
                <option value="BNB">BNB Smart Chain</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1">Primary chain pre-selected during complaint intake.</p>
            </div>

            <div>
              <label className="text-slate-300 font-semibold block mb-2">Forensic Trace Execution Mode</label>
              <select
                value={settings.defaultMode}
                onChange={(e) => handleChange('defaultMode', e.target.value as any)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="LIVE">Live On-Chain Mode (Etherscan / RPC / Mempool)</option>
                <option value="DEMO">Demo Scenario Mode (Deterministic Fixtures)</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1">Controls whether traces dispatch live network probes.</p>
            </div>

            <div>
              <label className="text-slate-300 font-semibold block mb-2">AI Forensics & Copilot Provider</label>
              <select
                value={settings.aiProvider}
                onChange={(e) => handleChange('aiProvider', e.target.value as any)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="gemini">Google Gemini 1.5 Flash (Cloud AI)</option>
                <option value="deterministic">Deterministic Statutory Engine (Offline)</option>
                <option value="auto">Auto-Select with Guardrail Fallback</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1">Backend LLM used for case-aware legal advisory.</p>
            </div>

            <div>
              <label className="text-slate-300 font-semibold block mb-2">Maximum Trace Exploration Hops</label>
              <input
                type="number"
                min={2}
                max={10}
                value={settings.maxTraceHops}
                onChange={(e) => handleChange('maxTraceHops', Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
              />
              <p className="text-[11px] text-slate-500 mt-1">Bounded graph traversal depth (2-10 hops).</p>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div>
                <span className="font-semibold text-slate-200 block">Auto-Screen OFAC Sanctions</span>
                <span className="text-[11px] text-slate-500">Screen addresses against US Treasury SDN on ingest.</span>
              </div>
              <input
                type="checkbox"
                checked={settings.autoScreenOFAC}
                onChange={(e) => handleChange('autoScreenOFAC', e.target.checked)}
                className="h-4 w-4 rounded accent-blue-600 cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div>
                <span className="font-semibold text-slate-200 block">Auto-Draft Section 91 Notice</span>
                <span className="text-[11px] text-slate-500">Draft statutory requisition when VASP attributed.</span>
              </div>
              <input
                type="checkbox"
                checked={settings.autoDraftSection91}
                onChange={(e) => handleChange('autoDraftSection91', e.target.checked)}
                className="h-4 w-4 rounded accent-blue-600 cursor-pointer"
              />
            </div>
          </CardContent>
        </Card>

        {/* System Profile */}
        <Card className="border-navy-700/80">
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-blue-400" />
              <CardTitle className="text-sm">Platform & Legal Framework</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Target Problem Statement:</span>
              <span className="font-semibold text-white">SIH 26183 (CryptoTrace LEA)</span>
            </div>
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Active Legal Code:</span>
              <span className="font-semibold text-white">BNSS 2023 & BSA 2023 (India)</span>
            </div>
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Statutory Notice Mandate:</span>
              <span className="font-mono text-blue-300">Section 91 BNSS / CrPC</span>
            </div>
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Electronic Evidence Standard:</span>
              <span className="font-mono text-emerald-300">Section 65B BSA 2023 Certificate</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">VASP Scoring Policy:</span>
              <span className="font-mono text-amber-300">policy_v1_india_kyc (Active)</span>
            </div>
          </CardContent>
        </Card>

        {/* Runtime Network & API Gateway */}
        <Card className="border-navy-700/80">
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center gap-2">
              <Server className="h-4 w-4 text-emerald-400" />
              <CardTitle className="text-sm">API Gateway & Connectivity</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">FastAPI Backend Origin:</span>
              <span className="font-mono text-white">http://127.0.0.1:8765</span>
            </div>
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Next.js Proxy Rewrite:</span>
              <span className="font-mono text-blue-300">/api/:path* -&gt; 8765/api/:path*</span>
            </div>
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Audit Storage Engine:</span>
              <span className="font-mono text-emerald-300">SQLite Chained Ledger (sqlite3)</span>
            </div>
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Ingestion Circuit Breaker:</span>
              <span className="font-semibold text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" /> Armed & Nominal
              </span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">Evidence Content Store:</span>
              <span className="font-mono text-slate-300">SHA-256 Content-Addressed Hash</span>
            </div>
          </CardContent>
        </Card>

        {/* Active Session & Security Context */}
        <Card className="border-navy-700/80">
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-amber-400" />
              <CardTitle className="text-sm">Security & Operator Context</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Logged In Operator:</span>
              <span className="font-semibold text-white">{user?.name} ({user?.username})</span>
            </div>
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Assigned Role:</span>
              <Badge variant="navy">{user?.role}</Badge>
            </div>
            <div className="flex justify-between py-2 border-b border-navy-800">
              <span className="text-slate-400">Jurisdiction Unit:</span>
              <span className="text-slate-200">{user?.unit}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">Supervisor Signing Privilege:</span>
              <span
                className={`font-semibold ${
                  user?.role === 'SUPERVISOR' || user?.role === 'ADMINISTRATOR'
                    ? 'text-emerald-400'
                    : 'text-slate-500'
                }`}
              >
                {user?.role === 'SUPERVISOR' || user?.role === 'ADMINISTRATOR'
                  ? 'ENABLED (Section 91 Requisition Approval)'
                  : 'RESTRICTED (Drafting Only)'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Telemetry & Debugging Drawer */}
        <Card className="border-navy-700/80">
          <CardHeader className="border-b border-navy-800 pb-3">
            <div className="flex items-center gap-2">
              <Terminal className="h-4 w-4 text-purple-400" />
              <CardTitle className="text-sm">Developer Telemetry Drawer</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-4 text-xs">
            <p className="text-slate-400">
              The floating developer & forensics drawer tracks live API requests, status codes, round-trip
              latencies, and RFC-5424 structured system events.
            </p>

            <div className="flex items-center gap-3">
              <Button
                variant={isDrawerOpen ? 'danger' : 'primary'}
                onClick={toggleDrawer}
                className="text-xs"
              >
                {isDrawerOpen ? 'Close Telemetry Drawer' : 'Open Telemetry Drawer'}
              </Button>

              <Button variant="outline" onClick={clearLogs} className="text-xs">
                Clear Telemetry Buffer
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
