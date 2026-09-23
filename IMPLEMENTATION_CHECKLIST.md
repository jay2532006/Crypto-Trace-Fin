# CryptoTrace LEA Implementation Checklist
## Quick Start Guide: Priority-Ordered Tasks

**Target**: SIH 26183 Demonstration Ready  
**Timeframe**: 12 weeks (full-time team of 3-4)  
**Last Updated**: September 2026

---

## PHASE 0: FOUNDATION (Weeks 1-2)
### Critical Path Items — Must Complete Before Phase 1

#### Week 1: Database & Auth Foundation
- [ ] **1.1 PostgreSQL Schema**
  - [ ] Create migration: `001_initial_schema.sql`
  - [ ] Define 12 canonical tables (see ADAPTATION_STRATEGY Phase 1.1)
  - [ ] Add UNIQUE constraints for idempotency
  - [ ] Create indexes on (chain_id, tx_hash), (from_addr), (case_id), (demo_data)
  - [ ] Test: Run migrations in development environment
  - [ ] Test: Verify backward-compatible SQLite read from legacy TraceX data
  - **Owner**: Database Lead  
  - **Deliverable**: `backend/db/migrations/001_initial_schema.sql`

- [ ] **1.2 Configuration Management**
  - [ ] Create `backend/config/base.py` (shared settings)
  - [ ] Create `backend/config/development.py` (SQLite for local dev)
  - [ ] Create `backend/config/staging.py` (PostgreSQL + real APIs)
  - [ ] Create `backend/config/production.py` (PostgreSQL + API gating)
  - [ ] Implement `.env` file loading via `python-dotenv`
  - [ ] Add validation: No secrets in source code, `.env` never tracked
  - [ ] Test: Verify environment-specific behavior loads correctly
  - **Owner**: Backend Lead  
  - **Deliverable**: `backend/config/` module + validated `.env.example`

- [ ] **1.3 RBAC Framework**
  - [ ] Create `backend/auth/rbac.py`
    - [ ] Define role enums: INVESTIGATOR, SUPERVISOR, ADMIN, ANALYST
    - [ ] Define permission matrix (role → allowed actions)
    - [ ] Implement permission check functions
  - [ ] Create `backend/auth/jwt_handler.py`
    - [ ] JWT token generation (payload: user_id, role, unit)
    - [ ] Token validation and refresh logic
    - [ ] Token expiration (default 8 hours)
  - [ ] Create `backend/auth/decorators.py`
    - [ ] `@require_role(INVESTIGATOR)` decorator for routes
    - [ ] `@require_case_ownership` decorator for case access
  - [ ] Create `users` table in database
    - [ ] Columns: user_id, username, password_hash, role, unit, created_date
    - [ ] Seed with test users (investigator1, supervisor1, admin1)
  - [ ] Test: Unit tests for permission checks, token generation
  - **Owner**: Auth Lead  
  - **Deliverable**: `backend/auth/` module + test suite

#### Week 2: Audit & Storage Foundation
- [ ] **2.1 Audit Framework**
  - [ ] Create `backend/audit/audit_engine.py`
  - [ ] Define audit event schema in database: `audit_events` table
    - [ ] Columns: event_id, timestamp, user_id, action, resource_id, result, details, previous_hash, event_hash
  - [ ] Implement audit logger:
    - [ ] `log_action(user, action, resource_id, result, details)`
    - [ ] Compute event_hash = SHA-256(previous_hash + event_data)
    - [ ] Chained integrity verification
  - [ ] Create audit log verification utility:
    - [ ] `verify_audit_chain(start_event_id, end_event_id)`
    - [ ] Detects tampering
  - [ ] Test: Unit tests for logging, chain verification
  - **Owner**: Database Lead  
  - **Deliverable**: `backend/audit/` module + audit table + verification tests

