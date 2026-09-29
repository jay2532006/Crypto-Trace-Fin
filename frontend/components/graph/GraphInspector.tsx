// @ts-nocheck
import React from "react";
import type { GraphEdge, GraphNode } from "../../types";
import { Badge } from "../common/Badge";

interface GraphInspectorProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedId?: string;
  activeEdgeId?: string;
  onNode: (node: GraphNode) => void;
  onEdge: (edge: GraphEdge) => void;
}

export function GraphInspector({ nodes, edges, selectedId, activeEdgeId, onNode, onEdge }: GraphInspectorProps) {
  return (
    <aside className="graph-inspector" aria-label="Fund-flow quick inspector">
      <div className="inspector-head">
        <div>
          <strong>Fund-Flow Quick Inspector</strong>
          <p>Select an entity or transfer edge to open its forensic dossier.</p>
        </div>
        <Badge tone="green">{nodes.length} Nodes · {edges.length} Edges</Badge>
      </div>

      <div className="inspector-section">
        <span className="section-kicker">Key Entity Nodes</span>
        <div className="inspector-node-grid">
          {nodes.slice(0, 8).map((node) => (
            <button key={node.id} className={`inspector-node ${selectedId === node.id ? "selected" : ""}`} onClick={() => onNode(node)}>
              <strong>{node.label}</strong>
              <small className="mono">{node.id} · {node.chain}</small>
            </button>
          ))}
        </div>
      </div>

      <div className="inspector-section">
        <span className="section-kicker">Transfers & Heuristic Leads</span>
        <div className="inspector-edge-list">
          {edges.map((edge) => {
            const isSelected = selectedId === edge.id || activeEdgeId === edge.id;
            return (
              <button key={edge.id} className={`inspector-edge ${isSelected ? "selected" : ""}`} onClick={() => onEdge(edge)}>
                <span className="inspector-edge-copy">
                  <Badge tone={edge.style === "DASHED" ? "heuristic" : "blue"}>{edge.style === "DASHED" ? "LEAD" : `H${edge.hop}`}</Badge>
                  <span className="mono">{edge.source} → {edge.target}</span>
                </span>
                <strong>₹{Math.round(edge.value_inr / 1000)}k</strong>
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
