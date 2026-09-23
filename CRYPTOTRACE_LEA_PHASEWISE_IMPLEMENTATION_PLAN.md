# CryptoTrace LEA — Phasewise Implementation & TraceX Adaptation Plan

**Project:** SIH 26183 — Real-Time Crypto Fraud Attribution System for Indian Law Enforcement  
**Base repository:** TraceX v2.0-PRO (SIH 26182)  
**Delivery target:** SIH 26183 demonstration-ready system  
**Implementation model:** phase-gated sequential delivery with no fixed calendar duration  
**Status model:** every phase ends with evidence-backed `PASS`, `PARTIAL`, `NOT VERIFIED`, `FAIL`, or `NOT APPLICABLE`

---

## 1. Implementation Position

CryptoTrace LEA should be implemented as an **adaptation and architectural refactor of TraceX**, not as a superficial rename.

The existing TraceX repository is the closest reusable baseline because it already contains a FastAPI backend, multi-chain address validation, graph tracing, VASP registry/attribution, provider clients, Neo4j synchronization, demo fixtures, a dashboard, and legal-notice generation. The CryptoTrace requirements, however, change the system's persistence model, attribution semantics, evidence model, live-provider backbone, supervision model, and legal-action boundary.

The implementation therefore follows this rule:

> **Reuse infrastructure where its behavior is compatible; rebuild anything whose semantics conflict with CryptoTrace LEA.**

The CryptoTrace product must remain evidence-first: it assists investigation but does not claim wallet ownership, criminal liability, automatic freezing, or automatic legal action.

---

# 2. Authority Order

Use the documents in this order when two requirements appear inconsistent:

1. **Verified repository behavior** documented by the TraceX Master README.
2. **CryptoTrace LEA PRD + Master Implementation Plan** for the target product.
3. **Brief Explanation** for the intended investigator workflow and demonstration semantics.
4. **Adaptation Strategy** for concrete migration/refactoring guidance.
5. **Implementation Checklist** for task-level scheduling.

Where the checklist or adaptation document conflicts with the PRD's confirmed live-provider backbone or canonical roles, update the checklist before implementation.

---

# 3. Critical Corrections to the Existing Checklist

These are not optional cleanup items. They should be corrected before the relevant workstream begins.

| Existing checklist/adaptation behavior | CryptoTrace LEA target | Decision |
|---|---|---|
| SQLite as durable storage | PostgreSQL system of record | **Replace** |
| Neo4j can store synchronized investigation state | Graph is reconstructable projection only | **Refactor** |
| TraceX Etherscan-based live Ethereum harvesting | Ethereum direct RPC/WebSocket live path; Etherscan historical/labels only | **Replace live path** |
| Blockstream as the canonical Bitcoin provider | Mempool.space is the confirmed SIH backbone | **Change canonical provider** |
| Bitquery treated as a required live provider | Not part of confirmed CryptoTrace live backbone | **Remove from critical path** |
| Single attribution percentage | Separate risk + attribution; VERIFIED/INFERRED/UNRESOLVED labels | **Replace** |
| Static VASP regex scoring | AdaptiveVASPScorer with versioned policy and scoring trace | **Rebuild** |
| Auto-generated legal notice | Draft-only, supervisor-gated preservation request | **Rebuild** |
| Single-user TraceX | INVESTIGATOR / SUPERVISOR / ADMINISTRATOR / INTEGRATION_SERVICE | **Replace auth model** |
| TraceX analyst role | Not a canonical CryptoTrace role | **Do not introduce as core RBAC** |
| Runtime UI key manager writes `.env` | Environment/secret configuration only | **Remove runtime secret-writing behavior** |
| Arbitrary Cypher endpoint | Controlled graph API only | **Disable/remove from production surface** |
| Arbitrary custom API tester | Internal/admin diagnostics only if retained | **Remove from investigator production surface** |
| AI Copilot as a central capability | Deterministic intelligence is the submission baseline | **Defer/optional** |
| Generic demo scenarios | CryptoTrace-specific fixtures with `demo_data=true` and visible provenance | **Replace fixtures** |
| “Recovery Probability” as a normal probability | Primary UI label: **Heuristic Recovery Estimate** | **Rename/reframe** |

---

# 4. Target Delivery Architecture

```text
                  Investigator / Supervisor
                           |
                    Investigator UI
                           |
                    FastAPI API Layer
                           |
       +-------------------+--------------------+
       |                   |                    |
       v                   v                    v
    Case APIs          Trace APIs         Evidence APIs
       |                   |                    |
       +-------------------+--------------------+
                           |
                    Domain / Service Layer
                           |
        +------------------+----------------------+
        |                  |                      |
        v                  v                      v
    Ingestion          Core Intelligence      Governance
        |                  |                      |
  Chain adapters       Bounded tracer       RBAC / audit
  Provider manager     Typology engine       evidence
  Checkpoints          VASP scorer            case workflow
  Finality/reorg       Cross-chain           supervisor gates
        |                  |                      |
        +------------------+----------------------+
                           |
                  PostgreSQL — SYSTEM OF RECORD
                           |
          +----------------+----------------+
          |                                 |
          v                                 v
   Graph projection                    Redis
   Memgraph / Neo4j              cache / coordination
          |
          v
   Rebuildable from PostgreSQL

Raw provider payloads
        |
        v
Write-once object storage
SHA-256 deterministic serialization
        |
        v
Evidence Manifest
```