- [ ] **2.2 Raw Payload Storage**
  - [ ] Create `backend/storage/raw_payload_storage.py`
  - [ ] Implement deterministic JSON serialization:
    - [ ] Sort keys alphabetically
    - [ ] Compact JSON (no whitespace)
    - [ ] Consistent encoding (UTF-8)
  - [ ] Implement SHA-256 hashing of serialized payload
  - [ ] File storage structure: `raw/{chain_id}/{block_height}/{tx_hash}/{provider}/{type}/{hash}.json`
  - [ ] Create `evidence_manifest` table:
    - [ ] Columns: manifest_id, case_id, event_id, payload_hash, provider, serialization_version, verified_timestamp
  - [ ] Implement storage operations:
    - [ ] `store_raw_payload(payload_dict, metadata) -> payload_hash`
    - [ ] `retrieve_raw_payload(payload_hash) -> payload_dict`
    - [ ] `verify_integrity(payload_hash) -> bool`
  - [ ] Test: Deterministic hashing (same input = same hash), integrity verification
  - **Owner**: Storage Lead  
  - **Deliverable**: `backend/storage/` module + evidence_manifest table + tests

- [ ] **2.3 Security Hardening**
  - [ ] Add secret scanning (git-secrets, detect-secrets)
  - [ ] Verify no API keys in `app.py`, `requirements.txt`, or fixtures
  - [ ] Test: Run security checks on codebase
  - [ ] Create `.gitignore` entry for `.env`
  - [ ] Document secret rotation procedure
  - **Owner**: Backend Lead  
  - **Deliverable**: Security test suite + `.gitignore` + documentation

- [ ] **2.4 Test Infrastructure**
  - [ ] Create `backend/tests/conftest.py` (pytest fixtures)
  - [ ] Create test database (PostgreSQL in Docker or SQLite in-memory)
  - [ ] Implement test user fixtures (investigator, supervisor, admin)
  - [ ] Implement test case fixtures (with demo_data=true)
  - [ ] Set up GitHub Actions CI/CD for test runs
  - **Owner**: QA Lead  
  - **Deliverable**: `backend/tests/` directory + pytest configuration + CI pipeline

---

## PHASE 1: DOMAIN MODELS & CORE INTELLIGENCE (Weeks 3-6)

### Week 3: Canonical Models & Adapters Foundation

- [ ] **3.1 Domain Models Definition**
  - [ ] Create `backend/models/domain_models.py`
    - [ ] Define Pydantic models for all 12 entities (see ADAPTATION_STRATEGY Phase 1.1)
    - [ ] Add validation rules (address format, value ranges, etc.)
    - [ ] Add serialization (to_dict, from_dict)
  - [ ] Create `backend/models/confidence_types.py`
    - [ ] ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]
    - [ ] LabelType = Literal["VERIFIED", "INFERRED", "UNRESOLVED"]
    - [ ] LinkType = Literal["PROVEN", "HEURISTIC_CORRELATION"]
    - [ ] RiskCategory = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
  - [ ] Create SQLAlchemy ORM mappings: `backend/db/models.py`
    - [ ] Map Pydantic models to database tables
    - [ ] Add relationships (Case has many Transactions, etc.)
  - [ ] Test: Unit tests for model validation, serialization
  - **Owner**: Data Architect  
  - **Deliverable**: `backend/models/` module + ORM mappings + validation tests

- [ ] **3.2 Chain Adapters - Part 1 (EVM)**
  - [ ] Create `backend/adapters/chain_adapter_base.py`
    - [ ] Abstract base class with methods:
      - [ ] `validate_address(addr: str) -> bool`
      - [ ] `fetch_transactions(addr, start_block, end_block) -> List[Transaction]`
      - [ ] `fetch_transfers(tx_hash) -> List[Transfer]`
      - [ ] `get_canonical_identity(event) -> tuple`
      - [ ] `normalize_to_canonical(raw_event) -> Transfer`
      - [ ] `get_finality_state(tx_hash) -> str`
  - [ ] Create `backend/adapters/evm_adapter.py`
    - [ ] Implement for Ethereum, Polygon, BNB
    - [ ] `fetch_transfers()`: Query receipt logs + internal TXNs + ERC-20 events
    - [ ] Handle ERC-20, ERC-721, ERC-1155 transfers
    - [ ] Store raw payloads (receipt JSON + traces)
    - [ ] Canonical identity: (chain_id, tx_hash, event_type, log_index, transfer_index)
  - [ ] Connect to Etherscan API (via TraceX `real_api.py` code)
  - [ ] Test: Unit tests with fixture transactions, integration tests with Etherscan
  - **Owner**: Chain Lead  
  - **Deliverable**: `backend/adapters/evm_adapter.py` + tests

