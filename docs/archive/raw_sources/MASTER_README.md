# CryptoTrace LEA (SIH 26183) — Master System Documentation & Architectural Specification

> **Institutional Cryptocurrency Intelligence, Multi-Hop Attribution, Statutory Asset Freezing & Court-Admissible Evidence Dossier Platform**  
> **Theme:** Ministry of Home Affairs (MHA) / Indian Cyber Crime Coordination Centre (I4C) — CIS Division  
> **Problem Statement ID:** SIH 26183> **Architecture Version:** 2.1.0-SIH26183 (Production Clean Architecture & Win Plan Hardened)  
> **Status:** 129/129 Pytest Tests Green (100% Pass, 0 Regressions) | 18/18 Next.js Routes Compiled (Production Ready) | 10 Immutable Benchmark Baselines

---

## 1. Executive Summary & Core Capabilities

**CryptoTrace LEA** is an institutional-grade blockchain forensic intelligence and asset-recovery workstation engineered specifically for Indian Law Enforcement Agencies (LEAs), State Cyber Crime Police Stations, and Central Investigative Agencies (CBI, ED, NIA, I4C). The platform integrates real-time multi-chain explorer telemetry directly into statutory police workflows, empowering investigating officers to trace defrauded cryptocurrency, attribute terminal exchange clusters, issue enforceable asset freezing notices under **Section 91 of the Bharatiya Nagarik Suraksha Sanhita (BNSS 2023)**, and generate tamper-evident court dossiers compliant with **Section 63 & 65B of the Bharatiya Sakshya Adhiniyam (BSA 2023) / Indian Evidence Act**.

```
[ Victim Complaint / NCRP Portal / SAHYOG Bulletin ]
                        │
                        ▼ (Full BIP-39 2,048-Word Pre-Ingestion Sanitization)
            [ Automated Intake Gateway ]
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
[ LIVE ON-CHAIN CRAWLER ]       [ BENCHMARK EVALUATION ]
 (Etherscan, TronGrid, RPC)     (Deterministic Fixtures)
       │                                 │
       └────────────────┬────────────────┘
                        ▼
         [ Bounded Forensic Tracer ]
   ┌────────────────────┼────────────────────┐
   ▼                    ▼                    ▼
[MULE NETWORK]   [BRIDGE CROSS-CHAIN]  [PRIVACY MIXER HALT]
(3+ rapid hops)   (PROVEN event log)   (Pre-mixer freeze)
   └────────────────────┬────────────────────┘
                        ▼
   [ Dynamic Attribution & 6-Step VASP Scorer ]
  (Ambiguity Capped, FIU-IND Registry, Policy v1)
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
[AI COPILOT]     [RECOVERY WINDOW]  [OFAC SDN NEXUS]
(Grounded §91)    (4-Factor Decay)   (Critical +45)
       │                │                │
       └────────────────┬────────────────┘
                        ▼
    [ Standardized PDF Dossier & Notice Engine ]
 (ReportLab Deterministic Engine + Two-Officer Maker/Checker)
                        │
                        ▼
    [ SHA-256 Chained Immutable Audit Ledger ]
```

---

## 2. Completed 8-Phase Win Plan Implementation

The system implements the complete architectural upgrade plan specified in `TRACEX_SAHYOG_WIN_PLAN.md` and `LOGIC_IMPLEMENTATION_PLAN (1).md` without regression:

| Phase | Milestone Title | Key Architectural Implementations | Test Verification |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Baseline & CI/CD** | Golden baseline test suite, added `"NCRP"` to `CaseSource`, feature flags (`TRACE_STOP_AT_MIXER`, `TRACE_CROSS_CHAIN`, `TRACE_OFAC_SANCTIONS`), GitHub Actions CI pipeline, and dev requirements. | `test_golden_baseline.py`<br>`test_phase0_logic_fixes.py` (21/21) |
| **Phase 1** | **Attribution Correctness** | `AttributionResolver` walks terminal entities dynamically; enforces `MEDIUM` confidence ceiling on multi-match clusters; falls back to `UNRESOLVED` without defaulting to WazirX; parses live block timestamps (`_parse_transfer_timestamp`). | `test_phase5_attribution.py` (4/4)<br>`test_phase1_resilience.py` |
| **Phase 2** | **Privacy Mixer Boundary** | Curated `mixer_registry.py` (0.1, 1, 10, 100 ETH Tornado Cash pools on ETH/Arbitrum); `privacy_asset.py` typology; `MixerRecommendationEngine` generating pre-mixer freeze targets & $\le 0.25$ exit candidates; red mixer terminal markers in Cytoscape; Section 5 mixer directive in notices. | `test_phase6_mixer_boundary.py` (3/3)<br>`test_phase2_detection_gaps.py` |
| **Phase 3** | **Cross-Chain Bridges** | `bridge_registry.py` with Stargate, Across V2, and Wormhole router contracts and event topics; `cross_chain_analyzer.py` emitting `PROVEN` smart contract bridge links with solid cyan lines vs heuristic dashed lines. | `test_phase7_cross_chain.py` (3/3)<br>`test_phase3_accuracy.py` |
| **Phase 4** | **NCRP / SAHYOG Intake** | Bundled official 2,048-word English BIP-39 dictionary (`bip39_english.txt`); `bip39_validator.py` quarantining $\ge 12$ word seed phrases and private keys; persistent SQLite deduplication; `IntakeOrchestrator` managing state machine (`RECEIVED` $\to$ `NOTICE DRAFTED`); `/intake` UI with MHA Sandbox badge. | `test_phase8_intake_api.py` (4/4)<br>`test_phase4_external_boundaries.py` |
| **Phase 5** | **Forensic UI Story** | Dynamic `elapsed_hours` calculation from case creation / earliest hop; `CaseSummaryCard` with 6-step scoring breakdown accordion; `TimeToActionBanner` with urgency coloring and honest ineligibility disclosures; embedded in `/investigations`. | Frontend Verified<br>`test_phase5_polish.py` |
| **Phase 6** | **AI Copilot & PDF Report** | AI Copilot endpoints (`/recommend`, `/chat`, `/health`) with grounding guardrail and provider badges (`Groq`, `Gemini`, `Rule-Based Fallback`); deterministic court-admissible PDF investigation report via ReportLab + Matplotlib (`GET /api/v1/cases/{id}/report.pdf`) with bit-for-bit identical SHA-256 output. | `test_phase6_report_pdf.py` (3/3) |
| **Phase 7** | **OFAC Sanctions & Demo** | Screened all traversed addresses against official OFAC SDN registry; +45 risk bump triggering `CRITICAL` risk; prominent Red Sanctions Alert Banner; 10 dedicated evaluation benchmark fixtures; 4-Factor Recovery distribution chart; 7-Step Guided Demo Console (`/demo`); legacy dashboard bridge banner. | `test_phase7_ofac_and_fixtures.py` (3/3) |
| **Phase 8** | **Hardening & Verification** | Startup refusal if `APP_ENV=production` and default insecure `SECRET_KEY` is present; in-memory transfer caching per `(chain, address)`; graceful degradation of `data_completeness_pct` on provider timeout; **129 passed backend tests**; **18/18 static routes compiled cleanly**; **10/10 immutable golden baselines**. | Full Suite Verified (129/129) |

---

## 3. Quick Launch Guide

### Prerequisites
* **Python 3.10+** (Python 3.11, 3.12, 3.13 fully supported)
* **Node.js 18+** & **npm**

### Starting the Servers

#### Option A: Quick Command
```powershell
# 1. Start Backend API Server (Port 8765)
python -m uvicorn --app-dir "d:/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35/Crypto-Trace-Fin-08ac82779695698a5eab76d43b8a258cfabd9f35" app:app --host 0.0.0.0 --port 8765

# 2. In a second terminal, start Next.js Frontend (Port 3000)
cd frontend
npm run dev
```

#### Option B: Running Tests
```powershell
# Run complete test suite (129 tests across 18 test suites)
python -m pytest backend/tests -v

# Run frontend typecheck
npm --prefix frontend run typecheck

# Run production Next.js build
npm --prefix frontend run build
```

---

## 4. Key Access URLs & Ports

