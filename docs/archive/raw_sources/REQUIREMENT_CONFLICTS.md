# CryptoTrace LEA — Requirement Discrepancy & Conflict Register

**Document Path:** `docs/REQUIREMENT_CONFLICTS.md`

**Purpose:** Record discrepancies between the CryptoTrace LEA requirements and the TraceX baseline, establish the governing resolution, and prevent contradictory implementation decisions.

## Document Precedence

Use the following order for target-product requirements:

1. `CRYPTOTRACE_LEA_PRD (1)(1).md`
2. `CRYPTOTRACE_LEA_IMPLEMENTATION_PLAN (1)(1).md`
3. `CRYPTOTRACE_LEA_PHASEWISE_IMPLEMENTATION_PLAN.md`
4. `CRYPTOTRACE_LEA_BRIEF_EXPLANATION(2).docx`
5. `ADAPTATION_STRATEGY(1).md`
6. `IMPLEMENTATION_CHECKLIST(1).md`
7. `MASTER_README(1).md` — TraceX baseline behavior

`MASTER_README(1).md` remains authoritative only for understanding what already exists in TraceX. It does not override the CryptoTrace target architecture.

---

# Registered Discrepancies & Formal Resolutions

## Conflict 1 — Canonical RBAC Roles

### Discrepancy

`IMPLEMENTATION_CHECKLIST(1).md` and `ADAPTATION_STRATEGY(1).md` use:

- `INVESTIGATOR`
- `SUPERVISOR`
- `ADMIN`
- `ANALYST`

The CryptoTrace PRD defines the canonical roles as:

1. `INVESTIGATOR`
2. `SUPERVISOR`
3. `ADMINISTRATOR`
4. `INTEGRATION_SERVICE`

The PRD also defines an Analyst persona as a possible future intelligence consumer, but explicitly states that any future bank-facing role requires explicit RBAC design. fileciteturn11file0L1-L1

### Resolution

Implement only the canonical CryptoTrace roles:

```text
INVESTIGATOR
SUPERVISOR
ADMINISTRATOR
INTEGRATION_SERVICE
```

Do **not** create `ADMIN` or `ANALYST` as implicit aliases.

If an analyst/read-only persona is later required, define a separate permission profile through documented RBAC change control. Do not automatically inherit investigator permissions.

### Status

**RESOLVED — PRD controls.**

---

## Conflict 2 — Primary Bitcoin Provider Backbone

### Discrepancy

TraceX uses Blockstream Esplora in its provider stack. The CryptoTrace PRD defines:

**Mempool.space** as the confirmed Bitcoin backbone.

The PRD does not require Blockstream as a production provider. fileciteturn11file9L1-L1

### Resolution

Use:

```text
Primary live Bitcoin provider:
Mempool.space
```

Blockstream Esplora may remain as an optional secondary/fallback adapter only if it is implemented explicitly as a resilience mechanism.

Any fallback result must preserve:

- provider name;
- provider version/source;
- retrieval timestamp;
- raw payload hash;
- normalized provenance.

Never describe Blockstream as the canonical Bitcoin provider.

### Status

**RESOLVED — Mempool.space is canonical.**

---

## Conflict 3 — Live Ethereum Event Ingestion Path

### Discrepancy

TraceX uses Etherscan as a major Ethereum data source. CryptoTrace requires direct Ethereum RPC/WebSocket infrastructure for the live event path.

The PRD explicitly restricts Etherscan to:

- historical address lookup;
- label enrichment.

It must not be the live event stream. fileciteturn11file9L1-L1

### Resolution

Implement:

```text
ETH_RPC_PRIMARY_URL
    ↓
WebSocket / newHeads
    ↓
HTTP fallback
    ↓
live block/event ingestion
```

Use Etherscan only for historical and label-enrichment operations.

### Status

**RESOLVED — direct RPC/WebSocket controls live Ethereum ingestion.**

---

## Conflict 4 — Authoritative Persistence Layer

### Discrepancy

TraceX uses:

```text
SQLite
+
flat JSON investigation records
+
Neo4j synchronization
```

CryptoTrace requires PostgreSQL as the durable system of record.

The PRD explicitly defines:

- PostgreSQL as the durable system of record;
- graph storage as a rebuildable projection;
- Redis as speed/coordination only;
- raw provider payloads in write-once evidence storage. fileciteturn11file7L1-L1

### Important correction

Do **not** describe CryptoTrace as having only “12 canonical entities.”

The PRD defines at least these 15 canonical domain entities:

```text
Chain
Address
Transaction
Transfer
Asset
EntityLabel
PatternFinding
VASPCluster
CrossChainLink
RiskAssessment
InvestigativeRecommendation
EvidenceManifest
Case
AuditEvent
CryptoAlert
```

Database implementation will also require operational tables/entities such as users, sessions, checkpoints, policies and request/workflow state.

### Resolution

Production/staging:

```text
PostgreSQL = authoritative system of record
```

Development/testing:

```text
SQLite = optional local-development fallback only
```

Graph:

```text
PostgreSQL
    ↓
Neo4j/Memgraph projection
```

Redis:

```text
cache / coordination only
```

No material case state may exist exclusively in Redis or the graph.

### Status

**RESOLVED — PostgreSQL controls authoritative persistence.**

---

## Conflict 5 — Attribution vs Risk Scoring Semantics

### Discrepancy

TraceX blends attribution/risk concepts into a single heuristic confidence value.

CryptoTrace requires:

```text
Risk
≠
Attribution
```

Risk must be separately stored and explained from VASP attribution.

VASP attribution uses:

- `VERIFIED`
- `INFERRED`
- `UNRESOLVED`

and the versioned `AdaptiveVASPScorer`.

