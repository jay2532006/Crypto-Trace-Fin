# scripts/update_frontend_mock_api.py
with open("frontend/services/mockApi.ts", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update runTrace
old_run_trace = """      if (res.data && res.data.trace_id) {
        latestTraceResult = {
          trace_id: res.data.trace_id,
          case_id: caseId,
          start_wallet: targetAddr,
          execution_timestamp: new Date().toISOString(),
          status: "COMPLETED",
          total_hops: (res.data.hops || []).length,
          total_volume_usd: res.data.risk?.total_volume_usd || 125000,
          total_volume_inr: (res.data.risk?.total_volume_usd || 125000) * 88,
          destination_vasp: res.data.attribution?.vasp_name || "Unknown VASP",
          recovery_potential: res.data.recovery?.recommendation || "High",
          limits
        };
        return envelope<TraceResult>(latestTraceResult, "LIVE_BACKEND");
      }"""

new_run_trace = """      if (res.data && (res.data.trace_id || res.data.case_id || res.data.hops)) {
        const traceHops = res.data.hops || [];
        const rawAttr = res.data.attribution || {};
        const destVasp = rawAttr.vasp_name || rawAttr.nearest_vasp || "Unresolved";
        const totalUsd = res.data.traced_value_usd ?? res.data.risk?.total_volume_usd ?? 125000;
        const totalInr = res.data.traced_value_inr ?? (totalUsd * 83.5);

        latestTraceResult = {
          trace_id: res.data.trace_id || `TR-${res.data.case_id || Date.now()}`,
          case_id: res.data.case_id || caseId,
          start_wallet: targetAddr,
          execution_timestamp: new Date().toISOString(),
          status: "COMPLETED",
          total_hops: traceHops.length,
          total_volume_usd: totalUsd,
          total_volume_inr: totalInr,
          destination_vasp: destVasp,
          recovery_potential: res.data.recovery_estimate?.display_tier || res.data.recovery?.recommendation || "Moderate",
          limits,
          coverage: res.data.partial_result ? "PARTIAL" : "COMPLETE",
          data_completeness_pct: res.data.data_completeness_pct,
          earliest_transaction_date: res.data.earliest_transaction_date,
          time_window_truncations: res.data.time_window_truncations ?? 0,
          partial_result: res.data.partial_result ?? false,
          termination_reason: res.data.termination_reason ?? "TARGET_REACHED",
          ofac_sanction_hit: res.data.ofac_sanction_hit ?? false,
          node_count: (res.data.nodes || []).length,
          edge_count: (res.data.edges || []).length,
          max_depth_reached: traceHops.length,
        };

        // Wire nodes & edges to live graph so Cytoscape graph canvas renders live backend nodes
        if (Array.isArray(res.data.nodes) && Array.isArray(res.data.edges)) {
          (fixture.graph as any).nodes = res.data.nodes.map((n: any, idx: number) => ({
            id: n.id || `W${idx + 1}`,
            address: n.id,
            chain: (res.data.chain || targetChain).toLowerCase(),
            type: n.type || "intermediary",
            depth: n.depth ?? idx,
            balance_usd: 0,
            hop: Math.abs(n.depth ?? idx),
          }));
          (fixture.graph as any).edges = res.data.edges.map((e: any, idx: number) => ({
            id: `E${idx + 1}`,
            from_address: e.from,
            to_address: e.to,
            amount: e.amount,
            asset: e.asset || "USDT",
            tx_hash: e.tx_hash || `0xtx_${idx + 1}`,
            hop: idx + 1,
            edge_type: e.edge_type || "FORWARD",
          }));
        }

        // Wire typologies if returned
        if (Array.isArray(res.data.typologies) && res.data.typologies.length > 0) {
          (fixture as any).typologies = res.data.typologies.map((typ: any, idx: number) => ({
            finding_id: `FIND-${idx + 1}`,
            pattern_type: typ.rule_id || typ.typology_name || "UNKNOWN_TYPOLOGY",
            india_specific: typ.india_specific ?? false,
            confidence: typ.confidence || "HIGH",
            rule_version: typ.rule_version || "1.0",
            evidence_references: typ.evidence_references || [],
            data_coverage: "COMPLETE",
            uncertainty_note: typ.uncertainty_note || "",
            total_value_aggregated_usd: typ.amount_usd || 0,
          }));
        }

        // Wire recovery if returned
        if (res.data.recovery_estimate) {
          (fixture as any).recovery = {
            eligible: res.data.recovery_estimate.eligible ?? true,
            label: "Heuristic Recovery Estimate",
            recovery_score: res.data.recovery_estimate.recovery_score ?? 0.65,
            display_tier: res.data.recovery_estimate.display_tier ?? "GREEN",
            action_window_hours: res.data.recovery_estimate.action_window_hours ?? 48,
            value_ratio: res.data.recovery_estimate.value_ratio ?? 1.0,
            exchange_cooperation: res.data.recovery_estimate.exchange_cooperation ?? 0.85,
            time_urgency: res.data.recovery_estimate.time_urgency ?? 0.8,
            path_clarity: res.data.recovery_estimate.path_clarity ?? 0.75,
            top_candidate_confidence: res.data.recovery_estimate.top_candidate_confidence ?? 0.88,
            disclaimer: res.data.recovery_estimate.disclaimer ?? "Heuristic calculation",
            cooperation_source: "FIU-IND Compliance Registry",
            cooperation_last_reviewed: new Date().toISOString(),
          };
        }

        return envelope<TraceResult>(latestTraceResult, "LIVE_BACKEND");
      }"""

assert old_run_trace in content, "Could not find old_run_trace"
content = content.replace(old_run_trace, new_run_trace)

# 2. Update getAlerts
old_alerts = """  async getAlerts() {
    return envelope<CryptoAlert[]>([...(fixture.alerts as CryptoAlert[]), ...syntheticAlerts]);
  },"""

new_alerts = """  async getAlerts() {
    try {
      const res = await apiClient.get<any>("/api/v1/alerts");
      const alertList = res.data?.alerts || (Array.isArray(res.data) ? res.data : null);
      if (alertList && Array.isArray(alertList) && alertList.length > 0) {
        const liveAlerts: CryptoAlert[] = alertList.map((a: any, idx: number) => ({
          alert_id: a.alert_id || `ALT-${idx + 1}`,
          severity: a.severity || (a.risk_category === "CRITICAL" ? "HIGH" : "MEDIUM"),
          type: a.trigger_reason ? a.trigger_reason.replace(/\\s+/g, "_").toUpperCase() : (a.risk_category || "TYPOLOGY_HIT"),
          title: a.trigger_reason || `Alert for case ${a.case_id || 'unknown'}`,
          case_id: a.case_id || "CR-2026-UNSPECIFIED",
          wallet: a.details?.wallet || a.details?.address || a.details?.sanctioned_address || "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
          created_at: a.timestamp || new Date().toISOString(),
          status: "OPEN",
          evidence_references: [a.case_id || "CR-2026-001"],
        }));
        return envelope<CryptoAlert[]>(liveAlerts, "LIVE_BACKEND");
      }
    } catch (e) {
      console.warn("Backend /api/v1/alerts unavailable, using fixture:", e);
    }
    return envelope<CryptoAlert[]>([...(fixture.alerts as CryptoAlert[]), ...syntheticAlerts], "FIXTURE_REPLAY");
  },"""

assert old_alerts in content, "Could not find old_alerts"
content = content.replace(old_alerts, new_alerts)

# 3. Add new backend helper methods at the end of mockApi object
old_end = """    supervisorRequest = { ...supervisorRequest, status: decision };
    return envelope(supervisorRequest, "LIVE_BACKEND");
  }
};"""

new_end = """    supervisorRequest = { ...supervisorRequest, status: decision };
    return envelope(supervisorRequest, "LIVE_BACKEND");
  },

  /**
   * §7.2: Fetch LEA aggregate analytics dashboard (/api/v1/analytics/dashboard)
   */
  async getAnalyticsDashboard() {
    try {
      const res = await apiClient.get<any>("/api/v1/analytics/dashboard");
      if (res.data && res.data.data) {
        return envelope(res.data.data, "LIVE_BACKEND");
      }
    } catch (e) {
      console.warn("Backend analytics dashboard unavailable:", e);
    }
    return envelope({
      total_cases: 12,
      total_usd: 485000,
      total_inr: 40740000,
      critical_count: 3,
      fraud_type_distribution: { "INVESTMENT_SCAM": 5, "MULE_NETWORK": 4, "RANSOMWARE": 2, "OTHER": 1 },
      top_vasps: [["WazirX", 5], ["CoinDCX", 4], ["Mudrex", 2], ["Binance", 1]]
    }, "FIXTURE_REPLAY");
  },

  /**
   * §6.1: Fetch cross-case linked investigations (/api/v1/cases/{case_id}/linked-cases)
   */
  async getLinkedCases(caseId: string) {
    try {
      const res = await apiClient.get<any>(`/api/v1/cases/${encodeURIComponent(caseId)}/linked-cases`);
      if (res.data) {
        return envelope(res.data, "LIVE_BACKEND");
      }
    } catch (e) {
      console.warn("Backend linked cases unavailable:", e);
    }
    return envelope({ case_id: caseId, linked_case_count: 0, linked_cases: [] }, "FIXTURE_REPLAY");
  },

  /**
   * §Phase5: Fetch VASP geographic coordinates (/api/v1/vasps/geo)
   */
  async getVaspGeo() {
    try {
      const res = await apiClient.get<any>("/api/v1/vasps/geo");
      if (res.data) {
        return envelope(res.data, "LIVE_BACKEND");
      }
    } catch (e) {
      console.warn("Backend VASP geo unavailable:", e);
    }
    return envelope([], "FIXTURE_REPLAY");
  },

  /**
   * §8.3: Fetch system cache statistics (/api/v1/system/cache-stats)
   */
  async getCacheStats() {
    try {
      const res = await apiClient.get<any>("/api/v1/system/cache-stats");
      if (res.data && res.data.data) {
        return envelope(res.data.data, "LIVE_BACKEND");
      }
    } catch (e) {
      console.warn("Backend cache stats unavailable:", e);
    }
    return envelope({
      hot_addr: { hits: 0, misses: 0, size: 0 },
      vasp_label: { hits: 0, misses: 0, size: 0 },
      trace: { hits: 0, misses: 0, size: 0 },
      price: { hits: 0, misses: 0, size: 0 },
      health: { hits: 0, misses: 0, size: 0 },
    }, "FIXTURE_REPLAY");
  }
};"""

assert old_end in content, "Could not find old_end"
content = content.replace(old_end, new_end)

with open("frontend/services/mockApi.ts", "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: mockApi.ts successfully updated!")
