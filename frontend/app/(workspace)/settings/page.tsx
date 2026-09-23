'use client';

import React from 'react';
import {
  Settings,
  Shield,
  Server,
  Lock,
  FileCode,
  Globe,
  Database,
  CheckCircle2,
  Terminal,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/stores/auth-store';
import { useDebugStore } from '@/stores/debug-store';

export default function SettingsPage() {
  const { user } = useAuthStore();
  const { isDrawerOpen, toggleDrawer, clearLogs } = useDebugStore();

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
            System deployment parameters, statutory policy versioning, and runtime diagnostics.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
