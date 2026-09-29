// @ts-nocheck
import React from "react";
import type { AuditEvent } from "../../types";
import { Badge } from "./Badge";

export function AuditTimeline({ events }: { events: AuditEvent[] }) {
  if (!events.length) {
    return <div style={{ color: "var(--text-3)", padding: "16px", fontSize: "13px" }}>No audit entries recorded yet.</div>;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      {events.map((event) => {
        const roleTone = event.actor_role === "SUPERVISOR" ? "green" : event.actor_role === "SYSTEM" ? "fixture" : "blue";
        return (
          <div
            key={event.audit_id}
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "14px",
              padding: "12px 14px",
              borderRadius: "var(--r-md)",
              background: "var(--elev-2)",
              border: "1px solid var(--line)"
            }}
          >
            <div style={{ marginTop: "2px" }}>
              <Badge tone={roleTone}>{event.actor_role}</Badge>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "3px", minWidth: 0, flex: 1 }}>
              <strong style={{ fontSize: "13.5px", color: "var(--text)" }}>{event.action.replace(/_/g, " ")}</strong>
              <span className="mono" style={{ fontSize: "11px", color: "var(--accent-2)" }}>{event.target_id}</span>
              <small style={{ fontSize: "11px", color: "var(--text-3)" }}>
                {event.timestamp.replace("T", " ").slice(0, 19)} · <span className="mono">{event.integrity_hash}</span>
              </small>
            </div>
          </div>
        );
      })}
    </div>
  );
}
