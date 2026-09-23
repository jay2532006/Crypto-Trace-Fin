# CryptoTrace LEA — Product Requirements Document (PRD)

**Project:** SIH 26183 — Real-Time Crypto Fraud Attribution System for Indian Law Enforcement  
**Product:** CryptoTrace LEA  
**Document Status:** Baseline PRD for controlled implementation  
**Authority:** `CRYPTOTRACE_LEA_MASTER_GUIDE_v3.md`  
**Related Document:** `CRYPTOTRACE_LEA_IMPLEMENTATION_PLAN.md`  
**Explanation Document:** `CRYPTOTRACE_LEA_EXPLANATION.docx`

---

## 1. Document Governance

This PRD and the Implementation Plan are linked documents.

- The PRD defines **why**, **what**, **who**, and **acceptance expectations**.
- The Implementation Plan defines **how**, **in what order**, and **how each requirement is verified**.
- Neither document may introduce a requirement that contradicts the Master Guide.
- If a conflict is discovered, the Master Guide takes precedence, followed by verified repository behavior, then these documents.
- Every implementation phase must reference the relevant PRD requirement IDs.
- Every completed requirement must have evidence: code, automated test, operational test, or explicitly documented limitation.

**Evidence language:**
- `CODE-VERIFIED`
- `AUTOMATED-TEST-VERIFIED`
- `OPERATIONALLY-VERIFIED`
- `FIXTURE/SIMULATION-VERIFIED`
- `DOCUMENTATION-ONLY`
- `NOT VERIFIED`

---

## 2. Executive Summary

CryptoTrace LEA helps investigators move from a victim-reported cryptocurrency wallet to actionable, explainable, evidence-backed intelligence.

The reported wallet may be a burner, collection, intermediary, laundering, or externally controlled deposit wallet. Therefore, the product must not act as an ownership oracle. It must trace funds, detect suspicious movement patterns, identify candidate VASPs/exchanges using provenance-aware evidence, represent cross-chain uncertainty, categorize risk, and produce investigator recommendations and evidence packages.

The core product principle is:

> **AI-assisted fraud intelligence, not blind AI automation.**

The first demonstrable system is deterministic, explainable, provenance-aware, and human-supervised. Supervised ML is an optional future augmentation and remains gated by the Master Guide requirement for at least 100 genuinely qualifying court-confirmed labeled cases.

---

## 3. Problem Statement

Investigators often receive a wallet address without a complete understanding of:

- where the funds originated;
- how funds moved through intermediary wallets;
- whether peeling, fan-in, fan-out, rapid-hop, consolidation, mixer, DEX, or bridge behavior occurred;
- whether funds reached a known or suspected exchange/VASP;
- whether cross-chain movement is proven or merely correlated;
- how reliable the attribution is;
- what evidence supports each conclusion; and
- what action can be safely recommended.

Manual investigation across explorers, spreadsheets, exchange labels, and disconnected tools is slow, difficult to reproduce, and vulnerable to inconsistent reasoning.

CryptoTrace LEA provides one controlled investigation workspace for this workflow.

---

## 4. Product Vision

### 4.1 Novel Contributions Beyond Commercial Tools

The SIH submission explicitly foregrounds three defensible project contributions:

1. **MULE_NETWORK:** A purpose-built typology for Indian cybercrime investigation, designed around the behavioral pattern observed in NCRP-documented mule wallet networks. The typology defines a named, versioned, auditable detection rule with explicit evidence fields and confidence limits. It is the primary India-specific innovation in this system. This is a defined contribution to Indian law enforcement investigation that this evaluation specifies and implements; no claim is made about the capabilities of every other system.
2. **AdaptiveVASPScorer:** A context-sensitive attribution scoring system that adjusts confidence weights based on trace characteristics including mixer presence, value magnitude, label quality, hop count, and exchange jurisdiction. The scoring trace is fully explainable, policy-versioned, and auditable per case.
3. **RecoveryProbabilityScore:** A heuristic urgency indicator that translates blockchain tracing results into victim-impact language. It provides a time-bounded estimate of recovery likelihood based on traced value, elapsed time, exchange cooperation, and path complexity, expressed as a number an investigating officer can act on without blockchain expertise.

These three contributions must be stated at the beginning of the demonstration before the technical walkthrough.

Build a near-real-time, multi-chain, investigator-centered intelligence platform that converts suspect wallet addresses into:

