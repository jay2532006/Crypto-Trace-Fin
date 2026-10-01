# scripts/update_architecture_doc.py
import re

doc_path = "docs/ARCHITECTURE_AND_CORE_LOGIC.md"
with open(doc_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update High-Level System Architecture Diagram to include 5-tier TTLCache, Failover Waterfall, BSC/BNB
old_diag = """       +------------------v--------------------------------------------------+
       |               ISOLATED LIVE PROVIDER BACKBONE                       |
       | • Ethereum (RPC Primary + Etherscan Fallback)                       |
       | • Polygon (RPC Primary + Polygonscan Fallback)                      |
       | • Bitcoin (Mempool.space Primary + Esplora Fallback)                |
       | • TRON (TronGrid TRC-20 + Full Node RPC)                            |
       | • CoinGecko (Indicative Fiat/Spot Rates Only)                       |
       +---------------------------------------------------------------------+"""

new_diag = """       +------------------v--------------------------------------------------+
       |            5-TIER IN-PROCESS TTL CACHE LAYER (cachetools)           |
       | • HOT_ADDR (2000 / 300s)          • PRICE (50 / 60s)               |
       | • VASP_LABEL (500 / 3600s)        • HEALTH (20 / 30s)              |
       | • TRACE (200 / 1800s)             • Keys: (chain, address) scoped   |
       +----------------------------------+----------------------------------+
                                          |
       +----------------------------------v----------------------------------+
       |       ISOLATED LIVE PROVIDER BACKBONE (Failover Waterfall)          |
       | • ProviderCircuitBreaker (threshold=3, cooldown=60s, half-open)    |
       | • Ethereum (PublicNode Primary -> Ankr -> Cloudflare -> DRPC)       |
       | • BNB / BSC (Chain 56: Ankr RPC Primary -> Binance LlamaRPC)        |
       | • Polygon (DRPC Primary -> Ankr -> Polygon-RPC)                     |
       | • Bitcoin (Mempool.space Primary -> Blockstream -> Blockchain.info) |
       | • TRON (TronGrid TRC-20 -> TronFullNode -> TronStack)               |
       | • CoinGecko (Indicative Fiat/Spot Rates Only)                       |
       +---------------------------------------------------------------------+"""

assert old_diag in content, "Could not find old_diag"
content = content.replace(old_diag, new_diag)

# 2. Update Step 3 (Live and Demo Path)
old_step3 = """### IF mode = LIVE (Real Data Path)

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
- Stops early if `max_nodes = 1000` or `timeout = 60s` is reached"""

new_step3 = """### IF mode = LIVE (Real Data Path)

```
BoundedTracer
    ├──▶ 5-Tier TTLCache (CacheManager)
    │         └── HOT_ADDR (ttl=300s), VASP_LABEL (ttl=3600s), TRACE (ttl=1800s)
    └──▶ ProviderManager.fetch_transfers(address, chain) / fetch_with_failover()
              │  (Guarded by ProviderCircuitBreaker: threshold=3, cooldown=60s)
              ├── chain = ETH  →  EVMAdapter (Chain 1: PublicNode -> Ankr -> Cloudflare -> DRPC)
              ├── chain = BSC  →  EVMAdapter (Chain 56: Ankr RPC -> Binance LlamaRPC)
              ├── chain = POLYGON  →  EVMAdapter (Chain 137: DRPC -> Ankr -> Polygon-RPC)
              ├── chain = BTC  →  BitcoinAdapter (Mempool.space -> Blockstream -> Blockchain.info)
              └── chain = TRON  →  TronAdapter (TronGrid -> TronFullNode -> TronStack)
```

It performs **Multi-Directional BFS (Breadth-First Search)**:
- Governed by `TraceDirection` enum (`FORWARD`, `BACKWARD`, `BIDIRECTIONAL`)
- **Forward Traversal**: Starts at suspect wallet, queries outgoing transfers (`direction == "OUT"`), visits recipient wallets up to `max_hops = 5` levels deep.
- **Backward (Fan-In) Traversal**: Activated when `direction` is `BACKWARD` or `BIDIRECTIONAL`. Queries incoming transfers for the seed wallet up to `max_backward_hops = 2`. Nodes tagged `type="funding_source"`, edges tagged `edge_type="FAN_IN"`, aggregated into `fan_in_summary`.
- **DeFi / DEX Router Detection**: When a recipient matches `DEX_REGISTRY` (Uniswap V2/V3/Universal, SushiSwap, PancakeSwap V2, Curve 3pool, SunSwap), node is typed `defi_swap`, edge tagged `DEFI_SWAP`, emits `DEFI_OBFUSCATION`, and BFS continues past the liquidity pool with `asset_reset=True`.
- **Convergence Tracking**: Identifies intermediate addresses receiving funds from $\\ge 2$ independent branches; tracks `convergence_nodes` in trace result.
- **Strict Bounding**: Stops early if `max_nodes = 1000` or `timeout = 120s` (raised from 60s for multi-chain resilience). If timeout occurs after $\\ge 2$ hops, returns `PARTIAL_COMPLETE` with a 15% completeness deduction and banner."""

assert old_step3 in content, "Could not find old_step3"
content = content.replace(old_step3, new_step3)

# 3. Update Step 5a Typology Engine
old_step5a = """| Rule | Detects |
|------|---------|
| `mule_network_rule` | Rapid fan-out — one wallet sending to many recipients |
| `mixer_boundary_rule` | Hops through known mixer/tumbler wallet addresses |
| `peel_chain_rule` | Linear chain where each hop sends slightly less (gas peel) |
| `rapid_hop_rule` | Multiple hops occurring within 24 hours |"""

new_step5a = """| Rule | Detects |
|------|---------|
| `mule_network_rule` | Rapid pass-through across >=3 intermediate unhosted wallets; fee consistency within 15%; NO synthetic 600s fallback (caps at LOW confidence with explicit uncertainty disclosure if timestamps missing) |
| `mixer_boundary_rule` | Hops through known mixer/tumbler wallet addresses (Tornado Cash, Blender, etc.) |
| `peel_chain_rule` | Successive value reduction strictly in the 0.5%–5% per-hop range across >=3 hops to UNIQUE recipient addresses (real implementation, NOT a stub) |
| `rapid_hop_rule` | Multiple hops within chain-specific velocity windows (ETH: 10,800s; TRON: 3,600s; BTC: 86,400s; POLYGON: 1,800s; BSC: 3,600s) |
| `consolidation_funnel_rule` | Convergence where >=2 independent branches merge into a single collection address prior to VASP off-ramp |"""

assert old_step5a in content, "Could not find old_step5a"
content = content.replace(old_step5a, new_step5a)

# 4. Update Step 5b Adaptive VASP Scorer description
old_step5b_text = """### 5b. AdaptiveVASPScorer — The Core Innovation
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
`backend/attribution/vasp_registry.py` — intentional, forensic-grade curated data."""

new_step5b_text = """### 5b. AttributionResolver & AdaptiveVASPScorer — Core Innovation
**Files:** `backend/attribution/attribution_resolver.py`, `backend/attribution/adaptive_vasp_scorer.py`, `backend/attribution/vasp_registry.py`

#### Nearest-VASP-First Resolution (§1.1):
`AttributionResolver.resolve()` walks the traversed hops sorted strictly by `hop_number` (traversal order) and returns the **FIRST (nearest) VASP match**, NOT the terminal node:
- Once an exchange hot-wallet is encountered, internal exchange sweep movements downstream do NOT override the identified entry point.
- Single unambiguous match -> `VERIFIED` (`exact=True`).
- Ambiguous multi-VASP match (shared pattern/cluster) -> `INFERRED`, `is_ambiguous=True`, confidence capped at `MEDIUM`, and `score_all_candidates()` returns a ranked list of candidate scores descending.
- No VASP encountered -> `UNRESOLVED`.

#### 6-Step Adaptive Scoring Sequence:
Per PRD mandate under `policy_v1_india_kyc`:
```
Step 1: Load versioned policy (policy_v1_india_kyc)  → base weight = 0.50
Step 2: Apply SINGLE_HOP override (+0.20 if hop_count == 1)
Step 3: Apply contextual modifiers alphabetically:
        - a_jurisdiction: India FIU-registered (+0.15), foreign registered (+0.08)
        - b_hop_decay: -0.08 per hop beyond hop 1, strictly CAPPED at -0.20
        - c_hot_wallet_match: exact (+0.35), cluster heuristic (+0.15)
        - d_mixer_penalty: -0.30 if mixer detected
        - e_recent_activity: +0.10 if <= 7 days
Step 4: Resolve conflicting modifiers conservatively (mixer presence suppresses cluster match)
Step 5 & 6: Clamp raw score to [5, 95] and assign classification band:
        - VERIFIED / HIGH: FIU-registered + exact match + no mixer + hops <= 2
        - INFERRED / MEDIUM: score >= 60, no mixer
        - INFERRED / LOW (deep_trace_partial): score 40-59, hops >= 3, no mixer
        - UNRESOLVED / LOW: all other cases
        - Completeness Cap: if data_completeness_pct < 70%, confidence capped at MEDIUM
```

Output: `AttributionScore` containing:
- `vasp_name`, `vasp_id`, `score` (0 to 100), `label_type`, `confidence_band`
- `nearest_vasp_hop`: Hop number where VASP was first encountered
- `ranked_candidates`: Ranked list of all candidate scores on ambiguous matches
- `nodal_officer_email`: Auto-populated from `VASP_REGISTRY`
- `fiu_status`: `REGISTERED` / `UNREGISTERED`
- `scoring_steps`: Full explainable audit trace of every mathematical weight decision

The **VASP Registry** in `backend/attribution/vasp_registry.py` contains 10 Indian VASPs (WazirX, CoinDCX, ZebPay, Mudrex, BitBNS, Giottus, Unocoin, Pi42, CoinSwitch, BuyUcoin, KoinBX, SunCrypto, Flitpay) and 5 global VASPs (Binance, KuCoin, Bybit, OKX, Bitget, MEXC, HTX, Gate.io) complete with geographic coordinates, FATF greylist status, and cached address tag lookups (`lookup_address_tags()`)."""

assert old_step5b_text in content, "Could not find old_step5b_text"
content = content.replace(old_step5b_text, new_step5b_text)

# 5. Update Step 5c and 5d
old_step5c_5d = """### 5c. Risk Assessment
**File:** `backend/assessment/risk_assessment.py`

Produces a risk score (0–100) based on:
- Typologies detected (mixer = +40 risk, peel chain = +25)
- Hop count (more hops = higher obfuscation risk)
- Attribution confidence (lower confidence = higher residual risk)
- Chain (TRON historically associated with USDT scams)

---

### 5d. Recovery Estimator
**File:** `backend/assessment/recovery_estimate.py`

Operational asset recovery probability estimator gated strictly by **PRD FR-016 boundary rules**:
1. **Zero-Hop Rejection**: Trace depth == 0 $\\implies$ `ESTIMATE_NOT_APPLICABLE` (untracked funds).
2. **Attribution Gating**: Attribution == `LEAD` or `NONE` $\\implies$ `ESTIMATE_NOT_APPLICABLE` (no identifiable custodial counterparty).
3. **Low-Value Threshold**: Defrauded amount $< \\$120$ $\\implies$ `LOW_VALUE_UNECONOMIC` (uneconomic to pursue statutory freeze).

For valid cases, computes a 4-factor operational urgency score:
- **Base Score**: 0.40–0.90 based on VASP FIU-IND registration and operational jurisdiction.
- **72-Hour Decay Curve**: Exponential decay where recovery odds diminish as hours elapse.
- **Fraud Type Modifiers**: Phishing, task scams, ransomware, and extortion modifiers applied.
- **Actionable Window**: Remaining freeze countdown window displayed to the investigating officer."""

new_step5c_5d = """### 5c. Risk Assessment
**File:** `backend/assessment/risk_assessment.py`

Produces an independent composite risk score (0–100) based on:
- **Fraud Amount Tiers (§3.1)**: >= $1.2M USD (+35 pts), >= $120K USD (+25 pts), >= $12K USD (+15 pts), else 0.
- **Cross-Chain Layering (§3.2)**: 1 bridge (+10 pts), 2+ bridges (+20 pts), bridge + mixer compound (+30 pts).
- **Offshore VASP Penalty (§3.3)**: `fiu_status == "UNREGISTERED"` and non-India jurisdiction (+15 pts).
- **Cross-Rule Compounding (§3.4)**: MULE + RAPID_HOP (+15 pts), MULE + MIXER (+10 pts and forced `CRITICAL` risk), OFAC + typologies (forced `CRITICAL` risk, min 85).
- **Typologies & Sanctions**: OFAC SDN hit (+45 pts), Mixer interaction (+30 pts), Mule network (+20 pts), Peel chain (+15 pts), Consolidation funnel (+15 pts), Hop velocity (+10 pts for >=4 hops, else +5).
- **Automated Alert Dispatch**: Dispatches automated critical alert when `risk_category == "CRITICAL"` or `ofac_sanction_hit == True` via `AlertDispatcher`.

---

### 5d. Recovery Estimator (Heuristic Recovery Estimate)
**File:** `backend/assessment/recovery_estimate.py`

Calculates the **Heuristic Recovery Estimate** (0–100) and operational action window (4–36 hours):
- **Mandatory PRD FR-016 Boundary Gating**: Evaluates 4 eligibility conditions:
  1. `hop_count > 0` (zero-hop traces invalid).
  2. `traced_amount_usd >= 120.0` (approx ₹10,000 INR minimum actionable threshold).
  3. `data_completeness_pct >= 70.0%`.
  4. `attribution_confidence not in ["LEAD", "NONE", "LOW"]` and `mixer_detected == False`.
  If boundary conditions are not met, returns `display_tier = "ineligible"`, `recovery_score = 0`, and `action_window_hours = 0`.
- **Temporal Verification Guarantee (§4.1)**: If `elapsed_hours` is missing/unverifiable from case creation date or hop timestamps, returns `display_tier = "insufficient_data"` — never fabricates a default urgency.
- **Fraud-Type Modifiers (§4.2)**: `TASK_BASED_FRAUD` (+5 pts), `RANSOMWARE` (-10 pts), `SEXTORTION` (-15 pts), `DARKNET` (-30 pts), `ORGANIZED_CRIME` (-10 pts), `INVESTMENT_SCAM`/`PHISHING` (0 pts).
- **Core Factors (Eligible Cases)**:
  - VASP Cooperation: Indian FIU-registered (+35 pts), Global registered (+20 pts).
  - Time Decay: <= 24h (+30 pts, window max(6, 36-h)); 24-48h (+15 pts, window max(4, 48-h)); > 48h (+5 pts, window 12h).
  - Path Simplicity: 1 hop (+25 pts), 2-3 hops (+15 pts), 4+ hops (+5 pts).
  - Attribution Band: HIGH (+10 pts), MEDIUM (+5 pts)."""

assert old_step5c_5d in content, "Could not find old_step5c_5d"
content = content.replace(old_step5c_5d, new_step5c_5d)

# 6. Update Step 6b Database Tables
old_db_tables = """| Table | What's Stored |
|-------|---------------|
| `cases` | Case ID, wallet, chain, complainant, FIR number, status |
| `investigations` | Full trace result JSON, risk score, VASP name, confidence |
| `transfers` | Individual normalized blockchain transfer events |
| `evidence_items` | Evidence hashes with chain-of-custody metadata |
| `audit_events` | SHA-256 chained audit log (see Step 7) |"""

new_db_tables = """| Table | What's Stored |
|-------|---------------|
| `cases` | Case ID, wallet, chain, complainant, FIR number, status |
| `investigations` | Full trace result JSON, risk score, VASP name, confidence |
| `transfers` | Individual normalized blockchain transfer events |
| `evidence_items` | Evidence hashes with chain-of-custody metadata |
| `audit_events` | SHA-256 chained audit log (see Step 7) |
| `wallet_index` | Cross-case wallet clustering index (`address`, `chain`, `case_id`, `hop_depth`, `first_seen`) for `REPEAT_OFFENDER_WALLET` detection |
| `alerts` | Automated alert dispatch records (`alert_id`, `case_id`, `risk_category`, `trigger_reason`, `severity`, `dispatched_to`, `timestamp`, `details_json`) |"""

assert old_db_tables in content, "Could not find old_db_tables"
content = content.replace(old_db_tables, new_db_tables)

# 7. Update Part 3 Section 2 (AttributionResolver nearest-VASP, decay cap, deep_trace_partial)
old_sec2_resolver = r"""7. **Resolution Across Candidates (`AttributionResolver`):**  
   Extracts terminal destination nodes ($to\_address$ that is not a $from\_address$). Matches against `hot_wallet_patterns`.  
   - 0 matches: `UNRESOLVED` (`vasp_key = None`, `exact = False`).
   - 1 match: `VERIFIED` (`exact = True`).
   - $> 1$ matches (ambiguous cluster overlap): `INFERRED`, `is_ambiguous = True`, confidence capped at `MEDIUM`."""

new_sec2_resolver = r"""7. **Nearest-VASP-First Resolution (`AttributionResolver` §1.1):**  
   Walks hops sorted strictly by `hop_number` (traversal order) and returns the FIRST address that matches a `VASP_REGISTRY` entry. This correctly attributes the nearest deposit counterparty rather than downstream internal exchange movements:
   - 0 matches: `UNRESOLVED` (`vasp_key = None`, `exact = False`, `label_type = "UNRESOLVED"`).
   - 1 match: `VERIFIED` if exact hot-wallet pattern match, else `INFERRED`.
   - Multi-VASP candidate overlap: `INFERRED`, `is_ambiguous = True`, confidence capped at `MEDIUM`, and `score_all_candidates()` scores all plausible candidates in descending order."""

assert old_sec2_resolver in content, "Could not find old_sec2_resolver"
content = content.replace(old_sec2_resolver, new_sec2_resolver)

old_decay = r"""   - **`b_hop_decay`:** Penalty formula: $-\max(0.0, (hop\_count - 1) \times 0.08)$ (decaying $-8.0$ points per hop beyond hop 1)."""
new_decay = r"""   - **`b_hop_decay`:** Penalty formula: $-\min(0.20, \max(0.0, (hop\_count - 1) \times 0.08))$ (decaying $-8.0$ points per hop beyond hop 1, capped at $-0.20$ to prevent valid deep traces from collapsing)."""
assert old_decay in content, "Could not find old_decay"
content = content.replace(old_decay, new_decay)

old_sec2_step6 = """   - `VERIFIED`: `is_fiu_reg and is_exact_wallet_match and not mixer_detected and hop_count <= 2`. Confidence is `HIGH`.
   - `INFERRED`: `clamped_score >= 60 and not mixer_detected`. Confidence is `MEDIUM` if `hop_count > 1` else `HIGH`.
   - `UNRESOLVED`: All other cases. Confidence is `LOW`."""

new_sec2_step6 = """   - `VERIFIED`: `is_fiu_reg and is_exact_wallet_match and not mixer_detected and hop_count <= 2`. Confidence is `HIGH`.
   - `INFERRED`: `clamped_score >= 60 and not mixer_detected`. Confidence is `MEDIUM` if `hop_count > 1` else `HIGH`.
   - `INFERRED (deep_trace_partial)`: `40 <= clamped_score < 60 and hop_count >= 3 and not mixer_detected`. Confidence is `LOW` (retains deep VASP cluster matches as actionable leads rather than discarding them).
   - `UNRESOLVED`: All other cases. Confidence is `LOW`."""

assert old_sec2_step6 in content, "Could not find old_sec2_step6"
content = content.replace(old_sec2_step6, new_sec2_step6)

# 8. Fix Mule Network synthetic fallback in Section 3
old_mule_600 = """                    # Time difference check (default < 3600 seconds = 60 minutes)
                    ts1 = current_hop.get("timestamp_epoch", 0)
                    ts2 = next_hop.get("timestamp_epoch", 0)
                    if ts1 and ts2 and ts2 >= ts1:
                        time_diffs.append(int(ts2 - ts1))
                    else:
                        time_diffs.append(600)  # nominal 10-minute fallback"""

new_mule_600 = """                    # §2.1: Only append a real time diff when BOTH timestamps are present and valid.
                    # Never inject a synthetic fallback — that is fabricated evidence.
                    ts1 = current_hop.get("timestamp_epoch", 0)
                    ts2 = next_hop.get("timestamp_epoch", 0)
                    if ts1 and ts2 and ts2 >= ts1:
                        time_diffs.append(int(ts2 - ts1))
                        hops_with_timing += 1
                    else:
                        hops_without_timing += 1"""

assert old_mule_600 in content, "Could not find old_mule_600"
content = content.replace(old_mule_600, new_mule_600)

# 9. Add PeelChainRule and ConsolidationFunnelRule in Section 3
old_typology_rules = """#### 3c. RAPID_HOP Rule (`rules/other_rules.py`):"""

new_typology_rules = """#### 3b-2. PEEL_CHAIN Rule (`rules/other_rules.py` §2.3):
- **Core Definition:** Successive value reduction strictly in the 0.5%–5% per-hop range across >= 3 hops to UNIQUE recipient addresses.
- **Real Implementation (Not a Stub):** Prevents false positives from single large deductions (e.g. mixer fees) and enforces address uniqueness (`len(set(addresses)) == len(addresses)`).

```python
# backend/typologies/rules/other_rules.py
class PeelChainRule:
    RULE_ID = "PEEL_CHAIN"
    RULE_VERSION = "1.1"

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        hops = trace_result.get("hops", [])
        if len(hops) < 3:
            return None
        amounts = [float(h.get("amount", 0)) for h in hops]
        addresses = [h.get("to_address", "").lower() for h in hops]
        if not all(a > 0 for a in amounts) or len(set(addresses)) < len(addresses):
            return None
        per_hop_ratios = []
        for i in range(len(amounts) - 1):
            if amounts[i] <= 0: return None
            per_hop_ratios.append((amounts[i] - amounts[i + 1]) / amounts[i])
        if not all(0.005 <= r <= 0.05 for r in per_hop_ratios):
            return None
        return PatternFinding(
            finding_id=f"FIND-PEEL-{case_id[-8:]}",
            case_id=case_id,
            typology_name="PEEL_CHAIN",
            rule_version=self.RULE_VERSION,
            confidence="HIGH" if len(amounts) >= 4 else "MEDIUM",
            evidence_json={
                "hop_count": len(amounts),
                "initial_amount": amounts[0],
                "final_amount": amounts[-1],
                "peel_decay_ratio": round(amounts[-1] / amounts[0], 3),
                "per_hop_reduction_pcts": [round(r * 100, 2) for r in per_hop_ratios],
                "unique_addresses": True,
            },
            uncertainty_notes="Successive 0.5–5% per-hop deductions to unique addresses; consistent with peel wallet laundering.",
            data_completeness_pct=trace_result.get("data_completeness_pct", 90.0),
            india_specific=False,
        )
```

#### 3b-3. CONSOLIDATION_FUNNEL Rule (`rules/other_rules.py` §2.4):
- **Core Definition:** Detects 2+ independent upstream branches merging into a single intermediary collection address prior to onward transmission or VASP deposit.
- **Graph Mechanics:** Tracked via `convergence_nodes` in trace graph.

```python
# backend/typologies/rules/other_rules.py
class ConsolidationFunnelRule:
    RULE_ID = "CONSOLIDATION_FUNNEL"
    RULE_VERSION = "1.0"

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        edges = trace_result.get("edges", [])
        if len(edges) < 2: return None
        in_sources: Dict[str, set] = {}
        for e in edges:
            fa = (e.get("from") or "").strip().lower()
            ta = (e.get("to") or "").strip().lower()
            if fa and ta and fa != ta:
                in_sources.setdefault(ta, set()).add(fa)
        convergent = {ta: srcs for ta, srcs in in_sources.items() if len(srcs) >= 2}
        if convergent:
            conv_addr, sources = next(iter(convergent.items()))
            return PatternFinding(
                finding_id=f"FIND-CONV-{case_id[-8:] if len(case_id)>=8 else case_id}",
                case_id=case_id,
                typology_name="CONSOLIDATION_FUNNEL",
                confidence="HIGH" if len(sources) >= 3 else "MEDIUM",
                evidence_json={
                    "convergence_address": conv_addr,
                    "inbound_branch_count": len(sources),
                    "source_addresses": list(sources)[:10],
                },
                uncertainty_notes=f"Consolidation funnel detected: {len(sources)} branches merge into {conv_addr[:10]}...",
                data_completeness_pct=trace_result.get("data_completeness_pct", 90.0),
                india_specific=False,
            )
        return None
```

#### 3c. RAPID_HOP Rule (`rules/other_rules.py`):"""

assert old_typology_rules in content, "Could not find old_typology_rules"
content = content.replace(old_typology_rules, new_typology_rules)

# Update RAPID_HOP description to include chain-specific thresholds
old_rapid_hop = r"""- **Velocity Threshold:** $\ge 3$ consecutive hops traversed within $time\_span \le 10,800$ seconds (3 hours).
- **Evidence Fields:** `total_time_span_seconds`, `hop_velocity` (hops/hour), `hops_in_window`."""

new_rapid_hop = """- **Chain-Specific Velocity Thresholds (§2.2):**
  - Ethereum (`ETH`): 10,800s (3 hours)
  - TRON (`TRON`): 3,600s (1 hour)
  - Bitcoin (`BTC`): 86,400s (24 hours)
  - Polygon (`POLYGON`): 1,800s (30 minutes)
  - BNB Chain (`BSC`): 3,600s (1 hour)
- **Evidence Fields:** `total_time_span_seconds`, `threshold_seconds`, `chain`, `hop_velocity` (hops/hour), `hops_in_window`."""

assert old_rapid_hop in content, "Could not find old_rapid_hop"
content = content.replace(old_rapid_hop, new_rapid_hop)

# 10. Update Risk Scoring section 5 in Part 3
old_risk_comp = r"""1. **Component Evaluation:**  
   Extracts `hops`, `typologies`, and `ofac_sanction_hit` from `trace_result`:
   - `ofac_sanctions`: $+45$ if `ofac_sanction_hit` is true; else $0$.
   - `mixer_interaction`: $+30$ if `"MIXER_BOUNDARY"` in typologies; else $0$.
   - `mule_network`: $+20$ if `"MULE_NETWORK"` in typologies; else $0$.
   - `peel_chain`: $+15$ if `"PEEL_CHAIN"` in typologies; else $0$.
   - `hop_velocity`: $+10$ if $len(hops) \ge 4$; else $+5$.
2. **Summation & Capping:**  
   $total\_risk = \min(100, \sum components.values())$.
3. **Band Categorization:**  
   - $\ge 75$: `"CRITICAL"`
   - $\ge 50$: `"HIGH"`
   - $\ge 25$: `"MEDIUM"`
   - $< 25$: `"LOW"`"""

new_risk_comp = """1. **Component Evaluation (§3.1-§3.4):**  
   - `fraud_amount`: >= $1.2M USD (+35 pts), >= $120K USD (+25 pts), >= $12K USD (+15 pts), else 0.
   - `cross_chain_layering`: 1 bridge (+10 pts), 2+ bridges (+20 pts), bridge + mixer compound (+30 pts).
   - `offshore_vasp_penalty`: `fiu_status == "UNREGISTERED"` and jurisdiction != "INDIA" (+15 pts).
   - `compound_mule_rapid`: +15 pts if MULE and RAPID_HOP detected.
   - `compound_mule_mixer`: +10 pts if MULE and MIXER detected.
   - `ofac_sanctions`: +45 pts if `ofac_sanction_hit` is true.
   - `mixer_interaction`: +30 pts if `"MIXER_BOUNDARY"` in typologies.
   - `mule_network`: +20 pts if `"MULE_NETWORK"` in typologies.
   - `peel_chain`: +15 pts if `"PEEL_CHAIN"` in typologies.
   - `consolidation_funnel`: +15 pts if `"CONSOLIDATION_FUNNEL"` in typologies.
   - `hop_velocity`: +10 pts if len(hops) >= 4; else +5.
2. **Summation & Capping:**  
   $total\_risk = \\min(100, \\sum components.values())$.
3. **Category Override Rules (§3.4):**  
   - If OFAC hit and typologies present -> `CRITICAL` (minimum score 85).
   - Elif MULE and MIXER present -> `CRITICAL` (minimum score 75).
   - Elif total_risk >= 75 -> `CRITICAL`
   - Elif total_risk >= 50 -> `HIGH`
   - Elif total_risk >= 25 -> `MEDIUM`
   - Else -> `LOW`"""

assert old_risk_comp in content, "Could not find old_risk_comp"
content = content.replace(old_risk_comp, new_risk_comp)

# 11. Update Part 4 Database Tables list
old_part4_tables = """10. **`investigations`** (Contains data):
    - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    - `case_id` (TEXT)
    - `suspect_address` (TEXT)
    - `chain` (TEXT)
    - `crime_category` (TEXT)
    - `nearest_vasp` (TEXT)
    - `risk_score` (INTEGER)
    - `risk_category` (TEXT)
    - `confidence` (INTEGER)
    - `investigating_officer` (TEXT)
    - `created_at` (TEXT)
    - `result_json` (TEXT)"""

new_part4_tables = """10. **`investigations`** (Contains data):
    - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    - `case_id` (TEXT)
    - `suspect_address` (TEXT)
    - `chain` (TEXT)
    - `crime_category` (TEXT)
    - `nearest_vasp` (TEXT)
    - `risk_score` (INTEGER)
    - `risk_category` (TEXT)
    - `confidence` (INTEGER)
    - `investigating_officer` (TEXT)
    - `created_at` (TEXT)
    - `result_json` (TEXT)

11. **`wallet_index`** (§6.1 Cross-Case Wallet Clustering Index):
    - `address` (TEXT NOT NULL)
    - `chain` (TEXT NOT NULL DEFAULT 'ETH')
    - `case_id` (TEXT NOT NULL)
    - `hop_depth` (INTEGER NOT NULL DEFAULT 0)
    - `first_seen` (TEXT DEFAULT CURRENT_TIMESTAMP)
    - `PRIMARY KEY (address, chain, case_id)`
    - `INDEX idx_wallet_index_addr (address, chain)`

12. **`alerts`** (§7.1 Automated Alert Dispatch Table):
    - `alert_id` (TEXT PRIMARY KEY)
    - `case_id` (TEXT NOT NULL)
    - `risk_category` (TEXT NOT NULL)
    - `trigger_reason` (TEXT NOT NULL)
    - `severity` (TEXT NOT NULL DEFAULT 'CRITICAL')
    - `dispatched_to` (TEXT NOT NULL DEFAULT 'INTERNAL_LOG')
    - `timestamp` (TEXT DEFAULT CURRENT_TIMESTAMP)
    - `details_json` (TEXT NOT NULL DEFAULT '{}')
    - `INDEX idx_alerts_case (case_id)`"""

assert old_part4_tables in content, "Could not find old_part4_tables"
content = content.replace(old_part4_tables, new_part4_tables)

# 12. Update Part 4 API Endpoints Table
old_intake_row = """| `POST`| `/api/v1/intake/ncrp/complaint` | **INTEGRATION_SERVICE** | Ingests cybercrime complaint. | Yes |"""
new_intake_row = """| `POST`| `/api/v1/intake/ncrp/complaint` | **INVESTIGATOR / ADMIN / INTEGRATION_SERVICE** | Ingests cybercrime complaint (§8.5 fix). | Yes |
| `GET` | `/api/v1/system/cache-stats` | None | Returns 5-tier TTL cache hits, misses, and backend type (§8.3). | Yes |
| `GET` | `/api/v1/cases/{case_id}/linked-cases` | JWT Bearer | Returns cross-case syndicate wallet links (§6.1). | Yes |
| `GET` | `/api/v1/alerts` | JWT Bearer | Retrieves dispatched automated forensic alerts (§7.1). | Yes |
| `GET` | `/api/v1/analytics/dashboard` | JWT Bearer | Surfaces executive LEA dashboard KPIs and VASP breakdown. | Yes |
| `GET` | `/api/v1/vasps/geo` | None | Returns geographic coordinates & FATF greylist status for all VASPs. | Yes |
| `WS`  | `/ws/trace/{case_id}` | None | Real-time WebSocket trace stream (HOP_COMPLETE, MIXER_BOUNDARY, etc.). | Yes |"""

assert old_intake_row in content, "Could not find old_intake_row"
content = content.replace(old_intake_row, new_intake_row)

with open(doc_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: ARCHITECTURE_AND_CORE_LOGIC.md successfully updated!")
