-- ============================================================================
-- CryptoTrace LEA — Canonical PostgreSQL Database Schema Migration
-- Migration ID: 001_initial_schema.sql
-- Description: Authoritative system of record for cases, transactions, 
--              transfers, typologies, attribution, evidence, and audit logs.
-- ============================================================================

-- 1. Cases Table
CREATE TABLE IF NOT EXISTS cases (
    case_id VARCHAR(64) PRIMARY KEY,
    source VARCHAR(32) NOT NULL DEFAULT 'COMPLAINT',
    chain VARCHAR(16) NOT NULL,
    wallet VARCHAR(128) NOT NULL,
    reported_amount NUMERIC(28, 8),
    complaint_text TEXT,
    complainant_name VARCHAR(128),
    fir_number VARCHAR(64),
    created_by VARCHAR(64) NOT NULL,
    assigned_to VARCHAR(64),
    status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    demo_data BOOLEAN NOT NULL DEFAULT FALSE,
    source_origin VARCHAR(64) NOT NULL DEFAULT 'LIVE_LEA_INTAKE'
);

CREATE INDEX IF NOT EXISTS idx_cases_wallet ON cases(wallet);
CREATE INDEX IF NOT EXISTS idx_cases_chain ON cases(chain);
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_demo ON cases(demo_data);

-- 2. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    chain_id VARCHAR(16) NOT NULL,
    tx_hash VARCHAR(128) NOT NULL,
    block_number BIGINT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'SUCCESS',
    raw_payload_hash VARCHAR(64) NOT NULL,
    PRIMARY KEY (chain_id, tx_hash)
);

-- 3. Transfers Table (Canonical Identity: chain_id, tx_hash, event_type, log_index, transfer_index)
CREATE TABLE IF NOT EXISTS transfers (
    id BIGSERIAL PRIMARY KEY,
    chain_id VARCHAR(16) NOT NULL,
    tx_hash VARCHAR(128) NOT NULL,
    log_index INT NOT NULL DEFAULT 0,
    transfer_index INT NOT NULL DEFAULT 0,
    event_type VARCHAR(16) NOT NULL DEFAULT 'NATIVE',
    from_addr VARCHAR(128) NOT NULL,
    to_addr VARCHAR(128) NOT NULL,
    amount NUMERIC(28, 8) NOT NULL,
    asset VARCHAR(32) NOT NULL,
    direction VARCHAR(8) NOT NULL DEFAULT 'OUT',
    raw_payload_hash VARCHAR(64) NOT NULL,
    finality_state VARCHAR(16) NOT NULL DEFAULT 'CONFIRMED',
    timestamp TIMESTAMP WITH TIME ZONE,
    provider_source VARCHAR(64) NOT NULL,
    CONSTRAINT uq_canonical_transfer UNIQUE (chain_id, tx_hash, event_type, log_index, transfer_index)
);

CREATE INDEX IF NOT EXISTS idx_transfers_from ON transfers(from_addr, chain_id);
CREATE INDEX IF NOT EXISTS idx_transfers_to ON transfers(to_addr, chain_id);
CREATE INDEX IF NOT EXISTS idx_transfers_tx ON transfers(tx_hash, chain_id);

-- 4. Entities Table
CREATE TABLE IF NOT EXISTS entities (
    entity_id VARCHAR(64) PRIMARY KEY,
    address VARCHAR(128) NOT NULL,
    chain VARCHAR(16) NOT NULL,
    entity_type VARCHAR(32) NOT NULL DEFAULT 'WALLET',
    first_seen TIMESTAMP WITH TIME ZONE,
    last_active TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_entity_addr UNIQUE (address, chain)
);

-- 5. Entity Labels Table
CREATE TABLE IF NOT EXISTS entity_labels (
    id BIGSERIAL PRIMARY KEY,
    entity_id VARCHAR(64) NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    label VARCHAR(128) NOT NULL,
    source VARCHAR(64) NOT NULL,
    confidence_level VARCHAR(16) NOT NULL, -- LOW, MEDIUM, HIGH
    label_type VARCHAR(16) NOT NULL,       -- VERIFIED, INFERRED, UNRESOLVED
    verified_date DATE
);

