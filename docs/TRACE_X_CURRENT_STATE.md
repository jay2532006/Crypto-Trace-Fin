# TraceX Current State Assessment & Adaptation Mapping
**Document Path:** `docs/TRACE_X_CURRENT_STATE.md`  
**Purpose:** Comprehensive baseline analysis of the existing TraceX v2.0-PRO (SIH 26182) repository against CryptoTrace LEA (SIH 26183) PRD, Implementation Plan, and Phasewise Implementation Roadmap.  
**Author:** Principal Software Engineer, CryptoTrace LEA  
**Date:** September 2026  

---

## 1. Executive Assessment Summary

The existing repository contains a working prototype developed for Problem Statement 26182 (TraceX). While it demonstrates functional concepts (FastAPI routing, multi-chain address parsing, basic NetworkX BFS traversal, static VASP hot wallet lookup, and HTML dashboard rendering), its core semantics, architecture, and security properties directly conflict with CryptoTrace LEA (Problem Statement 26183) standards:

1. **Storage Authority:** TraceX relies on a flat SQLite table (`investigations`) with unindexed JSON blobs and assumes Neo4j can be an authoritative state store. CryptoTrace mandates PostgreSQL as the sole authoritative system of record with normalized entities, deterministic raw payload archiving, and treat graph engines as purely rebuildable projections.
2. **Attribution & Scoring:** TraceX computes a single blended confidence percentage based on static regexes. CryptoTrace requires separate Risk vs. Attribution dimensions, the six-step `AdaptiveVASPScorer` with policy versioning, and strict separation of `VERIFIED`, `INFERRED`, and `UNRESOLVED` entity labels.
3. **Typologies:** TraceX has generic heuristics without confidence ceilings or uncertainty bounds. CryptoTrace mandates the purpose-built `MULE_NETWORK` rule (India-specific, hard-capped at MEDIUM confidence), exact `MIXER_BOUNDARY` parameters, and evidence-grounded findings.
4. **Victim Recovery:** TraceX uses a linear "freezing urgency" countdown. CryptoTrace requires the deterministic `RecoveryProbabilityScore` (labeled "Heuristic Recovery Estimate") with bounded eligibility and action windows.
5. **Security & Governance:** TraceX has zero RBAC, single-user mode, unrestricted Cypher execution, arbitrary outbound HTTP execution, runtime `.env` mutation from the browser UI, and automatic legal notice creation. CryptoTrace requires multi-role RBAC, chained SHA-256 audit logging, supervisor-gated legal workflows (`DRAFT` → `PENDING_APPROVAL` → `APPROVED`), and immutable environment-based secrets.

Below is the exhaustive component-by-component mapping.

---

## 2. Component-by-Component Mapping

### Component 1: `app.py` (FastAPI Server & Route Dispatcher)
- **Existing Purpose:** Monolithic 553-line FastAPI application serving API routes, background tasks, static dashboard HTML, SQLite database initialization, and Neo4j telemetry.
- **Decision:** **REFACTOR (SPLIT & MODULARIZE)**
- **Reason:** Monolithic structure combines database schema setup, authentication, external API proxies, Cypher queries, and file serving in one file. Conflicts with clean architecture, RBAC middleware, and modular API routers.
- **Target CryptoTrace Component:** `backend/api/` (split into `case_routes.py`, `trace_routes.py`, `findings_routes.py`, `evidence_routes.py`, `notice_routes.py`, `auth_routes.py`) with a lightweight `app.py` mounting routers and middleware.
- **Relevant PRD Requirement:** PRD Section 6 (User Roles & Personas), Section 17 (RBAC & Governance), Section 18 (System Architecture).
- **Test Requirement:** Integration tests verifying all endpoints enforce RBAC token verification, return standard error structures, and maintain backward compatibility for existing diagnostic clients.

---

### Component 2: `engine/address_validator.py`
- **Existing Purpose:** Multi-chain address validation for Bitcoin (Legacy, SegWit Bech32), EVM (0x with EIP-55 checksum), TRON (Base58Check prefix 0x41), and Solana.
- **Decision:** **KEEP / REUSE + EXTEND**
- **Reason:** Cryptographic decoding and format validation logic are sound and mathematically correct. Needs extension for explicit chain configurations, canonical chain ID assignment, and rejection of unsupported chains.
- **Target CryptoTrace Component:** `backend/adapters/address_validator.py` and `backend/models/domain_models.py`
- **Relevant PRD Requirement:** PRD Section 5.1 (Supported Chains: EVM, Bitcoin UTXO, Tron), Section 7.2 (Canonical Address Entity).
- **Test Requirement:** Unit tests covering valid and invalid checksums, prefix mutations, and malformed addresses across BTC, ETH, Polygon, and TRON.

