// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { CryptoAlert } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { EmptyState, SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";
import { formatWallet } from "../utils/formatters";

interface AlertsViewProps {
  onNavigate: (route: string) => void;
  openTransaction: (txHash: string) => Promise<void>;
}

export function AlertsView({ onNavigate }: AlertsViewProps) {
  const [alerts, setAlerts] = useState<CryptoAlert[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    mockApi.getAlerts()
      .then((res) => { if (active) setAlerts(res.data); })
      .catch((err) => { if (active) setError(err.message || "Failed to load alerts."); })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  const filtered = alerts.filter((alert) => severityFilter === "ALL" ? true : alert.severity === severityFilter);

  if (loading) return <SkeletonLoader text="Scanning onchain alert events..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div className="view-stack alerts-view">
      <div className="page-heading">
        <div><h1>Alert Triage</h1><p>Review typology detections and rapid fund-movement flags requiring investigator attention.</p></div>
        <Badge tone="red">{alerts.filter((alert) => alert.severity === "HIGH").length} Critical Alerts</Badge>
      </div>

      <section className="kestrel-panel">
        <div className="kestrel-panel-head">
          <div><h2>Alert Register</h2><p>Select an alert to open its active investigation context.</p></div>
          <div className="segmented" aria-label="Filter alerts by severity">
            {["ALL", "HIGH", "MEDIUM", "LOW"].map((severity) => <button key={severity} type="button" className={severityFilter === severity ? "selected" : ""} onClick={() => setSeverityFilter(severity)}>{severity}</button>)}
          </div>
        </div>

        <div className="table-wrap">
          <div className="table-head grid-alert"><span>Severity</span><span>Alert Type</span><span>Linked Case</span><span>Target Wallet</span><span>Status</span></div>
          {filtered.length === 0 ? <EmptyState title="No alerts match this severity" description="Choose another severity filter to restore the register." actionLabel="Show all alerts" onAction={() => setSeverityFilter("ALL")} /> : filtered.map((alert) => (
            <button key={alert.alert_id} className="table-row grid-alert" onClick={() => onNavigate("investigations")}>
              <Badge tone={alert.severity === "HIGH" ? "red" : alert.severity === "MEDIUM" ? "amber" : "neutral"}>{alert.severity}</Badge>
              <strong>{alert.type.replace(/_/g, " ")}</strong>
              <span className="mono table-muted">{alert.case_id}</span>
              <span className="mono text-accent">{formatWallet(alert.wallet)}</span>
              <span className={`status-indicator ${alert.status === "OPEN" ? "open" : "acknowledged"}`}>{alert.status}</span>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
