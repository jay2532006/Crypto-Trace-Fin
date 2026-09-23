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

## 2. Role-Based Access Control (RBAC)

The system enforces four canonical roles:

| Role | Permissions |
|---|---|
| `INVESTIGATOR` | Create cases, execute bounded forensic traces, draft Section 91 notices, export dossiers. |
| `SUPERVISOR` | All Investigator permissions, plus approve/reject Section 91 preservation directives, sign court disclosures. |
| `ADMINISTRATOR` | Full system access, manage agency users, configure provider backbones, rebuild graph projections. |
| `INTEGRATION_SERVICE` | Automated ingest of complaint feeds from NCRP / I4C SAHYOG; cannot approve notices or delete cases. |

---

## 3. Cryptographic Tamper-Evident Audit Trail

1. **Chained SHA-256 Ledger**: Every mutation is logged with an event hash calculated as:
   $$\text{Hash}_n = \text{SHA256}(\text{Hash}_{n-1} \parallel \text{EventID} \parallel \text{Timestamp} \parallel \text{Actor} \parallel \text{Action} \parallel \text{Resource} \parallel \text{Details})$$
2. **Evidence Integrity**: All raw provider responses are stored deterministically and indexed by their SHA-256 digest, providing verifiable compliance with Section 65B Bharatiya Sakshya Adhiniyam, 2023 (BSA).
3. **Continuous Verification**: The `/api/v1/audit/verify-chain` endpoint and dashboard modal allow supervisory officers to verify that no records in the audit log have been altered or deleted.