---

### Component 3: `engine/graph_tracer.py`
- **Existing Purpose:** 5-hop fund flow tracing using NetworkX `MultiDiGraph`, simulated benchmark generation, and basic shortest-path calculations.
- **Decision:** **REBUILD**
- **Reason:** Does not enforce strict deterministic traversal ordering; lacks checkpoint/resume capability; merges risk with attribution; lacks bounded constraints (max nodes, max outflows, time window, timeout); does not report canonical termination reasons (`COMPLETE`, `MAX_HOPS`, `MAX_NODES`, `TIMEOUT`, `VALUE_THRESHOLD`).
- **Target CryptoTrace Component:** `backend/tracing/trace_engine.py` (`BoundedTracer`), `backend/tracing/graph_builder.py`, `backend/tracing/path_finder.py`.
- **Relevant PRD Requirement:** PRD Section 9 (Bounded Fund-Flow Tracing: 9.1–9.7).
- **Test Requirement:** Deterministic replay tests verifying that identical inputs yield identical path orderings, termination condition tests (hitting hop limit, node limit, timeout).

---

### Component 4: `engine/vasp_cluster.py`
- **Existing Purpose:** Static dictionary of 15+ VASPs with regex patterns for hot wallets and nodal emails. Computes heuristic attribution confidence as a raw percentage.
- **Decision:** **REBUILD**
- **Reason:** Static regex matching cannot handle contextual confidence weights, policy versioning, single-hop overrides, or data completeness caps. Conflates attribution with liability.
- **Target CryptoTrace Component:** `backend/attribution/adaptive_vasp_scorer.py` (`AdaptiveVASPScorer`), `backend/attribution/vasp_registry.py`, `backend/attribution/label_classifier.py`.
- **Relevant PRD Requirement:** PRD Section 11 (VASP Attribution & AdaptiveVASPScorer: 11.1–11.6).
- **Test Requirement:** Unit tests executing the exact 6-step scoring sequence, verifying policy versions, context modifiers, clamping (0.01–0.80), weight renormalization to 1.0, and `VERIFIED` vs `INFERRED` vs `UNRESOLVED` classification.

---

### Component 5: `engine/real_api.py`
- **Existing Purpose:** Unified data harvester calling Etherscan V2, TronGrid, Blockstream Esplora, and Bitquery GraphQL.
- **Decision:** **SPLIT & REFACTOR**
- **Reason:** Etherscan is improperly used as the live Ethereum path (PRD mandates direct RPC/WebSocket as the primary live path, using Etherscan only for historical lookup and labels). Blockstream is used instead of Mempool.space. Bitquery is on the critical path. Lacks canonical event identity, raw payload archiving, and finality state tracking.
- **Target CryptoTrace Component:** `backend/adapters/` (`chain_adapter_base.py`, `evm_adapter.py`, `bitcoin_adapter.py`, `tron_adapter.py`, `provider_manager.py`).
- **Relevant PRD Requirement:** PRD Section 8 (Live Blockchain Provider Backbone: 8.1–8.6).
- **Test Requirement:** Provider-specific integration tests verifying raw payload extraction, canonical event identity creation: `(chain_id, tx_hash, event_type, log_index, transfer_index)`, and fallback execution.

---

### Component 6: `engine/typology.py`
- **Existing Purpose:** Basic rule functions for peel chain, rapid dispersion, structuring, mixer interaction, and round amount anomaly.
- **Decision:** **REBUILD**
- **Reason:** Lacks the primary SIH 26183 innovation `MULE_NETWORK`. Does not enforce the required confidence ceilings (MEDIUM cap on heuristic rules), lacks explicit uncertainty notes, and does not record data completeness metrics.
- **Target CryptoTrace Component:** `backend/typologies/typology_engine.py` and `backend/typologies/rules/` (`mule_network.py`, `mixer_boundary.py`, `peel_chain.py`, `fan_in.py`, `fan_out.py`, `rapid_hop.py`, `dex_bridge_analysis.py`).
- **Relevant PRD Requirement:** PRD Section 10 (Explainable Typology Detection: 10.1–10.8).
- **Test Requirement:** Unit tests for `MULE_NETWORK` verifying minimum 3 suspect-origin wallets, < 60 min immediacy, fee-normalized consistency, MEDIUM confidence ceiling, and uncertainty documentation. Exact parameter verification for `MIXER_BOUNDARY` (+14,400s window, 0.90–0.995 payout ratio, 0.25 confidence).

