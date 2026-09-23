# CryptoTrace LEA vs. TraceX Technical Baseline

## 1. Executive Summary

This document establishes the authoritative technical baseline comparison between the legacy **TraceX** codebase and the **CryptoTrace LEA (SIH 26183)** target architecture. 

CryptoTrace LEA is **not a rebranding** of TraceX. TraceX served as an initial prototype scaffold that contained significant architectural gaps, mock-heavy endpoints, and unverified data claims. CryptoTrace LEA completely overhauls the foundation into an **evidence-backed, auditable, and court-defensible blockchain intelligence platform** purpose-built for Indian Law Enforcement Agencies (MHA/I4C).

---

## 2. Architectural Comparison Matrix

| Capability Area | Legacy TraceX Baseline | CryptoTrace LEA Target Architecture |
| :--- | :--- | :--- |
| **Primary Data Authority** | Volatile in-memory mock dicts or fragile Neo4j state | Authoritative PostgreSQL relational store with 15+ canonical entities and migrations |
| **Graph Projection** | Direct coupling to Neo4j; loss of graph = loss of truth | Graph as a transient, rebuildable projection (`rebuild_from_db()`); PostgreSQL is source of truth |
| **Raw Ingestion & Storage** | Ephemeral, lossy parsing directly to memory | Canonical deterministic payload storage (`RawPayloadStorage`) keyed by SHA-256 with sorted JSON keys |
| **Audit Logging** | Unchained application logs; easily mutated or deleted | Cryptographically chained audit engine (`AuditEngine`) with SHA-256 hash-linking and verification |
| **Role-Based Access Control** | Single-role or development-mode header bypasses | Strict canonical RBAC (`INVESTIGATOR`, `SUPERVISOR`, `ADMINISTRATOR`, `INTEGRATION_SERVICE`) via JWT |
| **Security Surface** | Exposed endpoints (`/api/test/custom`, `/api/neo4j/query`) | Locked down with HTTP 403 Forbidden; strictly sanitized input boundaries |
| **Typology Detection** | Hardcoded heuristics; conflated peel chains with mule networks | Formalized `MULE_NETWORK` rule: $\ge 3$ intermediate hops, $<60\text{m}$ velocity, $\pm 15\%$ fee tolerance, strict `MEDIUM` confidence ceiling |
| **VASP Attribution** | Arbitrary static string matching | `AdaptiveVASPScorer`: 6-step context weighting, `policy_v1_india_kyc`, `VERIFIED`/`INFERRED` classification, clamp $[0.01, 0.80]$ |
| **Asset Recovery Probability** | Mock percentage numbers displayed without evidence | `Heuristic Recovery Estimate`: PRD FR-016 boundary gating (zero-hop rejected, LEAD/NONE rejected, sub-$120 rejected) |
| **Cross-Chain Tracking** | Claimed automatic cross-chain tracing | Strict classification: `PROVEN` (bridge deposit/claim event) vs `HEURISTIC_CORRELATION` (time/amount proximity) |
| **Legal Workflows** | Static mock PDF export | Section 91 CrPC notice generation with state-machine governance (`DRAFT` $\to$ `PENDING_APPROVAL` $\to$ `APPROVED`) |
| **External Gateways (NCRP / SAHYOG)** | Mocked responses simulating live government portals | Explicit boundary adapters with private-key rejection; reports `UNAVAILABLE_UNAUTHORIZED` if unauthenticated |
| **Ingestion Pipeline** | Ad-hoc polling script without checkpointing | 8-stage resilient pipeline (`FETCH`, `VALIDATE`, `EXTRACT`, `NORMALIZE`, `DEDUPLICATE`, `PERSIST`, `COMMIT`, `ADVANCE`) with reorg rollback |

---

## 3. Detailed Component Disposition

### 3.1 Preserved and Adapted Components
- **Dashboard UI Layout**: Adapted `dashboard.html` to integrate live-data banners for Mule Network uncertainty, interactive 6-step VASP weights, recovery action countdowns, and Section 91 approval decks.
- **Multi-Chain Provider Base**: Adapted `backend/adapters/` into an abstraction layer (`ChainAdapterBase`) driving EVM (RPC), Bitcoin (Mempool.space), and Tron (TronGrid) adapters.

### 3.2 Deprecated and Rebuilt Components
- **Mock Ingestion**: Replaced with `LiveIngestionPipeline` supporting block checkpoints, reorg detection, and validation circuit breakers.
- **Neo4j Direct Querying**: Replaced with `GraphProjection` in `backend/graph/graph_projection.py` utilizing NetworkX for fast graph computations, rebuildable on demand from PostgreSQL.
- **Unverified Typologies**: Replaced with deterministic rules in `backend/typologies/rules/` that bind every finding to exact transaction hashes and include mandatory uncertainty disclosures.

---

## 4. Key Inventions Introduced

1. **Mule Network Typology Rule (`MuleNetworkRule`)**:
   - Detects layered smurfing patterns across 3 or more intermediate hops.
   - Enforces a temporal velocity under 60 minutes per hop.
   - Requires gas/fee variance within $\pm 15\%$.
   - Enforces a strict `MEDIUM` confidence ceiling to prevent overstating algorithmic certainty in court.

2. **Adaptive VASP Scorer (`AdaptiveVASPScorer`)**:
   - Implements a 6-step context-weighted scoring formula:
     $$\text{Final Score} = \sum (\text{Step Weight} \times \text{Step Evidence})$$
   - Classifies attribution into `VERIFIED` (on-chain operational proof) or `INFERRED` (heuristic).
   - Bounds individual step adjustments between $0.01$ and $0.80$ to eliminate arbitrary extremes.

3. **Heuristic Recovery Estimate (`RecoveryEstimator`)**:
   - Gated strictly by PRD FR-016 boundary criteria:
     - Zero-hop traces $\implies$ `ESTIMATE_NOT_APPLICABLE` (untracked funds).
     - Attribution is `LEAD` or `NONE` $\implies$ `ESTIMATE_NOT_APPLICABLE` (no identifiable counterparty).
     - Transfer volume $< \$120$ $\implies$ `LOW_VALUE_UNECONOMIC` (uneconomic to pursue).
   - Computes an actionable 72-hour window countdown linked to VASP compliance latency.

---

## 5. Compliance and Defensibility

All code adheres strictly to Indian legal requirements:
- Section 65B Indian Evidence Act compliant raw payload preservation.
- Section 91 CrPC notice generation with cryptographic tamper evidence.
- Zero credential leakage: Incoming NCRP/SAHYOG inputs are scanned and rejected if private keys or seed phrases are detected.
