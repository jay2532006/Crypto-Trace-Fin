# TraceX Sahyog — Win Plan: Gap Closure, Live Product, and Demo
 
 **Problem statement:** SIH 26183 (Crypto asset tracing & attribution for LEAs)  
 **Current Status:** 100% IMPLEMENTED & VERIFIED (129/129 Tests Passing, 10 Baselines)  
 **Historical Baseline:** 168 files, ~69K LOC, 30/30 backend tests passing  
 **Final Verification:** 129/129 backend tests green across 18 test files, zero regressions, all 8 Win Plan phases + 6 logic phases fully complete (see `L1-Logs.md` & `LOGIC_IMPLEMENTATION_PLAN (1).md`)


---

## 0. Read this first — what I verified, and what I found

Everything below was checked against your code, not assumed.

### 0.1 Defects reproduced on the current code

I ran the current `BoundedTracer` (LIVE mode, stubbed provider) on `suspect → Tornado Cash → 2 post-mixer wallets`:

| # | Defect | Evidence | Fix in |
|---|--------|----------|--------|
| D1 | Tracer **expands past the mixer** (`0xpostmixer1`, `0xpostmixer2` traversed) | `addresses expanded` list | Phase 2 |
| D2 | `termination_reason` is `COMPLETE` even after crossing a mixer | output | Phase 2 |
| D3 | **Attribution says "WazirX"** for a case with no exchange. `vasp_key="WAZIRX"` is hardcoded in `trace_engine.py`; `is_exact` checks one hardcoded address | output: `Zanmai Labs Pvt Ltd (WazirX)` | Phase 1 |
| D4 | Mixer node typed `intermediary`, so the frontend's amber hexagon `MIXER` style never fires | node types | Phase 2 |
| D5 | Live-mode hop timestamps are all `int(time.time())`, so `RAPID_HOP` / `MULE_NETWORK` timing is meaningless on live data | `trace_engine.py` live loop | Phase 1 |
| D6 | `elapsed_hours=14.0` hardcoded, so "Time to Action" can't reflect a real complaint | `trace_engine.py` | Phase 5 |
| D7 | `cross_chain_analyzer` is **never called** from the trace path; fixture 03's expected typology is `RAPID_HOP`, so nothing in the demo yields a `CrossChainLink` | grep + fixture | Phase 3 |
| D8 | `CaseSource` literal has no `"NCRP"`, but `ncrp_adapter` writes `source: "NCRP"` | `confidence_types.py` | Phase 0 |
| D9 | `0x28c6c062…` appears under **both** WAZIRX and BINANCE in `vasp_registry.py`; first-match silently wins | registry | Phase 1 |
| D10 | Neither adapter is reachable over HTTP; there is no route for SAHYOG/NCRP ingest | `app.py` router list | Phase 4 |

### 0.2 Things I checked that turned out fine (so you don't waste time)

- `create_case` accepts both a dict and kwargs, and `canonical_db is db_manager`, so the SAHYOG adapter and the case route do **not** conflict.
- Recovery logic **already** forces `ineligible` when a mixer is detected, and fixture 02 already expects that. Gap 2 is a tracer + UI problem, **not** a scoring rewrite.
- Adapter validation (private-key and seed-phrase rejection, idempotency, audit logging) is solid. Phase 4 wraps it; it does **not** rewrite it.



### 0.3 Architecture constraint: two parallel stacks

The repo has a **legacy stack** (`engine/` + `POST /api/trace` → `dashboard.html`) and a **new stack** (`backend/` + `/api/v1/*` → Next.js). **All new work lands in the new stack** (`backend/` + `frontend/`). The legacy stack is left untouched except for one optional demo bridge (Phase 7.4). This is the main "no damage" guarantee.

---

## 1. Guiding rules (the "no damage" contract)

1. **Additive only.** New modules, new routes, new optional fields. No signature changes to existing public functions.
2. **Feature-flagged.** Every behavioural change ships behind a flag defaulting to the *old* behaviour until its tests pass (see §2).
3. **Old response keys are frozen.** New keys are added; none renamed or removed. The existing frontend and `test_phase2_api.py` keep working.
4. **`case_id` derivation is frozen.** `test_ncrp_valid_ingest_and_unauthorized_boundary` asserts `case_id == unique_ack`; do not change ID logic.
5. **Green gate.** Every phase ends with `pytest backend/tests -q` → **≥ 30 passed, 0 failed** *plus* the new tests for that phase.
6. **Honesty over polish.** Anything demo-only is labelled `DEMO` in the UI and API (`demo_data: true`). We never present fixture output as live output. This is also what makes it credible to judges (see §10).