- [ ] **3.3 Chain Adapters - Part 2 (Bitcoin & Tron)**
  - [ ] Create `backend/adapters/bitcoin_adapter.py`
    - [ ] Validate addresses: P2PKH (1...), P2SH (3...), SegWit (bc1...)
    - [ ] `fetch_transfers()`: Query UTXO sets via Blockstream Esplora
    - [ ] Store raw payloads (transaction JSON + UTXO metadata)
    - [ ] Canonical identity: (chain_id, tx_hash, NATIVE, 0, transfer_index)
  - [ ] Create `backend/adapters/tron_adapter.py`
    - [ ] Validate TRON addresses (Base58Check, starts with T)
    - [ ] `fetch_transfers()`: Query TronGrid for TRC-20 events + TRX transfers
    - [ ] Store raw payloads (transaction JSON + event logs)
    - [ ] Canonical identity: (chain_id, tx_hash, event_type, log_index, transfer_index)
  - [ ] Create `backend/adapters/provider_manager.py`
    - [ ] Health checks for all providers
    - [ ] Fallback logic (primary → secondary → offline)
    - [ ] Rate limit handling
    - [ ] Record provider source in every normalized record
  - [ ] Test: Unit tests with fixture data, integration tests with providers
  - **Owner**: Chain Lead  
  - **Deliverable**: `backend/adapters/` module (bitcoin, tron, provider_manager) + tests

### Week 4: Tracing Engine & Typology Foundation

- [ ] **4.1 Trace Engine**
  - [ ] Create `backend/tracing/trace_engine.py`
    - [ ] Class: `BoundedTracer`
    - [ ] Method: `trace(start_address, chain, constraints: TraceConstraints) -> TraceResult`
    - [ ] Implement BFS traversal (forward and backward)
    - [ ] Respect all bounded constraints (max_hops, time_window, value_threshold, max_nodes, timeout)
    - [ ] Checkpoint/resume capability
    - [ ] Deterministic ordering for reproducibility
    - [ ] Report termination reason (COMPLETE, MAX_HOPS, MAX_NODES, TIMEOUT, etc.)
  - [ ] Create `backend/tracing/graph_builder.py`
    - [ ] Construct NetworkX graph from transfers
    - [ ] Maintain node/edge metadata (values, hop depth, timestamps)
  - [ ] Create `backend/tracing/path_finder.py`
    - [ ] Shortest-path algorithm
    - [ ] All-paths enumeration (with limit)
    - [ ] Path value aggregation
  - [ ] Test: Unit tests with fixture traces, integration tests with live data
  - **Owner**: Algorithm Lead  
  - **Deliverable**: `backend/tracing/` module + comprehensive test suite

- [ ] **4.2 Typology Engine - Foundation & MULE_NETWORK** ⭐ INNOVATION
  - [ ] Create `backend/typologies/typology_engine.py`
    - [ ] Registry of versioned typology rules
    - [ ] Method: `detect(trace_result, case: Case) -> List[PatternFinding]`
    - [ ] Rule evaluation framework
  - [ ] Create `backend/typologies/rules/mule_network.py` ⭐
    - [ ] Rule name: MULE_NETWORK
    - [ ] Version: 1.0
    - [ ] Description: 3+ wallets with single-in/single-out pattern
    - [ ] Evidence fields:
      - [ ] wallet_count, wallet_addresses
      - [ ] inbound/outbound amounts
      - [ ] amount_similarity_ratio (fee-normalized)
      - [ ] additional_activity_count
      - [ ] time_between_transfers
    - [ ] Scoring: Confidence = MEDIUM (hard cap; heuristic pattern)
    - [ ] Uncertainty notes: "Wallet history may be PARTIAL. Does not establish ownership."
    - [ ] Detection logic:
      - [ ] Check wallet_count >= 3
      - [ ] Check fee-normalized value consistency
      - [ ] Check transfer-to-transfer immediacy (< 60 min)
      - [ ] Penalize if wallets have additional activity
  - [ ] Create base test fixture: MULE_NETWORK demo case
    - [ ] 3 wallets with peel pattern
    - [ ] Predictable amounts and timing
    - [ ] Expected finding: MULE_NETWORK with MEDIUM confidence
  - [ ] Test: Unit tests for MULE_NETWORK detection, fixture case walkthrough
  - **Owner**: Typology Lead  
  - **Deliverable**: `backend/typologies/` module + MULE_NETWORK rule + demo fixture + tests