1. normalized blockchain facts;
2. bounded fund-flow traces;
3. explainable typology findings;
4. provenance-aware VASP candidates;
5. separate risk and attribution assessments;
6. cross-chain evidence with uncertainty;
7. a deterministic victim-impact recovery estimate;
8. human-reviewable recommendations; and
9. tamper-evident evidence packages.

### 4.1 Novel Contributions Beyond Commercial Tools

For the SIH evaluation narrative, CryptoTrace LEA explicitly positions three capabilities as its project contributions:

1. **`MULE_NETWORK`** — A purpose-built typology for Indian cybercrime investigation, designed around the behavioral pattern observed in NCRP-documented mule wallet networks. The typology defines a named, versioned, auditable detection rule with explicit evidence fields and confidence limits. It is the primary India-specific innovation in this system. This is a defined contribution to Indian law enforcement investigation that this evaluation specifies and implements; no claim is made about the capabilities of every other system.
2. **AdaptiveVASPScorer** — A context-sensitive attribution scoring system that adjusts confidence weights based on trace characteristics including mixer presence, value magnitude, label quality, hop count, and exchange jurisdiction. The scoring trace is fully explainable, policy-versioned, and auditable per case.
3. **RecoveryProbabilityScore** — A heuristic urgency indicator that translates blockchain tracing results into victim-impact language. It provides a time-bounded estimate of recovery likelihood based on traced value, elapsed time, exchange cooperation, and path complexity, expressed as a number an investigating officer can act on without blockchain expertise. It is the primary victim-impact output of the system and is designed specifically for the operational workflow of Indian law enforcement agencies responding to cybercrime complaints.

These are the capabilities that must be named first in the SIH demonstration before the technical workflow begins.

---

## 5. Goals and Non-Goals

### 5.1 Goals

- Support EVM networks, Bitcoin UTXO, and Tron as core demonstration chains.
- Provide continuously updated indexing with checkpoint recovery.
- Handle finality and reorganization states.
- Trace funds with bounded computational controls.
- Detect explainable fraud/laundering typologies.
- Separate risk from attribution confidence.
- Distinguish verified, inferred, and unresolved VASP relationships.
- Distinguish proven bridge events from heuristic cross-chain correlation.
- Provide investigator-friendly dashboards and case workflows.
- Preserve provenance, audit history, and evidence integrity.
- Support authorized NCRP, SAHYOG, and VASP request boundaries.
- Prevent automatic legal action.
- Preserve a clear LIVE vs FIXTURE/DEMO distinction.
- Surface victim-impact urgency through the deterministic RecoveryProbabilityScore on qualifying cases.
- Demonstrate an India-specific `MULE_NETWORK` capability and contextual VASP attribution scoring.

### 5.2 Non-Goals

- Proving legal ownership of a wallet.
- Automatically declaring guilt or criminal liability.
- Automatically freezing funds or filing legal requests.
- Treating an exchange/VASP label as proof of illicit conduct.
- Training supervised ML before the Master Guide gate is met.
- Treating synthetic fixtures as real intelligence.
- Inferring hidden ownership without explicit evidence.
- Cryptographically de-anonymizing mixer transactions; mixer boundary leads are probabilistic investigative aids only.
- Cryptographically de-anonymizing mixer transactions. Mixer-boundary leads are probabilistic investigative aids only.
- Replacing investigator or supervisor judgment.

---

## 6. Users and Personas

### 6.1 Investigator

Needs to:
- ingest a complaint or wallet;
- inspect the fund-flow graph;
- understand suspicious intermediaries;
- filter by hop, time, value, chain, and typology;
- inspect evidence and provenance;
- write notes and recommendations;
- create preservation-request drafts.

### 6.2 Supervisor

Needs to:
- review investigator findings;
- approve or reject preservation-request drafts;
- inspect audit history;
- review confidence, uncertainty, and evidence completeness;
- prevent unsupported legal or attribution conclusions.

### 6.3 Administrator

Needs to:
- manage configuration, roles, policy versions, and integrations;
- inspect system health;
- manage authorized operational settings;
- maintain audit and security controls.

### 6.4 Integration Service

Used for controlled machine-to-machine intake/synchronization, with restricted permissions and explicit provenance.

### 6.5 Bank/AML Analyst

