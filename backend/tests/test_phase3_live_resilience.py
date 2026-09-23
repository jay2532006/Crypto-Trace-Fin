"""
CryptoTrace LEA — Phase 3 Live Connectivity, Ingestion Pipeline & Resilience Tests
Validates:
- 8-stage ingestion pipeline (FETCH -> VALIDATE -> EXTRACT -> NORMALIZE -> DEDUPLICATE -> PERSIST -> COMMIT -> ADVANCE)
- Checkpoint advancement and reorg handling
- Graph rebuild projection from authoritative database
- Provider isolation & resilience
"""

import pytest
from backend.ingestion.pipeline import ingestion_pipeline
from backend.graph.graph_projection import graph_projection
from backend.adapters.provider_manager import provider_manager
from backend.audit.audit_engine import audit_engine


class TestPhase3LiveResilience:
    def test_01_ingestion_pipeline_validation_and_deduplication(self):
        # 1. Invalid payload rejection (Validation stage)
        invalid_res = ingestion_pipeline.process_raw_event({}, chain="ETH")
        assert invalid_res["status"] == "REJECTED"
        assert invalid_res["stage"] == "FETCH"

        # Missing fields rejection
        partial_res = ingestion_pipeline.process_raw_event({"tx_hash": "0x123", "amount": 0}, chain="ETH")
        assert partial_res["status"] == "REJECTED"
        assert partial_res["stage"] == "VALIDATE"

        # 2. Valid raw event processing
        event = {
            "tx_hash": "0xabc1234567890abcdef1234567890abcdef1234567890abcdef1234567890abc",
            "from_address": "0x1111111111111111111111111111111111111111",
            "to_address": "0x2222222222222222222222222222222222222222",
            "amount": 2.5,
            "asset": "ETH",
            "block_number": 19500000,
            "event_type": "NATIVE",
            "event_index": 0,
            "transfer_index": 0,
        }
        res1 = ingestion_pipeline.process_raw_event(event, chain="ETH")
        assert res1["status"] == "INGESTED"
        assert res1["stage"] == "ADVANCE"
        assert res1["checkpoint"] == 19500000
        assert len(res1["raw_hash"]) == 64

        # 3. Duplicate event suppression
        res2 = ingestion_pipeline.process_raw_event(event, chain="ETH")
        assert res2["status"] == "DEDUPLICATED"
        assert res2["stage"] == "DEDUPLICATE"

    def test_02_checkpointing_and_reorg_handling(self):
        current_cp = ingestion_pipeline.get_checkpoint("ETH")
        assert current_cp >= 19500000

        # Simulate chain reorg rollback
        reorg_res = ingestion_pipeline.handle_reorg("ETH", rollback_block=19499990)
        assert reorg_res["status"] == "REORG_HANDLED"
        assert reorg_res["rollback_block"] == 19499990
        assert ingestion_pipeline.get_checkpoint("ETH") == 19499990

    def test_03_graph_rebuild_from_authoritative_db(self):
        # Clear graph projection
        graph_projection.clear()
        stats_before = graph_projection.get_stats()
        assert stats_before["nodes"] == 0
        assert stats_before["edges"] == 0

        # Rebuild from database
        rebuild_res = graph_projection.rebuild_from_db(actor="test_admin")
        assert rebuild_res["status"] == "REBUILT"
        assert rebuild_res["is_consistent"] is True

        stats_after = graph_projection.get_stats()
        assert stats_after["nodes"] >= 2
        assert stats_after["edges"] >= 1

    def test_04_provider_isolation_and_health(self):
        health = provider_manager.check_health()
        assert "ETH" in health
        assert "POLYGON" in health
        assert "BTC" in health
        assert "TRON" in health

        # Address detection
        assert provider_manager.detect_chain("0x742d35Cc6634C0532925a3b844Bc454e4438f44e") == "ETH"
        assert provider_manager.detect_chain("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t") == "TRON"
        assert provider_manager.detect_chain("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq") == "BTC"

    def test_05_audit_chain_integrity_after_ingestion(self):
        audit_res = audit_engine.verify_audit_chain()
        assert audit_res["is_valid"] is True
        assert audit_res["total_events"] > 0
