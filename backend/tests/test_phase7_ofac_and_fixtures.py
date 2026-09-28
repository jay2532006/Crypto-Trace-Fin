# backend/tests/test_phase7_ofac_and_fixtures.py
"""
CryptoTrace LEA - Phase 7 OFAC SDN Screening & Extended Demo Fixtures Tests
Validates:
1. OFAC Sanctions screening and detection on Lazarus Group / SDN designated addresses
2. Dynamic +45 risk score bump leading to CRITICAL risk category
3. Verification that all 6 demo fixtures are registered and intact
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.fixtures.demo_cases_v2 import get_crypto_trace_fixtures
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from engine.ofac_sanctions import screen_ofac_sanctions


class TestPhase7OFACAndFixtures(unittest.TestCase):
    def test_01_all_six_fixtures_present(self):
        fixtures = get_crypto_trace_fixtures()
        self.assertEqual(len(fixtures), 6, "Expected exactly 6 demo fixtures")
        case_ids = [f["case_id"] for f in fixtures]
        self.assertIn("CR-2026-MULE-IND-01", case_ids)
        self.assertIn("CR-2026-MIXER-BOUND-02", case_ids)
        self.assertIn("CR-2026-BRIDGE-XCHAIN-03", case_ids)
        self.assertIn("CR-2026-BRIDGE-XCHAIN-04", case_ids)
        self.assertIn("CR-2026-OFAC-SDN-05", case_ids)
        self.assertIn("CR-2026-MULE-FANIN-06", case_ids)

    def test_02_ofac_screening_function(self):
        # Lazarus Group Ronin exploiter address
        res_sanctioned = screen_ofac_sanctions("0x098b716b8aaf21512996dc57eb0615e2383e2f96", "ETH")
        self.assertTrue(res_sanctioned["is_sanctioned"])
        self.assertEqual(res_sanctioned["risk_level"], "CRITICAL")
        self.assertIn("Lazarus Group", res_sanctioned["entity_name"])
        self.assertEqual(res_sanctioned["ofac_sdn_id"], "34991")

        # Innocent address
        res_clean = screen_ofac_sanctions("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "ETH")
        self.assertFalse(res_clean["is_sanctioned"])
        self.assertEqual(res_clean["risk_level"], "CLEAR")

    def test_03_ofac_sanctions_trace_execution(self):
        res = bounded_tracer.trace(
            start_address="0x098b716b8aaf21512996dc57eb0615e2383e2f96",
            chain="ETH",
            constraints=TraceConstraints(max_hops=4),
            case_id="CR-2026-OFAC-SDN-05",
            mode="DEMO"
        )
        self.assertTrue(res.get("ofac_sanction_hit"))
        self.assertGreaterEqual(len(res.get("ofac_details", [])), 1)
        risk = res.get("risk", {})
        self.assertGreaterEqual(risk.get("risk_score", 0), 75)
        self.assertEqual(risk.get("risk_category"), "CRITICAL")
        self.assertEqual(risk.get("component_scores", {}).get("ofac_sanctions"), 45)


if __name__ == "__main__":
    unittest.main()
