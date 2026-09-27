# CryptoTrace LEA — Complete System & Live Data Flow
**SIH 26183 | Technical Architecture Reference**
**Last Updated:** 2026-09-27

---

## The Big Picture

```
Browser (localhost:3000)
    │
    ▼
Next.js Frontend  ──── api-client.ts (axios) ────▶  FastAPI Backend (app.py, port 8765)
                                                              │
                              ┌───────────────────────────────┤
                              │                               │
                         engine/ (OLD)               backend/ (NEW)
                         graph_tracer.py              tracing/trace_engine.py
                         real_api.py                  adapters/
                              │                               │
                    ┌─────────┘               ┌──────────────┤
                    │                         │              │
              Blockstream              EVMAdapter      BitcoinAdapter
              Etherscan                TronAdapter
              TronGrid
              CoinGecko
                    │                         │
                    └─────────────────────────┘
                                  │
                            Live Blockchain APIs
                         (Bitcoin / ETH / Polygon / TRON)
```

---

## Step 1 — User Triggers a Trace

The investigator opens `http://localhost:3000`, logs in (JWT token stored in browser
`localStorage`), then submits a wallet address from the Investigations page.

The frontend calls:
```
POST http://localhost:3000/api/v1/trace
```

`next.config.mjs` **rewrites** this transparently to `http://127.0.0.1:8765/api/v1/trace`
(the backend). The JWT token is automatically attached via the axios interceptor in
`frontend/lib/api-client.ts`.

---

## Step 2 — Backend Receives the Request

`app.py` routes it to `backend/api/trace_routes.py → execute_trace()`.

The request body:
```json
{
  "address": "0xABC...",
  "chain": "ETH",
  "mode": "DEMO",
  "max_hops": 5
}
```

**`mode` is the most critical field:**

| Mode | Behaviour |
|------|-----------|
| `DEMO` | Uses simulated/fixture data. No live API calls. Deterministic — same address always gives same result. **This is the current default.** |
| `LIVE` | Makes real HTTP calls to Blockstream / Etherscan / TronGrid APIs and traverses the real blockchain. |

---

## Step 3 — The Trace Engine (BoundedTracer)

**File:** `backend/tracing/trace_engine.py → BoundedTracer.trace()`

### IF mode = LIVE (Real Data Path)

```
BoundedTracer
    └──▶ ProviderManager.fetch_transfers(address, chain)
              │
              ├── chain = ETH / POLYGON  →  EVMAdapter
              │       └── Etherscan V2 API
              │           GET api.etherscan.io/v2/api?chainid=1&module=account
              │                &action=txlist&address={addr}&offset=50
              │           Raw JSON stored → data/raw/eth/{block}/{txhash}/etherscan_v2/txlist/{sha256}.json
              │
              ├── chain = BTC  →  BitcoinAdapter
              │       └── Blockstream Esplora API (No key needed)
              │           GET blockstream.info/api/address/{addr}/txs
              │
              └── chain = TRON  →  TronAdapter
                      └── TronGrid API
                          GET api.trongrid.io/v1/accounts/{addr}/transactions
```

It performs **BFS (Breadth-First Search)**:
- Starts at the suspect wallet
- Gets all outgoing transfers
- Visits each recipient wallet — up to `max_hops = 5` levels deep
- Stops early if `max_nodes = 1000` or `timeout = 60s` is reached

### IF mode = DEMO (Default — What Currently Runs)

No external API is called for the hop graph. Instead, a **fixed 4-hop peel chain**
is generated deterministically from the input address:

```python
mule_wallets = [
    start_address,
    "0x71c8fb9284285741829e05e55099e0344d9f1091",
    "0x81c8fb9284285741829e05e55099e0344d9f1092",
    "0x91d9ef53912185741829e05e55099e0344d9f1093",
    "0x28c6c06298d514db089934071355e5743bf21d60",  # WazirX / Binance Cluster
]
```

Transaction hashes in DEMO mode are `"0xsimulated_tx_hash_1"`, `"_2"`, etc.
Same wallet address → always same graph output.

---

## Step 4 — Price Feed (CoinGecko — Always Live)

Runs **in parallel** with every trace regardless of mode.

**File:** `engine/price_feed.py`

```
GET api.coingecko.com/api/v3/simple/price
    ?ids=bitcoin,ethereum,solana,tron,tether,binancecoin,matic-network
    &vs_currencies=usd,inr
```

- Results cached **in-memory** for **5 minutes** (`CACHE_TTL = 300` seconds)
- On cache hit: returns immediately, no API call
- On cache miss or expiry: fresh API call, updates cache
- If API fails: falls back to hardcoded defaults:
  - BTC = $81,131 / ₹76,64,859
  - ETH = $2,525 / ₹2,38,568
  - USDT = $1.00 / ₹94.46
