# CryptoTrace LEA — Logical Gap Analysis

**SIH 26183 · Logical Gap Analysis**  
**Gap Analysis v1**

---

# Logic vs Problem Statement — Full Gap Map
## Where the Algorithms Break, Where They're Incomplete, What's Missing

Every logical gap found by cross-referencing the core logic document, the architecture spec, and every requirement in SIH 26183 — with precise fixes for each.

---

### Executive Summary

| Category | Count | Status |
|---|---|---|
| **Critical Gaps** | **8** | Urgent algorithmic & evidence integrity fixes |
| **Logic Flaws** | **9** | Behavioral heuristics & chain-specific rules |
| **Missing Features** | **7** | Explicit SIH problem statement mandates |
| **Improvements** | **6** | Enhancements & data consistency |
| **Total Findings** | **30** | Complete audit catalog |

---

## 01. Tracing Engine — Logical Gaps & Flaws

### Gap 1.1: Forward-Only BFS — Cannot Trace Incoming Funds (Fan-In Attacks)
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** PS requires *"fund movement patterns"*
- **Summary:** The engine starts from the suspect wallet and only follows **outgoing** transfers. It completely ignores who funded the suspect wallet — the layering chain above it. Indian investment scams typically show multi-source aggregation into a single collector wallet before forwarding to an exchange. Your system misses the entire upstream network.

#### Current Logic:
- `outflows = [t for t in live_transfers if t.direction == "OUT"]`
- The BFS queue only ever enqueues `to_addr` — never `from_addr`
- Victim reports wallet W1. W1 receives from 50 victims, forwards to exchange. System only shows W1 → exchange, never shows the 50 victims → W1 flow

#### Fix:
- Add a `TraceDirection` enum: `FORWARD | BACKWARD | BIDIRECTIONAL`
- Backward pass: enqueue all `from_addr` of incoming transfers up to 2 hops behind the suspect address
- Label backward nodes as `"victim_aggregator"` or `"funding_source"` — do not attribute VASP to them, just count and show the funding scale
- Limit backward depth to 2 to prevent graph explosion

> [!WARNING]
> The problem statement explicitly says "detect fund movement patterns" and "detection of intermediary laundering wallets." Upstream aggregation IS a laundering pattern. Missing it means the mule network detection only catches the forwarding leg, not the aggregation leg — which is where the fraud victims appear.

---

### Gap 1.2: Cycle Detection Only Prevents Re-visit — Loses Convergence Evidence
- **Severity:** `HIGH`
- **Impact / PS Alignment:** Missing typology signal
- **Summary:** When two BFS branches reach the same address, the second incoming edge is appended to `edges` and `hops`, but the address is not re-enqueued. This is logically correct for traversal but the convergence event — which is a strong typology signal for money laundering consolidation — is never flagged.

#### Current Logic:
- When address A is already in `visited_nodes`, the node record is skipped with `continue`
- The edge IS recorded but no flag is set
- Two separate peel chains converging into one wallet before depositing to an exchange — a classic consolidation move — is invisible to the typology engine

#### Fix:
- Track `convergence_nodes: Dict[str, int]` — count of times each address appears as a `to_addr`
- Any address with convergence count ≥ 2 should be flagged as a `CONSOLIDATION_HOP` node type
- Add a new `CONSOLIDATION_FUNNEL` typology rule that fires when 2+ independent chains merge before a VASP deposit

---

### Gap 1.3: 90-Day Time Window Is a Hard Cutoff With No Warning
- **Severity:** `HIGH`
- **Impact / PS Alignment:** Silent data loss
- **Summary:** `time_window_days = 90` silently excludes transactions older than 90 days. Many darknet and ransomware investigations involve wallet activity going back 12–18 months. When the cutoff truncates the trace, `data_completeness_pct` is not penalized for this — it only penalizes provider errors.

#### Current Logic:
- `data_completeness_pct = 100.0 if DEMO else max(30.0, 92.5 - (provider_errors * 15.0))`
- Time window truncation is completely invisible to the completeness metric
- A 180-day old wallet could return 0 transactions and the system reports 92.5% completeness

#### Fix:
- Track `time_window_truncations: int` — incremented when the oldest available transaction is older than `time_window_days`
- Deduct 10% from completeness per truncation event
- Add a `TIME_WINDOW_WARNING` to `boundary_events` when truncation happens
- Expose `earliest_transaction_date` in the trace result so the investigator knows the actual data horizon

---

