// @ts-nocheck
import React, { useState, useEffect } from "react";
import type { AuditEvent, PreservationRequest, Role } from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { AuditTimeline } from "../components/common/AuditTimeline";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";

interface SupervisorViewProps {
  role: Role;
  auditRefresh: number;
  setAuditRefresh: (v: number) => void;
}

export function SupervisorView({ role, auditRefresh, setAuditRefresh }: SupervisorViewProps) {
  const [request, setRequest] = useState<PreservationRequest | null>(null);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [note, setNote] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [reqRes, audRes] = await Promise.all([
        mockApi.getSupervisorRequests(),
        mockApi.getAudit()
      ]);
      setRequest(reqRes.data[0]);
      setAudit(audRes.data);
    } catch (err: any) {
      setError(err.message || "Failed to load supervisor data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [auditRefresh]);

  const handleDraft = async () => {
    await mockApi.createPreservationRequest();
    setNote("Preservation request drafted and submitted for supervisor review.");
    setAuditRefresh(auditRefresh + 1);
  };

  const handleDecision = async (decision: "APPROVED" | "REJECTED") => {
    if (role !== "SUPERVISOR") {
      setNote("Approval is supervisor-gated. Switch role to SUPERVISOR in topbar to review.");
      return;
    }

    await mockApi.approvePreservationRequest(decision, "Demo Supervisor");
    setNote(`Request ${decision}. Audit entry generated. (No live legal freeze executed)`);
    setAuditRefresh(auditRefresh + 1);
  };

  if (loading) return <SkeletonLoader text="Loading supervisor authorization queue..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="sec-head">
        <div>
          <h2>Supervisor Oversight & Preservation Requests</h2>
          <p>Role-gated legal review workflow adhering to Section 91 CrPC standards</p>
        </div>
        <Badge tone={role === "SUPERVISOR" ? "green" : "blue"}>Active Role: {role}</Badge>
      </div>

      <div className="kestrel-grid-3">
        {/* Preservation Request Form/Card */}
        <div style={{ gridColumn: "span 2" }}>
          <div className="kestrel-panel">
            <div className="kestrel-panel-head">
              <div>
                <h2>Preservation Request Workflow</h2>
                <p>Status: Draft → Pending Supervisor → Approved / Rejected</p>
              </div>
            </div>

            {request && (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                <div style={{
                  padding: "16px",
                  borderRadius: "var(--r-md)",
                  background: "var(--elev-2)",
                  border: "1px solid var(--line)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  flexWrap: "wrap",
                  gap: "10px"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <Badge tone={request.status === "APPROVED" ? "green" : request.status === "REJECTED" ? "red" : "amber"}>
                      {request.status}
                    </Badge>
                    <span className="mono" style={{ fontWeight: 700, color: "var(--text)" }}>
                      {request.request_id}
                    </span>
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--text-3)" }}>
                    Recipient VASP: <strong style={{ color: "var(--accent-2)" }}>{request.recipient}</strong>
                  </div>
                </div>

                <div style={{ padding: "14px", background: "var(--elev-2)", borderRadius: "var(--r-md)", fontSize: "13px" }}>
                  <span style={{ display: "block", color: "var(--text-3)", fontSize: "11px", textTransform: "uppercase", marginBottom: "4px" }}>
                    Preservation Purpose
                  </span>
                  <p style={{ margin: 0, color: "var(--text)", lineHeight: "1.5" }}>{request.purpose}</p>
                  <p className="mono" style={{ margin: "10px 0 0", fontSize: "11.5px", color: "var(--accent-2)" }}>
                    Attached Manifest: {request.evidence_manifest_id}
                  </p>
                </div>

                <div style={{
                  padding: "12px 14px",
                  borderRadius: "var(--r-md)",
                  background: "rgba(232, 178, 75, 0.08)",
                  border: "1px solid rgba(232, 178, 75, 0.25)",
                  fontSize: "12px",
                  color: "var(--gold)"
                }}>
                  <strong>Compliance Boundary:</strong> Supervisor approval generates an immutable audit record for court submission. It does not file automatic freezing or make live API calls to VASP entities.
                </div>

                <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                  <button className="btn-secondary" onClick={handleDraft}>
                    Draft / Reset Request
                  </button>
                  <button className="btn-primary" onClick={() => handleDecision("APPROVED")}>
                    Approve as Supervisor
                  </button>
                  <button className="btn-danger" onClick={() => handleDecision("REJECTED")}>
                    Reject Request
                  </button>
                </div>

                {note && (
                  <div style={{
                    padding: "12px 16px",
                    borderRadius: "var(--r-md)",
                    background: "rgba(55, 179, 148, 0.1)",
                    border: "1px solid var(--accent)",
                    color: "var(--accent-2)",
                    fontSize: "13px"
                  }}>
                    {note}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Audit Timeline */}
        <div>
          <div className="kestrel-panel" style={{ height: "100%" }}>
            <div className="kestrel-panel-head">
              <div>
                <h2>Audit Trail</h2>
                <p>Material investigator actions</p>
              </div>
            </div>

            <AuditTimeline events={audit} />
          </div>
        </div>
      </div>
    </div>
  );
}