May use the platform as an intelligence consumer or referral source, but cannot be granted law-enforcement privileges by assumption. Any future bank-facing role requires explicit RBAC design.

---

## 7. Product Principles

1. **Evidence before conclusion.**
2. **Attribution is not ownership proof.**
3. **Risk and attribution are separate dimensions.**
4. **Every recommendation is explainable.**
5. **Cross-chain uncertainty is explicit.**
6. **Intermediary wallets are first-class outputs.**
7. **Public and synthetic data are visibly labeled.**
8. **No automatic legal action.**
9. **External integrations require authorization and sandbox/interface specifications before being called live.**
10. **ML must improve calibration or detection against the deterministic baseline; it must not replace provenance or evidence.**
11. **Implementation truth is more authoritative than optimistic documentation.**

---

## 8. Core User Journey

### 8.1 End-to-End Workflow

1. Receive a suspect wallet from investigator intake, NCRP, or an authorized SAHYOG boundary.
2. Validate address and resolve chain/network context.
3. Create or link a case idempotently.
4. Fetch and normalize blockchain activity.
5. Persist transfers and checkpoints.
6. Build/update graph representation.
7. Run bounded tracing.
8. Detect typologies and intermediary behavior.
9. Resolve VASP labels and clusters with provenance.
10. Analyze cross-chain links.
11. Produce separate risk and attribution assessments.
12. Compute the deterministic RecoveryProbabilityScore when the qualifying VASP-confidence condition is met.
13. Generate explainable recommendations.
14. Present results in the investigator workstation.
15. Build a signed/hash-linked evidence manifest.
16. Permit supervisor-gated preservation-request drafting and approval.
17. Preserve an audit trail of every material action.

---

## 9. Functional Requirements

### FR-001 — Case Intake

The system shall accept a suspect wallet through:
- investigator intake;
- authorized NCRP intake;
- authorized SAHYOG bulletin ingestion.

The system shall validate required fields, preserve source provenance, and prevent duplicate case creation.

### FR-002 — Multi-Chain Address Handling

The system shall support:
- EVM addresses and token activity;
- Bitcoin UTXO addresses and transactions;
- Tron/TRC-20 activity.

Confirmed live backbone: Ethereum via ETH_RPC_PRIMARY_URL (WebSocket and HTTP), Polygon via POLYGON_RPC_PRIMARY_URL (WebSocket and HTTP), Tron via TRON_RPC_PRIMARY_URL (HTTP polling) plus TRON_GRID_API_KEY for TRC-20 event indexing, Etherscan via ETHERSCAN_API_KEY for historical address lookups and label enrichment only (never the live event path), Bitcoin via Mempool.space without authentication, and pricing via CoinGecko without authentication. Solana and additional cross-chain capabilities remain extensions only where data sources and evidence can be established.

### FR-003 — Live Indexing

The system shall support continuous indexing with:
- confirmed provider infrastructure;
- retries with bounded backoff/jitter;
- circuit breakers;
- provider provenance;
- confirmed live provider backbone: ETH_RPC_PRIMARY_URL, POLYGON_RPC_PRIMARY_URL, TRON_RPC_PRIMARY_URL, TRON_GRID_API_KEY, ETHERSCAN_API_KEY (historical/labels only), Mempool.space, and CoinGecko;
- deduplication;
- checkpointing;
- finality states;
- reorganization handling;
- explicit LIVE/FIXTURE execution mode.

#### Confirmed Live Provider Backbone

The following providers are secured and are the concrete blockchain-data and supporting-data backbone for the SIH demonstration; no additional provider procurement is required:

- **Ethereum mainnet:** `ETH_RPC_PRIMARY_URL`, available through WebSocket and HTTP. Live head subscription uses `eth_subscribe` / `newHeads`.
- **Polygon PoS:** `POLYGON_RPC_PRIMARY_URL`, available through WebSocket and HTTP. Live head subscription uses `eth_subscribe` / `newHeads`.
- **Tron:** `TRON_RPC_PRIMARY_URL` for full-node HTTP polling plus `TRON_GRID_API_KEY` for TRC-20 event indexing. Tron live polling runs every 3 seconds.
- **Etherscan:** `ETHERSCAN_API_KEY` restricted to historical address lookups and label enrichment. It is never part of the live event path.
- **Bitcoin:** Mempool.space, unauthenticated.
- **Pricing:** CoinGecko, unauthenticated, for market-price enrichment only.

