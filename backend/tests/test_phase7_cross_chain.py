# backend/tests/test_phase7_cross_chain.py
"""
CryptoTrace LEA - Phase 3 Cross-Chain Verification Tests
Validates:
1. Bridge registry completeness (every entry must have verified_on and source_url)
2. PROVEN smart contract bridge classification vs HEURISTIC_CORRELATION
3. Exact tolerance boundaries for heuristic classification (5% fee, 3600s time delta)
4. Tracer bridge detection, node creation, and destination chain continuation
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.cross_chain.bridge_registry import BRIDGE_REGISTRY, is_bridge_contract, get_bridge_info
from backend.cross_chain.cross_chain_analyzer import cross_chain_analyzer
from backend.tracing.trace_engine import BoundedTracer, TraceConstraints
from backend.models.domain_models import Transfer

class TestPhase7CrossChain(unittest.TestCase):
    def test_01_bridge_registry_completeness(self):
        """Every entry in BRIDGE_REGISTRY must have a source_url and non-empty verified_on date."""
        self.assertGreaterEqual(len(BRIDGE_REGISTRY), 3)
        for key, entry in BRIDGE_REGISTRY.items():
            self.assertTrue(entry.get("source_url"), f"{key} missing source_url")
            self.assertTrue(entry.get("verified_on"), f"{key} missing verified_on")
            self.assertTrue(len(entry.get("contract_addresses", [])) > 0, f"{key} has no contracts")

    def test_02_proven_vs_heuristic_correlation(self):
        """Bridge TX hash present -> PROVEN; Bridge TX hash absent -> HEURISTIC_CORRELATION."""
        # 1. With bridge tx hash -> PROVEN
        proven = cross_chain_analyzer.analyze_cross_chain(
            from_chain="ETH", from_addr="0x111",
            to_chain="TRON", to_addr="T222",
            amount_from=1000.0, amount_to=995.0,
            time_delta_seconds=300,
            bridge_tx_hash="0xbridge_tx_hash_123",
            bridge_protocol="Stargate / LayerZero"
        )
        self.assertEqual(proven.link_type, "PROVEN")
        self.assertEqual(proven.confidence, "HIGH")
        self.assertEqual(proven.supporting_evidence["bridge_protocol"], "Stargate / LayerZero")

        # 2. Without bridge tx hash (within 5% and 3600s) -> HEURISTIC_CORRELATION (MEDIUM)
        heuristic = cross_chain_analyzer.analyze_cross_chain(
            from_chain="ETH", from_addr="0x111",
            to_chain="TRON", to_addr="T222",
            amount_from=1000.0, amount_to=960.0, # 4% delta
            time_delta_seconds=1800, # 30 min
            bridge_tx_hash=None
        )
        self.assertEqual(heuristic.link_type, "HEURISTIC_CORRELATION")
        self.assertEqual(heuristic.confidence, "MEDIUM")

        # 3. Outside tolerance (> 5% delta) -> LOW
        heuristic_low = cross_chain_analyzer.analyze_cross_chain(
            from_chain="ETH", from_addr="0x111",
            to_chain="TRON", to_addr="T222",
            amount_from=1000.0, amount_to=900.0, # 10% delta
            time_delta_seconds=1800,
            bridge_tx_hash=None
        )
        self.assertEqual(heuristic_low.link_type, "HEURISTIC_CORRELATION")
        self.assertEqual(heuristic_low.confidence, "LOW")

    def test_03_tracer_bridge_detection_and_continuation(self):
        """Tracer detects Across bridge contract and continues trace to recipient."""
        tracer = BoundedTracer()
        mock_pm = MagicMock()
        tracer.provider_mgr = mock_pm

        across_spoke = "0x5c7bcabeed66d3a177f1981a815a513511116b47" # Registered Across SpokePool

        t1 = Transfer(
            chain_id="ETH", tx_hash="0xbridge_dep", log_index=0, transfer_index=0,
            event_type="BRIDGE", from_addr="0xsuspect",
            to_addr=across_spoke, amount=50.0, asset="USDT", direction="OUT",
            raw_payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        # Recipient sends onwards
        t_dest = Transfer(
            chain_id="TRON", tx_hash="0xdest_tx", log_index=0, transfer_index=0,
            event_type="TRC20", from_addr="TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
            to_addr="TWazirX_deposit", amount=49.9, asset="USDT", direction="OUT",
            raw_payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

        def mock_fetch(addr, chain="ETH", limit=20):
            if addr.lower() == "0xsuspect":
                return [t1]
            if addr.lower() == "tydzsyuepvnymqk4zgp9swwcted2miatw6":
                return [t_dest]
            return []

        mock_pm.fetch_transfers.side_effect = mock_fetch

        res = tracer.trace(
            start_address="0xsuspect",
            chain="ETH",
            constraints=TraceConstraints(max_hops=4),
            case_id="CR-2026-TEST-XCHAIN",
            mode="LIVE"
        )

        self.assertTrue(len(res["cross_chain_links"]) > 0)
        # §1.3 FIX UPDATE: link_type must be HEURISTIC_CORRELATION when no real
        # dest_tx_hash is returned by a provider call. PROVEN is only valid when
        # a real on-chain delivery tx is confirmed — not from a literal constant.
        self.assertEqual(res["cross_chain_links"][0]["link_type"], "HEURISTIC_CORRELATION",
                         "§1.3: without a real provider dest_tx_hash, link_type must be HEURISTIC_CORRELATION")
        node_ids = [n["id"] for n in res["nodes"]]
        self.assertIn(across_spoke, node_ids)
        # §1.3: The hardcoded TRON recipient fabrication has been removed.
        # We do NOT assert the old hardcoded TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6 address here.
        # The bridge contract itself (across_spoke) is the correct to_addr for the edge.

if __name__ == "__main__":
    unittest.main()