### Gap 1.4: Bridge Destination Is Hardcoded — Not Actually Resolved from Chain
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** Fabricates forensic evidence
- **Summary:** When a bridge contract is hit, `decoded_recipient` is hardcoded as a fixed address based on whether dest_chain is TRON or ETH. This means every single ETH→TRON bridge hop shows the exact same recipient address regardless of the actual transaction. The "PROVEN" link_type is assigned even though the destination was never actually queried.

```python
# Current code — THIS IS THE PROBLEM:
dest_chain = "TRON" if chain == "ETH" else "ETH"
decoded_recipient = "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6" if dest_chain == "TRON" else "0x28c6c06298d514db089934071355e5743bf21d60"
# Every ETH→TRON bridge hop will ALWAYS show the same WazirX/Binance address
# regardless of actual on-chain events. This is not PROVEN — it is fabricated.
```

#### Why This Is Dangerous:
- A court report generated from this trace will claim a PROVEN cross-chain link to a specific address that was never actually verified
- The `link_type="PROVEN"` assertion is false — it's deterministic fixture data, not an on-chain verified event
- This creates a Section 65B IEA evidence integrity problem

#### Fix:
- For LIVE mode: query the destination chain's block explorer for the bridge delivery transaction using the source tx_hash as a correlation key
- If destination tx cannot be found within 1 hour: classify as `HEURISTIC_CORRELATION`, never `PROVEN`
- Only assign `PROVEN` when `dest_tx_hash` is actually retrieved from a live provider

---

### Gap 1.5: Timeout Kills Entire Trace — No Partial Result Saved
- **Severity:** `HIGH`
- **Impact / PS Alignment:** Demo reliability risk
- **Summary:** When `timeout_seconds = 60` is hit, the loop breaks with `termination_reason = "TIMEOUT"`. The post-traversal pipeline (typology, VASP scoring, risk) still runs on whatever was collected. But if the timeout happens at hop 1 because the provider was slow, the investigator gets a bare skeleton with no meaningful output.

#### Fix:
- Before the BFS loop, set a `partial_checkpoint_at_hop = 2`. When `len(hops) >= 2` and timeout occurs, the result is marked `PARTIAL_COMPLETE` rather than `TIMEOUT`, and the post-traversal pipeline still runs fully. The investigator gets a 2-hop partial result with a warning banner instead of an empty result.
- Increase `timeout_seconds` to `120` for non-demo cases. The 60s limit is too aggressive for multi-chain traces where each provider call takes 2–4s.

---

## 02. VASP Attribution — Logic Gaps

### Gap 2.1: Attribution Resolver Only Checks Terminal Nodes — Misses Intermediate VASP Deposits
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** Nearest VASP detection broken
- **Summary:** The `AttributionResolver.resolve()` function identifies terminal addresses — those that appear as `to_addr` but never as `from_addr`. But in real Indian fraud, funds often hit a known exchange deposit address at hop 2 or 3 and then move again internally within the exchange. Your resolver misses the earlier VASP deposit because it only looks at the last address.

#### Current Logic:
- `terminal_addrs = [addr for addr in to_addrs if addr not in from_addrs]`
- Path: Victim → Mule1 → Mule2 → **WazirX deposit** → WazirX internal wallet → WazirX cold storage
- WazirX deposit address IS a `from_addr` (it sends internally), so it's excluded from terminal_addrs
- The resolver sees WazirX cold storage as the terminal, which is NOT in the hot wallet patterns → returns UNRESOLVED

#### Fix:
- Change resolver to check ALL addresses in the trace (not just terminal ones) against VASP patterns
- Return the **first** (nearest) VASP match in BFS order, not the last
- Mark subsequent hops from a matched VASP as `type: "vasp_internal"` — do not trace them further
- This is exactly what the problem statement means by "identifying the nearest exchange receiving direct deposits"

> [!CAUTION]
> The problem statement says: **"identifying the nearest exchange or VASP receiving direct deposits."** The current resolver finds the furthest address, not the nearest VASP. This is the core attribution requirement and it's logically inverted.

---

### Gap 2.2: VASP Scorer Called with Hardcoded "WAZIRX" in DEMO Mode — Bypasses Attribution
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** Demo shows wrong VASP
- **Summary:** In DEMO mode, `adaptive_vasp_scorer.score_candidate(vasp_key="WAZIRX", ...)` is called with a hardcoded key regardless of what the trace actually resolved. This means every demo trace attributes funds to WazirX even if the demo case is configured to terminate at a Tornado Cash mixer or a Bybit address.