---

### Component 7: `engine/price_feed.py`
- **Existing Purpose:** CoinGecko spot pricing with USD/INR conversion and basic in-memory caching.
- **Decision:** **KEEP / REUSE + EXTEND**
- **Reason:** Sound pricing conversion utility. Must be strictly documented that price data is market enrichment and not blockchain evidence.
- **Target CryptoTrace Component:** `backend/enrichment/price_feed.py`.
- **Relevant PRD Requirement:** PRD Section 8.6 (Pricing Data Enrichment).
- **Test Requirement:** Test rate limiting, cache expiration, and graceful fallback when CoinGecko is unreachable.

---

### Component 8: `engine/neo4j_engine.py`
- **Existing Purpose:** Connects to Neo4j Aura Cloud, creates node/relationship schemas, syncs trace graphs, and executes raw Cypher queries via HTTP endpoint.
- **Decision:** **REFACTOR & LOCK DOWN**
- **Reason:** Neo4j was treated as an authoritative synchronized store rather than a rebuildable projection. The endpoint `/api/neo4j/query` allows arbitrary Cypher execution by any user, which is a major security flaw.
- **Target CryptoTrace Component:** `backend/graph/neo4j_projection.py` (read-only projection service, rebuild command from PostgreSQL; unrestricted Cypher endpoint removed from production API).
- **Relevant PRD Requirement:** PRD Section 18.2 (Graph Projection as Rebuildable Store).
- **Test Requirement:** Test graph rebuild from PostgreSQL: clears graph, reads normalized records, rebuilds nodes/edges, and compares counts.

---

### Component 9: `engine/notice_generator.py`
- **Existing Purpose:** Directly generates Section 91 BNSS 2023 / CrPC requisition notices to VASP nodal officers and writes plain text files to disk without human review gates.
- **Decision:** **REBUILD**
- **Reason:** Automatically generating and dispatching legal notices violates core LEA legal workflow mandates. CryptoTrace requires draft-only generation gated by mandatory supervisor review (`DRAFT` → `PENDING_APPROVAL` → `APPROVED` / `REJECTED`).
- **Target CryptoTrace Component:** `backend/legal/notice_generator.py` and `backend/api/notice_routes.py`.
- **Relevant PRD Requirement:** PRD Section 15 (Preservation Request Workflow: 15.1–15.5).
- **Test Requirement:** Unit and route tests verifying that investigators can only create drafts, non-supervisors cannot approve drafts, and audit logs record every state transition.

---

### Component 10: `engine/ofac_sanctions.py`
- **Existing Purpose:** Checks wallet addresses against static and live US Treasury OFAC SDN sanctions list (Tornado Cash, Blender.io, Lazarus Group, Garantex).
- **Decision:** **KEEP / REUSE + EXTEND**
- **Reason:** Solid sanctions dataset. Needs clear labeling as an auxiliary intelligence enrichment source with explicit list publication date/version provenance.
- **Target CryptoTrace Component:** `backend/enrichment/ofac_sanctions.py`.
- **Relevant PRD Requirement:** PRD Section 10.6 (Mixer & Sanctions Boundary).
- **Test Requirement:** Test address matching against known sanctioned entities and non-sanctioned clean addresses.

---

### Component 11: `engine/ai_copilot.py`
- **Existing Purpose:** Dual-provider LLM chat assistant (Google Gemini Flash + Groq Qwen) with multilingual support and deterministic fallback.
- **Decision:** **DEFER / OPTIONAL**
- **Reason:** PRD establishes that deterministic intelligence (explainable typologies, bounded tracing, AdaptiveVASPScorer) is the mandatory core baseline. AI Copilot must not be on the critical path for Phase 0 or Phase 1 acceptance.
- **Target CryptoTrace Component:** `backend/copilot/ai_copilot.py` (isolated as secondary optional service).
- **Relevant PRD Requirement:** PRD Section 4 (Deterministic Intelligence First; AI as optional auxiliary).
- **Test Requirement:** Verify that the core platform functions completely without external LLM API keys.