### Non-negotiable storage rule

- PostgreSQL: authoritative durable state.
- Graph store: reconstructable traversal projection.
- Redis: performance/coordination only.
- Object storage: write-once raw-provider evidence.
- No material case state exists only in Redis or the graph.

---

# 5. TraceX Reuse / Change / Removal Map

| TraceX module/concept | Action | Implementation treatment |
|---|---|---|
| `app.py` FastAPI dispatcher | **KEEP + SPLIT** | Preserve FastAPI architecture, but move auth, DB, routes, services and configuration into bounded modules. |
| `address_validator.py` | **KEEP + EXTEND** | Preserve proven address parsing. Add CryptoTrace chain rules and make unsupported-chain activation explicit. |
| `graph_tracer.py` | **REBUILD CORE** | Keep graph traversal concepts, but replace the broad TraceX flow with bounded deterministic BFS, explicit limits, provenance and trace termination reasons. |
| `vasp_cluster.py` | **REBUILD CORE** | Preserve registry data structures as seed material; replace scoring semantics with `VERIFIED/INFERRED/UNRESOLVED` + AdaptiveVASPScorer. |
| `real_api.py` | **SPLIT/REPLACE** | Break provider-specific harvesting into EVM, Bitcoin and Tron adapters plus `provider_manager.py`. |
| Etherscan integration | **KEEP LIMITED** | Historical Ethereum lookup + label enrichment only. Never use it as the live Ethereum event stream. |
| TronGrid | **KEEP** | TRC-20 event indexing. Pair with configured Tron full-node HTTP polling. |
| Blockstream Esplora | **OPTIONAL** | May remain as a fallback adapter, but not the canonical SIH Bitcoin backbone. |
| Mempool.space | **ADD / CANONICAL** | Use as the confirmed Bitcoin source for the SIH backbone. |
| Direct Ethereum RPC/WebSocket | **ADD / CANONICAL** | Required live event path. |
| Direct Polygon RPC/WebSocket | **ADD / CANONICAL** | Required live event path. |
| `price_feed.py` / CoinGecko | **KEEP** | Pricing enrichment only. Do not make pricing part of evidence provenance beyond price-source metadata. |
| `neo4j_engine.py` | **KEEP + REFACTOR** | Preserve projection/sync capability. Remove any assumption that graph data is authoritative. Add PostgreSQL rebuild procedure. |
| Neo4j arbitrary Cypher API | **REMOVE/LOCK DOWN** | No unrestricted investigator-controlled graph query endpoint in the production UI. |
| `ai_copilot.py` | **DEFER** | Optional grounded assistant after deterministic baseline is stable. Not a dependency for Phase 1 acceptance. |
| `notice_generator.py` | **REBUILD** | Convert auto-action notice generation to draft-only preservation-request workflow with supervisor approval. |
| `ofac_sanctions.py` | **OPTIONAL ENRICHMENT** | Retain only as an auxiliary screening module with source/version provenance; it is not a CryptoTrace core acceptance dependency. |
| `api_tester.py` | **LIMIT** | Keep internal diagnostics if useful; remove arbitrary external request capability from investigator workflows. |
| `key_manager.py` | **REMOVE UI SECRET MUTATION** | Replace `.env` mutation with environment-based secrets and deployment-time secret management. |
| `demo_cases.py` | **REBUILD FIXTURES** | Create CryptoTrace-specific MULE_NETWORK, mixer-boundary, bridge, fan-in and rapid-hop fixtures. |
| `dashboard.html` | **REUSE VISUAL/INTERACTION IDEAS, REBUILD UI** | Keep graph and dense forensic interaction patterns; redesign around evidence, uncertainty, provenance and supervisor states. |
| SQLite | **DEV/LEGACY ONLY** | Development fallback and legacy read support only. No authoritative production case persistence. |

---

# 6. Phase Map

| Phase | Schedule | Objective | Status |
|---|---:|---|---|
| **Phase 0** |  | Foundation hardening and migration boundary | SIH critical path |
| **Phase 1** |  | Domain models and deterministic intelligence | SIH critical path |
| **Phase 2** |  | Investigator workstation and controlled workflow | SIH critical path |
| **Phase 3** |  | Live connectivity, checkpoints and resilience | SIH critical path |
| **Phase 6** |  | Hardening, E2E verification and demonstration | SIH critical path |
| **Phase 4A** | Post-SIH / authorized deployment | NCRP, SAHYOG, VASP external boundaries | Conditional |
| **Phase 4B** | Post-SIH / governance track | Outcome and label governance | Conditional |
| **Phase 5** | Post-launch only | Supervised ML augmentation | Gated future work |

Phase 4A/4B must not be presented as live SIH capabilities unless their authorization, interface contracts and operational evidence actually exist.

Phase 5 is explicitly outside the SIH submission scope.

---

# 7. PHASE 0 — FOUNDATION HARDENING


### Objective

Turn the TraceX prototype into a safe CryptoTrace application foundation before adding intelligence.

