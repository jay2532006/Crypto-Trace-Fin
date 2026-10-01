# CryptoTrace LEA — Security & Governance Policy

## 1. Attack Surface Hardening & Lockdowns

Per PRD Section 18.2, 19.3, and the Phasewise Implementation Plan, high-risk testing endpoints from legacy TraceX have been strictly disabled:

### 1.1 Unrestricted Cypher Execution
- **Endpoint**: `POST /api/neo4j/query`
- **Enforcement**: Permanently returns `403 Forbidden`.
- **Rationale**: Direct arbitrary query execution against the graph database presents a critical Cypher injection vulnerability and allows unauthorized data exfiltration.

### 1.2 Arbitrary Outbound HTTP Execution
- **Endpoint**: `POST /api/test/custom`
- **Enforcement**: Permanently returns `403 Forbidden`.
- **Rationale**: Permitting investigators to enter arbitrary URLs and headers creates a Server-Side Request Forgery (SSRF) vector against internal government networks.

### 1.3 Secret Management & Immutability
- **Policy**: No runtime `.env` modification through HTTP endpoints.
- **Enforcement**: All API keys, RPC credentials, and JWT signing keys are loaded strictly from the system environment via `backend/config/base.py`. Secrets are excluded from application logs and API response payloads.

---

## 2. Role-Based Access Control (RBAC) & Intake Authentication

The system enforces four canonical roles:

| Role | Permissions |
|---|---|
| `INVESTIGATOR` | Create cases, execute bounded forensic traces, submit complaints via NCRP intake, draft Section 91 notices, export dossiers. |
| `SUPERVISOR` | All Investigator permissions, plus approve/reject Section 91 preservation directives, sign court disclosures. |
| `ADMINISTRATOR` | Full system access, manage agency users, configure provider backbones, inspect cache statistics. |
| `INTEGRATION_SERVICE` | Automated ingest of complaint feeds from NCRP / I4C SAHYOG; cannot approve notices or delete cases. |

### 2.1 NCRP Intake Role Fix (§8.5)
- **Endpoint**: `POST /api/v1/intake/ncrp/complaint`
- **Security Rectification**: Previously, the endpoint strictly required `INTEGRATION_SERVICE` or `ADMINISTRATOR`, causing a `403 Forbidden` error when human investigators submitted complaints via the investigator workstation UI.
- **Implementation**: In `backend/api/intake_routes.py`, `_INTAKE_ALLOWED_ROLES` explicitly includes `{"INVESTIGATOR", "ADMINISTRATOR", "INTEGRATION_SERVICE"}`.
- **Verification**: Verified by `backend/tests/test_phase0_logic_fixes.py::TestNcrpIntakeAuth::test_ncrp_intake_accepts_investigator_role`.

---

## 3. Cryptographic Tamper-Evident Audit Trail

1. **Chained SHA-256 Ledger**: Every mutation is logged with an event hash calculated as:
   $$\text{Hash}_n = \text{SHA256}(\text{Hash}_{n-1} \parallel \text{EventID} \parallel \text{Timestamp} \parallel \text{Actor} \parallel \text{Action} \parallel \text{Resource} \parallel \text{Details})$$
2. **Continuous Verification**: The `/api/v1/audit/verify-chain` endpoint and dashboard modal allow supervisory officers to verify that no records in the audit log have been altered or deleted.

---

## 4. Resilience & Blast-Radius Mitigation Controls

### 4.1 Provider Circuit Breaker (§8.2)
- **Component**: `ProviderCircuitBreaker` in `backend/adapters/provider_manager.py`
- **Mechanism**: Tracks consecutive HTTP failures and rate limits per provider URL. Trips after `FAILURE_THRESHOLD = 3` consecutive failures or HTTP 429 responses, entering an `OPEN` state for `OPEN_DURATION_S = 60.0` seconds. After cooldown, permits a single half-open probe request.
- **Security Impact**: Prevents cascading connection exhaustion and limits the blast radius of a compromised, malicious, or malfunctioning RPC node returning malformed or slow responses. The cascading waterfall immediately fails over to secondary RPCs without halting the pipeline.