- [ ] **4.3 Other Typology Rules** (Parallel to MULE_NETWORK)
  - [ ] Create `backend/typologies/rules/peel_chain.py`
  - [ ] Create `backend/typologies/rules/fan_in.py`
  - [ ] Create `backend/typologies/rules/fan_out.py`
  - [ ] Create `backend/typologies/rules/rapid_hop.py`
  - [ ] Create `backend/typologies/rules/mixer_boundary.py`
  - [ ] Create `backend/typologies/rules/dex_bridge_analysis.py`
  - [ ] Test: Basic detection logic for each
  - **Owner**: Typology Lead  
  - **Deliverable**: All 6 rule modules + tests (non-blocking for MULE_NETWORK focus)

### Week 5: VASP Attribution & Cross-Chain Analysis

- [ ] **5.1 AdaptiveVASPScorer** ⭐ INNOVATION
  - [ ] Create `backend/attribution/adaptive_vasp_scorer.py`
    - [ ] Class: `AdaptiveVASPScorer`
    - [ ] Method: `score_candidate(vasp_cluster, trace_result, case) -> AttributionScore`
    - [ ] AttributionScore output:
      - [ ] score (0-100)
      - [ ] score_components (dict breakdown)
      - [ ] policy_version (e.g., "policy_v1_india_kyc")
      - [ ] scoring_steps (List[ScoringStep] for audit trail)
      - [ ] label_type (VERIFIED|INFERRED|UNRESOLVED)
      - [ ] confidence_band (CRITICAL|HIGH|MEDIUM|LOW)
    - [ ] Scoring factors (adaptive weights):
      - [ ] Mixer presence (-30 if detected)
      - [ ] Value magnitude
      - [ ] Label quality (VERIFIED=+50, INFERRED=+20, UNRESOLVED=+5)
      - [ ] Hop count to VASP
      - [ ] Exchange jurisdiction (+10 India, +5 Tier-1, 0 Unknown)
      - [ ] Hot-wallet match strength
      - [ ] Recent activity (< 7 days = +15)
      - [ ] Time-to-liquidation risk
    - [ ] Confidence cap logic: If data_completeness < 70%, cap at MEDIUM
  - [ ] Create `backend/attribution/vasp_registry.py`
    - [ ] Enhanced VASP registry with policy versioning
    - [ ] Fields: vasp_id, legal_name, fiu_registration_status, hot_wallet_patterns, known_deposits, nodal_officer, policy_version
    - [ ] Seed registry with 15+ Indian exchanges (WazirX, CoinDCX, ZebPay, etc.)
  - [ ] Create `backend/attribution/label_classifier.py`
    - [ ] Classification logic: VERIFIED|INFERRED|UNRESOLVED
    - [ ] VERIFIED: FIU-registered + official compliance registry
    - [ ] INFERRED: Hot-wallet pattern match (high confidence)
    - [ ] UNRESOLVED: Candidate but no strong evidence
  - [ ] Test: Scoring breakdown tests, policy versioning, label classification
  - **Owner**: Attribution Lead  
  - **Deliverable**: `backend/attribution/` module + comprehensive scoring tests

