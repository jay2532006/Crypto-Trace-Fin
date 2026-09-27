"use client";

import * as React from "react";
import { Shield, User, LogOut, ChevronDown, Activity } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { UserRoleBadge } from "./UserRoleBadge";
import { PRESET_USERS, loginUser } from "@/lib/auth";
import { apiClient } from "@/lib/api-client";

export function TopBar() {
  const { session, setSession, logout } = useAuthStore();
  const [dropdownOpen, setDropdownOpen] = React.useState(false);
  const [prices, setPrices] = React.useState<{
    btc?: number;
    btc_inr?: number;
    eth?: number;
    eth_inr?: number;
    usdt_inr?: number;
    tron_inr?: number;
  }>({
    btc: 84426,
    btc_inr: 8089753,
    eth: 2686,
    eth_inr: 257467,
    usdt_inr: 95.8,
    tron_inr: 31.98,
  });

  React.useEffect(() => {
    const fetchPrices = () => {
      apiClient
        .get("/api/prices")
        .then((res) => {
          if (res.data) {
            const data = res.data;
            setPrices({
              btc: data.BTC?.usd ?? data.btc?.usd ?? 84426,
              btc_inr: data.BTC?.inr ?? data.btc?.inr ?? 8089753,
              eth: data.ETH?.usd ?? data.eth?.usd ?? 2686,
              eth_inr: data.ETH?.inr ?? data.eth?.inr ?? 257467,
              usdt_inr: data.USDT?.inr ?? data.usdt?.inr ?? 95.8,
              tron_inr: data.TRON?.inr ?? data.tron?.inr ?? 31.98,
            });
          }
        })
        .catch(() => {});
    };
    fetchPrices();
    const interval = setInterval(fetchPrices, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSwitchPersona = async (username: string) => {
    const preset = PRESET_USERS.find((u) => u.username === username);
    if (!preset) return;
    try {
      const s = await loginUser(preset.username, preset.password);
      setSession(s);
      setDropdownOpen(false);
    } catch {
      // Fallback local switch
      setSession({
        username: preset.username,
        fullName: preset.fullName,
        role: preset.role,
        unit: preset.unit,
      });
      setDropdownOpen(false);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-[#070F1E]/95 backdrop-blur px-6 shadow-sm">
      {/* Brand & Emblem Placeholder */}
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#062B6F] text-white shadow-sm border border-[#1F66B8]/30">
          <Shield className="h-5 w-5 text-[#E5A33D]" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-display font-extrabold tracking-wide text-base text-[#062B6F] dark:text-white">
              CRYPTOTRACE LEA
            </span>
            <span className="rounded bg-[#EAF3FC] dark:bg-blue-950/60 px-1.5 py-0.5 text-[10px] font-bold text-[#062B6F] dark:text-blue-300 border border-[#1F66B8]/20">
              SIH 26183
            </span>
          </div>
          <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
            Institutional Cybercrime Intelligence & Attribution Platform
          </p>
        </div>
      </div>

      {/* Spot Price Ticker & Telemetry */}
      <div className="hidden lg:flex items-center gap-4 text-xs font-mono bg-slate-50 dark:bg-slate-900/60 px-3.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
          <span className="font-sans font-bold text-[10px] text-slate-400">BTC</span>
          <span>${prices.btc?.toLocaleString()}</span>
        </div>
        <span className="text-slate-300 dark:text-slate-700">|</span>
        <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
          <span className="font-sans font-bold text-[10px] text-slate-400">ETH</span>
          <span>${prices.eth?.toLocaleString()}</span>
        </div>
        <span className="text-slate-300 dark:text-slate-700">|</span>
        <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-bold">
          <span className="font-sans font-bold text-[10px] text-slate-400">USDT/INR</span>
          <span>₹{prices.usdt_inr?.toFixed(2)}</span>
        </div>
        <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse ml-1" title="Live Telemetry Connected" />
      </div>

      {/* User Session & Role Menu */}
      <div className="relative flex items-center gap-3">
        <UserRoleBadge role={session?.role} />

        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/80 px-3 py-1.5 text-xs text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <User className="h-3.5 w-3.5 text-[#1F66B8]" />
            <span className="font-medium max-w-[120px] truncate">{session?.fullName || "Officer"}</span>
            <ChevronDown className="h-3 w-3 text-slate-400" />
          </button>

          {/* Persona & Logout Dropdown */}
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-64 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0D1B2A] p-2 text-xs shadow-xl z-50">
              <div className="border-b border-slate-100 dark:border-slate-800 px-3 py-2">
                <p className="font-bold text-slate-900 dark:text-white">{session?.fullName}</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">{session?.unit}</p>
              </div>

              <div className="py-2">
                <p className="px-3 pb-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider font-sans">
                  Switch Persona (Audit & Test)
                </p>
                {PRESET_USERS.map((u) => (
                  <button
                    key={u.username}
                    onClick={() => handleSwitchPersona(u.username)}
                    className={`w-full flex items-center justify-between px-3 py-1.5 text-left rounded-md transition-colors ${
                      session?.username === u.username
                        ? "bg-[#EAF3FC] text-[#062B6F] dark:bg-blue-950 dark:text-blue-200 font-semibold"
                        : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                    }`}
                  >
                    <span>{u.fullName}</span>
                    <span className="text-[10px] opacity-75">{u.role}</span>
                  </button>
                ))}
              </div>

              <div className="border-t border-slate-100 dark:border-slate-800 pt-1">
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    logout();
                  }}
                  className="flex w-full items-center gap-2 px-3 py-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-md transition-colors"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
