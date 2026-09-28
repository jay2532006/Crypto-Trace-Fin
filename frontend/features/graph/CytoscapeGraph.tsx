'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape, { Core, EventObject } from 'cytoscape';
import { ZoomIn, ZoomOut, Maximize2, RefreshCw, Layers, ShieldAlert, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useGraphStore } from '@/stores/graph-store';
import { formatAddress, formatCrypto } from '@/lib/utils';
import type { GraphNode, GraphEdge } from '@/types/domain';

interface CytoscapeGraphProps {
  nodes?: GraphNode[];
  edges?: GraphEdge[];
  onNodeSelect?: (node: GraphNode | null) => void;
  height?: string;
  interactive?: boolean;
}

export const CytoscapeGraph: React.FC<CytoscapeGraphProps> = ({
  nodes: propNodes,
  edges: propEdges,
  onNodeSelect,
  height = '620px',
  interactive = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [layoutName, setLayoutName] = useState<'breadthfirst' | 'cose' | 'concentric'>('breadthfirst');
  const [selectedEntity, setSelectedEntity] = useState<GraphNode | null>(null);

  const setSelectedStoreNode = useGraphStore((s) => s.setSelectedNode);

  const activeNodes: GraphNode[] = propNodes || [];
  const activeEdges: GraphEdge[] = propEdges || [];

  const initCytoscape = useCallback(() => {
    if (!containerRef.current) return;

    // Destroy existing instance if any
    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    const elements: cytoscape.ElementDefinition[] = [];

    // Map domain nodes to Cytoscape elements
    activeNodes.forEach((node: GraphNode) => {
      let nodeColor = '#3B82F6'; // Default primary blue
      let nodeBorderColor = '#60A5FA';
      let shape: cytoscape.Css.NodeShape = 'ellipse';

      const typeStr = (node.type || '').toUpperCase();
      if (typeStr === 'SUSPECT') {
        nodeColor = '#DC2626'; // Red
        nodeBorderColor = '#F87171';
        shape = 'diamond';
      } else if (typeStr === 'VASP') {
        nodeColor = '#1D4ED8'; // Dark Navy Blue
        nodeBorderColor = '#93C5FD';
        shape = 'round-rectangle';
      } else if (typeStr === 'MIXER') {
        nodeColor = '#D97706'; // Amber / Warning
        nodeBorderColor = '#EF4444'; // Red terminal marker border
        shape = 'hexagon';
      } else if (typeStr === 'MULE') {
        nodeColor = '#8B5CF6'; // Purple
        nodeBorderColor = '#C4B5FD';
        shape = 'ellipse';
      }

      elements.push({
        group: 'nodes',
        data: {
          id: node.id,
          label: node.label || formatAddress(node.address),
          address: node.address,
          type: node.type,
          color: nodeColor,
          borderColor: nodeBorderColor,
          shape: shape,
          balance: node.balance,
          riskScore: node.risk_score,
          vaspName: node.vasp_name,
          raw: node,
        },
      });
    });

    // Map domain edges to Cytoscape elements
    activeEdges.forEach((edge: GraphEdge) => {
      const isMixerBoundary = edge.is_mixer_boundary || edge.edge_type === 'MIXER_EXIT' || edge.edge_type === 'MIXER_ENTRY';
      const isPeel = edge.edge_type === 'PEELING_CHAIN';

      let lineStyle: cytoscape.Css.LineStyle = 'solid';
      let lineColor = '#4B5563'; // Neutral gray
      const isBridge = edge.edge_type === 'BRIDGE' || (edge as any).is_cross_chain || (edge as any).link_type === 'PROVEN';
      const isHeuristicBridge = (edge as any).link_type === 'HEURISTIC_CORRELATION';
      if (isMixerBoundary) {
        lineStyle = 'dashed';
        lineColor = '#F59E0B'; // Amber dashed
      } else if (isPeel) {
        lineStyle = 'dashed';
        lineColor = '#8B5CF6'; // Purple dashed
      } else if (isBridge) {
        lineStyle = 'solid';
        lineColor = '#06B6D4'; // Solid cyan for PROVEN bridge
      } else if (isHeuristicBridge) {
        lineStyle = 'dashed';
        lineColor = '#94A3B8'; // Dashed grey for heuristic bridge
      }

      elements.push({
        group: 'edges',
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          amount: edge.amount,
          token: edge.token || 'ETH',
          lineStyle: lineStyle,
          lineColor: lineColor,
          txHash: edge.tx_hash,
          isMixerBoundary,
          raw: edge,
        },
      });
    });

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(color)',
            'border-color': 'data(borderColor)',
            'border-width': 2,
            'label': 'data(label)',
            'color': '#E2E8F0',
            'font-size': '11px',
            'font-weight': 600,
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'shape': 'data(shape)' as any,
            'width': 44,
            'height': 44,
            'text-background-color': '#070F1E',
            'text-background-opacity': 0.85,
            'text-background-padding': '3px',
            'text-background-shape': 'roundrectangle',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#38BDF8',
          } as any,
        },
        {
          selector: 'edge',
          style: {
            'width': 2.5,
            'line-color': 'data(lineColor)',
            'line-style': 'data(lineStyle)' as any,
            'target-arrow-color': 'data(lineColor)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.2,
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#38BDF8',
            'target-arrow-color': '#38BDF8',
            'width': 4,
          },
        },
      ],
      layout: {
        name: layoutName,
        directed: true,
        padding: 50,
        spacingFactor: 1.25,
      } as any,
      userZoomingEnabled: interactive,
      userPanningEnabled: interactive,
      boxSelectionEnabled: false,
    });

    cy.on('tap', 'node', (evt: EventObject) => {
      const nodeData = evt.target.data('raw') as GraphNode;
      setSelectedEntity(nodeData);
      setSelectedStoreNode(nodeData as any);
      if (onNodeSelect) {
        onNodeSelect(nodeData);
      }
    });

    cy.on('tap', (evt: EventObject) => {
      if (evt.target === cy) {
        setSelectedEntity(null);
        setSelectedStoreNode(null);
        if (onNodeSelect) {
          onNodeSelect(null);
        }
      }
    });

    cyRef.current = cy;
  }, [activeNodes, activeEdges, layoutName, interactive, onNodeSelect, setSelectedStoreNode]);

  useEffect(() => {
    initCytoscape();
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [initCytoscape]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit(undefined, 40);

  return (
    <div className="relative w-full rounded-xl border border-navy-800 bg-[#070f1e] overflow-hidden shadow-2xl">
      {/* Top Toolbar */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 bg-navy-900/90 backdrop-blur-md px-3 py-2 rounded-lg border border-navy-700/60 shadow-lg">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mr-2 flex items-center gap-1.5">
          <Layers className="h-3.5 w-3.5 text-blue-400" />
          Layout
        </span>
        <button
          onClick={() => setLayoutName('breadthfirst')}
          className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
            layoutName === 'breadthfirst'
              ? 'bg-blue-600 text-white'
              : 'text-slate-300 hover:bg-navy-800'
          }`}
        >
          Flow
        </button>
        <button
          onClick={() => setLayoutName('cose')}
          className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
            layoutName === 'cose'
              ? 'bg-blue-600 text-white'
              : 'text-slate-300 hover:bg-navy-800'
          }`}
        >
          Force-Directed
        </button>
        <button
          onClick={() => setLayoutName('concentric')}
          className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
            layoutName === 'concentric'
              ? 'bg-blue-600 text-white'
              : 'text-slate-300 hover:bg-navy-800'
          }`}
        >
          Concentric
        </button>
      </div>

      {/* Zoom / Viewport Controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-1.5 bg-navy-900/90 backdrop-blur-md p-1.5 rounded-lg border border-navy-700/60 shadow-lg">
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="p-1.5 text-slate-300 hover:text-white hover:bg-navy-800 rounded transition-colors"
        >
          <ZoomIn className="h-4 w-4" />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="p-1.5 text-slate-300 hover:text-white hover:bg-navy-800 rounded transition-colors"
        >
          <ZoomOut className="h-4 w-4" />
        </button>
        <button
          onClick={handleFit}
          title="Fit View"
          className="p-1.5 text-slate-300 hover:text-white hover:bg-navy-800 rounded transition-colors"
        >
          <Maximize2 className="h-4 w-4" />
        </button>
        <button
          onClick={initCytoscape}
          title="Reset Layout"
          className="p-1.5 text-slate-300 hover:text-white hover:bg-navy-800 rounded transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 flex flex-wrap items-center gap-3 bg-navy-900/90 backdrop-blur-md px-3 py-2 rounded-lg border border-navy-700/60 shadow-lg text-[11px] font-medium text-slate-300">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rotate-45 bg-red-600 border border-red-400 inline-block" />
          <span>Suspect Seed</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-blue-700 border border-blue-400 inline-block" />
          <span>VASP Entity</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-amber-600 border border-amber-400 inline-block" />
          <span>Mixer Boundary</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-purple-600 border border-purple-400 inline-block" />
          <span>Mule Wallet</span>
        </div>
        <div className="flex items-center gap-1.5 pl-2 border-l border-navy-700">
          <span className="w-4 border-t-2 border-slate-500 inline-block" />
          <span>On-Chain Hop</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-4 border-t-2 border-dashed border-amber-400 inline-block" />
          <span>Mixer Boundary (Heuristic)</span>
        </div>
      </div>

      {/* Cytoscape Canvas Container */}
      <div
        ref={containerRef}
        style={{ height }}
        className="w-full h-full cursor-grab active:cursor-grabbing"
      />

      {/* Selected Entity Mini-Card */}
      {selectedEntity && (
        <div className="absolute bottom-4 right-4 z-10 w-72 bg-navy-900/95 backdrop-blur-lg p-3.5 rounded-xl border border-blue-500/40 shadow-2xl animate-fade-in text-xs">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-navy-800">
            <span className="font-semibold text-slate-200 uppercase tracking-wide flex items-center gap-1.5">
              {selectedEntity.type === 'VASP' ? (
                <Building2 className="h-3.5 w-3.5 text-blue-400" />
              ) : (
                <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />
              )}
              {selectedEntity.type} Node
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-navy-800 text-slate-400 font-mono">
              Risk: {selectedEntity.risk_score ? `${Math.round(selectedEntity.risk_score * 100)}%` : 'N/A'}
            </span>
          </div>
          <div className="space-y-1.5 font-mono text-[11px]">
            <div>
              <span className="text-slate-500">Address: </span>
              <span className="text-blue-300 break-all">{selectedEntity.address}</span>
            </div>
            {selectedEntity.vasp_name && (
              <div>
                <span className="text-slate-500">Entity: </span>
                <span className="text-emerald-400 font-sans font-semibold">{selectedEntity.vasp_name}</span>
              </div>
            )}
            {selectedEntity.balance !== undefined && (
              <div>
                <span className="text-slate-500">Observed Balance: </span>
                <span className="text-slate-200">{formatCrypto(selectedEntity.balance, 'ETH')}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
