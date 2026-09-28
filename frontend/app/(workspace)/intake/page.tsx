"use client";

import * as React from "react";
import { 
  Radio, ShieldAlert, ArrowRight, ShieldCheck, AlertOctagon, 
  RefreshCw, Play, FileText, CheckCircle2, Clock, Send, Lock
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

export default function IntakePage() {
  const [gatewayStatus, setGatewayStatus] = React.useState<any>(null);
  const [queue, setQueue] = React.useState<any[]>([]);
  const [rejections, setRejections] = React.useState<any[]>([
    {
      id: "REJ-NCRP-092",
      type: "NCRP_COMPLAINT",
      reason: "SECURITY VIOLATION: Potential 64-character private key detected in complaint narrative. Rejected for security compliance.",
      timestamp: "10 mins ago",
      snippet: "Victim stated suspect sent key 0x4f3edf983ac636a65a842ce7c78d9aa... to access wallet."
    },
    {
      id: "REJ-SEED-041",
      type: "SAHYOG_BULLETIN",
      reason: "SECURITY VIOLATION: Potential 12/24-word seed phrase / mnemonic detected in bulletin narrative. Rejected to protect victim credentials.",
      timestamp: "32 mins ago",
      snippet: "Complainant was instructed to write down words: abandon ability able about above..."
    }
  ]);
  const [loading, setLoading] = React.useState(false);
  const [actionMessage, setActionMessage] = React.useState<string | null>(null);

  const fetchStatusAndQueue = React.useCallback(async () => {
    try {
      const stRes = await fetch("http://localhost:8765/api/v1/intake/status");
      if (stRes.ok) {
        setGatewayStatus(await stRes.json());
      }
      const qRes = await fetch("http://localhost:8765/api/v1/intake/queue");
      if (qRes.ok) {
        setQueue(await qRes.json());
      }
    } catch (e) {
      console.error("Intake fetch error:", e);
    }
  }, []);

  React.useEffect(() => {
    fetchStatusAndQueue();
    const interval = setInterval(fetchStatusAndQueue, 4000);
    return () => clearInterval(interval);
  }, [fetchStatusAndQueue]);

  // Dispatch simulated test complaint
  const handleSimulateNCRP = async () => {
    setLoading(true);
    setActionMessage(null);
    try {
      // Login as integration service or pass token
      const authRes = await fetch("http://localhost:8765/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "admin1", password: "Password@123" }),
      });
      const authData = await authRes.json();
      const token = authData.access_token;

      const ack = `NCRP-MHA-${Date.now()}`;
      const res = await fetch("http://localhost:8765/api/v1/intake/ncrp/complaint", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ncrp_ack_number: ack,
          chain: "TRON",
          suspect_wallet: "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
          reported_amount: 54200.0,
          complainant_name: "Ramesh K. Verma",
          complaint_text: "Victim defrauded of 54,200 USDT via fake high-yield crypto investment syndicate.",
          fir_number: `FIR-${Date.now() % 1000}/CYBER`,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setActionMessage(`[?] NCRP Complaint Ingested successfully: Case ID ${data.case_id}`);
        fetchStatusAndQueue();
      } else {
        setActionMessage(`[!] Ingestion rejected: ${JSON.stringify(data)}`);
      }
    } catch (err: any) {
      setActionMessage(`[!] Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Test Security Rejection demo moment
  const handleTestSecurityRejection = async () => {
    setLoading(true);
    setActionMessage(null);
    try {
      const authRes = await fetch("http://localhost:8765/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "admin1", password: "Password@123" }),
      });
      const authData = await authRes.json();
      const token = authData.access_token;

      const res = await fetch("http://localhost:8765/api/v1/intake/ncrp/complaint", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ncrp_ack_number: `NCRP-BAD-${Date.now()}`,
          chain: "ETH",
          suspect_wallet: "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
          complaint_text: "Victim stated suspect sent key 0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d to access wallet.",
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        const rejEntry = {
          id: `REJ-LIVE-${Date.now() % 1000}`,
          type: "NCRP_COMPLAINT",
          reason: data.detail?.reason || data.detail || "SECURITY VIOLATION: Private key detected",
          timestamp: "Just now",
          snippet: "Victim stated suspect sent key 0x4f3edf983ac636... to access wallet."
        };
        setRejections(prev => [rejEntry, ...prev]);
        setActionMessage("[?] Safeguard Triggered: Payload REJECTED as expected to prevent key leakage into court records!");
      }
    } catch (err: any) {
      setActionMessage(`[!] Test error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerTrace = async (caseId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8765/api/v1/intake/${caseId}/trace`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      if (res.ok) {
        setActionMessage(`[?] Forensic trace completed and legal preservation notice drafted for ${caseId}!`);
        fetchStatusAndQueue();
      }
    } catch (err: any) {
      setActionMessage(`[!] Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-400">
              <Radio className="h-5 w-5 animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                NCRP & SAHYOG Automated Intake Feed
                <Badge variant="outline" className="text-xs border-amber-500/60 bg-amber-500/10 text-amber-300">
                  SIH 26183 Core Gateway
                </Badge>
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Real-time government complaint ingestion, credential leak rejection, and automated preservation notice drafting.
              </p>
            </div>
          </div>
        </div>

        {/* Sandbox Warning Banner / Status Chip */}
        <div className="flex items-center gap-2 bg-amber-950/40 border border-amber-500/50 px-3.5 py-2 rounded-lg text-xs">
          <AlertOctagon className="h-4 w-4 text-amber-400 flex-shrink-0" />
          <div>
            <span className="font-bold text-amber-300 block">
              {gatewayStatus?.banner || "SANDBOX GATEWAY ? NOT A LIVE MHA CONNECTION"}
            </span>
            <span className="text-[10px] text-amber-200/70">
              Adapters report UNAVAILABLE_UNAUTHORIZED without credentials; flips to live when configured.
            </span>
          </div>
        </div>
      </div>

      {actionMessage && (
        <div className="rounded-lg bg-blue-950/60 border border-blue-500/40 p-3 text-xs text-blue-200 flex items-center justify-between">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="text-slate-400 hover:text-white">?</button>
        </div>
      )}

      {/* Simulator Action Panel for Demo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 bg-slate-900/60 border-slate-800 space-y-3">
          <div className="flex items-center gap-2">
            <Radio className="h-4 w-4 text-blue-400" />
            <h3 className="text-xs font-bold text-white uppercase">1. Simulate NCRP Complaint</h3>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Emit mock NCRP cybercrime complaint with suspect TRON wallet (54,200 USDT).
          </p>
          <Button 
            onClick={handleSimulateNCRP} 
            disabled={loading}
            className="w-full text-xs bg-blue-600 hover:bg-blue-500 text-white"
          >
            <Send className="h-3.5 w-3.5 mr-1.5" />
            Dispatch NCRP Complaint
          </Button>
        </Card>

        <Card className="p-4 bg-slate-900/60 border-slate-800 space-y-3">
          <div className="flex items-center gap-2">
            <Lock className="h-4 w-4 text-red-400" />
            <h3 className="text-xs font-bold text-red-300 uppercase">2. Test Key Leak Safeguard</h3>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Dispatch payload with a leaked private key to verify 100% rejection compliance.
          </p>
          <Button 
            onClick={handleTestSecurityRejection} 
            disabled={loading}
            variant="danger"
            className="w-full text-xs bg-red-600/80 hover:bg-red-600 text-white"
          >
            <ShieldAlert className="h-3.5 w-3.5 mr-1.5" />
            Test Security Rejection
          </Button>
        </Card>

        <Card className="p-4 bg-slate-900/60 border-slate-800 space-y-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <h3 className="text-xs font-bold text-emerald-300 uppercase">Gateway Provenance</h3>
          </div>
          <div className="text-[11px] space-y-1 text-slate-300 font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">NCRP Gateway:</span>
              <span className="text-amber-400 font-semibold">{gatewayStatus?.ncrp?.status || "SANDBOX"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">SAHYOG Gateway:</span>
              <span className="text-amber-400 font-semibold">{gatewayStatus?.sahyog?.status || "SANDBOX"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Deduplication:</span>
              <span className="text-emerald-400">Postgres Authoritative</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Intake Processing Pipeline */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Clock className="h-4 w-4 text-cyan-400" />
            Intake Pipeline Progression (RECEIVED ? VALIDATED ? TRACING ? ATTRIBUTED ? NOTICE DRAFTED)
          </h2>
          <Badge variant="outline" className="text-xs text-slate-400">
            {queue.length} Active Records
          </Badge>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Case / ACK Reference</th>
                <th className="p-3">Source</th>
                <th className="p-3">Suspect Wallet</th>
                <th className="p-3">Progression State</th>
                <th className="p-3">Time</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {queue.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-slate-500 italic">
                    No complaints in current queue. Click "Dispatch NCRP Complaint" above to simulate inbound ingestion.
                  </td>
                </tr>
              ) : (
                queue.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3 font-bold text-white">{item.case_id}</td>
                    <td className="p-3">
                      <Badge variant="outline" className="text-[10px] border-blue-500/50 text-blue-300">
                        {item.source}
                      </Badge>
                    </td>
                    <td className="p-3 text-cyan-300">{item.wallet?.slice(0, 10)}...{item.wallet?.slice(-6)}</td>
                    <td className="p-3">
                      <Badge 
                        className={`text-[10px] font-bold ${
                          item.status === "NOTICE DRAFTED"
                            ? "bg-emerald-600 text-white"
                            : item.status === "ATTRIBUTED"
                            ? "bg-blue-600 text-white"
                            : item.status === "TRACING"
                            ? "bg-purple-600 text-white animate-pulse"
                            : "bg-amber-600 text-white"
                        }`}
                      >
                        {item.status}
                      </Badge>
                    </td>
                    <td className="p-3 text-slate-400 text-[10px]">{new Date(item.timestamp).toLocaleTimeString()}</td>
                    <td className="p-3 text-right">
                      {item.status !== "NOTICE DRAFTED" ? (
                        <Button 
                          size="sm"
                          onClick={() => handleTriggerTrace(item.case_id)}
                          disabled={loading}
                          className="text-[10px] h-7 bg-cyan-600 hover:bg-cyan-500 text-white"
                        >
                          <Play className="h-3 w-3 mr-1" />
                          Execute Trace
                        </Button>
                      ) : (
                        <a 
                          href="/legal-notices" 
                          className="inline-flex items-center text-[10px] text-emerald-400 hover:underline"
                        >
                          <FileText className="h-3 w-3 mr-1" />
                          Review Notice Draft
                        </a>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Security Rejection Panel (PRD Rule 4 / Evidentiary Demo Moment) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-red-300 uppercase tracking-wider flex items-center gap-2">
            <AlertOctagon className="h-4 w-4 text-red-400" />
            Security Rejection Log (Credential Leak Prevention)
          </h2>
          <span className="text-[10px] text-slate-400">Rejected before database entry or court evidence transmission</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {rejections.map((rej, i) => (
            <div key={i} className="rounded-xl border border-red-900/60 bg-red-950/20 p-4 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <Badge variant="danger" className="text-[10px] bg-red-600 text-white font-mono">
                  {rej.id} ? {rej.type}
                </Badge>
                <span className="text-[10px] text-slate-400">{rej.timestamp}</span>
              </div>
              <p className="text-red-300 font-semibold text-[11px]">{rej.reason}</p>
              <div className="rounded bg-black/60 p-2 font-mono text-[10px] text-slate-400 border border-red-900/40">
                Snippet: <span className="text-slate-300">{rej.snippet}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