## 2. Feature flags (add to `backend/config/base.py`)

| Flag | Default | Enables |
|------|---------|---------|
| `TRACE_STOP_AT_MIXER` | `true` | Phase 2 mixer boundary halt |
| `TRACE_CROSS_CHAIN` | `true` | Phase 3 bridge detection in tracer |
| `INTAKE_ENABLED` | `true` | Phase 4 `/api/v1/intake/*` routes |
| `INTAKE_AUTOTRACE` | `false` | Auto-run trace on intake (off in prod; on for demo) |
| `DEMO_SEED_ON_START` | `false` | Phase 7 seeds demo cases |

Each flag is read once via the existing config module. If a flag is off, the code path is byte-for-byte the current behaviour.

---

## PHASE 0 — Safety net and baseline (½ day)

**Objective:** Lock in "30 green" and make regressions impossible to miss.

| Task | Detail |
|------|--------|
| 0.1 Snapshot baseline | Tag `pre-winplan`. Record `pytest backend/tests -q` = 30 passed. |
| 0.2 Golden-output test | New `backend/tests/test_golden_baseline.py`: run the **DEMO-mode** tracer on the three fixtures and assert the *current* key set + `typologies` + `termination_reason`. Any accidental change to the demo path fails here first. |
| 0.3 Fix D8 | Add `"NCRP"` to `CaseSource` in `confidence_types.py` (additive Literal member). |
| 0.4 CI | `.github/workflows/ci.yml`: install `requirements.txt` **plus** `pytest httpx PyJWT bcrypt`, run pytest, run `npm run build` in `frontend/`. Note: `requirements.txt` is missing test deps, so document that or add `requirements-dev.txt`. |
| 0.5 Secret scan | Add `gitleaks` pre-commit hook (§0.3). |

**Exit criteria:** 30 + golden tests green; CI green on a clean checkout.

---

## PHASE 1 — Attribution correctness (1 day) — *fixes D3, D5, D9*

**Why first:** a live demo where a ransomware case is attributed to WazirX destroys trust faster than any missing feature.

### 1.1 Attribution resolver (new file, additive)

`backend/attribution/attribution_resolver.py`

```python
class AttributionResolver:
    def resolve(self, trace_result) -> ResolvedAttribution:
        """
        Walk terminal/deposit nodes of the trace; match each against VASP_REGISTRY
        hot_wallet_patterns (case-insensitive, chain-aware).
        - 0 matches  -> vasp_key=None  -> label UNRESOLVED  (never default to WAZIRX)
        - 1 match    -> that vasp_key
        - >1 match   -> AMBIGUOUS: return all candidates, cap confidence at MEDIUM   (fixes D9)
        """
```

### 1.2 Wire into `trace_engine.py` (minimal diff)

Replace only the two hardcoded lines:

```python
# BEFORE
is_exact = any("28c6c062" in h.get("to_address","").lower() for h in hops)
attribution = adaptive_vasp_scorer.score_candidate(vasp_key="WAZIRX", ...)
# AFTER
resolved = attribution_resolver.resolve(raw_result)
attribution = adaptive_vasp_scorer.score_candidate(
    vasp_key=resolved.vasp_key or "UNKNOWN", is_exact_wallet_match=resolved.exact, ...)
```

`score_candidate` already handles unknown keys (falls back to `vasp_info` default at line ~57) and already emits `UNRESOLVED`, so **no scorer changes**.

**DEMO path guard:** the DEMO fixture branch keeps `mule_wallets[-1] = 0x28c6…` and `WAZIRX`, so golden test (0.2) still passes. Only LIVE resolves dynamically.

### 1.3 Duplicate-wallet policy (D9)

Keep the registry data unchanged (no data damage); resolver treats a multi-VASP address as `AMBIGUOUS` and the UI shows "Shared hot wallet: WazirX / Binance, confirm via both nodal officers". This is more honest *and* more useful to an investigator.

### 1.4 Real timestamps (D5)

