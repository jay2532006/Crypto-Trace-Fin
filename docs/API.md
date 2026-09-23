# CryptoTrace LEA — API Reference

## Base URLs
- Default: `http://localhost:8000`
- API Prefix: `/api/v1`

---

## 1. Authentication & RBAC

### `POST /api/v1/auth/login`
Authenticates an investigator or supervisory officer and issues a role-scoped JWT token.
- **Request Body**:
  ```json
  {
    "username": "investigator1",
    "password": "Password123!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "username": "investigator1",
      "role": "INVESTIGATOR",
      "agency": "Cyber Crime Police Station",
      "badge_number": "MH-CYBER-4091"
    }
  }
  ```

---

## 2. Case Intake & Management

### `POST /api/v1/cases`
Creates a formal investigation case record in authoritative storage.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "chain": "ETH",
    "wallet": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "reported_amount": 14.5,
    "complaint_text": "Victim defrauded via Telegram investment task",
    "fir_number": "FIR No. 247/2024",
    "complainant_name": "Rajesh Kumar",
    "demo_data": false
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "case_id": "CR-2026-ETH-4438F4",
    "status": "OPEN",
    "created_date": "2026-09-23T12:00:00Z"
  }
  ```

### `GET /api/v1/cases`
Lists investigation cases with pagination and status filters.

---

## 3. Bounded Forensic Attribution Tracing

### `POST /api/trace` or `POST /api/v1/trace`
Executes bounded deterministic multi-hop attribution tracing, running the 3 SIH 26183 core innovations:
1. `MULE_NETWORK` Typology Rule Engine
2. `AdaptiveVASPScorer` with 6-step contextual modifiers under `policy_v1_india_kyc`
3. `RecoveryProbabilityScore` (Heuristic Recovery Estimate)

- **Request Body**:
  ```json
  {
    "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "chain": "ETH",
    "mode": "DEMO",
    "max_hops": 5
  }
  ```
- **Response Structure**:
  ```json
  {
    "status": "completed",
    "case_id": "CR-2026-AUTO-9182",
    "chain": "ETH",
    "nodes": [...],
    "edges": [...],
    "hops": [...],
    "pattern_findings": [
      {
        "rule": "MULE_NETWORK",
        "india_specific": true,
        "severity": "HIGH",
        "confidence": "MEDIUM",
        "evidence": "Detected mule chain with 3 intermediate single-in/single-out wallets...",
        "uncertainty_note": "Identified intermediate addresses exhibit single-in/single-out rapid transfer behavior..."
      }
    ],
    "attribution": {
      "vasp_name": "CoinDCX",
      "score": 0.88,
      "label_type": "VERIFIED",
      "confidence_band": "HIGH",
      "policy_version": "policy_v1_india_kyc",
      "fiu_status": "REGISTERED",
      "scoring_steps": [
        {
          "step_name": "Prior Base Probability",
          "input_value": 0.85,
          "weight": 0.35,
          "contribution": 0.297,
          "reasoning": "Direct deposit address identified in curated registry"
        }
      ]
    },
    "recovery": {
      "recovery_score": 78.5,
      "action_window_hours": 18.0,
      "display_tier": "Eligible",
      "explanation": "Asset reached cooperative FIU-registered exchange (CoinDCX)...",
      "legal_disclaimer": "Heuristic operational estimate for prioritization only..."
    },
    "cross_chain": {
      "detected": false,
      "link_type": null
    },
    "raw_payload_hash": "a1b2c3d4e5f60718293a4b5c6d7e8f90...",
    "evidence_manifest": { ... }
  }
  ```

---

## 4. Section 91 BNSS Lawful Notice Preservation Workflow

### `POST /api/v1/notices/draft`
Drafts a Section 91 BNSS / Section 106 asset restraint requisition directive (initial status `DRAFT`).

### `POST /api/v1/notices/{case_id}/submit`
Submits the drafted requisition to the supervisory officer for legal review (status `PENDING_APPROVAL`).

### `POST /api/v1/notices/{case_id}/approve`
**Supervisor Only** (`SUPERVISOR` or `ADMINISTRATOR` role required). Signs and authorizes the directive (status `APPROVED`), unlocking gateway dispatch.
- **Request Body**:
  ```json
  {
    "supervisor_id": "MHA-I4C-SUP-8824",
    "supervisor_name": "SP Vikramaditya",
    "approved": true
  }
  ```

---

## 5. Audit Chain & Evidence Verification

### `GET /api/v1/audit/verify-chain`
Cryptographically verifies the SHA-256 chained hash integrity of the complete audit log and returns verification status.
- **Response**:
  ```json
  {
    "valid": true,
    "is_valid": true,
    "total_events": 24,
    "latest_hash": "8f9a2e3b1c4d5e6f...",
    "message": "Audit chain hash sequence is 100% cryptographically verified and unbroken."
  }
  ```

---

## 6. Security Lockdowns

### `POST /api/neo4j/query`
- **Status**: `403 Forbidden`
- **Reason**: Unrestricted Cypher execution disabled per PRD Section 18.2.

### `POST /api/test/custom`
- **Status**: `403 Forbidden`
- **Reason**: Arbitrary outbound HTTP execution disabled per PRD Section 19.3.