```python
# In trace_engine.py DEMO branch — hardcoded WAZIRX regardless of demo case
if mode.upper() == "DEMO":
    attribution = adaptive_vasp_scorer.score_candidate(
        vasp_key="WAZIRX",  # ← ALWAYS WazirX in demo, even for mixer/OFAC cases
        trace_result=raw_result,
        ...
    )
```

#### Problem:
- Demo case CR-2026-MIXER-BOUND-02 (Tornado Cash) would still attribute to WazirX
- Demo case CR-2026-OFAC-SDN-05 (Lazarus Group / Binance) would also attribute to WazirX
- Each demo case's VASP is predetermined but the scorer ignores it

#### Fix:
- Read `vasp_key` from the demo case fixture: `demo_cases_v2.py` already has the expected VASP per case
- Replace hardcoded "WAZIRX" with `fixture_case.expected_vasp`
- Or better: always use the live `attribution_resolver.resolve()` path even in DEMO mode — the fixture data already terminates at the right address

---

### Gap 2.3: Hop Penalty Decay Is Uncapped — Can Drive Score Negative Before Clamping
- **Severity:** `HIGH`
- **Impact / PS Alignment:** Over-penalizes deep traces
- **Summary:** Step 3b formula: `-max(0.0, (hop_count - 1) × 0.08)`. At 5 hops this is -0.32 (-32 points). At the default `max_hops=5`, the raw score before clamping for a non-exact, non-FIU, non-recent wallet would be: 50 + 0 + 0 - 32 + 15 + 0 + 0 = 33. After clamping: 33. Label: UNRESOLVED (below 60). Every deep trace with a heuristic cluster match returns UNRESOLVED regardless of the cluster confidence.

#### Details:
- **Problem:** A 4-hop trace to a Binance hot wallet with cluster-heuristic match gets score 33 → UNRESOLVED. But that cluster match is actually strong evidence — it should be INFERRED at minimum.
- **Fix A:** Cap hop penalty at `-0.20` (max 20 points, not unlimited). Formula: `-min(0.20, (hop_count - 1) × 0.08)`
- **Fix B:** Increase the INFERRED threshold from 60 to account for deep-trace scenarios: add a `DEEP_TRACE_PARTIAL` confidence band for score 40–59 with explicit uncertainty language
- **Why it matters:** The problem statement requires "real-time tracing capability" — deep traces should still produce actionable output, not UNRESOLVED non-answers

---

### Gap 2.4: Single VASP Candidate — No Multi-VASP Ranking Output
- **Severity:** `MEDIUM`
- **Impact / PS Alignment:** Limits investigative output
- **Summary:** The scorer evaluates one `vasp_key` at a time. When the resolver finds an ambiguous match (e.g. address in both WazirX and Binance clusters), it returns `candidates[0]` and caps at MEDIUM. But an investigator would benefit from seeing ALL matching VASPs ranked by score — especially for freeze notices where you may need to contact multiple exchanges.

#### Details:
- **Fix:** When `is_ambiguous=True`, run `score_candidate()` for each candidate VASP in the ambiguous set and return a ranked list of `AttributionScore` objects
- **Frontend:** Show a "VASP Candidates" accordion that lists each candidate with its individual score and a "Contact All" button for freeze notices
- **Problem statement alignment:** "enhance coordination with VASPs" — you can't coordinate with all of them if you only surface one

---

## 03. Typology Engine — Logic Gaps

### Gap 3.1: MULE_NETWORK Rule: Timestamp Fallback Creates False Positives
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** False positive in demo
- **Summary:** When `timestamp_epoch` is missing or zero on a hop, the code injects a nominal `600` seconds (10 minutes) fallback. This means if 3+ hops are missing timestamps — which happens frequently in DEMO mode where fixture data may omit timestamps — the rule will fire on synthetic time differences and produce a false MULE_NETWORK finding.

```python
# Current code in mule_network.py — PROBLEM:
if ts1 and ts2 and ts2 >= ts1:
    time_diffs.append(int(ts2 - ts1))
else:
    time_diffs.append(600)  # ← Injected 10-minute fake timestamp
# If all 3 required hops have missing timestamps:
# time_diffs = [600, 600] — all within 3600s threshold
# Rule fires! But there is NO actual timing evidence.
```

#### Impact:
- A MULE_NETWORK finding with fabricated timing evidence is a false positive that could affect investigative decisions
- The court report would cite timing evidence that doesn't exist
- In a live investigation, presenting this to a judge under Section 65B IEA would be challenged

