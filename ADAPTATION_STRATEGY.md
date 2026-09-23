# CryptoTrace LEA Adaptation Strategy
## Modifying TraceX (SIH 26182) for Your SIH 26183 Requirements

**Document Purpose**: A complete technical mapping showing how to refactor the existing GitHub solution to meet your CryptoTrace LEA product requirements.

**Current Status**: 
- **Your Project**: SIH 26183 (Real-Time Crypto Fraud Attribution System for Indian Law Enforcement)
- **Existing Solution**: TraceX v2.0-PRO (Problem Statement 26182)
- **Adaptation Scope**: ~70% code reuse with architectural refinements

---

## EXECUTIVE SUMMARY: KEY DIFFERENCES

### TraceX (GitHub Solution) vs CryptoTrace LEA (Your Requirements)

| Aspect | TraceX | CryptoTrace LEA | Adaptation Required |
|--------|--------|-----------------|---------------------|
| **Primary Innovation** | AI Copilot + VASP Attribution | MULE_NETWORK Typology + AdaptiveVASPScorer + RecoveryProbabilityScore | ✅ Core feature swap |
| **Attribution Confidence** | Single percentage score | Separate risk & attribution with VERIFIED/INFERRED/UNRESOLVED labels | ✅ Schema redesign |
| **Certainty Expression** | Deterministic conclusions | Evidence-first with explicit uncertainty bounds (MEDIUM/HIGH/etc.) | ✅ UI/Output redesign |
| **Cross-Chain Handling** | Time/value correlation heuristics | Distinguish proven bridges from heuristic correlation | ✅ Tracing logic upgrade |
| **Recovery Estimate** | Freezing urgency countdown (linear) | Heuristic Recovery Estimate with action window (victim-impact focused) | ✅ New scoring module |
| **Legal Output** | Auto-generated Section 91 notices | Draft-only notices; supervisor-gated preservation requests | ✅ Workflow gating |
| **Data Provenance** | Provider labels + timestamps | Raw payload SHA-256 hashing + deterministic serialization | ✅ Storage layer upgrade |
| **VASP Scoring** | Static hot-wallet regex matching | AdaptiveVASPScorer with policy-versioned context weights | ✅ Scoring engine rebuild |
| **Supervision** | Single-user mode | RBAC with investigator/supervisor/admin roles | ✅ Auth layer addition |
| **Demo/Fixture Distinction** | Mixed with live data | Explicit fixture/demo labeling and source provenance | ✅ Case metadata redesign |

---

## PHASE-BY-PHASE ADAPTATION ROADMAP

### PHASE 0: Foundation Hardening (Prerequisite)

**Objective**: Prepare TraceX codebase for CryptoTrace LEA baseline.

#### 0.1 Database Migration (Critical)
**Current TraceX State**:
- SQLite only (`sahyog.db`)
- Schema: `investigations` table with flat JSON payload storage

**CryptoTrace LEA Requirement**:
- PostgreSQL as primary durable system (SQLite for dev only)
- Normalized schema: `cases`, `transactions`, `transfers`, `entities`, `labels`, `findings`, `audit_events`
- Raw payload archive with SHA-256 deterministic serialization

**Adaptation Tasks**:
```
1. Create PostgreSQL schema migration scripts
   Location: backend/db/migrations/
   
   Tables to implement:
   - cases (case_id, complaint_source, chain, wallet, reported_amount, status)
   - transactions (chain_id, tx_hash, block_number, timestamp, raw_payload_hash)
   - transfers (chain_id, tx_hash, log_index, event_type, from_addr, to_addr, amount, asset, finality_state)
   - entities (address, chain, entity_type, labels)
   - entity_labels (entity_id, label, source, confidence, verified/inferred/unresolved)
   - pattern_findings (case_id, typology_name, confidence, evidence_json)
   - vasp_clusters (cluster_id, vasp_name, hot_wallets, region, score_metadata)
   - cross_chain_links (from_chain, from_addr, to_chain, to_addr, link_type, evidence_type)
   - risk_assessments (case_id, risk_score, risk_category, components_json)
   - recovery_assessments (case_id, recovery_score, action_window_hours, display_tier)
   - audit_events (user, action, resource_id, timestamp, details, signature)
   
2. Preserve backward compatibility
   - Read existing SQLite investigations
   - Migrate to PostgreSQL with provenance records
   - Mark all migrated records with source="legacy_tracex"
   
3. Redis caching layer
   - Database 0: Recent transaction cache (7-day TTL)
   - Database 1: Duplicate suppression (7-day TTL)
   - Database 2: Session/RBAC state
   - Keep Redis reconstructible from PostgreSQL (no exclusive state)
```

#### 0.2 RBAC and Authorization (Critical)
**Current TraceX State**:
- No authentication; single-user mode

**CryptoTrace LEA Requirement**:
- Multi-role RBAC: INVESTIGATOR, SUPERVISOR, ADMIN, ANALYST
- Case-level access control
- Audit trail on all material actions

**Adaptation Tasks**:
```
1. Implement authentication layer
   File: backend/auth/
   - jwt_handler.py (token generation, validation, refresh)
   - rbac.py (role definitions, permission matrices)
   - decorators.py (Flask/FastAPI route protection)
   
   Roles:
   - INVESTIGATOR: Read cases, create traces, write notes, draft notices
   - SUPERVISOR: Approve preservation requests, review high-risk cases
   - ADMIN: User management, configuration, audit access
   - ANALYST: Read-only access, generate reports
   
2. Database-backed session management
   - users table (username, password_hash, role, unit, created_at)
   - sessions table (user_id, token, issued_at, expires_at)
   - activity_log table (user_id, action, resource, timestamp, details)
   
3. Case access boundaries
   - Investigators can only access cases assigned to them or their unit
   - Supervisors can access all cases in their hierarchy
   - Preserve case provenance (created_by, assigned_to)
```

