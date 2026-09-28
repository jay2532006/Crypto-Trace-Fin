# CryptoTrace LEA — Frontend UI/UX Requirements & Functional Specification

> **Workstation Specification for Indian Law Enforcement Agencies (LEAs)**  
> **Alignment:** Ministry of Home Affairs (MHA) / I4C CIS Division (Problem Statement SIH 26183)  
> **Target Framework:** Next.js 14 (App Router) + React 18 + TailwindCSS + Lucide Icons + Cytoscape.js  
> **Backend Synchronization:** FastAPI Canonical v1 APIs (`http://localhost:8765/api/v1/...`)  
> **Security & RBAC:** Role-Based Access Control (Investigator, Supervisor, Administrator)

---

## 1. Architectural UI Overview & Design System

The CryptoTrace LEA frontend workstation is structured as a mission-critical, low-latency intelligence console tailored for cyber police officers, forensic investigators, and supervisory leadership.

### Color Palette & Visual Tokens
- **Background**: Dark Mode (`#0b1120`, `#0f172a`, `#020617`) with glassmorphism and subtle border illumination (`#1e293b`, `#334155`).
- **Primary / Forensic Blue**: `#2563eb`, `#3b82f6` (System controls, navigations, verified hops).
- **Attribution / Success Emerald**: `#10b981`, `#059669` (FIU-IND registered VASPs, verified terminal hot wallets).
- **Privacy Mixer / Critical Hazard Red**: `#ef4444`, `#dc2626` (Mixer boundaries, OFAC SDN hits, statutory quarantine).
- **Cross-Chain Bridge Cyan**: `#06b6d4`, `#0891b2` (PROVEN smart contract bridge corridors, LayerZero/Stargate routers).
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
   - **Chain Dropdown**: `ETH` (Ethereum ERC-20), `TRON` (TRC-20), `BTC` (Bitcoin), `POLYGON`.
   - **Max Hops Slider**: Integer range `1` to `6` (Default `4`).
   - **Button**: `Start Multi-Hop Trace` (Icon: `Play`, Variant: Primary Blue).
     - **API**: `POST /api/v1/trace`
     - **Payload**: `{"address": "...", "chain": "...", "max_hops": 4, "mode": "LIVE"|"DEMO"}`
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
   - Displays live **Indian Rupee (₹ INR)** conversion via CoinGecko spot rates.
3. **Confirmed Transactions Table**:
   - Displays the last 10 confirmed on-chain transactions.
   - Columns: Tx Hash, Block Age, Counterparty, Value, Explorer Link.
   - Button: `Load Into Graph` (Icon: `Network`, Variant: Outline Cyan) — Appends transactions into Cytoscape graph canvas.

#### C. Forensic Intelligence Cards (Win Plan Components)
1. **Time-to-Action Banner (`TimeToActionBanner.tsx`)**:
   - **Data**: `traceData.recovery_estimate`
   - **Display**: Action window hours remaining (e.g., `22 Hours Remaining`), urgent dissipation countdown, color-coded urgency badge (`URGENT`, `EXPIRING`, `MODERATE`).
   - **Ineligible State**: If criteria not met (e.g., < $120 value, mixer obstruction), displays explicit disclaimer: "Ineligible for recovery estimation per PRD FR-016".
2. **Trace Boundary Card (`TraceBoundaryCard.tsx`)**:
   - **Data**: `traceData.boundary_events`, `traceData.partial_recommendation`
   - **Display**: Rendered when `termination_reason === "MIXER_BOUNDARY_HIT"`.
   - **Visuals**: Red hazard badge, Pre-Mixer Target Address, Recommended Off-Chain Actions (subpoena RPC logs, issue freeze order on pre-mixer wallet).
   - **Button**: `Copy Pre-Mixer Address` (Icon: `Copy`).
3. **Case Summary Card (`CaseSummaryCard.tsx`)**:
   - **Data**: `traceData.attribution`
   - **Display**: Terminal VASP Chip (e.g., `WazirX (Zanmai Labs Pvt Ltd)`), Confidence Band (`HIGH` / `MEDIUM` / `LOW`), FIU-IND Registration Status (`REGISTERED` / `UNREGISTERED`).
   - **Scoring Accordion**: Expandable 6-step breakdown (Base Confidence, FIU Bonus, Exact Match, Hop Penalty, Freshness, Data Completeness).
4. **OFAC Sanctions Nexus Alert Banner**:
   - **Data**: Rendered when `traceData.ofac_sanction_hit === true`.
   - **Visuals**: Flashing red warning banner citing official OFAC Specially Designated Nationals (SDN) registry.
   - **Text**: Identifies designated entity (e.g., "Lazarus Group - Ronin Bridge Exploiter, SDN ID 34991").
   - **Directive**: "Mandatory Section 91 BNSS Immediate Asset Freeze Order in effect."
5. **AI Investigator Copilot Panel (`CopilotPanel.tsx`)**:
   - **Header**: "AI Investigator Copilot" with **Provider Badge** (`Groq`, `Gemini`, `Rule-Based Fallback`).
   - **Guardrail Pill**: "BNSS §91 Grounded — Zero Hallucinations Tolerated".
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
  - Terminal Exchange / VASP Node: Emerald Green with verified checkmark.
  - Privacy Mixer Node: Crimson Red with octagon stop icon.
  - Bridge Contract Node: Cyan with dual-chain badge.
- **Edge Standards**:
  - Standard Transfer: Solid slate line with transaction amount label.
  - PROVEN Bridge Link: Solid cyan line (`link_type: "PROVEN"`).
  - Heuristic Correlation: Dashed purple line (`link_type: "HEURISTIC_CORRELATION"`).

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
