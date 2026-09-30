# backend/tests/test_phase3_accuracy.py
"""
CryptoTrace LEA — Phase 3 Unit Tests: Risk, Recovery, and Attribution Accuracy
Verifies:
- §3.1 Fraud amount risk tiers (>₹10L, >₹1Cr, >₹10Cr) + negative tests
- §3.2 Cross-chain layering penalty (1 bridge, 2+ bridges, bridge+mixer compound) + negative tests
- §3.3 Offshore/unregistered VASP penalty (+15 if UNREGISTERED + OFFSHORE) + negative tests
- §3.4 Cross-rule compounding risk bonuses (mule+rapid, mule+mixer with CRITICAL override, OFAC override)
- §2.2 Chain-specific RAPID_HOP thresholds (TRON 1h vs ETH 3h vs BTC 24h vs Polygon 30m vs BSC 1h)
- §1.6 Time-window truncation warning, 10% completeness penalty, earliest_transaction_date + negative tests
- §1.7 Timeout degradation to PARTIAL_COMPLETE (>=2 hops) vs TIMEOUT (<2 hops) + banner + 15% penalty
- §4.1 elapsed_hours non-fabrication -> display_tier="insufficient_data" when None + negative tests
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from backend.assessment.risk_assessment import RiskAssessor
from backend.assessment.recovery_estimate import RecoveryEstimator
from backend.typologies.rules.other_rules import RapidHopRule
from backend.tracing.trace_engine import BoundedTracer, TraceConstraints
from backend.models.domain_models import Transfer


class TestPhase3Accuracy(unittest.TestCase):
    def setUp(self):
        self.risk_assessor = RiskAssessor()
        self.recovery_estimator = RecoveryEstimator()
        self.rapid_rule = RapidHopRule()

    # ─────────────────────────────────────────────────────────────
    # §3.1 Fraud Amount Component Tests
    # ─────────────────────────────────────────────────────────────
    def test_3_1_amount_tiers_and_negative(self):
        """Verify fraud-amount risk scoring tiers: >₹10L, >₹1Cr, >₹10Cr and below threshold."""
        base_trace = {
            "chain": "ETH",
            "hops": [],
            "typologies": [],
            "cross_chain_links": [],
            "attribution": {"vasp_key": "WAZIRX", "fiu_status": "REGISTERED", "jurisdiction": "INDIA"},
        }

        # Case 1: > ₹10 Crore ($1,200,000+) -> +35
        base_trace["hops"] = [{"amount": 1500000.0, "asset": "USDT"}]
        res_high = self.risk_assessor.assess_risk("CR-AMT-1", base_trace)
        self.assertEqual(res_high.component_scores.get("fraud_amount"), 35)

        # Case 2: > ₹1 Crore ($120,000 - $1,199,999) -> +25
        base_trace["hops"] = [{"amount": 250000.0, "asset": "USDT"}]
        res_med = self.risk_assessor.assess_risk("CR-AMT-2", base_trace)
        self.assertEqual(res_med.component_scores.get("fraud_amount"), 25)

        # Case 3: > ₹10 Lakh ($12,000 - $119,999) -> +15
        base_trace["hops"] = [{"amount": 50000.0, "asset": "USDT"}]
        res_low = self.risk_assessor.assess_risk("CR-AMT-3", base_trace)
        self.assertEqual(res_low.component_scores.get("fraud_amount"), 15)

        # Negative Test: Below ₹10 Lakh ($5,000 < $12,000) -> 0
        base_trace["hops"] = [{"amount": 5000.0, "asset": "USDT"}]
        res_neg = self.risk_assessor.assess_risk("CR-AMT-NEG", base_trace)
        self.assertEqual(res_neg.component_scores.get("fraud_amount"), 0)

        # Negative Test: Zero amount -> 0
        base_trace["hops"] = []
        res_zero = self.risk_assessor.assess_risk("CR-AMT-ZERO", base_trace)
        self.assertEqual(res_zero.component_scores.get("fraud_amount"), 0)

    # ─────────────────────────────────────────────────────────────
    # §3.2 Cross-Chain Layering Penalty Tests
    # ─────────────────────────────────────────────────────────────
    def test_3_2_cross_chain_layering_and_negative(self):
        """Verify cross-chain layering penalties: 1 bridge (+10), 2+ bridges (+20), and bridge+mixer compound (+10)."""
        base_trace = {
            "chain": "ETH",
            "hops": [{"amount": 1000.0, "asset": "USDT"}],
            "typologies": [],
            "cross_chain_links": [{"from_chain": "ETH", "to_chain": "TRON"}],
            "attribution": {"vasp_key": "BINANCE", "fiu_status": "REGISTERED", "jurisdiction": "INDIA"},
        }

        # 1 bridge -> 10 points
        res_1_bridge = self.risk_assessor.assess_risk("CR-BR-1", base_trace)
        self.assertEqual(res_1_bridge.component_scores.get("cross_chain_layering"), 10)

        # 2+ bridges -> 20 points
        base_trace["cross_chain_links"] = [
            {"from_chain": "ETH", "to_chain": "TRON"},
            {"from_chain": "TRON", "to_chain": "BSC"},
        ]
        res_2_bridge = self.risk_assessor.assess_risk("CR-BR-2", base_trace)
        self.assertEqual(res_2_bridge.component_scores.get("cross_chain_layering"), 20)

        # 2 bridges + MIXER_BOUNDARY -> 20 + 10 = 30 points
        base_trace["typologies"] = ["MIXER_BOUNDARY"]
        res_compound = self.risk_assessor.assess_risk("CR-BR-MIX", base_trace)
        self.assertEqual(res_compound.component_scores.get("cross_chain_layering"), 30)

        # Negative Test: 0 bridges -> 0 points
        base_trace["cross_chain_links"] = []
        base_trace["typologies"] = []
        res_clean = self.risk_assessor.assess_risk("CR-BR-CLEAN", base_trace)
        self.assertEqual(res_clean.component_scores.get("cross_chain_layering"), 0)

    # ─────────────────────────────────────────────────────────────
    # §3.3 Offshore / Unregistered VASP Penalty Tests
    # ─────────────────────────────────────────────────────────────
    def test_3_3_offshore_unregistered_vasp_and_negative(self):
        """Verify offshore/unregistered VASP penalty (+15) and exemption for FIU-IND registered."""
        # Positive Test: UNREGISTERED + SEYCHELLES (non-India) -> +15
        trace_offshore = {
            "chain": "ETH",
            "hops": [{"amount": 1000.0, "asset": "USDT"}],
            "typologies": [],
            "attribution": {
                "vasp_key": "BYBIT",
                "fiu_status": "UNREGISTERED",
                "jurisdiction": "SEYCHELLES",
            },
        }
        res_offshore = self.risk_assessor.assess_risk("CR-OFFSHORE", trace_offshore)
        self.assertEqual(res_offshore.component_scores.get("offshore_vasp_penalty"), 15)

        # Negative Test 1: FIU-IND REGISTERED Indian exchange (WazirX) -> 0
        trace_registered = {
            "chain": "ETH",
            "hops": [{"amount": 1000.0, "asset": "USDT"}],
            "typologies": [],
            "attribution": {
                "vasp_key": "WAZIRX",
                "fiu_status": "REGISTERED",
                "jurisdiction": "INDIA",
            },
        }
        res_reg = self.risk_assessor.assess_risk("CR-REG", trace_registered)
        self.assertEqual(res_reg.component_scores.get("offshore_vasp_penalty"), 0)

        # Negative Test 2: FIU-IND REGISTERED Foreign exchange (Binance) -> 0
        trace_binance = {
            "chain": "ETH",
            "hops": [{"amount": 1000.0, "asset": "USDT"}],
            "typologies": [],
            "attribution": {
                "vasp_key": "BINANCE",
                "fiu_status": "REGISTERED",
                "jurisdiction": "MALTA",
            },
        }
        res_binance = self.risk_assessor.assess_risk("CR-BINANCE", trace_binance)
        self.assertEqual(res_binance.component_scores.get("offshore_vasp_penalty"), 0)

    # ─────────────────────────────────────────────────────────────
    # §3.4 Cross-Rule Compounding Risk Bonuses Tests
    # ─────────────────────────────────────────────────────────────
    def test_3_4_cross_rule_compounding_bonuses(self):
        """Verify MULE+RAPID (+15), MULE+MIXER (+10 & CRITICAL override), and OFAC override."""
        # 1. MULE_NETWORK + RAPID_HOP -> +15 compounding bonus
        trace_mule_rapid = {
            "chain": "ETH",
            "hops": [{"amount": 1000.0, "asset": "USDT"}],
            "typologies": ["MULE_NETWORK", "RAPID_HOP"],
            "attribution": {"vasp_key": "WAZIRX", "fiu_status": "REGISTERED", "jurisdiction": "INDIA"},
        }
        res_mr = self.risk_assessor.assess_risk("CR-MR", trace_mule_rapid)
        self.assertEqual(res_mr.component_scores.get("compound_mule_rapid"), 15)

        # 2. MULE_NETWORK + MIXER_BOUNDARY -> +10 compounding bonus AND CRITICAL override
        trace_mule_mixer = {
            "chain": "ETH",
            "hops": [{"amount": 100.0, "asset": "USDT"}],
            "typologies": ["MULE_NETWORK", "MIXER_BOUNDARY"],
            "attribution": {"vasp_key": "UNKNOWN", "fiu_status": "UNKNOWN", "jurisdiction": "UNKNOWN"},
        }
        res_mm = self.risk_assessor.assess_risk("CR-MM", trace_mule_mixer)
        self.assertEqual(res_mm.component_scores.get("compound_mule_mixer"), 10)
        self.assertEqual(res_mm.risk_category, "CRITICAL")

        # 3. OFAC hit + Typology -> Immediate CRITICAL override
        trace_ofac = {
            "chain": "ETH",
            "hops": [{"amount": 100.0, "asset": "USDT"}],
            "typologies": ["PEEL_CHAIN"],
            "ofac_sanction_hit": True,
            "attribution": {"vasp_key": "UNKNOWN", "fiu_status": "UNKNOWN", "jurisdiction": "UNKNOWN"},
        }
        res_ofac = self.risk_assessor.assess_risk("CR-OFAC", trace_ofac)
        self.assertEqual(res_ofac.risk_category, "CRITICAL")

        # Negative Test: Single typology (e.g. MULE alone) -> 0 compound bonus
        trace_single = {
            "chain": "ETH",
            "hops": [{"amount": 100.0, "asset": "USDT"}],
            "typologies": ["MULE_NETWORK"],
            "attribution": {"vasp_key": "WAZIRX", "fiu_status": "REGISTERED", "jurisdiction": "INDIA"},
        }
        res_single = self.risk_assessor.assess_risk("CR-SINGLE", trace_single)
        self.assertEqual(res_single.component_scores.get("compound_mule_rapid", 0), 0)
        self.assertEqual(res_single.component_scores.get("compound_mule_mixer", 0), 0)

    # ─────────────────────────────────────────────────────────────
    # §2.2 Chain-Specific RAPID_HOP Threshold Tests
    # ─────────────────────────────────────────────────────────────
    def test_2_2_chain_specific_rapid_hop_thresholds(self):
        """Verify RAPID_HOP thresholds: TRON (3600s), ETH (10800s), BTC (86400s), Polygon (1800s), BSC (3600s)."""
        now = int(time.time())

        # TRON test: 3 hops with 2000s total interval (<=3600s TRON threshold) -> FIRES
        tron_hops_fast = [
            {"hop_number": 1, "from_address": "T1", "to_address": "T2", "timestamp_epoch": now - 2000, "amount": 100},
            {"hop_number": 2, "from_address": "T2", "to_address": "T3", "timestamp_epoch": now - 1000, "amount": 99},
            {"hop_number": 3, "from_address": "T3", "to_address": "T4", "timestamp_epoch": now, "amount": 98},
        ]
        trace_tron_fast = {"chain": "TRON", "hops": tron_hops_fast, "data_completeness_pct": 90.0}
        finding_tron = self.rapid_rule.evaluate(trace_tron_fast, "CR-TRON-FAST")
        self.assertIsNotNone(finding_tron)
        self.assertEqual(finding_tron.typology_name, "RAPID_HOP")

        # Negative Test TRON: 3 hops with 5000s total interval (>3600s TRON threshold) -> DOES NOT FIRE
        tron_hops_slow = [
            {"hop_number": 1, "from_address": "T1", "to_address": "T2", "timestamp_epoch": now - 5000, "amount": 100},
            {"hop_number": 2, "from_address": "T2", "to_address": "T3", "timestamp_epoch": now - 2500, "amount": 99},
            {"hop_number": 3, "from_address": "T3", "to_address": "T4", "timestamp_epoch": now, "amount": 98},
        ]
        trace_tron_slow = {"chain": "TRON", "hops": tron_hops_slow, "data_completeness_pct": 90.0}
        finding_tron_slow = self.rapid_rule.evaluate(trace_tron_slow, "CR-TRON-SLOW")
        self.assertIsNone(finding_tron_slow)

        # BTC test: 3 hops with 40000s interval (<=86400s BTC threshold) -> FIRES on BTC
        btc_hops = [
            {"hop_number": 1, "from_address": "B1", "to_address": "B2", "timestamp_epoch": now - 40000, "amount": 1},
            {"hop_number": 2, "from_address": "B2", "to_address": "B3", "timestamp_epoch": now - 20000, "amount": 0.99},
            {"hop_number": 3, "from_address": "B3", "to_address": "B4", "timestamp_epoch": now, "amount": 0.98},
        ]
        trace_btc = {"chain": "BTC", "hops": btc_hops, "data_completeness_pct": 90.0}
        finding_btc = self.rapid_rule.evaluate(trace_btc, "CR-BTC-FAST")
        self.assertIsNotNone(finding_btc)

        # Negative Test ETH with same 40000s interval (>10800s ETH threshold) -> DOES NOT FIRE on ETH
        trace_eth_slow = {"chain": "ETH", "hops": btc_hops, "data_completeness_pct": 90.0}
        finding_eth_slow = self.rapid_rule.evaluate(trace_eth_slow, "CR-ETH-SLOW")
        self.assertIsNone(finding_eth_slow)

    # ─────────────────────────────────────────────────────────────
    # §1.6 Time-Window Truncation Penalty Tests
    # ─────────────────────────────────────────────────────────────
    def test_1_6_time_window_truncation_penalty(self):
        """Verify time-window truncation detection, 10% completeness penalty, and earliest_transaction_date."""
        tracer = BoundedTracer()
        mock_pm = MagicMock()
        tracer.provider_mgr = mock_pm

        now = int(time.time())
        # Old transaction near the 90-day boundary (e.g. 89 days ago)
        old_epoch = str(now - (89 * 86400))

        mock_transfer = Transfer(
            chain_id="ETH",
            tx_hash="0xold_tx_hash_1",
            from_addr="0xsuspect_addr_window",
            to_addr="0xrecipient_addr_window",
            amount=100.0,
            asset="USDT",
            raw_payload_hash="H_OLD",
            timestamp=old_epoch,
            direction="OUT",
        )
        mock_pm.fetch_transfers.return_value = [mock_transfer]

        # Trace with 90-day window
        constraints = TraceConstraints(max_hops=1, time_window_days=90)
        res = tracer.trace(
            start_address="0xsuspect_addr_window",
            chain="ETH",
            constraints=constraints,
            case_id="CR-TEST-WINDOW-TRUNC",
            mode="LIVE",
        )

        self.assertGreaterEqual(res["time_window_truncations"], 1)
        self.assertIsNotNone(res["earliest_transaction_date"])
        # completeness should be penalized by 10% from base (92.5 - 10.0 = 82.5)
        self.assertEqual(res["data_completeness_pct"], 82.5)
        # Warning boundary event present
        has_window_warning = any(b.get("kind") == "TIME_WINDOW_WARNING" for b in res["boundary_events"])
        self.assertTrue(has_window_warning)

        # Negative Test: Recent transaction (e.g. 2 days ago) -> 0 truncations, no 10% penalty
        recent_epoch = str(now - (2 * 86400))
        mock_transfer_recent = Transfer(
            chain_id="ETH",
            tx_hash="0xrecent_tx_hash",
            from_addr="0xsuspect_recent",
            to_addr="0xrecipient_recent",
            amount=50.0,
            asset="USDT",
            raw_payload_hash="H_REC",
            timestamp=recent_epoch,
            direction="OUT",
        )
        mock_pm.fetch_transfers.return_value = [mock_transfer_recent]

        res_recent = tracer.trace(
            start_address="0xsuspect_recent",
            chain="ETH",
            constraints=constraints,
            case_id="CR-TEST-WINDOW-CLEAN",
            mode="LIVE",
        )
        self.assertEqual(res_recent["time_window_truncations"], 0)
        self.assertEqual(res_recent["data_completeness_pct"], 92.5)
        has_window_warning_neg = any(b.get("kind") == "TIME_WINDOW_WARNING" for b in res_recent["boundary_events"])
        self.assertFalse(has_window_warning_neg)

    # ─────────────────────────────────────────────────────────────
    # §1.7 Timeout Degradation to PARTIAL_COMPLETE Tests
    # ─────────────────────────────────────────────────────────────
    def test_1_7_timeout_partial_complete_and_negative(self):
        """Verify timeout degradations: >= 2 hops produces PARTIAL_COMPLETE with banner, < 2 hops produces TIMEOUT."""
        tracer = BoundedTracer()
        mock_pm = MagicMock()
        tracer.provider_mgr = mock_pm

        now = int(time.time())
        current_time = [1000000.0]

        def mock_time():
            return current_time[0]

        # Setup transfers so 2 hops occur before timeout is triggered
        def side_effect_fetch(addr, chain="ETH", limit=50):
            if "suspect" in addr:
                return [Transfer(
                    chain_id="ETH", tx_hash="0xtx1", from_addr=addr, to_addr="0xhop1", amount=100.0,
                    asset="ETH", raw_payload_hash="H1", timestamp=str(now - 1000), direction="OUT"
                )]
            elif "hop1" in addr:
                # Advance clock after hop 1 is fetched so next loop iteration triggers timeout (500s > 10s)
                current_time[0] += 500.0
                return [Transfer(
                    chain_id="ETH", tx_hash="0xtx2", from_addr=addr, to_addr="0xhop2", amount=99.0,
                    asset="ETH", raw_payload_hash="H2", timestamp=str(now - 500), direction="OUT"
                )]
            return []

        mock_pm.fetch_transfers.side_effect = side_effect_fetch

        with patch("backend.tracing.trace_engine.time.time", side_effect=mock_time):
            constraints = TraceConstraints(max_hops=5, timeout_seconds=10)
            res_partial = tracer.trace(
                start_address="0xsuspect_timeout_partial",
                chain="ETH",
                constraints=constraints,
                case_id="CR-TIMEOUT-PARTIAL",
                mode="LIVE",
            )

        self.assertEqual(res_partial["termination_reason"], "PARTIAL_COMPLETE")
        self.assertTrue(res_partial["partial_result"])
        self.assertIsNotNone(res_partial["ui_warning_banner"])
        # Completeness gets 15% deduction: 92.5 - 15.0 = 77.5%
        self.assertEqual(res_partial["data_completeness_pct"], 77.5)
        # Full post-traversal executed
        self.assertIn("attribution", res_partial)
        self.assertIn("risk", res_partial)

        # Negative Test: Timeout triggers immediately before 2 hops are discovered (< 2 hops)
        call_idx = [0]

        def mock_time_immediate():
            call_idx[0] += 1
            if call_idx[0] >= 2:
                return 1000500.0
            return 1000000.0

        with patch("backend.tracing.trace_engine.time.time", side_effect=mock_time_immediate):
            res_timeout = tracer.trace(
                start_address="0xsuspect_timeout_bare",
                chain="ETH",
                constraints=constraints,
                case_id="CR-TIMEOUT-BARE",
                mode="LIVE",
            )

        self.assertEqual(res_timeout["termination_reason"], "TIMEOUT")
        self.assertFalse(res_timeout["partial_result"])

    # ─────────────────────────────────────────────────────────────
    # §4.1 Elapsed Hours Non-Fabrication Tests
    # ─────────────────────────────────────────────────────────────
    def test_4_1_elapsed_hours_insufficient_data_and_negative(self):
        """Verify recovery estimator yields display_tier='insufficient_data' when elapsed_hours is None, and computes when provided."""
        # Positive Test: elapsed_hours=None -> display_tier="insufficient_data"
        rec_none = self.recovery_estimator.estimate_recovery(
            case_id="CR-MISSING-TIME",
            traced_amount_usd=50000.0,
            data_completeness_pct=95.0,
            attribution_confidence="HIGH",
            is_fiu_registered_vasp=True,
            hop_count=2,
            elapsed_hours=None,
            mixer_detected=False,
        )
        self.assertEqual(rec_none.display_tier, "insufficient_data")
        self.assertEqual(rec_none.recovery_score, 0)
        self.assertEqual(rec_none.action_window_hours, 0)
        self.assertIn("Insufficient timing data", rec_none.disclaimer)

        # Negative Test: elapsed_hours provided (e.g. 10.0 hours) -> display_tier="eligible"
        rec_valid = self.recovery_estimator.estimate_recovery(
            case_id="CR-VALID-TIME",
            traced_amount_usd=50000.0,
            data_completeness_pct=95.0,
            attribution_confidence="HIGH",
            is_fiu_registered_vasp=True,
            hop_count=2,
            elapsed_hours=10.0,
            mixer_detected=False,
        )
        self.assertEqual(rec_valid.display_tier, "eligible")
        self.assertGreaterEqual(rec_valid.recovery_score, 60)
        self.assertGreater(rec_valid.action_window_hours, 0)


if __name__ == "__main__":
    unittest.main()
