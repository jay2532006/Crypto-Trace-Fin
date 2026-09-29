// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { Case, Chain, SourceType } from "../types";
import { mockApi, type IntakeInput } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { EmptyState, SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";
import { formatInr } from "../utils/formatters";

interface CasesViewProps {
  activeCase: Case;
  setActiveCase: (c: Case) => void;
  onNavigate: (route: string) => void;
}

export function CasesView({ activeCase, setActiveCase, onNavigate }: CasesViewProps) {
  const [source, setSource] = useState<SourceType>("NCRP_INTAKE");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [createdCaseId, setCreatedCaseId] = useState<string | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [queueError, setQueueError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const initialForm: IntakeInput = {
    source: "NCRP_INTAKE",
    complaint_id: "NCRP-2026-184721",
    fraud_type: "INVESTMENT_FRAUD",
    fraud_amount_inr: 200000,
    incident_datetime: "2026-09-16T14:32",
    state: "Chhattisgarh",
    chain: "ethereum",
    wallet: activeCase.reported_wallet
  };
  const [form, setForm] = useState<IntakeInput>(initialForm);

  const loadCases = async () => {
    setLoading(true);
    setQueueError(null);
    try {
      const res = await mockApi.getCases();
      if (res.success && res.data) setCases(res.data);
      else setQueueError(res.error?.message ?? "Unable to load the active case queue.");
    } catch (err) {
      setQueueError(err instanceof Error ? err.message : "Unable to load the active case queue.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void loadCases(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setMessage(null);
    setCreatedCaseId(null);

    try {
      const response = await mockApi.createCase({ ...form, source });
      if (!response.success || !response.data) {
        setMessage(response.error?.message ?? "Validation failed. Please verify the intake fields.");
        return;
      }

      const caseRes = await mockApi.getCase(response.data.case_id);
      if (caseRes.data) setActiveCase(caseRes.data);
      setCreatedCaseId(response.data.case_id);
      setMessage(`Case ${response.data.case_id} created and added to the intake register.`);
      await loadCases();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Unable to create the demo case.");
    } finally {
      setBusy(false);
    }
  };

  const filteredCases = cases.filter((c) =>
    c.case_id.toLowerCase().includes(search.toLowerCase()) ||
    c.reported_wallet.toLowerCase().includes(search.toLowerCase()) ||
    c.fraud_type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="view-stack cases-view">
      <div className="page-heading">
        <div>
          <h1>Case Intake & Active Queue</h1>
          <p>Register a complaint, validate its known facts, and open the selected case workspace.</p>
        </div>
        <span className="context-chip">Local intake register</span>
      </div>

      <div className="case-intake-layout">
        <section className="kestrel-panel intake-panel">
          <div className="kestrel-panel-head">
            <div>
              <h2>Case Intake Form</h2>
              <p>Select the registry source before entering the complaint and wallet facts.</p>
            </div>
            <div className="segmented" aria-label="Case registry source">
              <button type="button" className={source === "NCRP_INTAKE" ? "selected" : ""} onClick={() => setSource("NCRP_INTAKE")}>NCRP Intake</button>
              <button type="button" className={source === "SAHYOG" ? "selected" : ""} onClick={() => setSource("SAHYOG")}>SAHYOG</button>
              <button type="button" className={source === "MANUAL" ? "selected" : ""} onClick={() => setSource("MANUAL")}>Manual Entry</button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="form-grid">
            <label className="form-label">Complaint / Bulletin ID<input className="form-input mono" value={form.complaint_id} onChange={(e) => setForm({ ...form, complaint_id: e.target.value })} placeholder="e.g. NCRP-2026-184721" /></label>
            <label className="form-label">Fraud Classification<input className="form-input" value={form.fraud_type} onChange={(e) => setForm({ ...form, fraud_type: e.target.value })} placeholder="e.g. INVESTMENT_FRAUD" /></label>
            <label className="form-label">Reported Loss (INR ₹)<input className="form-input" type="number" min="1" value={form.fraud_amount_inr} onChange={(e) => setForm({ ...form, fraud_amount_inr: Number(e.target.value) })} /></label>
            <label className="form-label">Incident Timestamp<input className="form-input" type="datetime-local" value={form.incident_datetime} onChange={(e) => setForm({ ...form, incident_datetime: e.target.value })} /></label>
            <label className="form-label">Originating Indian State<input className="form-input" value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} placeholder="e.g. Chhattisgarh" /></label>
            <label className="form-label">Primary Blockchain<select className="form-select" value={form.chain} onChange={(e) => setForm({ ...form, chain: e.target.value as Chain })}><option value="ethereum">Ethereum (ETH / ERC-20)</option><option value="polygon">Polygon (MATIC / PoS)</option><option value="tron">Tron (TRX / TRC-20)</option><option value="bitcoin">Bitcoin (BTC / UTXO)</option></select></label>
            <label className="form-label span-2">Suspect Wallet Address<input className="form-input mono" value={form.wallet} onChange={(e) => setForm({ ...form, wallet: e.target.value })} placeholder="0x... or Tron/Bitcoin address" /></label>

            <div className="span-2 action-row">
              <button type="submit" className="btn-primary" disabled={busy}>{busy ? "Creating case..." : "Validate & Create Demo Case"}</button>
              <button type="button" className="btn-secondary" onClick={() => { setForm(initialForm); setSource("NCRP_INTAKE"); }}>Load Fixture Defaults</button>
            </div>
          </form>

          {message && (
            <div className={`inline-feedback ${createdCaseId ? "success" : "error"}`} role={createdCaseId ? "status" : "alert"}>
              <span>{message}</span>
              {createdCaseId && <button className="link-btn" onClick={() => onNavigate("investigations")}>Open Investigation →</button>}
            </div>
          )}
        </section>

        <section className="kestrel-panel queue-panel">
          <div className="kestrel-panel-head">
            <div>
              <h2>Active Queue</h2>
              <p>Select a case to switch the active workspace.</p>
            </div>
          </div>
          <input className="form-input queue-search" placeholder="Filter by case ID, wallet, or fraud type..." value={search} onChange={(e) => setSearch(e.target.value)} aria-label="Filter active case queue" />

          {loading ? <SkeletonLoader text="Loading case queue..." /> : queueError ? <ErrorNotice message={queueError} onRetry={() => void loadCases()} /> : filteredCases.length === 0 ? <EmptyState title="No matching cases" description="Try a case ID, wallet address, or fraud classification." actionLabel="Clear filter" onAction={() => setSearch("")} /> : (
            <div className="queue-list">
              {filteredCases.map((c) => {
                const isCurrent = c.case_id === activeCase.case_id;
                return (
                  <button key={c.case_id} className={`queue-item ${isCurrent ? "selected" : ""}`} onClick={() => { setActiveCase(c); onNavigate("investigations"); }}>
                    <div className="queue-item-head"><span className="mono">{c.case_id}</span><Badge tone={c.source_badge}>{c.source_badge}</Badge></div>
                    <div className="queue-item-main"><span>{c.fraud_type.replace(/_/g, " ")}</span><strong>{formatInr(c.fraud_amount_inr)}</strong></div>
                    <div className="queue-item-meta"><span className="mono">{c.primary_chain}</span><Badge tone="partial">{c.data_coverage}</Badge></div>
                  </button>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
