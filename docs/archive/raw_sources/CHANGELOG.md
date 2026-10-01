# CryptoTrace LEA — Changelog

## [2.1.0-SIH26183] - 2026-10-01

### Logic Implementation Plan (Phases 0–5) & Post-Audit Hardening
- **Post-Audit DEMO-Mode Synthetic Generator Hardening**:
  - Replaced universal 4-hop mule trail in `trace_engine.py` with case_id-branched fixture loader `_get_demo_fixture_hops()`.
  - `CR-2026-MIXER-BOUND-02`: Traverses 2 hops terminating at Tornado Cash Router (`0xd90e2f925da726b50c4ed8d0fb90ad053324f31b`), `edge_type="MIXER_BOUNDARY"`, `is_mixer=True`, producing `typologies: ["MULE_NETWORK", "MIXER_BOUNDARY"]`, `attribution: label_type="UNRESOLVED", vasp_name=None`, and `MIXER_BOUNDARY` boundary event.
  - `CR-2026-OFAC-SDN-05`: Halts at 1 hop at Lazarus Group SDN address (`0x098b716b8aaf21512996dc57eb0615e2383e2f96`), producing `ofac_sanction_hit: True`, `attribution: label_type="UNRESOLVED"`, `typologies: ["OFAC_SANCTION"]`, and `risk_category: "CRITICAL"`.
  - Added `TestPhase0DemoIntegration` with 3 integration and snapshot tests in `test_phase0_logic_fixes.py`.
  - Generated 10 immutable post-Phase-0 baseline snapshots under `backend/tests/fixtures/baselines/`.
  - **Full test suite passes: 129/129 tests (100% green, 0 regressions)**.

### Phase 0: Evidence Integrity Emergency Fixes
- **Nearest-VASP Resolution (§1.1)**: `AttributionResolver` walks BFS trace in traversal order returning first matching VASP hot-wallet hop, ignoring internal exchange sweeps.
- **DEMO Mode Hardcoding Removal (§1.2)**: Removed unconditional WAZIRX attribution in DEMO mode; routed through canonical resolver.
- **Bridge Link Verification (§1.3)**: `CrossChainAnalyzer` assigns `PROVEN` only when confirmed via real query; defaults to `HEURISTIC_CORRELATION` otherwise.
- **Mule Timestamp Fallback Removal (§2.1)**: Eliminated fabricated 600s interval fallback on missing timestamps in `MuleNetworkRule`.
- **Peel Chain Rule Hardening (§2.3)**: Audited `PeelChainRule` to enforce strict 0.5%–5% per-hop reduction to unique addresses.
- **NCRP Intake Authorization Fix (§8.5)**: Added `INVESTIGATOR` role to allowed callers of NCRP intake gateway.
- **Execution Timeout Extension (§1.7)**: Bundled 120s timeout for live on-chain traversals.

### Phase 1: Live Resilience & Fault Tolerance
- **Cascading Provider Failover (§8.1)**: Implemented `fetch_with_failover()` across Primary $\to$ Secondary $\to$ Tertiary provider endpoints.
- **Provider Circuit Breaker (§8.2)**: Implemented `ProviderCircuitBreaker` with 3-failure trip and 60-second open duration.
- **In-Process 5-Tier TTL Cache (§8.3)**: Added `cachetools.TTLCache` across hot addresses, VASP labels, traces, prices, and health telemetry. Added `GET /api/v1/system/cache-stats`.
- **Persistent Intake Deduplication (§8.4)**: Seeded `processed_bulletin_hashes` from SQLite on adapter initialization.
- **Hop Retry Queue with Exponential Backoff (§1.8)**: Added `_fetch_hop_with_retry()` with 3 retries and $2^\text{attempt}$ backoff.

### Phase 2: Core Problem-Statement Detection Gaps
- **DeFi / DEX Detection (§1.9)**: Curated `DEX_REGISTRY` detecting Uniswap, SushiSwap, PancakeSwap, Curve, and SunSwap routers, emitting `DEFI_OBFUSCATION` pattern finding with asset reset annotation.
- **Cross-Case Wallet Clustering (§6.1)**: Created `wallet_index` table and index for cross-case correlation; flags `repeat_offender: True` and exposes `GET /api/v1/cases/{id}/linked-cases`.
- **Automated Alert Dispatch (§7.1)**: Created `alerts` table and `AlertDispatcher` dispatching push events on `CRITICAL` risk or `ofac_sanction_hit: True`.
- **Backward Fan-In Tracing (§1.4)**: Supported `TraceDirection.BIDIRECTIONAL` and `BACKWARD` with `max_backward_hops=2`, aggregating funding sources.
- **BSC / BNB Chain Support (§1.10)**: Integrated BSC chain ID 56 with free Ankr RPC and address disambiguation.