#### 0.3 Audit and Integrity (Critical)
**Current TraceX State**:
- Minimal logging; no evidence manifest

**CryptoTrace LEA Requirement**:
- Chained audit events with SHA-256 signatures
- Evidence manifest linking raw payloads to normalized records
- Deterministic raw payload serialization

**Adaptation Tasks**:
```
1. Audit event schema
   File: backend/audit/audit_engine.py
   
   Every material event records:
   - timestamp (ISO 8601)
   - user (who)
   - action (what)
   - resource_id (case/transaction)
   - result (success/failure)
   - details (JSON context)
   - previous_hash (chain integrity)
   - event_hash (SHA-256 of this record)
   
2. Raw payload storage
   File: backend/storage/raw_payload_storage.py
   
   Structure: raw/{chain_id}/{block_height}/{tx_hash}/{provider_name}/{payload_type}/{payload_hash}.json
   
   Deterministic serialization rules:
   - Sort all JSON keys alphabetically
   - Compact JSON (no whitespace)
   - No trailing whitespace
   - SHA-256 of serialized JSON = filename
   
3. Evidence manifest table
   - case_id, event_id, payload_hash, provider_source, serialization_version
   - Enables cross-verification and integrity audits
```

#### 0.4 Configuration and Environment Separation (Important)
**Current TraceX State**:
- Single `.env` file; mode switching via flag

**CryptoTrace LEA Requirement**:
- Environment-specific configs (dev/staging/prod)
- Secret sanitization
- Clear LIVE vs FIXTURE/DEMO distinction

**Adaptation Tasks**:
```
1. Configuration structure
   File: backend/config/
   - base.py (shared settings)
   - development.py (SQLite, mock APIs, verbose logging)
   - staging.py (PostgreSQL, real APIs, fixture data allowed)
   - production.py (PostgreSQL, real APIs, fixtures prohibited)
   
2. Secret management
   - Use environment variables only (never hardcoded)
   - Secrets never logged or returned in responses
   - API keys loaded at startup; validation happens once
   - Rotation without server restart (via key_manager)
   
3. Demo/Fixture labeling
   - Every record has demo_data boolean field
   - Every finding has source_confidence and source_origin fields
   - UI prominently marks FIXTURE/DEMO status
   - Production mode rejects fixture ingestion
```

#### 0.5 Test Fixtures (Important)
**Current TraceX State**:
- Pre-configured demo cases in demo_cases.py

**CryptoTrace LEA Requirement**:
- Fixture cases with explicit demo labeling
- Deterministic, reproducible test data
- Must not be presented as live intelligence

**Adaptation Tasks**:
```
1. Fixture schema enhancement
   File: backend/fixtures/
   - demo_cases_v2.py (CryptoTrace-specific fixtures)
   - fixture_loader.py (load and seed with demo labeling)
   
   Each fixture includes:
   - case_id (unique identifier)
   - demo_data = True
   - source_origin = "DEMO_CASE_SIH26183"
   - documented_investigation_pattern (description)
   - expected_findings (list of typologies to be detected)
   
2. Fixture examples to implement
   - MULE_NETWORK case (3+ wallets with peel pattern)
   - Mixer boundary case (Tornado Cash interaction)
   - Cross-chain bridge case (proven vs heuristic)
   - Fan-in consolidation case
   - Rapid-hop layering case
```

---

### PHASE 1: Domain Models and Core Intelligence

**Objective**: Implement canonical CryptoTrace LEA entities and core detection logic.

#### 1.1 Canonical Domain Models (Critical)
**Current TraceX State**:
- Generic transfer/transaction objects; VASP registry as dict

**CryptoTrace LEA Requirement**:
- Strictly typed domain models with provenance
- Explicit confidence/label types (VERIFIED/INFERRED/UNRESOLVED)
- Cross-chain link type distinction (PROVEN vs HEURISTIC)

**Adaptation Tasks**:
```
Location: backend/models/

File: domain_models.py
- Chain (id, name, rpc_endpoints, finality_depth)
- Address (address, chain, entity_type, first_seen, last_active)
- Transaction (chain_id, tx_hash, block_number, timestamp, status, raw_payload_hash)
- Transfer (chain_id, tx_hash, log_index, event_type, from_addr, to_addr, 
           amount, asset, direction, raw_payload_hash, finality_state)
- Asset (symbol, decimals, token_address, chain)
- EntityLabel (entity_id, label, source, confidence_level, 
              label_type: VERIFIED|INFERRED|UNRESOLVED, verified_date)
- VASPCluster (cluster_id, vasp_name, regions, hot_wallet_patterns, 
              adaptive_score_metadata, policy_version)
- PatternFinding (case_id, typology_id, rule_name, rule_version, 
                 confidence: MEDIUM|HIGH|LOW, evidence_json, 
                 uncertainty_notes, data_completeness_pct)
- CrossChainLink (from_chain, from_addr, to_chain, to_addr, 
                 link_type: PROVEN|HEURISTIC_CORRELATION, 
                 supporting_evidence, confidence)
- RiskAssessment (case_id, risk_score: 0-100, risk_category: CRITICAL|HIGH|MEDIUM|LOW,
                 component_scores: dict)
- RecoveryAssessment (case_id, recovery_score: 0-100, action_window_hours,
                     display_tier: eligible|ineligible, 
                     calculation_basis, disclaimer)
- InvestigativeRecommendation (case_id, finding_id, recommendation_text,
                              evidence_links, next_actions)
- EvidenceManifest (case_id, event_id, payload_hash, provider_source,
                   serialization_version, verified_at)
- AuditEvent (user_id, action, resource_id, resource_type, timestamp,
            result, details_json, previous_event_hash, event_hash)
- Case (case_id, source: COMPLAINT|NCRP|SAHYOG, chain, wallet, 
       reported_amount, complaint_text, created_by, assigned_to,
       status: OPEN|CLOSED|ARCHIVED, created_date, demo_data)

File: confidence_types.py
- ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]
- LabelType = Literal["VERIFIED", "INFERRED", "UNRESOLVED"]
- LinkType = Literal["PROVEN", "HEURISTIC_CORRELATION"]
- RiskCategory = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
```