`Transfer.timestamp` already exists in the model. In the live loop set `timestamp_epoch` from `t.timestamp` (ISO → epoch), falling back to current time **only** if absent, and record `timestamp_source: "CHAIN" | "FALLBACK"` on the hop so typology rules and the UI can discount fallback timing.

**Tests** (`test_phase5_attribution.py`):
- ransomware/mixer trace → `label_type == "UNRESOLVED"`, `vasp_name != WazirX`
- trace ending at `0x21a31ee1…` → Binance, exact
- trace ending at `0x28c6c062…` → `AMBIGUOUS`, confidence ≤ MEDIUM, both candidates listed
- hop timestamps come from `Transfer.timestamp` when present
- DEMO fixture 01 unchanged (golden test)

**Exit:** all green; the mixer demo no longer names an exchange.

---

## PHASE 2 — Mixer / tumbler handling (Gap 2: 25% → ~85%) (1.5 days)

**Design principle:** a forensic tool must *stop honestly* rather than trace through cryptographic obfuscation. It stops, explains why, and still gives the officer something actionable.

### 2.1 Tracer changes (`trace_engine.py`, behind `TRACE_STOP_AT_MIXER`)

1. Extend `KNOWN_MIXERS` into a shared module `backend/typologies/mixer_registry.py` (mixer_boundary.py imports from it; **same 4 addresses preserved**). Add more Tornado Cash pools (100 ETH, 0.1/1/10/100 ETH on other chains) and a `category` field: `MIXER | PRIVACY_POOL | NO_KYC_SWAP`.
2. In the live loop, after computing `to_addr`: if it's a known mixer → append the edge, create the node with **`type: "mixer"`** (fixes D4; the frontend already styles `MIXER`), **do not enqueue** it, and record a boundary event.
3. New fields on the result (additive):

```json
"termination_reason": "MIXER_BOUNDARY_HIT",
"boundary_events": [{
  "kind": "MIXER", "name": "Tornado Cash (1 ETH)", "address": "0x910c…",
  "hop_number": 1, "deposit_amount": 30.0, "asset": "ETH",
  "why_stopped": "Fund flow beyond this point is cryptographically obfuscated. Onward addresses cannot be attributed to the depositor.",
  "search_window_seconds": 14400
}],
"partial_recommendation": { … }
```

`termination_reason` precedence: `TIMEOUT` > `MIXER_BOUNDARY_HIT` > `MAX_NODES` > `MAX_HOPS` > `COMPLETE`. Multiple boundaries are all listed; the tracer keeps tracing **other branches** that don't cross a mixer.

### 2.2 Partial investigative recommendation (the "what now?" the evaluation flagged)

`backend/legal/mixer_recommendation.py` produces a recommendation even though the trace stopped:
- **Pre-mixer freeze:** request freeze on all *pre-mixer* nodes and the depositing address (still actionable).
- **Deposit evidence package:** tx hash, block, amount, timestamp, mixer name for the court record.
- **Payout-side watch (LEAD only, never proof):** list candidate exits from the existing `+14,400 s` / `0.90–0.995` heuristic, each labelled *"Possible Exit — Heuristic Only"*, with the existing uncertainty text.
- **Off-chain leads:** IP/device logs and KYC from the *funding-side* VASP (if one is upstream), plus victim-side communications.

Wire into `notice_generator` as an optional `partial_recommendation` section so notices generated from a mixer-terminated trace don't silently omit context.

### 2.3 Frontend (`CytoscapeGraph.tsx`, additive)

- Render the `MIXER` node with a **red terminal marker** and a "TRACE TERMINATED" badge; dashed amber inbound edge (already styled).
- Tooltip / side panel = the `why_stopped` text.
- New `frontend/components/forensic/TraceBoundaryCard.tsx`: uncertainty card ("Trace terminated at Tornado Cash (1 ETH). Beyond this point flows are obfuscated. Heuristic exit candidates below are leads, not proof."). Reuse `UncertaintyBanner` styling.
- Add `boundary_events`, `termination_reason` to `frontend/types/domain.ts` as optional fields.

### 2.4 Privacy-coin awareness (scorecard says "no Monero/Zcash")