| Portal / Resource | URL | Description |
| :--- | :--- | :--- |
| **Guided Demo Console** | `http://localhost:3000/demo` | 7-step guided evaluation walkthrough demonstrating all core requirements |
| **Investigations Studio** | `http://localhost:3000/investigations` | Interactive Cytoscape graph canvas, Live/Demo toggle, Live On-Chain Inspector, AI Copilot |
| **NCRP Ingestion Gateway** | `http://localhost:3000/intake` | Government sandbox complaint ingestion with credential leak quarantine |
| **Heuristic Recovery Urgency** | `http://localhost:3000/recovery` | Multi-factor operational urgency calculator with progress distribution chart |
| **Case Docket** | `http://localhost:3000/cases` | Registered case list, FIR binding, and status tracking |
| **Section 91 Notice Console** | `http://localhost:3000/legal-notices` | Statutory BNSS notice drafting, review, and supervisor approval |
| **Cryptographic Audit Ledger** | `http://localhost:3000/audit` | Chained SHA-256 audit log with 1-click verification of zero post-facto tampering |
| **Backend REST API** | `http://localhost:8765` | FastAPI service root |
| **Swagger API Docs** | `http://localhost:8765/docs` | Interactive OpenAPI documentation for all 54 endpoints |
| **Court-Admissible PDF Report** | `http://localhost:8765/api/v1/cases/CR-2026-MULE-8821/report.pdf` | Direct download of deterministic Section 65B certified PDF investigation dossier |
| **Legacy Dashboard** | `dashboard.html` | Browser dashboard featuring persistent top banner bridge to workspace |

---

## 5. Pre-Configured Access Personas (RBAC)

The platform enforces Role-Based Access Control (RBAC). The following credentials are pre-seeded in the database:

| Username | Password | Role | Unit / Station | Statutory Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **`investigator1`** | `Password@123` | **INVESTIGATOR** | Cyber Crime Police Station, Mumbai | Create cases, execute traces, draft Section 91 notices, run copilot |
| **`supervisor1`** | `Password@123` | **SUPERVISOR** | Cyber Crime CID HQ, Maharashtra | Authorize & approve statutory Section 91 notices, verify audits |
| **`admin1`** | `Password@123` | **ADMINISTRATOR** | MHA / I4C CIS Division | System configuration, API keys, provider management |

---

## 6. SIH 26183 Dedicated Demonstration Scenarios

Ten reproducible evaluation fixtures are pre-configured in `backend/fixtures/` and verified with immutable baseline snapshots in `backend/tests/fixtures/baselines/`:

| Case ID | Chain | Primary Typology | Terminal Entity / Outcome | Scoring & Differentiators |
| :--- | :--- | :--- | :--- | :--- |
| **`CR-2026-MULE-8821`** | TRON | `MULE_NETWORK` | **WazirX (Zanmai Labs)** | 3-hop high-velocity mule syndicate, FIU-registered exchange attribution, `VERIFIED` score 0.88, Section 91 notice ready. |
| **`CR-2026-MIXER-BOUND-02`** | ETH | `MIXER_BOUNDARY` | **Tornado Cash (10 ETH Pool)** | Extortion ransom routes into mixer. Engine halts expansion (`MIXER_HALT`), generates pre-mixer freeze targets, caps exit candidates at 0.25, attribution `UNRESOLVED`. |
| **`CR-2026-CROSS-CHAIN-BRIDGE-03`** | ETH | `CROSS_CHAIN_BRIDGE` | **Stargate Bridge $\to$ TRON** | ETH USDT $\to$ TRON USDT bridge routing. Differentiates `PROVEN` smart contract events from heuristic correlation. |
| **`CR-2026-PEEL-CHAIN-04`** | BTC | `PEEL_CHAIN` | **Change Address Segregation** | Structured incremental peeling; isolates payment hops from high-frequency change outputs. |
| **`CR-2026-OFAC-SDN-05`** | ETH | `OFAC_SANCTION_HIT` | **Lazarus Group (Ronin Exploiter)** | Direct hit on US Treasury OFAC SDN List (SDN ID 34991). Immediate +45 risk bump to `CRITICAL` (90/100) and Red Sanctions Banner. |
| **`CR-2026-FLASH-LOAN-DEFI-06`** | ETH | `DEFI_INTERACTION` | **Aave / Uniswap Pool** | Flash loan liquidity manipulation tagged with smart contract interaction labels. |
| **`CR-2026-DEPOSIT-SWEEP-07`** | ETH | `CONSOLIDATION_FUNNEL` | **CoinDCX Consolidation** | 4-to-1 multi-victim task scam consolidation into domestic VASP with Section 91 preservation priority. |
| **`CR-2026-CHAIN-HOP-MULTICURRENCY-08`** | BTC/ETH | `RAPID_HOP` | **Multi-Currency Flow** | Cross-asset value normalizer active with real-time INR/USD dual denomination. |
| **`CR-2026-MULTI-REORG-RESILIENCE-09`** | ETH | `REORG_RESILIENCE` | **Canonical DB Rollback** | Deep 2-block chain reorganization recovery without data corruption. |
| **`CR-2026-REVERTED-TX-FAILURE-10`** | ETH | `FAILED_EXECUTION` | **Reverted Transaction** | Zeroes out unexecuted value transfers while retaining forensic execution trail. |