---

### Component 12: `engine/api_tester.py`
- **Existing Purpose:** Diagnostic test runner for external APIs with arbitrary HTTP request execution endpoint (`POST /api/test/custom`).
- **Decision:** **REMOVE ARBITRARY HTTP / LIMIT TO INTERNAL DIAGNOSTICS**
- **Reason:** Arbitrary outbound HTTP execution creates a Server-Side Request Forgery (SSRF) security vulnerability in LEA networks.
- **Target CryptoTrace Component:** `backend/diagnostics/health_checks.py` (internal health pings only, accessible only to ADMIN role).
- **Relevant PRD Requirement:** PRD Section 19.3 (Security Hardening).
- **Test Requirement:** Ensure non-admin users cannot trigger diagnostic network requests and arbitrary URLs are rejected.

---

### Component 13: `engine/key_manager.py`
- **Existing Purpose:** Reads and writes API keys directly to `.env` file from browser UI requests.
- **Decision:** **REMOVE RUNTIME SECRET MUTATION**
- **Reason:** Allowing the application to rewrite its own `.env` file at runtime from browser requests is a severe security vulnerability. Secrets must be managed via server environment variables or deployment config.
- **Target CryptoTrace Component:** `backend/config/base.py` (read-only environment configuration loaded at startup).
- **Relevant PRD Requirement:** PRD Section 19.2 (Secret Management).
- **Test Requirement:** Verify secrets are never logged, never returned in API payloads, and environment cannot be mutated via HTTP calls.

---

### Component 14: `engine/demo_cases.py`
- **Existing Purpose:** Hardcoded benchmark scenarios (WazirX, Pig Butchering, Darknet, Ransomware, Flash Loan).
- **Decision:** **REBUILD FIXTURES**
- **Reason:** Scenarios do not match CryptoTrace LEA PRD test fixtures and lack explicit `demo_data=true` flags and provenance metadata.
- **Target CryptoTrace Component:** `backend/fixtures/demo_cases_v2.py` (dedicated fixtures: India Mule Network, Mixer Boundary, Cross-Chain Bridge, Fan-In, Rapid-Hop, all explicitly tagged `demo_data=true`).
- **Relevant PRD Requirement:** PRD Section 5.1 (Explicit LIVE vs FIXTURE Distinction).
- **Test Requirement:** Fixture loader tests verifying that all fixture cases carry immutable `demo_data=true` flags and are prohibited from being submitted as live cases.

---

### Component 15: Database Layer (`data/sahyog.db`)
- **Existing Purpose:** Flat SQLite table `investigations` storing unindexed JSON strings.
- **Decision:** **REBUILD (POSTGRESQL SYSTEM OF RECORD + NORMALIZED SCHEMA)**
- **Reason:** SQLite cannot support high-concurrency ingestion, idempotent transfer logging, relational integrity, or audit chaining. PostgreSQL is the authoritative system of record.
- **Target CryptoTrace Component:** `backend/db/` (`database.py`, `models.py`, `migrations/001_initial_schema.sql`). SQLite retained only as optional local dev fallback.
- **Relevant PRD Requirement:** PRD Section 18.1 (PostgreSQL Authoritative Storage).
- **Test Requirement:** Migration tests creating all 12 canonical tables, foreign keys, unique idempotency constraints, and backward-compatible read tests for legacy SQLite cases.

---

### Component 16: Authentication & Authorization Layer
- **Existing Purpose:** Completely absent. Single-user access with no credentials or roles.
- **Decision:** **REBUILD FROM SCRATCH**
- **Reason:** LEA operations mandate multi-role RBAC, session management, and access controls.
- **Target CryptoTrace Component:** `backend/auth/` (`rbac.py`, `jwt_handler.py`, `decorators.py`) with canonical roles: `INVESTIGATOR`, `SUPERVISOR`, `ADMINISTRATOR`, `INTEGRATION_SERVICE`.
- **Relevant PRD Requirement:** PRD Section 17 (Role-Based Access Control).
- **Test Requirement:** Unit tests verifying permission matrices, token issuance, expiration, and role enforcement decorators on protected routes.

