# CryptoTrace LEA — Modern Next.js Frontend
**SIH Problem Statement 26183 | Law Enforcement Cryptocurrency Intelligence & Attribution Platform**

Production-ready, evidence-first, institutional frontend for **CryptoTrace LEA**, designed specifically for Law Enforcement Agencies (LEAs) in India (I4C, MHA, State Cyber Cells). Built with Next.js 14 App Router, TypeScript, Tailwind CSS, TanStack Query, Zustand, and Cytoscape.js.

---

## 🏛️ Institutional Design System & Standards
- **Government Authority Palette**: Navy blue `#062B6F`, `#082B63`, Slate dark `#070F1E`, `#0B1528`, Saffron/Gold accent `#E5A33D`, Forest Green `#198754`, Crimson Red `#DC2626`.
- **Zero-Mock Rule in Production**: All operational forensic workflows connect directly to the Python/FastAPI backend on port 8765 via `/api/*` reverse-proxy rewrites.
- **Section 91 BNSS 2023 / CrPC Workflow**: Strict role-gated preservation drafting and supervisor approval gates.
- **Section 65B Bharatiya Sakshya Adhiniyam (BSA 2023)**: Content-addressed evidence storage with live SHA-256 integrity verification.
- **Mandatory Uncertainty Disclosure (PRD §9)**: Automated heuristics (Mule networks, peeling chains) display explicit confidence limits capped at `MEDIUM` with court admissibility disclaimers.

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js >= 18.17.0 (Verified on Node v24.13.0, npm 11.6.2)
- Python 3.10+ (Running the CryptoTrace LEA FastAPI backend on `http://127.0.0.1:8765`)

### 1. Start the FastAPI Backend (Terminal 1)
```powershell
cd d:\CRYPTO-TRACE\tracex-sahyog-main\tracex-sahyog-main
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload
```

