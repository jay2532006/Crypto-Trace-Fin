// @ts-nocheck
import React from "react";
import type { Case, Role } from "../../types";

interface HalyardTopbarProps {
  activeCase: Case | null;
  role: Role;
  onRoleToggle: () => void;
  uiMode: "halyard" | "kestrel" | "classic";
  onSetUiMode: (mode: "halyard" | "kestrel" | "classic") => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onRefresh?: () => void;
  onOpenAlerts?: () => void;
}

export function HalyardTopbar({
  activeCase,
  role,
  onRoleToggle,
  uiMode,
  onSetUiMode,
  searchQuery,
  onSearchChange,
  onRefresh,
  onOpenAlerts
}: HalyardTopbarProps) {
  return (
    <header className="halyard-topbar">
      {/* 72px Signature Logo Cell matching Halyard.canvas */}
      <div className="halyard-logo-cell" title="CryptoTrace LEA — Halyard Console">
        <svg className="halyard-logo" viewBox="0 0 26 26" fill="none" aria-hidden="true">
          <path d="M13 2.2 5.4 14.4h5.7L9.6 23.8 20.4 10.6h-6.2l1.9-8.4Z" fill="currentColor" />
        </svg>
      </div>

      {/* Breadcrumbs matching Halyard.canvas */}
      <nav className="halyard-crumbs" aria-label="Investigation breadcrumb">
        <span className="org">CryptoTrace LEA</span>
        <span className="slash" aria-hidden="true">/</span>
        <span className="proj">Field Workstation</span>
        {activeCase && (
          <span className="case-id-tag" title="Active Investigation Case">
            {activeCase.case_id}
          </span>
        )}
      </nav>

      {/* Right Action Controls */}
      <div className="halyard-topbar-right">
        {/* Universal Search */}
        <div style={{ position: "relative", width: "240px" }}>
          <input
            type="search"
            placeholder="Search wallet / tx / vasp…"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{
              width: "100%",
              height: "32px",
              padding: "0 10px 0 28px",
              fontSize: "12px"
            }}
            aria-label="Search forensic entity"
          />
          <svg
            width="13"
            height="13"
            viewBox="0 0 20 20"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            style={{
              position: "absolute",
              left: "9px",
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--text-3)",
              pointerEvents: "none"
            }}
          >
            <circle cx="9" cy="9" r="5.6" />
            <path d="M13.2 13.2L17 17" />
          </svg>
        </div>

        {/* Synthetic Safe Environment Capsule */}
        <div className="env-status-capsule" title="Synthetic Fixture Replay Environment">
          <span className="pulse-dot" />
          <span>REPLAY · DEMO</span>
        </div>

        {/* Role Gating Switcher */}
        <button
          type="button"
          onClick={onRoleToggle}
          className="halyard-ghost"
          style={{
            borderColor: role === "SUPERVISOR" ? "var(--accent-line)" : "var(--line)",
            color: role === "SUPERVISOR" ? "var(--accent)" : "var(--text)"
          }}
          title="Click to toggle between Investigator and Supervisor roles"
        >
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <rect x="4.4" y="8.6" width="11.2" height="8" rx="2" />
            <path d="M7 8.6V6.4a3 3 0 0 1 6 0v2.2" />
          </svg>
          <span>Role: <strong>{role}</strong></span>
        </button>

        {/* 3-Way Theme Switcher (Halyard / Kestrel / Classic) */}
        <div className="halyard-theme-switch" title="Switch UI design system">
          <button
            type="button"
            className={`halyard-theme-btn ${uiMode === "halyard" ? "active" : ""}`}
            onClick={() => onSetUiMode("halyard")}
          >
            Halyard
          </button>
          <button
            type="button"
            className={`halyard-theme-btn ${uiMode === "kestrel" ? "active" : ""}`}
            onClick={() => onSetUiMode("kestrel")}
          >
            Kestrel
          </button>
          <button
            type="button"
            className={`halyard-theme-btn ${uiMode === "classic" ? "active" : ""}`}
            onClick={() => onSetUiMode("classic")}
          >
            Classic
          </button>
        </div>

        {/* Alerts Square Button */}
        <button
          type="button"
          className="halyard-ghost square"
          onClick={onOpenAlerts}
          aria-label="Notifications & Alerts"
          title="Open real-time alerts triage"
        >
          <svg width="15" height="15" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4.5 7.6a4.5 4.5 0 0 1 9 0c0 2.9.9 4.2 1.5 4.8H3c.6-.6 1.5-1.9 1.5-4.8Z" />
            <path d="M7.4 14.4a1.7 1.7 0 0 0 3.2 0" />
          </svg>
          <span style={{
            position: "absolute",
            top: "2px",
            right: "2px",
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            background: "var(--red)"
          }} />
        </button>

        {/* Refresh Button */}
        {onRefresh && (
          <button
            type="button"
            className="halyard-ghost square"
            onClick={onRefresh}
            aria-label="Refresh telemetry"
            title="Refresh case & audit telemetry"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
          </button>
        )}
      </div>
    </header>
  );
}