### PRD mapping

`FR-003`, `FR-004`, `FR-011`, `FR-013`, `NFR-001`, `NFR-002`, `NFR-006`, `NFR-007`

---

##  — Database, Configuration and RBAC

### 0.1 Repository freeze and baseline capture

Before modifying code:

- Create a dedicated `cryptotrace-lea` branch/repository.
- Tag the untouched TraceX baseline.
- Capture current:
  - backend build result;
  - frontend build result;
  - test count;
  - supported endpoints;
  - environment variables;
  - database schema;
  - demo fixtures;
  - external integrations.
- Record every baseline limitation.
- Do not silently edit TraceX in place without a reversible baseline.

**Deliverable:** `docs/BASELINE.md`

### 0.2 PostgreSQL schema

Create migrations for:

- `cases`
- `transactions`
- `transfers`
- `assets`
- `entity_labels`
- `pattern_findings`
- `vasp_clusters`
- `cross_chain_links`
- `risk_assessments`
- `recovery_assessments`
- `investigative_recommendations`
- `evidence_manifest`
- `audit_events`
- `crypto_alerts`
- users/access-control state as required

Add:

- foreign keys;
- uniqueness constraints;
- indexes for tracing/case retrieval;
- `demo_data`;
- provenance fields;
- confidence/label fields;
- policy/rule version fields.

### 0.3 Canonical event uniqueness

Implement the five-part canonical identity:

```text
chain_id
tx_hash
event_type
event-type-specific index
transfer_index
```

Required event types:

```text
NATIVE
ERC20
TRC20
INTERNAL
BRIDGE
```

The PostgreSQL constraint is the permanent idempotency authority.

### 0.4 Configuration separation

Create:

```text
backend/config/
    base.py
    development.py
    staging.py
    production.py
```

Enforce:

- environment-only secrets;
- `.env` excluded from Git;
- no secrets in logs;
- explicit `LIVE` vs `DEMO`;
- production rejects fixture ingestion;
- provider configuration validation at startup.

### 0.5 RBAC

Use canonical roles:

```text
INVESTIGATOR
SUPERVISOR
ADMINISTRATOR
INTEGRATION_SERVICE
```

Core authorization rules:

- investigator can create/trace/review assigned cases;
- supervisor can review/approve controlled preservation requests;
- administrator controls configuration, policy and user administration;
- integration service receives narrowly scoped machine permissions;
- no investigator approval endpoint;
- no automatic legal action.

### Phase 0  gate

Do not start intelligence implementation until:

- migrations run cleanly;
- role enforcement exists on protected routes;
- no secrets are tracked;
- baseline is recoverable;
- canonical event identity is implemented;
- case `demo_data` semantics are defined.

---

##  — Audit, Raw Evidence and Test Infrastructure

### 0.6 Chained audit log

Implement:

```text
timestamp
user
action
resource_id
result
details
previous_hash
event_hash
```

Add:

- append-only behavior;
- chain verification;
- tamper test;
- audit events for material user/system/supervisor actions.

### 0.7 Raw payload archive

Implement deterministic serialization:

- alphabetically sorted keys;
- compact JSON;
- UTF-8;
- no unnecessary whitespace;
- SHA-256 of the serialized bytes.

Store:

```text
raw/
  {chain_id}/
    {block_height}/
      {tx_hash}/
        {provider_name}/
          {payload_type}/
            {payload_hash}.json
```

Raw payloads are write-once from application workflows.

### 0.8 Evidence manifest

For each evidence item retain:

- case ID;
- event ID;
- provider;
- payload hash;
- serialization version;
- creation/verification timestamps;
- relationship to normalized records.

### 0.9 Security controls

Run:

- secret scanning;
- dependency audit;
- tracked-file scan;
- log-sanitization tests;
- authorization tests.

### 0.10 Test framework

Create:

```text
backend/tests/
    unit/
    integration/
    fixtures/
```

Set up:

- pytest;
- deterministic fixtures;
- database test environment;
- CI;
- exact test-count reporting.

### Phase 0 Exit Gate

`PASS` only when:

- database migrations are reproducible;
- RBAC denies unauthorized actions;
- audit-chain verification passes;
- raw-payload integrity verification passes;
- fixture data is visibly classified;
- CI is green;
- no secret scan findings remain.

---

# 8. PHASE 1 — DOMAIN MODELS AND CORE INTELLIGENCE


### Objective

Build the deterministic intelligence engine that converts normalized blockchain facts into bounded, explainable investigative outputs.

### PRD mapping

`FR-002`, `FR-004`, `FR-005`, `FR-006`, `FR-007`, `FR-008`, `FR-009`, `FR-010`, `FR-016`

---

## Domain Models and Chain Adapters

### 1.1 Domain model layer

Create strongly typed models for:

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
- AuditEvent
- CryptoAlert

Create explicit types for:

```text
ConfidenceLevel
LabelType
CrossChainLinkType
RiskCategory
FinalityState
ExecutionMode
```

### 1.2 EVM adapter

Implement for Ethereum and Polygon:

- native transfers;
- ERC-20 transfers;
- internal traces where provider evidence supports them;
- receipt/log normalization;
- canonical identities;
- finality state;
- raw payload capture.