---

## 7. Complete REST API Endpoint Directory

The backend exposes 54 endpoints across canonical routers:

### A. AI Copilot (Phase 6.1)
- `POST /api/v1/copilot/{case_id}/recommend` — Generates BNSS §91 grounded actions with provider fallback badge (`Groq` / `Gemini` / `Rule-Based Fallback`).
- `POST /api/v1/copilot/{case_id}/chat` — Interactive natural language queries in English and Hindi with anti-hallucination address grounding check.
- `GET /api/v1/copilot/health` — Returns status of active AI inference providers and rate-limit cache.

### B. Standardized PDF Report Generation (Phase 6.2)
- `GET /api/v1/cases/{case_id}/report.pdf` — Returns court-admissible, deterministic PDF investigation dossier with Section 65B certification, server-side fund-flow graph, hop table, attribution decomposition, and audit hashes.

### C. Government Ingestion & Intake (Phase 4)
- `POST /api/v1/intake/ncrp/complaint` — Ingests citizen fraud complaint from NCRP portal with 2,048-word BIP-39 sanitizer and persistent deduplication.
- `POST /api/v1/intake/sahyog/bulletin` — Ingests multi-wallet threat intelligence bulletin from SAHYOG portal.
- `GET /api/v1/intake/status` — Returns ingestion pipeline status, processed count, and quarantine log.
- `GET /api/v1/intake/queue` — Lists active complaints progressing through workflow stages.
- `POST /api/v1/intake/{case_id}/trace` — Triggers automated background trace for an ingested complaint.

### D. Tracing & Intelligence (Phases 1, 2, 3, 7)
- `POST /api/v1/trace` — Bounded multi-hop traversal with dynamic attribution, mixer boundary halting, cross-chain bridge parsing, and OFAC sanctions screening.
- `GET /api/v1/fixtures` — Lists all 6 dedicated SIH evaluation benchmark scenarios.
- `GET /api/live/{address}?chain={chain}` — Queries live on-chain balances, recent transactions, counterparties, and OFAC status.
- `GET /api/chains` — Explorer endpoints and protocol configurations for BTC, ETH, TRON, and Polygon.
- `GET /api/vasps` — Institutional registry of 15+ VASPs with FIU registration status and nodal contact emails.

### E. Case Docket & Management
- `POST /api/v1/cases` — Registers an authorized investigation record.
- `GET /api/v1/cases` — Lists investigative cases in the docket.
- `GET /api/v1/cases/{case_id}` — Detailed dossier lookup for a case.

### F. Statutory Section 91 Notices (Maker/Checker)
- `POST /api/v1/notices/draft` — Compiles formal Section 91 BNSS freeze requisition notice.
- `GET /api/v1/notices/{draft_id}` — Retrieves drafted requisition text and target details.
- `POST /api/v1/notices/{draft_id}/submit` — Submits draft for supervisory review.
- `POST /api/v1/notices/{draft_id}/approve` — Supervisor authorization and cryptographic signing.
- `POST /api/v1/notices/{draft_id}/reject` — Supervisor rejection with written justification.

