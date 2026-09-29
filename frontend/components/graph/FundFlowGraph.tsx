// @ts-nocheck
import React, { useState } from "react";
import type { GraphEdge, GraphNode } from "../../types";
import { Badge } from "../common/Badge";

interface FundFlowGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedId?: string;
  activeEdgeId?: string;
  onNode: (node: GraphNode) => void;
  onEdge: (edge: GraphEdge) => void;
}

export function FundFlowGraph({
  nodes,
  edges,
  selectedId,
  activeEdgeId,
  onNode,
  onEdge
}: FundFlowGraphProps) {
  const [fullScreen, setFullScreen] = useState(false);
  const totalValue = edges.reduce((sum, edge) => sum + edge.value_inr, 0);

  const graphNodes = nodes.filter((node) =>
    edges.some((edge) => edge.source === node.id || edge.target === node.id)
  );

  const center = { x: 560, y: 360 };
  const positions = computeCircularPositions(graphNodes, edges, center);

  return (
    <div className={`graph-shell ${fullScreen ? "fullscreen-graph" : ""}`}>
      <div className="graph-toolbar">
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span className="badge green">CIRCULAR TOPOLOGY</span>
          <span style={{ fontSize: "12px", color: "var(--text-3)" }}>
            Radial fund-flow · click nodes or edges for forensic drilldown
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <strong className="mono" style={{ fontSize: "13px", color: "var(--gold)", letterSpacing: "-0.01em" }}>
            ₹{totalValue.toLocaleString("en-IN")} <span style={{ fontSize: "11px", fontWeight: 500, color: "var(--text-3)", textTransform: "uppercase" }}>traced</span>
          </strong>
          <button
            className="btn-secondary"
            style={{ height: "30px", padding: "0 12px", fontSize: "11.5px", display: "inline-flex", alignItems: "center", gap: "6px" }}
            onClick={() => setFullScreen(!fullScreen)}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
              <path d="M15 3H21V9M9 21H3V15M21 3L14 10M3 21L10 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span>{fullScreen ? "Exit Fullscreen" : "Fullscreen"}</span>
          </button>
        </div>
      </div>

      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        <svg
          className="circular-graph"
          viewBox="0 0 1120 720"
          role="img"
          aria-label="Circular fund-flow network graph"
          style={{ width: "100%", height: fullScreen ? "100%" : "auto" }}
        >
          <defs>
            <marker
              id="arrow-confirmed-kestrel"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="7"
              markerHeight="7"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#4F9FD1" />
            </marker>
            <marker
              id="arrow-heuristic-kestrel"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="7"
              markerHeight="7"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#E8B24B" />
            </marker>
            <radialGradient id="network-glow-kestrel" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#37B394" stopOpacity="0.22" />
              <stop offset="50%" stopColor="#1C8A72" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#08090B" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Background Stage Glow & Hop Rings */}
          <circle cx={center.x} cy={center.y} r="320" fill="url(#network-glow-kestrel)" />
          <circle className="network-ring" cx={center.x} cy={center.y} r="105" />
          <circle className="network-ring" cx={center.x} cy={center.y} r="205" />
          <circle className="network-ring outer" cx={center.x} cy={center.y} r="305" />

          {/* Ring Labels */}
          <text x={center.x} y={center.y - 110} fill="var(--text-3)" fontSize="10" textAnchor="middle">H1 · Hop Distance 1</text>
          <text x={center.x} y={center.y - 210} fill="var(--text-3)" fontSize="10" textAnchor="middle">H2 · Aggregation Orbit</text>
          <text x={center.x} y={center.y - 310} fill="var(--text-3)" fontSize="10" textAnchor="middle">H3–H5 · Downstream Boundary</text>

          {/* Edges */}
          {edges.map((edge) => {
            const source = positions[edge.source];
            const target = positions[edge.target];
            if (!source || !target) return null;

            const selected = selectedId === edge.id || activeEdgeId === edge.id;
            const bend = getArcBend(source, target, center, edge.hop);
            const mid = getQuadraticPoint(source, bend, target, 0.5);

            return (
              <g
                key={edge.id}
                className={`flow-edge ${selected ? "selected" : ""}`}
                onClick={() => onEdge(edge)}
              >
                <path
                  d={`M ${source.x} ${source.y} Q ${bend.x} ${bend.y} ${target.x} ${target.y}`}
                  className={edge.style === "DASHED" ? "dashed" : ""}
                  markerEnd={edge.style === "DASHED" ? "url(#arrow-heuristic-kestrel)" : "url(#arrow-confirmed-kestrel)"}
                />
                <foreignObject x={mid.x - 56} y={mid.y - 18} width="112" height="36">
                  <button
                    className={`edge-pill ${edge.style === "DASHED" ? "heuristic" : ""}`}
                    onClick={(event) => {
                      event.stopPropagation();
                      onEdge(edge);
                    }}
                  >
                    <span>{edge.asset}</span>
                    <strong>₹{Math.round(edge.value_inr / 1000)}k</strong>
                  </button>
                </foreignObject>
              </g>
            );
          })}

          {/* Nodes */}
          {graphNodes.map((node) => {
            const pos = positions[node.id];
            if (!pos) return null;

            const isReported = node.id === "W1" || node.type === "REPORTED_WALLET";
            const radius = isReported ? 44 : node.type === "AGGREGATION_WALLET" ? 42 : node.type.includes("VASP") ? 38 : 34;
            const isSelected = selectedId === node.id;

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                className={`flow-node ${isSelected ? "selected" : ""}`}
                onClick={() => onNode(node)}
              >
                <circle
                  r={radius}
                  fill={isReported ? "#162B25" : node.type.includes("VASP") ? "#17231E" : "#12151B"}
                  stroke={isReported ? "var(--accent-2)" : node.type.includes("HEURISTIC") ? "var(--gold)" : "var(--accent)"}
                />
                <text y="-5">{node.label}</text>
                <text y="13" className="mono">{node.id} · {node.chain}</text>
                <text y={radius + 18} className="node-type">
                  {node.type.replace(/_/g, " ")}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "10px 20px",
        background: "var(--elev-1)",
        borderTop: "1px solid var(--line)",
        fontSize: "12px",
        color: "var(--text-3)"
      }}>
        <div style={{ display: "flex", gap: "16px" }}>
          <span><i style={{ display: "inline-block", width: "12px", height: "3px", background: "#4F9FD1", marginRight: "6px" }} />Confirmed Flow</span>
          <span><i style={{ display: "inline-block", width: "12px", height: "3px", borderTop: "2px dashed #E8B24B", marginRight: "6px" }} />Heuristic Exit (Mixer)</span>
        </div>
        <span>{edges.length} active edges rendered · Deterministic Fixture Graph</span>
      </div>
    </div>
  );
}

function computeCircularPositions(
  nodes: GraphNode[],
  edges: GraphEdge[],
  center: { x: number; y: number }
) {
  const depth = new Map<string, number>();
  nodes.forEach((node) => depth.set(node.id, node.id === "W1" ? 0 : 1));

  for (let pass = 0; pass < 8; pass += 1) {
    edges.forEach((edge) => {
      const nextDepth = Math.max(depth.get(edge.target) ?? 0, (depth.get(edge.source) ?? 0) + 1);
      depth.set(edge.target, Math.min(6, nextDepth));
    });
  }

  const positions: Record<string, { x: number; y: number }> = {};
  const centerNode =
    nodes.find((node) => node.type === "AGGREGATION_WALLET") ??
    nodes.find((node) => node.id === "W5") ??
    nodes[0];

  if (centerNode) {
    positions[centerNode.id] = center;
  }

  const orbitNodes = nodes
    .filter((node) => node.id !== centerNode?.id)
    .sort((a, b) => (depth.get(a.id) ?? 0) - (depth.get(b.id) ?? 0) || a.id.localeCompare(b.id));

  const radiusByType: Record<string, number> = {
    REPORTED_WALLET: 245,
    INTERMEDIARY_WALLET: 205,
    BRIDGE_CONTRACT: 150,
    DEX_POOL: 178,
    MIXER_BOUNDARY: 262,
    HEURISTIC_EXIT: 300,
    VASP_CANDIDATE: 284,
    VASP_DEPOSIT: 304,
    CROSS_CHAIN_DESTINATION: 240
  };

  orbitNodes.forEach((node, index) => {
    const count = orbitNodes.length || 1;
    const angle = -Math.PI / 2 + (index * 2 * Math.PI) / count;
    const radius = radiusByType[node.type] ?? Math.min(305, 150 + (depth.get(node.id) ?? 1) * 42);
    positions[node.id] = {
      x: center.x + Math.cos(angle) * radius,
      y: center.y + Math.sin(angle) * radius
    };
  });

  return positions;
}

function getArcBend(
  source: { x: number; y: number },
  target: { x: number; y: number },
  center: { x: number; y: number },
  hop: number
) {
  const midX = (source.x + target.x) / 2;
  const midY = (source.y + target.y) / 2;
  const dx = midX - center.x;
  const dy = midY - center.y;
  const length = Math.hypot(dx, dy) || 1;
  const pull = hop % 2 === 0 ? 46 : -34;
  return {
    x: midX + (dy / length) * pull,
    y: midY - (dx / length) * pull
  };
}

function getQuadraticPoint(
  source: { x: number; y: number },
  bend: { x: number; y: number },
  target: { x: number; y: number },
  t: number
) {
  const mt = 1 - t;
  return {
    x: mt * mt * source.x + 2 * mt * t * bend.x + t * t * target.x,
    y: mt * mt * source.y + 2 * mt * t * bend.y + t * t * target.y
  };
}