### Phase 3: Risk, Recovery & Attribution Accuracy
- **Tiered Amount-Based Risk (§3.1)**: Added `amount_component()` (+15 to +35 pts) for fraud amounts up to ₹10 Crore.
- **Cross-Chain Layering Risk (§3.2)**: Added bridge hop penalty (+10 to +30 pts) in risk assessment.
- **Offshore / Unregistered VASP Penalty (§3.3)**: Added +15 pts penalty for non-FIU unregistered entities.
- **Cross-Rule Compounding Bonuses (§3.4)**: Added compounding risk bonuses for MULE+RAPID (+15), MULE+MIXER (CRITICAL), and OFAC hits (CRITICAL).
- **Chain-Specific RAPID_HOP Thresholds (§2.2)**: Calibrated rapid-hop thresholds for ETH (3h), TRON (1h), BTC (24h), Polygon (30m), BSC (1h).
- **Time-Window Truncation Penalty (§1.6)**: Penalized data completeness (-10%) on 90-day horizon truncations with `earliest_transaction_date`.
- **Partial-Complete Timeout Degradation (§1.7)**: Checks point $\ge 2$ hops on timeout, returning `PARTIAL_COMPLETE` with full assessment rather than empty skeleton.
- **Non-Fabricated Elapsed Hours (§4.1)**: Handled missing case timestamps as `insufficient_data` without fabricated 2.5h default.

### Phase 4: Demo Polish & High-Value Capabilities
- **Capped Hop-Decay Penalty (§5.1)**: Capped hop penalty at -0.20 to prevent deep 4-hop and 5-hop traces from collapsing to zero confidence.
- **Ranked Multi-VASP Candidates (§5.2)**: Implemented `score_all_candidates()` returning ranked candidates on ambiguous cluster matches.
- **Expanded VASP Registry (§6.2)**: Added 10 domestic Indian exchanges (Mudrex, BitBNS, Giottus, Unocoin, etc.) and 5 top global exchanges (OKX, Bitget, MEXC, etc.).
- **FIU-IND Compliance Auto-Draft (§6.3)**: Auto-inserts Section 12A PMLA 2002 clauses and nodal officer emails into Section 91 notices.
- **Convergence Tracking & CONSOLIDATION_FUNNEL (§1.5, §2.4)**: Detected multi-branch fund funnels and added `ConsolidationFunnelRule`.
- **Fraud-Type Recovery Modifiers (§4.2)**: Calibrated recovery difficulty by crime category (Ransomware, Task Fraud, Sextortion, Darknet).
- **LEA Aggregate Analytics Dashboard (§7.2)**: Added `get_lea_aggregate_analytics()` and `GET /api/v1/analytics/dashboard`.
- **WebSocket Live Trace Feed (§8.6)**: Implemented `TraceStreamManager` at `/ws/trace/{case_id}` emitting real-time BFS events.

### Phase 5: Polish & Extended Grounding
- **First-Class Data Completeness Metric (§8.7)**: Added color-coded KPI banner and partial execution warnings in frontend.
- **OFAC Entity-Name Fuzzy Screening**: Implemented sliding-window token matching resilient to typos.
- **AI Copilot Context Grounding**: Enriched copilot prompt dossier with fraud type, data completeness, and sanctions nexus.
- **INR / USD Dual Currency Display**: Injected dual-currency values across trace root and all forward/backward hops (83.5 rate).
- **VASP Geographic Coordinates**: Mapped lat/lng and FIU status across all registry VASPs; added `GET /api/v1/vasps/geo`.

---

## [1.0.0-SIH26183] - 2026-09-23

### Initial Prototype & Foundation Architecture
- Initial MULE_NETWORK typology rule prototype.
- Initial AdaptiveVASPScorer implementation.
- Basic Heuristic Recovery Estimate.
- Chained audit logging and canonical RBAC definitions.
- Isolated blockchain providers (EVM, Bitcoin, Tron).