### G. Cryptographic Audit & Evidence Integrity
- `GET /api/v1/audit/events` — Chronological chained audit event stream.
- `GET /api/v1/audit/verify-chain` — Validates Genesis-to-Head SHA-256 chain integrity.
- `GET /api/v1/audit/trail/{case_id}` — Case-specific chained audit trail.
- `GET /api/v1/evidence/payload/{payload_hash}` — Retrieves raw on-disk serialized evidence payload.
- `POST /api/v1/evidence/verify/{payload_hash}` — Re-computes SHA-256 hash to prove zero tampering.

### H. Authentication & Roles (JWT)
- `POST /api/v1/auth/login` — Issues HS256 JWT access tokens.
- `GET /api/v1/auth/me` — Returns authenticated investigator identity and roles.

---

## 8. Directory Structure

```text
tracex-sahyog-main/
├── backend/
│   ├── adapters/            # Blockchain gateways & BIP-39 validator
│   ├── api/                 # FastAPI canonical v1 routers (intake, copilot, cases, trace...)
│   ├── assessment/          # RiskAssessor & RecoveryEstimator engines
│   ├── attribution/         # AttributionResolver & AdaptiveVASPScorer
│   ├── audit/               # Immutable chained SHA-256 audit engine
│   ├── config/              # AppConfig & environment feature flags
│   ├── cross_chain/         # Bridge registry (Stargate, Across, Wormhole) & analyzer
│   ├── db/                  # SQLite schema manager, migrations, deduplication
│   ├── fixtures/            # 6 dedicated demonstration benchmark scenarios
│   ├── ingestion/           # IntakeOrchestrator state machine
│   ├── legal/               # ReportGenerator (PDF), NoticeGenerator (§91), MixerRecommender
│   ├── models/              # Pydantic schemas, domain types, confidence tiers
│   ├── storage/             # Raw evidence payload repository
│   ├── tests/               # 51 unit & regression tests (100% passing)
│   └── typologies/          # MixerRegistry, MuleNetwork, PeelChain, PrivacyAsset
├── engine/                  # Legacy & auxiliary intelligence utilities (OFAC, Neo4j, Real API)
├── frontend/                # Next.js 14 Workspace Portal
│   ├── app/(workspace)/
│   │   ├── demo/            # 7-Step Guided Evaluation Walkthrough
│   │   ├── intake/          # Sandbox NCRP/SAHYOG Ingestion Console
│   │   ├── investigations/  # Graph canvas, Live/Demo Inspector, Copilot
│   │   ├── recovery/        # 4-Factor Urgency Distribution Chart
│   │   ├── cases/           # Case docket & FIR binding
│   │   ├── legal-notices/   # Section 91 BNSS requisition manager
│   │   └── audit/           # Tamper-evident audit chain verifier
│   ├── components/forensic/ # TimeToActionBanner, TraceBoundaryCard, CaseSummaryCard, CopilotPanel...
│   ├── features/graph/      # Interactive Cytoscape.js canvas
│   └── types/domain.ts      # TypeScript interfaces matching backend models
├── data/                    # SQLite database (sahyog.db), audit logs, evidence
├── dashboard.html           # Legacy browser dashboard with workspace navigation banner
├── Frontend Requirements.md # Comprehensive UI component and button specification
└── app.py                   # Main FastAPI application entrypoint with security guards
```

---

## 9. Statutory Compliance & Evidence Integrity

- **Section 91 Bharatiya Nagarik Suraksha Sanhita (BNSS, 2023)**: Formal statutory production order served to registered Nodal Officers for crypto asset freezing and KYC unmasking.
- **Section 63 & 65B Bharatiya Sakshya Adhiniyam (BSA, 2023) / IEA**: Electronic evidence generated by the system includes immutable SHA-256 ledger hashes, server-side cryptographic audit signatures, and deterministic PDF byte reproducibility.
- **PMLA & FIU-IND Guidelines**: Contextual attribution rewards reporting entities registered with the Financial Intelligence Unit - India with preferential evidentiary weighting.
