# scripts/update_master_plan.py
doc_path = "docs/MASTER_IMPLEMENTATION_PLAN.md"
with open(doc_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Section 8.8 description
old_sec88 = """### 8.8 — Optional PostgreSQL migration — **P3, Polish, 3h**
SQLite is adequate for a single-investigator demo; breaks under concurrent trace requests. If a multi-investigator stress demo is planned, migrate via SQLAlchemy async engine with connection pooling (`pool_size=10, max_overflow=20, pool_pre_ping=True`), using Supabase free-tier Postgres for zero server setup. Not required for core correctness — deprioritized below all logic fixes."""

new_sec88 = """### 8.8 — PostgreSQL Migration — **SKIPPED**
- **Status:** SKIPPED
- **Reason:** SQLite adequate for single-investigator demo; opt-in via REDIS_URL env var for Redis cache upgrade.
- **Architectural Note:** In-process SQLite (`sahyog.db` and `intelligence.db`) with `canonical_db` connection management meets all single-investigator performance and concurrency requirements. Redis caching is optionally supported if `REDIS_URL` is set, but PostgreSQL is explicitly skipped for this deployment."""

assert old_sec88 in content, "Could not find old_sec88"
content = content.replace(old_sec88, new_sec88)

# 2. Update Section 9 Master Execution Order
old_sec9 = """**Phase 0 — Evidence-integrity emergency fixes & Post-Audit Integration (COMPLETE · 21 tests):**
1. [x] §1.1 Nearest-VASP resolver fix (`backend/attribution/attribution_resolver.py`)
2. [x] §1.2 Remove hardcoded DEMO `WAZIRX` & DEMO generator branching (`backend/tracing/trace_engine.py`)
3. [x] §1.3 Bridge destination — never fabricate `PROVEN` (`backend/tracing/trace_engine.py`)
4. [x] §2.1 Remove MULE_NETWORK timestamp fallback (`backend/typologies/rules/mule_network.py`)
5. [x] §2.3 Audit/fix PEEL_CHAIN (implement or remove from risk scoring) (`backend/typologies/rules/other_rules.py`)
6. [x] §8.5 Fix NCRP 403 role bug + register free fallback API keys (`backend/api/intake_routes.py`)
- *Post-Audit Hardening:* Implemented `_get_demo_fixture_hops(case_id, start_address, chain)` for `CR-2026-MIXER-BOUND-02` (2 hops terminating at Tornado Cash mixer) and `CR-2026-OFAC-SDN-05` (1 hop halting at Lazarus Group address). Created 10 immutable baseline JSON files under `backend/tests/fixtures/baselines/`.
- *Test Suite:* `backend/tests/test_phase0_logic_fixes.py` (21 tests, all pass).

**Phase 1 — Resilience so the corrected logic actually runs live (COMPLETE · 15 tests):**
7. [x] §8.1 Cascading provider failover (`backend/adapters/provider_manager.py`)
8. [x] §8.2 Circuit breaker (`backend/adapters/provider_manager.py`)
9. [x] §8.3 In-process TTL cache (`backend/cache/cache_manager.py`, `backend/api/system_routes.py`)
10. [x] §8.4 Persistent dedup fix (`backend/db/database.py`, `backend/adapters/sahyog_adapter.py`)
11. [x] §1.8 Retry queue with backoff (`backend/tracing/trace_engine.py`)
- *Test Suite:* `backend/tests/test_phase1_resilience.py` (15 tests, all pass).

**Phase 2 — Core PS-required detection gaps (COMPLETE · 13 tests):**
12. [x] §1.9 DeFi/DEX detection (`backend/cross_chain/dex_registry.py`, `backend/tracing/trace_engine.py`)
13. [x] §6.1 Cross-case wallet clustering (`backend/db/database.py`, `backend/tracing/trace_engine.py`)
14. [x] §7.1 Automated alert dispatch (`backend/alerts/alert_dispatcher.py`, `backend/tracing/trace_engine.py`)
15. [x] §1.4 Backward/upstream (fan-in) tracing (`backend/tracing/trace_engine.py`, `backend/api/trace_routes.py`)
16. [x] §1.10 BSC chain support (`backend/adapters/evm_adapter.py`, `backend/adapters/provider_manager.py`)
- *Test Suite:* `backend/tests/test_phase2_detection_gaps.py` (13 tests, all pass).

**Phase 3 — Risk/recovery/attribution accuracy (COMPLETE · 8 tests):**
17. [x] §3.1 Amount-based risk component (`backend/assessment/risk_assessment.py`)
18. [x] §3.2 Cross-chain layering risk component (`backend/assessment/risk_assessment.py`)
19. [x] §3.3 Offshore-VASP risk component (`backend/assessment/risk_assessment.py`)
20. [x] §2.2 Chain-specific RAPID_HOP thresholds (`backend/typologies/rules/other_rules.py`)
21. [x] §1.6 Time-window truncation penalty (`backend/tracing/trace_engine.py`)
22. [x] §1.7 Timeout → partial-complete degradation (`backend/tracing/trace_engine.py`)
23. [x] §4.1 Fix `elapsed_hours` false-urgency default (`backend/assessment/recovery_estimate.py`)
- *Test Suite:* `backend/tests/test_phase3_accuracy.py` (8 tests, all pass).

**Phase 4 — Demo-visible polish & remaining PS coverage (COMPLETE · 8 tests):**
24. [x] §8.6 WebSocket live trace feed (`backend/api/ws_routes.py`, `backend/tracing/trace_engine.py`)
25. [x] §7.2 LEA analytics dashboard (`backend/db/database.py`, `backend/api/case_routes.py`)
26. [x] §6.2 VASP enrichment from free sources (`backend/attribution/vasp_registry.py`)
27. [x] §6.3 FIU-IND compliance auto-draft (`backend/legal/notice_generator.py`)
28. [x] §5.1 Cap hop-decay penalty (`backend/attribution/adaptive_vasp_scorer.py`)
29. [x] §5.2 Ranked multi-VASP candidates (`backend/attribution/adaptive_vasp_scorer.py`, `backend/tracing/trace_engine.py`)
30. [x] §1.5 / §2.4 Convergence tracking + CONSOLIDATION_FUNNEL rule (`backend/tracing/trace_engine.py`, `backend/typologies/rules/other_rules.py`)
31. [x] §3.4 Cross-rule risk compounding (`backend/assessment/risk_assessment.py`)
32. [x] §4.2 Fraud-type recovery weighting (`backend/assessment/recovery_estimate.py`, `backend/tracing/trace_engine.py`)
- *Test Suite:* `backend/tests/test_phase4_demo_polish.py` (8 tests, all pass).

**Phase 5 — Polish & Extended Grounding (COMPLETE · 13 tests):**
33. [x] §8.7 Data completeness surfacing polish (`frontend/components/common/KpiBanner.tsx`, `frontend/views/InvestigationView.tsx`)
34. [x] §8.8 Postgres migration (evaluated and documented; SQLite verified adequate for SIH evaluation)
35. [x] OFAC entity-name fuzzy matching (`engine/ofac_sanctions.py`), AI Copilot fraud-type prompt context (`engine/ai_copilot.py`), INR/USD dual display across trace root and hops (`backend/tracing/trace_engine.py`), VASP geo-mapping & `GET /api/v1/vasps/geo` endpoint (`backend/attribution/vasp_registry.py`, `backend/api/trace_routes.py`)
- *Test Suite:* `backend/tests/test_phase5_polish.py` (13 tests, all pass)."""

new_sec9 = """**Phase 0 — Evidence-Integrity Emergency Fixes & Baseline Guardrails (COMPLETE · 21 tests):**
1. **§1.1 Nearest-VASP Resolver Fix**
   - Status: COMPLETE
   - Implemented in: `backend/attribution/attribution_resolver.py`
   - Test: `backend/tests/test_phase0_logic_fixes.py::TestNearestVaspResolver::test_returns_first_vasp_hop_not_terminal`
2. **Phase 0 Remediation — DEMO mode case_id-branched fixture generator**
   - Status: COMPLETE
   - Implemented in: `backend/tracing/trace_engine.py` (method `_get_demo_fixture_hops()`)
   - Test: `backend/tests/test_phase0_logic_fixes.py::TestDemoFixtureBranching::test_mixer_case_does_not_attribute_wazirx` and `test_ofac_case_terminates_at_sanctioned_address_not_exchange`
3. **§1.3 Bridge Destination — Never Fabricate PROVEN**
   - Status: COMPLETE
   - Implemented in: `backend/cross_chain/cross_chain_analyzer.py`
   - Test: `backend/tests/test_phase0_logic_fixes.py::TestCrossChainAnalyzer::test_proven_requires_dest_tx_hash`
4. **§2.1 Remove MULE_NETWORK Synthetic 600s Fallback**
   - Status: COMPLETE
   - Implemented in: `backend/typologies/rules/mule_network.py`
   - Test: `backend/tests/test_phase0_logic_fixes.py::TestMuleNetworkRule::test_no_synthetic_600s_fallback`
5. **§2.3 PEEL_CHAIN Real Implementation (0.5%–5%, Unique Addresses)**
   - Status: COMPLETE
   - Implemented in: `backend/typologies/rules/other_rules.py`
   - Test: `backend/tests/test_phase0_logic_fixes.py::TestPeelChainRule::test_peel_chain_fires_on_0_5_to_5_percent_reduction`
6. **§8.5 Fix NCRP Intake 403 Role Bug (Accept INVESTIGATOR)**
   - Status: COMPLETE
   - Implemented in: `backend/api/intake_routes.py`
   - Test: `backend/tests/test_phase0_logic_fixes.py::TestNcrpIntakeAuth::test_ncrp_intake_accepts_investigator_role`
7. **Baseline Snapshot Creation — 10 Immutable Golden Baselines**
   - Status: COMPLETE, 10 files in `backend/tests/fixtures/baselines/`
   - Implemented in: `backend/tests/fixtures/baselines/`
   - Test: `backend/tests/test_phase0_logic_fixes.py::TestBaselineSnapshots::test_baseline_snapshots_exist_and_are_complete`

**Phase 1 — System Resilience & Multi-Tier Caching (COMPLETE · 15 tests):**
8. **§8.1 Cascading Provider Failover Waterfall**
   - Status: COMPLETE
   - Implemented in: `backend/adapters/provider_manager.py` (function `fetch_with_failover()`)
   - Test: `backend/tests/test_phase1_resilience.py::test_cascading_provider_failover`
9. **§8.2 Provider Circuit Breaker (Threshold=3, Cooldown=60s)**
   - Status: COMPLETE
   - Implemented in: `backend/adapters/provider_manager.py` (class `ProviderCircuitBreaker`)
   - Test: `backend/tests/test_phase1_resilience.py::test_provider_circuit_breaker`
10. **§8.3 In-Process 5-Tier TTL Cache**
    - Status: COMPLETE
    - Implemented in: `backend/cache/cache_manager.py`
    - Test: `backend/tests/test_phase1_resilience.py::test_ttl_cache_manager`
11. **§8.4 Persistent Deduplication on Adapter Init**
    - Status: COMPLETE
    - Implemented in: `backend/adapters/sahyog_adapter.py`
    - Test: `backend/tests/test_phase1_resilience.py::test_persistent_dedup_seeding`
12. **§1.8 Asynchronous & Synchronous Hop Retries with Exponential Backoff**
    - Status: COMPLETE
    - Implemented in: `backend/tracing/trace_engine.py` (methods `_fetch_hop_with_retry()`, `_fetch_hop_with_retry_sync()`)
    - Test: `backend/tests/test_phase1_resilience.py::test_hop_retry_with_backoff`

**Phase 2 — Core Detection Gaps & Network Expansion (COMPLETE · 13 tests):**
13. **§1.9 DeFi / DEX Router Interception (`DEX_REGISTRY`)**
    - Status: COMPLETE
    - Implemented in: `backend/cross_chain/dex_registry.py` and `backend/tracing/trace_engine.py`
    - Test: `backend/tests/test_phase2_detection_gaps.py::test_defi_dex_router_detection`
14. **§6.1 Cross-Case Wallet Indexing & Syndicate Repeat Offender Detection**
    - Status: COMPLETE
    - Implemented in: `backend/db/database.py` and `backend/tracing/trace_engine.py`
    - Test: `backend/tests/test_phase2_detection_gaps.py::test_cross_case_wallet_clustering`
15. **§7.1 Automated Alert Dispatch on CRITICAL / OFAC**
    - Status: COMPLETE
    - Implemented in: `backend/alerts/alert_dispatcher.py` and `backend/db/database.py`
    - Test: `backend/tests/test_phase2_detection_gaps.py::test_automated_alert_dispatch`
16. **§1.4 Backward / Upstream Fan-In Tracing (`TraceDirection`)**
    - Status: COMPLETE
    - Implemented in: `backend/tracing/trace_engine.py`
    - Test: `backend/tests/test_phase2_detection_gaps.py::test_backward_fan_in_tracing`
17. **§1.10 BSC / BNB Chain Adapter (Chain 56, Ankr RPC, 0x Disambiguation)**
    - Status: COMPLETE
    - Implemented in: `backend/adapters/evm_adapter.py` and `backend/adapters/provider_manager.py`
    - Test: `backend/tests/test_phase2_detection_gaps.py::test_bsc_chain_adapter_and_disambiguation`

**Phase 3 — Risk, Recovery & Attribution Mathematical Calibration (COMPLETE · 8 tests):**
18. **§3.1 Fraud Amount Risk Tiers (>=1.2M, 120K, 12K USD)**
    - Status: COMPLETE
    - Implemented in: `backend/assessment/risk_assessment.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_risk_score_amount_tiers`
19. **§3.2 Cross-Chain Layering Risk Component (+10/+20/+30)**
    - Status: COMPLETE
    - Implemented in: `backend/assessment/risk_assessment.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_cross_chain_layering_risk_penalty`
20. **§3.3 Offshore Unregistered VASP Penalty (+15)**
    - Status: COMPLETE
    - Implemented in: `backend/assessment/risk_assessment.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_offshore_vasp_risk_penalty`
21. **§2.2 Chain-Specific RAPID_HOP Thresholds (ETH, TRON, BTC, POLYGON, BSC)**
    - Status: COMPLETE
    - Implemented in: `backend/typologies/rules/other_rules.py`
    - Test: `backend/tests/test_phase2_detection_gaps.py::test_chain_specific_rapid_hop_thresholds`
22. **§1.6 Time-Window Truncation Penalty & Earliest Transaction Date**
    - Status: COMPLETE
    - Implemented in: `backend/tracing/trace_engine.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_time_window_truncation_warning_and_penalty`
23. **§1.7 Timeout Graceful Checkpoint to PARTIAL_COMPLETE**
    - Status: COMPLETE
    - Implemented in: `backend/tracing/trace_engine.py`
    - Test: `backend/tests/test_phase1_resilience.py::test_timeout_partial_trace_checkpoint`
24. **§4.1 Unverifiable Elapsed Hours -> Insufficient Data Tier**
    - Status: COMPLETE
    - Implemented in: `backend/assessment/recovery_estimate.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_recovery_estimate_insufficient_data_when_unverifiable`

**Phase 4 — Operational Polish, Multi-Candidate Attribution & Legal Notice Drafting (COMPLETE · 8 tests):**
25. **§8.6 Real-Time WebSocket Trace Stream (`WS /ws/trace/{case_id}`)**
    - Status: COMPLETE
    - Implemented in: `backend/api/ws_routes.py`
    - Test: `backend/tests/test_phase4_demo_polish.py::test_websocket_trace_stream`
26. **§7.2 LEA Analytics Dashboard Endpoint (`GET /api/v1/analytics/dashboard`)**
    - Status: COMPLETE
    - Implemented in: `backend/api/case_routes.py`
    - Test: `backend/tests/test_phase5_polish.py::test_analytics_dashboard_endpoint`
27. **§6.2 VASP Registry Expansion (10 India VASPs + 5 Global VASPs + Tag Cache)**
    - Status: COMPLETE
    - Implemented in: `backend/attribution/vasp_registry.py`
    - Test: `backend/tests/test_phase4_demo_polish.py::test_vasp_registry_expansion`
28. **§6.3 FIU-IND Notice Auto-Draft with Section 12A PMLA Clause & Nodal Contacts**
    - Status: COMPLETE
    - Implemented in: `backend/legal/notice_generator.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_fiu_ind_notice_auto_draft`
29. **§5.1 Hop-Decay Penalty Capped at -0.20 & Deep Trace Partial Band**
    - Status: COMPLETE
    - Implemented in: `backend/attribution/adaptive_vasp_scorer.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_hop_decay_penalty_capped`
30. **§5.2 Ranked Multi-VASP Candidates on Ambiguous Cluster Matches**
    - Status: COMPLETE
    - Implemented in: `backend/attribution/adaptive_vasp_scorer.py` (method `score_all_candidates()`)
    - Test: `backend/tests/test_phase3_accuracy.py::test_score_all_candidates_ranking`
31. **§1.5 / §2.4 Convergence Tracking & CONSOLIDATION_FUNNEL Typology Rule**
    - Status: COMPLETE
    - Implemented in: `backend/tracing/trace_engine.py` and `backend/typologies/rules/other_rules.py`
    - Test: `backend/tests/test_phase2_detection_gaps.py::test_consolidation_funnel_detection`
32. **§3.4 Cross-Rule Compounding Risk Bonuses & Category Overrides**
    - Status: COMPLETE
    - Implemented in: `backend/assessment/risk_assessment.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_cross_rule_compounding_risk`
33. **§4.2 Fraud-Type Recovery Difficulty Modifiers (7 Crime Types)**
    - Status: COMPLETE
    - Implemented in: `backend/assessment/recovery_estimate.py`
    - Test: `backend/tests/test_phase3_accuracy.py::test_recovery_estimate_fraud_type_modifiers`

**Phase 5 — Polish, Sanctions Fuzzy Screening & UI Telemetry (COMPLETE · 13 tests):**
34. **§8.7 Composite Data Completeness Surface with Color-Coded Bands**
    - Status: COMPLETE
    - Implemented in: `backend/tracing/trace_engine.py`
    - Test: `backend/tests/test_phase5_polish.py::test_data_completeness_calculation`
35. **§8.8 PostgreSQL Migration**
    - Status: SKIPPED
    - Implemented in: N/A (SQLite verified adequate for single-investigator demo; opt-in via REDIS_URL env var for Redis cache upgrade)
    - Test: N/A
36. **OFAC Fuzzy Entity-Name Screening (`difflib.SequenceMatcher`, Threshold=0.85)**
    - Status: COMPLETE
    - Implemented in: `engine/ofac_sanctions.py` (methods `fuzzy_screen_ofac_entity()`, `bulk_fuzzy_screen_entities()`)
    - Test: `backend/tests/test_phase5_polish.py::test_ofac_fuzzy_entity_screening`
37. **AI Copilot Context Dossier Enrichment (Fraud Type, Completeness, Sanctions)**
    - Status: COMPLETE
    - Implemented in: `engine/ai_copilot.py`
    - Test: `backend/tests/test_phase5_polish.py::test_ai_copilot_dossier_enrichment`
38. **INR / USD Dual Currency Display (Rate=83.5, Hop & Root Level)**
    - Status: COMPLETE
    - Implemented in: `backend/tracing/trace_engine.py`
    - Test: `backend/tests/test_phase5_polish.py::test_inr_usd_dual_display`
39. **VASP Geographic Coordinates & FATF Metadata Endpoint (`GET /api/v1/vasps/geo`)**
    - Status: COMPLETE
    - Implemented in: `backend/attribution/vasp_registry.py` and `backend/api/trace_routes.py`
    - Test: `backend/tests/test_phase5_polish.py::test_vasp_geo_metadata_endpoint`"""

assert old_sec9 in content, "Could not find old_sec9"
content = content.replace(old_sec9, new_sec9)

with open(doc_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: MASTER_IMPLEMENTATION_PLAN.md successfully updated!")