#### 1.2 Chain Adapters with Provenance (Critical)
**Current TraceX State**:
- address_validator.py (validation only)
- real_api.py (live fetch; limited provenance tracking)

**CryptoTrace LEA Requirement**:
- Full provider provenance tracking
- Canonical event identity for idempotency
- Raw payload storage with SHA-256 hashing
- Finality state machine handling

**Adaptation Tasks**:
```
Location: backend/adapters/

File: chain_adapter_base.py
- Abstract base class for all chain adapters
- Methods:
  - validate_address(addr) -> bool
  - fetch_transactions(addr, start_block, end_block) -> List[Transaction]
  - fetch_transfers(tx_hash) -> List[Transfer]
  - compute_canonical_identity(event) -> (chain_id, tx_hash, event_type, index, transfer_idx)
  - normalize_to_canonical(raw_event) -> Transfer (with provenance)
  - get_finality_state(tx_hash) -> "PENDING"|"CONFIRMED"|"FINALIZED"|"REORGANIZED"

File: evm_adapter.py
- Supports: Ethereum, Polygon, BNB Chain
- fetch_transfers(): Query receipt logs, trace internal TXNs, handle ERC-20 events
- Providers: Etherscan, RPC (Infura/Alchemy), local node
- Canonical identity: (chain_id, tx_hash, event_type[NATIVE|ERC20|INTERNAL], log_index|trace_index, transfer_index)
- Raw payload: Entire receipt JSON + trace response (alphabetically sorted)

File: bitcoin_adapter.py
- Supports: Bitcoin mainnet only (not Lightning)
- fetch_transfers(): Query UTXO sets via Blockstream Esplora
- Providers: Blockstream Esplora, mempool.space, bitcoin-cli (local)
- Canonical identity: (chain_id, tx_hash, NATIVE, 0, transfer_index)
- Raw payload: Transaction JSON + UTXO metadata

File: tron_adapter.py
- Supports: TRON mainnet only
- fetch_transfers(): Query TronGrid for TRC-20 events and TRX transfers
- Providers: TronGrid HTTP, TronWeb
- Canonical identity: (chain_id, tx_hash, event_type[NATIVE|TRC20], log_index, transfer_index)
- Raw payload: Transaction JSON + event log response

File: provider_manager.py
- Maintain provider health, fallback logic, rate limiting
- Track provider-specific latency and error rates
- Record provider source in every normalized record
```

#### 1.3 Trace Engine with Bounded Traversal (Critical)
**Current TraceX State**:
- graph_tracer.py; 5-hop limit; NetworkX; no checkpoint recovery

**CryptoTrace LEA Requirement**:
- Bounded BFS with multiple control parameters
- Checkpoint/resume capability
- Deterministic ordering for reproducibility
- Termination reason reporting

**Adaptation Tasks**:
```
Location: backend/tracing/

File: trace_engine.py
- Main orchestrator for bounded tracing
- Class: BoundedTracer
  
  Methods:
  - trace(start_address, chain, constraints: TraceConstraints) -> TraceResult
    
    TraceConstraints:
    - max_hops: int (default 5)
    - time_window_days: int (default 90)
    - min_value_usd: float (default 0)
    - max_nodes: int (default 1000)
    - max_outflows_per_node: int (default 50)
    - timeout_seconds: int (default 300)
    - direction: "FORWARD"|"BACKWARD"|"BOTH"
    - include_internal_txns: bool
    - stop_at_known_exchange: bool
    
  - resume(trace_id, from_checkpoint) -> TraceResult
  
  Methods (internal):
  - _bfs_forward(node, visited, queue, constraints, depth)
  - _bfs_backward(node, visited, queue, constraints, depth)
  - _check_termination_conditions(constraints, current_state)
  - _save_checkpoint(trace_id, state)
  - _load_checkpoint(trace_id)
  - _serialize_deterministically(path_item)
  
  TraceResult:
  - paths: List[Path] (each path is chain of transfers)
  - total_nodes: int
  - total_edges: int
  - termination_reason: str ("COMPLETE"|"MAX_HOPS"|"MAX_NODES"|"TIMEOUT"|"VALUE_THRESHOLD"|"TIME_WINDOW")
  - summary_statistics
  - checkpoint_id (for resumption)
  - provenance: {paths: [{transfers: []}]}

File: graph_builder.py
- Construct graph from transfers
- Maintain node/edge metadata (values, hop depth, timestamps)
- Support for multigraph (multiple transfers between same pair)
- Reachability analysis and cycle detection

File: path_finder.py
- Deterministic path enumeration
- Shortest-path and all-paths algorithms
- Path value aggregation and filtering
```

#### 1.4 Typology Detection Engine (Critical - India-Specific MULE_NETWORK)
**Current TraceX State**:
- typology.py; generic FATF rules; limited confidence bounds

**CryptoTrace LEA Requirement**:
- Named, versioned typologies with evidence fields
- MULE_NETWORK as primary innovation (India-specific)
- Explicit confidence caps (MEDIUM for heuristic patterns)
- Data completeness visibility