-- 6. VASP Clusters Table
CREATE TABLE IF NOT EXISTS vasp_clusters (
    cluster_id VARCHAR(64) PRIMARY KEY,
    vasp_name VARCHAR(128) NOT NULL,
    regions JSONB DEFAULT '[]'::jsonb,
    hot_wallet_patterns JSONB DEFAULT '[]'::jsonb,
    known_deposits JSONB DEFAULT '[]'::jsonb,
    nodal_officer_email VARCHAR(128) NOT NULL,
    fiu_registration_status VARCHAR(32) NOT NULL DEFAULT 'REGISTERED',
    policy_version VARCHAR(32) NOT NULL DEFAULT 'policy_v1_india_kyc'
);

-- 7. Pattern Findings Table
CREATE TABLE IF NOT EXISTS pattern_findings (
    finding_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    typology_name VARCHAR(64) NOT NULL,
    rule_version VARCHAR(16) NOT NULL DEFAULT '1.0',
    confidence VARCHAR(16) NOT NULL, -- LOW, MEDIUM, HIGH
    evidence_json JSONB NOT NULL,
    uncertainty_notes TEXT NOT NULL,
    data_completeness_pct NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
    india_specific BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_findings_case ON pattern_findings(case_id);

-- 8. Cross Chain Links Table
CREATE TABLE IF NOT EXISTS cross_chain_links (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    from_chain VARCHAR(16) NOT NULL,
    from_addr VARCHAR(128) NOT NULL,
    to_chain VARCHAR(16) NOT NULL,
    to_addr VARCHAR(128) NOT NULL,
    link_type VARCHAR(32) NOT NULL, -- PROVEN, HEURISTIC_CORRELATION
    supporting_evidence JSONB NOT NULL,
    confidence VARCHAR(16) NOT NULL
);

-- 9. Risk Assessments Table
CREATE TABLE IF NOT EXISTS risk_assessments (
    case_id VARCHAR(64) PRIMARY KEY REFERENCES cases(case_id) ON DELETE CASCADE,
    risk_score INT NOT NULL, -- 0 to 100
    risk_category VARCHAR(16) NOT NULL, -- CRITICAL, HIGH, MEDIUM, LOW
    component_scores JSONB NOT NULL
);

-- 10. Recovery Assessments Table
CREATE TABLE IF NOT EXISTS recovery_assessments (
    case_id VARCHAR(64) PRIMARY KEY REFERENCES cases(case_id) ON DELETE CASCADE,
    recovery_score INT NOT NULL, -- 0 to 100
    action_window_hours INT NOT NULL,
    display_tier VARCHAR(16) NOT NULL, -- eligible, ineligible
    calculation_basis TEXT NOT NULL,
    disclaimer TEXT NOT NULL
);

-- 11. Preservation Requests (Legal Workflow Table)
CREATE TABLE IF NOT EXISTS preservation_requests (
    draft_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    trace_id BIGINT,
    created_by VARCHAR(64) NOT NULL,
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    recipient_vasp VARCHAR(128) NOT NULL,
    recipient_email VARCHAR(128) NOT NULL,
    legal_authority VARCHAR(64) NOT NULL DEFAULT 'SECTION_91_BNSS_2023',
    demanded_items JSONB NOT NULL,
    transaction_references JSONB NOT NULL,
    draft_text TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT', -- DRAFT, PENDING_APPROVAL, APPROVED, REJECTED
    supervisor_id VARCHAR(64),
    supervisor_notes TEXT,
    reviewed_timestamp TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_requests_case ON preservation_requests(case_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON preservation_requests(status);

-- 12. Evidence Manifest Table
CREATE TABLE IF NOT EXISTS evidence_manifest (
    manifest_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    event_id VARCHAR(64) NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,
    provider_source VARCHAR(64) NOT NULL,
    serialization_version VARCHAR(32) NOT NULL DEFAULT 'v1-deterministic',
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_manifest_case ON evidence_manifest(case_id);
CREATE INDEX IF NOT EXISTS idx_manifest_hash ON evidence_manifest(payload_hash);
