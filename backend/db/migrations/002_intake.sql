-- ============================================================================
-- CryptoTrace LEA ? Phase 4 Intake Deduplication Schema Migration
-- Migration ID: 002_intake.sql
-- Description: Persistent deduplication table for NCRP/SAHYOG bulletins.
-- ============================================================================

CREATE TABLE IF NOT EXISTS intake_dedupe (
    content_hash VARCHAR(64) PRIMARY KEY,
    source VARCHAR(32) NOT NULL,
    bulletin_or_ack_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_intake_dedupe_source ON intake_dedupe(source);
CREATE INDEX IF NOT EXISTS idx_intake_dedupe_ref ON intake_dedupe(bulletin_or_ack_id);