**Adaptation Tasks**:
```
Location: backend/typologies/

File: typology_engine.py
- Registry of versioned typology rules
- Class: TypologyEngine
  
  Methods:
  - detect(trace_result, case: Case) -> List[PatternFinding]
  - _evaluate_rule(rule_version, trace, case) -> PatternFinding or None
  
File: rules/

File: mule_network.py (MAIN INDIA-SPECIFIC INNOVATION)
- Rule ID: MULE_NETWORK
- Rule Version: 1.0
- Description: Three or more wallets display single-in/single-out pattern 
  with limited additional activity, characteristic of Indian mule networks
  
  Evidence fields:
  - wallet_count: int (must be >= 3)
  - wallet_addresses: List[str]
  - inbound_amounts: List[float]
  - outbound_amounts: List[float]
  - amount_similarity_ratio: float (0-1)
  - additional_activity_count: int
  - time_between_transfers: List[int] (seconds)
  - policy_tolerance_pct: int (default 15)
  
  Scoring logic:
  - Confidence: MEDIUM (hard cap; heuristic pattern only)
  - Calculation:
    1. Check wallet_count >= 3
    2. Calculate fee-normalized value consistency
    3. Check for transfer-to-transfer immediacy (< 60 min)
    4. Penalize if wallets have additional activity
    5. Output: MEDIUM confidence + detailed evidence
  
  Uncertainty notes:
  - Wallet history may be PARTIAL (indexing gaps)
  - Does not establish ownership (complaint-linked only)
  - Investigative lead; not proof of mule identity
  - Limited to behavioral pattern; not transaction content

File: peel_chain.py
- Rule: Single inbound → Series of diminishing outflows
- Confidence: HIGH (if wallet has no other activity), MEDIUM (mixed activity)
- Evidence: hop sequence, value degradation, timing

File: fan_in.py
- Rule: Multiple sources → Single wallet
- Confidence: HIGH (consolidation to known exchange), MEDIUM (unknown destination)
- Evidence: source count, amounts, time window

File: fan_out.py
- Rule: Single wallet → Multiple destinations
- Confidence: MEDIUM (generic pattern; could be legitimate)
- Evidence: destination count, amounts, timing

File: rapid_hop.py
- Rule: Frequent transfers (> 5 per hour) through intermediaries
- Confidence: MEDIUM (layering pattern)
- Evidence: hop frequency, time intervals, value preservation

File: mixer_boundary.py
- Rule: Transfer to known mixer address
- Confidence: HIGH (if address is verified mixer)
- Evidence: mixer name, address, incoming/outgoing amounts
- Uncertainty: Output amounts are heuristic correlations only

File: dex_bridge_analysis.py
- Rule: Crossing to DEX or cross-chain bridge
- Types: PROVEN (hash-linked transaction), HEURISTIC_CORRELATION (time/value match)
- Confidence: HIGH (PROVEN), LOW-MEDIUM (HEURISTIC)
- Evidence: transaction hash (if proven), correlation basis (if heuristic)

File: consolidation.py
- Rule: Layered consolidation with pause intervals
- Confidence: MEDIUM (behavioral pattern)
- Evidence: consolidation stages, timing, amounts
```

#### 1.5 VASP Attribution with Adaptive Scoring (Critical)
**Current TraceX State**:
- vasp_cluster.py; static hot-wallet regex matching; single confidence %; no policy versioning

**CryptoTrace LEA Requirement**:
- AdaptiveVASPScorer context weights based on trace characteristics
- Policy-versioned scoring with complete audit trail
- Separate VERIFIED/INFERRED/UNRESOLVED label types
- Full explainability of scoring steps

**Adaptation Tasks**:
```
Location: backend/attribution/

File: adaptive_vasp_scorer.py
- Class: AdaptiveVASPScorer
  
  Methods:
  - score_candidate(vasp_cluster, trace_result, case) -> AttributionScore
    
    AttributionScore:
    - vasp_name: str
    - score: 0-100
    - score_components: dict (breakdown)
    - policy_version: str (e.g., "policy_v1_india_kyc")
    - scoring_steps: List[ScoringStep] (complete audit trail)
    - label_type: VERIFIED|INFERRED|UNRESOLVED
    - confidence_band: CRITICAL|HIGH|MEDIUM|LOW
    
    ScoringStep:
    - step_name: str
    - input_value: any
    - weight: float
    - output_contribution: float
    - reasoning: str
  
  Scoring context factors (adaptive weights):
  - Mixer presence in trace (-30 points if detected)
  - Value magnitude (higher = lower confidence if no label)
  - Label quality (VERIFIED label = +50 base, INFERRED = +20, UNRESOLVED = +5)
  - Hop count to VASP (closer = higher confidence)
  - Exchange jurisdiction (Indian = +10, Tier-1 = +5, Unknown = 0)
  - Hot-wallet pattern match strength (exact = +50, regex = +25, clustering = +10)
  - Recent activity on VASP (within 7 days = +15)
  - Time-to-liquidation risk (< 24 hours = urgent; decrease confidence for attribution)
  
  Base calculation:
  1. Start with hot-wallet pattern match (0-50)
  2. Apply context weights (adaptive adjustment -30 to +50)
  3. Confidence cap based on evidence completeness (if data_completeness < 70%, cap at MEDIUM)
  4. Output score + label_type + detailed scoring steps

File: vasp_registry.py
- Enhanced VASP registry with policy versioning
- Fields per VASP:
  - vasp_id, legal_name, common_names, regions
  - fiu_registration_status (REGISTERED|UNREGISTERED|SUSPENDED)
  - hot_wallet_patterns: {chain: List[{pattern: str, confidence: str}]}
  - known_deposits: {chain: List[{address: str, verified_date: date}]}
  - nodal_officer: {name, email, phone}
  - compliance_contact, emergency_contact
  - regulatory_portals: {country: url}
  - policy_version (e.g., "v1_india_kyc") - for scoring context
  - last_verified_date

File: label_classifier.py
- Classify VASP labels as VERIFIED|INFERRED|UNRESOLVED
- VERIFIED: FIU-registered, address in official compliance registry
- INFERRED: Hot-wallet pattern match with high confidence
- UNRESOLVED: Candidate VASP but no strong evidence
```