### 4.2 Cross-Chain Cache Isolation (§8.3)
- **Component**: `CacheManager` / `TTLCache` in `backend/cache/cache_manager.py`
- **Key Scoping**: Address cache keys are strictly isolated per blockchain and address: `addr:{chain.upper()}:{address.lower()}`.
- **Security Impact**: Eliminates cross-chain collision vulnerabilities where identical hexadecimal addresses across EVM chains (Ethereum, Polygon, BSC) or format overlaps might otherwise lead to cache poisoning or cross-case data leakage.
- **Read-Through Transparency**: Cold and warm cache queries produce byte-identical results, guaranteeing evidence integrity.

---

## 5. Automated Alert Dispatch & Law Enforcement Push

### 5.1 Real-Time Alert Dispatch (§7.1)
- **Component**: `AlertDispatcher` in `backend/alerts/alert_dispatcher.py`
- **Trigger Conditions**: Automatically triggers whenever a trace resolves to `risk_category == "CRITICAL"` or `ofac_sanction_hit == True`.
- **Integration Points**:
  - Writes to canonical SQLite `alerts` table for LEA auditing and `/api/v1/alerts` retrieval.
  - Outbound webhook integration configured via environment variable `ALERT_WEBHOOK_URL` (with 3-second non-blocking timeout).
  - Outbound notification via `ALERT_RECIPIENT_EMAIL` when SMTP is configured.

---

## 6. OFAC Sanctions Screening & Fuzzy Entity Resolution

### 6.1 Address Screening & Traversal Halting
- Traversed addresses are screened against the US Treasury OFAC Specially Designated Nationals (SDN) registry.
- An exact address match applies a +45 risk bump, forces the risk category to `CRITICAL`, halts BFS traversal at the sanctioned node, marks attribution as `UNRESOLVED`, and triggers immediate alert dispatch.

### 6.2 Fuzzy Entity-Name Matching (§Phase 5 Polish)
- **Component**: `fuzzy_screen_ofac_entity()` and `bulk_fuzzy_screen_entities()` in `engine/ofac_sanctions.py`
- **Algorithm**: Uses `difflib.SequenceMatcher` to evaluate query strings against known sanctioned entities, aliases, and parenthetical qualifiers with a similarity threshold of `0.85`.
- **Capabilities**: Supports sliding-window token matching, direct substring matching, and bulk entity screening for batch investigative intakes.

---

## 7. Regression Anchors & Baseline Integrity

### 7.1 Immutable Golden Baselines
- 10 reference trace snapshots are archived in `backend/tests/fixtures/baselines/` covering all benchmark scenarios (mule networks, mixer boundaries, OFAC hits, bridge crossings, fan-in patterns).
- **Integrity Guard**: `backend/tests/test_phase0_logic_fixes.py::TestBaselineSnapshots::test_baseline_snapshots_exist_and_are_complete` validates the presence of all 10 baseline files and verifies that each snapshot contains all 9 required evidentiary keys (`case_id`, `hops`, `nodes`, `edges`, `attribution`, `typologies`, `recovery_estimate`, `boundary_events`, `data_completeness_pct`).

---

## 8. Credential Quarantine & Production Defense

1. **BIP-39 Seed Phrase & Private Key Quarantine**:
   - `backend/adapters/bip39_validator.py` loads the official 2,048-word English BIP-39 dictionary.
   - Any complaint narrative or bulletin submitted via `/api/v1/intake/*` containing $\ge 12$ mnemonic words or a 64-character hexadecimal private key string is automatically rejected (`HTTP 400 Bad Request`) and quarantined before database persistence.
2. **Production Startup Defense**:
   - In production (`APP_ENV=production`), the application refuses to start if `SECRET_KEY` remains the insecure default value or is under 32 characters in length.
3. **Evidence Integrity Testing**:
   - Verified via `test_phase0_logic_fixes.py`, `test_phase1_resilience.py`, and `test_phase8_intake_api.py` as part of the 129/129 passing test suite.