### 2. Start the Next.js Frontend (Terminal 2)
```powershell
cd d:\CRYPTO-TRACE\tracex-sahyog-main\tracex-sahyog-main\frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔑 Preset Credentials (1-Click Evaluation)

The login screen (`/login`) includes 1-click persona quick-fill buttons:

| Role | Username | Password | Jurisdiction Unit | Operational Privileges |
| :--- | :--- | :--- | :--- | :--- |
| **Investigator** | `investigator1` | `Password@123` | Cyber Crime Police Station | Tracing, Case Intake, Requisition Drafting |
| **Supervisor** | `supervisor1` | `Password@123` | Office of SP (Cyber) | Section 91 Notice Approval & Rejection Gate |
| **Administrator** | `admin1` | `Password@123` | State Cyber Command | Full System Config & Audit Trail Clearance |
| **Service Integration** | `ncrp_service` | `Password@123` | I4C NCRP / SAHYOG Gateway | API Ingestion & System Webhooks |

---

## 📂 Architecture & Directory Layout

```
frontend/
├── app/
│   ├── (auth)/
│   │   └── login/page.tsx             # 1-Click Evaluation & JWT Authentication
│   ├── (workspace)/
│   │   ├── layout.tsx                 # Protected Layout with TopBar & Sidebar
│   │   ├── dashboard/page.tsx         # KPI Deck, Active Cases & Notice Status
│   │   ├── cases/page.tsx             # Case Intake & Validation (Private Key Rejection)
│   │   ├── investigations/page.tsx    # Forensic Trace Workspace & Cytoscape Graph
│   │   ├── typologies/page.tsx        # MULE_NETWORK & MIXER_BOUNDARY Rule Engines
│   │   ├── attribution/page.tsx       # AdaptiveVASPScorer 6-Step Dynamic Matrix
│   │   ├── recovery/page.tsx          # Heuristic Recovery Estimate (PRD FR-016 Gated)
│   │   ├── legal-notices/page.tsx     # Section 91 CrPC Requisition & Approval
│   │   ├── evidence/page.tsx          # SHA-256 Content-Addressed Evidence Manifest
│   │   ├── audit/page.tsx             # Cryptographic Chained Audit Ledger
│   │   ├── provider-status/page.tsx   # Blockchain Gateway Diagnostics & Latency
│   │   └── settings/page.tsx          # Node Profile, BNSS/BSA Mandate & Telemetry
│   ├── globals.css                    # Tailwind Tokens & Institutional Themes
│   ├── layout.tsx                     # Root Layout (Google Fonts Outfit & Inter)
│   └── providers.tsx                  # TanStack Query & Auth Initialization
├── components/
│   ├── debug/
│   │   └── DebugPanel.tsx             # Floating Telemetry & RFC-5424 Log Drawer
│   ├── forensic/
│   │   ├── AddressBadge.tsx           # Formatted Crypto Address with Copy
│   │   ├── ConfidencePill.tsx         # HIGH / MEDIUM / LOW / LEAD Pill
│   │   ├── HashDisplay.tsx            # SHA-256 & Tx Hash Truncated Display
│   │   └── UncertaintyBanner.tsx      # PRD §9 Mandatory Uncertainty Disclosure
│   ├── navigation/
│   │   ├── Sidebar.tsx                # Institutional Collapsible Navigation
│   │   ├── TopBar.tsx                 # Live Crypto Ticker & Persona Switcher
│   │   └── UserRoleBadge.tsx          # Canonical 4-Role Pill
│   └── ui/                            # Accessible UI Primitives
│       ├── Alert.tsx, Badge.tsx, Button.tsx, Card.tsx, Input.tsx, Modal.tsx, Table.tsx
├── features/
│   └── graph/
│       └── CytoscapeGraph.tsx         # Client-side Forensic Fund-Flow Graph Canvas
├── lib/
│   ├── api-client.ts                  # Axios with x-request-id & Latency Interceptors
│   ├── auth.ts                        # JWT Session Storage & Preset Users
│   ├── logger.ts                      # RFC-5424 Structured In-Memory Logger
│   ├── permissions.ts                 # 4-Role RBAC Capability Matrix
│   ├── query-client.ts                # TanStack Query Client Configuration
│   └── utils.ts                       # INR, USD, Crypto & Address Formatters
├── stores/
│   ├── auth-store.ts                  # Zustand Auth Session State
│   ├── debug-store.ts                 # Zustand Developer Drawer & Log Store
│   └── graph-store.ts                 # Zustand Cytoscape Node/Edge State
├── next.config.mjs                    # Reverse Proxy to 127.0.0.1:8765
├── tailwind.config.ts                 # MHA/I4C Institutional Color Palette
└── tsconfig.json                      # Strict TypeScript Configuration
```

---

## 🔍 Core Innovations Implemented

### 1. MULE_NETWORK Typology Engine (`/typologies`)
- **Criteria**: $\ge 3$ intermediate wallets, sub-60 minute hop turnover, $\pm 15\%$ fee tolerance.
- **Standard**: Capped strictly at `MEDIUM` confidence to avoid overstating correlations in legal affidavits. Includes interactive parameter simulation deck.

### 2. Adaptive VASP Attribution Engine (`/attribution`)
- **Deterministic 6-Step Scoring Matrix**:
  1. Jurisdiction Policy Load (`policy_v1_india_kyc`)
  2. Single-Hop Structural Override (+20 points)
  3. Contextual Modifiers: FIU-IND domestic registration (+15), Hop decay (-8 per hop), Hot wallet pattern (+35 exact / +15 cluster), Mixer penalty (-30), Cluster recency (+10).
  4. Conflict Resolution: Suppresses exact matches when mixer boundary is crossed.
  5. Clamp & Renormalize: Clamped in bound `[5, 95]`.

### 3. Heuristic Recovery Estimate (`/recovery`)
- **PRD FR-016 Boundary Gating**: Gated by threshold ($\ge ₹10,000$ INR / $\$120$ USD), hop count $> 0$, data completeness $\ge 70\%$, confidence $\ge \text{MEDIUM}$, zero mixer presence.
- **Golden Window Countdown**: Dynamic 24–48 hour urgency decay gauge for time-critical Section 91 preservation notice dispatch.

### 4. Cryptographic Chained Audit Ledger (`/audit`)
- **Tamper Evidence**: Every forensic query, case creation, and notice sign-off is linked via `previous_event_hash` to the `GENESIS_0000...` root block.
- **Integrity Validation**: One-click verification validating zero broken hash pointers.

---

## 🧪 Build & Typecheck Verification
```powershell
# Run TypeScript Typecheck (0 errors)
npm run typecheck

# Run Next.js Production Build (0 errors, 16 static routes)
npm run build
```