#### Fix:
- Remove the 600s fallback entirely
- Track `hops_with_timing` vs `hops_without_timing`
- Only include timing-confirmed hops in the mule wallet list
- If `hops_with_timing < 2`, set `confidence = "LOW"` and add uncertainty note: "Timing evidence incomplete — temporal pattern could not be verified"

---

### Gap 3.2: RAPID_HOP Rule: 3-Hour Window Is Chain-Agnostic — Wrong for Bitcoin
- **Severity:** `HIGH`
- **Impact / PS Alignment:** Chain-specific false positives
- **Summary:** The RAPID_HOP rule fires when ≥3 hops occur within 10,800 seconds (3 hours). This is appropriate for EVM chains where blocks are ~12 seconds. But Bitcoin has ~10-minute block times. Three Bitcoin hops in 3 hours = 3 consecutive blocks, which is completely normal Bitcoin behavior, not rapid hop laundering.

| Chain | Block Time | 3 hops in 3h = ? | Suspicious? | Correct Threshold |
|---|---|---|---|---|
| **ETH** | ~12s | Could be <1 minute | Yes — suspicious | 10,800s (3h) ✓ |
| **TRON** | ~3s | Could be <30 seconds | Very suspicious | 3,600s (1h) — should be tighter |
| **BTC** | ~600s | 3 sequential blocks = normal | No — completely normal | 86,400s (24h) for BTC |
| **POLYGON** | ~2s | Near-instant | Very suspicious | 1,800s (30m) — tightest |

> [!TIP]
> **Fix:** Add a `RAPID_HOP_THRESHOLDS: Dict[str, int]` config per chain. ETH: 10800, TRON: 3600, BTC: 86400, POLYGON: 1800. Pass `chain` into the `evaluate()` call and use the chain-specific threshold.

---

### Gap 3.3: PEEL_CHAIN Rule Is Referenced But Never Shown Implemented
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** Unverifiable risk component
- **Summary:** The `TypologyEngine` includes `peel_chain_rule` in its rules list and the risk assessor adds +15 for "PEEL_CHAIN". But the logic-core document only references `rules/other_rules.py` and shows only `RapidHopRule`. The peel chain detection logic is either missing or hidden in an undocumented location. Yet the risk assessor scores it — meaning if it somehow fires, 15 points are added without verifiable logic.

#### Details:
- **What peel chain is:** A pattern where each hop transfers a slightly smaller amount to a new address, "peeling" off a layer fee, while the remainder goes to the next wallet. Classic BTC money laundering pattern.
- **What to verify:** Check if `peel_chain_rule` is actually defined in `other_rules.py` or elsewhere. If it's a placeholder class that always returns `None`, remove it from the risk scoring components to avoid phantom +15 risk points
- **Implement properly:** Peel chain = successive value reduction of 1–5% per hop, minimum 3 hops, each to a unique address. Formula: `(hop[i].amount - hop[i+1].amount) / hop[i].amount` is between 0.005 and 0.05 for all consecutive pairs

---

### Gap 3.4: Typology Rules Are Independent — No Cross-Rule Compounding
- **Severity:** `MEDIUM`
- **Impact / PS Alignment:** Risk under-estimation
- **Summary:** The typology engine runs all 5 rules in isolation with no inter-rule signaling. In real fraud cases, RAPID_HOP + MULE_NETWORK occurring simultaneously is a much stronger signal than either alone. The current engine returns both findings but the risk scorer simply adds their scores without multiplicative amplification.

#### Fix:
- Add a `compound_risk_bonus` to the risk assessor: when both MULE_NETWORK and RAPID_HOP are present simultaneously, add +15 bonus points on top of their individual contributions
- When MULE_NETWORK + MIXER_BOUNDARY co-occur: add +10 bonus and force `CRITICAL` regardless of numeric score
- When OFAC + ANY typology: immediately return CRITICAL with a mandatory freeze alert, no further scoring needed
- This creates a compound risk matrix that better reflects real investigative judgment

---

## 04. Risk Scoring — Logic Gaps

### Gap 4.1: Risk Score Has No Amount Factor — ₹1,000 Fraud Scores Same as ₹1 Crore Fraud
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** Triage logic missing
- **Summary:** The risk scoring components are: OFAC (45), mixer (30), mule (20), peel (15), hop velocity (5–10). None of them incorporate the fraud amount. A ₹1,000 task-based fraud and a ₹1 crore investment scam would produce identical risk scores given the same typologies. This directly violates investigative triage logic — high-value cases should be prioritized for immediate action.

