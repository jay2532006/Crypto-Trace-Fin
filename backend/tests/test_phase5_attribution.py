# backend/tests/test_phase5_attribution.py
"""
CryptoTrace LEA - Attribution Correctness Verification Tests (Phase 1)
Validates fixes for D3, D5, D9:
1. Dynamic attribution resolution instead of hardcoded WazirX
2. Ambiguous multi-match resolution (0x28c6c062... matches WAZIRX & BINANCE, caps confidence at MEDIUM)
3. Exact single-match resolution (0x5041ed75... matches WAZIRX -> VERIFIED, HIGH)
4. Unknown address -> vasp_name: UNKNOWN, label_type: UNRESOLVED
5. DEMO mode preservation (fixtures unchanged)
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.attribution.attribution_resolver import attribution_resolver, ResolvedAttribution
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from backend.fixtures.demo_cases_v2 import CRYPTO_TRACE_FIXTURES

class TestPhase5Attribution(unittest.TestCase):
    def test_01_unknown_address_unresolved(self):
        """Unknown terminal wallet yields vasp_key=None and UNRESOLVED label."""
        trace_result = {
            "hops": [
                {"from_address": "0xvictim", "to_address": "0xunknown1234567890abcdef", "amount": 10.0}
            ]
        }
        resolved = attribution_resolver.resolve(trace_result)
        self.assertIsNone(resolved.vasp_key)
        self.assertEqual(resolved.label_type, "UNRESOLVED")
        self.assertFalse(resolved.exact)
        self.assertEqual(len(resolved.candidates), 0)

    def test_02_ambiguous_match_caps_confidence(self):
        """0x28c6c062... appears in both WAZIRX and BINANCE -> AMBIGUOUS, capped at MEDIUM."""
        trace_result = {
            "hops": [
                {"from_address": "0xmule", "to_address": "0x28c6c06298d514db089934071355e5743bf21d60", "amount": 5000.0}
            ]
        }
        resolved = attribution_resolver.resolve(trace_result)
        self.assertTrue(resolved.is_ambiguous)
        self.assertIn("WAZIRX", resolved.candidates)
        self.assertIn("BINANCE", resolved.candidates)
        self.assertEqual(resolved.confidence_cap, "MEDIUM")
        self.assertEqual(resolved.label_type, "INFERRED")

    def test_03_exact_single_match_wazirx(self):
        """0x5041ed75... is unique to WAZIRX -> VERIFIED."""
        trace_result = {
            "hops": [
                {"from_address": "0xmule", "to_address": "0x5041ed759dd4afc3a72b8192c143f72f4724081a", "amount": 5000.0}
            ]
        }
        resolved = attribution_resolver.resolve(trace_result)
        self.assertFalse(resolved.is_ambiguous)
        self.assertEqual(resolved.vasp_key, "WAZIRX")
        self.assertEqual(resolved.label_type, "VERIFIED")
        self.assertTrue(resolved.exact)

    def test_04_demo_fixture_preserved(self):
        """DEMO mode on CR-2026-MULE-IND-01 continues to attribute to WAZIRX."""
        fix = CRYPTO_TRACE_FIXTURES[0]
        res = bounded_tracer.trace(
            start_address=fix["suspect_wallet"],
            chain=fix["chain"],
            constraints=TraceConstraints(max_hops=4),
            case_id=fix["case_id"],
            mode="DEMO"
        )
        self.assertIn("WazirX", res["attribution"]["vasp_name"])
        self.assertIn(res["attribution"]["label_type"], ["VERIFIED", "INFERRED"])

if __name__ == "__main__":
    unittest.main()
