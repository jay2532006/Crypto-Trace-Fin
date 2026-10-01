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

1. **Traces the money** — follows every transaction hop across up to 6 blockchain hops
2. **Identifies the exchange** — finds which registered crypto exchange (VASP) is the terminal destination
3. **Flags every suspicious wallet along the way** — mule accounts, layering wallets, mixer entry points
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

**Step 2 — Bounded Multi-Hop Tracing** (`POST /api/v1/trace`):
The `bounded_tracer` in `backend/tracing/trace_engine.py` performs a breadth-first traversal of on-chain transactions. It calls live blockchain APIs (Etherscan V2 for Ethereum/ERC-20, TronGrid for TRC-20 USDT, Blockstream for Bitcoin). Each hop is evaluated against `TraceConstraints` — a configurable depth limit, a mixer boundary halt flag, and a cross-chain bridge detection flag.

**Step 3 — VASP Attribution** (`backend/attribution/attribution_resolver.py`):
The `AttributionResolver` evaluates each terminal address against the curated VASP registry. It computes a confidence score using the `AdaptiveVASPScorer` — a 6-factor weighted formula: base confidence, FIU-IND registration bonus, exact address match, hop penalty, data freshness, and data completeness.

**Step 4 — Typology Detection** (`backend/typologies/`):
The `typology_engine.py` classifies the trace into known fraud patterns: `MULE_NETWORK`, `MIXER_BOUNDARY`, `RAPID_HOP`, `CROSS_CHAIN_BRIDGE`, `OFAC_SANCTION_HIT`, `PEEL_CHAIN`. The `mixer_registry.py` holds curated Tornado Cash pool addresses (0.1, 1, 10, 100 ETH pools on Ethereum and Arbitrum).

**Step 5 — Cross-Chain Bridge Detection** (`backend/cross_chain/`):
The `cross_chain_analyzer.py` checks each hop against `bridge_registry.py`, which holds router contracts and event topics for Stargate, Across V2, and Wormhole. A `PROVEN` link is emitted when a smart contract event is decoded directly. A `HEURISTIC_CORRELATION` link is emitted when temporal correlation alone supports the bridge conclusion.

**Step 6 — OFAC Sanctions Screening**:
Every traversed address is checked against the US Treasury OFAC Specially Designated Nationals list. An OFAC hit applies a +45 risk score bump, triggering `CRITICAL` risk level and a mandatory red alert banner.

**Step 7 — Evidence & Audit** (`backend/audit/`):
Every trace action is appended to a SHA-256 chained audit ledger. Each event hash incorporates the hash of the preceding event, making any post-facto tampering cryptographically detectable.

**Step 8 — Report Generation** (`backend/legal/`):
The `ReportGenerator` uses ReportLab with `rl_config.invariant = 1` for deterministic PDF output — the same inputs always produce a bit-for-bit identical PDF with the same SHA-256 hash. This reproducibility is required for Section 65B evidence admissibility.

---

## 5. Key Capabilities

### 5.1 Multi-Chain Tracing
The system traces transactions across Ethereum (ERC-20 tokens including USDT, USDC), TRON (TRC-20 USDT — heavily used in India-linked scam flows), Bitcoin, and Polygon. Live blockchain data is fetched from public APIs. When APIs are unavailable, the system falls back to algorithmically generated simulation and clearly labels the output as `SIMULATED` — investigators always know which data is real.

### 5.2 Privacy Mixer Boundary Handling
When a traced wallet enters a known privacy mixer, the engine stops tracing forward rather than producing false attribution. Instead it marks the last known pre-mixer wallet as the primary freeze target, generates a Mixer Boundary Directive with specific recommended off-chain actions, and lists exit candidates capped at addresses with ≤ 0.25 ETH withdrawn post-mixing to reduce false positive risk.

### 5.3 Exchange Wallet Clustering
The VASP registry contains over 15 Indian and international exchanges with their known deposit address clusters, FIU-IND registration status, and nodal officer contact information. Attribution scores reflect cluster membership, direct address matches, and regulatory registration.

### 5.4 Statutory Notice Generation (Maker/Checker)
The platform implements a two-officer approval workflow for Section 91 BNSS notices. An Investigator drafts the notice (auto-populated with VASP details, transaction hashes, and case data). A Supervisor reviews and cryptographically approves or rejects it. Approved notices carry a digital signature traceable to the authorizing officer.

### 5.5 AI Investigator Copilot
An AI assistant panel gives investigators plain-language investigative recommendations grounded strictly in the trace evidence. It is configured with an explicit anti-hallucination guardrail — it will not reference any address, hash, or entity not present in the active trace payload. It supports queries in English and Hindi. The AI provider badge (Groq, Gemini, or Rule-Based Fallback) is always visible so investigators know exactly what generated the recommendation.

### 5.6 Court-Admissible Evidence Package
Every case generates: a deterministic PDF investigation dossier with fund-flow graph, hop table, attribution decomposition, and audit hashes (Section 65B compliant); a SHA-256 chained audit ledger covering all system actions; and a cryptographic evidence payload verifiable via the evidence integrity endpoint.

### 5.7 Recovery Urgency Calculator
A 4-factor scoring calculator estimates the operational urgency of fund recovery for each case, accounting for elapsed time since crime, transaction value, chain type, and VASP cooperation history. It outputs a color-coded urgency band and is explicit about ineligibility — cases involving confirmed mixer entry or below-threshold values display disclaimers rather than inflated estimates.

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
- Multi-hop on-chain traversal for Ethereum (ERC-20), TRON (TRC-20), Bitcoin, and Polygon
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
The backend exposes 54 REST endpoints across 8 routers: AI Copilot, PDF Report, Intake, Tracing & Intelligence, Case Management, Statutory Notices, Audit & Evidence, and Authentication, plus WebSocket streaming at `/ws/trace/{case_id}`. Interactive documentation at `http://localhost:8765/docs`.

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