#### Current Logic:
- Components: OFAC=45, mixer=30, mule=20, peel=15, velocity=5/10
- Amount is not a component
- A ₹50 dusting attack that hits a mixer scores 30 (MEDIUM)
- A ₹50 lakh ransomware that has clean hops scores only 5–10 (LOW)

#### Fix — Add Amount Component:
- `> ₹10 lakh ($12K+): +15 points`
- `> ₹1 crore ($120K+): +25 points`
- `> ₹10 crore ($1.2M+): +35 points`
- This ensures high-value cases always rank higher in the investigator alert queue

---

### Gap 4.2: Risk Score Ignores Cross-Chain Events — Bridge Layering Not Penalized
- **Severity:** `HIGH`
- **Impact / PS Alignment:** PS explicitly mentions multi-chain
- **Summary:** The problem statement explicitly lists "multi-chain transfers" as a key challenge. Cross-chain bridge usage is one of the strongest laundering indicators — it deliberately obscures the fund trail. Yet the risk assessor has no component for cross-chain movement. A case with 3 bridge hops across ETH→TRON→BSC scores identically to a clean single-chain trace.

#### Fix:
- Add `cross_chain_layering: int` to risk components
- 1 bridge hop: +10 points
- 2+ bridge hops: +20 points
- Bridge hop + mixer in same trace: +30 points (compound)
- Add to the risk assessor: `"cross_chain_layering": 20 if len(trace_result.get("cross_chain_links", [])) >= 2 else (10 if cross_chain_links else 0)`

---

### Gap 4.3: VASP Jurisdiction Not Used in Risk Score — Offshore VASPs Same Risk as Indian
- **Severity:** `HIGH`
- **Impact / PS Alignment:** Jurisdiction matters for freezing
- **Summary:** Bybit (Dubai), MEXC (Seychelles), HTX (offshore) are present in the registry as UNREGISTERED. Funds reaching them are dramatically harder to freeze than funds reaching WazirX (FIU-IND registered). The risk score doesn't differentiate — a TRON transfer to a Bybit wallet scores the same risk as a transfer to WazirX.

#### Fix:
- Add `offshore_vasp_penalty` to risk components: +15 if attributed VASP is `fiu_status = "UNREGISTERED"` and country is not India
- This directly aligns with the problem statement's goal of "freezing of proceeds of crime" — offshore unregistered VASPs make freezing far harder
- Surface this explicitly in the UI: "Offshore VASP detected — coordination delay expected (MLAT process)"

---

## 05. Recovery Estimate — Logic Gaps

### Gap 5.1: elapsed_hours Defaults to 2.5 When Case Has No Created_Date
- **Severity:** `HIGH`
- **Impact / PS Alignment:** False urgency misleads investigators
- **Summary:** If the database lookup for `created_date` fails or the case doesn't exist yet, `elapsed_hours` defaults to `2.5`. This artificially places every new case in the "≤24h" high-urgency bracket with +30 time score and a 33.5-hour action window — regardless of how old the fraud actually is. A victim who waited 3 days before filing gets shown a 33-hour action window that doesn't exist.

#### Fix:
- Change the fallback to use `elapsed_hours = None` and handle explicitly: when elapsed is unknown, use the hop `timestamp_epoch` from the earliest hop as a proxy, then compute elapsed from that
- If truly no timing information is available, return `display_tier = "insufficient_data"` with message: "Complaint timestamp not available — elapsed time cannot be estimated"
- Never show a false urgency window — this could cause an investigator to deprioritize a genuinely urgent case that was filed with a DB error

---

### Gap 5.2: Recovery Score Has No Fraud Type Weighting
- **Severity:** `MEDIUM`
- **Impact / PS Alignment:** PS names all 7 fraud types
- **Summary:** The problem statement lists 7 fraud types: investment scams, task fraud, sextortion, ransomware, phishing, darknet, organised crime. Each has different recovery urgency and VASP cooperation likelihood. Ransomware VASPs typically comply faster under pressure. Darknet transactions have near-zero recovery potential. The recovery estimator treats all fraud types identically.

| Fraud Type | Typical Recovery Window | VASP Cooperation | Suggested Modifier |
|---|---|---|---|
| **Investment Scam** | 24–48h if caught early | High (India VASPs) | +0 (baseline) |
| **Task-Based Fraud** | 12–24h | High | +5 (faster off-ramp) |
| **Ransomware** | 72h+ (negotiation) | Medium | -10 (delayed) |
| **Sextortion** | Very short (victim shame delays reporting) | Medium | -15 (underreported) |
| **Darknet** | Near zero | Very Low | -30 (near ineligible) |
| **Phishing** | 24–48h | High | +0 (baseline) |

