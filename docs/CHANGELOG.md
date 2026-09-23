# CryptoTrace LEA — Changelog

## [1.0.0-SIH26183] - 2026-09-23

### Major Innovations & Architectural Modernization
- **⭐ MULE_NETWORK Typology Engine**: Purpose-built detection for Indian cybercrime layering networks. Requires $\ge 3$ intermediate single-in/single-out wallets, sub-60 minute elapsed time, fee-normalized consistency within 15% tolerance, strict `MEDIUM` confidence ceiling, and mandatory uncertainty disclosure.
- **⭐ AdaptiveVASPScorer Attribution Engine**: Dynamic 6-step contextual weighting sequence under versioned policy `policy_v1_india_kyc`. Features separate `VERIFIED` and `INFERRED` classifications, penalty clamping $[0.01, 0.80]$, data completeness capping, and explainable scoring step audit traces.
- **⭐ Heuristic Recovery Estimate**: Operational victim-impact indicator (0-100) with remaining action window hours countdown, gated by PRD FR-016 boundary conditions, with statutory disclaimer under Section 106 BNSS 2023.

### Foundation Hardening & Security (Phase 0)
- **Authoritative Database**: PostgreSQL migration schema (`001_initial_schema.sql`) for canonical entities with SQLite fallback for local development.
- **Deterministic Raw Payload Storage**: Canonical compact JSON serialization with sorted keys, stored in `data/raw/...` indexed by SHA-256 for Section 65B BSA compliance.
- **Chained Audit Ledger**: Cryptographic SHA-256 chaining where each event embeds `previous_event_hash`, verifiable via `/api/v1/audit/verify-chain`.
- **Role-Based Access Control (RBAC)**: Canonical roles: `INVESTIGATOR`, `SUPERVISOR`, `ADMINISTRATOR`, `INTEGRATION_SERVICE` with JWT authentication.
- **Security Lockdowns**: Direct Cypher (`/api/neo4j/query`) and arbitrary outbound HTTP execution (`/api/test/custom`) permanently disabled with HTTP 403 Forbidden.

### Ingestion, Resilience & Tracing (Phases 1-3)
- **Isolated Live Provider Backbone**: Isolated EVM (ETH, Polygon RPC), Bitcoin (Mempool.space), and TRON (TronGrid TRC-20) adapters with resilient fallbacks.
- **8-Stage Ingestion Pipeline**: `FETCH` $\to$ `VALIDATE` $\to$ `EXTRACT` $\to$ `NORMALIZE` $\to$ `DEDUPLICATE` $\to$ `PERSIST` $\to$ `COMMIT` $\to$ `ADVANCE`.
- **Rebuildable Graph Projection**: Reconstructible on-demand from authoritative DB via `rebuild_from_db()`.
- **Supervisor-Gated Preservations**: Lawful Section 91 notices start as `DRAFT`, require `PENDING_APPROVAL`, and unlock gateway dispatch only upon `SUPERVISOR` sign-off.

### Workstation Interface Enhancements
- Modern cyber-forensic UI integrated in `dashboard.html`:
  - `sih-mule-banner` for Mule Network alerts.
  - `sih-adaptive-card` with expandable 6-step scoring trace table.
  - `sih-recovery-card` with action window countdown and factor breakdowns.
  - `sih-supervisor-deck` for notice approval lifecycle.
  - Cryptographic audit chain verification modal.