#### 1.6 Cross-Chain Analysis with Proven vs Heuristic Distinction (Important)
**Current TraceX State**:
- Treats all cross-chain correlations as heuristic (time/value matching)

**CryptoTrace LEA Requirement**:
- Distinguish PROVEN bridge events (transaction hash linked) from heuristic correlation
- Explicit uncertainty when correlation is inferred

**Adaptation Tasks**:
```
Location: backend/cross_chain/

File: cross_chain_analyzer.py
- Class: CrossChainAnalyzer
  
  Methods:
  - analyze_cross_chain_paths(case_id, traces: {chain: TraceResult}) 
    -> List[CrossChainLink]
  
  CrossChainLink types:
  
  1. PROVEN bridges (LinkType.PROVEN):
     - Event: Bridge contract call on source chain
     - Evidence: Source TX hash → Bridge TX hash → Destination TX hash
     - Confidence: HIGH
     - Data: Exact amounts, timestamps, bridge protocol
     - Examples:
       - Stargate, Across, LayerZero (if we have hash)
       - Official block explorer confirms bridge execution
  
  2. Heuristic correlation (LinkType.HEURISTIC_CORRELATION):
     - Evidence: Time proximity + amount match (within fee tolerance)
     - Confidence: MEDIUM-LOW (depends on uniqueness)
     - Data: Source amount, destination amount, time delta, fee estimate
     - Caveat: Multiple wallets could match same amount/time
  
  Methods:
  - _detect_proven_bridges(chain_traces) -> List[ProvenLink]
  - _detect_heuristic_correlations(chain_traces) -> List[HeuristicLink]
  - _validate_bridge_transaction(tx_hash) -> bool
  - _time_value_match_score(source, dest, time_delta_sec, fee_pct) -> float

File: bridge_registry.py
- Known bridge protocols (Stargate, Across, cBridge, Portal)
- Bridge contract addresses by chain
- Bridge function signatures for event detection
- Fee estimation for each bridge type
```

---

### PHASE 2: Investigator Experience (APIs & Dashboards)

**Objective**: Build case intake workflows, investigator dashboards, and evidence interfaces.

#### 2.1 Case Intake and Validation APIs (Important)
**Current TraceX State**:
- POST `/api/trace` (no case pre-registration)

**CryptoTrace LEA Requirement**:
- Separate case creation from trace execution
- Case linkage to complaints/NCRP bulletins
- Provenance tracking (who submitted, when, from where)

**Adaptation Tasks**:
```
Location: backend/api/

File: case_routes.py
- POST /api/v1/cases
  Input: CaseIntakeRequest
    - source: "COMPLAINT"|"NCRP_BULLETIN"|"SAHYOG"
    - chain: str
    - suspect_wallet: str
    - reported_amount: float (optional)
    - complaint_text: str
    - complainant_name: str (optional)
    - fir_number: str (optional)
    - investigating_officer: str
    - case_notes: str
  Output: Case (with case_id, created_timestamp)
  Actions: Create case record, validate wallet format
  
- GET /api/v1/cases/{case_id}
  Output: Case + current trace status
  
- GET /api/v1/cases
  Query: status, chain, assigned_to, date_range
  Output: List[Case] (paginated)
  
- PUT /api/v1/cases/{case_id}
  Input: Case updates (notes, assignment, status)
  Output: Case (updated)
  Audit: Record update action

File: trace_routes.py
- POST /api/v1/cases/{case_id}/trace
  Input: TraceRequest
    - max_hops, time_window, constraints
    - execution_mode: "LIVE"|"DEMO" (if demo_data on case, force DEMO)
  Output: TraceResult (async; returns trace_id)
  Actions: Queue trace job, monitor progress
  
- GET /api/v1/traces/{trace_id}/status
  Output: {status: "PENDING"|"IN_PROGRESS"|"COMPLETED"|"FAILED", progress_pct}
  
- GET /api/v1/traces/{trace_id}/result
  Output: Fully hydrated TraceResult + all findings
  
- GET /api/v1/traces/{trace_id}/graph
  Output: Graph JSON (for visualization)
```

#### 2.2 Investigation Dashboard (Important)
**Current TraceX State**:
- dashboard.html; vis-network graph; AI copilot chat drawer; notice generator modal

**CryptoTrace LEA Requirement**:
- Investigator workstation design (evidence-first, graph-centric)
- Separate risk/attribution panels
- Uncertainty and data completeness visibility
- Supervisor approval indicators

