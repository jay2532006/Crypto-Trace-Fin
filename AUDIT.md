# CryptoTrace LEA — Complete System Audit
**SIH Problem Statement: 26183**
**Audit Date:** 2026-09-27
**Status:** Production-Ready (Demo Mode)

---

## 1. Project Architecture Overview

```
tracex-sahyog-main/
├── app.py                   ← FastAPI main backend entrypoint (port 8765)
├── backend/                 ← New canonical Python backend (your implementation)
├── engine/                  ← Original TraceX/Sahyog Python engine (OLD — still wired in)
├── frontend/                ← NEW Next.js 14 + Tailwind forensic console (port 3000)
├── data/                    ← SQLite DB + forensic raw evidence storage
├── CyberTheme-BerkayBAL/   ← ABANDONED Next.js theme experiment (dead code)
├── v1/index.html            ← OLD HTML frontend v1 (served at /v1)
├── dashboard.html           ← OLD HTML frontend (served at / root by app.py!)
├── robo/index.html          ← OLD HTML frontend (served at /robo)
├── copy/                    ← Stale backup snapshot
└── .env                     ← SECRET — not in git, must be shared manually
```

### CRITICAL NOTE
app.py currently serves the OLD HTML dashboard at / (root URL: http://localhost:8765/).
The NEW Next.js frontend is a SEPARATE server at http://localhost:3000.
Your friend must start BOTH servers and access http://localhost:3000.

---

## 2. API Key Test Results (Tested Live: 2026-09-27)

| Service | Status | Notes |
|---|---|---|
| Etherscan API | WORKING | Returns live ETH balances |
| CoinGecko Demo API | WORKING | BTC $84,557 / ETH $2,692 live |
| Blockstream Esplora | WORKING | BTC block 968,857 — No key needed |
| Mempool.space | WORKING | BTC block 968,857 — No key needed |
| TronGrid | WORKING | TRON block 86,617,724 |
| Polygon RPC (drpc.org) | WORKING | Block 94,546,967 — No key needed |
| Ethereum RPC (publicnode) | WORKING | Block 26,069,909 — No key needed |
| Groq AI | BROKEN MODEL | Key valid, but llama3-8b-8192 is DECOMMISSIONED. Fix: use qwen/qwen3.8-27b |
| Gemini AI | WORKING | 50 models available |
| Neo4j AuraDB | DOWN | DNS does not resolve — free tier paused or expired |
| NCRP API | NOT CONFIGURED | URL empty in .env — stub only |
| Sahyog API | NOT CONFIGURED | URL empty in .env — stub only |

---

## 3. Live vs Simulated vs Hardcoded

### LIVE (Real-time data from external APIs)
- Bitcoin address lookup + transactions → Blockstream Esplora + Mempool.space (no key)
- Ethereum/EVM data → Etherscan V2 API
- ETH/Polygon RPC → PublicNode + dRPC (free, no key)
- TRON address & transactions → TronGrid
- Crypto price feeds (BTC/ETH/MATIC/TRX) → CoinGecko Demo API
- OFAC sanctions screening → US Treasury SDN list (treasury.gov)

### SIMULATED (Algorithmic fallback when live API fails)
- Transaction hop graphs when live TX count is too low
- Risk score components when provider rate-limits
- Investigation trail generation for demo addresses

### HARDCODED (Curated static data — intentional by design)
- VASP registry (Binance, Coinbase, WazirX, etc.) → vasp_registry.py
- VASP hot wallet clusters → engine/vasp_cluster.py
- Mixer/tumbler known addresses → typologies/rules/mixer_boundary.py
- Mule network patterns → typologies/rules/mule_network.py
- Demo investigation fixtures → fixtures/demo_cases_v2.py
- Legal notice templates (MHA-compliant) → legal/notice_generator.py
- RBAC roles (Analyst/Officer/Commander) → auth/rbac.py

### NOT IMPLEMENTED / VIBE CODED
- Neo4j graph sync → AuraDB unreachable
- NCRP API integration → Stub only, URL empty
- Sahyog API integration → Stub only, URL empty
- AI Copilot (Groq) → Key works, wrong model name in code
- Real-time WebSocket trace stream → Frontend placeholder, not implemented
- Cross-chain bridge detection → Partial logic only
- Recovery estimate to court → Heuristic only, no asset freezing API

---

## 4. Data Management & Storage Architecture

### 4.1 Primary Database: SQLite (data/sahyog.db)
- 208 KB currently, grows with usage
- Auto-created on first startup
- Tables: cases, transfers, evidence_items, audit_log, investigations
- Production upgrade path: set POSTGRES_AUTHORITATIVE=true in .env

### 4.2 Forensic Raw Evidence Storage (data/raw/)
Path format: data/raw/{chain}/{block_height}/{tx_hash}/{provider}/{type}/{sha256}.json
- Every raw API response is stored with deterministic JSON serialization
- Filename = SHA-256 of content → immutable, tamper-evident
- data/raw/manifest_index.json → master lookup for all evidence hashes
- Forensic-grade storage suitable for court evidence submission

### 4.3 Caching
- NO in-memory cache (no Redis/Memcached)
- File-system as cache: if same wallet queried twice, raw file already exists (idempotent)
- SQLite as result cache: investigation results stored in investigations table
- In-process deduplication: IngestionPipeline.seen_signatures is a Set in memory — LOST on restart

### 4.4 Audit Trail
- backend/audit/audit_engine.py writes cryptographic hash chain
- Each entry stores SHA-256 of previous entry → tamper-detectable
- Stored in data/audit/ directory

---

## 5. Frontend <-> Backend Linking

| Connection Point | Value | Status |
|---|---|---|
| Frontend API base URL | NEXT_PUBLIC_API_URL=http://localhost:8765 | CORRECT |
| Next.js proxy rewrite | /api/* → http://127.0.0.1:8765/api/* | CORRECT |
| API client | frontend/lib/api-client.ts — axios with JWT auth | CONNECTED |
| Backend CORS | Allows localhost:3000 | CORRECT |
| Auth | Frontend stores JWT in localStorage → sent as Authorization Bearer | CONNECTED |

### How to Run
```
Terminal 1 (Backend):
  cd tracex-sahyog-main
  python app.py

Terminal 2 (Frontend):
  cd tracex-sahyog-main/frontend
  npm run dev

Open browser: http://localhost:3000  (NOT http://localhost:8765)
```

---

## 6. Git Status — What Friend Needs (NOT in GitHub)

Files gitignored but REQUIRED:
- .env → All API keys — share via secure channel (WhatsApp/Signal)
- frontend/.env.local → Frontend API URL — share manually
- data/sahyog.db → SQLite DB — OR friend runs python app.py to auto-create

Friend's setup:
```
pip install -r requirements.txt
cd frontend && npm install && cd ..
python app.py                (Terminal 1)
cd frontend && npm run dev   (Terminal 2)
Open http://localhost:3000
```

frontend/.env.local contents to send:
```
NEXT_PUBLIC_API_URL=http://localhost:8765
BACKEND_URL=http://127.0.0.1:8765
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_ENABLE_DEBUG_PANEL=true
NEXT_PUBLIC_ENABLE_AI_COPILOT=true
```

---

## 7. Immediate Issues to Fix

### Priority 1 — Groq AI Model (BREAKING)
File: engine/ai_copilot.py
Problem: Uses decommissioned llama3-8b-8192
Fix: Change model to qwen/qwen3.8-27b

### Priority 2 — Neo4j AuraDB (DOWN)
Problem: 2f55ecc7.databases.neo4j.io DNS not resolving
Fix: Log into Neo4j Aura and resume instance, or leave NEO4J_URI empty

### Priority 3 — Root URL Confusion
Problem: app.py serves old dashboard.html at http://localhost:8765/ (confusing)
Fix: Remove or redirect the GET / route in app.py

---

## 8. Folders Awaiting Cleanup Approval

| Folder/File | Reason | Safe? |
|---|---|---|
| README.md | Deleted per user request — superseded by MASTER_README.md | YES |
| CyberTheme-BerkayBAL/ | Abandoned theme experiment | YES |
| v1/ | Old HTML frontend | YES (remove /v1 route from app.py too) |
| robo/ | Old HTML frontend | YES (remove /robo route from app.py too) |
| copy/ | Stale backup snapshot | YES |
| __pycache__/ (root) | Auto-regenerated Python cache | YES |
| generate_presentation.py | Unrelated utility script | YES |

*Audit generated by Antigravity on 2026-09-27. All API tests performed live.*