- Used to convert satoshis / wei / sun → USD and INR in every response

---

## Step 5 — Intelligence Layer (4 Modules, Run Sequentially)

After hops are collected (live or demo), 4 intelligence modules run on the result:

### 5a. Typology Engine
**File:** `backend/typologies/typology_engine.py`

Runs 4 rules against the hop graph:

| Rule | Detects |
|------|---------|
| `mule_network_rule` | Rapid fan-out — one wallet sending to many recipients |
| `mixer_boundary_rule` | Hops through known mixer/tumbler wallet addresses |
| `peel_chain_rule` | Linear chain where each hop sends slightly less (gas peel) |
| `rapid_hop_rule` | Multiple hops occurring within 24 hours |

Each rule returns a `PatternFinding` with:
- `typology_name` (e.g., `PEEL_CHAIN`)
- `confidence_score` (0.0–1.0)
- `severity` (LOW / MEDIUM / HIGH / CRITICAL)
- `reasoning` (plain-English explanation for the investigator)

---

### 5b. AdaptiveVASPScorer — The Core Innovation
**File:** `backend/attribution/adaptive_vasp_scorer.py`

Executes a **6-step adaptive scoring sequence** per PRD mandate:

```
Step 1: Load versioned policy (policy_v1_india_kyc)  → base weight = 0.50
Step 2: Apply SINGLE_HOP override
        (if destination IS a known VASP hot wallet → score jumps immediately)
Step 3: Apply contextual modifiers alphabetically
        - mixer_detected?   → penalty
        - hop_count > 3?    → penalty
        - data_completeness_pct < 80? → penalty
        - exact_wallet_match? → bonus
Step 4: Resolve conflicting modifiers conservatively (take the penalty)
Step 5: Clamp all weights to range [0.01, 0.80]
Step 6: Renormalize weights to sum exactly 1.0
```

Output: `AttributionScore` containing:
- `vasp_name` — which exchange (e.g., WazirX, Binance, Coinbase)
- `score` — 0 to 100
- `label_type` — VERIFIED / INFERRED / UNRESOLVED
- `confidence_band` — CRITICAL / HIGH / MEDIUM / LOW
- `nodal_officer_email` — VASP's compliance contact
- `fiu_status` — REGISTERED / UNREGISTERED (Indian FIU-IND)
- `scoring_steps` — full explainable audit trace of every weight decision

The **VASP Registry** (Binance, WazirX, Coinbase, Kraken, etc.) is hardcoded in
`backend/attribution/vasp_registry.py` — intentional, forensic-grade curated data.

---

### 5c. Risk Assessment
**File:** `backend/assessment/risk_assessment.py`

Produces a risk score (0–100) based on:
- Typologies detected (mixer = +40 risk, peel chain = +25)
- Hop count (more hops = higher obfuscation risk)
- Attribution confidence (lower confidence = higher residual risk)
- Chain (TRON historically associated with USDT scams)

---

### 5d. Recovery Estimator
**File:** `backend/assessment/recovery_estimate.py`

Heuristic estimate of whether funds can be frozen. Inputs:
- Is the VASP FIU-IND registered? (registered = legally compellable in India)
- Elapsed hours since crime (< 72 hrs = highest freeze probability)
- Jurisdiction of VASP (India / Cayman / Seychelles etc.)
- Mixer involved? (mixer = funds likely non-recoverable)
- Hop count (> 5 hops = lower recovery chance)

> Note: This is a heuristic estimator only. Not connected to any real asset freezing API.

---

## Step 6 — Data Persistence (Two Stores)

### 6a. Forensic Raw Evidence Store — `data/raw/`

```
data/raw/
  {chain}/
    {block_number}/
      {tx_hash}/
        {provider}/
          {type}/
            {sha256_hash}.json   ← exact raw API response, immutable
```

- Every raw API response is stored with **deterministic JSON serialization** (sorted keys, compact)
- The filename IS the SHA-256 of the content — identical data produces identical filename
- **Idempotent**: querying the same wallet twice doesn't duplicate files
- `data/raw/manifest_index.json` — master lookup: `{sha256_hash} → relative_file_path`
- Court-admissible: investigators can prove the raw evidence has not been tampered with

### 6b. SQLite Database — `data/sahyog.db`

Tables written on every trace:

| Table | What's Stored |
|-------|---------------|
| `cases` | Case ID, wallet, chain, complainant, FIR number, status |
| `investigations` | Full trace result JSON, risk score, VASP name, confidence |
| `transfers` | Individual normalized blockchain transfer events |
| `evidence_items` | Evidence hashes with chain-of-custody metadata |
| `audit_events` | SHA-256 chained audit log (see Step 7) |

