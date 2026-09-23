# CryptoTrace LEA — Master Phased Implementation Plan

**Project:** SIH 26183 — Real-Time Crypto Fraud Attribution System for Indian Law Enforcement  
**Related PRD:** `CRYPTOTRACE_LEA_PRD.md`  
**Explanation Document:** `CRYPTOTRACE_LEA_EXPLANATION.docx`  
**Authority:** `CRYPTOTRACE_LEA_MASTER_GUIDE_v3.md`

---

## 0. Implementation Control Rules

This plan is intentionally phase-gated.

1. Do not skip prerequisites.
2. Do not implement a later phase by assumption.
3. Do not claim live integration without operational evidence.
4. Do not replace deterministic, explainable functionality with ML prematurely.
5. Do not use synthetic fixtures as production evidence.
6. Every phase must end with a verification report.
7. Functional implementation, tests, documentation, and Git state must agree.
8. If a requirement cannot be verified, mark it `NOT VERIFIED` or `PARTIAL`.
9. Never expose secrets in source, logs, fixtures, reports, or commits.
10. Preserve the signed-off baseline unless a defect is verified.

---

## 1. Phase Map

| Phase | Name | Gate |
|---|---|---|
| 0 | Foundation Hardening | Persistence, RBAC, audit, configuration, safety |
| 1 | Domain Models and Core Intelligence | Canonical entities, adapters, tracing, typologies |
| 2 | Investigator Experience | APIs, dashboards, evidence and case workflows |
| 3 | Live Connectivity and Resilience | Live providers, checkpoints, finality, reorg, alerts, WebSockets |
| 4A | Authorized External Boundaries | NCRP, SAHYOG, VASP request workflow |
| 4B | Evidence and Outcome Governance (Non-ML) | Case-outcome schema, labeling, provenance, data-quality governance |
| 5 | Post-Launch Intelligence Enhancement | Outside SIH submission scope — conditional on post-launch labeled case accumulation |
| | **Note** | This phase is not part of the SIH 26183 submission. It is documented here as a future product direction only. It must not appear in any SIH presentation, demo script, or evaluation submission as a delivered or in-progress capability. |
| 6 | Hardening and Demonstration | Security, performance, deployment, demo rehearsal |

The post-launch intelligence roadmap is intentionally outside the SIH submission scope. It is not scheduled in the sequential delivery timeline, Gantt chart, presentation, demo script, or evaluation submission. Any future ML work must first satisfy the PRD governance gate and the Master Guide.

---

## 2. Phase 0 — Foundation Hardening

### Objectives

Establish a safe, persistent, auditable foundation.

### PRD Mapping

`FR-003`, `FR-004`, `FR-011`, `FR-013`, `NFR-001`, `NFR-002`, `NFR-006`

### Workstreams

- Configuration and environment separation.
- Database connection and migrations.
- Canonical RBAC roles.
- Audit event schema and chained integrity.
- Graph safety boundaries.
- Secret sanitization.
- Error envelope and request correlation.
- Test fixtures with explicit demo labels.

### Required Outputs

- Migration baseline.
- Configuration validation.
- Role enforcement.
- Audit verification utility.
- Security test suite.
- Foundation verification report.

### Exit Criteria

- Database migrations are reproducible.
- Unauthorized roles are rejected.
- Secrets are not present in tracked files or logs.
- Audit chain integrity can be verified.
- Fixture data is visibly classified.

---

## 3. Phase 1 — Domain Models and Core Intelligence

### Objectives

Implement canonical crypto entities and deterministic intelligence.

### PRD Mapping

`FR-002`, `FR-004`, `FR-005`, `FR-006`, `FR-007`, `FR-008`, `FR-009`, `FR-010`

### Workstreams

#### 3.1 Canonical Models

- Chain
- Address
- Transaction
- Transfer
- Asset
- EntityLabel
- PatternFinding
- VASPCluster
- CrossChainLink
- RiskAssessment
- InvestigativeRecommendation
- EvidenceManifest
- Case

#### 3.2 Chain Adapters

- EVM
- Bitcoin UTXO
- Tron/TRC-20
- Solana boundary only if evidence-supported

Each adapter must normalize into the canonical model and retain source provenance.