Provider design:

```text
Live events  -> direct RPC/WebSocket
Historical   -> Etherscan
Labels       -> Etherscan / approved registry
```

### 1.3 Bitcoin adapter

Use Mempool.space as the confirmed SIH source.

Normalize:

- transactions;
- inputs/outputs;
- UTXO relationships;
- confirmation state;
- raw payload provenance.

### 1.4 Tron adapter

Use:

- Tron full-node HTTP for chain state/polling;
- TronGrid for TRC-20 indexing.

Normalize:

- TRX;
- TRC-20;
- transaction/event evidence.

### 1.5 Provider manager

Create:

- health check;
- timeout;
- retry;
- bounded backoff;
- provider provenance;
- primary/secondary logic;
- isolated chain workers.

Provider failure on one chain must not stop another.

###  Acceptance

Test:

- address validation;
- canonical normalization;
- provider provenance;
- event identity;
- deterministic serialization;
- all core adapter fixtures.

---

## Bounded Trace Engine and Typologies

### 1.6 Bounded tracer

Implement deterministic BFS with:

- maximum hops;
- time window;
- minimum value;
- maximum outflows;
- maximum nodes;
- timeout;
- deterministic ordering;
- path-level provenance;
- termination reason.

Expose applied limits in the trace result.

### 1.7 Graph builder

Use a graph abstraction that can write to the graph projection after PostgreSQL persistence.

Graph entities should remain reconstructable from PostgreSQL.

### 1.8 Core typologies

Implement versioned deterministic rules for:

- peel chain;
- fan-in;
- fan-out;
- rapid-hop;
- consolidation;
- mixer exposure;
- DEX boundary;
- bridge-mediated movement.

### 1.9 `MIXER_BOUNDARY_CLUSTER_LEAD`

Implement the exact CryptoTrace semantics:

- search same mixer pool;
- deposit time through +14,400 seconds;
- payout between 0.90 and 0.995 of deposit denomination;
- fixed confidence `0.25`;
- confidence band `LEAD`;
- immutable confidence;
- required uncertainty text;
- dashed graph edges;
- hover label `Possible Exit — Heuristic Only`.

Never allow AdaptiveVASPScorer to increase this confidence.

### 1.10 `MULE_NETWORK` — primary India-specific capability

Implement the PRD rule:

- at least 3 suspect-origin wallets;
- each forwards through a separate intermediate wallet;
- intermediate wallets satisfy the required behavioral properties;
- common aggregation address;
- required time windows;
- fee-normalized amount comparison;
- separate native/token findings;
- partial indexing warning where applicable;
- `complaint_linked` vs `behavior_only`;
- `india_specific=true`;
- confidence fixed at `MEDIUM`;
- exact uncertainty note;
- rule version + transaction evidence.

Create tests for:

- true positive;
- fewer than three wallets;
- timing violation;
- aggregation violation;
- fee-normalization edge case;
- partial-history case;
- token/native separation.

###  Gate

`PASS` only when the tracer is bounded and deterministic and all mandatory typology evidence fields exist.

---

## VASP Attribution and Cross-Chain Analysis

### 1.11 VASP registry redesign

Retain useful TraceX registry information as seed data, but normalize:

- VASP;
- jurisdiction;
- label source;
- label type;
- evidence reference;
- confidence;
- review date;
- registry version.

A label is never equivalent to ownership proof.

### 1.12 AdaptiveVASPScorer

Implement the exact six-step sequence:

1. load versioned policy;
2. apply `SINGLE_HOP` structural override;
3. apply multipliers alphabetically:
   - `HIGH_VALUE`
   - `INDIA_EXCHANGE`
   - `LONG_HOP`
   - `MIXER_PATH`
   - `SPARSE_LABEL`
4. resolve same-dimension conflicts conservatively;
5. clamp weights to `0.01–0.80`;
6. renormalize to exactly `1.0` and score.

Persist:

- policy version;
- base weights;
- fired modifiers;
- modifier reasons;
- thresholds;
- intermediate vectors;
- final vector;
- final score.

Required tests:

- SINGLE_HOP;
- MIXER_PATH;
- SINGLE_HOP + MIXER_PATH;
- HIGH_VALUE + SPARSE_LABEL;
- LONG_HOP + INDIA_EXCHANGE;
- zero-hop rejection.

### 1.13 Cross-chain analyzer

Separate:

```text
PROVEN
HEURISTIC_CORRELATION
```

Proven bridge movement requires direct evidence from a supported bridge/protocol boundary.

Heuristic correlation must retain:

- evidence basis;
- time relation;
- value relation;
- confidence;
- uncertainty note.

###  Gate

No inferred VASP appears as verified ownership and no heuristic cross-chain link appears as proven.

---

## Risk, Recovery Estimate and Recommendation Layer

### 1.14 Risk assessment

Store separately:

```text
risk_score
risk_category
rules_used
input references
evidence references
uncertainty flags
rule/policy version
```

Risk and attribution must never collapse into one score.

### 1.15 Heuristic Recovery Estimate

Implement PRD FR-016 exactly.

Formula:

```text
value_ratio
× exchange_cooperation
× time_urgency
× path_clarity
× top_candidate_confidence
```