- [ ] **5.2 Cross-Chain Analysis**
  - [ ] Create `backend/cross_chain/cross_chain_analyzer.py`
    - [ ] Method: `analyze_cross_chain_paths(case_id, traces: {chain: TraceResult}) -> List[CrossChainLink]`
    - [ ] PROVEN bridges (LinkType.PROVEN):
      - [ ] Detect bridge contract calls on source chain
      - [ ] Link to destination tx via bridge protocol
      - [ ] Confidence: HIGH
    - [ ] Heuristic correlation (LinkType.HEURISTIC_CORRELATION):
      - [ ] Time proximity + amount match (within fee tolerance)
      - [ ] Confidence: MEDIUM-LOW
    - [ ] Methods:
      - [ ] `_detect_proven_bridges(chain_traces)`
      - [ ] `_detect_heuristic_correlations(chain_traces)`
      - [ ] `_validate_bridge_transaction(tx_hash)`
      - [ ] `_time_value_match_score(source, dest, time_delta, fee_pct)`
  - [ ] Create `backend/cross_chain/bridge_registry.py`
    - [ ] Known bridges: Stargate, Across, cBridge, Portal
    - [ ] Bridge contract addresses by chain
    - [ ] Fee estimation per bridge
  - [ ] Test: Proven bridge detection, heuristic correlation scoring
  - **Owner**: Cross-Chain Lead  
  - **Deliverable**: `backend/cross_chain/` module + tests

### Week 6: Risk Assessment & Recovery Estimate

- [ ] **6.1 Risk Assessment**
  - [ ] Create `backend/assessment/risk_assessment.py`
    - [ ] Class: `RiskAssessor`
    - [ ] Method: `assess_risk(case_id, trace_result) -> RiskAssessment`
    - [ ] RiskAssessment:
      - [ ] risk_score (0-100)
      - [ ] risk_category (CRITICAL|HIGH|MEDIUM|LOW)
      - [ ] component_scores (dict breakdown)
    - [ ] Component scoring:
      - [ ] Mixer presence
      - [ ] OFAC sanctions hit
      - [ ] Rapid layering/smurfing
      - [ ] Hop count and anonymity
      - [ ] Volume and velocity
  - [ ] Integrate with OFAC screening (from TraceX `ofac_sanctions.py`)
  - [ ] Test: Risk scoring on fixture cases
  - **Owner**: Risk Lead  
  - **Deliverable**: `backend/assessment/risk_assessment.py` + tests

- [ ] **6.2 RecoveryProbabilityScore** ⭐ INNOVATION
  - [ ] Create `backend/assessment/recovery_estimate.py`
    - [ ] Class: `RecoveryEstimator`
    - [ ] Method: `estimate_recovery(case_id, trace_result, risk_assessment) -> RecoveryAssessment`
    - [ ] RecoveryAssessment:
      - [ ] recovery_score (0-100; heuristic urgency indicator)
      - [ ] action_window_hours (time before liquidation risk)
      - [ ] display_tier (eligible|ineligible)
      - [ ] calculation_basis (explanation)
      - [ ] disclaimer (clearly marked as heuristic)
    - [ ] Factors:
      - [ ] Traced value amount
      - [ ] Elapsed time since theft
      - [ ] Exchange cooperation likelihood
      - [ ] Path complexity (hop count)
      - [ ] Finality state (CONFIRMED = actionable)
    - [ ] Display only if:
      - [ ] Value >= threshold (e.g., INR 10,000)
      - [ ] Data completeness >= 70%
      - [ ] Attribution confidence >= MEDIUM
    - [ ] Otherwise: display_tier = ineligible + reason
  - [ ] Create demo case with eligible recovery
    - [ ] Clear fund flow to identified VASP
    - [ ] Recent transactions (< 48 hours)
    - [ ] Moderate amount
  - [ ] Test: Eligibility logic, action window calculation
  - **Owner**: Recovery Lead  
  - **Deliverable**: `backend/assessment/recovery_estimate.py` + tests + demo case

---

## PHASE 2: INVESTIGATOR EXPERIENCE (Weeks 7-9)

### Week 7: Case Intake & APIs