---

## 06. Missing Features Required by the Problem Statement

### Gap 6.1: DeFi Protocol Detection Is Completely Missing
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** PS explicitly names DeFi
- **Summary:** The problem statement explicitly names "DeFi protocols" as a challenge. DeFi encompasses DEX swaps (Uniswap, SushiSwap), liquidity pools, yield farms, and flash loans. Fraudsters swap USDT to ETH via Uniswap to obscure the asset trail. None of this is detected — the system treats Uniswap router calls as standard intermediary hops.

#### What's Missing:
- No DEX router registry (Uniswap V2/V3, SushiSwap, PancakeSwap, DODO)
- No asset swap detection — USDT in, ETH out through same address isn't traced across the asset change
- No liquidity pool interaction detection
- No flash loan detection (common in DeFi exploit laundering)

#### Minimum Fix for Demo:
- Add a `DEX_REGISTRY` dict with top 5 DEX router addresses (Uniswap V3: `0xE592427A0AEce92De3Edee1F18E0157C05861564`)
- When a hop hits a DEX router, flag as `type: "defi_swap"` and add a `DEFI_OBFUSCATION` finding
- Don't halt BFS — continue following the swap recipient, but mark the asset may have changed

---

### Gap 6.2: No FIU-IND Compliance Check on Destination VASP
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** Core India-specific requirement
- **Summary:** The VASP registry distinguishes FIU-IND registered vs unregistered entities. But there is no automated compliance verification step — the system doesn't check whether the destination VASP has filed Suspicious Transaction Reports (STR) for the flagged wallet. FIU-IND has a DEXTER portal for exactly this cross-check. Missing this is a significant gap for Indian LEA users.

#### Details:
- **What FIU-IND integration means:** When a wallet is attributed to an Indian FIU-registered VASP (WazirX, CoinDCX, etc.), the system should automatically draft a STR-cross-reference note and include the VASP's nodal officer email in the freeze notice
- **What exists:** `nodal_officer_email` is in the VASP registry ✓ — but it's never surfaced in the freeze notice draft automatically
- **Fix:** When attribution is VERIFIED or INFERRED and the VASP is FIU-IND registered, the notice generator should auto-populate the nodal officer email, the VASP's freeze order format (each exchange has a specific format), and a reference to PMLA 2002 Section 12A

---

### Gap 6.3: No Wallet Clustering Across Multiple Cases — Isolated Per-Case Analysis
- **Severity:** `CRITICAL`
- **Impact / PS Alignment:** PS requires clustering
- **Summary:** The problem statement says "clustering of exchange wallets" and "organized cyber-enabled financial crimes." Organized crime means the same mule wallets appear across multiple victim complaints. The current system analyzes each case in isolation — it has no cross-case wallet graph. If wallet A appears in 10 different NCRP complaints, the investigator sees 10 separate cases with no connection drawn between them.

#### What's Missing:
- No `wallet_appearances` cross-case index in SQLite
- No alert when a wallet appears in 2+ cases
- KùzuDB graph exists but is only used per-case — no cross-case query

#### Fix:
- Add a `wallet_index` table to `sahyog.db`: `(address, case_id, hop_depth, first_seen)`
- After every trace, insert all traversed addresses into this table
- On new complaint intake: query `wallet_index` for the suspect address — if it appears in prior cases, immediately flag as `REPEAT_OFFENDER_WALLET` and cross-link the cases
- Add a "Linked Cases" panel in the investigation view

> [!IMPORTANT]
> This is arguably the single most impactful missing feature for organized crime investigations. A mule network coordinator reuses the same wallets across hundreds of victims. Cross-case clustering would surface this pattern immediately.

---

### Gap 6.4: No Automated Alert Generation on High-Risk Findings
- **Severity:** `HIGH`
- **Impact / PS Alignment:** PS explicitly requires automated alerts
- **Summary:** The problem statement requires "automated alert generation." The system generates findings and risk scores but there is no autonomous alert dispatch. If a CRITICAL risk case is traced at 3 AM, no alert is sent anywhere — the investigator has to log in and check manually. The "alerts" page in the frontend is a display component, not a push notification system.

