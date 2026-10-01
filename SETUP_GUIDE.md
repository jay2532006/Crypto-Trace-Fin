# TraceX Sahyog — Setup Guide
### Complete Local Development & Evaluation Setup
**Platform: TraceX Sahyog v2.0 | SIH 26183**

---

## Prerequisites

Before starting, ensure the following are installed on your machine:

| Requirement | Minimum Version | Check Command |
|---|---|---|
| **Python** | 3.10+ (3.11, 3.12, 3.13 supported) | `python --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Git** | Any recent version | `git --version` |

> **Tested on:** Python 3.13.14, Node.js v24.13.0, npm 11.6.2, Windows 11

---

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd tracex-sahyog-main
```

---

## 2. Backend Setup

### 2.1 Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 2.2 Install All Backend Dependencies

```bash
# Install production + development dependencies
pip install -r requirements-dev.txt
```

This installs:
- **FastAPI + Uvicorn** — API server
- **PyJWT + bcrypt** — Authentication & RBAC
- **ReportLab + Matplotlib** — Deterministic PDF generation
- **Groq + google-generativeai** — AI Copilot providers
- **pytest + httpx + pytest-asyncio** — Test runner
- **networkx, requests, pydantic, python-dotenv** — Core utilities

### 2.3 Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Windows
copy .env.example .env   # if .env.example exists

# Or create manually
```

Edit `.env` with the following:

```env
# ── Core Security ──────────────────────────────────────────
SECRET_KEY=your-strong-secret-key-minimum-32-chars
APP_ENV=development       # Set to "production" for prod (enforces SECRET_KEY check)
APP_MODE=demo             # "demo" uses fixtures; "live" hits real APIs

# ── Blockchain API Keys (optional but recommended for LIVE mode) ──
ETHERSCAN_API_KEY=your-etherscan-v2-api-key
TRONGRID_API_KEY=your-trongrid-api-key
# Bitcoin (Blockstream) requires no API key

# ── AI Copilot Providers (at least one recommended) ──
GROQ_API_KEY=your-groq-api-key         # Primary provider (fastest)
GEMINI_API_KEY=your-gemini-api-key     # Secondary provider fallback

# ── CORS & Network ─────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:3000   # Frontend URL

# ── Feature Flags ──────────────────────────────────────────
TRACE_STOP_AT_MIXER=true      # Halt trace at mixer boundary (recommended: true)
TRACE_CROSS_CHAIN=true        # Enable cross-chain bridge detection
TRACE_OFAC_SANCTIONS=true     # Enable OFAC SDN screening
```

> **Note on API Keys:** The system works without API keys in `APP_MODE=demo`. LIVE mode benefits from Etherscan and TronGrid keys to avoid rate limits. The AI Copilot falls back to rule-based recommendations if no AI provider key is set.

### 2.4 Initialize the Database

The SQLite database initializes automatically on first server start. No manual migration step is required — the `backend/db/database.py` schema manager handles this.

### 2.5 Start the Backend Server

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8765 --reload
```

You should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8765
```

**Verify it's running:**
```bash
curl http://localhost:8765/
```
Expected response:
```json
{
  "service": "TraceX Sahyog Blockchain Intelligence API",
  "version": "2.0.0",
  "status": "operational",
  "frontend": "http://localhost:3000",
  "docs": "/docs"
}
```

---

## 3. Frontend Setup

### 3.1 Install Node Dependencies

```bash
cd frontend
npm install
```

This installs: Next.js 14, React 18, Framer Motion, TailwindCSS, Cytoscape.js, Zustand, Recharts, Lucide Icons, Axios, React Query, and all type definitions.

### 3.2 Configure Frontend Environment

Create `frontend/.env.local`:

```env
# Backend API base URL
NEXT_PUBLIC_API_URL=http://localhost:8765
```

### 3.3 Start the Frontend Dev Server

```bash
# From the frontend directory
npm run dev

# Or from the project root
npm --prefix frontend run dev
```

The frontend starts at **http://localhost:3000**

---

## 4. Full System Verification

With both servers running, open **http://localhost:3000** in your browser.

You should land on the login page. Use these pre-seeded credentials:

| Username | Password | Role | Permissions |
|---|---|---|---|
| `investigator1` | `Password@123` | **INVESTIGATOR** | Create cases, run traces, draft notices, use Copilot |
| `supervisor1` | `Password@123` | **SUPERVISOR** | Approve/reject Section 91 notices, verify audit |
| `admin1` | `Password@123` | **ADMINISTRATOR** | System config, API key management |

---

## 5. Running the Test Suite

```bash
# Run all 129 backend tests across 18 test files
pytest backend/tests/ -v

# Run golden baseline non-regression tests (10 baseline fixtures)
pytest backend/tests/test_phase0_logic_fixes.py -v

# Run core logic resilience, detection gap, and accuracy suites
pytest backend/tests/test_phase1_resilience.py backend/tests/test_phase2_detection_gaps.py backend/tests/test_phase3_accuracy.py -v

# Run external boundary and WebSocket stream suites
pytest backend/tests/test_phase4_external_boundaries.py backend/tests/test_phase4_demo_polish.py backend/tests/test_phase5_polish.py -v

# Frontend type check (zero errors expected)
npm --prefix frontend run typecheck

