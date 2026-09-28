# backend/tests/test_golden_baseline.py
"""
CryptoTrace LEA - Golden Baseline Regression Test
Asserts the DEMO-mode tracer returns the expected key set, typologies, and termination reasons
on the 3 original demo fixtures. Ensures any changes to LIVE mode or refactoring do not break
the deterministic DEMO baseline.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from backend.fixtures.demo_cases_v2 import CRYPTO_TRACE_FIXTURES

class TestGoldenBaseline(unittest.TestCase):
    def test_golden_fixtures_demo_mode(self):
        expected_keys = {
            'attribution', 'case_id', 'chain', 'data_completeness_pct', 'edges',
            'execution_time_ms', 'hops', 'mode', 'nodes', 'ofac_sanction_hit',
            'pattern_findings', 'recovery_estimate', 'risk', 'suspect_address',
            'termination_reason', 'total_edges', 'total_nodes', 'typologies'
        }

        for fix in CRYPTO_TRACE_FIXTURES[:3]:
            res = bounded_tracer.trace(
                start_address=fix["suspect_wallet"],
                chain=fix["chain"],
                constraints=TraceConstraints(max_hops=4),
                case_id=fix["case_id"],
                mode="DEMO"
            )

            # All expected keys must be present (additive keys allowed)
            for k in expected_keys:
                self.assertIn(k, res, f"Missing key {k} in fixture {fix['case_id']}")

            self.assertEqual(res["mode"], "DEMO")
            self.assertEqual(res["case_id"], fix["case_id"])
            self.assertIn("MULE_NETWORK", res["typologies"])
            self.assertEqual(res["termination_reason"], "MAX_HOPS")
            self.assertEqual(len(res["hops"]), 4)
            self.assertEqual(len(res["nodes"]), 5)

if __name__ == "__main__":
    unittest.main()