Provider workers shall be isolated so failure of one chain/provider does not stop other chains. Historical lookup, label-enrichment, and pricing workers are auxiliary to the live chain-event path.

WebSocket UI delivery alone shall not be treated as proof of real-time blockchain intelligence.

### FR-004 — Canonical Data Model

The system shall normalize chain-specific records into canonical entities including:
- Chain;
- Address;
- Transaction;
- Transfer;
- Asset;
- EntityLabel;
- PatternFinding;
- VASPCluster;
- CrossChainLink;
- RiskAssessment;
- InvestigativeRecommendation;
- EvidenceManifest;
- Case;
- AuditEvent;
- CryptoAlert.

### FR-005 — Bounded Tracing

Tracing shall support configurable:
- maximum hops;
- time window;
- minimum value;
- maximum outflows;
- maximum nodes;
- timeout.

The system shall prevent uncontrolled graph expansion and expose the applied limits.

### FR-006 — Typology Detection

The system shall detect, explain, and version findings for:
- peel chains;
- fan-in;
- fan-out;
- rapid-hop layering;
- consolidation;
- mixer exposure;
- **`MIXER_BOUNDARY_CLUSTER_LEAD`**;
- DEX boundary;
- bridge-mediated cross-chain movement;
- **`MULE_NETWORK`**.

A finding must store rules/version, inputs, relevant transfers, evidence references, and uncertainty.

#### `MIXER_BOUNDARY_CLUSTER_LEAD`

When the trace engine reaches a known mixer contract and marks the boundary, the system shall search the same mixer pool for withdrawals occurring from the deposit timestamp through +14,400 seconds. It shall identify the deposit pool, denomination, and timestamp, then return withdrawal destinations whose payout amount is between `0.90` and `0.995` of the deposit denomination. Each returned destination is a heuristic investigative lead with fixed `confidence = 0.25` and `confidence_band = LEAD`. This value is immutable and cannot be increased by AdaptiveVASPScorer or any other modifier.

The finding uncertainty note shall be exactly:

> This address received a withdrawal from the same mixer pool in the same denomination window as the traced deposit. This is a timing and denomination correlation only. It is not cryptographic proof of connection to the suspect wallet. Do not treat as confirmed attribution without independent corroboration.

Mixer boundary leads shall render as dashed graph edges from the mixer boundary node to each lead address, with hover label **Possible Exit — Heuristic Only**.

#### `MULE_NETWORK`

A `MULE_NETWORK` finding is raised when three or more suspect-origin wallets — either linked to NCRP complaint records or exhibiting the behavioral signature of a single large inflow immediately followed by a single outflow to a previously unseen address with no other activity — each forward funds through separate intermediate wallets. The intermediate wallets must share at least two of these three properties: (1) first-ever transaction within 48 hours of one another; (2) exactly one inbound transfer and exactly one outbound transfer with no other on-chain activity; (3) transaction amounts within 20% after network fees. All intermediate wallets must direct their outputs to one aggregation address within 72 hours of the first intermediate wallet receiving funds.

Required fields:
- `pattern_type = MULE_NETWORK`;
- `victim_wallet_count` integer;
- `intermediate_wallet_addresses` list of strings;
- `aggregation_address` string;
- `time_window_hours` from first victim outflow to final aggregation;
- `total_value_aggregated_usd`;
- `confidence = MEDIUM`;
- `rule_version`;
- `evidence_references` listing every relevant transaction hash;
- `uncertainty_note` exactly equal to:

> Mule wallet classification is based on behavioral heuristics only. Individual wallet control requires KYC verification which is outside the scope of on-chain analysis.

The finding shall also contain `india_specific = true`. In the investigator UI it shall render with an amber badge reading **India Fraud Pattern**.

### FR-007 — VASP Clustering and Attribution

The system shall distinguish:
- labelled;
- inferred;
- unresolved.

The system shall not present inferred clustering as confirmed ownership. Attribution confidence shall be separate from risk category.

The base attribution score uses the six evidence components and starting weights: label `0.35`, directness `0.25`, retained `0.15`, finality `0.10`, temporal `0.10`, corroboration `0.05`. The starting vector is a policy baseline, not a fixed final vector in all contexts.

#### FR-007-A — Dynamic Attribution Weight Adjustment

The scorer must follow this six-step deterministic processing order:

1. **Load policy version.** Retrieve the active policy document from the versioned policy store and record its version identifier. All thresholds come from this document, not application code.
2. **Apply structural overrides.** `SINGLE_HOP` fires only when `hop_count == 1` and sets the directness base weight to `0.50`. No later modifier may change that directness weight. `LONG_HOP` fires when `hop_count >= 5` and `SINGLE_HOP` did not fire.
3. **Apply contextual multipliers.** Apply applicable multipliers in alphabetical order: `HIGH_VALUE`, `INDIA_EXCHANGE`, `LONG_HOP`, `MIXER_PATH`, and `SPARSE_LABEL`. `BRIDGE_PATH` is reserved for future policy use. `path_contains_bridge` must be recorded as a boolean in `scoring_metadata`, but no current multiplier fires on it.
4. **Resolve remaining conflicts.** If multiple step-3 multipliers modify the same dimension, apply the more conservative adjustment, defined as the multiplier producing the lower absolute weight for that dimension.
5. **Clamp.** Clamp every weight to `0.01–0.80` inclusive.
6. **Renormalize and score.** Divide each weight by the sum so the vector sums exactly to `1.0`, then compute the dot product with the score vector.

Record every step, fired modifier, reason, threshold, intermediate weight vector, final normalized vector, and policy version in `scoring_metadata` for every `VaspCandidate`. Policies are versioned and administrator-updatable without deployment.

### FR-008 — Cross-Chain Intelligence

The system shall distinguish:
- proven bridge events supported by direct evidence;
- heuristic time/value/address correlation.

These states must never be presented as equivalent.

### FR-009 — Risk and Attribution

Risk scoring shall be explainable, versioned, and separately stored from attribution confidence. Every score must identify the rules, inputs, evidence references, and uncertainty flags used.

### FR-010 — Recommendations

Recommendations shall be advisory and explainable. They shall not automatically initiate legal action, freeze funds, or submit statutory requests.

### FR-011 — Evidence and Audit

The system shall:
- create evidence manifests;
- preserve source references;
- maintain tamper-evident audit history;
- support cryptographic integrity verification;
- distinguish hash chaining, authentication signing, and evidence signing;
- preserve immutable references to the evidence state used for a decision.

### FR-012 — Authorized External Boundaries

The system shall support controlled boundaries for:
- NCRP intake and status synchronization;
- SAHYOG bulletin ingestion;
- VASP preservation-request drafting and supervisor approval.

Live government connectivity shall not be claimed without authorization, interface specifications, and operational evidence.

#### FR-012-A — Demo-Ready NCRP Mock Adapter

When `DEMO_MODE=true`, accept the specified NCRP-shaped schema, validate complaint ID `NCRP-YYYY-XXXXXX`, chain/address, fraud type, positive INR amount, ISO timestamp, Indian state, and SHA256 `victim_id_hash` without raw PII. Create a Case with `source=NCRP_INTAKE`, `source_reference=complaint_id`, queue tracing, and return HTTP 201 with `case_id`. Provide a no-payload fixture trigger for one-click demonstration. Expose `demo_data=true` in every mock response and display `DEMO DATA`; use source badges NCRP blue, Manual Entry grey, and SAHYOG purple.

### FR-013 — RBAC

Canonical roles:
- `INVESTIGATOR`
- `SUPERVISOR`
- `ADMINISTRATOR`
- `INTEGRATION_SERVICE`

Approval operations must be supervisor-gated. Investigators may draft where permitted but cannot approve.

### FR-014 — Investigator Workstation

The UI shall provide:
- live/fixture mode visibility;
- alert triage;
- SLA visibility;
- recovery urgency visibility;
- timeline playback;
- hop-depth filtering;
- dense transaction views;
- address copy controls;
- evidence/provenance panels;
- case promotion;
- audit timeline;
- clear uncertainty and confidence labels;
- `MULE_NETWORK` amber `India Fraud Pattern` badge;
- mixer-boundary leads rendered with dashed graph edges and hover text `Possible Exit — Heuristic Only`;
- `FIXTURE REPLAY` badge for every DEMO_WARM response;
- source badges and visible `DEMO DATA` state.

The interface must not look like a generic AI-generated dashboard. Typography, spacing, hierarchy, contrast, density, and interaction patterns must support investigative work.