# Production build verification
npm --prefix frontend run build
```

Expected output:
```
======================= 129 passed, 4 warnings in 7.17s =======================
```

---

## 6. Key Access URLs

| Page | URL | Description |
|---|---|---|
| **Home / Login** | http://localhost:3000 | Authentication portal |
| **Investigations Studio** | http://localhost:3000/investigations | Main tracing workspace — graph canvas, AI Copilot, Live Inspector |
| **Guided Demo Console** | http://localhost:3000/demo | 7-step evaluation walkthrough through all 6 demo scenarios |
| **Case Docket** | http://localhost:3000/cases | Registered investigation cases |
| **NCRP Intake** | http://localhost:3000/intake | Complaint ingestion with BIP-39 quarantine |
| **Recovery Urgency** | http://localhost:3000/recovery | 4-factor urgency calculator |
| **Section 91 Notices** | http://localhost:3000/legal-notices | Notice drafting and approval queue |
| **Audit Ledger** | http://localhost:3000/audit | SHA-256 chained tamper-evident audit log |
| **Provider Status** | http://localhost:3000/provider-status | Blockchain API health monitoring |
| **API Docs (Swagger)** | http://localhost:8765/docs | Interactive documentation for all 54 endpoints |
| **API Health** | http://localhost:8765/ | JSON health check |

---

## 7. Running the Demo Scenarios

Six pre-configured scenarios are available from the **Guided Demo Console** (`/demo`) or directly via the Investigations Studio. Load them by case ID:

| Case ID | What it demonstrates |
|---|---|
| `CR-2026-MULE-IND-01` | Mule network → WazirX attribution (TRON) |
| `CR-2026-MIXER-BOUND-02` | Tornado Cash boundary halt + mixer directive (ETH) |
| `CR-2026-BRIDGE-XCHAIN-03` | ETH → TRON cross-chain bridge → CoinDCX |
| `CR-2026-BRIDGE-XCHAIN-04` | Stargate LayerZero bridge → Polygon |
| `CR-2026-OFAC-SDN-05` | Lazarus Group OFAC SDN hit → CRITICAL risk |
| `CR-2026-MULE-FANIN-06` | 4-victim task scam consolidation → CoinDCX |

**To download a sample court-admissible PDF report:**
```
http://localhost:8765/api/v1/cases/CR-2026-MULE-IND-01/report.pdf
```

---

## 8. Environment Variable Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | `cryptotrace-lea-insecure-dev-secret-key-32charsmin` | JWT signing secret. **Must be changed in production.** |
| `APP_ENV` | No | `development` | Set to `production` to enforce security guard |
| `APP_MODE` | No | `demo` | `demo` uses fixtures; `live` hits real blockchain APIs |
| `ETHERSCAN_API_KEY` | No | — | Etherscan V2 key for Ethereum/ERC-20 live tracing |
| `TRONGRID_API_KEY` | No | — | TronGrid key for TRC-20 USDT live tracing |
| `GROQ_API_KEY` | No | — | Groq LLM API key for AI Copilot (primary) |
| `GEMINI_API_KEY` | No | — | Google Gemini API key for AI Copilot (fallback) |
| `ALLOWED_ORIGINS` | No | `*` | CORS allowed origins (comma-separated) |
| `TRACE_STOP_AT_MIXER` | No | `true` | Halt tracing at mixer boundary |
| `TRACE_CROSS_CHAIN` | No | `true` | Enable cross-chain bridge detection |
| `TRACE_OFAC_SANCTIONS` | No | `true` | Enable OFAC SDN screening |

---

## 9. Troubleshooting

### Backend won't start — "FATAL: Insecure default SECRET_KEY"
**Cause:** `APP_ENV=production` is set with the default secret key.  
**Fix:** Either set a strong `SECRET_KEY` in `.env`, or set `APP_ENV=development` for local testing.

### Port 8765 already in use
```bash
# Windows — find and kill the process
netstat -ano | findstr :8765
taskkill /PID <PID> /F

# Then restart
python -m uvicorn app:app --host 0.0.0.0 --port 8765
```

### Frontend cannot connect to backend (CORS error)
**Fix:** Ensure `ALLOWED_ORIGINS=http://localhost:3000` is set in `.env` and the backend has restarted after the change.

### "Module not found" errors in pytest
**Fix:** Run pytest from the project root, not from inside `backend/`:
```bash
# Correct
python -m pytest backend/tests -v

# Incorrect
cd backend && pytest tests/
```

### AI Copilot shows "Rule-Based Fallback" badge
**Cause:** No `GROQ_API_KEY` or `GEMINI_API_KEY` is set.  
**Fix:** Add at least one AI provider key to `.env`. The Copilot continues to function with rule-based recommendations — no crash.

### ReportLab PDF generation fails
**Fix:** Ensure `reportlab` and `matplotlib` are installed:
```bash
pip install reportlab>=4.0.0 matplotlib>=3.7.0
```

### Neo4j connection warning on startup
```
Schema initialization warning: Cannot resolve address ...neo4j.io:7687
```
**This is expected and non-fatal.** Neo4j is an optional graph database integration. The platform runs fully without it — all tracing and data uses SQLite.

---

## 10. Production Deployment Checklist

Before deploying to a production environment:

- [ ] Set a strong `SECRET_KEY` (minimum 32 characters, randomly generated)
- [ ] Set `APP_ENV=production` in environment
- [ ] Set `ALLOWED_ORIGINS` to your actual frontend domain (not `*`)
- [ ] Configure real `ETHERSCAN_API_KEY` and `TRONGRID_API_KEY`
- [ ] Configure at least one AI provider key (`GROQ_API_KEY` or `GEMINI_API_KEY`)
- [ ] Place SQLite `data/sahyog.db` on a persistent volume
- [ ] Run the full test suite and confirm 51/51 pass: `python -m pytest backend/tests -v`
- [ ] Run production frontend build and confirm 0 errors: `npm --prefix frontend run build`
- [ ] Serve frontend via `npm run start` (or deploy to Vercel/Cloudflare)
- [ ] Run backend via `gunicorn` with `uvicorn` workers for multi-process production serving

---

*TraceX Sahyog v2.0 | Backend: FastAPI + Uvicorn | Frontend: Next.js 14 + Framer Motion*