#### 3.2-A Canonical Event Identity and Raw Payload Serialization

Every canonical event identity contains five fields: `chain_id`, `tx_hash`, `event_type`, an event-type-specific index field, and `transfer_index`. `event_type` is one of `NATIVE`, `ERC20`, `TRC20`, `INTERNAL`, or `BRIDGE`. ERC20/TRC20 use integer `log_index`; NATIVE uses integer `transfer_index` starting at `0` per transaction; INTERNAL uses integer `trace_index` following provider ordering; BRIDGE uses the protocol message nonce where available, otherwise integer `log_index`. The fifth field is the secondary integer `transfer_index` for multiple canonical transfers sharing a log index, such as batch-transfer contracts. PostgreSQL uniqueness covers all five identity fields.

Chain-specific identity rules must be documented before ingestion is enabled for each supported chain; any future chain must define its identity rules before activation. Raw JSON is deterministically serialized with alphabetically sorted keys, compact output, and no whitespace before SHA256 hashing.

#### 3.3 Trace Engine

Implement bounded BFS/graph tracing with:
- hop limit;
- time window;
- value threshold;
- outflow limit;
- node limit;
- timeout;
- deterministic ordering;
- provenance per path item.

#### 3.4 Typology Engine

Implement versioned rules for:
- peel chain;
- fan-in;
- fan-out;
- rapid-hop;
- consolidation;
- mixer exposure;
- `MIXER_BOUNDARY_CLUSTER_LEAD`;
- DEX boundary;
- bridge-mediated movement;
- `MULE_NETWORK` as a named India-specific detection pattern.

For `MIXER_BOUNDARY_CLUSTER_LEAD`, query the same mixer pool from deposit time through +14,400 seconds and return withdrawals with payout amount between 0.90 and 0.995 of the deposit denomination. Every lead is fixed at confidence `0.25`, band `LEAD`, and must retain the exact heuristic uncertainty note required by PRD FR-006. Render the graph relationship as dashed with hover label **Possible Exit — Heuristic Only**.

For `MULE_NETWORK`, require at least three suspect-origin wallets and the specified intermediate-wallet behavioral properties. A single large inflow exceeds five times the median inbound transfer value for all addresses active on that chain in the same seven-day window; if the median is unavailable, use the policy-configured USD floor of `500`. A previously unseen address is one whose first recorded transaction in indexed history is the transfer in question; if indexing begins later than possible historical activity, include the earliest indexed block height in `data_coverage_note`. Evaluate native and token transfers separately; produce separate linked findings when both asset types are involved. Normalize network fees using the actual gas cost in USD at the block timestamp before applying the 20% amount-similarity tolerance. Mark incomplete wallet history `PARTIAL` with the earliest indexed block height and show a UI warning. A known exchange aggregation address must link its VASP label and note that it is a labelled exchange without changing confidence. Distinguish `complaint_linked` and `behavior_only` wallets. Complaint linkage increases investigative weight but does not raise the fixed `MEDIUM` confidence cap. Emit the PRD-required fields, set `india_specific = true`, and cap confidence at `MEDIUM`.

#### 3.5 VASP Intelligence

Maintain:
- labelled;
- inferred;
- unresolved.

Implement **AdaptiveVASPScorer** from PRD FR-007-A using the mandatory six-step order: load versioned policy; apply the `SINGLE_HOP` structural override with hard precedence; apply contextual multipliers alphabetically (`HIGH_VALUE`, `INDIA_EXCHANGE`, `LONG_HOP`, `MIXER_PATH`, `SPARSE_LABEL`); resolve same-dimension conflicts conservatively; clamp weights to `0.01–0.80`; and renormalize to exactly `1.0` before scoring. `path_contains_bridge` is recorded but has no current multiplier. Persist every step and policy version in `scoring_metadata`. Unit tests must cover SINGLE_HOP alone, MIXER_PATH alone, SINGLE_HOP + MIXER_PATH, HIGH_VALUE + SPARSE_LABEL, LONG_HOP + INDIA_EXCHANGE, and rejection of zero-hop traces before scoring.

No inferred relationship may be displayed as verified ownership.

### Exit Criteria

