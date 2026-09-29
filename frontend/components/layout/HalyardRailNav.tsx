import React from "react";
import type { Route } from "./Sidebar";

interface HalyardRailNavProps {
  currentRoute: Route;
  onNavigate: (route: Route) => void;
  openAlertsCount?: number;
}

export function HalyardRailNav({ currentRoute, onNavigate, openAlertsCount = 18 }: HalyardRailNavProps) {
  return (
    <nav className="halyard-railnav" aria-label="Investigation sections">
      {/* 1. Casework Navigation */}
      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "overview" ? "is-active" : ""}
          onClick={() => onNavigate("overview")}
          aria-label="Overview"
          title="Overview"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3.2 8.6L10 3.2l6.8 5.4v7a1.4 1.4 0 0 1-1.4 1.4H4.6a1.4 1.4 0 0 1-1.4-1.4Z" />
            <path d="M7.8 17V11h4.4v6" />
          </svg>
          <span className="halyard-tooltip">Overview</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "cases" ? "is-active" : ""}
          onClick={() => onNavigate("cases")}
          aria-label="Cases"
          title="Cases"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3.6" width="14" height="12.8" rx="2" />
            <path d="M3 7.8h14M8.2 7.8v8.6" />
          </svg>
          <span className="halyard-tooltip">Cases (Intake)</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "alerts" ? "is-active" : ""}
          onClick={() => onNavigate("alerts")}
          aria-label="Alerts"
          title="Alerts"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M15.4 13.5H4.6c.6-.6 1.4-1.8 1.4-4.5a4 4 0 1 1 8 0c0 2.7.8 3.9 1.4 4.5Z" />
            <path d="M8 15.5a2 2 0 0 0 4 0" />
          </svg>
          {openAlertsCount > 0 && <span className="badge-dot" />}
          <span className="halyard-tooltip">Alerts ({openAlertsCount})</span>
        </button>
      </div>

      <span className="halyard-rail-sep" aria-hidden="true" />

      {/* 2. Trace & Analysis Navigation */}
      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "investigations" ? "is-active" : ""}
          onClick={() => onNavigate("investigations")}
          aria-label="Investigations"
          title="Investigations"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="10" cy="10" r="3" />
            <circle cx="4" cy="6" r="2" />
            <circle cx="16" cy="6" r="2" />
            <circle cx="16" cy="14" r="2" />
            <circle cx="4" cy="14" r="2" />
            <path d="M5.8 7l2.5 1.7M14.2 7l-2.5 1.7M5.8 13l2.5-1.7M14.2 13l-2.5-1.7" />
          </svg>
          <span className="halyard-tooltip">Fund-Flow Atlas</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "transactions" ? "is-active" : ""}
          onClick={() => onNavigate("transactions")}
          aria-label="Transactions"
          title="Transactions"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 6h12M4 10h12M4 14h8" />
          </svg>
          <span className="halyard-tooltip">Transactions</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "wallets" ? "is-active" : ""}
          onClick={() => onNavigate("wallets")}
          aria-label="Wallets"
          title="Wallets"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4.5" width="14" height="11" rx="2" />
            <path d="M17 9h-3a1.5 1.5 0 0 0 0 3h3" />
          </svg>
          <span className="halyard-tooltip">Suspect Wallets</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "typologies" ? "is-active" : ""}
          onClick={() => onNavigate("typologies")}
          aria-label="Typologies"
          title="Typologies"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="10 2.5 17 6.5 17 13.5 10 17.5 3 13.5 3 6.5 10 2.5" />
            <line x1="10" y1="2.5" x2="10" y2="17.5" />
          </svg>
          <span className="halyard-tooltip">Typologies (Mule Net)</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "vasp" ? "is-active" : ""}
          onClick={() => onNavigate("vasp")}
          aria-label="VASP Intelligence"
          title="VASP Intelligence"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <ellipse cx="10" cy="5.4" rx="6.2" ry="2.4" />
            <path d="M3.8 5.4v9.2c0 1.3 2.8 2.4 6.2 2.4s6.2-1.1 6.2-2.4V5.4" />
            <path d="M3.8 10c0 1.3 2.8 2.4 6.2 2.4s6.2-1.1 6.2-2.4" />
          </svg>
          <span className="halyard-tooltip">VASP Scorer</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "cross-chain" ? "is-active" : ""}
          onClick={() => onNavigate("cross-chain")}
          aria-label="Cross-Chain"
          title="Cross-Chain"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 14l4-4 3 3 7-7" />
            <path d="M12 6h5v5" />
          </svg>
          <span className="halyard-tooltip">Cross-Chain Bridges</span>
        </button>
      </div>

      <span className="halyard-rail-sep" aria-hidden="true" />

      {/* 3. Records & Governance */}
      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "evidence" ? "is-active" : ""}
          onClick={() => onNavigate("evidence")}
          aria-label="Evidence Vault"
          title="Evidence Vault"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 2.5l6.5 3v5c0 4.2-2.8 8.1-6.5 9-3.7-.9-6.5-4.8-6.5-9v-5l6.5-3Z" />
            <path d="M7.5 10l2 2 3.5-3.5" />
          </svg>
          <span className="halyard-tooltip">Evidence Vault</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "reports" ? "is-active" : ""}
          onClick={() => onNavigate("reports")}
          aria-label="Reports"
          title="Reports"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 3.4h6.4L15 7v9.6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4.4a1 1 0 0 1 1-1Z" />
            <path d="M11.2 3.4V7H15" />
          </svg>
          <span className="halyard-tooltip">Court Dossier</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "supervisor" ? "is-active" : ""}
          onClick={() => onNavigate("supervisor")}
          aria-label="Supervisor Review"
          title="Supervisor Review"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <rect x="4.4" y="8.6" width="11.2" height="8" rx="2" />
            <path d="M7 8.6V6.4a3 3 0 0 1 6 0v2.2" />
          </svg>
          <span className="halyard-tooltip">Sec 91 CrPC Preservation</span>
        </button>
      </div>

      <div className="rail-btn-wrapper">
        <button
          type="button"
          className={currentRoute === "system" ? "is-active" : ""}
          onClick={() => onNavigate("system")}
          aria-label="System Health"
          title="System Health"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="10" cy="10" r="7" />
            <path d="M3.4 8.2h13.2M3.4 11.8h13.2" />
          </svg>
          <span className="halyard-tooltip">System Status</span>
        </button>
      </div>

      {/* 4. Rail Bottom */}
      <div className="halyard-rail-bottom">
        <span className="halyard-rail-sep" aria-hidden="true" />
        <div className="rail-btn-wrapper">
          <button
            type="button"
            onClick={() => onNavigate("investigations")}
            aria-label="Quick Search"
            title="Quick Search"
          >
            <svg width="19" height="19" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
              <circle cx="9" cy="9" r="5.6" />
              <path d="M13.2 13.2L17 17" />
            </svg>
            <span className="halyard-tooltip">Search Entity</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