The scorer must execute its defined six-step policy order and persist the complete scoring trace. fileciteturn9file2L1-L1

### Resolution

Implement independent outputs:

```text
Risk Assessment
    risk_score
    risk_category
    risk_components

Attribution Assessment
    attribution_score
    confidence
    label_type
    evidence
    policy_version
    scoring_metadata
```

Never treat an attribution score as proof of wallet ownership.

### Status

**RESOLVED — independent risk and attribution dimensions.**

---

## Conflict 6 — Recovery Estimate Terminology and Eligibility

### Discrepancy

TraceX uses concepts such as “Freezing Urgency Countdown.”

The CryptoTrace PRD requires the primary UI wording:

**Heuristic Recovery Estimate**

The PRD defines the recovery calculation and its boundary conditions.

However, `IMPLEMENTATION_CHECKLIST(1).md` additionally proposes:

- a minimum amount threshold such as INR 10,000;
- data completeness `>= 70%`;
- attribution confidence `>= MEDIUM`.

Those additional thresholds are **not the governing FR-016 rule in the PRD text** retrieved for this register.

The PRD instead requires a completed trace with a qualifying VASP candidate and specifies these boundary rules:

- HIGH or VERIFIED VASP candidate;
- zero/missing fraud amount → insufficient-data state;
- future/missing incident timestamp → warning and `time_urgency = 1.0`;
- zero-hop trace → invalid for scoring;
- `LEAD` or `NONE` top VASP candidate → do not display the score.

The PRD also defines the deterministic components and RED/AMBER/GREEN display thresholds. fileciteturn11file1L1-L1

### Resolution

Primary UI label:

> **Heuristic Recovery Estimate**

Use the PRD FR-016 eligibility logic as the authoritative baseline.

Do **not** silently enforce the checklist-only:

```text
minimum INR 10,000
data completeness >= 70%
attribution >= MEDIUM
```

unless these are formally promoted into the PRD through change control.

The implementation must enforce:

```text
completed trace
+
qualifying VASP candidate
+
non-zero/non-missing fraud amount
+
valid incident timing
+
hop_count > 0
+
top candidate not LEAD/NONE
```

and use the PRD-defined calculation:

```text
value_ratio
× exchange_cooperation
× time_urgency
× path_clarity
× top_candidate_confidence
```

Primary display:

```text
Heuristic Recovery Estimate
```

Secondary wording, where used:

```text
Recovery Probability (not a statistical probability)
```

### Status

**RESOLVED — PRD FR-016 controls. Checklist thresholds are not automatically binding.**

---

## Conflict 7 — Legal Requisition / Preservation Workflow

### Discrepancy

TraceX can generate legal notices directly without the required supervisor gate.

CryptoTrace requires a controlled preservation-request workflow:

```text
DRAFT
    ↓
PENDING_APPROVAL
    ↓
APPROVED
or
REJECTED
```

The implementation checklist explicitly requires supervisor authorization for approval. fileciteturn9file0L1-L1

### Resolution

Implement:

```text
backend/legal/notice_generator.py
backend/api/notice_routes.py
```

with:

- draft generation;
- evidence binding;
- submission-for-approval;
- supervisor-only approval;
- rejection;
- audit events;
- export after approval where authorized.

Investigators may create/draft but cannot approve.

No automatic:

- asset freezing;
- legal filing;
- statutory submission;
- seizure action.

### Status

**RESOLVED — supervisor-gated workflow controls.**

---

# Additional Governance Rules

## Rule 1 — Live Data Has Separate Acceptance Evidence

A feature is not `LIVE-VERIFIED` merely because its code exists.

Operational evidence must show:

1. real provider connection;
2. actual blockchain data retrieval;
3. normalization;
4. durable persistence;
5. downstream processing;
6. evidence provenance;
7. correct UI presentation.

The PRD explicitly requires operational evidence before claiming live government or external connectivity. fileciteturn11file1L1-L1

---

## Rule 2 — Fixtures Never Become Production Evidence

Fixtures may be used for:

- unit tests;
- integration tests;
- regression tests;
- deterministic adapter tests.

They must not be used as proof of:

- live indexing;
- real VASP attribution;
- live tracing;
- operational recovery;
- production integration.

The PRD explicitly requires a visible LIVE/FIXTURE distinction and prohibits treating synthetic fixtures as real intelligence. fileciteturn11file0L1-L1

---

## Rule 3 — Graph Is Rebuildable Projection

Every graph node and relationship must have corresponding authoritative relational data.

A graph rebuild must be capable of reconstructing the same investigation graph from PostgreSQL. fileciteturn11file7L1-L1

---

## Rule 4 — Etherscan Is Never the Live Ethereum Stream

Etherscan can enrich and retrieve historical information.

It cannot be used as the canonical live Ethereum event ingestion mechanism.

---

## Rule 5 — No Unverified Performance Claims

Do not use claims such as “sub-50ms” unless benchmark evidence exists.

Performance must be measured against defined workloads. fileciteturn11file7L1-L1

---

## Rule 6 — No AI Dependency for Core Functionality

The deterministic system must operate without external LLM credentials.

AI Copilot remains optional and secondary.

The PRD explicitly gates supervised ML behind the qualifying labeled-case requirement and keeps deterministic intelligence as the baseline. fileciteturn11file3L1-L1

---

# Final Resolution Policy

When a discrepancy appears:

1. identify the exact source requirement;
2. identify the higher-precedence document;
3. record the conflict here;
4. implement the higher-precedence requirement;
5. update affected tests;
6. update implementation documentation;
7. do not silently preserve the lower-precedence behavior.

No change to a canonical requirement may be introduced solely inside application code.