- Canonical models have schema tests.
- Tracing is bounded and deterministic.
- Typology findings include evidence references.
- Cross-chain proof and heuristic correlation are separated.
- Risk and attribution are separate outputs.

---

## 4. Phase 2 — Investigator Experience

### Objectives

Turn deterministic intelligence into a usable investigator workstation and a coherent complaint-to-action demonstration flow.

### PRD Mapping

`FR-010`, `FR-012-A`, `FR-014`, `FR-016`, `NFR-003`, `NFR-005`

### Workstreams

- Case APIs.
- Trace APIs.
- Pattern and VASP APIs.
- Cross-chain APIs.
- Risk and recommendation APIs.
- Evidence manifest APIs.
- Supervisor decision APIs.
- Case intake modal.
- Transaction detail drawer.
- Findings panel.
- Attribution evidence panel.
- Audit timeline.
- Legal notice modal.
- Fund-flow graph.
- Timeline playback.
- Hop-depth filters.
- Alert triage.
- RecoveryProbabilityScore computation, persistence, first-position dashboard metric, component tooltip, disclaimer, and supervisor queue sorting by ascending `action_window_hours`.
- Mock NCRP Complaint Flow active only in DEMO_MODE, including one-click fixture trigger, source badges, and API-level `demo_data=true`.

#### 2.1 Attribution and Recovery

Implement the **RecoveryProbabilityScore** required by PRD FR-016 for qualifying completed traces. Store `recovery_score`, `value_ratio`, `exchange_cooperation`, `time_urgency`, `path_clarity`, `action_window_hours`, and `display_tier` in PostgreSQL. The frontend component must use **Heuristic Recovery Estimate** as the primary label; `Recovery Probability` may appear only as secondary text with **(not a statistical probability)**. Include administrator estimate source, review date, reviewer identity, and the exact cooperation tooltip text. Implement the required zero/missing amount, future/missing incident time, zero-hop rejection, and LEAD/NONE attribution boundary behavior. Make the score the first visible case metric when computed and enable supervisor queue sorting by `action_window_hours` ascending.

The VASP cooperation registry must be administrator-reviewable, source-attributed, date-stamped, and configuration-driven.

#### 2.2 Mock NCRP Complaint Flow

When `DEMO_MODE = true`, implement the controlled NCRP mock intake defined by PRD FR-012-A.

- Validate the realistic complaint schema and `NCRP-YYYY-XXXXXX` complaint IDs.
- Create the case with `source = NCRP_INTAKE` and queue the reported wallet for tracing.
- Return HTTP `201`, `case_id`, confirmation, and `demo_data = true`.
- Provide a no-payload one-click fixture trigger for the presentation.
- Keep all demo-mode intake visibly marked **DEMO DATA**.
- Render source badges: NCRP blue, Manual Entry grey, SAHYOG purple.

### UX Rules

- Clearly display LIVE vs FIXTURE REPLAY.
- Use blockchain identifiers in monospace.
- Use restrained color and semantic badges.
- Avoid repetitive cards and generic AI dashboard styling.
- Use progressive disclosure for complex evidence.
- Display confidence, uncertainty, finality, and provenance.
- Never present an inferred VASP as a confirmed owner.
- Show `RecoveryProbabilityScore` first on qualifying cases and make its action window operationally visible.
- Show `MULE_NETWORK` as an amber **India Fraud Pattern** finding.
- Show mixer-boundary heuristic leads as dashed graph edges with **Possible Exit — Heuristic Only**.
- Show demo warm results with the yellow **FIXTURE REPLAY** badge and every mock NCRP response with **DEMO DATA**.

### Exit Criteria

- All APIs have authentication and role checks.
- Investigator can trace and inspect a case.
- Supervisor actions are visibly separated.
- Evidence and provenance are accessible.
- Frontend build completes successfully.
- UX verification includes screenshots or a documented manual walkthrough.

---

## 5. Phase 3 — Live Connectivity and Resilience

### Objectives

Provide continuously updated blockchain intelligence with failure and reorg resilience.

### PRD Mapping

`FR-003`, `FR-004`, `FR-005`, `FR-006`, `FR-014`, `NFR-002`, `NFR-004`, `NFR-005`, `NFR-007`

### Workstreams

#### 3.1 Confirmed Live Provider Backbone