---

### Component 17: Audit & Evidence Storage Layer
- **Existing Purpose:** Minimal file-based notice saving in `reports/`. No evidence manifests, no raw payload storage, no hash verification.
- **Decision:** **REBUILD FROM SCRATCH**
- **Reason:** Forensic evidence in court must have verifiable provenance and tamper resistance.
- **Target CryptoTrace Component:** `backend/storage/raw_payload_storage.py` (deterministic JSON serialization, SHA-256 calculation, `raw/` directory structure) and `backend/audit/audit_engine.py` (chained SHA-256 audit logging).
- **Relevant PRD Requirement:** PRD Section 16 (Evidence Manifest & Audit Integrity: 16.1–16.5).
- **Test Requirement:** Deterministic serialization tests (same dictionary order/whitespace = exact same SHA-256 hash), audit chain integrity tests, and tamper detection tests.

---

### Component 18: Frontend (`dashboard.html` / `index.html`)
- **Existing Purpose:** 796 KB single-page cyber command center styled with custom dark theme, embedding Vis.js, audio synthesizer, and hardcoded UI widgets.
- **Decision:** **REFACTOR & REBUILD INVESTIGATOR WORKSTATION UI**
- **Reason:** UI currently displays single confidence scores, lacks supervisor approval buttons, lacks raw payload verification tables, lacks the three core innovation panels (`MULE_NETWORK`, `AdaptiveVASPScorer`, `RecoveryProbabilityScore`), and does not prominently display `LIVE` vs `FIXTURE` provenance badges.
- **Target CryptoTrace Component:** `frontend/` / updated `dashboard.html` with dedicated panels for:
  1. Case Header & Provenance (`LIVE` vs `FIXTURE/DEMO`).
  2. `MULE_NETWORK` Typology Alert Card with uncertainty disclosures.
  3. `AdaptiveVASPScorer` Panel with explainable 6-step breakdown and policy version.
  4. Heuristic Recovery Estimate Panel with action window countdown.
  5. Supervisor Approval Workflow for legal notices.
  6. Evidence Manifest & Raw Payload SHA-256 Verifier.
- **Relevant PRD Requirement:** PRD Section 6, 10, 11, 14, 15, 16.
- **Test Requirement:** Browser-level automated and manual walkthrough testing of all panels, status badges, and interactive graph behaviors.

---

### Component 19: Deployment Scripts (`start.bat`, `start.sh`)
- **Existing Purpose:** Windows batch script and Linux bash script for launching uvicorn.
- **Decision:** **KEEP / REUSE + EXTEND**
- **Reason:** Effective 1-click startup mechanism. Extend with environment checks, migration runner, and dependency verification.
- **Target CryptoTrace Component:** `start.bat`, `start.sh`, `docker-compose.yml`.
- **Relevant PRD Requirement:** PRD Section 19.1 (Deployment Architecture).
- **Test Requirement:** Test clean startup on Windows and Linux environments.

---

## 3. Summary of Transformation Decisions

| Category | Component Count | Components |
|:---|:---:|:---|
| **KEEP / REUSE + EXTEND** | 4 | `address_validator.py`, `price_feed.py`, `ofac_sanctions.py`, `start.bat`/`start.sh` |
| **REFACTOR** | 3 | `app.py`, `real_api.py`, `neo4j_engine.py` |
| **REBUILD** | 6 | `graph_tracer.py`, `vasp_cluster.py`, `typology.py`, `notice_generator.py`, `demo_cases.py`, Database layer (`sahyog.db` → PostgreSQL) |
| **NEW (BUILD FROM SCRATCH)** | 4 | RBAC & JWT (`backend/auth/`), Deterministic Storage & Manifest (`backend/storage/`), Chained Audit Engine (`backend/audit/`), Recovery Estimator (`backend/assessment/`) |
| **REMOVE / LOCK DOWN** | 3 | Runtime `.env` UI mutation (`key_manager.py`), Arbitrary Cypher execution (`/api/neo4j/query`), Arbitrary outbound HTTP tester (`/api/test/custom`) |
| **DEFER (OPTIONAL)** | 1 | `ai_copilot.py` (Secondary assistance; non-critical for core evaluation) |