**Adaptation Tasks**:
```
Location: frontend/src/

File: InvestigatorDashboard.vue (or React equivalent)
- Layout:
  1. Top: Case header (case ID, source, chain, wallet, reported amount, status)
  2. Left: Case controls (timeline, filters, notes)
  3. Center: Fund-flow graph (vis-network or D3)
  4. Right: Information panels (tabbed)
     - Attribution & Risk
     - Findings (typologies, VASP candidates)
     - Cross-Chain Analysis
     - Evidence & Provenance
     - Recommendations
     - Audit History
  5. Bottom: Evidence manifest + raw payload links
  
File: components/CaseHeader.vue
- Display: case_id, source, chain, wallet, reported_amount, LIVE/FIXTURE badge
- Actions: Edit notes, assign case, change status

File: components/FundFlowGraph.vue
- Visualization using vis-network or D3
- Node types:
  - 🔴 Suspect wallet (starting point)
  - 🟡 Intermediary (unknown)
  - 🔵 VASP candidate
  - ⚫ Mixer (Tornado Cash, etc.)
  - 🟢 Known exchange (FIU-registered)
- Edge labels: TX hash, amount, asset, timestamp
- Click to expand evidence, show raw payload hash

File: components/AttributionPanel.vue
- Display: VASP candidates ranked by AdaptiveVASPScorer
- For each candidate:
  - VASP name + logo
  - Score (0-100) + label_type (VERIFIED|INFERRED|UNRESOLVED)
  - Confidence band (CRITICAL|HIGH|MEDIUM|LOW)
  - Scoring breakdown (expandable)
  - Policy version reference
  - Nodal officer contact info

File: components/RiskPanel.vue
- Display: Risk score (0-100) + risk_category
- Component breakdown (pie chart)
- Contributing findings (links to typologies)

File: components/FindingsPanel.vue
- List all detected typologies
- For each finding:
  - Typology name (MULE_NETWORK, PEEL_CHAIN, etc.)
  - Confidence level with India-specific context
  - Evidence cards (expandable)
  - Uncertainty notes
  - Data completeness percentage
  - "Add to Recommendation" action

File: components/RecoveryEstimatePanel.vue
- Display RecoveryAssessment (if eligible)
- Show: recovery_score, action_window_hours, display_tier
- Disclaimer (clearly marked)
- Urgency visual (progress bar, countdown)

File: components/EvidencePanel.vue
- Evidence manifest table
  - Event ID, Type, Provider, Payload Hash, Verified Date
  - "Verify Integrity" action (recompute hash)
  - Download raw payload JSON

File: components/AuditPanel.vue
- Timeline of case actions
- User, action, resource, timestamp, result
- Search/filter capabilities
```

#### 2.3 Notice Generation (Draft-Only, Supervisor-Gated) (Important)
**Current TraceX State**:
- Auto-generates Section 91 notices with no approval gate

**CryptoTrace LEA Requirement**:
- Draft-only output (cannot auto-submit)
- Supervisor approval required
- Explicit preservation-request workflow gating

**Adaptation Tasks**:
```
Location: backend/legal/

File: notice_generator.py
- Class: NoticeGenerator
  
  Methods:
  - draft_preservation_request(case_id, trace_id, investigating_officer_id) 
    -> PreservationRequestDraft
    
    PreservationRequestDraft:
    - draft_id, case_id, created_by, created_timestamp
    - recipient_vasp, recipient_email, recipient_phone
    - legal_authority: "SECTION_91_BNSS_2023"|"SECTION_91_CrPC"
    - demanded_items: List[str]
      - "Immediate freeze of wallet address X"
      - "KYC disclosure (Aadhaar, PAN, Passport)"
      - "Transaction logs for wallet X"
      - "Linked bank accounts and beneficiaries"
      - "IP logs, device fingerprints, login history"
    - transaction_references: List[{tx_hash, amount, timestamp}]
    - supporting_evidence_links: List[{finding_type, finding_id}]
    - draft_text: str (formatted notice)
    - status: "DRAFT"|"PENDING_APPROVAL"|"APPROVED"|"REJECTED"
  
  Methods:
  - submit_for_approval(draft_id, supervisor_id)
  - approve_draft(draft_id, supervisor_id, approval_notes)
  - reject_draft(draft_id, supervisor_id, rejection_reason)
  - export_as_pdf(draft_id) -> bytes
  - export_as_plaintext(draft_id) -> str
  - send_to_vasp(draft_id, via: "EMAIL"|"PORTAL"|"CERTIFIED_MAIL")

File: notice_routes.py
- POST /api/v1/cases/{case_id}/draft-notice
  Input: {trace_id, investigating_officer_id}
  Output: PreservationRequestDraft (status=DRAFT)
  Requires: INVESTIGATOR role
  
- GET /api/v1/notices/{draft_id}
  Output: PreservationRequestDraft
  
- POST /api/v1/notices/{draft_id}/submit-for-approval
  Output: PreservationRequestDraft (status=PENDING_APPROVAL)
  Requires: INVESTIGATOR role
  
- POST /api/v1/notices/{draft_id}/approve
  Input: {supervisor_id, approval_notes}
  Output: PreservationRequestDraft (status=APPROVED)
  Requires: SUPERVISOR role
  Audit: Record approval
  
- POST /api/v1/notices/{draft_id}/reject
  Input: {supervisor_id, rejection_reason}
  Output: PreservationRequestDraft (status=REJECTED)
  Requires: SUPERVISOR role
  
- GET /api/v1/notices/{draft_id}/export
  Query: format ("pdf"|"txt")
  Output: File download
  Audit: Record export
```

#### 2.4 Evidence and Provenance Interfaces (Important)
**Current TraceX State**:
- Limited provenance tracking; no raw payload inspection

**CryptoTrace LEA Requirement**:
- Raw payload verification interface
- Evidence manifest with SHA-256 verification
- Audit trail for all material actions

**Adaptation Tasks**:
```
Location: frontend/src/components/

File: EvidenceManifestPanel.vue
- Table of all events in case
- Columns: Event ID, Type, Provider, Payload Hash, Serialized Date, Status
- Actions per row:
  - "View Raw Payload" → download JSON
  - "Verify Integrity" → recompute SHA-256, compare
  - "View Source" → link to external explorer/provider

File: RawPayloadViewer.vue
- Side panel showing raw JSON (formatted, read-only)
- Display: Provider name, fetch timestamp, payload hash
- Verification status (✓ matches computed | ✗ hash mismatch)
- "Download" button (JSON file)

File: AuditTrailTimeline.vue
- Chronological list of all case actions
- Columns: Timestamp, User, Action, Resource, Result, Details
- Filter by user, action type, time range
- "View Details" expands full record
```

---

### PHASE 3: Live Connectivity and Resilience

**Objective**: Connect live blockchain providers, implement checkpoint recovery, handle finality.

**Note**: Largely parallel to TraceX; adapt for PostgreSQL and provenance requirements.

---

### PHASE 4A & 4B: External Boundaries & Governance (Post-Launch Scope)

**Objective**: NCRP/SAHYOG/VASP request workflows and case-outcome labeling.