Be honest rather than fake it: add `backend/typologies/rules/privacy_asset.py` that flags **exposure** to XMR/ZEC-related bridges and no-KYC swap services (`category: NO_KYC_SWAP`) as a boundary, identical UX to a mixer. **We do not claim to trace Monero.** The limitation goes in `docs/LIMITATIONS.md`, and judges tend to reward honest scoping over overclaiming.

**Tests** (`test_phase6_mixer_boundary.py`, using the same stub-provider technique I used to reproduce D1):
- suspect → mixer → post-mixer: post-mixer addresses **not** expanded
- `termination_reason == "MIXER_BOUNDARY_HIT"`, one `boundary_events` entry, mixer node `type == "mixer"`
- two-branch trace: clean branch continues, mixer branch halts
- recovery `display_tier == "ineligible"` (regression: existing rule still fires)
- attribution label `UNRESOLVED` (depends on Phase 1)
- `TRACE_STOP_AT_MIXER=false` → old behaviour exactly (golden)
- `partial_recommendation` present, every exit candidate labelled heuristic, confidence ≤ 0.25
- fixture `CR-2026-MIXER-BOUND-02` end-to-end

**Exit:** the reproduction script from §0.1 now shows 1 address expanded past the boundary (the mixer itself, not beyond) and `MIXER_BOUNDARY_HIT`.

---

## PHASE 3 — Cross-chain bridge tracing (Gap 3: 50% → ~85%) (2 days)

### 3.1 Bridge registry (`backend/cross_chain/bridge_registry.py`, new)

Data-driven registry (JSON-backed, unit-testable), each entry: `protocol`, `chain`, `contract_addresses`, `event_topic`, `decoder`, `dest_chain_id_field`, `verification_source`.

Ship 3 real, decodable bridges rather than a long fake list:
1. **Stargate / LayerZero** (ETH ⇄ BSC/POLYGON/ARB)
2. **Across** (EVM ⇄ EVM)
3. **Wormhole** token bridge (ETH ⇄ TRON/Solana where applicable)

> ⚠️ **Verify before demo:** contract addresses and event signatures must be re-checked against each protocol's official docs and a block explorer at build time. I have not looked them up in this session and do not want to hand you addresses from memory that could be wrong or stale. Put each in the registry with a `source_url` and `verified_on` date, and add a test that fails if `verified_on` is empty.

### 3.2 Bridge detection in the tracer (behind `TRACE_CROSS_CHAIN`)

When a hop's `to_addr` is a registered bridge contract:
1. Decode the deposit tx (adapter already exposes `EventType = "BRIDGE"`) → destination chain + recipient + amount.
2. Call `cross_chain_analyzer.analyze_cross_chain(..., bridge_tx_hash=<deposit tx>)` → `PROVEN` **only if** the destination-chain delivery event is found and the message ID / nonce matches; otherwise fall back to `HEURISTIC_CORRELATION`.
3. Continue the trace on the destination chain with `start_address = decoded recipient`, `chain = dest`, `depth` preserved (bridge hop counts as one hop). Add `chain` to each node.
4. Append to `cross_chain_links[]` (additive key).

**Fix in analyzer (small, additive):** it currently hardcodes `"bridge_protocol": "Across / LayerZero"`. Take `bridge_protocol` as an optional parameter defaulting to that string, so existing callers are unchanged.

### 3.3 Graph and UI

- Cytoscape: **dashed cyan cross-chain edge** with a chain badge on each node; `PROVEN` = solid cyan + shield icon, `HEURISTIC` = dotted grey + "unverified" label.
- New "Cross-chain links" panel listing protocol, both tx hashes, and `PROVEN`/`HEURISTIC` with the disclaimer.
- Multi-chain legend and per-chain node colouring.

### 3.4 The guaranteed demo case (fixture 03 upgrade)

Add `CR-2026-BRIDGE-XCHAIN-04` with a **recorded** real bridge transaction pair, stored as raw payloads under `data/raw/` using the repo's existing manifest/hash convention so it replays deterministically offline **and** is auditable. Selecting fixture 03/04 in DEMO mode replays it; in LIVE mode the same logic runs on real data. Choose the historical tx pair at build time from a block explorer (again: not fabricated).