The fund-flow graph shall show confirmed/solid paths and heuristic mixer-boundary leads/dashed paths as immediately distinguishable visual semantics. `MULE_NETWORK` findings shall use the amber **India Fraud Pattern** badge. `NCRP_INTAKE` cases shall show the blue `NCRP` source badge, manual cases grey, and SAHYOG cases purple.

When a demo warm result is returned, the UI must display the yellow **FIXTURE REPLAY** badge.

### FR-015 — Phase 4 ML Gate

Supervised ML shall remain deferred until the Master Guide's prerequisites are met, including at least 100 genuinely qualifying court-confirmed labeled cases. This is a product-governance gate and is outside the SIH submission scope.

When unlocked after the product gate is legitimately satisfied, the first ML stage shall:
1. establish ground truth;
2. build crypto-specific features;
3. train a gradient-boosting baseline;
4. compare against deterministic rules;
5. deploy only if empirical results justify it;
6. maintain feature attribution and human oversight.

A neural/GNN model shall not be assumed to be the first model.

---

### FR-016 — Recovery Probability Score

For completed traces with a HIGH or VERIFIED VASP candidate, compute the deterministic heuristic `value_ratio × exchange_cooperation × time_urgency × path_clarity × top_candidate_confidence`. Internal identifiers and API/database fields may use `recovery_score`, but the primary UI label must be **Heuristic Recovery Estimate**. `Recovery Probability` may appear only as smaller secondary text with the qualifier **(not a statistical probability)**.

The cooperation registry contains administrator-maintained heuristic estimates. Each entry must record the estimate value, the data source or rationale, last-reviewed date, and reviewer identity. The system must not present these values as factual statistics. The case tooltip must state: `Exchange cooperation value: [value] — administrator estimate, last reviewed [date].`

Boundary rules: (a) if `fraud_amount_inr` or `fraud_amount_usd` is zero or missing, set `value_ratio = 0` and display `Insufficient data — fraud amount not reported.`; (b) if `incident_datetime` is future or missing, set `time_urgency = 1.0` and flag a data-quality warning; (c) reject `hop_count = 0` before scoring as an invalid trace result; (d) if the top VASP candidate has confidence band `LEAD` or `NONE`, do not display the score and show `Attribution confidence insufficient for recovery estimate.`

Use `value_ratio=min(1,traced/fraud)`, `time_urgency=max(.05,1-hours_since_incident/72)`, and `path_clarity=1/max(1,hop_count)`. Persist all components, score, `action_window_hours=max(0,72-hours_since_incident)`, and RED/AMBER/GREEN tiers with explicit boundaries: RED `<0.20`, AMBER `>=0.20 and <=0.50`, GREEN `>0.50`. Display the primary label with component tooltip, source, disclaimer, and supervisor sorting by ascending action window.

## 10. Non-Functional Requirements

### NFR-001 — Security

- No private keys, mnemonics, API keys, bearer tokens, or passwords in logs or tracked files.
- Production authentication must not accept development-only authentication headers.
- Least-privilege RBAC.
- Secure secret configuration.
- Explicit input validation and output sanitization.
- Raw provider payload archives are write-once and are never overwritten or deleted by application workflows.

### NFR-002 — Reliability

- Checkpoint resumability.
- Idempotent ingestion.
- Retry and circuit-breaker behavior.
- Redis DEDUP isolation in database 1 with no eviction policy; loss of dedup records is treated as a reliability failure equivalent to data loss.
- Reorg-aware rollback/reconciliation.
- Durable handling of downstream intelligence failures.
- The Redis `DEDUP` namespace must be isolated in database `1` with **no eviction policy**. Loss of deduplication records is a reliability failure equivalent to event/data loss.

### NFR-003 — Explainability

Every major output must answer:
- What was observed?
- Which rule/model generated the finding?
- What evidence supports it?
- What uncertainty exists?
- What is the confidence level?
- What is not proven?

Every `VaspCandidate` must also expose a complete attribution weight trace: base weights, fired modifiers, modifier reasons, renormalized final weights, and policy version. A missing or incomplete `scoring_metadata` object is an explainability failure. Fixed-confidence mixer-boundary leads must retain their immutable `0.25 / LEAD` scoring metadata.

### NFR-004 — Performance

Performance targets must be measured against defined workloads. No unverified “sub-50ms” or similar claim may be presented as achieved without benchmark evidence. Under normal operation, Redis hot-address lookups shall achieve a hit rate above `80%`. Trace-result cache hit rate is expected to be lower (`20–40%`) because of key specificity and must be measured and reported.