#### Fixes:
- **Minimum fix for demo:** After every trace that produces CRITICAL risk, write an alert record to SQLite `alerts` table with timestamp, case_id, risk_category, and trigger reason
- **Push notification:** Add an email dispatch for CRITICAL risk using Python's `smtplib` with Gmail SMTP — free, no external service needed
- **WebSocket broadcast:** When an alert is created, broadcast a WebSocket event to all connected investigator sessions so the alert tray updates live
- **Webhook for NCRP:** POST a JSON alert to a configurable `ALERT_WEBHOOK_URL` — this is the stub integration point for SAHYOG/NCRP that doesn't require real government credentials

---

### Gap 6.5: No Analytics Dashboard for LEA — Aggregate Statistics Missing
- **Severity:** `HIGH`
- **Impact / PS Alignment:** PS requires LEA analytics dashboard
- **Summary:** The problem statement requires "analytics dashboards for law enforcement agencies." The current dashboard shows per-case investigation details. There is no aggregate view showing: total cases this week, total frozen value, fraud type distribution, most common destination VASPs, mule network hotspots, or inter-state fraud corridors. This is what a LEA commanding officer needs, not hop-level case details.

#### Fixes:
- **Add to dashboard/page.tsx:** A summary stats bar showing: Cases This Week, Total Traced Value (₹), CRITICAL Risk Cases, Average Trace Time
- **Add a bar chart** showing fraud type distribution across all cases (using `fraud_type` from intake)
- **Add a VASP frequency table:** "Top 5 destination VASPs this month" — computed by aggregating `attribution.vasp_name` across all cases
- **All of this runs on SQLite queries** — no new infrastructure needed

---

## 07. Overall System Improvements

### Gap 7.1: OFAC Screening Only Checks Exact Addresses — Misses Named Entities
- **Severity:** `MEDIUM`
- **Module:** `engine/ofac_sanctions.py`
- **Summary:** The `screen_ofac_sanctions()` function performs exact address matching. But OFAC also designates named individuals and organizations whose wallet addresses change. If Lazarus Group creates a new wallet not yet in the SDN list, it won't be caught. The UN Security Council 1718 Committee maintains a separate North Korea cryptocurrency sanctions list that is not integrated.

#### Fixes:
- **Fix:** Add fuzzy entity name matching — when an Etherscan label for an address matches a known SDN entity name (e.g., "Lazarus Group", "Tornado Cash"), flag as a soft OFAC hit with lower confidence
- **Add:** Chainalysis free reactor links are publicly published for major hacks. Cross-reference the traced wallets against publicly disclosed hack attribution addresses (Ronin bridge, Harmony bridge)
- **Indian equivalent:** ED/CBI FIR-linked addresses — if any address in the trace appears in published enforcement orders, flag it

---

### Gap 7.2: AI Copilot Prompt Has No Fraud-Type Context — Generic Forensic Output
- **Severity:** `MEDIUM`
- **Module:** `engine/ai_copilot.py`
- **Summary:** The system prompt says "cryptocurrency forensic intelligence reasoning engine" but the user prompt doesn't inject the fraud type (investment scam vs ransomware vs sextortion). The AI generates a generic briefing. A sextortion case briefing and a ransomware case briefing should read completely differently — sextortion requires urgency on victim privacy, ransomware requires decryption timeline context.

#### Fixes:
- **Fix:** Inject `fraud_type` from the case record into the AI prompt: "This is a [INVESTMENT_FRAUD] case. Adjust your investigative recommendations to prioritize [asset freeze over evidence preservation for investment fraud]."
- Add fraud-type-specific instruction addenda to the system prompt that activate based on the case type
- This costs zero extra tokens if done as a conditional append to the system prompt

---

### Gap 7.3: BSC / BNB Chain Is Listed in VASP Registry But Not in Trace Engine
- **Severity:** `HIGH`
- **Impact / PS Alignment:** Data inconsistency
- **Summary:** The VASP registry lists Binance, WazirX, and others as supporting BNB/BSC chain. The cluster data mentions BSC addresses. But the `detect_chain()` function only supports ETH, TRON, BTC, and POLYGON. A BSC address starting with `0x` would be classified as ETH and traced against Ethereum's blockchain — returning wrong or empty results.

#### Fixes:
- **Fix:** BSC addresses are identical format to ETH (`0x...`, 42 chars). Add BSC as a configurable chain with `BSC_RPC_URL` (Ankr provides free BSC RPC: `rpc.ankr.com/bsc`)
- **Chain disambiguation:** When an `0x` address is submitted, check both Etherscan and BSCScan for transaction history. The chain with more transactions in the last 90 days wins
- **VASP registry fix:** Add explicit `chain: "BSC"` labels to BSC-specific hot wallet addresses in `vasp_cluster.py`