**Tests** (`test_phase7_cross_chain.py`):
- decoder unit tests against recorded log payloads
- `PROVEN` requires matching dest-side event; missing dest event → `HEURISTIC_CORRELATION` (never `PROVEN`)
- amount/time tolerance boundaries (5%, 3600 s), including exactly-on-boundary
- trace continues on destination chain; `depth` and `chain` correct
- registry completeness test (`source_url`, `verified_on` present)
- `TRACE_CROSS_CHAIN=false` → old behaviour (golden)

**Exit:** demo case renders a two-chain graph with one `PROVEN` edge.

---

## PHASE 4 — SAHYOG / NCRP live intake (Gap 1: 35% → ~85%) (2 days)

**Insight from the code review:** the adapters are already good. What's missing is the *door* (HTTP routes) and the *bridge to the tracer*.

### 4.1 Routes (`backend/api/intake_routes.py`, new; register in `backend/api/__init__.py` and `app.py`)

| Endpoint | Purpose | Auth |
|----------|---------|------|
| `POST /api/v1/intake/ncrp/complaint` | NCRP-style complaint → `ncrp_adapter.ingest_ncrp_complaint` | `INTEGRATION_SERVICE` role or service token |
| `POST /api/v1/intake/sahyog/bulletin` | Bulletin → `sahyog_adapter.ingest_bulletin` | same |
| `GET  /api/v1/intake/status` | Both `get_connection_status()` results | any authenticated user |
| `GET  /api/v1/intake/queue` | Recent intakes with trace status | investigator+ |
| `POST /api/v1/intake/{case_id}/trace` | Kick off trace for an ingested case | investigator+ |

`INTEGRATION_SERVICE` already exists in `UserRole`, and `rbac.py` is the place to add the permission. Reuse existing JWT, RBAC, and `audit_engine`.

### 4.2 Intake → trace orchestration (`backend/ingestion/intake_orchestrator.py`, new)

```
complaint/bulletin ──► adapter (validate, reject keys/seed, dedupe, create case)
                   ──► [if INTAKE_AUTOTRACE] enqueue trace (FastAPI BackgroundTasks)
                   ──► trace → attribution → typologies → risk → recovery
                   ──► generate preservation-notice DRAFT (status=DRAFT, needs supervisor)
                   ──► audit chain entries at every step
```

- **Human-in-the-loop preserved:** notices stay `DRAFT → PENDING_APPROVAL`; nothing is auto-sent. That aligns with the existing governance model and is a plus for LEA judges.
- **Idempotent:** replaying the same ack/bulletin returns `EXISTING`/`ALREADY_EXISTS` (already implemented).
- **Persist the trace against the case** (existing `trace_id` on `PreservationRequestDraft`).

### 4.3 Real bug to fix while here

`SAHYOGAdapter.processed_bulletin_hashes` is an **in-memory set**, so dedupe is lost on restart, and the hash is computed from `bulletin_id + agency + len(wallets)` only (two different bulletins with the same ID/agency/wallet count collide, and a *changed* bulletin silently dedupes). Fix: persist the hash in the DB (new table `intake_dedupe`, additive migration `002_intake.sql`) and hash the canonicalised content. Keep `ALREADY_EXISTS` semantics so existing tests pass.

### 4.4 Honest boundary + mock gateway

Keep the adapters' `UNAVAILABLE_UNAUTHORIZED` behaviour (correct per PRD, never fake a government connection). For the demo, add a **clearly-labelled sandbox mode**:

- `scripts/mock_ncrp_gateway.py` — a tiny FastAPI app that *emits* NCRP-shaped complaints and SAHYOG-shaped bulletins to your `/intake` endpoints, like a real upstream would.
- UI shows **`SANDBOX GATEWAY — NOT A LIVE MHA CONNECTION`** on the Intake page. When real credentials are set, the badge flips to the adapter's real status.

This answers the judge's "how does a complaint enter your system?" with a running end-to-end flow **without ever claiming a live government link**. Say it that way in the pitch.

### 4.5 Frontend: Intake page (`frontend/app/(workspace)/intake/page.tsx`, new)

- Live intake feed (poll or SSE) with per-row state: `RECEIVED → VALIDATED → TRACING → ATTRIBUTED → NOTICE DRAFTED`.
- Gateway status chip (sandbox vs. authorized).
- Rejection panel showing **rejected** payloads (private-key / seed-phrase) with the security reason, a great demo moment.
- Add to `Sidebar.tsx`.