### NFR-005 — Auditability

Material actions must be auditable, including:
- case creation;
- ingestion;
- evidence generation;
- recommendation generation;
- approval;
- external synchronization;
- status transitions;
- configuration changes.

### NFR-006 — Maintainability

- Clear module boundaries.
- Versioned policies and rules.
- Migration-controlled schema changes.
- Tests tied to acceptance criteria.
- Documentation synchronized with actual implementation.

### Canonical Event Identity and Serialization Contract

Every canonical event identity contains five fields: `chain_id`, `tx_hash`, `event_type`, an event-type-specific index field, and secondary `transfer_index`. `event_type` is one of `NATIVE`, `ERC20`, `TRC20`, `INTERNAL`, or `BRIDGE`. ERC20/TRC20 use integer `log_index`; NATIVE uses integer `transfer_index` starting at `0` per transaction; INTERNAL uses integer `trace_index` following provider ordering; BRIDGE uses the protocol message nonce where available, otherwise integer `log_index`. The secondary `transfer_index` distinguishes multiple canonical transfers sharing a log index, including batch-transfer contracts. The PostgreSQL uniqueness constraint covers the complete five-field canonical identity. Each supported chain must document its identity rules before ingestion is enabled; future chains must do the same before activation.

Before hashing, JSON payloads are serialized with alphabetically sorted keys, compact JSON, and no whitespace. The resulting SHA256 is the `raw_payload_hash`; all integrity verification procedures must use this same deterministic serialization.

### NFR-007 — Storage Layer Responsibilities

The system uses four storage layers with fixed responsibilities. Data must not be stored outside the layer responsible for it.

**PostgreSQL — durable system of record.** PostgreSQL stores all durable, legally admissible application data, including cases, evidence items, audit events, ingestion checkpoints, VASP preservation requests, case outcome records, recovery scores, user decisions, and label-registry entries. PostgreSQL participates in the evidence chain. No material case state or decision may exist only in Redis or the graph store.

**Graph store (Memgraph or Neo4j) — traversal projection.** The graph store holds address-to-address relationships, transaction path edges, entity cluster assignments, VASP deposit-cluster membership, and bridge links. It is used for traversal queries and is not a system of record. Every graph node and edge must have a corresponding PostgreSQL row, and the graph must be fully reconstructable from PostgreSQL.

**Redis — speed and coordination layer.** Redis is reconstructable from PostgreSQL and contains only the explicitly defined cache/coordination namespaces. Nothing may exist exclusively in Redis.

**Object storage — raw provider payload archive.** Every raw payload is stored at `raw/chain_id/block_height/tx_hash/provider_name/payload_type/payload_hash.json`, where `provider_name` is a provider slug, `payload_type` is one of `block_response`, `tx_response`, `receipt_response`, `trace_response`, or `event_log_response`, and `payload_hash` is the SHA256 of deterministically serialized JSON. Serialization uses alphabetically sorted keys, compact JSON, and no whitespace. The filename is the hash itself, enabling cross-provider deduplication and cross-reference. PostgreSQL stores this value as `raw_payload_hash`; verification must use the same serialization contract. Object storage is write-once; raw payloads must never be overwritten or deleted.

**Idempotency authority.** PostgreSQL is the permanent correctness safeguard. The `transfers` table must have a database-level UNIQUE constraint on `(chain_id, tx_hash, log_index, event_type, transfer_index)` for the canonical event identity represented by the row. Any violation is silently rejected at the database level and logged as `DUPLICATE_SUPPRESSED`. Redis database 1 is a seven-day speed layer that catches recent duplicates before they reach PostgreSQL; it is not the only protection.

### NFR-008 — Deployment

- SQLite may be used for development/testing where supported.
- PostgreSQL compatibility must not be described as operationally verified unless PostgreSQL is actually exercised.
- Production deployment requires explicit environment, secret, observability, backup, and rollback validation.

---

## 11. Architecture Requirements

The canonical pipeline is:

**Intake → Validate → Index → Normalize → Persist → Graph → Trace → Typology → VASP Intelligence → Cross-Chain Analysis → Risk → Attribution → Recovery Estimate → Recommendation → Alert/Case → Evidence/Audit → Investigator UI**

### Storage and Provider Architecture