The SIH demo uses the following already-secured infrastructure; no provider procurement work remains:

- `ETH_RPC_PRIMARY_URL` — Ethereum mainnet WebSocket + HTTP.
- `POLYGON_RPC_PRIMARY_URL` — Polygon PoS WebSocket + HTTP.
- `TRON_RPC_PRIMARY_URL` — Tron full-node HTTP polling.
- `TRON_GRID_API_KEY` — TronGrid TRC-20 event indexing.
- `ETHERSCAN_API_KEY` — historical Ethereum address lookup and label enrichment only; never part of the live event path.
- Mempool.space — Bitcoin, no authentication required.
- CoinGecko — pricing, no authentication required.

Ethereum and Polygon run independent async `newHeads` subscription tasks. Tron runs an independent 3-second HTTP polling task. Historical/label/pricing services are isolated auxiliary workers. A failure on one chain/provider must not stop another chain.

#### 3.2 Eight-Stage Pipeline Contract

All confirmed chain providers run independently and concurrently. The pipeline stages are a contract, not a descriptive checklist.

**Stage 1 — FETCH**
Pull raw block or event data from the confirmed provider.

**Stage 2 — VALIDATE**
Require block number greater than the last checkpoint, correct transaction-hash length for the chain, syntactically valid addresses, and non-negative value. Reject and log every validation failure with the reason and `chain_id`.

**Stage 3 — EXTRACT**
Identify all transfers in the block: native value transfers, EVM ERC-20 `Transfer` events using topic `0xddf252ad`, Tron TRC-20 `Transfer` events, and provider-returned internal traces. Tag each extraction `NATIVE`, `ERC20`, `TRC20`, or `INTERNAL`.

**Stage 4 — NORMALIZE**
Convert every extracted transfer into the canonical `Transfer` model. Persist `raw_amount` as a string, never a float. Serialize raw JSON with alphabetically sorted keys, compact output, and no whitespace, then hash it with SHA256. Store payloads at `raw/chain_id/block_height/tx_hash/provider_name/payload_type/payload_hash.json`.

**Stage 5 — DEDUPLICATE**
Use the canonical five-field event identity: `chain_id`, `tx_hash`, `event_type`, event-type-specific index (`log_index`, `transfer_index`, `trace_index`, or bridge nonce/log index), and secondary `transfer_index`. Redis DB1 catches recent duplicates quickly with a seven-day TTL. PostgreSQL is authoritative and permanently guarantees correctness through a database-level UNIQUE constraint on `(chain_id, tx_hash, log_index, event_type, transfer_index)`; any violation is silently rejected and logged as `DUPLICATE_SUPPRESSED`. A durable retry record supports replay of claimed-but-uncommitted events.

**Stage 6 — PERSIST**
Write PostgreSQL first, then graph store. Never reverse this order. Any write failure places the event on a durable retry structure; it is never silently discarded.

**Stage 7 — COMMIT**
Update the chain checkpoint with `last_block_height`, `last_block_hash`, and `updated_at`. This checkpoint is the restart boundary.

**Stage 8 — ADVANCE**
Publish the normalized transfer to the downstream consumer topic so the typology engine, tracer, and alert engine can consume it without polling.

#### 3.3 Redis Cache Layer Contract

Redis namespaces are isolated and must never be mixed.

**DEDUP**
- Key: `dedup:chain_id:tx_hash:log_index`
- Value: integer `1`
- TTL: 7 days
- Redis DB: `1`
- Eviction: none

**HOT_ADDR**
- Key: `addr:chain_id:address`
- Value: JSON `{balance,address_type,label_name,label_source,label_confidence,last_seen_block,risk_tier}`
- TTL: 300 seconds
- Redis DB: `0`
- Eviction policy: `allkeys-lru`
- Cache miss source: PostgreSQL only; never a live provider round-trip.
- Explicitly invalidate when a new confirmed transaction touches the address.

**TRACE_RESULT**
- Key: `trace:chain_id:address:hop_limit:time_window_days`
- TTL: 1800 seconds
- Redis DB: `0`
- Maintain Set index `trace_addr_index:chain_id:address` containing all trace keys that include the address.
- On a new confirmed transaction, invalidate all affected trace keys through the index, then delete the index itself.

