# CryptoTrace LEA (SIH 26183) ? Master System Documentation

> **Institutional Cryptocurrency Intelligence, Multi-Hop Attribution & Statutory Asset Freezing Platform**  
> **Theme:** Ministry of Home Affairs (MHA) / Indian Cyber Crime Coordination Centre (I4C) ? CIS Division  
> **Problem Statement ID:** SIH 26183  
> **Architecture Version:** 2.0.0-SIH26183 (Production Clean Architecture)

---

## 1. Executive Summary & Core Capabilities

**CryptoTrace LEA** is an end-to-end blockchain forensic intelligence workstation engineered for Indian Law Enforcement Agencies (LEAs), State Cyber Police Stations, and Central Agencies (CBI, ED, NIA). The platform bridges live on-chain explorer telemetry directly into judicial workflows, empowering investigating officers to trace stolen digital assets, identify destination Virtual Asset Service Providers (VASPs), issue enforceable asset freeze notices, and produce court-admissible evidence.

### Primary Differentiators
1. **Interactive Dual-Mode Pipeline**:
   - ?? **LIVE ON-CHAIN MODE**: Directly crawls **Etherscan V2**, **TronGrid**, and **Blockstream Esplora** in real-time, discovers live multi-hop transaction paths, and links genuine transaction hashes to block explorers.
   - ?? **BENCHMARK DEMO MODE**: Loads pre-packaged, reproducible benchmark scenarios (WazirX breach, NCRP mule rings, Tornado mixer boundaries) for zero-latency hackathon jury evaluation.
2. **Dedicated Live On-Chain Data Inspector**:
   - Direct 1-click test wallets for **Vitalik Buterin (ETH)**, **Binance Hot Wallet (ETH)**, **Official Tether USDT Contract (TRON)**, and **Satoshi Nakamoto Genesis (BTC)**.
   - Live on-chain balance display paired with real-time **Indian Rupee (? INR)** spot conversions via CoinGecko.
   - Table of confirmed transactions with 1-click "Load Into Graph" streaming into interactive Cytoscape network canvas.
3. **Statutory Legal Requisition Engine (Section 91 BNSS 2023 / Section 91 CrPC)**:
   - Translates technical transaction graphs into statutory freezing orders served to registered exchange Nodal Officers.
   - Enforces the statutory **Two-Officer Rule**: Investigating Officers draft notices; Supervisory Officers review and approve.
4. **Cryptographic SHA-256 Tamper-Evident Audit Chain**:
   - Every case creation, trace execution, and legal notice approval is hashed and linked to the previous block hash via a Genesis-to-Head cryptographic chain in SQLite.
   - Compliant with **Section 63 & 65B of the Bharatiya Sakshya Adhiniyam (BSA 2023)** / Indian Evidence Act.
5. **Multi-Provider Health & Gateway Diagnostics**:
   - Built-in diagnostic suite testing 7 external APIs simultaneously with millisecond latency telemetry.

---

## 2. Quick Launch Guide (Running Everything)

### Prerequisites
* **Python 3.10+** (Python 3.11 / 3.12 / 3.13 supported)
* **Node.js 18+** & **npm**

### Step 1: Start the Backend (FastAPI)
Open a terminal in the project root:
```powershell
# In d:\CRYPTO-TRACE\tracex-sahyog-main\tracex-sahyog-main
python app.py
```
* **Backend URL:** `http://localhost:8765`
* **Swagger API Docs:** `http://localhost:8765/docs`
* **ReDoc Specification:** `http://localhost:8765/redoc`

### Step 2: Start the Frontend (Next.js 14)
Open a second terminal in the `frontend` directory:
```powershell
cd frontend
npm run dev
```
* **Frontend Portal:** `http://localhost:3000`

---

## 3. Pre-Configured Access Credentials (RBAC Personas)

The platform enforces Role-Based Access Control (RBAC). For testing and demonstration, use the following verified credentials:

| Username | Password | Assigned Role | Unit / Organization | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **`investigator1`** | `Password@123` | **INVESTIGATOR** | Cyber Crime Police Station, Mumbai | Create cases, execute traces, draft Section 91 notices |
| **`supervisor1`** | `Password@123` | **SUPERVISOR** | Cyber Crime CID HQ, Maharashtra | Review & approve statutory freeze notices, sign audits |
| **`admin1`** | `Password@123` | **ADMINISTRATOR** | MHA / I4C CIS Division | System configuration, API keys, provider management |

---

## 4. Frontend Workstation Modules

The Next.js 14 frontend (`frontend/app/(workspace)/...`) is structured into dedicated operational consoles:

| Route | Module Title | Key Functionality |
| :--- | :--- | :--- |
| **`/login`** | Authentication Portal | Secure JWT-based access with 1-click persona switcher for evaluation. |
| **`/dashboard`** | Operations Command Console | Live CoinGecko Fiat Spot Rates Banner (BTC ?, ETH ?, USDT ?, TRX ?), active case metrics, tracked fraud volume, and cryptographic security state. |
| **`/investigations`** | Forensic Trace & Attribution | **Mode Switcher** (`?? LIVE ON-CHAIN` vs `?? BENCHMARK DEMO`), **Live On-Chain Data Inspector** (with 1-click test wallets), Cytoscape interactive graph canvas, and hop-by-hop ledger. |
| **`/cases`** | Case Dossier Intake | Victim complaint intake, FIR number binding, suspect wallet validation, and anti-credential leak guardrails (rejects private keys). |
| **`/legal-notices`** | Section 91 BNSS Notices | Draft, review, and approve statutory asset-freezing orders directed to Indian and international exchange Nodal Officers. |
| **`/audit`** | Cryptographic Audit Ledger | Real-time event log with 1-click Genesis-to-Head SHA-256 chain integrity verification. |
| **`/evidence`** | Digital Evidence Repository | Case evidence manifest with automated SHA-256 tamper verification proving court admissibility. |
| **`/provider-status`** | Gateway Health Diagnostics | Real-time upstream health monitor running live latency diagnostics against Etherscan, TronGrid, Blockstream, CoinGecko, and OFAC. |

---

## 5. Complete REST API Specification

The FastAPI backend exposes 45 endpoints across canonical v1 routers and diagnostic services:

### A. Health & Diagnostics
* `GET /api/health` ? Backend operational status, version, and server timestamp.
* `GET /api/config` ? Active runtime mode, supported chains, and disclaimer metadata.
* `GET /api/prices` ? Real-time cryptocurrency spot rates in USD and INR via CoinGecko.
* `GET /api/test/apis` ? Diagnostic connectivity check across all 7 connected blockchain & threat APIs.
* `GET /api/test/api/{api_id}` ? Live ping against a specific API gateway (`etherscan`, `trongrid`, `esplora`, `coingecko`, `ofac`, `chainabuse`).

### B. Live Blockchain Harvester & Tracing
* `GET /api/live/{address}?chain={chain}` ? Queries real on-chain balance, recent block transactions, counterparties, and OFAC status via public explorers.
* `POST /api/v1/trace` ? **Canonical Trace Engine**. Bounded multi-hop traversal supporting `mode: "LIVE"` (on-chain exploration) and `mode: "DEMO"` (benchmark evaluation).
* `GET /api/chains` ? Metadata, explorers, and supported standards for BTC, ETH, TRON, and Polygon.
* `GET /api/vasps` ? Institutional registry of 15+ VASPs with FIU-IND statuses, nodal emails, and hot wallet clusters.

### C. Case Dossier Management
* `GET /api/v1/cases` ? Retrieves all registered investigative cases.
* `POST /api/v1/cases` ? Ingests a new cybercrime complaint with cryptographic validation and audit logging.
* `GET /api/v1/cases/{case_id}` ? Detailed dossier lookup for a specific case.

### D. Statutory Legal Notices (Section 91 BNSS / CrPC)
* `POST /api/v1/notices/draft` ? Compiles a formal Section 91 asset freeze requisition notice.
* `GET /api/v1/notices/{draft_id}` ? Retrieves drafted requisition details.
* `POST /api/v1/notices/{draft_id}/submit` ? Submits draft for supervisory review.
* `POST /api/v1/notices/{draft_id}/approve` ? Supervisory cryptographic approval and authorization.
* `POST /api/v1/notices/{draft_id}/reject` ? Supervisory rejection with remarks.

### E. Cryptographic Audit & Evidence
* `GET /api/v1/audit/events` ? Chronological chained audit event stream from SQLite.
* `GET /api/v1/audit/verify-chain` ? Validates SHA-256 chain integrity from Genesis to Head.
* `GET /api/v1/audit/trail/{case_id}` ? Case-specific chained audit trail.
* `GET /api/v1/evidence/payload/{payload_hash}` ? Retrieves raw JSON payload by SHA-256 fingerprint.
* `POST /api/v1/evidence/verify/{payload_hash}` ? Re-computes SHA-256 hash against on-disk payload to prove forensic integrity.

### F. Authentication & RBAC
* `POST /api/v1/auth/login` ? Issues signed JWT access token.
* `GET /api/v1/auth/me` ? Returns current authenticated officer persona and permissions.

### G. AI Forensic Copilot (Groq / Gemini)
* `GET /api/ai/health` ? Tests connectivity to Groq Cloud and Google Gemini.
* `POST /api/ai/copilot/chat` ? Context-grounded forensic Q&A assistant (English, Hindi, Hinglish).
* `POST /api/ai/copilot/summary` ? Generates fund flow summary and VASP attribution briefing.
* `POST /api/ai/copilot/report` ? Compiles formal Section 91 judicial investigation report.

---

## 6. External API Gateways & Connectivity

TraceX integrates with 7 external blockchain and intelligence providers:

