// @ts-nocheck
"use client";

import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Shield, Lock, User, AlertCircle, ArrowRight, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PRESET_USERS, loginUser } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setSession } = useAuthStore();

  const [username, setUsername] = React.useState("investigator1");
  const [password, setPassword] = React.useState("Password@123");
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const isExpired = searchParams?.get("expired") === "1";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const session = await loginUser(username, password);
      setSession(session);
      router.push("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Authentication failed. Check official badge credentials or network connection."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPreset = (u: (typeof PRESET_USERS)[0]) => {
    setUsername(u.username);
    setPassword(u.password);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-4 sm:p-6 bg-slate-900 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#082B63] via-[#070F1E] to-[#040812]">
      {/* Top Government Institutional Banner */}
      <div className="w-full max-w-md text-center mb-6 space-y-2">
        <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-[#062B6F] text-white shadow-xl border border-[#1F66B8]/40 mb-2">
          <Shield className="h-7 w-7 text-[#E5A33D]" />
        </div>
        <h1 className="text-2xl font-bold font-display text-white tracking-wide">
          CRYPTOTRACE LEA
        </h1>
        <p className="text-xs text-slate-300 font-medium tracking-wide uppercase">
          Ministry of Home Affairs // Indian Cybercrime Coordination Centre (I4C)
        </p>
      </div>

      {/* Main Login Card */}
      <div className="w-full max-w-md rounded-2xl border border-slate-700/80 bg-[#0D1B2A]/90 p-8 shadow-2xl backdrop-blur-md space-y-6">
        <div className="border-b border-slate-800 pb-4">
          <h2 className="text-lg font-bold text-white">Investigative Officer Authentication</h2>
          <p className="text-xs text-slate-400 mt-1">
            Access restricted to authorized Law Enforcement personnel (Section 91 CrPC / Section 106 BNSS).
          </p>
        </div>

        {isExpired && (
          <div className="rounded-lg bg-amber-500/10 border border-amber-500/30 p-3 text-xs text-amber-300 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>Session expired for security compliance. Please sign in again.</span>
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-3 text-xs text-red-300 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Officer Username / Badge ID"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. investigator1"
            required
          />
          <Input
            label="Security Passphrase"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••••••"
            required
          />

          <Button type="submit" variant="primary" className="w-full h-11 text-sm font-semibold gap-2 mt-2" isLoading={isLoading}>
            <span>Secure System Sign In</span>
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>

        {/* 1-Click Evaluation Credentials Picker */}
        <div className="border-t border-slate-800/80 pt-5 space-y-3">
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider text-center">
            SIH Evaluation — 1-Click Persona Pre-fills
          </p>
          <div className="grid grid-cols-1 gap-2">
            {PRESET_USERS.map((preset) => (
              <button
                key={preset.username}
                type="button"
                onClick={() => handleSelectPreset(preset)}
                className={`flex items-center justify-between p-2.5 rounded-lg border text-left text-xs transition-all ${
                  username === preset.username
                    ? "bg-[#1F66B8]/20 border-[#1F66B8] text-white"
                    : "bg-slate-900/50 border-slate-800 text-slate-300 hover:bg-slate-800/60"
                }`}
              >
                <div>
                  <div className="font-semibold text-slate-100 flex items-center gap-1.5">
                    {preset.fullName}
                    {username === preset.username && <CheckCircle2 className="h-3 w-3 text-emerald-400" />}
                  </div>
                  <div className="text-[10px] text-slate-400">{preset.unit}</div>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-[#062B6F] text-blue-200 border border-blue-500/20">
                  {preset.role}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Legal Notice */}
      <div className="mt-8 text-center text-[11px] text-slate-500 max-w-md">
        Protected under IT Act 2000 & Criminal Procedure Code. Unauthorized access attempts are monitored and recorded on cryptographic audit ledgers.
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <React.Suspense fallback={<div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-400">Loading CryptoTrace LEA Portal...</div>}>
      <LoginForm />
    </React.Suspense>
  );
}
