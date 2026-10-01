# CryptoTrace LEA — Unified Product & Functional Specification
**Smart India Hackathon SIH 26183 | Ministry of Home Affairs (MHA) / I4C CIS Division**  
**Version:** 2.1.0-SIH26183  
**Status:** 100% IMPLEMENTED & VERIFIED (129/129 Tests Passing, 10 Immutable Golden Baselines)  

---

## Master Document Navigation
This master document consolidates all product requirements, functional definitions, user experience requirements, and statutory boundary conditions into a single authoritative reference with zero content loss.

- [Part 1: Executive Product Brief & Capability Overview](#part-1-executive-product-brief--capability-overview) (Source: `PRODUCT_BRIEF.md`)
- [Part 2: Product Requirements Document (PRD: FR-001 - FR-016)](#part-2-product-requirements-document-prd-fr-001---fr-016) (Source: `CRYPTOTRACE_LEA_PRD (1).md`)
- [Part 3: Frontend UI/UX Specification & Screen Catalog](#part-3-frontend-uiux-specification--screen-catalog) (Source: `Frontend Requirements.md`)
- [Part 4: System Limitations, Uncertainty & Boundary Conditions](#part-4-system-limitations-uncertainty--boundary-conditions) (Source: `docs/LIMITATIONS.md`)

---

# Part 1: Executive Product Brief & Capability Overview
> **Original Source Document:** `PRODUCT_BRIEF.md`  
> **Lines Preserved:** 309  

---

# TraceX Sahyog — Product Brief
### Real-Time Crypto Fraud Attribution System for Indian Law Enforcement
**Aligned with MHA / I4C Problem Statement SIH 26183**
**Version 2.0 | Prepared for Internal Review & Evaluation**

---

## Table of Contents

1. [The Problem — In Plain Language](#1-the-problem--in-plain-language)
2. [What This Product Does](#2-what-this-product-does)
3. [Who Is This For](#3-who-is-this-for)
4. [The Core Workflow — Step by Step](#4-the-core-workflow--step-by-step)
5. [Key Capabilities](#5-key-capabilities)
6. [What Makes It Novel](#6-what-makes-it-novel)
7. [Scope & Boundaries](#7-scope--boundaries)
8. [Technical Architecture (For Engineers)](#8-technical-architecture-for-engineers)
9. [Legal & Compliance Foundation](#9-legal--compliance-foundation)
10. [Demonstration Scenarios](#10-demonstration-scenarios)
11. [Known Constraints & Honest Disclosures](#11-known-constraints--honest-disclosures)
12. [What Success Looks Like](#12-what-success-looks-like)

---

## 1. The Problem — In Plain Language

Every day in India, thousands of people lose money to cryptocurrency scams — investment frauds, sextortion, ransomware, task-based frauds, and organized cybercrime networks. When a victim reports the scam, they typically provide the wallet address the fraudster told them to send money to.

Here is what happens next, and why it's a problem:

**Fraudsters do not receive money directly.** They use a chain of wallets designed to obscure the trail:

- A victim sends money to **Wallet A** (a "burner" or temporary wallet).
- Wallet A immediately moves money to **Wallet B**, then B to C, and so on — sometimes across different blockchains entirely.
- Eventually the money reaches **Wallet X** — an exchange (also called a VASP — Virtual Asset Service Provider) — where it can be converted to cash.

The investigator only knows about Wallet A. Without identifying Wallet X — the exchange where the money actually lands — there is **no one to serve a legal notice to, no asset to freeze, and no chance of recovery.**

Doing this manually — following every transaction hop across potentially multiple blockchains — requires rare technical expertise and takes days. During those days, the money moves further, gets mixed or bridged across chains, and recovery becomes practically impossible. Law enforcement agencies describe a window of **24–48 hours** as the most critical for any chance of fund recovery. That window is almost always lost.

**TraceX Sahyog was built to close that window.**

---

## 2. What This Product Does

TraceX Sahyog is a software platform that takes a victim-reported wallet address and, in near-real time, automatically:

1. **Traces the money** — follows forward and backward (fan-in upstream) transaction hops across up to 6 hops on Ethereum, Tron, Bitcoin, Polygon, and BSC/BNB
2. **Identifies the exchange** — finds which registered crypto exchange (VASP) is the nearest direct deposit destination (hop-order traversal), ranking multiple candidates on ambiguous matches
3. **Flags every suspicious wallet along the way** — mule networks, peeling chains, consolidation funnels, rapid hops, DEX swaps, and mixer boundaries
4. **Detects obstructions** — identifies when money enters a privacy mixer or crosses to another blockchain
5. **Generates legal documents** — drafts Section 91 BNSS freeze notices ready for supervisor approval
6. **Creates court-admissible PDF reports** — with cryptographic integrity, reproducible byte-for-byte
7. **Provides an AI Copilot** — gives investigators plain-language next steps grounded only in the evidence

Everything is logged, timestamped, and cryptographically sealed so the evidence holds up in court.

---

## 3. Who Is This For

| Persona | Role in This System | What They Get |
|---|---|---|
| **Cyber Crime Investigator** | Primary user; runs traces, manages cases | Trace results, graph visualization, AI recommendations, PDF reports |
| **Supervisory Officer** | Authorizes legal notices | Notice review queue, one-click approve/reject with cryptographic sign-off |
| **System Administrator** | Manages platform, API keys, providers | System configuration, provider health monitoring |
| **Court / Legal Authority** | Receives evidence packages | Section 65B certified PDF dossiers with SHA-256 integrity proof |
| **VASP Nodal Officer** | Receives Section 91 notices | Formally drafted statutory preservation order with transaction evidence |

---

## 4. The Core Workflow — Step by Step

### For a Non-Technical Reader:

```
Victim reports scam wallet address
        ↓
Officer enters wallet address into TraceX Sahyog
        ↓
System automatically follows the money (up to 6 hops)
        ↓
System identifies the exchange (VASP) where money landed
        ↓
System flags every suspicious intermediate wallet
        ↓
Officer reviews graph visualization and AI recommendations
        ↓
Officer requests a Section 91 legal notice (one click)
        ↓
Supervisor reviews and approves the notice
        ↓
Notice sent to exchange's Nodal Officer → Assets frozen
        ↓
Court-admissible PDF report generated for prosecution
```

### For a Technical Reader:

**Step 1 — Complaint Ingestion** (`POST /api/v1/intake/ncrp/complaint`):
A wallet address arrives from the NCRP/SAHYOG portal. The `IntakeOrchestrator` state machine receives it, deduplicates it against the SQLite database, and sanitizes it through the BIP-39 validator — which quarantines any accidental submission of seed phrases or private keys before they can be stored.

**Step 2 — Bounded Multi-Hop Tracing** (`POST /api/v1/trace` & `WS /ws/trace/{case_id}`):
The `bounded_tracer` in `backend/tracing/trace_engine.py` performs a breadth-first traversal of on-chain transactions. It supports forward, backward (fan-in upstream funding sources up to 2 hops), and bidirectional tracing across Ethereum, Tron, Bitcoin, Polygon, and BSC/BNB Chain (Chain ID 56). Calls route through `fetch_with_failover()` across primary/fallback RPCs protected by `ProviderCircuitBreaker` (threshold=3, cooldown=60s) and a 5-tier `TTLCache`. Intercepts decentralized exchange routing via `DEX_REGISTRY` (Uniswap, PancakeSwap, Curve, SunSwap), tagging swap pools as `defi_swap` and resetting tracked asset quantities while continuing BFS traversal. Real-time progress is streamed via WebSocket (`WS /ws/trace/{case_id}`).

**Step 3 — VASP Attribution** (`backend/attribution/attribution_resolver.py`):
The `AttributionResolver` walks BFS hops in traversal order and evaluates each address against the expanded 15+ VASP registry (10 FIU-registered Indian exchanges + 5 global exchanges). It resolves the nearest VASP deposit first. When ambiguous or multiple cluster matches occur, `score_all_candidates()` returns a ranked list of candidates with calibrated confidence scores (hop decay penalty capped at -0.20, with a `deep_trace_partial` band for scores 40–59 across deep paths).

**Step 4 — Typology Detection** (`backend/typologies/`):
The `typology_engine.py` classifies the trace into verified typology rules: `MULE_NETWORK` (deterministic behavioral heuristics without synthetic fallbacks), `MIXER_BOUNDARY` (Tornado Cash pool halting and pre-mixer targeting), `RAPID_HOP` (calibrated to chain-specific block times: ETH 10,800s, TRON 3,600s, BTC 86,400s, POLYGON 1,800s, BSC 3,600s), `CROSS_CHAIN_BRIDGE`, `OFAC_SANCTION_HIT`, `PEEL_CHAIN` (real algorithm verifying 0.5%–5% per-hop reduction across >=3 unique addresses), `CONSOLIDATION_FUNNEL` (detecting 2+ branches merging into an aggregation wallet before a VASP deposit, tracking `convergence_nodes`), and `REPEAT_OFFENDER_WALLET` (cross-case syndicate detection via `wallet_index`).

**Step 5 — Cross-Chain Bridge Detection** (`backend/cross_chain/`):
The `cross_chain_analyzer.py` checks each hop against `bridge_registry.py`, which holds router contracts and event topics for Stargate, Across V2, and Wormhole. A `PROVEN` link is emitted when a smart contract event is decoded directly. A `HEURISTIC_CORRELATION` link is emitted when temporal correlation alone supports the bridge conclusion.

**Step 6 — OFAC Sanctions Screening** (`engine/ofac_sanctions.py`):
Every traversed address is screened against the US Treasury OFAC Specially Designated Nationals (SDN) list with exact address hashing and fuzzy entity-name matching (`difflib.SequenceMatcher`, threshold=0.85, supporting batch processing via `bulk_fuzzy_screen_entities()`). An OFAC hit applies a +45 risk score bump, forces risk level to `CRITICAL`, halts traversal at the sanctioned node, sets attribution to `UNRESOLVED`, and triggers automated alert dispatch (`AlertDispatcher`).

**Step 7 — Evidence & Audit** (`backend/audit/`):
Every trace action is appended to a SHA-256 chained audit ledger. Each event hash incorporates the hash of the preceding event, making any post-facto tampering cryptographically detectable.

**Step 8 — Report Generation** (`backend/legal/`):
The `ReportGenerator` uses ReportLab with `rl_config.invariant = 1` for deterministic PDF output — the same inputs always produce a bit-for-bit identical PDF with the same SHA-256 hash. This reproducibility is required for Section 65B evidence admissibility.

---

## 5. Key Capabilities

### 5.1 Multi-Chain Tracing
The system traces transactions across Ethereum (ERC-20 tokens including USDT, USDC), TRON (TRC-20 USDT — heavily used in India-linked scam flows), Bitcoin, Polygon, and BSC/BNB Chain (Chain ID 56, Ankr public RPC, with EVM 0x address disambiguation vs Ethereum). Live blockchain data is fetched through resilient provider cascades (`fetch_with_failover()`) with circuit breakers and a 5-tier TTL cache. When APIs are unavailable, the system handles failover gracefully without fabricating evidence.

### 5.2 Privacy Mixer Boundary Handling
When a traced wallet enters a known privacy mixer, the engine stops tracing forward rather than producing false attribution. Instead it marks the last known pre-mixer wallet as the primary freeze target, generates a Mixer Boundary Directive with specific recommended off-chain actions, and lists exit candidates capped at addresses with ≤ 0.25 ETH withdrawn post-mixing to reduce false positive risk.

### 5.3 Exchange Wallet Clustering & Nearest-VASP Attribution
The VASP registry contains 10 Indian exchanges (Mudrex, BitBNS, Giottus, Unocoin, Pi42, CoinSwitch, BuyUcoin, KoinBX, SunCrypto, Flitpay) and 5 global exchanges (OKX, Bitget, MEXC, HTX, Gate.io) with their known deposit address clusters, FIU-IND registration status, geographic coordinates (ISO country, lat/long, FATF status via `GET /api/v1/vasps/geo`), and nodal officer contact information. The engine walks BFS hops in traversal order to attribute the nearest exchange receiving direct deposits, and ranks multiple candidates via `score_all_candidates()` on ambiguous matches.

### 5.4 Statutory Notice Generation & FIU-IND Compliance (Maker/Checker)
The platform implements a two-officer approval workflow for Section 91 BNSS notices and FIU-IND compliance auto-drafts under PMLA Section 12A. Notices auto-populate the VASP nodal officer email (`nodal_officer_email` from `VASP_REGISTRY`), statutory Section 12A obligations, a **MANDATORY REPORTING ENTITY** badge, transaction hashes, and case metadata. An Investigator drafts the notice, and a Supervisor reviews and cryptographically approves or rejects it.

### 5.5 AI Investigator Copilot
An AI assistant panel gives investigators plain-language investigative recommendations grounded strictly in the trace evidence. It is configured with an explicit anti-hallucination guardrail — it will not reference any address, hash, or entity not present in the active trace payload. It supports queries in English and Hindi. The AI provider badge (Groq, Gemini, or Rule-Based Fallback) is always visible so investigators know exactly what generated the recommendation.

### 5.6 Court-Admissible Evidence Package & INR/USD Dual Display
Every case generates: a deterministic PDF investigation dossier with fund-flow graph, hop table, attribution decomposition, and audit hashes (Section 65B compliant); dual currency reporting with `traced_value_usd` and `traced_value_inr` (at fixed 83.5 INR/USD conversion rate) at case root and per-hop (`amount_usd` and `amount_inr`); a color-coded Data Completeness KPI bar (green >=85%, amber 65–84%, red <65%) exposing `earliest_transaction_date`; a SHA-256 chained audit ledger covering all system actions; and a cryptographic evidence payload verifiable via the evidence integrity endpoint.

### 5.7 Recovery Urgency Calculator & Fraud-Type Modifiers
A calibrated recovery calculator estimates the operational feasibility of fund recovery, accounting for elapsed time since crime, transaction value, chain type, VASP cooperation history, and fraud-type modifiers (TASK_BASED +5, RANSOMWARE -10, SEXTORTION -15, DARKNET -30, ORGANIZED_CRIME -10, INVESTMENT_SCAM/PHISHING 0). When elapsed time is unverifiable, it places the trace into an `insufficient_data` tier without fabricating false urgency (no hardcoded 2.5h fallback). Cases with mixer obstructions or below-threshold values display explicit disclaimers per PRD FR-016.

### 5.8 NCRP / SAHYOG Integration
The intake module receives wallet addresses from the National Cybercrime Reporting Portal (NCRP) and the SAHYOG multi-agency threat intelligence platform. The intake endpoint includes a BIP-39 seed phrase quarantine filter — if a victim accidentally pastes their own wallet recovery phrase into a complaint form, the system detects and quarantines it rather than storing it.

---

## 6. What Makes It Novel

Commercial blockchain tracing tools exist. This is an honest acknowledgment. What differentiates TraceX Sahyog:

| Differentiator | What it means in practice |
|---|---|
| **Indian legal framework integration** | Notices drafted under Section 91 BNSS (2023), not generic freeze requests. Evidence framed for BSA/IEA Section 65B admissibility. |
| **Mixer boundary halting with partial intelligence** | Rather than tracing through a mixer and producing false attribution, the system stops, explains why, and provides actionable pre-mixer intelligence. |
| **PROVEN vs. HEURISTIC bridge classification** | Cross-chain hops are classified by evidence quality — investigators know whether a bridge crossing is confirmed by smart contract events or inferred by correlation. |
| **Deterministic PDF reproducibility** | The same case always produces an identical PDF SHA-256 hash. This is a court requirement, not a feature. |
| **BIP-39 quarantine at intake** | Prevents accidental exposure of victim wallet credentials submitted via complaint portals. |
| **Transparent data source labeling** | Every API response labels each data point as LIVE, SIMULATED, or HARDCODED. Investigators never confuse real data with fallback data. |
| **Grounded AI with provider transparency** | Copilot recommendations cite only evidence in the active trace. The provider badge is always shown. |

---

## 7. Scope & Boundaries

### In Scope
- Tracing wallet addresses reported through NCRP/SAHYOG complaint portals
- Multi-hop forward and fan-in backward on-chain traversal for Ethereum (ERC-20), TRON (TRC-20), Bitcoin, Polygon, and BSC/BNB Chain
- VASP attribution with confidence scoring and FIU-IND registry cross-reference
- Privacy mixer boundary detection and partial intelligence generation
- Cross-chain bridge detection (Stargate, Across V2, Wormhole)
- OFAC SDN sanctions screening for every traversed address
- Mule network and layering pattern detection
- Statutory Section 91 BNSS notice drafting and two-officer approval workflow
- Court-admissible PDF report generation with Section 65B certification
- SHA-256 chained audit trail for tamper-evident evidence integrity
- Role-Based Access Control (Investigator, Supervisor, Administrator)
- AI investigator copilot with anti-hallucination grounding
- 4-factor recovery urgency estimation with honest ineligibility disclosure

### Out of Scope (Honest Boundaries)
- **Tracing through mixers**: The system deliberately halts at mixer boundaries. There is no claim of de-mixing capability.
- **DeFi protocol depth tracing**: Complex DeFi interactions (liquidity pools, flash loans) are flagged but not deeply traced in the current version.
- **Wallet attribution for unlabeled VASPs**: Attribution accuracy is bounded by the VASP label registry. Wallets connecting to unlabeled entities resolve as `UNRESOLVED`.
- **Criminal prosecution**: The system generates intelligence and legal documents. Prosecution decisions remain with the competent authority.
- **KYC data access**: The system identifies which exchange holds the funds. KYC unmasking requires the exchange's response to the Section 91 notice — the system facilitates but cannot compel that response.

---

## 8. Technical Architecture (For Engineers)

### Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python), Uvicorn ASGI |
| Database | SQLite with SHA-256 chained audit tables |
| Frontend | Next.js 14 (App Router), React 18, Framer Motion, TailwindCSS, Cytoscape.js |
| Graph Visualization | Cytoscape.js with dagre and cola layout algorithms |
| PDF Generation | ReportLab with `rl_config.invariant = 1` (deterministic output) |
| Authentication | JWT HS256 tokens |
| AI Integration | Groq API (primary), Gemini API (secondary), Rule-Based Engine (fallback) |
| Blockchain APIs | Etherscan V2 (ETH), TronGrid (TRON), Blockstream (BTC) |
| State Management | Zustand (frontend) |

### Backend Module Map

```
backend/
├── adapters/         — Blockchain gateway clients & BIP-39 validator
├── api/              — 54 FastAPI route handlers (canonical v1 routers)
├── assessment/       — RiskAssessor & RecoveryEstimator engines
├── attribution/      — AttributionResolver & AdaptiveVASPScorer
├── audit/            — Immutable SHA-256 chained audit engine
├── config/           — AppConfig & feature flags
├── cross_chain/      — Bridge registry & cross-chain analyzer
├── db/               — SQLite schema manager & deduplication logic
├── fixtures/         — 10 demonstration benchmark scenarios & immutable baselines
├── ingestion/        — IntakeOrchestrator state machine
├── legal/            — PDF ReportGenerator, notice drafting, mixer directives
├── models/           — Pydantic schemas & domain types
├── storage/          — Raw evidence payload repository
├── tests/            — 129 unit & regression tests across 18 test files (100% passing)
└── typologies/       — MixerRegistry, MuleNetwork, PeelChain, PrivacyAsset
```

### Key Design Decisions
- **No default secret in production**: The server refuses to start if `APP_ENV=production` and the default insecure `SECRET_KEY` is present. Security is enforced at startup, not configuration documentation.
- **In-memory transfer cache**: Transfer results are cached per `(chain, address)` pair to avoid redundant API calls within a trace session.
- **Graceful degradation**: When a blockchain API times out, `data_completeness_pct` is reduced in the response and the source is labeled `SIMULATED`. The trace continues rather than failing.
- **Feature flags**: `TRACE_STOP_AT_MIXER`, `TRACE_CROSS_CHAIN`, and `TRACE_OFAC_SANCTIONS` can be toggled independently via environment variables.

### API Surface
The backend exposes REST and WebSocket endpoints across 9 routers: AI Copilot, PDF Report, Intake, Tracing & Intelligence, Case Management, Statutory Notices, Audit & Evidence, System/Resilience, and WebSocket streaming. Key endpoints verified in source:
- `POST /api/v1/trace` — Execute forward, backward, or bidirectional multi-hop trace
- `WS  /ws/trace/{case_id}` — Real-time trace event stream (`HOP_COMPLETE`, `MIXER_BOUNDARY`, `VASP_IDENTIFIED`, `TYPOLOGY_DETECTED`, `TRACE_COMPLETE`)
- `GET  /api/v1/system/cache-stats` — Inspect 5-tier TTL cache hits, misses, and sizes
- `GET  /api/v1/cases/{case_id}/linked-cases` — Query cross-case syndicate links via `wallet_index`
- `GET  /api/v1/alerts` — Review automated alert dispatch events
- `GET  /api/v1/analytics/dashboard` — LEA analytics KPIs (total cases, critical alerts, top 5 VASPs, avg trace time)
- `GET  /api/v1/vasps/geo` — Retrieve VASP geographic coordinates, ISO country, and FATF greylist status
- `POST /api/v1/intake/ncrp/complaint` — Ingest complaint (accepts `INVESTIGATOR` role)
Interactive Swagger documentation available at `http://localhost:8765/docs`.

### Test Coverage
129 backend unit and regression tests across 18 test files — all passing (100% green, 0 regressions). 10 immutable golden baseline snapshots in `backend/tests/fixtures/baselines/`. Frontend TypeScript compilation verified clean across all 18 static routes.


---

## 9. Legal & Compliance Foundation

### Section 91, Bharatiya Nagarik Suraksha Sanhita (BNSS, 2023)
Authorizes law enforcement to compel production of documents or things from any person or organization. In this context: formal production orders served to VASP Nodal Officers requiring KYC records and account freezing. The platform auto-populates these notices with the specific VASP name, nodal officer contact, all traced transaction hashes, the case reference number, and the statutory compliance deadline.

### Sections 63 & 65B, Bharatiya Sakshya Adhiniyam (BSA, 2023)
Governs admissibility of electronic records in Indian courts. Section 65B requires that computer-generated evidence be accompanied by a certificate confirming the computer was functioning properly and the output faithfully represents the data. The system's SHA-256 chained audit ledger, deterministic PDF reproducibility, and cryptographic evidence payload verification are designed specifically to satisfy this requirement.

### PMLA & FIU-IND Guidelines
Prevention of Money Laundering Act registration with the Financial Intelligence Unit - India is used as an evidentiary weighting factor in VASP attribution scoring. FIU-IND registered exchanges receive a confidence score bonus because they are subject to regulatory oversight and are obligated to respond to production orders.

---

## 10. Demonstration Scenarios

Six pre-configured benchmark scenarios demonstrate every major system capability:

| Scenario | Chain | What It Demonstrates |
|---|---|---|
| **CR-2026-MULE-IND-01** | TRON | 3-hop mule syndicate tracing to WazirX (Zanmai Labs). FIU-registered exchange attribution with Section 91 notice ready. Confidence 0.88 (VERIFIED). |
| **CR-2026-MIXER-BOUND-02** | ETH | Ransom payment routes into Tornado Cash 10 ETH pool. System halts, generates pre-mixer freeze target and mixer directive. Demonstrates honest boundary handling. |
| **CR-2026-BRIDGE-XCHAIN-03** | ETH | ETH USDT → TRON USDT cross-chain bridge routing → CoinDCX. Distinguishes PROVEN smart contract events from HEURISTIC correlation. |
| **CR-2026-BRIDGE-XCHAIN-04** | ETH | Stargate Bridge Router cross-chain liquidity event decoded from LayerZero event topics → Polygon recipient. |
| **CR-2026-OFAC-SDN-05** | ETH | Direct OFAC SDN list hit — Lazarus Group / Ronin Bridge exploiter (SDN ID 34991). +45 risk bump to CRITICAL. Mandatory freeze directive. |
| **CR-2026-MULE-FANIN-06** | ETH | 4-victim task scam funds consolidating into a single CoinDCX cluster. Multi-victim attribution with Section 91 priority. |

---

## 11. Known Constraints & Honest Disclosures

**Attribution accuracy is bounded by the VASP registry.** The system can only identify exchanges it knows about. An unlabeled wallet cluster resolves as `UNRESOLVED`, not as a false positive. The registry currently covers 15+ VASPs covering the majority of India-market relevant exchanges.

**Mixer tracing is not possible.** Tornado Cash and similar privacy protocols cryptographically break forward tracing. The system handles this by halting and providing pre-mixer intelligence rather than producing speculative downstream attribution.

**Live API rate limits apply.** The Etherscan, TronGrid, and Blockstream public APIs have rate limits. During high-volume sessions, some hops may fall back to simulated data. This is transparently labeled in every response.

**KYC unmasking requires VASP cooperation.** The system identifies which exchange holds the funds. Getting the suspect's identity from that exchange requires a legal notice and the exchange's compliance.

**The 24–48 hour recovery window is an operational reality, not a platform limitation.** Even with near-real-time attribution, recovery depends on the investigator acting on the intelligence, the supervisor approving the notice, and the exchange executing the freeze.

---

## 12. What Success Looks Like

**From the investigator's perspective:**
> A victim reports a wallet address. Within minutes I have a graph showing where the money went, which exchange is holding it, which wallets were used for layering, and a draft legal notice ready for my supervisor to approve.

**From the supervisor's perspective:**
> I receive a notice with the evidence already attached. I review it, approve it digitally, and it goes to the exchange's nodal officer. I have an audit trail proving exactly when I approved it and what evidence supported the decision.

**From the court's perspective:**
> The investigation report is a deterministic PDF whose SHA-256 hash can be independently reproduced from the raw evidence payload. The audit ledger proves no record was altered after the fact.

**From the victim's perspective:**
> The funds were traced to an exchange within the recovery window. A preservation order was served. There was a chance.

---

*This document was prepared from the TraceX Sahyog project codebase and associated internal specifications. No information was sourced from external references or web sources.*

*Platform: TraceX Sahyog v2.0 | Backend: FastAPI on port 8765 | Frontend: Next.js 14 on port 3000 | Tests: 51 passing*


---


# Part 2: Product Requirements Document (PRD: FR-001 - FR-016)
> **Original Source Document:** `CRYPTOTRACE_LEA_PRD (1).md`  
> **Lines Preserved:** 690  

---

# CryptoTrace LEA — Product Requirements Document (PRD)

**Project:** SIH 26183 — Real-Time Crypto Fraud Attribution System for Indian Law Enforcement  
**Product:** CryptoTrace LEA  
**Document Status:** 100% IMPLEMENTED & VERIFIED (129/129 Tests Passing, 10 Immutable Golden Baselines)  
**Execution Spec:** `LOGIC_IMPLEMENTATION_PLAN (1).md` & `L1-Logs.md`  
**Authority:** `CRYPTOTRACE_LEA_MASTER_GUIDE_v3.md`  

> [!NOTE]
> **Implementation Complete (October 2026):** All functional and non-functional requirements (including FR-016 recovery boundary gating, Section 91 BNSS notice generation, Mule Network typology, and 6-step VASP scoring) are fully implemented and verified via 129/129 passing backend tests.


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
- EVM addresses and token activity across Ethereum, Polygon, and BSC/BNB Chain;
- Bitcoin UTXO addresses and transactions;
- Tron/TRC-20 activity.

Confirmed live backbone: Ethereum via ETH_RPC_PRIMARY_URL (WebSocket and HTTP), Polygon via POLYGON_RPC_PRIMARY_URL (WebSocket and HTTP), BSC/BNB Chain via Chain ID 56 (Ankr public RPC, with EVM 0x address disambiguation vs Ethereum via tx receipt/RPC checks), Tron via TRON_RPC_PRIMARY_URL (HTTP polling) plus TRON_GRID_API_KEY for TRC-20 event indexing, Etherscan via ETHERSCAN_API_KEY for historical address lookups and label enrichment only (never the live event path), Bitcoin via Mempool.space without authentication, and pricing via CoinGecko without authentication. Solana remains planned for future extension.

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

### FR-005 — Bounded Tracing & Traversal Controls

Tracing shall support configurable:
- `direction`: `TraceDirection.FORWARD`, `TraceDirection.BACKWARD` (fan-in upstream funding sources up to 2 hops), or `TraceDirection.BIDIRECTIONAL`;
- maximum hops (forward depth limit);
- time window (with a 10% penalty per truncation and `earliest_transaction_date` exposed);
- minimum value;
- maximum outflows;
- maximum nodes;
- timeout (with graceful degradation to `PARTIAL_COMPLETE` and 15% deduct if len(hops)>=2);
- decentralized exchange interception via `DEX_REGISTRY`: tagging swap pools as `defi_swap`, emitting `DEFI_SWAP` edges, resetting asset quantity, and continuing BFS past the router.

The system shall prevent uncontrolled graph expansion and expose all applied limits and truncation flags.

### FR-006 — Typology Detection

The system shall detect, explain, and version findings for:
- **`PEEL_CHAIN`**: Real implementation verifying 0.5%–5% per-hop reduction across >=3 consecutive unique addresses (not a stub);
- **`CONSOLIDATION_FUNNEL`**: Detects when 2+ independent branches merge into an aggregation wallet before a VASP deposit, tracking `convergence_nodes`;
- **`MULE_NETWORK`**: Detects multi-victim mule fan-in patterns with real timestamp calculations (synthetic 600s fallback eliminated);
- **`RAPID_HOP`**: Evaluated against chain-specific block times: ETH 10,800s (3h), TRON 3,600s (1h), BTC 86,400s (24h), POLYGON 1,800s (30m), BSC 3,600s (1h);
- **`REPEAT_OFFENDER_WALLET`**: Cross-case syndicate wallet matching via SQLite `wallet_index`;
- **`MIXER_BOUNDARY`** & **`MIXER_BOUNDARY_CLUSTER_LEAD`**: Tornado Cash pool detection and pre-mixer targeting;
- **`DEFI_OBFUSCATION`**: Emitted upon encountering registered DEX routers;
- **`CROSS_CHAIN_BRIDGE`**: Distinguishes PROVEN smart contract logs from HEURISTIC correlations.

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

### FR-007 — Nearest-VASP Attribution & Multi-Candidate Scoring

The system resolves the **nearest VASP** receiving direct deposits by walking BFS hops in traversal order (not terminal address inference). It distinguishes:
- labelled;
- inferred;
- unresolved.

When funds hit a VASP deposit cluster, the branch terminates to eliminate internal exchange noise. When multiple cluster matches exist, `score_all_candidates()` returns a ranked list of candidate attributions sorted by confidence score descending.

The base attribution score uses the six evidence components and starting weights: label `0.35`, directness `0.25`, retained `0.15`, finality `0.10`, temporal `0.10`, corroboration `0.05`. Hop-decay penalties are capped at -0.20 (preventing excessive attenuation on deep traces), and candidates with scores 40–59 on deep paths are assigned to the `deep_trace_partial` confidence band.

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

### FR-009 — Risk Assessment & Compounding Model

Risk scoring shall be explainable, versioned, and separately stored from attribution confidence. The composite risk score incorporates:
- **Base Typology Risk**: Calculated from detected typology rules;
- **Fraud Amount Tiers**: >=$1.2M USD (+35), >=$120K USD (+25), >=$12K USD (+15), else 0;
- **Cross-Chain Layering**: 1 bridge (+10), 2+ bridges (+20), bridge + mixer (+30);
- **Offshore Unregistered VASP Penalty**: FIU status `UNREGISTERED` and country non-India (+15);
- **Cross-Rule Compounding**:
  - `MULE_NETWORK` + `RAPID_HOP` → +15 risk bonus;
  - `MULE_NETWORK` + `MIXER_BOUNDARY` → +10 risk bonus and forces risk level to `CRITICAL`;
  - `OFAC_SANCTION_HIT` + any other rule → forces immediate `CRITICAL` risk level and traversal halt;
- **Time Truncation**: 10% risk deduction per truncated window with `TIME_WINDOW_WARNING`;
- **Automated Dispatch**: Emits alerts via `AlertDispatcher` when `risk_category == CRITICAL` or `ofac_sanction_hit == True`.

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

Use `value_ratio=min(1,traced/fraud)`, `time_urgency=max(.05,1-hours_since_incident/72)`, and `path_clarity=1/max(1,hop_count)`. Incorporate fraud-type recovery difficulty modifiers:
- `TASK_BASED`: +5%
- `RANSOMWARE`: -10%
- `SEXTORTION`: -15%
- `DARKNET`: -30%
- `ORGANIZED_CRIME`: -10%
- `INVESTMENT_SCAM` / `PHISHING`: 0%

When incident elapsed time cannot be verified from complaint records or on-chain timestamps, the system returns an `insufficient_data` tier with no fabricated false urgency (no 2.5h hardcoded fallback). Persist all components, score, `action_window_hours=max(0,72-hours_since_incident)`, and RED/AMBER/GREEN tiers with explicit boundaries: RED `<0.20`, AMBER `>=0.20 and <=0.50`, GREEN `>0.50`. Display the primary label with component tooltip, source, disclaimer, and supervisor sorting by ascending action window.

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

### NFR-008 — Deployment & Storage Selection

- **SQLite System of Record**: SQLite (`sahyog.db` and `intelligence.db`) with `canonical_db` connection management is verified and adequate for single-investigator operations.
- **PostgreSQL Migration**: **SKIPPED**. (SQLite adequate for single-investigator demo; opt-in via REDIS_URL env var for Redis cache upgrade).
- **In-Memory / Redis Caching**: Multi-tier caching is implemented via in-process `TTLCache` with transparent byte-identical guarantees, with optional Redis upgrade via `REDIS_URL`.

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



---


# Part 3: Frontend UI/UX Specification & Screen Catalog
> **Original Source Document:** `Frontend Requirements.md`  
> **Lines Preserved:** 404  

---

# CryptoTrace LEA — Frontend UI/UX Requirements & Functional Specification

> **Workstation Specification for Indian Law Enforcement Agencies (LEAs)**  
> **Alignment:** Ministry of Home Affairs (MHA) / I4C CIS Division (Problem Statement SIH 26183)  
> **Target Framework:** Next.js 14 (App Router) + React 18 + TailwindCSS + Lucide Icons + Cytoscape.js  
> **Backend Synchronization:** FastAPI Canonical v1 APIs (`http://localhost:8765/api/v1/...`)  
> **Security & RBAC:** Role-Based Access Control (Investigator, Supervisor, Administrator)  
> **Implementation Status:** 18/18 Next.js Routes Compiled Cleanly | 129/129 Pytest Tests Passing | WebSocket Real-Time Stream Enabled (`/ws/trace/{case_id}`)


---

## 1. Architectural UI Overview & Design System

The CryptoTrace LEA frontend workstation is structured as a mission-critical, low-latency intelligence console tailored for cyber police officers, forensic investigators, and supervisory leadership.

### Color Palette & Visual Tokens
- **Background**: Dark Mode (`#0b1120`, `#0f172a`, `#020617`) with glassmorphism and subtle border illumination (`#1e293b`, `#334155`).
- **Primary / Forensic Blue**: `#2563eb`, `#3b82f6` (System controls, navigations, verified hops).
- **Attribution / Success Emerald**: `#10b981`, `#059669` (FIU-IND registered VASPs, verified nearest VASP deposit hot wallets).
- **Privacy Mixer / Critical Hazard Red**: `#ef4444`, `#dc2626` (Mixer boundaries, OFAC SDN hits, statutory quarantine).
- **Cross-Chain Bridge Cyan**: `#06b6d4`, `#0891b2` (PROVEN smart contract bridge corridors, LayerZero/Stargate routers).
- **DeFi Swap Teal**: `#14b8a6`, `#0d9488` (DEX router pools, Uniswap, PancakeSwap, Curve swaps).
- **Time Urgency Amber**: `#f59e0b`, `#d97706` (24-48h recovery dissipation windows, intermediate mule accounts).
- **Typography**: Inter / Outfit for UI controls; JetBrains Mono / SF Mono for transaction hashes, addresses, and cryptographic hashes.

---

## 2. Comprehensive Screen-by-Screen UI Specification

---

### Screen 1: Investigations & Forensic Tracing Studio (`/investigations`)

The primary workspace where investigating officers analyze on-chain fund flows, visualize transaction graphs, and execute attribution.

#### A. Header Controls & Mode Switcher
1. **Interactive Mode Switcher Toggle**:
   - **Label**: `🟢 LIVE ON-CHAIN MODE` vs `🟡 BENCHMARK DEMO MODE`
   - **Backend Binding**: Passed as `mode="LIVE"` or `mode="DEMO"` to `POST /api/v1/trace`.
   - **Behavior**:
     - `LIVE`: Interactively crawls live Etherscan V2, TronGrid, and Blockstream APIs in real-time.
     - `DEMO`: Loads deterministic benchmark fixtures without incurring external RPC rate limits.
2. **Target Input Bar**:
   - **Input**: Suspect Address / Transaction Hash (`0x...` or `T...`).
   - **Chain Dropdown**: `ETH` (Ethereum ERC-20), `TRON` (TRC-20), `BTC` (Bitcoin), `POLYGON`, `BSC` (BNB Chain ID 56).
   - **Direction Dropdown**: `FORWARD` (Default), `BACKWARD` (Upstream fan-in up to 2 hops), `BIDIRECTIONAL`.
   - **Max Hops Slider**: Integer range `1` to `6` (Default `4`).
   - **Button**: `Start Multi-Hop Trace` (Icon: `Play`, Variant: Primary Blue).
     - **API**: `POST /api/v1/trace`
     - **Payload**: `{"address": "...", "chain": "...", "max_hops": 4, "direction": "FORWARD", "mode": "LIVE"|"DEMO"}`
     - **Loading State**: Rotating radar icon with "Executing Bounded Ledger Search...".
     - **Success State**: Renders graph, pops TimeToActionBanner, CaseSummaryCard, and Hop Table.

#### B. Dedicated Live On-Chain Data & Fund Flow Inspector
A dedicated panel allowing officers to inspect raw on-chain state before tracing:
1. **1-Click Test Persona Buttons**:
   - `Vitalik Buterin (ETH)` (`0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`)
   - `Binance Hot Wallet (ETH)` (`0x28c6c06298d514db089934071355e5743bf21d60`)
   - `Official Tether USDT (TRON)` (`TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t`)
   - `Satoshi Nakamoto Genesis (BTC)` (`1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`)
   - **Action**: Auto-fills the search input and automatically fetches live explorer balance and transactions.
2. **On-Chain Balance & Spot Valuation Card**:
   - Displays live crypto balance (e.g., `6.7179 ETH`).
   - Displays live **Indian Rupee (₹ INR)** and USD conversion via CoinGecko spot rates and 83.5 INR/USD rate.
3. **Confirmed Transactions Table**:
   - Displays the last 10 confirmed on-chain transactions.
   - Columns: Tx Hash, Block Age, Counterparty, Value, Explorer Link.
   - Button: `Load Into Graph` (Icon: `Network`, Variant: Outline Cyan) — Appends transactions into Cytoscape graph canvas.

#### C. Forensic Intelligence Cards (Win Plan Components)
1. **Time-to-Action Banner (`TimeToActionBanner.tsx`)**:
   - **Data**: `traceData.recovery_estimate`
   - **Display**: Action window hours remaining (e.g., `22 Hours Remaining`), urgent dissipation countdown, color-coded urgency badge (`URGENT`, `EXPIRING`, `MODERATE`).
   - **Ineligible State**: If criteria not met (e.g., < $120 value, mixer obstruction), displays explicit disclaimer: "Ineligible for recovery estimation per PRD FR-016".
2. **Data Completeness KPI Bar (`KpiBanner.tsx`)**:
   - **Data**: `traceData.data_completeness_pct`
   - **Color Coding**: Green (`>=85%`), Amber (`65%–84%`), Red (`<65%`).
   - **Details**: Exposes `earliest_transaction_date` and component breakdowns (RPC timeouts, time window truncation flags).
3. **Trace Boundary Card (`TraceBoundaryCard.tsx`)**:
   - **Data**: `traceData.boundary_events`, `traceData.partial_recommendation`
   - **Display**: Rendered when `termination_reason === "MIXER_BOUNDARY_HIT"`.
   - **Visuals**: Red hazard badge, Pre-Mixer Target Address, Recommended Off-Chain Actions (subpoena RPC logs, issue freeze order on pre-mixer wallet).
   - **Button**: `Copy Pre-Mixer Address` (Icon: `Copy`).
4. **Case Summary Card (`CaseSummaryCard.tsx`)**:
   - **Data**: `traceData.attribution`
   - **Display**: Nearest VASP Deposit Chip (e.g., `WazirX (Zanmai Labs Pvt Ltd)` or `CoinDCX`), Confidence Band (`HIGH` / `MEDIUM` / `LOW`), FIU-IND Registration Status (`REGISTERED` / `UNREGISTERED`). Dual currency display shows `traced_value_inr` and `traced_value_usd`.
   - **Scoring Accordion**: Expandable 6-step breakdown (Base Confidence, FIU Bonus, Exact Match, Hop Penalty capped at -0.20, Freshness, Data Completeness). Multiple ranked candidate list via `score_all_candidates()`.
5. **OFAC Sanctions Nexus Alert Banner**:
   - **Data**: Rendered when `traceData.ofac_sanction_hit === true`.
   - **Visuals**: Flashing red warning banner citing official OFAC Specially Designated Nationals (SDN) registry.
   - **Text**: Identifies designated entity (e.g., "Lazarus Group - Ronin Bridge Exploiter, SDN ID 34991"). Traversal halts at sanctioned address with risk level forced to `CRITICAL`.
   - **Directive**: "Mandatory Section 91 BNSS Immediate Asset Freeze Order in effect."
6. **AI Investigator Copilot Panel (`CopilotPanel.tsx`)**:
   - **Header**: "AI Investigator Copilot" with **Provider Badge** (`Groq`, `Gemini`, `Rule-Based Fallback`).
   - **Guardrail Pill**: "BNSS §91 Grounded — Zero Hallucinations Tolerated".
   - **Dossier Context**: Enriched with crime category, fraud type, data completeness %, partial trace warning, and sanctions nexus.
   - **Strategic Directive Box**: Displays prioritized next steps generated by AI.
   - **Chat Thread**: Officer query interface with English & Hindi support.
   - **Form**: Query input + Button: `Ask Copilot` (Icon: `Send`, API: `POST /api/v1/copilot/{case_id}/chat`).

#### D. Interactive Graph Canvas (`CytoscapeGraph.tsx`)
- **Canvas Controls**:
  - `Zoom In` / `Zoom Out` / `Fit View` / `Reset Layout`.
  - `Export Graph PNG` (Downloads high-res snapshot of canvas).
  - `Export Graph JSON` (Exports Cytoscape node/edge elements for forensic evidence storage).
- **Node Color Standards**:
  - Suspect Seed Node: Amber / Red with target halo.
  - Intermediary Mule Node: Blue / Violet.
  - Nearest Exchange / VASP Deposit Node: Emerald Green with verified checkmark.
  - DeFi / DEX Swap Pool Node: Teal with swap badge (`defi_swap`).
  - Privacy Mixer Node: Crimson Red with octagon stop icon.
  - Bridge Contract Node: Cyan with dual-chain badge.
  - Funding Source Node: Indigo square (fan-in upstream source).
- **Edge Standards**:
  - Standard Transfer: Solid slate line with transaction amount label (`amount_usd` / `amount_inr`).
  - PROVEN Bridge Link: Solid cyan line (`link_type: "PROVEN"`).
  - Heuristic Correlation: Dashed purple line (`link_type: "HEURISTIC_CORRELATION"`).
  - DEFI_SWAP Edge: Dotted teal line with asset reset indicator (`DEFI_SWAP`).
  - FAN_IN Edge: Dashed blue line connecting upstream funding sources (`FAN_IN`).

#### E. Primary Investigative Action Toolbar
- **Button 1**: `Download Court-Admissible PDF Dossier` (Icon: `Download`, Variant: Emerald Success).
  - **API**: `GET /api/v1/cases/{case_id}/report.pdf`
  - **Behavior**: Downloads deterministic, Section 65B certified PDF report.
- **Button 2**: `Draft Section 91 BNSS Notice` (Icon: `FileText`, Variant: Primary Blue).
  - **Behavior**: Navigates to `/legal-notices` pre-filled with the attributed VASP and transaction hashes.
- **Button 3**: `Verify Chained Evidence Hash` (Icon: `ShieldCheck`, Variant: Outline).
  - **Behavior**: Computes SHA-256 hash of trace payload and verifies against `/api/v1/evidence/verify/{hash}`.

---

### Screen 2: Guided Evaluation Console (`/demo`)

A specialized, one-click evaluation console for SIH judges and senior leadership that proves each core challenge in an automated 7-step sequence.

#### Layout & Navigation
- **Top Evaluation Banner**: Cites SIH Problem Statement 26183, active golden baseline, and step counter.
- **Step Progress Tracker Bar**: 7 interactive step cards showing status (`Active`, `Completed`, `Upcoming`).
- **Left Column (4 Cols)**:
  - Step Title & Evaluation Scenario.
  - **Forensic Value Box**: Explains what this proves to the scorecard.
  - **Scorecard Area Badge**: Maps directly to SIH criteria (e.g., `Evaluation #2: Mule Network Detection`).
  - **Button**: `Run Step X Simulation` (Icon: `Play`, executes mock gateway or trace).
- **Right Column (8 Cols)**: Live interactive component preview corresponding to the active step:
  - **Step 1**: NCRP Sandbox Ingestion Card + 2,048-word BIP-39 sanitizer log.
  - **Step 2**: Mule Network Trace + CaseSummaryCard with 6-step scoring accordion.
  - **Step 3**: Cross-Chain Bridge Card with decoded Stargate router event.
  - **Step 4**: Privacy Mixer Card with honest boundary stop and pre-mixer freeze targets.
  - **Step 5**: Time-to-Action Countdown Banner + AI Copilot recommendation panel.
  - **Step 6**: Deterministic PDF Report Download Card + Section 91 notice approval preview.
  - **Step 7**: Cryptographic Audit Chain verification showing 100% untampered integrity.

---

### Screen 3: NCRP & SAHYOG Ingestion Gateway (`/intake`)

The official government complaint ingestion and threat bulletin synchronization console.

#### A. Gateway Status Banner
- **Status Badge**: `🟢 MHA SANDBOX ACTIVE (Zero Credential Leak Defense)`
- **Metrics Bar**: Total Complaints Received, Successfully Sanitized, Quarantined Violations, Auto-Traced Cases.

#### B. Simulation & Dispatch Controls
1. **Button**: `Dispatch Mock NCRP Complaint` (Icon: `Play`, Variant: Blue).
   - **API**: `POST /api/v1/intake/ncrp/complaint`
   - **Payload**: Generates mock citizen cyber fraud complaint (Acknowledgement #, Complainant Name, TRON/ETH wallet, Reported Loss INR).
   - **Behavior**: Appends to active pipeline table and logs to chained audit engine.
2. **Button**: `Test Credential Leak Defense (Quarantine Test)` (Icon: `AlertTriangle`, Variant: Danger Red).
   - **Payload**: Injects simulated victim complaint containing an authentic 12-word BIP-39 mnemonic seed phrase and private key.
   - **Expected Result**: System immediately rejects ingestion, raises `422 Unprocessable Entity`, and records incident in Credential Leak Quarantine Audit Log.
3. **Button**: `Dispatch SAHYOG Threat Bulletin` (Icon: `FileText`, Variant: Outline).
   - **API**: `POST /api/v1/intake/sahyog/bulletin`
   - **Payload**: Multi-wallet syndicate bulletin from state cyber cell.

#### C. Active Ingestion Pipeline Table
- **Columns**: Acknowledgement No, Source Portal, Complainant, Chain & Wallet, Defrauded Value (INR), Workflow State, Action.
- **Workflow State Badges**:
  - `RECEIVED` (Blue)
  - `VALIDATED_SANITIZED` (Emerald)
  - `TRACING` (Yellow animate-spin)
  - `ATTRIBUTED` (Cyan)
  - `NOTICE_DRAFTED` (Purple)
- **Row Action Button**: `Run Trace Now` (Icon: `ArrowRight`) — Triggers `POST /api/v1/intake/{case_id}/trace` and redirects to `/investigations`.

#### D. Credential Leak Quarantine Log
- Displays quarantined complaints where victim seed phrases or private keys were detected and sanitized.
- Columns: Event Timestamp, Incident Ref, Quarantined Secret Type (`BIP-39 MNEMONIC PHRASE`, `PRIVATE_KEY_HEX`), Action Taken (`PRE-INGESTION REJECTION & ISOLATION`).

---

### Screen 4: Case Docket & Management (`/cases`)

The legal docket organizing all authorized investigations.

#### A. Toolbar & Registration
1. **Button**: `+ Register New Case` (Icon: `Plus`, Variant: Primary Blue).
   - **Modal Fields**:
     - Case Reference ID (Auto-generated or custom e.g., `CR-2026-MUMBAI-042`).
     - FIR Number / Police Station Diary Ref.
     - Suspect Cryptocurrency Wallet Address.
     - Blockchain Network (`ETH`, `TRON`, `BTC`, `POLYGON`).
     - Defrauded Asset & Amount (e.g., `50,000 USDT`).
     - Complainant Full Name & Contact.
     - Source Category (`NCRP_PORTAL`, `SAHYOG_BULLETIN`, `DIRECT_LEA_FIR`).
     - Brief Narrative Summary.
   - **API**: `POST /api/v1/cases`
   - **Audit Action**: Automatically records `case:create` in chained audit ledger.
2. **Filter & Search Controls**:
   - Search by Wallet, Case ID, Complainant, or FIR number.
   - Filter dropdowns: Status (`OPEN`, `INVESTIGATING`, `NOTICE_SERVED`, `CLOSED`), Network, Date Range.

#### B. Case Docket Table
- **Columns**: Case ID, FIR Ref, Suspect Address, Blockchain, Defrauded Value, Assigned Officer, Status, Actions.
- **Row Action Buttons**:
  - `Investigate` (Icon: `Search`) — Opens trace in `/investigations`.
  - `PDF Dossier` (Icon: `Download`) — Direct call to `GET /api/v1/cases/{case_id}/report.pdf`.
  - `Issue Notice` (Icon: `FileText`) — Opens Section 91 drafting drawer.

---

### Screen 5: Statutory Legal Notices & Section 91 Governance (`/legal-notices`)

Enforces the statutory **Two-Officer Maker/Checker Rule** under Section 91 BNSS 2023 / Section 91 CrPC.

#### A. Requisition Status Tabs
- `All Notices`
- `Drafts (Investigator Worklist)`
- `Pending Supervisory Review`
- `Approved & Authorized (Cryptographically Signed)`
- `Served to Exchange`

#### B. Requisition Management Table
- **Columns**: Requisition Ref, Case ID, Target VASP / Entity, Nodal Officer Email, Statutory Act (`BNSS §91`), Status, Action.
- **Status Badges**:
  - `DRAFT`: Gray outline.
  - `PENDING_SUPERVISOR_APPROVAL`: Yellow pulse.
  - `AUTHORIZED_APPROVED`: Emerald green with badge.
  - `REJECTED`: Red outline.

#### C. Notice Drafting & Approval Drawer
When opening a requisition:
1. **Requisition Header**: Full case docket details, victim reference, suspect address, and identified VASP cluster.
2. **Formal Legal Notice Document Textarea**:
   - Contains formal legal requisition text formatted for judicial compliance:
     - Notice under Section 91 BNSS, 2023.
     - Requisition for immediate asset freezing, transaction records, IP/session connection logs, and KYC registration documents.
     - **Section 5 Mixer Directive** (if privacy pool was traversed, orders preservation of pre-mixer deposits).
     - **Cryptographic Evidence Hash Table**.
     - **Statutory Section 65B Indian Evidence Act Certificate**.
3. **Role-Gated Actions**:
   - **Investigator Persona (`investigator1`)**:
     - Button: `Save Draft Edits` (API: `POST /api/v1/notices/draft`).
     - Button: `Submit for Supervisory Review` (API: `POST /api/v1/notices/{draft_id}/submit`).
     - *Disabled*: Cannot approve or sign their own notice.
   - **Supervisor Persona (`supervisor1`)**:
     - Button: `Approve & Cryptographically Authorize Notice` (Icon: `CheckCircle`, Variant: Emerald Success).
       - API: `POST /api/v1/notices/{draft_id}/approve`
       - Behavior: Appends supervisor digital signature block and logs `notice:approve` in audit chain.
     - Button: `Reject with Remarks` (Icon: `XCircle`, Variant: Danger Red).
       - API: `POST /api/v1/notices/{draft_id}/reject`
       - Input Modal: Requires supervisor to enter mandatory written rejection remarks.
4. **Export Buttons**:
   - Button: `Copy Requisition Text` (Icon: `Copy`).
   - Button: `Download Signed Notice Letter (PDF)` (Icon: `Download`).

---

### Screen 6: Heuristic Recovery & Urgency Calculator (`/recovery`)

Translates complex multi-hop graph topology into actionable operational urgency metrics.

#### A. Visual Factor Distribution Chart (Phase 7.2 Win Plan)
A dedicated horizontal progress bar distribution card breaking down the 4 operational pillars:
1. **Exchange Cooperation**: `35 pts max` (FIU-IND registered domestic exchange = +35; Global registered = +20; Offshore = +5).
2. **Time Urgency Decay**: `30 pts max` (< 24h = +30; 24-48h = +15; > 48h = +5).
3. **Path Simplicity**: `25 pts max` (1 hop = +25; 2-3 hops = +15; 4+ hops = +5).
4. **Attribution Confidence**: `10 pts max` (HIGH = +10; MEDIUM = +5; LOW = 0).

#### B. Interactive Simulation Panel
Enables officers to model the recovery window based on operational parameters:
- **Slider**: Defrauded Value (INR / USD).
- **Slider**: Elapsed Hours since theft (`0.5h` to `72h`).
- **Slider**: Discovered Hops (`1` to `5`).
- **Toggle**: Destination VASP Registered with FIU-IND (`Yes` / `No`).
- **Toggle**: Mixer Interaction Incurred (`Yes` / `No`).
- **Dropdown**: Attribution Confidence (`HIGH`, `MEDIUM`, `LOW`).

#### C. Operational Boundary Disclosures
- Explicitly communicates PRD FR-016 boundary gating conditions:
  - Minimum actionable value: ₹10,000 INR ($120 USD).
  - Minimum data completeness: 70%.
  - Zero-hop traces and LOW/LEAD attribution are ineligible.
  - Mixer boundaries prevent recovery estimation.
- **Statutory Law Enforcement Disclaimer**:
  - Highlights: "Heuristic Recovery Estimate is an operational triage score to assist officers in meeting the 24-48 hour window for Section 91 notices. It is NOT a mathematical probability or restitution warranty."

---

### Screen 7: Cryptographic Audit Ledger & Evidence Repository (`/audit` & `/evidence`)

Provides mathematical proof of zero post-facto tampering for court presentation under Section 63/65B BSA 2023.

#### A. Audit Chain Verification Widget
- **Verification Trigger Button**: `Verify Entire Audit Trail` (Icon: `ShieldCheck`, Variant: Emerald).
  - **API**: `GET /api/v1/audit/verify-chain`
  - **Visual Status**:
    - `🟢 100% VALID UNTAMPERED AUDIT CHAIN`
    - Displays total cryptographically verified event blocks (e.g., `328 Event Blocks`).
    - Displays Genesis Block Hash & Chained Head Hash.
- **Tamper Simulation Notice**:
  - Demonstrates that modifying any single byte in SQLite invalidates the entire chained SHA-256 Merkle sequence.

#### B. Real-Time Audit Event Stream Table
- **Columns**: Block Index, Timestamp (UTC), User ID, Assigned Role, Action (`case:create`, `trace:execute`, `notice:approve`, `report:generate_pdf`), Resource ID, SHA-256 Block Hash.
- **Row Expand**: Shows exact JSON details payload and previous block hash link.

#### C. Digital Evidence Repository (`/evidence`)
- **Evidence Manifest Table**:
  - Lists forensic evidence artifacts attached to cases (raw ledger payloads, Cytoscape network snapshots, generated PDF dossiers).
  - Button: `Verify Payload Integrity` (API: `POST /api/v1/evidence/verify/{payload_hash}`).
  - Badge: `FORENSIC_INTEGRITY_CONFIRMED`.

---

### Screen 8: Upstream Gateway Health & Diagnostics (`/provider-status`)

Monitors the real-time operational status of all external blockchain explorers and intelligence APIs.

#### A. Gateway Health Cards Grid
Cards displaying real-time ping latency, connection state, and upstream quota metrics for:
1. **Ethereum Primary Gateway** (`Etherscan V2 API` / RPC).
2. **TRON Primary Gateway** (`TronGrid API` / Nile).
3. **Bitcoin Primary Gateway** (`Blockstream Esplora API` / Mempool.space).
4. **Currency Spot Valuation** (`CoinGecko Crypto & INR Engine`).
5. **Threat Screening** (`US OFAC Sanctions List Service`).
6. **Graph Database** (`Neo4j Aura Cloud Engine`).
7. **AI Reasoning** (`Groq LLaMA-3 / Gemini Flash Engine`).

#### B. Diagnostic Controls
- **Button**: `Run System-Wide Diagnostic Ping` (Icon: `Activity`, Variant: Primary Blue).
  - **API**: `GET /api/test/apis`
  - **Behavior**: Executes simultaneous asynchronous pings and updates latency bars (ms) across all cards.
- **Card-Level Button**: `Test Gateway Ping` (Calls `GET /api/test/api/{api_id}`).

---

### Screen 9: Global Workspace Layout & Navigation

The persistent framing surrounding all workspace screens.

#### A. Top Bar
1. **Live Cryptocurrency Spot Rates Ticker**:
   - Live prices fetched from `/api/prices` in INR:
     - `BTC: ₹78,42,150`
     - `ETH: ₹2,84,320`
     - `USDT: ₹88.45`
     - `TRX: ₹18.20`
2. **Current Case Indicator**: Shows active Case ID (e.g., `CR-2026-MULE-IND-01`) with quick-switch dropdown.
3. **Persona Switcher Dropdown (Evaluation Helper)**:
   - Allows instant role-switching between:
     - `investigator1` (Investigator - Cyber Crime PS Mumbai)
     - `supervisor1` (Supervisor - CID HQ Maharashtra)
     - `admin1` (Admin - MHA/I4C CIS Division)
   - Automatically refreshes JWT access token without requiring re-login.

#### B. Sidebar Navigation Links
- `Dashboard` (`/dashboard` - Icon: `LayoutDashboard`)
- `Guided Demo` (`/demo` - Icon: `PlayCircle`, Badge: `SIH 26183`)
- `NCRP Intake` (`/intake` - Icon: `ShieldAlert`, Badge: `Sandbox`)
- `Investigations` (`/investigations` - Icon: `Search`)
- `Case Docket` (`/cases` - Icon: `Briefcase`)
- `Legal Notices` (`/legal-notices` - Icon: `FileText`, Badge: `BNSS §91`)
- `Recovery Urgency` (`/recovery` - Icon: `TrendingUp`)
- `Evidence Manifest` (`/evidence` - Icon: `Database`)
- `Audit Ledger` (`/audit` - Icon: `ShieldCheck`)
- `Gateway Status` (`/provider-status` - Icon: `Activity`)

---

## 3. Comprehensive Button-to-API Mapping Matrix

| Button Name / Element | Screen Location | Target API Endpoint | HTTP Method | Request Body / Params | Required RBAC Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Start Multi-Hop Trace** | `/investigations` | `/api/v1/trace` | `POST` | `{"address": "...", "chain": "...", "max_hops": N, "mode": "LIVE"\|"DEMO"}` | Any Authenticated |
| **Inspect Cache Stats** | `/admin`, `/system` | `/api/v1/system/cache-stats` | `GET` | N/A | Any Authenticated |
| **Query Linked Cases** | `/investigations`, `/cases` | `/api/v1/cases/{id}/linked-cases` | `GET` | N/A | Any Authenticated |
| **List Automated Alerts** | `/alerts`, `/dashboard` | `/api/v1/alerts` | `GET` | N/A | Any Authenticated |
| **LEA Analytics Dashboard** | `/dashboard`, `/analytics` | `/api/v1/analytics/dashboard` | `GET` | N/A | Any Authenticated |
| **Query VASP Geo Locations**| `/map`, `/vasps` | `/api/v1/vasps/geo` | `GET` | N/A | Any Authenticated |
| **Live WebSocket Stream** | `/investigations` | `/ws/trace/{case_id}` | `WS` | Handshake | Any Authenticated |
| **Load Into Graph** | `/investigations` (Inspector) | `/api/live/{addr}` | `GET` | `?chain=ETH` | Any Authenticated |
| **Download PDF Dossier** | `/investigations`, `/cases`, `/demo` | `/api/v1/cases/{id}/report.pdf` | `GET` | N/A (Binary Stream) | Investigator, Supervisor |
| **Ask Copilot** | `/investigations` (Copilot) | `/api/v1/copilot/{id}/chat` | `POST` | `{"query": "...", "trace_data": {...}}` | Any Authenticated |
| **Refresh Copilot Actions** | `/investigations` (Copilot) | `/api/v1/copilot/{id}/recommend` | `POST` | N/A | Any Authenticated |
| **Dispatch Mock Complaint**| `/intake`, `/demo` | `/api/v1/intake/ncrp/complaint` | `POST` | `{"acknowledgement_no": "...", "chain": "...", ...}` | Any Authenticated |
| **Test Credential Leak** | `/intake` | `/api/v1/intake/ncrp/complaint` | `POST` | `{"description": "seed phrase words...", ...}` | Any Authenticated |
| **Register New Case** | `/cases` | `/api/v1/cases` | `POST` | `{"case_id": "...", "wallet": "...", "chain": "...", ...}` | Investigator, Admin |
| **Submit Notice for Review**| `/legal-notices` | `/api/v1/notices/{id}/submit` | `POST` | N/A | Investigator |
| **Approve & Authorize Notice**| `/legal-notices` | `/api/v1/notices/{id}/approve` | `POST` | N/A | **Supervisor Only** |
| **Reject Notice** | `/legal-notices` | `/api/v1/notices/{id}/reject` | `POST` | `{"remarks": "..."}` | **Supervisor Only** |
| **Verify Audit Chain** | `/audit`, `/demo` | `/api/v1/audit/verify-chain` | `GET` | N/A | Any Authenticated |
| **Verify Evidence Payload** | `/evidence` | `/api/v1/evidence/verify/{hash}`| `POST`| N/A | Any Authenticated |
| **Diagnostic Ping** | `/provider-status` | `/api/test/apis` | `GET` | N/A | Any Authenticated |
| **User Login** | `/login` | `/api/v1/auth/login` | `POST` | `{"username": "...", "password": "..."}` | Public |

---

## 4. UI Error Handling, Loading & Fallback Standards

1. **Anti-Hallucination & Provider Fallback**:
   - If Groq or Gemini API fails, AI Copilot gracefully falls back to deterministic rule-based heuristic generation.
   - Provider badge automatically updates to `Rule-Based Fallback` so officers and judges see transparent, uncompromised evidence.
2. **Provider Timeout & Degradation**:
   - If a live explorer times out during a crawl, the tracer never crashes.
   - It captures partial results, sets `termination_reason = "TIMEOUT"`, decrements `data_completeness_pct` (e.g., to 77.5%), and shows an amber notification.
3. **Zero Credential Leaks**:
   - Intake forms client-side and server-side validate against `bip39_english.txt`.
   - Seed phrases are rejected prior to state commits, shielding victims from accidental key exposure.
4. **Idempotent PDF Reports**:
   - PDF reports are generated with fixed metadata timestamps (`reportlab.rl_config.invariant = 1`) ensuring bit-for-bit identical hashes across multiple downloads.


---


# Part 4: System Limitations, Uncertainty & Boundary Conditions
> **Original Source Document:** `docs/LIMITATIONS.md`  
> **Lines Preserved:** 35  

---

# CryptoTrace LEA — Limitations & Boundary Conditions

## 1. Probabilistic vs Cryptographic Boundaries
- **Attribution vs Ownership**: CryptoTrace LEA identifies candidate Virtual Asset Service Providers (VASPs) through transaction clustering, deposit sweep patterns, and proximity heuristics. **Attribution does not constitute legal proof of beneficial ownership**; ownership can only be established through lawful KYC disclosure obtained via Section 91 BNSS 2023 directives served to the VASP nodal officer.
- **Unhosted Mule Wallets**: While the `MULE_NETWORK` rule identifies single-in/single-out rapid forwarding rings characteristic of organized mule syndicates, **confidence is strictly capped at MEDIUM**. Intermediate wallets are unhosted (self-custodial), and their controllers cannot be conclusively identified without off-chain banking or telecommunication evidence.

---

## 2. Privacy Mixers & Anonymity Enhancers
- **Mixer Boundary Heuristic**: Transits through Tornado Cash, Wasabi, or other coinjoin/mixer pools break deterministic transaction continuity. CryptoTrace LEA flags potential exits using temporal windows ($+14,400\text{s}$) and pool payout ratios ($0.90 - 0.995$), but labels these edges strictly as:
  $$\text{Possible Exit — Heuristic Only (Confidence: 0.25 / LEAD)}$$
- The system **never** claims confirmed attribution across a privacy pool.

---

## 3. Cross-Chain Bridges
- **Proven vs Heuristic Correlation**: Only cross-chain bridge events containing cryptographic validator attestations, mint/burn proofs, or verified contract event logs are classified as `PROVEN`.
- Time/value correlation across different blockchains without cryptographic proof is explicitly tagged as `HEURISTIC_CORRELATION` and carries mandatory uncertainty disclaimers.

---

## 4. Heuristic Recovery Estimate & PRD FR-016 Boundary Gating
- The recovery score (0-100) is an **operational prioritization metric** for law enforcement dispatch. It does **not** represent a statistical probability of fund return, nor does it guarantee asset seizure. Actual recovery depends entirely on judicial orders issued under Section 106 BNSS 2023 or Section 5 PMLA 2002.
- **Mandatory Boundary Gating (PRD FR-016)**:
  - **Zero-Hop Rejection**: Trace depth == 0 $\implies$ `ESTIMATE_NOT_APPLICABLE` (untracked funds cannot be prioritized).
  - **Attribution Gating**: Attribution == `LEAD` or `NONE` $\implies$ `ESTIMATE_NOT_APPLICABLE` (cannot calculate freeze probability without an identifiable custodial counterparty).
  - **Low-Value Threshold**: Defrauded amount $< \$120$ $\implies$ `LOW_VALUE_UNECONOMIC` (below actionable statutory recovery threshold).

---

## 5. Algorithmic Reproducibility & Baseline Invariants
- **Deterministic Branching**: In evaluation mode, DEMO cases follow realistic branching paths (`MIXER_HALT` for Tornado Cash pools and `SANCTION_HALT` for Lazarus OFAC addresses) rather than homogeneous paths.
- **Snapshot Integrity**: 10 immutable baseline snapshots in `backend/tests/fixtures/baselines/` enforce that all 9 canonical output keys remain byte-for-byte reproducible across releases.
- **Test Gate**: Verified via 129/129 passing pytest tests with 0 regressions.



---