**VASP_LABEL**
- Key: `vasp_label:chain_id:address`
- Value: `EntityLabel` JSON
- TTL: 86400 seconds
- Redis DB: `0`
- PostgreSQL label registry is the source of truth. Delete the Redis key explicitly when a registry label changes.

**DEMO_WARM**
- Key: `demo_warm:fixture_name`
- Value: precomputed `TraceResult` JSON
- TTL: 14400 seconds
- Redis DB: `0`
- Active only when `DEMO_MODE = true`. On startup in demo mode, iterate all fixtures in `crypto/fixtures/`, precompute trace results, and warm the cache. Matching fixture-wallet trace requests return the warm result immediately without BFS. The UI must display the yellow **FIXTURE REPLAY** badge.

For namespaces using Redis DB 0, configure `maxmemory = 2GB` and `allkeys-lru`.

#### 3.4 Storage Architecture Contract

- **PostgreSQL:** sole durable system of record for cases, evidence items, audit events, ingestion checkpoints, VASP preservation requests, case outcomes, recovery scores, user decisions, and label registry entries.
- **Memgraph/Neo4j:** reconstructable traversal projection for address relationships, transaction path edges, entity clusters, VASP deposit clusters, and bridge links. Every graph node/edge must map to PostgreSQL.
- **Redis:** speed/coordination only; all data reconstructable from PostgreSQL.
- **Object storage:** write-once archive of raw provider JSON. Store each response under a deterministic `chain_id/block_height/tx_hash` path and persist its SHA256 as `raw_payload_hash` in PostgreSQL.

Add an operational **graph rebuild procedure** that clears the graph projection and reconstructs it from PostgreSQL without loss of nodes or edges.

#### 3.5 Reliability and Operational Controls

- Provider failover with bounded exponential backoff capped at 60 seconds.
- Circuit breaker: more than 10 validation failures in 60 seconds pauses ingestion for that chain for 120 seconds and emits an operator alert.
- Finality state machine.
- Reorg detection and rollback.
- Durable `INTELLIGENCE_PENDING`.
- Alert fingerprinting and deduplication.
- WebSocket alert/case feeds with authentication and ping/pong.
- Indexer and alert operational APIs.
- Investigator UI operational indicators.


### Verification Requirements

- Test simulated reorgs including depth beyond the nominal reorg window.
- Test provider outage and recovery.
- Test WebSocket disconnect and reconnection with exponential backoff capped at 60 seconds.
- Test circuit breaker behavior by simulating more than 10 validation failures in 60 seconds and verifying a 120-second pause plus operator alert.
- Kill the process mid-block and verify checkpoint resume produces no event loss and no duplicates.
- Test duplicate block/transaction ingestion.
- Test downstream intelligence retry without transfer duplication.
- Test graph rebuild by clearing the graph store and reconstructing the identical graph from PostgreSQL.
- Test Redis namespace isolation, DEDUP DB 1 no-eviction behavior, and the invalidation rules for HOT_ADDR, TRACE_RESULT, and VASP_LABEL.
- Test DEMO_WARM startup warming and `FIXTURE REPLAY` labeling.
- Test production rejection of development authentication.
- Separately report live-provider tests and fixture/simulation tests.

### Exit Criteria

- Exact test counts are captured after completion.
- Checkpoint resume, provider recovery, circuit-breaker pause, and graph rebuild tests pass.
- Live-provider evidence is clearly distinguished from simulated evidence.
- PostgreSQL is not described as operationally tested unless actually exercised.
- Redis hot-address cache hit rate is measured and reported against the 80% target. Trace-cache hit rate is measured and reported.
- All acceptance criteria have evidence or documented limitations.
- Graph rebuild procedure is documented and tested.

---

## 6. Phase 4A — Authorized External Integration Boundaries

### Objectives

Implement controlled boundaries without claiming unauthorized live government connectivity. Blockchain provider procurement is already complete for the SIH demo; this phase does not add or replace chain-data providers.

### PRD Mapping

`FR-001`, `FR-011`, `FR-012`, `FR-013`, `NFR-001`, `NFR-005`

### Workstreams

#### 6.1 NCRP