- [ ] **7.1 Case Intake APIs**
  - [ ] Create `backend/api/case_routes.py`
    - [ ] POST `/api/v1/cases` (CaseIntakeRequest → Case)
    - [ ] GET `/api/v1/cases/{case_id}` (Case details)
    - [ ] GET `/api/v1/cases` (List with filters: status, chain, assigned_to, date_range)
    - [ ] PUT `/api/v1/cases/{case_id}` (Update case, log audit trail)
    - [ ] All endpoints: Apply RBAC decorators, log audit events
  - [ ] Create `backend/api/trace_routes.py`
    - [ ] POST `/api/v1/cases/{case_id}/trace` (Start trace, return trace_id)
    - [ ] GET `/api/v1/traces/{trace_id}/status` (Progress)
    - [ ] GET `/api/v1/traces/{trace_id}/result` (Full result + findings)
    - [ ] GET `/api/v1/traces/{trace_id}/graph` (Graph JSON for visualization)
  - [ ] Wire all routes to database operations (cases, traces, audit_events)
  - [ ] Test: API tests using pytest, integration tests with database
  - **Owner**: API Lead  
  - **Deliverable**: `backend/api/case_routes.py`, `trace_routes.py` + tests

- [ ] **7.2 Findings & Evidence APIs**
  - [ ] Create `backend/api/findings_routes.py`
    - [ ] GET `/api/v1/traces/{trace_id}/findings` (List all PatternFindings)
    - [ ] GET `/api/v1/findings/{finding_id}` (Detail with evidence)
  - [ ] Create `backend/api/evidence_routes.py`
    - [ ] GET `/api/v1/cases/{case_id}/evidence-manifest` (EvidenceManifest table)
    - [ ] GET `/api/v1/payloads/{payload_hash}` (Raw JSON)
    - [ ] POST `/api/v1/payloads/{payload_hash}/verify` (Recompute SHA-256)
  - [ ] Test: Evidence retrieval, integrity verification
  - **Owner**: API Lead  
  - **Deliverable**: Evidence API endpoints + tests

### Week 8: Dashboard Components

- [ ] **8.1 Core Dashboard Layout** (Vue/React)
  - [ ] Create `frontend/src/components/InvestigatorDashboard.vue`
    - [ ] Layout: Case header (top) | Controls (left) | Graph (center) | Panels (right) | Manifest (bottom)
  - [ ] Create `frontend/src/components/CaseHeader.vue`
    - [ ] Display: case_id, source, chain, wallet, reported_amount, LIVE/FIXTURE badge
    - [ ] Actions: Edit notes, assign, change status
  - [ ] Create `frontend/src/components/CaseControls.vue`
    - [ ] Timeline, filters (hop, time, value, chain, typology)
    - [ ] Notes editor
  - [ ] Test: Component rendering, data binding
  - **Owner**: Frontend Lead  
  - **Deliverable**: Dashboard layout + case header/controls

- [ ] **8.2 Information Panels (Right Side)**
  - [ ] Create `frontend/src/components/AttributionPanel.vue`
    - [ ] VASP candidates ranked by AdaptiveVASPScorer
    - [ ] Score breakdown (expandable), policy version, nodal officer
  - [ ] Create `frontend/src/components/RiskPanel.vue`
    - [ ] Risk score + category, component breakdown (pie), contributing findings
  - [ ] Create `frontend/src/components/FindingsPanel.vue`
    - [ ] List typologies, confidence levels, evidence (expandable), uncertainty notes, data completeness %
  - [ ] Create `frontend/src/components/RecoveryEstimatePanel.vue`
    - [ ] Recovery score, action window, display tier, disclaimer
  - [ ] Test: Data binding, expandable sections
  - **Owner**: Frontend Lead  
  - **Deliverable**: All 4 information panels