**Note**: These are conditional on successful SIH 26183 demonstration.

---

## DETAILED MIGRATION CHECKLIST

### Database Schema Migration
```
PostgreSQL Migration Files (backend/db/migrations/):

001_initial_schema.sql
  - Create all canonical tables (cases, transactions, transfers, etc.)
  - Add constraints, indexes, triggers

002_audit_tables.sql
  - Create audit_events, audit_signatures
  - Create audit trigger functions

003_indices.sql
  - Index on (chain_id, tx_hash) for transfers
  - Index on (from_addr, chain_id) for tracing
  - Index on (case_id) for case queries
  - Index on (demo_data) for filtering

Migration Test Suite:
  - Verify schema matches domain models
  - Test backward-compat read of legacy TraceX SQLite
  - Test audit trigger functionality
  - Benchmark query performance
```

### Code Reorganization
```
Current TraceX Structure:
  tracex-sahyog/
    ├── app.py
    ├── engine/
    │   ├── address_validator.py
    │   ├── graph_tracer.py
    │   ├── vasp_cluster.py
    │   ├── real_api.py
    │   ├── ai_copilot.py
    │   ├── notice_generator.py
    │   ├── ofac_sanctions.py
    │   ├── neo4j_engine.py
    │   ├── price_feed.py
    │   ├── api_tester.py
    │   ├── key_manager.py
    │   ├── demo_cases.py
    ├── dashboard.html
    └── data/

New CryptoTrace LEA Structure:
  cryptotrace-lea/
    ├── backend/
    │   ├── app.py (FastAPI entry point)
    │   ├── config/
    │   │   ├── base.py
    │   │   ├── development.py
    │   │   ├── staging.py
    │   │   ├── production.py
    │   ├── models/
    │   │   ├── domain_models.py
    │   │   ├── confidence_types.py
    │   │   ├── __init__.py (exports)
    │   ├── auth/
    │   │   ├── jwt_handler.py
    │   │   ├── rbac.py
    │   │   ├── decorators.py
    │   ├── db/
    │   │   ├── migrations/
    │   │   ├── connection.py
    │   │   ├── models.py (SQLAlchemy ORM)
    │   ├── audit/
    │   │   ├── audit_engine.py
    │   │   ├── audit_logger.py
    │   ├── storage/
    │   │   ├── raw_payload_storage.py
    │   │   ├── evidence_manifest.py
    │   ├── adapters/
    │   │   ├── chain_adapter_base.py
    │   │   ├── evm_adapter.py
    │   │   ├── bitcoin_adapter.py
    │   │   ├── tron_adapter.py
    │   │   ├── provider_manager.py
    │   ├── tracing/
    │   │   ├── trace_engine.py
    │   │   ├── graph_builder.py
    │   │   ├── path_finder.py
    │   ├── typologies/
    │   │   ├── typology_engine.py
    │   │   ├── rules/
    │   │   │   ├── mule_network.py ⭐ MAIN INNOVATION
    │   │   │   ├── peel_chain.py
    │   │   │   ├── fan_in.py
    │   │   │   ├── fan_out.py
    │   │   │   ├── rapid_hop.py
    │   │   │   ├── mixer_boundary.py
    │   │   │   ├── dex_bridge_analysis.py
    │   │   │   ├── consolidation.py
    │   ├── attribution/
    │   │   ├── adaptive_vasp_scorer.py ⭐ MAIN INNOVATION
    │   │   ├── vasp_registry.py
    │   │   ├── label_classifier.py
    │   ├── cross_chain/
    │   │   ├── cross_chain_analyzer.py
    │   │   ├── bridge_registry.py
    │   ├── assessment/
    │   │   ├── risk_assessment.py
    │   │   ├── recovery_estimate.py ⭐ MAIN INNOVATION
    │   ├── api/
    │   │   ├── case_routes.py
    │   │   ├── trace_routes.py
    │   │   ├── findings_routes.py
    │   │   ├── notice_routes.py
    │   │   ├── evidence_routes.py
    │   │   ├── audit_routes.py
    │   ├── legal/
    │   │   ├── notice_generator.py
    │   │   ├── preservation_workflow.py
    │   ├── fixtures/
    │   │   ├── demo_cases_v2.py
    │   │   ├── fixture_loader.py
    │   ├── tests/
    │   │   ├── unit/
    │   │   ├── integration/
    │   │   ├── fixtures/
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   │   ├── InvestigatorDashboard.vue
    │   │   │   ├── CaseHeader.vue
    │   │   │   ├── FundFlowGraph.vue
    │   │   │   ├── AttributionPanel.vue
    │   │   │   ├── RiskPanel.vue
    │   │   │   ├── FindingsPanel.vue
    │   │   │   ├── RecoveryEstimatePanel.vue
    │   │   │   ├── EvidencePanel.vue
    │   │   │   ├── NoticeGeneratorModal.vue
    │   │   ├── views/
    │   │   │   ├── InvestigatorWorkstation.vue
    │   │   │   ├── SupervisorReview.vue
    │   │   │   ├── CaseHistory.vue
    │   │   ├── services/
    │   │   │   ├── api_client.js
    │   │   │   ├── graph_renderer.js
    │   │   ├── App.vue
    │   │   ├── main.js
    ├── docker/
    │   ├── Dockerfile.backend
    │   ├── Dockerfile.frontend
    │   ├── docker-compose.yml
    ├── docs/
    │   ├── API.md
    │   ├── DEPLOYMENT.md
    │   ├── ARCHITECTURE.md
    ├── .env.example
    ├── README.md
```