Boundary behavior:

- missing/zero fraud amount → insufficient-data state;
- future/missing incident time → warning + `time_urgency = 1.0`;
- zero-hop → reject;
- top VASP confidence `LEAD`/`NONE` → do not display estimate.

Persist:

- `recovery_score`;
- `value_ratio`;
- `exchange_cooperation`;
- `time_urgency`;
- `path_clarity`;
- `action_window_hours`;
- `display_tier`;
- cooperation source;
- review date;
- reviewer identity.

UI label:

> **Heuristic Recovery Estimate**

Secondary wording may contain:

> Recovery Probability (not a statistical probability)

### 1.16 Recommendations

Generate evidence-linked, human-reviewable recommendations.

Recommendations must not:

- freeze assets automatically;
- file statutory requests automatically;
- declare ownership;
- declare guilt.

### Phase 1 Exit Gate

`PASS` requires:

- schema tests passing;
- adapters passing;
- bounded tracing passing;
- typology evidence complete;
- MULE_NETWORK passing;
- AdaptiveVASPScorer trace complete;
- cross-chain provenance distinct;
- risk and attribution separate;
- recovery estimate boundary tests passing.

---

# 9. PHASE 2 — INVESTIGATOR EXPERIENCE


### Objective

Turn the deterministic backend into an investigator workstation and controlled complaint-to-action demonstration.

### PRD mapping

`FR-001`, `FR-010`, `FR-012-A`, `FR-014`, `FR-016`, `NFR-003`, `NFR-005`

---

## Case and Trace APIs

Implement:

```text
POST /api/v1/cases
GET  /api/v1/cases/{case_id}
GET  /api/v1/cases
PUT  /api/v1/cases/{case_id}

POST /api/v1/cases/{case_id}/trace
GET  /api/v1/traces/{trace_id}/status
GET  /api/v1/traces/{trace_id}/result
GET  /api/v1/traces/{trace_id}/graph

GET  /api/v1/traces/{trace_id}/findings
GET  /api/v1/findings/{finding_id}

GET  /api/v1/cases/{case_id}/evidence-manifest
GET  /api/v1/payloads/{payload_hash}
POST /api/v1/payloads/{payload_hash}/verify
```

Every protected endpoint:

- validates role;
- validates case access;
- emits audit events where material;
- returns consistent error envelopes;
- includes execution mode/provenance as appropriate.

### NCRP / Case Intake Boundary

Implement the intake path so that the product workflow uses a real authorized intake boundary in the target deployment.

Requirements:

- validate the real intake schema supplied by the authorized NCRP boundary;
- validate wallet, chain, amount and incident-time fields;
- preserve source provenance;
- create or link cases idempotently;
- apply the real authentication and authorization boundary;
- hash sensitive identifiers where required;
- do not store raw PII unless explicitly required by the approved interface;
- reject fixture-only intake in production;
- do not provide a one-click synthetic complaint trigger in the production workflow.

If an authorized NCRP endpoint is unavailable during development, that limitation must be reported explicitly. It must not be represented as a working live integration.

---

## Investigator Dashboard

### Required layout

```text
TOP    : Case header + mode/source/status
LEFT   : Controls / timeline / filters / notes
CENTER : Fund-flow graph
RIGHT  : Findings / Attribution / Risk / Recovery / Cross-chain
BOTTOM : Evidence manifest / raw payload / audit
```

### Required panels

- `CaseHeader`
- `CaseControls`
- `FundFlowGraph`
- `FindingsPanel`
- `AttributionPanel`
- `RiskPanel`
- `RecoveryEstimatePanel`
- `EvidenceManifestPanel`
- `AuditTrailTimeline`

### UX semantics

Always distinguish:

```text
VERIFIED
INFERRED
UNRESOLVED
PARTIAL
HEURISTIC
```

Visually distinguish:

- confirmed graph relationships;
- heuristic mixer-boundary edges;
- live provider provenance;
- partial/incomplete indexing;
- verified/inferred/unresolved labels.

Required visible badges:

- source/provider provenance;
- `LIVE`;
- `PARTIAL` where indexing coverage is incomplete;
- amber `India Fraud Pattern`.

Avoid the existing TraceX “generic AI dashboard” feel. Preserve the forensic density and graph interaction pattern, but redesign the information hierarchy around evidence and uncertainty.

---

## Evidence + Supervisor-Gated Preservation Workflow

### Evidence UI

Provide:

- event ID;
- evidence type;
- provider;
- payload hash;
- serialization version/date;
- verification status;
- raw payload viewer;
- external source link where appropriate.

### Preservation workflow

The TraceX notice generator must be converted from automatic output behavior to:

```text
DRAFT
  ↓
PENDING_APPROVAL
  ↓
APPROVED / REJECTED
```

Only `SUPERVISOR` can approve.

Bind every draft to:

- case;
- trace;
- evidence manifest;
- transaction references;
- supporting findings;
- audit record.

No automatic freeze, filing, or legal submission.

### Phase 2 Exit Gate

`PASS` requires:

- investigator can create a case;
- investigator can run a trace;
- evidence is inspectable and verifiable;
- risk/attribution/recovery are visibly separate;
- supervisor permissions are visibly distinct;
- frontend build succeeds;
- manual UX walkthrough is recorded;
- demo/fixture labels are unambiguous.