---

## Complete Gap Registry — Priority Order

| # | Gap | Module | Severity | PS Alignment | Fix Effort |
|:---:|---|---|:---:|---|:---:|
| 1 | Attribution resolver finds furthest VASP, not nearest | `attribution_resolver.py` | `CRITICAL` | Core PS requirement | 2h |
| 2 | Bridge destination hardcoded — PROVEN evidence fabricated | `trace_engine.py` | `CRITICAL` | Evidence integrity | 3h |
| 3 | Demo mode hardcodes WAZIRX for all cases | `trace_engine.py` | `CRITICAL` | Demo correctness | 30min |
| 4 | MULE_NETWORK fires on missing timestamps via 600s fallback | `mule_network.py` | `CRITICAL` | Evidence accuracy | 1h |
| 5 | No cross-case wallet clustering — organized crime invisible | `database.py` | `CRITICAL` | "clustering" in PS | 3h |
| 6 | PEEL_CHAIN rule likely missing — phantom +15 risk points | `typology_engine.py` | `CRITICAL` | Risk integrity | 2h |
| 7 | DeFi protocols entirely undetected | `trace_engine.py` | `CRITICAL` | "DeFi protocols" in PS | 2h |
| 8 | No automated alert dispatch on CRITICAL risk | `new module` | `CRITICAL` | "automated alerts" in PS | 1.5h |
| 9 | Forward-only BFS — upstream aggregation invisible | `trace_engine.py` | `HIGH` | "fund movement patterns" | 4h |
| 10 | Risk score has no amount factor | `risk_assessment.py` | `HIGH` | Triage logic | 30min |
| 11 | Risk score ignores cross-chain bridge events | `risk_assessment.py` | `HIGH` | "multi-chain" in PS | 30min |
| 12 | Risk score ignores offshore VASP jurisdiction | `risk_assessment.py` | `HIGH` | Freeze coordination | 20min |
| 13 | RAPID_HOP threshold chain-agnostic — BTC false positives | `rapid_hop.py` | `HIGH` | Accuracy | 30min |
| 14 | 90-day cutoff silently drops data with no completeness penalty | `trace_engine.py` | `HIGH` | Data integrity | 1h |
| 15 | Timeout returns empty — no partial checkpoint | `trace_engine.py` | `HIGH` | Reliability | 1h |
| 16 | elapsed_hours defaults to 2.5 — false urgency | `recovery_estimate.py` | `HIGH` | Operational accuracy | 45min |
| 17 | No FIU-IND compliance auto-draft in freeze notice | `notice_generator.py` | `HIGH` | India LEA requirement | 1h |
| 18 | BSC chain listed in registry but not in trace engine | `provider_manager.py` | `HIGH` | Data consistency | 1.5h |
| 19 | No LEA aggregate analytics dashboard | `frontend` | `HIGH` | "analytics dashboards" in PS | 2h |
| 20 | Cycle detection loses convergence typology signal | `trace_engine.py` | `MEDIUM` | Pattern detection | 1h |
| 21 | Hop decay uncapped — deep traces always UNRESOLVED | `adaptive_vasp_scorer.py` | `MEDIUM` | Attribution accuracy | 30min |
| 22 | Single VASP candidate only — no ranked multi-VASP output | `attribution_resolver.py` | `MEDIUM` | "coordination with VASPs" | 2h |
| 23 | No cross-rule compounding in risk score | `risk_assessment.py` | `MEDIUM` | Risk accuracy | 30min |
| 24 | Recovery score has no fraud-type weighting | `recovery_estimate.py` | `MEDIUM` | PS lists 7 fraud types | 1h |
| 25 | OFAC only exact address match — misses entity patterns | `ofac_sanctions.py` | `MEDIUM` | Sanctions accuracy | 2h |
| 26 | AI copilot has no fraud-type context | `ai_copilot.py` | `MEDIUM` | Output relevance | 30min |
| 27 | No scalable blockchain indexing — BFS rescans on every trace | `trace_engine.py` | `LOW` | "scalable indexing" in PS | 8h |
| 28 | No Solana chain support — SOL listed in clusters only | `provider_manager.py` | `LOW` | Coverage | 4h |
| 29 | No INR/USD dual amount display in trace hops | `frontend` | `LOW` | India context | 30min |
| 30 | No geo-mapping of VASP jurisdictions in dashboard | `frontend` | `LOW` | Visual analytics | 2h |