**Tests** (`test_phase8_intake_api.py`):
- valid complaint → 200, case exists, audit entry chained
- private key / mnemonic → rejected, **no case created**, rejection audited
- replay → idempotent
- bulletin with 3 wallets across ETH/TRON/BTC → 3 wallets linked
- dedupe survives a fresh `SAHYOGAdapter()` instance (persistence fix)
- changed bulletin content with same ID is **not** silently deduped
- RBAC: investigator token cannot post to service-only ingest; no token → 401
- `INTAKE_AUTOTRACE=true` → trace persisted + notice `DRAFT`, never auto-approved
- existing `test_phase4_external_boundaries.py` passes unchanged

**Exit:** `curl` a complaint at the endpoint → watch it appear, trace, attribute, and produce a draft notice with no manual steps.

---

## PHASE 5 — "High priority" UI story (1 day)

| Item | Implementation |
|------|----------------|
| **VASP confidence band prominent (eval #4)** | New `CaseSummaryCard` at the top of the case view: attribution name, `VERIFIED/INFERRED/UNRESOLVED` chip, confidence band, hop distance. Reuse `ConfidencePill`. Expandable **scoring accordion** showing `scoring_steps` (mixer −30, hop distance, jurisdiction bonus). |
| **Time-to-Action banner (eval #5, fixes D6)** | Compute `elapsed_hours` from `case.created_date` (or `reported_at`) to now instead of the hardcoded `14.0`; expose `action_window_hours` + deadline timestamp. Banner: "Estimated action window: **N h**: freeze request recommended now". Colour by urgency (<6 h red). Show *ineligible* state honestly with reasons. |
| **Data completeness on findings (eval #9)** | Render `data_completeness_pct` on every `PatternFinding` and the "capped at MEDIUM because we saw 60% of the data" explanation. |

**Tests:** elapsed-hours computation (frozen clock), banner state matrix (eligible/ineligible × urgent/normal), component tests for the card.

---

## PHASE 6 — Medium priority: strengthen the story (1.5 days)

### 6.1 AI Copilot demo moment (eval #6)
`engine/ai_copilot.py` already has `recommend_actions`, `summarize_case`, and `generate_investigation_report`, with Groq/Gemini + rule-based fallback. Work:
- Expose them on the **new** stack: `POST /api/v1/copilot/{case_id}/recommend` (thin wrapper, no logic change).
- "AI Copilot" panel on the case page with streaming-style output and a visible **provider badge** (`Groq` / `Gemini` / `Rule-based fallback`) so a network failure during the demo degrades gracefully and honestly.
- **Guardrail:** the copilot must only cite fields present in the trace (no invented addresses/amounts). Add a post-check that every `0x…`/`T…` string in the output exists in the trace; strip/flag otherwise. This turns a hallucination risk into a demonstrated safeguard.
- **Rate-limit + cache** by `(case_id, trace_hash)` to stay inside free-tier quotas during judging.

### 6.2 Standardised PDF investigation report (eval #7)
- `backend/legal/report_generator.py` → PDF via `reportlab` (add to requirements). Sections: case header, complaint source (NCRP/SAHYOG ref), executive summary, fund-flow graph image, hop table with tx hashes, attribution + confidence + scoring steps, typologies with uncertainty notes, boundary events, cross-chain links, risk, recovery/action window, evidence manifest hashes, audit-chain head hash, disclaimers.
- **Determinism:** same input → same PDF bytes (fixed metadata timestamp) so the report hash can be stored in the evidence manifest.
- `GET /api/v1/cases/{id}/report.pdf`, RBAC-guarded and audited.
- Graph image: render server-side from NetworkX/matplotlib (don't depend on the browser).

### 6.3 Demo-ready fixtures
Extend `demo_cases_v2.py` (additive) with: `…-04` bridge case, an OFAC-hit case (eval #8, below), and a mule-network case with a real-looking fan-in. All tagged `demo_data=True`.

---

## PHASE 7 — Lower priority + the demo experience (1.5 days)

### 7.1 OFAC variant (eval #8)
`engine/ofac_sanctions.py` exists but `raw_result["ofac_sanction_hit"]` is hardcoded `False` in the new tracer. Wire `ofac_sanctions` into the tracer (behind a flag) so any traversed address on the SDN list sets `ofac_sanction_hit`, adds the +45 risk component, and shows a **red sanctions banner**. Include a demo case hitting a **publicly listed** SDN address (verify against the current OFAC SDN list at build time; do not rely on memory).

### 7.2 Recovery estimate polish
Add a per-factor breakdown chart (cooperation / time / path / attribution) to the Recovery page: this makes the "not a probability" disclaimer feel deliberate rather than defensive.

### 7.3 Guided demo mode (`frontend/app/(workspace)/demo/page.tsx`)
A one-click **Guided Demo** that walks the 3 scenarios in a fixed order with narration captions, mapped to the scorecard so judges see each gap closing:

| Step | Scenario | What it proves |
|------|----------|----------------|
| 1 | Mock NCRP complaint arrives (sandbox gateway) | Entry point, security rejection, audit chain |
| 2 | **Mule network** trace, TRON → WazirX-cluster | Your differentiator: MULE_NETWORK, VASP `VERIFIED`, scoring accordion |
| 3 | **Cross-chain** ETH → bridge → TRON → exchange | `PROVEN` vs heuristic |
| 4 | **Mixer** ransomware → Tornado | Honest stop, boundary card, partial recommendation, `UNRESOLVED` |
| 5 | Time-to-Action banner + Copilot recommendation | Actionability |
| 6 | Download PDF report + notice DRAFT → supervisor approve | Standardised reports, governance |
| 7 | Audit chain verify | Tamper-evidence |

Include a **"Demo / Live" toggle** with an unmissable `DEMO DATA` ribbon in demo mode, and a **fail-safe**: every step has an offline cached fixture, so a dead Wi-Fi at the venue can't break the demo.

### 7.4 Legacy dashboard bridge (optional)
`dashboard.html` (legacy) stays as is. If judges may open it, add one link/banner pointing to the new workspace, with no logic changes.

---

## PHASE 8 — Hardening, verification, release (1.5 days)

### 8.1 Security
- Rotate all leaked keys (§0.3); confirm none in git history (`git filter-repo` if needed).
- `SECRET_KEY` currently = `cryptotrace-lea-insecure-dev-secret-key-32charsmin`; **fail startup if `APP_ENV=production` and the default is in use.**
- Rate-limit intake endpoints; request-size limit (bulletins can be large); CORS from env only.
- Confirm the mnemonic detector isn't a false-positive machine: its BIP-39 regex list in the dump is a **truncated subset** (a-b words only), so it will miss most seed phrases starting with c–z. Replace with the full 2048-word list (bundled file) and require ≥12 *consecutive* matches. This is a real gap in a "security safeguard" you advertise.
- Dependency audit (`pip-audit`, `npm audit`).

### 8.2 Performance / resilience
- Tracer: per-provider timeout + retry with backoff; provider failure → `data_completeness_pct` drops and is shown, not a crash.
- Cache `fetch_transfers` per `(chain, address)` within a trace.
- Load test intake (50 concurrent complaints) and a 1000-node trace; assert the timeout path returns `TIMEOUT` with partial results.

### 8.3 Verification matrix (run before demo day)

| Requirement (SIH 26183) | Verified by |
|------------------------|-------------|
| Wallet ingestion via NCRP/SAHYOG | `test_phase8_intake_api` + guided demo step 1 |
| Multi-chain tracing (BTC/ETH/TRON) | adapter tests + live smoke script `scripts/verify_apis.py` |
| Mixer/tumbler challenge | `test_phase6_mixer_boundary` + demo step 4 |
| Cross-chain | `test_phase7_cross_chain` + demo step 3 |
| Exchange/VASP attribution w/ confidence | `test_phase5_attribution` + scoring accordion |
| Laundering-pattern detection | typology tests + MULE_NETWORK demo |
| Risk categorisation | existing risk tests + component breakdown |
| Standardised report | PDF determinism test + demo step 6 |
| Evidence integrity / audit | audit chain verify + evidence manifest tests |
| No regression | **30 baseline + golden tests green** |

### 8.4 Definition of done
- [ ] `pytest backend/tests -q` → all green (30 baseline + new)
- [ ] `npm run build` and `tsc --noEmit` clean; no console errors on any page
- [ ] Golden-output tests unchanged for DEMO mode
- [ ] Every flag OFF → behaviour identical to `pre-winplan` tag (diff the golden JSON)
- [ ] Demo rehearsed **offline** end-to-end twice, under 6 minutes
- [ ] Keys rotated; `gitleaks` clean

---

## 9. Schedule (≈ 12 working days; compress by parallelising)

```
Day 1     Phase 0 + Phase 1                     (baseline, attribution correctness)
Day 2-3   Phase 2 (mixer)      ║ Phase 4 (intake) in parallel — different files
Day 4-5   Phase 3 (cross-chain)║ Phase 4 continued
Day 6     Phase 5 (UI story)
Day 7-8   Phase 6 (copilot, PDF)
Day 9     Phase 7 (OFAC, guided demo)
Day 10-11 Phase 8 (hardening, verification, rehearsal)
Day 12    Buffer / bug bash
```

**If time is short, cut in this order (keep 1–3):**
1. Phase 1 (attribution fix): cheap and the biggest credibility risk
2. Phase 2 (mixer): honest stop + boundary card
3. Phase 4 (intake) with sandbox gateway: the judges' first question
4. Phase 3 (cross-chain): one recorded `PROVEN` hop
5. Phases 5–7 polish, in that order
6. Drop: privacy_asset rule, legacy-dashboard link, extra bridges

## 10. Positioning for judges (what to say and not say)

- **Lead with:** *"A victim reports a wallet: what does the investigating officer see in 60 seconds?"* Then run the guided demo.
- **Be explicit about sandbox vs. live.** Say: *"Government gateways are sandboxed here because we don't have MHA credentials. The adapter reports `UNAVAILABLE_UNAUTHORIZED` rather than faking a connection, and flips to live the moment credentials are configured."* This reads as forensic integrity, which is the point of the product.
- **Turn limitations into features.** Mixer stop, `UNRESOLVED` labels, `HEURISTIC_CORRELATION`, and "ineligible for recovery" are your credibility. A tool that never says "I don't know" isn't trustworthy for evidence.
- **Don't claim** to trace Monero, de-anonymise mixers, or have a live NCRP link.
- **On SIH 26182 overlap:** the differentiator is *complaint-in, officer-actionable-out* (NCRP intake → India-specific MULE_NETWORK → FIU-status-aware VASP attribution → recovery window → BNSS §91 notice draft), not a general blockchain explorer.

## 11. Risk register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Live RPC/Etherscan rate-limits or outage during judging | High | Offline replay fixtures for every demo step; provider badge; cached results |
| Copilot API quota/latency | Medium | Rule-based fallback already exists; cache; visible provider badge |
| Bridge contract addresses/ABI wrong | Medium | Verify against official docs + explorer; `verified_on` test; recorded payload replay |
| Regression in legacy `dashboard.html` | Low | Untouched by design; smoke test `GET /` and `POST /api/trace` in CI |
| Scope creep | High | Phase order above; cut list in §9 |
| Leaked keys abused | High (already exposed) | Rotate today |

## 12. File-change summary

**New:** `backend/attribution/attribution_resolver.py`, `backend/typologies/mixer_registry.py`, `backend/typologies/rules/privacy_asset.py`, `backend/legal/mixer_recommendation.py`, `backend/legal/report_generator.py`, `backend/cross_chain/bridge_registry.py`, `backend/api/intake_routes.py`, `backend/ingestion/intake_orchestrator.py`, `backend/db/migrations/002_intake.sql`, `scripts/mock_ncrp_gateway.py`, 6 new test files, `frontend/app/(workspace)/{intake,demo}/page.tsx`, `frontend/components/forensic/{TraceBoundaryCard,CaseSummaryCard,TimeToActionBanner,CopilotPanel}.tsx`, CI workflow.

**Modified (additive):** `trace_engine.py` (3 targeted edits), `mixer_boundary.py` (import registry), `cross_chain_analyzer.py` (optional param), `confidence_types.py` (+`NCRP`), `sahyog_adapter.py` (persist dedupe), `ncrp_adapter.py` and `sahyog_adapter.py` (full BIP-39 list), `demo_cases_v2.py` (+fixtures), `CytoscapeGraph.tsx`, `domain.ts`, `Sidebar.tsx`, `base.py` (flags), `requirements.txt`.

**Untouched:** `engine/*`, `dashboard.html`, `index.html`, scorer internals, risk/recovery formulas, audit engine, auth.