---

# 10. PHASE 3 — LIVE CONNECTIVITY AND RESILIENCE


### Objective

Make live indexing operationally resilient without weakening provenance or idempotency.

### PRD mapping

`FR-003`, `FR-004`, `FR-005`, `FR-006`, `FR-014`, `NFR-002`, `NFR-004`, `NFR-005`, `NFR-007`

---

## 10.1 Confirmed Live Backbone

### Ethereum

- `ETH_RPC_PRIMARY_URL`
- WebSocket `newHeads`
- HTTP fallback

### Polygon

- `POLYGON_RPC_PRIMARY_URL`
- WebSocket `newHeads`
- HTTP fallback

### Tron

- `TRON_RPC_PRIMARY_URL`
- 3-second polling
- `TRON_GRID_API_KEY` for TRC-20 indexing

### Bitcoin

- Mempool.space

### Historical/labels

- Etherscan only for historical lookups and label enrichment.

### Pricing

- CoinGecko.

Each chain operates as an isolated worker.

---

## 10.2 Eight-Stage Ingestion Pipeline

Implement as a contract:

```text
FETCH
  ↓
VALIDATE
  ↓
EXTRACT
  ↓
NORMALIZE
  ↓
DEDUPLICATE
  ↓
PERSIST
  ↓
COMMIT
  ↓
ADVANCE
```

### FETCH

Acquire raw provider data.

### VALIDATE

Reject invalid:

- block progression;
- transaction hashes;
- addresses;
- values.

Record chain-specific validation reason.

### EXTRACT

Extract:

- native transfers;
- ERC-20 transfers;
- TRC-20 transfers;
- supported internal traces;
- bridge events where evidence supports them.

### NORMALIZE

Create canonical transfer records.

Store `raw_amount` as string.

Hash raw JSON using deterministic serialization.

### DEDUPLICATE

Redis DB1:

- recent duplicate suppression;
- seven-day key TTL;
- **no eviction**.

PostgreSQL:

- permanent uniqueness authority.

### PERSIST

Write:

```text
PostgreSQL → graph projection
```

Never reverse the order.

### COMMIT

Advance checkpoint only after durable persistence.

Checkpoint includes:

- last block height;
- last block hash;
- update time.

### ADVANCE

Publish normalized transfer for downstream intelligence.

---

## 10.3 Redis Namespaces

Use only defined namespaces.

### `DEDUP`

- DB 1
- seven-day TTL
- no eviction

### `HOT_ADDR`

- DB 0
- 300-second TTL
- PostgreSQL as source of truth

### `TRACE_RESULT`

- DB 0
- 1,800-second TTL
- indexed invalidation on confirmed activity

### `VASP_LABEL`

- DB 0
- 86,400-second TTL
- PostgreSQL registry remains authoritative

### Development-only test cache

A development/test warm-cache may exist only outside the production runtime and must never be used as evidence of live functionality.

Production must not depend on pre-seeded trace results or fixture warming.

Do not create unbounded Redis-only business state.

---

## 10.4 Reliability Controls

Implement and test:

- bounded retry/backoff;
- maximum backoff of 60 seconds;
- circuit breaker;
- finality state machine;
- reorg detection;
- reorg rollback/reconciliation;
- durable downstream retry;
- alert fingerprinting;
- authenticated WebSocket feeds;
- operational health APIs.

### Circuit breaker contract

More than 10 validation failures in 60 seconds:

```text
pause chain = 120 seconds
emit operator alert
```

---

## 10.5 Graph Rebuild

Create an operational procedure that:

1. clears graph projection;
2. reads authoritative PostgreSQL rows;
3. recreates nodes/edges;
4. validates graph cardinality;
5. confirms no authoritative data was lost.

---

## 10.6 Phase 3 Verification

Mandatory tests:

- process killed mid-block;
- checkpoint resume;
- duplicate block;
- duplicate transaction;
- duplicate canonical transfer;
- provider outage;
- provider recovery;
- WebSocket disconnect;
- WebSocket reconnect;
- validation-failure circuit breaker;
- reorg within expected depth;
- reorg beyond nominal depth;
- downstream intelligence retry;
- graph rebuild;
- Redis namespace isolation;
- DEMO_WARM labeling;
- production authentication rejection of development headers.

Report live-provider tests separately from fixtures/simulations.

---

# 11. PHASE 6 — HARDENING AND DEMONSTRATION


### Objective

Convert the implementation into a defensible SIH demonstration and controlled deployment package.

### 11.1 Security review

Run:

- dependency review;
- secret scanning;
- API authorization review;
- input validation review;
- output sanitization review;
- audit coverage review;
- evidence tamper tests.

### 11.2 Storage/recovery verification

Validate:

- PostgreSQL backup/restore;
- raw payload retention;
- evidence manifest integrity;
- graph rebuild;
- Redis recoverability;
- checkpoint persistence.

Do not claim PostgreSQL operational verification unless PostgreSQL has actually been exercised.

### 11.3 Performance benchmark

Measure, rather than merely claim:

- 1-hop trace;
- 3-hop trace;
- 5-hop trace;
- typology execution;
- AdaptiveVASPScorer;
- graph query performance;
- hot-address cache hit rate;
- trace-result cache hit rate.

The repository's previous “sub-50ms” style claims must not be reused as achieved metrics without benchmark evidence.

### 11.4 End-to-end live verification

Run the smallest complete **live-data** investigation:

```text
Real authorized complaint/wallet intake
    ↓
live provider validation / provenance
    ↓
continuously indexed blockchain activity
    ↓
bounded trace over live transactions
    ↓
MULE_NETWORK / other typology from live evidence, where criteria are met
    ↓
VASP candidate from current provenance-aware labels
    ↓
risk + attribution
    ↓
Heuristic Recovery Estimate, only when live evidence satisfies the boundary conditions
    ↓
evidence-linked recommendation
    ↓
evidence manifest + raw payload hashes
    ↓
supervisor-gated preservation-request draft
    ↓
audit trail
```

A fixture-only walkthrough does not satisfy the final acceptance gate.

### 11.5 Live Demonstration Sequence

Open with the three project contributions:

1. `MULE_NETWORK`
2. `AdaptiveVASPScorer`
3. `RecoveryProbabilityScore` / Heuristic Recovery Estimate

Then show on a real live-data case:

1. authorized intake;
2. source and chain provenance;
3. current indexed blockchain activity;
4. bounded trace over actual transactions;
5. suspicious intermediaries;
6. typology evidence tied to actual transaction hashes;
7. VASP candidate + complete scoring trace;
8. proven-vs-heuristic cross-chain status;
9. separate risk and attribution;
10. recovery estimate only when live boundary conditions are satisfied;
11. evidence-linked recommendation;
12. evidence manifest and raw-payload hash verification;
13. preservation-request draft;
14. supervisor approval;
15. uncertainty, incomplete-indexing and other limitations.

### 11.6 Phase 6 Exit Gate

Do not call the product `PRODUCTION READY` unless operational requirements are actually verified.

Final artifact set:

```text
docs/
  ARCHITECTURE.md
  API.md
  DEPLOYMENT.md
  SECURITY.md
  LIMITATIONS.md
  BASELINE.md
  DEMO_SCRIPT.md
  VERIFICATION_REPORT.md
```

---

# 12. PHASE 4A — AUTHORIZED EXTERNAL BOUNDARIES
## Conditional / Post-SIH

This is outside the core SIH implementation path unless authorization and interface specifications already exist.

### NCRP

Implement only with documented boundary contract:

- complaint validation;
- address/chain detection;
- private-key/mnemonic rejection;
- idempotent case creation;
- external provenance;
- two-way status synchronization;
- remote-pending fallback;
- timeout/error isolation.

### SAHYOG

Implement:

- bulletin schema;
- multi-wallet extraction;
- collaborative case creation;
- provenance;
- duplicate handling;
- classification and access control.

### VASP Preservation Request

Implement external connectivity only after authorization:

- approved request creation;
- supervisor/admin approval;
- evidence binding;
- signed/hash-linked package;
- audit event;
- state transition after approval;
- explicit signer/HSM limitation.

Never convert this into automatic freezing or automatic legal action.

---

# 13. PHASE 4B — EVIDENCE AND OUTCOME GOVERNANCE
## Conditional / Post-SIH

Create durable schemas for:

- case disposition;
- confirmation status;
- labeling authority;
- outcome evidence;
- reviewer;
- confidence;
- legal/court confirmation metadata.

Add quality checks for:

- duplicate cases;
- missing labels;
- class imbalance;
- temporal coverage;
- chain coverage;
- case overlap;
- feature leakage;
- label leakage.

This phase creates governed data for future research. It does not require ML.

---

# 14. PHASE 5 — FUTURE ML
## Explicitly Outside SIH Scope

Do not train or deploy supervised ML in the SIH build.

Before ML:

1. obtain at least 100 genuinely qualifying court-confirmed labeled cases;
2. establish authoritative ground truth;
3. build reproducible crypto-specific features;
4. train an interpretable gradient-boosting baseline;
5. compare against the deterministic rules engine;
6. evaluate calibration/error modes;
7. integrate only if empirical evidence justifies it;
8. retain explainability, provenance, auditability and deterministic fallback.

Do not assume a neural/GNN model should be the first production model.

---

# 15. Master Phase Sequence

| Sequence | Phase | Deliverable / gate |
|---:|---|---|
| 1 | Phase 0 — Foundation Hardening | Database, configuration, RBAC, audit and evidence integrity operationally verified |
| 2 | Phase 1 — Domain Models and Core Intelligence | Live-provider normalization, bounded tracing, typologies, attribution and recovery logic verified |
| 3 | Phase 2 — Investigator Experience | Live case workflow, evidence inspection and supervisor controls verified |
| 4 | Phase 3 — Live Connectivity and Resilience | Continuous live ingestion, checkpoints, finality, reorg handling and provider recovery verified |
| 5 | Phase 6 — Hardening and Demonstration | End-to-end live case, security, performance and deployment verification complete |
| 6 | Phase 4A — Authorized External Boundaries | Only after real authorization and a tested external interface contract |
| 7 | Phase 4B — Evidence and Outcome Governance | Only after governed case-outcome data exists |
| 8 | Phase 5 — Future ML | Only after the documented labeled-case gate is genuinely satisfied |

