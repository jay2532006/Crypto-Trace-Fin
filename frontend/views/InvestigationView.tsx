// @ts-nocheck
import React, { useState, useEffect } from "react";
import type {
  Case,
  GraphEdge,
  GraphNode,
  PatternFinding,
  TraceLimits,
  TraceResult,
  Transaction,
  VASPCluster
} from "../types";
import { mockApi } from "../services/mockApi";
import { Badge } from "../components/common/Badge";
import { KpiBanner } from "../components/common/KpiBanner";
import { FundFlowGraph } from "../components/graph/FundFlowGraph";
import { GraphInspector } from "../components/graph/GraphInspector";
import { RapidFlowStrip } from "../components/graph/RapidFlowStrip";
import { SkeletonLoader, ErrorNotice } from "../components/common/StateFeedback";
import { formatInr, formatWallet, formatTechnicalId } from "../utils/formatters";

interface InvestigationViewProps {
  activeCase: Case;
  setDrawer: (drawer: any) => void;
  openTransaction: (txHash: string) => Promise<void>;
}

const defaultLimits: TraceLimits = {
  max_hops: 5,
  time_window_hours: 72,
  minimum_value_inr: 5000,
  max_outflows: 10,
  max_nodes: 100,
  timeout_seconds: 15
};

export function InvestigationView({ activeCase, setDrawer, openTransaction }: InvestigationViewProps) {
  const [limits, setLimits] = useState<TraceLimits>(defaultLimits);
  const [runningStage, setRunningStage] = useState<string>("READY");
  const [hopFilter, setHopFilter] = useState(6);
  const [isTracing, setIsTracing] = useState(false);
  const [revealedEdgeCount, setRevealedEdgeCount] = useState<number | null>(null);
  const [selectedGraphItem, setSelectedGraphItem] = useState<string>("E1");
  const [flowIndex, setFlowIndex] = useState(0);

  const [trace, setTrace] = useState<TraceResult | null>(null);
  const [graph, setGraph] = useState<{ nodes: GraphNode[]; edges: GraphEdge[] } | null>(null);
  const [typologies, setTypologies] = useState<PatternFinding[]>([]);
  const [vasps, setVasps] = useState<VASPCluster[]>([]);
  const [risk, setRisk] = useState<any>(null);
  const [recovery, setRecovery] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([
      mockApi.getTrace(),
      mockApi.getGraph(),
      mockApi.getTypologies(),
      mockApi.getVaspCandidates(),
      mockApi.getRisk(),
      mockApi.getRecovery(),
      mockApi.getRecommendations(),
      mockApi.getTransactions({ limit: 9 })
    ])
      .then(([tRes, gRes, typRes, vRes, rRes, recRes, recmRes, txRes]) => {
        if (!active) return;
        setTrace(tRes.data);
        setGraph(gRes.data);
        setTypologies(typRes.data);
        setVasps(vRes.data);
        setRisk(rRes.data);
        setRecovery(recRes.data);
        setRecommendations(recmRes.data);
        setTransactions(txRes.data);
      })
      .catch((err) => {
        if (active) setError(err.message || "Failed to load investigation dataset.");
      })
      .finally(() => active && setLoading(false));

    return () => { active = false; };
  }, [activeCase.case_id]);

  const visibleEdges = (graph?.edges ?? []).filter((edge) => edge.hop <= hopFilter);
  const displayedEdges = revealedEdgeCount === null ? visibleEdges : visibleEdges.slice(0, revealedEdgeCount);
  const activeFlowTx = transactions.length ? transactions[flowIndex % transactions.length] : null;
  const activeFlowEdge = activeFlowTx
    ? visibleEdges.find((edge) => activeFlowTx.tx_hash.includes(edge.tx_hash.replace("...", "").slice(0, 5)) || edge.tx_hash.includes(activeFlowTx.tx_hash.slice(0, 5)))
    : undefined;

  const runTrace = async () => {
    setIsTracing(true);
    setRevealedEdgeCount(0);
    setSelectedGraphItem("W1");

    const stages = ["FETCH", "VALIDATE", "EXTRACT", "NORMALIZE", "DEDUPLICATE", "PERSIST", "COMMIT", "ADVANCE"];
    for (let i = 0; i < visibleEdges.length; i += 1) {
      const stage = stages[i % stages.length];
      setRunningStage(`${stage} → Graph node discovery ${i + 1}/${visibleEdges.length}`);
      setRevealedEdgeCount(i + 1);
      setSelectedGraphItem(visibleEdges[i].id);
      await new Promise((resolve) => window.setTimeout(resolve, 260));
    }

    setRunningStage("ADVANCE → Synchronizing VASP & Typology intelligence");
    const response = await mockApi.runTrace(limits);
    setTrace(response.data);
    setRevealedEdgeCount(null);
    setIsTracing(false);
    setRunningStage("READY · PARTIAL COVERAGE");
  };

  const selectNode = (node: GraphNode) => {
    setSelectedGraphItem(node.id);
    setDrawer({ kind: "node", node });
  };

  const selectEdge = async (edge: GraphEdge) => {
    setSelectedGraphItem(edge.id);
    const tx = edge.tx_hash.startsWith("HEURISTIC") ? undefined : (await mockApi.getTransaction(edge.tx_hash)).data;
    setDrawer({ kind: "edge", edge, tx });
  };

  if (loading) return <SkeletonLoader text="Initializing bounded graph and typology intelligence..." />;
  if (error) return <ErrorNotice message={error} />;

  return (
    <div className="view-stack investigation-view">
      <section className="case-context-band">
        <div>
          <span className="section-kicker text-accent">Investigation Workstation</span>
          <h2>{activeCase.case_id} · <span className="table-muted">{activeCase.fraud_type.replace(/_/g, " ")}</span></h2>
          <p className="mono text-accent">Reported Wallet: {formatWallet(activeCase.reported_wallet)}</p>
        </div>
        <div className="inline-cluster">
          <Badge tone={activeCase.source_badge}>{activeCase.source_badge}</Badge>
          <Badge tone="partial">{activeCase.data_coverage}</Badge>
          <span className="badge neutral">Deterministic Target</span>
        </div>
      </section>

      <KpiBanner
        reportedWallet={activeCase.reported_wallet}
        caseId={activeCase.case_id}
        recovery={recovery}
        risk={risk}
        attributionBand={vasps[0]?.confidence_band || "HIGH"}
        traceCoverage={trace?.coverage || "PARTIAL"}
        dataCompletenessPct={(trace as any)?.data_completeness_pct}
        earliestTransactionDate={(trace as any)?.earliest_transaction_date}
        timeWindowTruncations={(trace as any)?.time_window_truncations ?? 0}
        partialResult={(trace as any)?.partial_result ?? false}
      />

      <RapidFlowStrip
        rows={transactions}
        activeIndex={flowIndex}
        onSelect={setFlowIndex}
        onOpen={openTransaction}
        isPlaying={false}
      />

      <div className="investigation-workbench">
        <div className="trace-controls">
          <section className="kestrel-panel trace-control-panel">
            <div className="kestrel-panel-head">
              <div><h2>Bounded Trace Scope</h2><p>Stage: {runningStage}</p></div>
              <Badge tone={isTracing ? "amber" : "green"}>{isTracing ? "TRACING" : "READY"}</Badge>
            </div>

            <div className="trace-limit-grid">
              <label className="form-label">Max Hops<input type="number" className="form-input" value={limits.max_hops} onChange={(e) => setLimits({ ...limits, max_hops: Number(e.target.value) })} /></label>
              <label className="form-label">Window Hours<input type="number" className="form-input" value={limits.time_window_hours} onChange={(e) => setLimits({ ...limits, time_window_hours: Number(e.target.value) })} /></label>
              <label className="form-label">Min INR Floor<input type="number" className="form-input" value={limits.minimum_value_inr} onChange={(e) => setLimits({ ...limits, minimum_value_inr: Number(e.target.value) })} /></label>
              <label className="form-label">Max Outflows<input type="number" className="form-input" value={limits.max_outflows} onChange={(e) => setLimits({ ...limits, max_outflows: Number(e.target.value) })} /></label>
              <label className="form-label">Max Nodes<input type="number" className="form-input" value={limits.max_nodes} onChange={(e) => setLimits({ ...limits, max_nodes: Number(e.target.value) })} /></label>
              <label className="form-label">Timeout Sec<input type="number" className="form-input" value={limits.timeout_seconds} onChange={(e) => setLimits({ ...limits, timeout_seconds: Number(e.target.value) })} /></label>
            </div>

            <div className="range-control">
              <div className="range-control-head"><span>Graph Hop Filter</span><strong className="mono text-accent">≤ {hopFilter} hops</strong></div>
              <input type="range" min="1" max="6" value={hopFilter} onChange={(e) => setHopFilter(Number(e.target.value))} />
            </div>

            <div className="action-stack">
              <button className="btn-primary" disabled={isTracing} onClick={() => void runTrace()}>{isTracing ? "Executing Bounded Trace..." : "Run Bounded Trace"}</button>
              {trace && (
                <div className="trace-receipt">
                  <div className="metric-line"><span>Nodes / Edges</span><strong>{trace.node_count} nodes · {trace.edge_count} edges</strong></div>
                  <div className="metric-line"><span>Max Depth</span><strong>{trace.max_depth_reached} hops</strong></div>
                  <div className="metric-line"><span>Termination</span><Badge tone="amber">{trace.termination_reason}</Badge></div>
                  <div className="metric-line"><span>Coverage</span><Badge tone="partial">{trace.coverage}</Badge></div>
                  {(trace as any)?.data_completeness_pct !== undefined && (
                    <div className="metric-line" title={`We confirmed ${Math.round((trace as any).data_completeness_pct)}% of the fund flow from public blockchain data.`}>
                      <span>Data Completeness</span>
                      <strong style={{
                        color: (trace as any).data_completeness_pct >= 85 ? "var(--green, #22c55e)" :
                               (trace as any).data_completeness_pct >= 65 ? "var(--amber, #f59e0b)" : "var(--red, #ef4444)"
                      }}>
                        {Math.round((trace as any).data_completeness_pct)}%
                      </strong>
                    </div>
                  )}
                  {(trace as any)?.ui_warning_banner && (
                    <div className="metric-line" style={{ color: "var(--amber, #f59e0b)", fontSize: "0.78rem", marginTop: "4px" }}>
                      ⚠ {(trace as any).ui_warning_banner}
                    </div>
                  )}
                  {(trace as any)?.earliest_transaction_date && (
                    <div className="metric-line">
                      <span>Data Horizon</span>
                      <span className="mono" style={{ fontSize: "0.78rem" }}>{(trace as any).earliest_transaction_date}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </section>
        </div>

        <div className="graph-workbench-center">
          <section className="kestrel-panel">
            <FundFlowGraph
              nodes={graph?.nodes ?? []}
              edges={displayedEdges}
              selectedId={selectedGraphItem}
              activeEdgeId={activeFlowEdge?.id}
              onNode={selectNode}
              onEdge={selectEdge}
            />
          </section>
        </div>

        <div className="graph-workbench-inspector">
          <GraphInspector
            nodes={graph?.nodes ?? []}
            edges={displayedEdges}
            selectedId={selectedGraphItem}
            activeEdgeId={activeFlowEdge?.id}
            onNode={selectNode}
            onEdge={selectEdge}
          />
        </div>
      </div>

      <div className="kestrel-grid-3 intelligence-grid">
        <section className="kestrel-panel">
          <div className="kestrel-panel-head"><div><h2>Typology Detection</h2><p>Rule-versioned fraud behavioral indicators</p></div></div>
          <div className="stack-list">
            {typologies.slice(0, 5).map((finding) => (
              <button key={finding.finding_id} className="list-item-button" onClick={() => setDrawer({ kind: "finding", finding })}>
                <div className="list-item-head"><strong>{finding.pattern_type}</strong>{finding.india_specific && <Badge tone="india">India Pattern</Badge>}</div>
                <div className="list-item-meta"><span>Confidence: <strong className="text-gold">{finding.confidence}</strong></span><span className="mono">{finding.rule_version}</span></div>
              </button>
            ))}
          </div>
        </section>

        <section className="kestrel-panel">
          <div className="kestrel-panel-head"><div><h2>VASP Intelligence</h2><p>Candidate exit clustering, not ownership proof</p></div></div>
          <div className="stack-list">
            {vasps.map((candidate, idx) => {
              const labelStatus = candidate.label_status || "INFERRED";
              const conf = typeof candidate.confidence === "number" ? candidate.confidence : 0.8;
              const hop = candidate.hop_distance ?? 1;
              const addr = candidate.address || candidate.hot_wallet || "";
              const name = candidate.name || candidate.vasp_name || `Candidate ${idx + 1}`;
              return (
                <button key={candidate.candidate_id || `cand-${idx}`} className="list-item-button list-item-split" onClick={() => setDrawer({ kind: "vasp", candidate })}>
                  <div><strong>{name}</strong><span className="mono table-muted">{formatTechnicalId(addr, 12, 4)}</span></div>
                  <div className="list-item-align-right"><Badge tone={labelStatus.toLowerCase()}>{labelStatus}</Badge><span className="text-accent">{Math.round(conf * 100)}% · hop {hop}</span></div>
                </button>
              );
            })}
          </div>
        </section>

        <section className="kestrel-panel">
          <div className="kestrel-panel-head"><div><h2>Advisory Actions</h2><p>Recommended investigative follow-ups</p></div></div>
          <div className="stack-list">
            {recommendations.map((rec) => (
              <article key={rec.recommendation_id} className="list-item-card">
                <div className="list-item-head"><strong>{rec.title}</strong><Badge tone={rec.priority === "HIGH" ? "red" : "amber"}>{rec.priority}</Badge></div>
                <p>{rec.reason}</p>
                <div className="reference-list">{rec.evidence_references.map((ref: string) => <button key={ref} className="mono" onClick={() => void openTransaction(ref)}>{ref} ↗</button>)}</div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