| Gateway Provider | Upstream Endpoint | Required Key / Env | Tier / Limits | Role in CryptoTrace LEA |
| :--- | :--- | :--- | :--- | :--- |
| **Etherscan V2 API** | `https://api.etherscan.io/v2/api` | `ETHERSCAN_API_KEY` | Developer Free | Live Ethereum & EVM balances, internal txs, and ERC-20 transfers. |
| **TronGrid API** | `https://api.trongrid.io` | `TRONGRID_API_KEY` | Pro Developer | TRON mainnet TRX balances and TRC-20 USDT token transfer events. |
| **Blockstream Esplora** | `https://blockstream.info/api` | *Public Gateway* | Open / Zero-Key | Bitcoin UTXO summaries, mempool status, and confirmed block transactions. |
| **CoinGecko API** | `https://api.coingecko.com/api/v3` | `COINGECKO_DEMO_API_KEY` | Demo Tier | Real-time spot prices for BTC, ETH, USDT, and TRX in both USD and INR (?). |
| **Groq LPU Cloud** | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` | Free Cloud Tier | Sub-second neural inference for AI Copilot reasoning (`qwen/qwen3.8-27b`). |
| **OFAC Sanctions List** | *Internal Engine + US Treasury SDN* | *Public Registry* | Open / Curated | Screening against US Treasury sanctioned wallets, mixers, and terror financing rings. |
| **Chainabuse API** | `https://www.chainabuse.com` | `CHAINABUSE_API_KEY` | Community Tier | Crowdsourced malicious wallet addresses and cybercrime reports. |

---

## 7. Data Architecture & Cryptographic Integrity

### SQLite Schema (`data/sahyog.db`)
* **`investigations`**: Case IDs, suspect addresses, detected chains, attribution metrics, and raw result JSON payloads.
* **`audit_events`**: Immutable ledger records storing `event_id`, `timestamp`, `user_id`, `action`, `resource_id`, `details_json`, `previous_event_hash`, and `event_hash`.
* **`notices`**: Drafted, submitted, and approved Section 91 notice documents.

### Cryptographic Chaining Formula
Every event appended to the audit ledger computes its cryptographic hash using the SHA-256 algorithm:
$$\text{Event Hash} = \text{SHA256}(\text{previous\_hash} \parallel \text{event\_id} \parallel \text{timestamp} \parallel \text{user\_id} \parallel \text{action} \parallel \text{resource\_id} \parallel \text{resource\_type} \parallel \text{result} \parallel \text{details\_json})$$

When verifying the chain (`/api/v1/audit/verify-chain`), the engine re-computes hashes from the Genesis block (`GENESIS_00000...`) to the latest head. If even a single byte has been altered in the database, the exact corrupted record index is flagged immediately.

---

## 8. Verification & Live Testing Walkthrough

To verify the complete platform integration:

1. **Check Live CoinGecko Price Feed**:
   Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard). The top header and dashboard banner will display live prices (e.g., `BTC: $84,445 (?80.91L)`, `USDT: ?95.79`).
2. **Inspect a Real Blockchain Wallet**:
   Navigate to [http://localhost:3000/investigations](http://localhost:3000/investigations).
   - In the **Live On-Chain Inspector**, click **"Vitalik Buterin (ETH)"** or **"Satoshi (BTC)"**.
   - Observe live balance, OFAC clearance, and confirmed transactions table.
   - Click **"Load Into Graph"** to render live transactions into the Cytoscape canvas.
3. **Execute Live Multi-Hop Trace**:
   - Toggle pipeline mode to **`?? LIVE ON-CHAIN`**.
   - Click **"EXECUTE TRACE"**.
   - Review multi-hop traversal metrics, VASP attribution verdict, and risk scoring.
4. **Draft & Approve Section 91 Notice**:
   - Click on the destination exchange node (e.g., WazirX).
   - Click **"Draft Section 91 Notice"** to generate the requisition document.
   - Switch persona to `supervisor1` via the top-right menu and approve the order.
5. **Verify Cryptographic Chain-of-Custody**:
   - Open [http://localhost:3000/audit](http://localhost:3000/audit).
   - Click **"Verify Cryptographic Integrity"** to confirm 100% mathematical integrity across all recorded actions.

---

## 9. Statutory Compliance & Legal Framework

* **Section 91, Bharatiya Nagarik Suraksha Sanhita (BNSS 2023)**: Replaces Section 91 of the Code of Criminal Procedure (CrPC 1973) for judicial summons to produce documents and digital assets.
* **Section 63 & 65B, Bharatiya Sakshya Adhiniyam (BSA 2023)**: Replaces Section 65B of the Indian Evidence Act 1872 for electronic records admissibility.
* **Section 67C, Information Technology Act (IT Act 2000)**: Mandatory preservation of cyber records by intermediaries.
* **FIU-IND Anti-Money Laundering Guidelines (PMLA 2002)**: Compliance verification for reporting virtual digital asset entities.