---

## Step 7 — Audit Chain (Tamper-Evident Log)

**File:** `backend/audit/audit_engine.py`

Every investigator action (login, trace, evidence export, notice generation) writes:

```
Row N:
  event_id       = UUID
  timestamp      = ISO 8601
  user_id        = "investigator1"
  action         = "trace:execute"
  resource_id    = "CR-2026-AUTO-ABC123"
  details_json   = { address, chain, mode, vasp_found, hops }
  previous_hash  = SHA-256 of Row N-1   ← CHAIN LINK
  event_hash     = SHA-256 of this entire row
```

If anyone edits Row 5, Row 6's `previous_hash` no longer matches → chain breaks →
tampering is instantly detectable. The `/api/v1/audit/verify-chain` endpoint checks this.

---

## Step 8 — Response Returns to Frontend

```
FastAPI backend
    └──▶ JSON response (hops, nodes, edges, typologies, attribution, risk, recovery)
            └──▶ Next.js proxy (port 3000)
                    └──▶ axios response interceptor (logs timing metrics)
                            └──▶ React state update
                                    └──▶ UI renders:
                                          - Fund flow graph (D3/Cytoscape nodes + edges)
                                          - Typology badges (PEEL_CHAIN, MULE_NETWORK)
                                          - Attribution card (VASP + score + scoring steps)
                                          - Risk score gauge (0-100)
                                          - Recovery probability estimate
```

---

## What is Live vs Simulated Right Now

```
LIVE (real API calls on every request):
  ✅ Bitcoin balance + transactions     → Blockstream Esplora (no key required)
  ✅ ETH / Polygon balance + txs        → Etherscan V2 API (key in .env)
  ✅ TRON balance + transactions        → TronGrid API (key in .env)
  ✅ Crypto prices (BTC/ETH/MATIC/TRX) → CoinGecko API (5-min in-memory cache)
  ✅ OFAC sanctions screening           → US Treasury SDN list (treasury.gov)

DEMO MODE (default — synthetic, no blockchain calls):
  ⚠️  Fund flow hop graph               → Hardcoded 4-wallet peel chain
  ⚠️  Transaction hashes                → "0xsimulated_tx_hash_1", "_2", "_3"...
  ⚠️  Amount values                     → Fixed $50,000 with small gas deductions

BROKEN / NOT IMPLEMENTED:
  ❌  Neo4j graph sync                  → AuraDB free tier expired (DNS down)
  ❌  AI Copilot (Groq)                 → Model fixed in code, needs backend restart
  ❌  NCRP / Sahyog APIs               → Stub only, URLs not configured in .env
  ❌  Real-time WebSocket stream        → Frontend placeholder, not wired to backend
  ❌  Cross-chain bridge detection      → Logic exists, limited real data
```

---

## Key Insight — How to Enable Real Tracing

The frontend currently sends `"mode": "DEMO"` by default in every trace request.

To see **actual on-chain data** in the fund flow graph, the frontend's trace request
body must be changed to `"mode": "LIVE"`.

**File to change:** `frontend/app/(workspace)/investigations/page.tsx`

Find where `apiClient.post("/api/v1/trace", {...})` is called and change:
```typescript
// Current (DEMO)
mode: "DEMO"

// Change to LIVE
mode: "LIVE"
```

In LIVE mode, the fund flow graph will show real transactions fetched from the blockchain.

---

## Summary: The Full Request Lifecycle

```
1. User submits wallet address at localhost:3000
2. axios → POST /api/v1/trace (JWT attached)
3. Next.js proxy rewrites → http://127.0.0.1:8765/api/v1/trace
4. FastAPI auth middleware validates JWT → extracts user role
5. BoundedTracer.trace() starts BFS
   ├─ LIVE: ProviderManager → EVMAdapter/BitcoinAdapter/TronAdapter → Live APIs
   └─ DEMO: Returns hardcoded 4-hop mule chain
6. CoinGecko price fetch (5-min cached)
7. Typology Engine scans hop graph (4 rules)
8. AdaptiveVASPScorer runs 6-step scoring
9. Risk Assessment produces 0-100 risk score
10. Recovery Estimator produces freeze probability
11. Raw API payload saved to data/raw/{chain}/.../{sha256}.json
12. Investigation record saved to data/sahyog.db
13. Audit event written with SHA-256 chain link
14. Full JSON response returned to frontend
15. React renders fund flow graph, typologies, attribution, risk
```

---

*Generated by Antigravity | Based on live code inspection of tracex-sahyog-main*