There is intentionally no calendar duration in this plan. A phase advances only after its exit gate is actually satisfied.

---

# 16. Definition of Done

A feature is not complete because a file exists or a test is scheduled.

For every requirement record:

```text
Requirement ID
Implementation location
Code status
Automated test status
Operational evidence
Execution mode
Limitations
Final status
```

Allowed final statuses:

```text
PASS
PARTIAL
NOT VERIFIED
FAIL
NOT APPLICABLE
```

Every phase verification report must additionally contain:

- scope;
- PRD mapping;
- files changed;
- migrations;
- exact test results;
- build result;
- security checks;
- operational evidence if claimed;
- known limitations.

---

# 17. Final Demonstration Contract

The final system should visibly communicate this chain:

```text
Complaint / Wallet
      ↓
Blockchain facts
      ↓
Normalized evidence
      ↓
Bounded trace
      ↓
Explainable typology
      ↓
Provenance-aware VASP candidate
      ↓
Uncertainty-aware attribution
      ↓
Separate risk
      ↓
Heuristic Recovery Estimate
      ↓
Evidence-linked recommendation
      ↓
Evidence package
      ↓
Supervisor-gated preservation workflow
      ↓
Audit history
```

The product position is therefore:

> **Evidence first. Deterministic intelligence before ML. Attribution is not ownership proof. Heuristics remain visibly heuristic. Legal action remains human-supervised.**

---

# 18. Source Reconciliation Notes

### Brief Solution Explanation

The brief requires an evidence-backed investigation, bounded tracing, typologies, VASP analysis, cross-chain uncertainty, risk/recovery separation, investigator outputs and supervisor-gated preservation behavior. Fixture/demo data must remain visibly separated from live intelligence.

### Master Implementation Plan

The implementation plan establishes the phase gates:

- Phase 0 foundation;
- Phase 1 deterministic intelligence;
- Phase 2 investigator experience;
- Phase 3 live connectivity/resilience;
- Phase 4A/4B authorized/governance boundaries;
- Phase 6 hardening/demo;
- future intelligence enhancement outside SIH.

### PRD

The PRD is the functional source of truth for:

- canonical entities;
- provider backbone;
- typologies;
- AdaptiveVASPScorer;
- cross-chain semantics;
- risk/attribution separation;
- evidence/audit;
- investigator workstation;
- RecoveryProbabilityScore / Heuristic Recovery Estimate;
- deployment and storage requirements.

### Adaptation Strategy

The adaptation strategy supplies the concrete TraceX-to-CryptoTrace refactoring map and target repository structure.

### Implementation Checklist

The checklist supplies the practical weekly execution order, but its provider and role references must be corrected where they conflict with the PRD.

### TraceX Master README

The TraceX manual is the source for what already exists and is therefore reusable: FastAPI routing, address validation, graph tracing, VASP registry, provider clients, Neo4j synchronization, pricing, diagnostics, demo cases and the current dashboard.

---

# 19. Recommended Repository Migration Sequence

```text
1. Freeze TraceX baseline
        ↓
2. Create CryptoTrace repository/branch
        ↓
3. Create PostgreSQL schema + migrations
        ↓
4. Move configuration/RBAC/audit/storage first
        ↓
5. Create canonical domain models
        ↓
6. Extract providers into adapters
        ↓
7. Rebuild bounded tracer
        ↓
8. Rebuild typology engine
        ↓
9. Rebuild VASP attribution
        ↓
10. Add cross-chain analyzer
        ↓
11. Add risk + recovery
        ↓
12. Add case/trace/evidence APIs
        ↓
13. Rebuild investigator dashboard
        ↓
14. Convert notice generation to supervisor-gated drafts
        ↓
15. Connect live providers
        ↓
16. Add checkpoints/finality/reorg/retry/cache
        ↓
17. Security + performance + graph rebuild
        ↓
18. End-to-end verification
        ↓
19. SIH demonstration
```

---

# 20. Bottom Line

Do **not** port the TraceX repository feature-for-feature.

Port the reusable infrastructure:

- FastAPI;
- address validation;
- graph traversal concepts;
- VASP registry seed data;
- provider-client patterns;
- Neo4j projection;
- CoinGecko enrichment;
- demo-fixture infrastructure;
- existing dashboard interaction concepts.

Rebuild the semantics that define CryptoTrace LEA:

- PostgreSQL authority;
- evidence manifests and deterministic hashing;
- canonical event identity;
- bounded deterministic tracing;
- `MULE_NETWORK`;
- `MIXER_BOUNDARY_CLUSTER_LEAD`;
- AdaptiveVASPScorer;
- proven-vs-heuristic cross-chain evidence;
- separate risk and attribution;
- Heuristic Recovery Estimate;
- RBAC and supervisor gating;
- live-provider isolation;
- checkpoint/finality/reorg handling;
- explicit LIVE/FIXTURE boundaries.

The implementation should end with a defensible, live-data SIH demonstration. Government integrations that are not authorized or operational must be explicitly marked as unavailable rather than simulated, and ML remains outside the deterministic baseline.
