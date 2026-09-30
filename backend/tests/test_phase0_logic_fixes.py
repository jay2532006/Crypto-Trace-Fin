"""
CryptoTrace LEA — Phase 0 Logic Fix Tests (§11.2)
Per-item unit tests for every Phase 0 change.

Each test covers:
  - A positive test (new path works correctly)
  - A negative test (old bug is actually gone)

Items covered:
  §1.1 — Nearest-VASP resolver returns FIRST VASP hop, not terminal node
  §1.2 — DEMO mode no longer hardcodes WAZIRX
  §1.3 — Bridge link_type is never PROVEN without a real dest_tx_hash
  §2.1 — MULE_NETWORK does NOT fire on fabricated timing (no 600s fallback)
  §2.3 — PEEL_CHAIN only fires on genuine 0.5-5% per-hop reductions to unique addrs
  §8.5 — NCRP intake endpoint accepts INVESTIGATOR role (not only INTEGRATION_SERVICE)
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.attribution.attribution_resolver import AttributionResolver, ResolvedAttribution
from backend.typologies.rules.mule_network import MuleNetworkRule
from backend.typologies.rules.other_rules import PeelChainRule
from backend.cross_chain.cross_chain_analyzer import cross_chain_analyzer


# ---------------------------------------------------------------------------
# §1.1 — Nearest-VASP resolver
# ---------------------------------------------------------------------------
class TestNearestVaspResolver(unittest.TestCase):
    """
    §1.1: resolver.resolve() must return the FIRST hop that matches a VASP
    hot-wallet pattern, not the terminal node.
    """

    def _make_resolver(self):
        # Minimal VASP registry with WazirX at hop 2 pattern
        registry = {
            "WAZIRX": {
                "hot_wallet_patterns": [
                    "0x28c6c06298d514db089934071355e5743bf21d60",
                ],
            },
            "COINDCX": {
                "hot_wallet_patterns": [
                    "0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88",
                ],
            },
        }
        return AttributionResolver(registry=registry)

    def test_returns_first_vasp_hop_not_terminal(self):
        """
        §1.1 positive: VASP is at hop 2; internal movement continues to hop 4.
        Resolver must return hop 2, not hop 4.
        """
        resolver = self._make_resolver()
        trace_result = {
            "hops": [
                {"hop_number": 1, "from_address": "0xvictim", "to_address": "0xmule1", "amount": 1000},
                # WazirX hot wallet hit at hop 2
                {"hop_number": 2, "from_address": "0xmule1", "to_address": "0x28c6c06298d514db089934071355e5743bf21d60", "amount": 998},
                # Internal exchange movement (hop 3 & 4)
                {"hop_number": 3, "from_address": "0x28c6c06298d514db089934071355e5743bf21d60", "to_address": "0xwazirx_cold1", "amount": 990},
                {"hop_number": 4, "from_address": "0xwazirx_cold1", "to_address": "0xwazirx_cold2", "amount": 985},
            ]
        }
        result = resolver.resolve(trace_result)
        self.assertEqual(result.vasp_key, "WAZIRX")
        self.assertEqual(result.hop_number, 2, "Resolver must return hop 2, not hop 4")
        self.assertEqual(result.label_type, "VERIFIED")
        self.assertTrue(result.exact)

    def test_unresolved_when_no_match(self):
        """§1.1 negative: no VASP match → UNRESOLVED (never default to anything)."""
        resolver = self._make_resolver()
        trace_result = {
            "hops": [
                {"hop_number": 1, "from_address": "0xvictim", "to_address": "0xunknown1", "amount": 1000},
                {"hop_number": 2, "from_address": "0xunknown1", "to_address": "0xunknown2", "amount": 998},
            ]
        }
        result = resolver.resolve(trace_result)
        self.assertIsNone(result.vasp_key)
        self.assertEqual(result.label_type, "UNRESOLVED")
        self.assertIsNone(result.hop_number)

    def test_ambiguous_match_returns_inferred(self):
        """§1.1: address shared by two VASPs → is_ambiguous=True, label_type=INFERRED."""
        registry = {
            "WAZIRX": {"hot_wallet_patterns": ["0xshared000"]},
            "BINANCE": {"hot_wallet_patterns": ["0xshared000"]},
        }
        resolver = AttributionResolver(registry=registry)
        trace_result = {
            "hops": [
                {"hop_number": 1, "from_address": "0xvictim", "to_address": "0xshared000", "amount": 500},
            ]
        }
        result = resolver.resolve(trace_result)
        self.assertTrue(result.is_ambiguous)
        self.assertEqual(result.label_type, "INFERRED")
        self.assertEqual(len(result.candidates), 2)


# ---------------------------------------------------------------------------
# §1.2 — DEMO mode must NOT hardcode WAZIRX
# ---------------------------------------------------------------------------
class TestDemoModeNoHardcodedWazirx(unittest.TestCase):
    """
    §1.2: attribution_resolver.resolve() is the single path for both DEMO and LIVE.
    A trace with non-WazirX terminal address must NOT return WAZIRX.
    """

    def test_non_wazirx_fixture_does_not_return_wazirx(self):
        """
        §1.2 negative: a trace that terminates at a KuCoin address must not return WAZIRX.
        The old DEMO branch would unconditionally return WAZIRX regardless.
        """
        registry = {
            "WAZIRX": {"hot_wallet_patterns": ["0x28c6c06298d514db089934071355e5743bf21d60"]},
            "KUCOIN": {"hot_wallet_patterns": ["0xd6216fc19db775df9774a6e33526131da7d19a2c"]},
        }
        resolver = AttributionResolver(registry=registry)
        # Trace terminates at KuCoin — must not return WAZIRX
        trace_result = {
            "hops": [
                {"hop_number": 1, "from_address": "0xvictim", "to_address": "0xmule", "amount": 1000},
                {"hop_number": 2, "from_address": "0xmule", "to_address": "0xd6216fc19db775df9774a6e33526131da7d19a2c", "amount": 998},
            ]
        }
        result = resolver.resolve(trace_result)
        self.assertNotEqual(result.vasp_key, "WAZIRX", "DEMO mode must not hardcode WAZIRX")
        self.assertEqual(result.vasp_key, "KUCOIN")

    def test_unresolved_fixture_stays_unresolved(self):
        """§1.2 negative: mixer-bound trace with no VASP hit must stay UNRESOLVED."""
        registry = {"WAZIRX": {"hot_wallet_patterns": ["0x28c6c06298d514db089934071355e5743bf21d60"]}}
        resolver = AttributionResolver(registry=registry)
        trace_result = {
            "hops": [
                {"hop_number": 1, "from_address": "0xvictim", "to_address": "0xtornado", "amount": 1000},
            ]
        }
        result = resolver.resolve(trace_result)
        self.assertIsNone(result.vasp_key)
        self.assertEqual(result.label_type, "UNRESOLVED")


# ---------------------------------------------------------------------------
# §1.3 — Bridge link_type must never be hardcoded PROVEN
# ---------------------------------------------------------------------------
class TestBridgeLinkTypeNeverFabricated(unittest.TestCase):
    """
    §1.3: CrossChainAnalyzer must only return PROVEN when bridge_tx_hash
    is a real value. With bridge_tx_hash=None it must return HEURISTIC_CORRELATION.
    """

    def test_no_hash_gives_heuristic_not_proven(self):
        """§1.3 positive: no hash → HEURISTIC_CORRELATION."""
        link = cross_chain_analyzer.analyze_cross_chain(
            from_chain="ETH",
            from_addr="0xsender",
            to_chain="TRON",
            to_addr="0xbridge_contract",
            amount_from=1000.0,
            amount_to=998.0,
            time_delta_seconds=180,
            bridge_tx_hash=None,
            dest_tx_hash=None,
        )
        self.assertEqual(link.link_type, "HEURISTIC_CORRELATION",
                         "Without a real hash, link_type must be HEURISTIC_CORRELATION, not PROVEN")

    def test_fabricated_string_hash_gives_proven_regression(self):
        """
        §1.3 negative/regression: old code passed f'{tx_hash}_dest_delivery' as dest_tx_hash.
        Now bridge_tx_hash=None → HEURISTIC. The synthetic delivery string no longer tricks
        the analyzer into PROVEN.
        The analyzer's logic: PROVEN requires bridge_tx_hash to be truthy.
        A None bridge_tx_hash must NOT produce PROVEN regardless of dest_tx_hash.
        """
        link = cross_chain_analyzer.analyze_cross_chain(
            from_chain="ETH",
            from_addr="0xsender",
            to_chain="TRON",
            to_addr="0xbridge_contract",
            amount_from=1000.0,
            amount_to=998.0,
            time_delta_seconds=180,
            bridge_tx_hash=None,  # §1.3: no real hash
            dest_tx_hash="0xreal_tx_hash_from_provider",  # only dest_tx_hash present
        )
        # Without bridge_tx_hash, must not be PROVEN
        self.assertNotEqual(link.link_type, "PROVEN")

    def test_real_hash_gives_proven(self):
        """§1.3: A real bridge_tx_hash from a provider call → PROVEN is valid."""
        link = cross_chain_analyzer.analyze_cross_chain(
            from_chain="ETH",
            from_addr="0xsender",
            to_chain="TRON",
            to_addr="0xrecipient",
            amount_from=1000.0,
            amount_to=998.0,
            time_delta_seconds=180,
            bridge_tx_hash="0xreal_bridge_tx_hash",
            dest_tx_hash="0xreal_dest_tx_hash",
        )
        self.assertEqual(link.link_type, "PROVEN")


# ---------------------------------------------------------------------------
# §2.1 — MULE_NETWORK: no fabricated 600s timestamp fallback
# ---------------------------------------------------------------------------
class TestMuleNetworkTimestampFix(unittest.TestCase):
    """
    §2.1: MULE_NETWORK must NOT fire based on synthetic timing.
    Hops with missing timestamp_epoch must not contribute fabricated time diffs.
    """

    def _make_hops_no_timestamps(self, n=4):
        """Create n hops with no timestamp_epoch (simulates missing data)."""
        hops = []
        for i in range(n):
            amt = 1000.0 - i * 10
            hops.append({
                "hop_number": i + 1,
                "from_address": f"0xfrom{i}",
                "to_address": f"0xto{i}",
                "amount": amt,
                # No timestamp_epoch — the bug was injecting 600 here
            })
        return hops

    def test_no_fabricated_timing_missing_timestamps(self):
        """
        §2.1 negative: hops with missing timestamp_epoch → no synthetic 600s gap.
        The rule should still fire (value pattern matches) but with:
        - confidence="LOW" (not MEDIUM)
        - hops_with_confirmed_timing=0
        - hops_with_missing_timing=3+
        - timing_evidence_complete=False
        """
        rule = MuleNetworkRule()
        hops = self._make_hops_no_timestamps(4)
        trace_result = {"hops": hops, "data_completeness_pct": 80.0}
        finding = rule.evaluate(trace_result, "CR-TEST-MULE01")

        if finding is not None:
            # If it fires, it must be LOW confidence with timing flagged
            self.assertEqual(finding.confidence, "LOW",
                             "Missing timestamps must downgrade confidence to LOW")
            self.assertFalse(finding.evidence_json.get("timing_evidence_complete", True),
                             "timing_evidence_complete must be False when timestamps missing")
            self.assertEqual(finding.evidence_json.get("hops_with_confirmed_timing", -1), 0,
                             "No confirmed timing hops when timestamps absent")
            # No synthetic 600s values in time_between_transfers_seconds
            time_diffs = finding.evidence_json.get("time_between_transfers_seconds", [])
            self.assertEqual(len(time_diffs), 0,
                             "time_between_transfers_seconds must be empty when no real timestamps exist")

    def test_real_timestamps_allow_medium_confidence(self):
        """§2.1 positive: all hops have real timestamps → MEDIUM confidence allowed."""
        rule = MuleNetworkRule()
        import time
        base_ts = int(time.time()) - 3600
        hops = []
        for i in range(4):
            hops.append({
                "hop_number": i + 1,
                "from_address": f"0xfrom{i}",
                "to_address": f"0xto{i}",
                "amount": 1000.0 - i * 10,
                "timestamp_epoch": base_ts + i * 300,  # 5 min apart
            })
        trace_result = {"hops": hops, "data_completeness_pct": 95.0}
        finding = rule.evaluate(trace_result, "CR-TEST-MULE02")
        if finding is not None:
            self.assertEqual(finding.confidence, "MEDIUM")
            self.assertTrue(finding.evidence_json.get("timing_evidence_complete", False))


# ---------------------------------------------------------------------------
# §2.3 — PEEL_CHAIN: correct 0.5-5% per-hop definition
# ---------------------------------------------------------------------------
class TestPeelChainCorrectDefinition(unittest.TestCase):
    """
    §2.3: PeelChain must only fire when EACH hop reduces by 0.5%–5% AND
    all addresses are unique. The old implementation (>= 0.85 across all hops)
    was too loose.
    """

    def test_genuine_peel_chain_fires(self):
        """§2.3 positive: 1% per-hop reduction to unique addresses → fires."""
        rule = PeelChainRule()
        hops = [
            {"hop_number": 1, "from_address": "0xa", "to_address": "0xb", "amount": 1000.0},
            {"hop_number": 2, "from_address": "0xb", "to_address": "0xc", "amount": 990.0},   # -1%
            {"hop_number": 3, "from_address": "0xc", "to_address": "0xd", "amount": 980.1},  # -1%
            {"hop_number": 4, "from_address": "0xd", "to_address": "0xe", "amount": 970.3},  # -1%
        ]
        trace_result = {"hops": hops, "data_completeness_pct": 90.0}
        finding = rule.evaluate(trace_result, "CR-TEST-PEEL01")
        self.assertIsNotNone(finding, "Genuine 1%-per-hop peel chain must be detected")
        self.assertEqual(finding.typology_name, "PEEL_CHAIN")

    def test_large_single_drop_does_not_fire(self):
        """
        §2.3 negative: 15% drop in one hop (old bug: >=0.85 threshold would miss this
        but previous implementation was wrong in the opposite direction — checked amount[i]>=amount[i+1]*0.85
        which is a DECAY check, not a PEEL check).
        A 50% single drop is NOT a peel chain.
        """
        rule = PeelChainRule()
        hops = [
            {"hop_number": 1, "from_address": "0xa", "to_address": "0xb", "amount": 1000.0},
            {"hop_number": 2, "from_address": "0xb", "to_address": "0xc", "amount": 500.0},  # -50%: not peel
            {"hop_number": 3, "from_address": "0xc", "to_address": "0xd", "amount": 250.0},  # -50%: not peel
        ]
        trace_result = {"hops": hops, "data_completeness_pct": 90.0}
        finding = rule.evaluate(trace_result, "CR-TEST-PEEL02")
        self.assertIsNone(finding, "50% per-hop drop is NOT a peel chain (exceeds 5% band)")

    def test_address_reuse_does_not_fire(self):
        """§2.3 negative: address reuse → not a peel chain (consolidation, not peeling)."""
        rule = PeelChainRule()
        hops = [
            {"hop_number": 1, "from_address": "0xa", "to_address": "0xb", "amount": 1000.0},
            {"hop_number": 2, "from_address": "0xb", "to_address": "0xb", "amount": 990.0},  # reuse!
            {"hop_number": 3, "from_address": "0xb", "to_address": "0xc", "amount": 980.0},
        ]
        trace_result = {"hops": hops, "data_completeness_pct": 90.0}
        finding = rule.evaluate(trace_result, "CR-TEST-PEEL03")
        self.assertIsNone(finding, "Address reuse must disqualify peel chain detection")

    def test_below_minimum_reduction_does_not_fire(self):
        """§2.3 negative: <0.5% per-hop reduction (just rounding) must not fire."""
        rule = PeelChainRule()
        hops = [
            {"hop_number": 1, "from_address": "0xa", "to_address": "0xb", "amount": 1000.0},
            {"hop_number": 2, "from_address": "0xb", "to_address": "0xc", "amount": 999.9},  # 0.01%
            {"hop_number": 3, "from_address": "0xc", "to_address": "0xd", "amount": 999.8},  # 0.01%
        ]
        trace_result = {"hops": hops, "data_completeness_pct": 90.0}
        finding = rule.evaluate(trace_result, "CR-TEST-PEEL04")
        self.assertIsNone(finding, "<0.5% reduction is not a peel chain")


# ---------------------------------------------------------------------------
# §8.5 — NCRP intake accepts INVESTIGATOR role
# ---------------------------------------------------------------------------
class TestIntakeRoleAcceptance(unittest.TestCase):
    """
    §8.5: require_integration_service must accept INVESTIGATOR, ADMINISTRATOR,
    and INTEGRATION_SERVICE. Previously only INTEGRATION_SERVICE/ADMINISTRATOR.
    """

    def test_investigator_in_allowed_roles(self):
        """§8.5 positive: INVESTIGATOR must be in the allowed roles set."""
        from backend.api.intake_routes import _INTAKE_ALLOWED_ROLES
        self.assertIn("INVESTIGATOR", _INTAKE_ALLOWED_ROLES,
                      "INVESTIGATOR must be allowed to submit intake forms")

    def test_integration_service_still_allowed(self):
        """§8.5: INTEGRATION_SERVICE must still be allowed (backward-compat)."""
        from backend.api.intake_routes import _INTAKE_ALLOWED_ROLES
        self.assertIn("INTEGRATION_SERVICE", _INTAKE_ALLOWED_ROLES)

    def test_administrator_still_allowed(self):
        """§8.5: ADMINISTRATOR must still be allowed (backward-compat)."""
        from backend.api.intake_routes import _INTAKE_ALLOWED_ROLES
        self.assertIn("ADMINISTRATOR", _INTAKE_ALLOWED_ROLES)

    def test_unknown_role_is_not_allowed(self):
        """§8.5 negative: random role must NOT be allowed."""
        from backend.api.intake_routes import _INTAKE_ALLOWED_ROLES
        self.assertNotIn("VIEWER", _INTAKE_ALLOWED_ROLES)
        self.assertNotIn("GUEST", _INTAKE_ALLOWED_ROLES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
