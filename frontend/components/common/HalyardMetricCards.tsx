import React from "react";

interface HalyardMetricCardsProps {
  onNavigate?: (route: string) => void;
  tracedAmount?: string;
  hopDepth?: number;
  vaspCount?: number;
  alertsCount?: number;
}

export function HalyardMetricCards({
  tracedAmount = "₹7,20,500",
  hopDepth = 4,
  vaspCount = 3,
  alertsCount = 18
}: HalyardMetricCardsProps) {
  return (
    <section className="telemetry-register" aria-label="Investigation telemetry register">
      <article className="telemetry-cell telemetry-volume">
        <div className="telemetry-cell-head">
          <span className="telemetry-icon" aria-hidden="true">
            <svg width="15" height="15" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <ellipse cx="9" cy="4.8" rx="5.4" ry="2.1" />
              <path d="M3.6 4.8v8.4c0 1.2 2.4 2.1 5.4 2.1s5.4-.9 5.4-2.1V4.8" />
              <path d="M3.6 9c0 1.2 2.4 2.1 5.4 2.1s5.4-.9 5.4-2.1" />
            </svg>
          </span>
          <h2>Traced Volume</h2>
        </div>
        <p>Confirmed on-chain movement</p>
        <strong className="telemetry-value">{tracedAmount}</strong>
        <TelemetryBars label="Hourly traced volume distribution" values={[12, 18, 10, 24, 42, 35, 58, 82, 94, 76, 45, 22]} start="00:00 UTC" end="24:00 UTC" />
      </article>

      <article className="telemetry-cell">
        <div className="telemetry-cell-head">
          <span className="telemetry-icon" aria-hidden="true">
            <svg width="15" height="15" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="6.4" cy="11.6" r="3.1" />
              <path d="M8.6 9.4L14.6 3.4M11 7l2 2M12.8 5.2l2 2" />
            </svg>
          </span>
          <h2>Graph Depth</h2>
        </div>
        <p>Hop traversal reached</p>
        <strong className="telemetry-value">{hopDepth} Hops</strong>
        <TelemetryBars label="Hop depth distribution" values={[90, 75, 60, 40, 15, 0, 0, 0, 0, 0, 0, 0]} start="H0 Root" end="H5 Boundary" />
      </article>

      <article className="telemetry-cell">
        <div className="telemetry-cell-head">
          <span className="telemetry-icon" aria-hidden="true">
            <svg width="15" height="15" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3.6" width="12" height="3.4" rx="1.2" />
              <path d="M4.2 7v6.4c0 .7.6 1.2 1.2 1.2h7.2c.6 0 1.2-.5 1.2-1.2V7M7.4 10.2h3.2" />
            </svg>
          </span>
          <h2>VASP Targets</h2>
        </div>
        <p>Attributed candidate clusters</p>
        <strong className="telemetry-value">{vaspCount} Clusters</strong>
        <TelemetryBars label="VASP cluster activity" values={[30, 48, 72, 92, 85, 64, 40, 20, 15, 0, 0, 0]} start="Deposit" end="Internal Hot" />
      </article>

      <article className="telemetry-cell telemetry-risk">
        <div className="telemetry-cell-head">
          <span className="telemetry-icon" aria-hidden="true">
            <svg width="15" height="15" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9.8 2.4L4.6 9.8h3.9l-.9 5.8 5.8-7.6H9.2Z" />
            </svg>
          </span>
          <h2>Risk Signals</h2>
        </div>
        <p>Alerts requiring triage</p>
        <strong className="telemetry-value">{alertsCount} Flags</strong>
        <TelemetryBars label="Alert velocity" values={[10, 15, 30, 55, 80, 70, 85, 90, 60, 40, 25, 15]} start="Low" end="Critical" />
      </article>
    </section>
  );
}

function TelemetryBars({ label, values, start, end }: { label: string; values: number[]; start: string; end: string }) {
  return (
    <div className="telemetry-chart">
      <div className="telemetry-bars" role="img" aria-label={label}>
        {values.map((value, index) => <span key={`${label}-${index}`} style={{ height: `${value}%` }} />)}
      </div>
      <div className="telemetry-axis"><span>{start}</span><span>{end}</span></div>
    </div>
  );
}