- [ ] **8.3 Graph Visualization**
  - [ ] Create `frontend/src/components/FundFlowGraph.vue` (using vis-network or D3)
    - [ ] Node types: suspect (red), intermediary (yellow), VASP (blue), mixer (black), exchange (green)
    - [ ] Edge labels: TX hash, amount, asset, timestamp
    - [ ] Click to expand evidence
    - [ ] Zoom/pan controls
  - [ ] Test: Graph rendering, click interactions
  - **Owner**: Frontend Lead (Visualization Specialist)  
  - **Deliverable**: FundFlowGraph component

### Week 9: Evidence & Notice Interfaces

- [ ] **9.1 Evidence Interfaces**
  - [ ] Create `frontend/src/components/EvidenceManifestPanel.vue`
    - [ ] Table: Event ID, Type, Provider, Payload Hash, Date, Status
    - [ ] Actions: View payload, verify integrity, view source
  - [ ] Create `frontend/src/components/RawPayloadViewer.vue`
    - [ ] Side panel with formatted JSON (read-only)
    - [ ] Verification status (✓ matches | ✗ mismatch)
    - [ ] Download button
  - [ ] Create `frontend/src/components/AuditTrailTimeline.vue`
    - [ ] Chronological list: Timestamp, User, Action, Resource, Result
    - [ ] Filter/search
  - [ ] Test: Table rendering, payload display, verification
  - **Owner**: Frontend Lead  
  - **Deliverable**: Evidence interfaces

- [ ] **9.2 Notice Generator (Draft-Only, Supervisor-Gated)**
  - [ ] Create `backend/api/notice_routes.py`
    - [ ] POST `/api/v1/cases/{case_id}/draft-notice` (Create draft, status=DRAFT)
    - [ ] GET `/api/v1/notices/{draft_id}` (Retrieve draft)
    - [ ] POST `/api/v1/notices/{draft_id}/submit-for-approval` (status=PENDING_APPROVAL)
    - [ ] POST `/api/v1/notices/{draft_id}/approve` (SUPERVISOR role required)
    - [ ] POST `/api/v1/notices/{draft_id}/reject`
    - [ ] GET `/api/v1/notices/{draft_id}/export` (format=pdf|txt)
  - [ ] Create `backend/legal/notice_generator.py`
    - [ ] Draft notice text generation (Section 91 BNSS 2023)
    - [ ] Auto-fill: IO name, FIR, wallet, transaction hashes
    - [ ] Export to PDF/TXT
  - [ ] Create `frontend/src/components/NoticeGeneratorModal.vue`
    - [ ] Form: investigator selection, case reference
    - [ ] Preview: Generated notice text
    - [ ] Actions: Submit for approval, edit, cancel
  - [ ] Test: Notice generation, approval workflow
  - **Owner**: Legal Lead  
  - **Deliverable**: Notice generator (backend + frontend) + supervisor workflow

---

## PHASE 3: LIVE CONNECTIVITY (Weeks 10-11)

- [ ] **10.1 Provider Connectivity**
  - [ ] Test all 5 blockchain providers (Etherscan, TronGrid, Blockstream, Bitquery, custom RPC)
  - [ ] Implement rate limit handling
  - [ ] Implement fallback/retry logic
  - [ ] Record provider latency metrics
  - [ ] Test: Integration tests with live data (staging environment)
  - **Owner**: Provider Integration Lead  
  - **Deliverable**: Tested provider connectivity

- [ ] **10.2 Checkpoint & Finality**
  - [ ] Implement checkpoint storage in database
  - [ ] Implement trace resumption from checkpoint
  - [ ] Implement finality state machine (PENDING|CONFIRMED|FINALIZED|REORGANIZED)
  - [ ] Test: Trace interruption and resumption, reorg handling
  - **Owner**: Algorithm Lead  
  - **Deliverable**: Checkpoint/resume capability + finality handling

- [ ] **10.3 Performance Testing**
  - [ ] Benchmark trace execution (1-hop, 3-hop, 5-hop)
  - [ ] Benchmark typology detection
  - [ ] Benchmark AdaptiveVASPScorer
  - [ ] Optimize bottlenecks (query indexing, caching)
  - **Owner**: QA Lead  
  - **Deliverable**: Performance benchmarks + optimization report

---