The live blockchain backbone is fixed to the confirmed providers defined under FR-003. The implementation must preserve provider-specific provenance and isolate chain workers.

The storage responsibilities are fixed to PostgreSQL (durable system of record), Memgraph/Neo4j (reconstructable graph projection), Redis (speed/coordination namespaces), and write-once object storage (raw provider payload archive). A graph rebuild from PostgreSQL is a required operational capability.

The architecture must separate:

- ingestion from downstream intelligence;
- risk from attribution;
- proven evidence from heuristic inference;
- live data from fixtures;
- machine-generated recommendations from legal decisions;
- external boundary data from blockchain-native data.

---

## 12. Success Criteria

The project is successful when it can demonstrate:

1. A reported wallet entering through a controlled intake boundary.
2. Near-real-time or replayed indexed activity with explicit mode.
3. Bounded multi-hop tracing.
4. Explainable intermediary/typology findings.
5. Candidate VASP identification with provenance.
6. Explicit cross-chain uncertainty.
7. Separate risk and attribution outputs.
8. A RecoveryProbabilityScore shown on qualifying cases with its heuristic disclaimer.
9. `MULE_NETWORK` and mixer-boundary heuristic findings rendered with their required uncertainty semantics.
10. Investigator-readable recommendations.
11. Hash/signature-verifiable evidence artifacts.
12. Supervisor-gated preservation-request workflow.
13. Secure RBAC and auditability.
14. Clear disclosure of all limitations and demo-data boundaries.

The smallest complete demo is:

**Victim-reported burner wallet → trace → suspicious intermediary/layering detection → labeled or candidate VASP identification → risk and attribution explanation → recommendation → evidence manifest.**

---

## 13. Acceptance Criteria Policy

Every acceptance criterion must include:

- requirement;
- implementation location;
- automated test or operational evidence;
- execution mode;
- limitation;
- final status.

Allowed statuses:
- `PASS`
- `PARTIAL`
- `NOT VERIFIED`
- `FAIL`
- `NOT APPLICABLE`

No feature is considered complete solely because a file exists or a test is scheduled.

---

## 14. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| False attribution | Separate candidate attribution from ownership proof; preserve evidence and uncertainty |
| False positives | Explain rules, expose evidence, use human review |
| Chain reorganization | Finality state machine, checkpoint rollback, reprocessing |
| Provider outage | Retry, circuit breaker, failover, provenance |
| External portal unavailable | Local durable state plus explicit remote-pending status |
| Synthetic data overclaim | Visible fixture/demo labeling |
| Data leakage | Case-level and potentially temporal splits; duplicate detection |
| ML overconfidence | Calibration, baseline comparison, feature attribution, human approval |
| Legal overreach | Draft-only requests and supervisor approval |
| Secret exposure | Sanitization, secret scanning, redacted provenance |
| UI overload | Progressive disclosure, filters, dense but structured investigator views |

---

## 15. Competitive/Innovation Positioning

The defensible product position is not “AI predicts criminals.” It is:

> **Evidence-backed, multi-chain investigative intelligence with explainable attribution, explicit uncertainty, durable provenance, and human-supervised legal workflows.**

Differentiators:
- deterministic explainability before ML;
- intermediary-first investigation;
- provenance-aware VASP clustering;
- proven vs heuristic cross-chain distinction;
- operational resilience and reorg handling;
- evidence/audit integration;
- supervisor-gated external legal workflows;
- investigator-focused UI rather than a graph-only visualization;
- `MULE_NETWORK` as the primary India-specific innovation contribution;
- AdaptiveVASPScorer with contextual weight adjustment and a complete scoring trace;
- RecoveryProbabilityScore with an action-window view of victim-impact urgency.

---

## 16. Out of Scope Until Explicitly Approved

- Automatic fund freezing.
- Automatic legal filing.
- Unverified government portal production claims.
- Unsupervised ownership inference.
- Neural ML before the Phase 4 gate.
- TEE/HSM claims without actual deployment evidence.
- Performance claims without reproducible benchmarks.

---

## 17. Document Linkage

The Implementation Plan must implement this PRD in phase order and map every phase to PRD IDs.

The Explanation document must describe the same architecture and terminology without introducing new requirements.

Any future change must update:
1. PRD;
2. Implementation Plan;
3. relevant architecture explanation;
4. acceptance criteria;
5. change log;
6. tests/evidence.

