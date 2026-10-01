# scripts/update_product_spec.py
import re

doc_path = "docs/PRODUCT_SPECIFICATION.md"
with open(doc_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Section 2 in Part 1
old_sec2 = """1. **Traces the money** \u2014 follows every transaction hop across up to 6 blockchain hops
2. **Identifies the exchange** \u2014 finds which registered crypto exchange (VASP) is the terminal destination
3. **Flags every suspicious wallet along the way** \u2014 mule accounts, layering wallets, mixer entry points"""

new_sec2 = """1. **Traces the money** \u2014 follows forward and backward (fan-in upstream) transaction hops across up to 6 hops on Ethereum, Tron, Bitcoin, Polygon, and BSC/BNB
2. **Identifies the exchange** \u2014 finds which registered crypto exchange (VASP) is the nearest direct deposit destination (hop-order traversal), ranking multiple candidates on ambiguous matches
3. **Flags every suspicious wallet along the way** \u2014 mule networks, peeling chains, consolidation funnels, rapid hops, DEX swaps, and mixer boundaries"""

assert old_sec2 in content, "Could not find old_sec2"
content = content.replace(old_sec2, new_sec2)

# 2. Update Technical Reader Steps 2, 3, 4
old_steps = """**Step 2 \u2014 Bounded Multi-Hop Tracing** (`POST /api/v1/trace`):
The `bounded_tracer` in `backend/tracing/trace_engine.py` performs a breadth-first traversal of on-chain transactions. It calls live blockchain APIs (Etherscan V2 for Ethereum/ERC-20, TronGrid for TRC-20 USDT, Blockstream for Bitcoin). Each hop is evaluated against `TraceConstraints` \u2014 a configurable depth limit, a mixer boundary halt flag, and a cross-chain bridge detection flag.

**Step 3 \u2014 VASP Attribution** (`backend/attribution/attribution_resolver.py`):
The `AttributionResolver` evaluates each terminal address against the curated VASP registry. It computes a confidence score using the `AdaptiveVASPScorer` \u2014 a 6-factor weighted formula: base confidence, FIU-IND registration bonus, exact address match, hop penalty, data freshness, and data completeness.

**Step 4 \u2014 Typology Detection** (`backend/typologies/`):
The `typology_engine.py` classifies the trace into known fraud patterns: `MULE_NETWORK`, `MIXER_BOUNDARY`, `RAPID_HOP`, `CROSS_CHAIN_BRIDGE`, `OFAC_SANCTION_HIT`, `PEEL_CHAIN`. The `mixer_registry.py` holds curated Tornado Cash pool addresses (0.1, 1, 10, 100 ETH pools on Ethereum and Arbitrum)."""

new_steps = """**Step 2 \u2014 Bounded Multi-Hop Tracing** (`POST /api/v1/trace` & `WS /ws/trace/{case_id}`):
The `bounded_tracer` in `backend/tracing/trace_engine.py` performs a breadth-first traversal of on-chain transactions. It supports forward, backward (fan-in upstream funding sources up to 2 hops), and bidirectional tracing across Ethereum, Tron, Bitcoin, Polygon, and BSC/BNB Chain (Chain ID 56). Calls route through `fetch_with_failover()` across primary/fallback RPCs protected by `ProviderCircuitBreaker` (threshold=3, cooldown=60s) and a 5-tier `TTLCache`. Intercepts decentralized exchange routing via `DEX_REGISTRY` (Uniswap, PancakeSwap, Curve, SunSwap), tagging swap pools as `defi_swap` and resetting tracked asset quantities while continuing BFS traversal. Real-time progress is streamed via WebSocket (`WS /ws/trace/{case_id}`).

**Step 3 \u2014 VASP Attribution** (`backend/attribution/attribution_resolver.py`):
The `AttributionResolver` walks BFS hops in traversal order and evaluates each address against the expanded 15+ VASP registry (10 FIU-registered Indian exchanges + 5 global exchanges). It resolves the nearest VASP deposit first. When ambiguous or multiple cluster matches occur, `score_all_candidates()` returns a ranked list of candidates with calibrated confidence scores (hop decay penalty capped at -0.20, with a `deep_trace_partial` band for scores 40\u201359 across deep paths).

**Step 4 \u2014 Typology Detection** (`backend/typologies/`):
The `typology_engine.py` classifies the trace into verified typology rules: `MULE_NETWORK` (deterministic behavioral heuristics without synthetic fallbacks), `MIXER_BOUNDARY` (Tornado Cash pool halting and pre-mixer targeting), `RAPID_HOP` (calibrated to chain-specific block times: ETH 10,800s, TRON 3,600s, BTC 86,400s, POLYGON 1,800s, BSC 3,600s), `CROSS_CHAIN_BRIDGE`, `OFAC_SANCTION_HIT`, `PEEL_CHAIN` (real algorithm verifying 0.5%\u20135% per-hop reduction across >=3 unique addresses), `CONSOLIDATION_FUNNEL` (detecting 2+ branches merging into an aggregation wallet before a VASP deposit, tracking `convergence_nodes`), and `REPEAT_OFFENDER_WALLET` (cross-case syndicate detection via `wallet_index`)."""

assert old_steps in content, "Could not find old_steps"
content = content.replace(old_steps, new_steps)

# 3. Update Step 6
old_step6 = """**Step 6 \u2014 OFAC Sanctions Screening**:
Every traversed address is checked against the US Treasury OFAC Specially Designated Nationals list. An OFAC hit applies a +45 risk score bump, triggering `CRITICAL` risk level and a mandatory red alert banner."""

new_step6 = """**Step 6 \u2014 OFAC Sanctions Screening** (`engine/ofac_sanctions.py`):
Every traversed address is screened against the US Treasury OFAC Specially Designated Nationals (SDN) list with exact address hashing and fuzzy entity-name matching (`difflib.SequenceMatcher`, threshold=0.85, supporting batch processing via `bulk_fuzzy_screen_entities()`). An OFAC hit applies a +45 risk score bump, forces risk level to `CRITICAL`, halts traversal at the sanctioned node, sets attribution to `UNRESOLVED`, and triggers automated alert dispatch (`AlertDispatcher`)."""

assert old_step6 in content, "Could not find old_step6"
content = content.replace(old_step6, new_step6)

# 4. Update Section 5 Capabilities
old_51 = """### 5.1 Multi-Chain Tracing
The system traces transactions across Ethereum (ERC-20 tokens including USDT, USDC), TRON (TRC-20 USDT \u2014 heavily used in India-linked scam flows), Bitcoin, and Polygon. Live blockchain data is fetched from public APIs. When APIs are unavailable, the system falls back to algorithmically generated simulation and clearly labels the output as `SIMULATED` \u2014 investigators always know which data is real."""

new_51 = """### 5.1 Multi-Chain Tracing
The system traces transactions across Ethereum (ERC-20 tokens including USDT, USDC), TRON (TRC-20 USDT \u2014 heavily used in India-linked scam flows), Bitcoin, Polygon, and BSC/BNB Chain (Chain ID 56, Ankr public RPC, with EVM 0x address disambiguation vs Ethereum). Live blockchain data is fetched through resilient provider cascades (`fetch_with_failover()`) with circuit breakers and a 5-tier TTL cache. When APIs are unavailable, the system handles failover gracefully without fabricating evidence."""

assert old_51 in content, "Could not find old_51"
content = content.replace(old_51, new_51)

old_53 = """### 5.3 Exchange Wallet Clustering
The VASP registry contains over 15 Indian and international exchanges with their known deposit address clusters, FIU-IND registration status, and nodal officer contact information. Attribution scores reflect cluster membership, direct address matches, and regulatory registration."""

new_53 = """### 5.3 Exchange Wallet Clustering & Nearest-VASP Attribution
The VASP registry contains 10 Indian exchanges (Mudrex, BitBNS, Giottus, Unocoin, Pi42, CoinSwitch, BuyUcoin, KoinBX, SunCrypto, Flitpay) and 5 global exchanges (OKX, Bitget, MEXC, HTX, Gate.io) with their known deposit address clusters, FIU-IND registration status, geographic coordinates (ISO country, lat/long, FATF status via `GET /api/v1/vasps/geo`), and nodal officer contact information. The engine walks BFS hops in traversal order to attribute the nearest exchange receiving direct deposits, and ranks multiple candidates via `score_all_candidates()` on ambiguous matches."""

assert old_53 in content, "Could not find old_53"
content = content.replace(old_53, new_53)

old_54 = """### 5.4 Statutory Notice Generation (Maker/Checker)
The platform implements a two-officer approval workflow for Section 91 BNSS notices. An Investigator drafts the notice (auto-populated with VASP details, transaction hashes, and case data). A Supervisor reviews and cryptographically approves or rejects it. Approved notices carry a digital signature traceable to the authorizing officer."""

new_54 = """### 5.4 Statutory Notice Generation & FIU-IND Compliance (Maker/Checker)
The platform implements a two-officer approval workflow for Section 91 BNSS notices and FIU-IND compliance auto-drafts under PMLA Section 12A. Notices auto-populate the VASP nodal officer email (`nodal_officer_email` from `VASP_REGISTRY`), statutory Section 12A obligations, a **MANDATORY REPORTING ENTITY** badge, transaction hashes, and case metadata. An Investigator drafts the notice, and a Supervisor reviews and cryptographically approves or rejects it."""

assert old_54 in content, "Could not find old_54"
content = content.replace(old_54, new_54)

old_56 = """### 5.6 Court-Admissible Evidence Package
Every case generates: a deterministic PDF investigation dossier with fund-flow graph, hop table, attribution decomposition, and audit hashes (Section 65B compliant); a SHA-256 chained audit ledger covering all system actions; and a cryptographic evidence payload verifiable via the evidence integrity endpoint."""

new_56 = """### 5.6 Court-Admissible Evidence Package & INR/USD Dual Display
Every case generates: a deterministic PDF investigation dossier with fund-flow graph, hop table, attribution decomposition, and audit hashes (Section 65B compliant); dual currency reporting with `traced_value_usd` and `traced_value_inr` (at fixed 83.5 INR/USD conversion rate) at case root and per-hop (`amount_usd` and `amount_inr`); a color-coded Data Completeness KPI bar (green >=85%, amber 65\u201384%, red <65%) exposing `earliest_transaction_date`; a SHA-256 chained audit ledger covering all system actions; and a cryptographic evidence payload verifiable via the evidence integrity endpoint."""

assert old_56 in content, "Could not find old_56"
content = content.replace(old_56, new_56)

old_57 = """### 5.7 Recovery Urgency Calculator
A 4-factor scoring calculator estimates the operational urgency of fund recovery for each case, accounting for elapsed time since crime, transaction value, chain type, and VASP cooperation history. It outputs a color-coded urgency band and is explicit about ineligibility \u2014 cases involving confirmed mixer entry or below-threshold values display disclaimers rather than inflated estimates."""

new_57 = """### 5.7 Recovery Urgency Calculator & Fraud-Type Modifiers
A calibrated recovery calculator estimates the operational feasibility of fund recovery, accounting for elapsed time since crime, transaction value, chain type, VASP cooperation history, and fraud-type modifiers (TASK_BASED +5, RANSOMWARE -10, SEXTORTION -15, DARKNET -30, ORGANIZED_CRIME -10, INVESTMENT_SCAM/PHISHING 0). When elapsed time is unverifiable, it places the trace into an `insufficient_data` tier without fabricating false urgency (no hardcoded 2.5h fallback). Cases with mixer obstructions or below-threshold values display explicit disclaimers per PRD FR-016."""

assert old_57 in content, "Could not find old_57"
content = content.replace(old_57, new_57)

# 5. Scope
old_scope = "- Multi-hop on-chain traversal for Ethereum (ERC-20), TRON (TRC-20), Bitcoin, and Polygon"
new_scope = "- Multi-hop forward and fan-in backward on-chain traversal for Ethereum (ERC-20), TRON (TRC-20), Bitcoin, Polygon, and BSC/BNB Chain"
assert old_scope in content, "Could not find old_scope"
content = content.replace(old_scope, new_scope)

# 6. Section 8 API Surface
old_sec8_api = """### API Surface
The backend exposes 54 REST endpoints across 8 routers: AI Copilot, PDF Report, Intake, Tracing & Intelligence, Case Management, Statutory Notices, Audit & Evidence, and Authentication, plus WebSocket streaming at `/ws/trace/{case_id}`. Interactive documentation at `http://localhost:8765/docs`."""

new_sec8_api = """### API Surface
The backend exposes REST and WebSocket endpoints across 9 routers: AI Copilot, PDF Report, Intake, Tracing & Intelligence, Case Management, Statutory Notices, Audit & Evidence, System/Resilience, and WebSocket streaming. Key endpoints verified in source:
- `POST /api/v1/trace` \u2014 Execute forward, backward, or bidirectional multi-hop trace
- `WS  /ws/trace/{case_id}` \u2014 Real-time trace event stream (`HOP_COMPLETE`, `MIXER_BOUNDARY`, `VASP_IDENTIFIED`, `TYPOLOGY_DETECTED`, `TRACE_COMPLETE`)
- `GET  /api/v1/system/cache-stats` \u2014 Inspect 5-tier TTL cache hits, misses, and sizes
- `GET  /api/v1/cases/{case_id}/linked-cases` \u2014 Query cross-case syndicate links via `wallet_index`
- `GET  /api/v1/alerts` \u2014 Review automated alert dispatch events
- `GET  /api/v1/analytics/dashboard` \u2014 LEA analytics KPIs (total cases, critical alerts, top 5 VASPs, avg trace time)
- `GET  /api/v1/vasps/geo` \u2014 Retrieve VASP geographic coordinates, ISO country, and FATF greylist status
- `POST /api/v1/intake/ncrp/complaint` \u2014 Ingest complaint (accepts `INVESTIGATOR` role)
Interactive Swagger documentation available at `http://localhost:8765/docs`."""

assert old_sec8_api in content, "Could not find old_sec8_api"
content = content.replace(old_sec8_api, new_sec8_api)

# 7. FR-002
old_fr002 = """### FR-002 \u2014 Multi-Chain Address Handling

The system shall support:
- EVM addresses and token activity;
- Bitcoin UTXO addresses and transactions;
- Tron/TRC-20 activity.

Confirmed live backbone: Ethereum via ETH_RPC_PRIMARY_URL (WebSocket and HTTP), Polygon via POLYGON_RPC_PRIMARY_URL (WebSocket and HTTP), Tron via TRON_RPC_PRIMARY_URL (HTTP polling) plus TRON_GRID_API_KEY for TRC-20 event indexing, Etherscan via ETHERSCAN_API_KEY for historical address lookups and label enrichment only (never the live event path), Bitcoin via Mempool.space without authentication, and pricing via CoinGecko without authentication. Solana and additional cross-chain capabilities remain extensions only where data sources and evidence can be established."""

new_fr002 = """### FR-002 \u2014 Multi-Chain Address Handling

The system shall support:
- EVM addresses and token activity across Ethereum, Polygon, and BSC/BNB Chain;
- Bitcoin UTXO addresses and transactions;
- Tron/TRC-20 activity.

Confirmed live backbone: Ethereum via ETH_RPC_PRIMARY_URL (WebSocket and HTTP), Polygon via POLYGON_RPC_PRIMARY_URL (WebSocket and HTTP), BSC/BNB Chain via Chain ID 56 (Ankr public RPC, with EVM 0x address disambiguation vs Ethereum via tx receipt/RPC checks), Tron via TRON_RPC_PRIMARY_URL (HTTP polling) plus TRON_GRID_API_KEY for TRC-20 event indexing, Etherscan via ETHERSCAN_API_KEY for historical address lookups and label enrichment only (never the live event path), Bitcoin via Mempool.space without authentication, and pricing via CoinGecko without authentication. Solana remains planned for future extension."""

assert old_fr002 in content, "Could not find old_fr002"
content = content.replace(old_fr002, new_fr002)

# 8. FR-005
old_fr005 = """### FR-005 \u2014 Bounded Tracing

Tracing shall support configurable:
- maximum hops;
- time window;
- minimum value;
- maximum outflows;
- maximum nodes;
- timeout.

The system shall prevent uncontrolled graph expansion and expose the applied limits."""

new_fr005 = """### FR-005 \u2014 Bounded Tracing & Traversal Controls

Tracing shall support configurable:
- `direction`: `TraceDirection.FORWARD`, `TraceDirection.BACKWARD` (fan-in upstream funding sources up to 2 hops), or `TraceDirection.BIDIRECTIONAL`;
- maximum hops (forward depth limit);
- time window (with a 10% penalty per truncation and `earliest_transaction_date` exposed);
- minimum value;
- maximum outflows;
- maximum nodes;
- timeout (with graceful degradation to `PARTIAL_COMPLETE` and 15% deduct if len(hops)>=2);
- decentralized exchange interception via `DEX_REGISTRY`: tagging swap pools as `defi_swap`, emitting `DEFI_SWAP` edges, resetting asset quantity, and continuing BFS past the router.

The system shall prevent uncontrolled graph expansion and expose all applied limits and truncation flags."""

assert old_fr005 in content, "Could not find old_fr005"
content = content.replace(old_fr005, new_fr005)

# 9. FR-006
old_fr006 = """### FR-006 \u2014 Typology Detection

The system shall detect, explain, and version findings for:
- peel chains;
- fan-in;
- fan-out;
- rapid-hop layering;
- consolidation;
- mixer exposure;
- **`MIXER_BOUNDARY_CLUSTER_LEAD`**;
- DEX boundary;
- bridge-mediated cross-chain movement;
- **`MULE_NETWORK`**."""

new_fr006 = """### FR-006 \u2014 Typology Detection

The system shall detect, explain, and version findings for:
- **`PEEL_CHAIN`**: Real implementation verifying 0.5%\u20135% per-hop reduction across >=3 consecutive unique addresses (not a stub);
- **`CONSOLIDATION_FUNNEL`**: Detects when 2+ independent branches merge into an aggregation wallet before a VASP deposit, tracking `convergence_nodes`;
- **`MULE_NETWORK`**: Detects multi-victim mule fan-in patterns with real timestamp calculations (synthetic 600s fallback eliminated);
- **`RAPID_HOP`**: Evaluated against chain-specific block times: ETH 10,800s (3h), TRON 3,600s (1h), BTC 86,400s (24h), POLYGON 1,800s (30m), BSC 3,600s (1h);
- **`REPEAT_OFFENDER_WALLET`**: Cross-case syndicate wallet matching via SQLite `wallet_index`;
- **`MIXER_BOUNDARY`** & **`MIXER_BOUNDARY_CLUSTER_LEAD`**: Tornado Cash pool detection and pre-mixer targeting;
- **`DEFI_OBFUSCATION`**: Emitted upon encountering registered DEX routers;
- **`CROSS_CHAIN_BRIDGE`**: Distinguishes PROVEN smart contract logs from HEURISTIC correlations."""

assert old_fr006 in content, "Could not find old_fr006"
content = content.replace(old_fr006, new_fr006)

# 10. FR-007
old_fr007 = """### FR-007 \u2014 VASP Clustering and Attribution

The system shall distinguish:
- labelled;
- inferred;
- unresolved.

The system shall not present inferred clustering as confirmed ownership. Attribution confidence shall be separate from risk category.

The base attribution score uses the six evidence components and starting weights: label `0.35`, directness `0.25`, retained `0.15`, finality `0.10`, temporal `0.10`, corroboration `0.05`. The starting vector is a policy baseline, not a fixed final vector in all contexts."""

new_fr007 = """### FR-007 \u2014 Nearest-VASP Attribution & Multi-Candidate Scoring

The system resolves the **nearest VASP** receiving direct deposits by walking BFS hops in traversal order (not terminal address inference). It distinguishes:
- labelled;
- inferred;
- unresolved.

When funds hit a VASP deposit cluster, the branch terminates to eliminate internal exchange noise. When multiple cluster matches exist, `score_all_candidates()` returns a ranked list of candidate attributions sorted by confidence score descending.

The base attribution score uses the six evidence components and starting weights: label `0.35`, directness `0.25`, retained `0.15`, finality `0.10`, temporal `0.10`, corroboration `0.05`. Hop-decay penalties are capped at -0.20 (preventing excessive attenuation on deep traces), and candidates with scores 40\u201359 on deep paths are assigned to the `deep_trace_partial` confidence band."""

assert old_fr007 in content, "Could not find old_fr007"
content = content.replace(old_fr007, new_fr007)

# 11. FR-009
old_fr009 = """### FR-009 \u2014 Risk and Attribution

Risk scoring shall be explainable, versioned, and separately stored from attribution confidence. Every score must identify the rules, inputs, evidence references, and uncertainty flags used."""

new_fr009 = """### FR-009 \u2014 Risk Assessment & Compounding Model

Risk scoring shall be explainable, versioned, and separately stored from attribution confidence. The composite risk score incorporates:
- **Base Typology Risk**: Calculated from detected typology rules;
- **Fraud Amount Tiers**: >=$1.2M USD (+35), >=$120K USD (+25), >=$12K USD (+15), else 0;
- **Cross-Chain Layering**: 1 bridge (+10), 2+ bridges (+20), bridge + mixer (+30);
- **Offshore Unregistered VASP Penalty**: FIU status `UNREGISTERED` and country non-India (+15);
- **Cross-Rule Compounding**:
  - `MULE_NETWORK` + `RAPID_HOP` \u2192 +15 risk bonus;
  - `MULE_NETWORK` + `MIXER_BOUNDARY` \u2192 +10 risk bonus and forces risk level to `CRITICAL`;
  - `OFAC_SANCTION_HIT` + any other rule \u2192 forces immediate `CRITICAL` risk level and traversal halt;
- **Time Truncation**: 10% risk deduction per truncated window with `TIME_WINDOW_WARNING`;
- **Automated Dispatch**: Emits alerts via `AlertDispatcher` when `risk_category == CRITICAL` or `ofac_sanction_hit == True`."""

assert old_fr009 in content, "Could not find old_fr009"
content = content.replace(old_fr009, new_fr009)

# 12. FR-016
old_fr016 = """Use `value_ratio=min(1,traced/fraud)`, `time_urgency=max(.05,1-hours_since_incident/72)`, and `path_clarity=1/max(1,hop_count)`. Persist all components, score, `action_window_hours=max(0,72-hours_since_incident)`, and RED/AMBER/GREEN tiers with explicit boundaries: RED `<0.20`, AMBER `>=0.20 and <=0.50`, GREEN `>0.50`. Display the primary label with component tooltip, source, disclaimer, and supervisor sorting by ascending action window."""

new_fr016 = """Use `value_ratio=min(1,traced/fraud)`, `time_urgency=max(.05,1-hours_since_incident/72)`, and `path_clarity=1/max(1,hop_count)`. Incorporate fraud-type recovery difficulty modifiers:
- `TASK_BASED`: +5%
- `RANSOMWARE`: -10%
- `SEXTORTION`: -15%
- `DARKNET`: -30%
- `ORGANIZED_CRIME`: -10%
- `INVESTMENT_SCAM` / `PHISHING`: 0%

When incident elapsed time cannot be verified from complaint records or on-chain timestamps, the system returns an `insufficient_data` tier with no fabricated false urgency (no 2.5h hardcoded fallback). Persist all components, score, `action_window_hours=max(0,72-hours_since_incident)`, and RED/AMBER/GREEN tiers with explicit boundaries: RED `<0.20`, AMBER `>=0.20 and <=0.50`, GREEN `>0.50`. Display the primary label with component tooltip, source, disclaimer, and supervisor sorting by ascending action window."""

assert old_fr016 in content, "Could not find old_fr016"
content = content.replace(old_fr016, new_fr016)

# 13. NFR-008 Deployment & Storage
old_nfr008 = """### NFR-008 \u2014 Deployment

- SQLite may be used for development/testing where supported.
- PostgreSQL compatibility must not be described as operationally verified unless PostgreSQL is actually exercised.
- Production deployment requires explicit environment, secret, observability, backup, and rollback validation."""

new_nfr008 = """### NFR-008 \u2014 Deployment & Storage Selection

- **SQLite System of Record**: SQLite (`sahyog.db` and `intelligence.db`) with `canonical_db` connection management is verified and adequate for single-investigator operations.
- **PostgreSQL Migration**: **SKIPPED**. (SQLite adequate for single-investigator demo; opt-in via REDIS_URL env var for Redis cache upgrade).
- **In-Memory / Redis Caching**: Multi-tier caching is implemented via in-process `TTLCache` with transparent byte-identical guarantees, with optional Redis upgrade via `REDIS_URL`."""

assert old_nfr008 in content, "Could not find old_nfr008"
content = content.replace(old_nfr008, new_nfr008)

# 14. Screen Catalog Table (Part 3)
old_table_row = """| **Start Multi-Hop Trace** | `/investigations` | `/api/v1/trace` | `POST` | `{"address": "...", "chain": "...", "max_hops": N, "mode": "LIVE"\\|"DEMO"}` | Any Authenticated |"""

new_table_rows = """| **Start Multi-Hop Trace** | `/investigations` | `/api/v1/trace` | `POST` | `{"address": "...", "chain": "...", "max_hops": N, "mode": "LIVE"\\|"DEMO"}` | Any Authenticated |
| **Inspect Cache Stats** | `/admin`, `/system` | `/api/v1/system/cache-stats` | `GET` | N/A | Any Authenticated |
| **Query Linked Cases** | `/investigations`, `/cases` | `/api/v1/cases/{id}/linked-cases` | `GET` | N/A | Any Authenticated |
| **List Automated Alerts** | `/alerts`, `/dashboard` | `/api/v1/alerts` | `GET` | N/A | Any Authenticated |
| **LEA Analytics Dashboard** | `/dashboard`, `/analytics` | `/api/v1/analytics/dashboard` | `GET` | N/A | Any Authenticated |
| **Query VASP Geo Locations**| `/map`, `/vasps` | `/api/v1/vasps/geo` | `GET` | N/A | Any Authenticated |
| **Live WebSocket Stream** | `/investigations` | `/ws/trace/{case_id}` | `WS` | Handshake | Any Authenticated |"""

assert old_table_row in content, "Could not find old_table_row"
content = content.replace(old_table_row, new_table_rows)

with open(doc_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: PRODUCT_SPECIFICATION.md successfully updated!")