## PHASE 6: DEMONSTRATION REHEARSAL (Week 12)

- [ ] **12.1 SIH 26183 Demo Script**
  - [ ] Introduce three innovations (MULE_NETWORK, AdaptiveVASPScorer, RecoveryProbabilityScore)
  - [ ] Demo case walkthrough (fixture + MULE_NETWORK finding)
  - [ ] Show Attribution panel with score breakdown
  - [ ] Show Evidence manifest with integrity verification
  - [ ] Show Supervisor approval gate
  - [ ] Script and timeline (20 minutes)
  - **Owner**: Product Lead  
  - **Deliverable**: Demo script + walkthrough video

- [ ] **12.2 End-to-End Testing**
  - [ ] Case intake → Trace → Findings → Attribution → Recovery estimate → Notice draft → Approval
  - [ ] Verify all three innovations work as designed
  - [ ] Verify RBAC enforcement (investigator vs supervisor permissions)
  - [ ] Verify audit logging on all actions
  - [ ] Verify fixture/demo data clearly marked
  - **Owner**: QA Lead  
  - **Deliverable**: E2E test report + sign-off

---

## KEY DELIVERABLES TIMELINE

| Week | Phase | Primary Deliverables |
|------|-------|----------------------|
| 1-2 | 0 | PostgreSQL schema, RBAC, Audit framework, Secret management |
| 3 | 1 | Domain models, EVM + Bitcoin + Tron adapters |
| 4 | 1 | Trace engine, MULE_NETWORK typology (⭐), other rules foundation |
| 5 | 1 | AdaptiveVASPScorer (⭐), VASP registry, Cross-chain analysis |
| 6 | 1 | Risk assessment, RecoveryProbabilityScore (⭐), Typology polish |
| 7 | 2 | Case intake APIs, Trace APIs, Evidence APIs |
| 8-9 | 2 | Dashboard components (all 4 panels), Graph visualization, Notice generator |
| 10-11 | 3 | Live provider connectivity, Checkpoint/resume, Performance optimization |
| 12 | 6 | Demo script, E2E testing, Sign-off |

---

## CRITICAL SUCCESS FACTORS

✅ **MUST HAVE for SIH 26183**:
1. MULE_NETWORK typology working (3+ wallet peel pattern, MEDIUM confidence)
2. AdaptiveVASPScorer with explainable scoring steps
3. RecoveryProbabilityScore with action window
4. Supervisor approval gate on notice generation
5. Explicit LIVE vs FIXTURE/DEMO labeling
6. All three innovations named and explained first in demo

✅ **NICE TO HAVE** (if time):
- AI Copilot (optional; rule-based primary is acceptable)
- Neo4j graph visualization (optional; vis-network sufficient)
- Multilingual support (English only acceptable for SIH)

❌ **OUT OF SCOPE**:
- Automatic fund freezing
- Automatic legal filing
- ML-based detection (rule-based only)

---

## TEAM ASSIGNMENTS (Suggested 3-4 People)

| Role | Weeks | Primary Responsibility |
|------|-------|--------------------------|
| **Backend/Database Lead** | 1-12 | Database schema, migrations, models, ORM, all backend APIs |
| **Algorithm/Core Logic Lead** | 3-11 | Adapters, trace engine, typologies, scoring algorithms |
| **Frontend Lead** | 7-9 | Dashboard components, graph viz, user interactions |
| **QA/Devops Lead** | 1-12 | Testing, CI/CD, security scanning, performance benchmarks |
| (Optional) **Attribution/Legal Specialist** | 5-9 | AdaptiveVASPScorer, Notice generator, recovery estimate |

---

## How to Use This Checklist

1. **Print and Post**: Use as Gantt chart on team wall (update weekly)
2. **GitHub Integration**: Create GitHub Issues from each checkbox, link to PRs
3. **Weekly Standup**: Review completed checkboxes, identify blockers
4. **Exit Criteria**: Don't advance to next phase until prior phase is ✅ COMPLETE with tests passing

---

**Next Action**: Start Week 1 with PostgreSQL schema migration. Good luck! 🚀