### Data Migration Path
```
Step 1: Export existing TraceX SQLite investigations to JSON
  Script: backend/scripts/export_legacy_tracex.py
  Output: data/legacy_cases.json
  
Step 2: Map legacy fields to new schema
  Script: backend/scripts/migrate_legacy_to_postgres.py
  Actions:
    - Read legacy JSON
    - Create Case records (source="LEGACY_TRACEX")
    - Create Transfer records from trace payloads
    - Mark all with demo_data=false, created_date=today
    - Note in case_notes: "Migrated from TraceX v2.0-PRO"
  
Step 3: Verify migration integrity
  Script: backend/scripts/verify_migration.py
  Checks:
    - Transaction counts match
    - Fund flow totals match
    - No duplicate transfers
    - All raw payloads accessible
  
Step 4: Parallel running (TraceX + CryptoTrace LEA)
  - Keep TraceX running in staging
  - Shadow new queries through both systems
  - Compare results
  - Cutover once confidence is high
```

---

## INTEGRATION REQUIREMENTS: KEY APIS TO KEEP

```
From TraceX (Mostly Reusable):
✅ Etherscan API (EVM provider)
✅ TronGrid API (TRON provider)
✅ Blockstream Esplora (Bitcoin provider)
✅ CoinGecko API (Pricing)
✅ OFAC Sanctions (for screening)
✅ Chainabuse API (crowdsourced malicious addresses)
✅ Google Gemini API (optional; AI reasoning - keep as fallback only)
✅ Groq LLM (optional; keep as fallback only)
⚠️ Neo4j Aura (optional; keep for graph visualization but not primary storage)
❌ Bitquery (can be replaced with chain-specific APIs)

To Add/Enhance (CryptoTrace LEA):
🆕 Additional RPC providers for finality detection
🆕 Mempool.space for Bitcoin transaction status
🆕 TronWeb for Tron state queries
🆕 Bridge protocol APIs (Stargate, Across) for proven bridge detection
```

---

## ACCEPTANCE CRITERIA: MIGRATION SUCCESS

```
Phase 0 Foundation:
☐ PostgreSQL migrations run without errors
☐ All secrets removed from source code
☐ RBAC enforced on all endpoints
☐ Audit logging records all material actions
☐ Fixture data clearly marked (demo_data=true)
☐ Configuration loads from environment only

Phase 1 Domain Models:
☐ All 12 canonical domain models defined and tested
☐ Chain adapters implemented for EVM, Bitcoin, TRON
☐ Canonical event identity enforced (5-field uniqueness)
☐ Raw payload storage with SHA-256 verification working
☐ Trace engine respects all bounded constraints
☐ MULE_NETWORK typology implemented with India-specific confidence cap
☐ AdaptiveVASPScorer produces fully explainable output
☐ Cross-chain links distinguish PROVEN vs HEURISTIC

Phase 2 UI:
☐ Case intake form working with validation
☐ Investigation dashboard displays all required panels
☐ Evidence manifest table queryable and verifiable
☐ Attribution panel shows scoring breakdown
☐ Risk panel displays component scores
☐ Notice generator produces draft-only output
☐ Supervisor approval workflow enforced

Phase 3 Connectivity:
☐ All 5 blockchain providers tested for connectivity
☐ Checkpoint recovery implemented and tested
☐ Finality state machine working (PENDING/CONFIRMED/FINALIZED)
☐ Live mode produces identical results to fixture mode (except data source)
☐ Rate limiting and fallover working

Demonstration Requirements (SIH 26183):
☐ MULE_NETWORK detection working on demo case
☐ AdaptiveVASPScorer showing context-weighted results
☐ RecoveryProbabilityScore computed and displayed
☐ Uncertainty explicitly shown (MEDIUM confidence on heuristic patterns)
☐ Supervisor approval gate on notice generation
☐ All three innovations named and explained before technical walkthrough
```

---

## TIMELINE ESTIMATE

```
Phase 0 (Foundation): 2 weeks
  - Database setup, migrations, RBAC
  - Audit framework
  - Secret management
  
Phase 1 (Domain Models): 4 weeks
  - Model definitions
  - Chain adapters (EVM, Bitcoin, TRON)
  - Trace engine
  - Typologies (MULE_NETWORK focus)
  - AdaptiveVASPScorer
  
Phase 2 (UI & APIs): 3 weeks
  - Case intake
  - Dashboard components
  - Evidence interfaces
  - Notice generator
  
Phase 3 (Live & Resilience): 2 weeks
  - Provider connectivity
  - Checkpoint recovery
  - Finality handling
  
Phase 6 (Demo Rehearsal): 1 week
  - End-to-end testing
  - Presentation script
  - Fixture case walkthrough
  
**Total: 12 weeks** (assuming full-time team of 3-4)
```

---

## FINAL RECOMMENDATIONS

### What to Keep from TraceX
- API provider integrations (Etherscan, TronGrid, Esplora, CoinGecko)
- Address validation logic
- VASP registry structure (enhance with policy versioning)
- Demo case framework (adapt with demo labeling)
- Notice generation core (add draft-only + approval gate)
- Frontend technology stack (Vue/React + vis-network)

### What to Replace Completely
- Single-user architecture → RBAC
- Flat JSON storage → Normalized PostgreSQL schema
- Auto-action notices → Draft-only with supervisor approval
- Generic FATF typologies → MULE_NETWORK as centerpiece
- Static VASP scoring → AdaptiveVASPScorer with policy versioning
- AI as core capability → AI as optional (rule-based primary)

### What to Add
- Raw payload storage with deterministic hashing
- Proven vs Heuristic cross-chain distinction
- RecoveryProbabilityScore (victim-impact translation)
- Complete audit trail with chained signatures
- Checkpoint/resume tracing capability
- Data completeness visibility
- Explicit uncertainty bounds on all findings
- Evidence manifest with integrity verification

---

This strategy document maps the ~70% code overlap while clearly delineating the 30% architectural and conceptual changes needed to align TraceX with CryptoTrace LEA's evidence-first, explainability-focused, human-supervised design.

