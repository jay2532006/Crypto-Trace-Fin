# CryptoTrace LEA — System Architecture (SIH 26183)

## 1. Architectural Philosophy: Evidence-First Intelligence
CryptoTrace LEA is engineered strictly as an **evidence-first, explainable, live-data-driven investigative intelligence system** designed for Indian Law Enforcement Agencies (LEA) and Cyber Crime Cells under the Ministry of Home Affairs (MHA) and I4C guidelines.

Unlike black-box AI tools or ungrounded heuristic engines:
- Every finding is anchored to raw, cryptographically hashed on-chain transactions.
- Probabilistic attribution and deterministic risk scoring are decoupled into independent dimensions.
- Algorithmic claims undergo versioned scoring policies (`policy_v1_india_kyc`) with explicit forensic audit traces.
- Statutory notices under Section 91 BNSS 2023 require mandatory supervisory officer sign-off prior to dispatch.

---

## 2. High-Level System Architecture

```text
                  +-------------------------------------------------+
                  |       LAW ENFORCEMENT INVESTIGATOR DESK         |
                  |     (dashboard.html — Cyber Forensic Station)    |
                  +-----------------------+-------------------------+
                                          |
                        HTTPS / JSON-RPC / REST API
                                          |
                  +-----------------------v-------------------------+
                  |         CRYPTOTRACE FASTAPI BACKEND             |
                  |     (RBAC, JWT, Audit Chains, Lockdowns)        |
                  +-------+-------------------------------+---------+
                          |                               |
       +------------------v--------------+   +------------v------------------+
       |   CORE FORENSIC INTELLIGENCE    |   |    8-STAGE INGESTION ENGINE   |
       | • Mule Network Engine (SIH-26183) |   | 1. FETCH      5. DEDUPLICATE  |
       | • Adaptive VASP Scorer (6-Step)  |   | 2. VALIDATE   6. PERSIST (DB) |
       | • Heuristic Recovery Estimator  |   | 3. EXTRACT    7. COMMIT (CP)  |
       | • Cross-Chain Analyzer (Proven) |   | 4. NORMALIZE  8. ADVANCE      |
       | • Mixer Boundary Heuristic      |   +------------+------------------+
       | • Bounded Deterministic Tracer  |                |
       +------------------+--------------+                |
                          |                               |
       +------------------v-------------------------------v------------------+
       |                     DURABLE SYSTEM OF RECORD                        |
       | • Authoritative Database (PostgreSQL / SQLite fallback)            |
       | • Deterministic Raw Storage (SHA-256 / data/raw/...)                |
       | • Chained Cryptographic Audit Ledger (SHA-256 event chaining)       |
       | • Graph Projection Engine (Rebuildable from DB authority)          |
       +------------------+--------------------------------------------------+
                          |
       +------------------v--------------------------------------------------+
       |               ISOLATED LIVE PROVIDER BACKBONE                       |
       | • Ethereum (RPC Primary + Etherscan Fallback)                       |
       | • Polygon (RPC Primary + Polygonscan Fallback)                      |
       | • Bitcoin (Mempool.space Primary + Esplora Fallback)                |
       | • TRON (TronGrid TRC-20 + Full Node RPC)                            |
       | • CoinGecko (Indicative Fiat/Spot Rates Only)                       |
       +---------------------------------------------------------------------+
```

---

## 3. Primary SIH 26183 Innovations

### 3.1 ⭐ Mule Network Typology Engine (`MULE_NETWORK`)
- **Target Threat**: Organized Indian cyber fraud syndicates (Telegram tasks, digital arrest scams, investment fraud).
- **Detection Criteria**:
  1. Minimum 3 suspect-origin intermediate wallets.
  2. Single-in / single-out pass-through behavior.
  3. Fee-normalized flow consistency (within 15% tolerance of incoming sum).
  4. Temporal velocity: transfers forwarded within < 60 minutes.
- **Explainability & Safeguards**:
  - `india_specific = True`.
  - **Fixed MEDIUM confidence ceiling**: Strictly prevents ungrounded high-confidence attribution claims on intermediate unhosted wallets without KYC disclosure.
  - **Mandatory Uncertainty Disclosure**: Explicitly discloses that intermediate wallet ownership cannot be proven solely from transaction velocity.

### 3.2 ⭐ Adaptive VASP Scorer (`AdaptiveVASPScorer`)
- **Dynamic 6-Step Scoring Sequence**:
  1. Base Prior Probability (Direct deposit address vs hop distance).
  2. Alphabetical Contextual Modifiers (Clustering, hot wallet sweeps, velocity).
  3. Conservative Conflict Resolution.
  4. Penalty Clamping to $[0.01, 0.80]$.
  5. Exact Renormalization to $1.0$.
  6. Confidence Band Assignment & Data Completeness Cap (Caps at `MEDIUM` if completeness < 70%).
- **Policy Versioning**: Tagged with `policy_v1_india_kyc`.
- **Classification**: Categorizes entities strictly into `VERIFIED` (known deposit wallet in FIU registry) or `INFERRED` (multi-hop proximity).

### 3.3 ⭐ Heuristic Recovery Estimate (`RecoveryProbabilityScore`)
- **Operational Purpose**: Enables LEA commanders to prioritize emergency freezing requisitions before off-ramp liquidation.
- **Telemetry Factors**:
  - Value Ratio: Threshold gating ($\ge ₹10,000$ / $\$120$).
  - Exchange Cooperation: FIU-registered Indian exchange vs offshore non-cooperative VASP.
  - Temporal Urgency: Exponential decay function over 24-hour action window.
  - Hop Path Clarity: Hop count distance and privacy mixer taint.
- **Mandatory Disclaimer**: Labeled as a **Heuristic Recovery Estimate** (0-100), explicitly disclaiming statistical guarantee of recovery.

---

## 4. Ingestion & Storage Architecture

### 4.1 Authoritative Persistence vs Projections
- **PostgreSQL / SQLite**: Authoritative system of record for all cases, transfers, findings, assessments, and notices.
- **Graph Projection**: In-memory NetworkX (or Neo4j) is strictly a **rebuildable projection**. It can be purged and completely reconstructed from DB transfers via `rebuild_from_db()` without data loss.
- **Redis**: Dedicated exclusively to transient duplicate suppression and hot caches; never used as single source of truth.

### 4.2 Raw Payload Storage & Evidence Manifest
- Raw incoming blockchain responses are serialized deterministically (alphabetically sorted keys, compact separators).
- Stored under `data/raw/{chain}/{block}/{tx}/{provider}/{hash}.json`.
- The SHA-256 hash forms an immutable cryptographic reference for court-admissible evidence under Section 65B of the Indian Evidence Act / BSA 2023.

### 4.3 Tamper-Evident Chained Audit Ledger
- Every state mutation (case creation, trace execution, notice submission, approval) produces an `AuditEvent`.
- Each event incorporates the `previous_event_hash`, forming a verifiable cryptographic blockchain within SQLite/PostgreSQL.
- Any unauthorized database tampering immediately invalidates `verify_audit_chain()`.

---

## 5. Security & Governance Boundaries
- **Direct Cypher Disabled**: `/api/neo4j/query` returns HTTP 403 Forbidden to prevent injection attacks and unconstrained graph queries.
- **Outbound HTTP Tester Disabled**: `/api/test/custom` returns HTTP 403 Forbidden to prevent Server-Side Request Forgery (SSRF).
- **Supervisor-Gated Preservations**: Lawful Section 91 notices start as `DRAFT` and cannot be dispatched without authenticated `SUPERVISOR` sign-off.