- Complaint validation.
- Chain/address detection.
- Private-key and mnemonic rejection.
- Idempotent case creation.
- Two-way status synchronization.
- Remote-pending fallback.
- External provenance.
- Timeout and error isolation.

#### 6.2 SAHYOG

- Bulletin schema validation.
- Multi-wallet extraction.
- Collaborative case creation.
- Bulletin provenance.
- Duplicate handling.
- Classification and access controls.

#### 6.3 VASP Preservation Request

- Draft lifecycle.
- Supervisor/admin approval.
- Investigator approval rejection.
- EvidenceManifest binding.
- Hash/signature verification.
- Audit event.
- Case state transition only after approval.
- Legal wording mapped to the Master Guide.
- Explicit HSM/local signer limitation.

### Mandatory Boundary

No automatic freeze, filing, or legal action.

### Verification

- Dedicated integration tests.
- RBAC boundary tests.
- Idempotency tests.
- Secret sanitization tests.
- Tamper test for evidence package.
- Failure isolation tests.
- Actual route registry inspection.
- Explicit distinction between mocked/simulated and live connectivity.

### Exit Criteria

`SIGNED OFF`, `SIGNED OFF WITH DOCUMENTED LIMITATIONS`, or `REQUIRES CORRECTION`.

Do not use `PRODUCTION READY` unless all relevant operational requirements are verified.

---

## 7. Phase 4B — Evidence and Outcome Governance (Non-ML)

### Objectives

Prepare durable case-outcome and label-governance data contracts without training, evaluating, or deploying ML during the SIH implementation. This phase is a data-governance foundation only.

### PRD Mapping

`FR-011`, `FR-015`, `NFR-003`, `NFR-005`, `NFR-007`

### Workstreams

#### 7.1 Case Outcome Schema

Define durable fields for case ID, source, chain(s), reported wallet, case disposition, confirmation status, labeling authority, evidence references, typology labels, attribution outcome, confidence, review timestamps, reviewer/supervisor, and any later legal/court confirmation metadata.

#### 7.2 Label Governance

Every label must identify its type, source, reviewer, evidence reference, version, confidence, and whether it is investigator-assigned, rule-derived, synthetic, or later confirmed by an authoritative outcome.

#### 7.3 Dataset Quality Controls

Provide data-quality checks for duplicates, missing labels, class imbalance, temporal coverage, chain coverage, case-level overlap, feature leakage, and label leakage so later research work can begin from governed data. No SIH demo functionality depends on model training.

#### 7.4 Feature Availability Registry

Document the provenance and reproducibility requirements for future crypto-specific features such as velocity, value distribution, counterparty diversity, hop depth, fan-in/fan-out, burstiness, mixer/DEX exposure, bridge evidence, VASP proximity, graph centrality, consolidation, and peeling indicators. Do not claim a feature is production-available until the repository can reproduce it.

### Exit Criteria

- Case-outcome and label schemas are versioned and persistent.
- Data-quality checks execute reproducibly.
- No ML training, model comparison, or ML deployment is included in the SIH submission build.
- Future model work is explicitly governed by PRD FR-015.

---

## 8. Future Roadmap — Post-Launch Intelligence Enhancement

**Scope status: OUTSIDE SIH SUBMISSION SCOPE. This section is not a sequential delivery phase and is excluded from all SIH timelines, Gantt charts, presentations, demo scripts, and evaluation submissions.**

This roadmap is retained only as a documented future path. No implementation, model training, evaluation, or deployment from this roadmap is required for the SIH build. Any future work must first satisfy PRD FR-015 and the Master Guide governance gate.

### Future Sequence (Reference Only)

1. Establish authoritative ground truth.
2. Build reproducible crypto-specific features.
3. Train an interpretable gradient-boosting baseline.
4. Compare empirically against the deterministic rules engine.
5. Evaluate calibration and error modes.
6. Integrate only if evidence justifies the change.
7. Preserve feature attribution, provenance, auditability, and deterministic fallback.

Do not schedule this work in the SIH submission timeline.

---

## 9. Phase 6 — Hardening and Demonstration

### Objectives

Prepare a defensible demonstration and controlled deployment package.

### Workstreams

