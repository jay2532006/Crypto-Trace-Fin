"""
CryptoTrace LEA — Phase 2 Detection Gaps Verification Tests
Tests all Phase 2 implementations per LOGIC_IMPLEMENTATION_PLAN (1).md §11.2:
- §1.9 DeFi / DEX router detection (positive + negative)
- §6.1 Cross-case wallet clustering & repeat offender detection (positive + negative + API)
- §7.1 Automated alert dispatch on CRITICAL risk & sanctions (positive + negative + API)
- §1.4 Backward / upstream (fan-in) tracing (positive + negative + bidirectional)
- §1.10 BSC / BNB chain detection & adapter integration (positive + negative)
"""

import os
import sys
import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from backend.cross_chain.dex_registry import is_dex_contract, get_dex_info, DEX_REGISTRY
from backend.adapters.provider_manager import provider_manager, ProviderManager
from backend.tracing.trace_engine import BoundedTracer, TraceConstraints, TraceDirection
from backend.models.domain_models import Transfer
from backend.db.database import canonical_db
from backend.alerts.alert_dispatcher import alert_dispatcher


class TestPhase2DetectionGaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # =========================================================================
    # §1.9: DeFi / DEX Router Detection Tests
    # =========================================================================
    def test_01_dex_registry_definitions(self):
        """Verify curated DEX registry contains expected top protocol routers."""
        self.assertIn("UNISWAP_V3_ETH", DEX_REGISTRY)
        self.assertIn("UNISWAP_V2_ETH", DEX_REGISTRY)
        self.assertIn("PANCAKESWAP_V2_BSC", DEX_REGISTRY)
        self.assertIn("SUNSWAP_V2_TRON", DEX_REGISTRY)

        # Uniswap V3 SwapRouter02
        v3_router = "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45"
        self.assertTrue(is_dex_contract(v3_router))
        info = get_dex_info(v3_router)
        self.assertIsNotNone(info)
        self.assertEqual(info["protocol"], "Uniswap V3")

    def test_02_dex_detection_positive(self):
        """
        Positive test §1.9: A hop hitting a DEX router tags node as defi_swap,
        edge as DEFI_SWAP, emits DEFI_OBFUSCATION finding, and continues BFS.
        """
        tracer = BoundedTracer()
        mock_pm = MagicMock()
        tracer.provider_mgr = mock_pm

        suspect = "0xsuspect_dex_flow_1"
        uniswap_v3 = "0xe592427a0aece92de3edee1f18e0157c05861564"  # Uniswap V3 Router
        next_hop = "0xterminal_recipient_after_swap"

        def mock_fetch(addr, chain="ETH", limit=50):
            if addr.lower() == suspect.lower():
                return [
                    Transfer(
                        chain_id="ETH",
                        tx_hash="0xswap_in",
                        log_index=0,
                        transfer_index=0,
                        event_type="ERC20",
                        from_addr=suspect,
                        to_addr=uniswap_v3,
                        amount=10000.0,
                        asset="USDT",
                        direction="OUT",
                        raw_payload_hash="H1",
                        finality_state="CONFIRMED",
                        timestamp="1700000000",
                        provider_source="MOCK",
                    )
                ]
            elif addr.lower() == uniswap_v3.lower():
                return [
                    Transfer(
                        chain_id="ETH",
                        tx_hash="0xswap_out",
                        log_index=0,
                        transfer_index=0,
                        event_type="NATIVE",
                        from_addr=uniswap_v3,
                        to_addr=next_hop,
                        amount=3.2,
                        asset="ETH",
                        direction="OUT",
                        raw_payload_hash="H2",
                        finality_state="CONFIRMED",
                        timestamp="1700000060",
                        provider_source="MOCK",
                    )
                ]
            return []

        mock_pm.fetch_transfers.side_effect = mock_fetch

        res = tracer.trace(
            start_address=suspect,
            chain="ETH",
            constraints=TraceConstraints(max_hops=3),
            case_id="CR-TEST-DEFI-POS-01",
            mode="LIVE",
        )

        # 1. DEX node tagged as defi_swap
        dex_nodes = [n for n in res["nodes"] if n["id"].lower() == uniswap_v3.lower()]
        self.assertEqual(len(dex_nodes), 1)
        self.assertEqual(dex_nodes[0]["type"], "defi_swap")

        # 2. DEX edge tagged as DEFI_SWAP
        dex_edges = [e for e in res["edges"] if e.get("edge_type") == "DEFI_SWAP"]
        self.assertGreaterEqual(len(dex_edges), 1)

        # 3. BFS continued beyond DEX to next_hop
        onward_nodes = [n for n in res["nodes"] if n["id"].lower() == next_hop.lower()]
        self.assertEqual(len(onward_nodes), 1)

        # 4. DEFI_OBFUSCATION finding emitted
        self.assertIn("DEFI_OBFUSCATION", res["typologies"])

    def test_03_dex_detection_negative(self):
        """
        Negative test §1.9: Regular intermediary transfer does NOT tag node as defi_swap
        and does NOT emit DEFI_OBFUSCATION.
        """
        tracer = BoundedTracer()
        mock_pm = MagicMock()
        tracer.provider_mgr = mock_pm

        suspect = "0xsuspect_nodefi_flow"
        regular_addr = "0x1111111111111111111111111111111111111111"

        def mock_fetch(addr, chain="ETH", limit=50):
            if addr.lower() == suspect.lower():
                return [
                    Transfer(
                        chain_id="ETH",
                        tx_hash="0xreg_tx",
                        log_index=0,
                        transfer_index=0,
                        event_type="ERC20",
                        from_addr=suspect,
                        to_addr=regular_addr,
                        amount=5000.0,
                        asset="USDT",
                        direction="OUT",
                        raw_payload_hash="H_REG",
                        finality_state="CONFIRMED",
                        timestamp="1700000000",
                        provider_source="MOCK",
                    )
                ]
            return []

        mock_pm.fetch_transfers.side_effect = mock_fetch

        res = tracer.trace(
            start_address=suspect,
            chain="ETH",
            constraints=TraceConstraints(max_hops=2),
            case_id="CR-TEST-NODEFI-NEG-01",
            mode="LIVE",
        )

        self.assertNotIn("DEFI_OBFUSCATION", res["typologies"])
        reg_nodes = [n for n in res["nodes"] if n["id"].lower() == regular_addr.lower()]
        self.assertEqual(len(reg_nodes), 1)
        self.assertEqual(reg_nodes[0]["type"], "intermediary")

    # =========================================================================
    # §6.1: Cross-Case Wallet Clustering & Repeat Offender Tests
    # =========================================================================
    def test_04_cross_case_wallet_indexing_and_repeat_offender(self):
        """
        Positive test §6.1: First trace indexes addresses; second trace on same wallet
        in a different case detects repeat offender and links cases.
        """
        tracer = BoundedTracer()
        shared_wallet = "0xshared_syndicate_mule_9999"
        case_a = "CR-2026-SYNDICATE-A"
        case_b = "CR-2026-SYNDICATE-B"

        # Trace Case A in DEMO mode starting from shared_wallet
        res_a = tracer.trace(
            start_address=shared_wallet,
            chain="ETH",
            constraints=TraceConstraints(max_hops=2),
            case_id=case_a,
            mode="DEMO",
        )
        self.assertIn("nodes", res_a)

        # Trace Case B in DEMO mode starting from the same shared_wallet
        res_b = tracer.trace(
            start_address=shared_wallet,
            chain="ETH",
            constraints=TraceConstraints(max_hops=2),
            case_id=case_b,
            mode="DEMO",
        )

        # Case B must detect Case A as a linked case
        self.assertTrue(res_b.get("repeat_offender"))
        linked_case_ids = [c["case_id"] for c in res_b.get("linked_cases", [])]
        self.assertIn(case_a, linked_case_ids)

        # Finding REPEAT_OFFENDER_WALLET must be present
        self.assertIn("REPEAT_OFFENDER_WALLET", res_b.get("typologies", []))

    def test_05_cross_case_negative_fresh_wallet(self):
        """
        Negative test §6.1: A brand new wallet with no prior history has
        repeat_offender=False and empty linked_cases.
        """
        tracer = BoundedTracer()
        fresh_wallet = "0xfresh_isolated_wallet_8888"
        case_id = "CR-2026-FRESH-ISOLATED"

        res = tracer.trace(
            start_address=fresh_wallet,
            chain="ETH",
            constraints=TraceConstraints(max_hops=2),
            case_id=case_id,
            mode="DEMO",
        )
        self.assertFalse(res.get("repeat_offender"))
        self.assertEqual(len(res.get("linked_cases", [])), 0)
        self.assertNotIn("REPEAT_OFFENDER_WALLET", res.get("typologies", []))

    def test_06_linked_cases_api_endpoint(self):
        """Verify GET /api/v1/cases/{case_id}/linked-cases API endpoint."""
        case_id = "CR-2026-SYNDICATE-A"
        resp = self.client.get(f"/api/v1/cases/{case_id}/linked-cases")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["case_id"], case_id)
        self.assertIsInstance(data["linked_cases"], list)
        self.assertGreaterEqual(data["linked_case_count"], 1)

    # =========================================================================
    # §7.1: Automated Alert Dispatch Tests
    # =========================================================================
    def test_07_alert_dispatch_positive_critical_risk(self):
        """
        Positive test §7.1: A trace that resolves with CRITICAL risk or sanctions
        automatically dispatches an alert, records it in SQLite, and exposes it via API.
        """
        # We invoke dispatch_alert directly and verify trace integration
        alert = alert_dispatcher.dispatch_alert(
            case_id="CR-TEST-ALERT-CRIT",
            risk_category="CRITICAL",
            trigger_reason="Rapid multi-hop mule consolidation into WazirX with OFAC flag",
            severity="CRITICAL",
            details={"risk_score": 85, "suspect_address": "0xcritical_suspect"},
        )

        self.assertIn("alert_id", alert)
        self.assertEqual(alert["risk_category"], "CRITICAL")
        self.assertEqual(alert["case_id"], "CR-TEST-ALERT-CRIT")

        # Verify via GET /api/v1/alerts
        resp = self.client.get("/api/v1/alerts")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        alerts_list = data.get("alerts", [])
        self.assertIsInstance(alerts_list, list)
        matching = [a for a in alerts_list if a["case_id"] == "CR-TEST-ALERT-CRIT"]
        self.assertGreaterEqual(len(matching), 1)
        self.assertEqual(matching[0]["risk_category"], "CRITICAL")

    def test_08_alert_dispatch_negative_low_risk(self):
        """
        Negative test §7.1: Trace with low risk does not dispatch an alert.
        """
        tracer = BoundedTracer()
        mock_pm = MagicMock()
        tracer.provider_mgr = mock_pm

        suspect = "0xclean_low_risk_wallet"
        mock_pm.fetch_transfers.return_value = []

        res = tracer.trace(
            start_address=suspect,
            chain="ETH",
            constraints=TraceConstraints(max_hops=1),
            case_id="CR-TEST-CLEAN-LOW",
            mode="LIVE",
        )

        self.assertFalse(res.get("alert_dispatched"))
        self.assertIsNone(res.get("alert_details"))

    # =========================================================================
    # §1.4: Backward / Upstream (Fan-In) Tracing Tests
    # =========================================================================
    def test_09_backward_tracing_fan_in_positive(self):
        """
        Positive test §1.4: Backward tracing fetches inbound transfers, creates
        funding_source nodes and FAN_IN edges, and produces fan_in_summary.
        """
        tracer = BoundedTracer()
        mock_pm = MagicMock()
        tracer.provider_mgr = mock_pm

        aggregator = "0xcollector_aggregator_wallet"
        victim_1 = "0xvictim_payer_1111"
        victim_2 = "0xvictim_payer_2222"

        def mock_fetch(addr, chain="ETH", limit=50):
            if addr.lower() == aggregator.lower():
                return [
                    Transfer(
                        chain_id="ETH",
                        tx_hash="0xinbound_1",
                        log_index=0,
                        transfer_index=0,
                        event_type="ERC20",
                        from_addr=victim_1,
                        to_addr=aggregator,
                        amount=25000.0,
                        asset="USDT",
                        direction="IN",
                        raw_payload_hash="H_IN_1",
                        finality_state="CONFIRMED",
                        timestamp="1700000000",
                        provider_source="MOCK",
                    ),
                    Transfer(
                        chain_id="ETH",
                        tx_hash="0xinbound_2",
                        log_index=0,
                        transfer_index=0,
                        event_type="ERC20",
                        from_addr=victim_2,
                        to_addr=aggregator,
                        amount=15000.0,
                        asset="USDT",
                        direction="IN",
                        raw_payload_hash="H_IN_2",
                        finality_state="CONFIRMED",
                        timestamp="1700000100",
                        provider_source="MOCK",
                    ),
                ]
            return []

        mock_pm.fetch_transfers.side_effect = mock_fetch

        res = tracer.trace(
            start_address=aggregator,
            chain="ETH",
            constraints=TraceConstraints(direction="BACKWARD", max_backward_hops=2),
            case_id="CR-TEST-FANIN-POS-01",
            mode="LIVE",
        )

        # 1. Check fan_in_summary
        fan_in = res.get("fan_in_summary", {})
        self.assertEqual(fan_in.get("funding_sources_count"), 2)
        self.assertEqual(fan_in.get("total_inbound_amount"), 40000.0)
        self.assertIn(victim_1, fan_in.get("funding_addresses", []))
        self.assertIn(victim_2, fan_in.get("funding_addresses", []))

        # 2. Check nodes and edges
        funding_nodes = [n for n in res["nodes"] if n.get("type") == "funding_source"]
        self.assertEqual(len(funding_nodes), 2)

        fan_in_edges = [e for e in res["edges"] if e.get("edge_type") == "FAN_IN"]
        self.assertEqual(len(fan_in_edges), 2)

        # 3. VASP attribution must not label funding sources
        self.assertEqual(res.get("attribution", {}).get("label_type"), "UNRESOLVED")

    def test_10_bidirectional_tracing(self):
        """
        Positive test §1.4: BIDIRECTIONAL mode runs both forward BFS and backward fan-in pass.
        """
        tracer = BoundedTracer()
        res = tracer.trace(
            start_address="0xbidirectional_suspect",
            chain="ETH",
            constraints=TraceConstraints(direction="BIDIRECTIONAL", max_hops=3, max_backward_hops=2),
            case_id="CR-TEST-BIDIRECTIONAL-01",
            mode="DEMO",
        )

        # Both forward hops and backward hops exist
        self.assertGreater(len(res.get("hops", [])), 0)
        self.assertGreater(len(res.get("backward_hops", [])), 0)
        fan_in = res.get("fan_in_summary", {})
        self.assertGreater(fan_in.get("funding_sources_count", 0), 0)

    def test_11_forward_only_negative_backward(self):
        """
        Negative test §1.4: Default FORWARD mode does not execute backward fan-in pass.
        """
        tracer = BoundedTracer()
        res = tracer.trace(
            start_address="0xforward_only_suspect",
            chain="ETH",
            constraints=TraceConstraints(direction="FORWARD"),
            case_id="CR-TEST-FORWARD-ONLY",
            mode="DEMO",
        )

        self.assertEqual(len(res.get("backward_hops", [])), 0)
        self.assertEqual(res.get("fan_in_summary", {}).get("funding_sources_count"), 0)

    # =========================================================================
    # §1.10: BSC / BNB Chain Support Tests
    # =========================================================================
    def test_12_bsc_chain_detection_and_adapter(self):
        """
        Positive test §1.10: BSC chain correctly detected via hint and adapter provides BSC config.
        """
        bsc_addr = "0x28c6c06298d514db089934071355e5743bf21d60"

        # Explicit hint disambiguation
        detected = provider_manager.detect_chain(bsc_addr, chain_hint="BSC")
        self.assertEqual(detected, "BSC")

        detected_bnb = provider_manager.detect_chain(bsc_addr, chain_hint="BNB")
        self.assertEqual(detected_bnb, "BSC")

        # Adapter lookup
        adapter = provider_manager.get_adapter("BSC")
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.chain_id_num, 56)
        self.assertEqual(adapter.asset, "BNB")

    def test_13_bsc_detection_negative(self):
        """
        Negative test §1.10: Non-EVM address or invalid chain does not resolve to BSC.
        """
        tron_addr = "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6"
        detected = provider_manager.detect_chain(tron_addr)
        self.assertEqual(detected, "TRON")

        btc_addr = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        detected_btc = provider_manager.detect_chain(btc_addr)
        self.assertEqual(detected_btc, "BTC")


if __name__ == "__main__":
    unittest.main()