- Security review.
- Storage/recovery architecture validation against `NFR-007`.
- Secret scanning.
- Dependency review.
- API authorization review.
- Performance benchmarks.
- Load and failure tests.
- Backup/restore test.
- PostgreSQL operational test if production deployment requires it.
- Evidence tamper test.
- UI manual walkthrough.
- Demo script.
- Prepare a two-minute, non-technical explanation of the three contributions: MULE_NETWORK, AdaptiveVASPScorer, and RecoveryProbabilityScore. Open the demo with these three contributions before the technical walkthrough.
- Architecture diagrams.
- Known limitations document.
- Reproducible setup instructions.
- Deployment validation against `NFR-008`.
- Two-minute judge-facing explanation of the three novel contributions, used as the opening of the demo.
- Demo validation that `MULE_NETWORK`, AdaptiveVASPScorer, RecoveryProbabilityScore, mock NCRP intake, and `FIXTURE REPLAY` labeling appear in the intended investigator flow.

### Demo Narrative

**Opening — state the three contributions before the technical walkthrough:**

1. **MULE_NETWORK:** A purpose-built typology for Indian cybercrime investigation with a named, versioned, auditable rule and explicit confidence limits.
2. **AdaptiveVASPScorer:** Context-sensitive attribution scoring with a fully explainable, policy-versioned, auditable weight trace.
3. **RecoveryProbabilityScore:** A heuristic urgency indicator translating tracing results into victim-impact language and an operational action window for Indian law-enforcement workflows.

The demo presenter must explain each in approximately two minutes total, in language understandable to a non-technical SIH judge, before opening the technical workflow.

Then:

1. Intake reported wallet.
2. Show chain and source provenance.
3. Show indexed activity and finality.
4. Run bounded trace.
5. Explain suspicious intermediaries.
6. Show typology evidence.
7. Show candidate VASP with confidence tier.
8. Show cross-chain proof/correlation distinction.
9. Show risk separately from attribution.
10. Generate recommendation.
11. Generate evidence manifest.
12. Draft preservation request.
13. Demonstrate supervisor approval and audit trail.
14. Show limitations and human-review boundaries.

---

## 10. Cross-Phase Verification Protocol

Every phase must produce:

| Item | Required |
|---|---|
| Scope | Yes |
| PRD mapping | Yes |
| Files changed | Yes |
| Database migrations | If applicable |
| Tests | Exact completed results |
| Build | Actual completed result |
| Security checks | Yes |
| Operational evidence | If claimed |
| Limitations | Yes |
| Git status | Yes |
| Commit/tag | Controlled |
| Checklist update | Yes |
| Change log update | Yes |

Do not report a scheduled task as completed.

---

## 11. Definition of Done

A feature is done only when:

1. It matches the PRD and Master Guide.
2. It has implementation evidence.
3. It has tests or a documented reason testing is unavailable.
4. It has security and failure behavior defined.
5. It has provenance behavior defined.
6. It has clear LIVE/FIXTURE status where relevant.
7. It does not contradict another document.
8. Its limitations are written down.
9. Git changes are intentional and traceable.
10. The final report reflects actual execution results.

---

## 12. Change Management

Any change to a requirement or architecture must update:

- PRD;
- Implementation Plan;
- Explanation document;
- acceptance criteria;
- tests;
- change log.

Do not update only one document.

The following are prohibited without explicit review:
- changing the ML gate;
- changing canonical RBAC roles;
- weakening supervisor approval;
- removing provenance;
- hiding uncertainty;
- presenting inferred attribution as ownership proof;
- claiming live NCRP/SAHYOG connectivity without evidence;
- replacing deterministic scoring without comparison evidence.

---

## 13. Final Project Direction

The SIH implementation strategy is:

**Build a reliable, explainable, multi-chain investigative substrate first; demonstrate the India-specific `MULE_NETWORK` pattern, AdaptiveVASPScorer, and RecoveryProbabilityScore; connect the complaint-to-investigation path through the controlled NCRP demo intake; and prove resilience, provenance, and storage reconstruction.**

Post-launch intelligence enhancement remains conditional and outside the SIH submission scope.

This plan is designed to maximize technical defensibility, investigator usability, operational realism, and demonstration clarity—not to maximize feature count.
