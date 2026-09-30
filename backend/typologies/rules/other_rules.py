"""
CryptoTrace LEA — Core Typology Rules (Peel Chain, Fan In, Fan Out, Rapid Hop, Bridge)
"""

from typing import Dict, Any, Optional, List
from backend.models.domain_models import PatternFinding


class PeelChainRule:
    RULE_ID = "PEEL_CHAIN"
    RULE_VERSION = "1.1"  # §2.3: Corrected implementation

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        """
        §2.3 CORRECTED PEEL CHAIN DEFINITION:
        Successive value reduction of 0.5–5% per hop (fee/peel pattern),
        minimum 3 hops, each hop to a UNIQUE address.

        Previous implementation used a single 85% check across all hops which
        incorrectly fired on large single drops (e.g. mixer fee). This is the
        correct per-hop range: [0.5%, 5%] per hop — small, consistent shaving.
        """
        hops = trace_result.get("hops", [])
        if len(hops) < 3:
            return None

        amounts = [float(h.get("amount", 0)) for h in hops]
        addresses = [h.get("to_address", "").lower() for h in hops]

        # All amounts must be positive
        if not all(a > 0 for a in amounts):
            return None

        # Each hop must be to a UNIQUE address (distinguishes peel from simple pass-through)
        if len(set(addresses)) < len(addresses):
            return None  # address reuse detected — not a peel chain

        # §2.3: Correct peel definition: each consecutive hop reduces amount by 0.5–5%
        per_hop_ratios: List[float] = []
        for i in range(len(amounts) - 1):
            if amounts[i] <= 0:
                return None
            ratio = (amounts[i] - amounts[i + 1]) / amounts[i]  # positive = reduction
            per_hop_ratios.append(ratio)

        # All hops must show a reduction in the 0.5%–5% band
        if not all(0.005 <= r <= 0.05 for r in per_hop_ratios):
            return None

        return PatternFinding(
            finding_id=f"FIND-PEEL-{case_id[-8:]}",
            case_id=case_id,
            typology_name="PEEL_CHAIN",
            rule_version=self.RULE_VERSION,
            confidence="HIGH" if len(amounts) >= 4 else "MEDIUM",
            evidence_json={
                "hop_count": len(amounts),
                "initial_amount": amounts[0],
                "final_amount": amounts[-1],
                "peel_decay_ratio": round(amounts[-1] / amounts[0], 3),
                "per_hop_reduction_pcts": [round(r * 100, 2) for r in per_hop_ratios],
                "unique_addresses": len(set(addresses)) == len(addresses),
            },
            uncertainty_notes=(
                "Successive 0.5–5% per-hop deductions to unique addresses; consistent with "
                "automated peel wallet laundering. Minimum 3-hop pattern confirmed."
            ),
            data_completeness_pct=trace_result.get("data_completeness_pct", 90.0),
            india_specific=False,
        )


RAPID_HOP_THRESHOLDS: Dict[str, int] = {
    "ETH": 10800,      # 3 hours (10,800s)
    "TRON": 3600,      # 1 hour (3,600s)
    "BTC": 86400,      # 24 hours (86,400s)
    "POLYGON": 1800,   # 30 minutes (1,800s)
    "BSC": 3600,       # 1 hour (3,600s)
}


class RapidHopRule:
    RULE_ID = "RAPID_HOP"
    RULE_VERSION = "1.1"  # §2.2: Chain-specific thresholds

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        hops = trace_result.get("hops", [])
        if len(hops) >= 3:
            chain = (trace_result.get("chain") or "ETH").upper()
            threshold = RAPID_HOP_THRESHOLDS.get(chain, 10800)
            # Check rapid time succession per chain velocity benchmark
            timestamps = [h.get("timestamp_epoch", 0) for h in hops if h.get("timestamp_epoch", 0) > 0]
            if len(timestamps) >= 3:
                time_span = max(timestamps) - min(timestamps)
                if time_span > 0 and time_span <= threshold:
                    return PatternFinding(
                        finding_id=f"FIND-RAPID-{case_id[-8:]}",
                        case_id=case_id,
                        typology_name="RAPID_HOP",
                        rule_version=self.RULE_VERSION,
                        confidence="MEDIUM",
                        evidence_json={
                            "total_time_span_seconds": time_span,
                            "threshold_seconds": threshold,
                            "chain": chain,
                            "hop_velocity": round(len(hops) / (time_span / 3600), 2) if time_span > 0 else 0.0,
                            "hops_in_window": len(hops),
                        },
                        uncertainty_notes=f"High-velocity fund dispersion through intermediary addresses within {chain} compressed time window ({threshold}s).",
                        data_completeness_pct=trace_result.get("data_completeness_pct", 85.0),
                        india_specific=False,
                    )
        return None


peel_chain_rule = PeelChainRule()
rapid_hop_rule = RapidHopRule()


class ConsolidationFunnelRule:
    RULE_ID = "CONSOLIDATION_FUNNEL"
    RULE_VERSION = "1.0"  # §2.4: 2+ independent branches merging before VASP

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        """
        §2.4: Fires when convergence tracking detects 2+ independent branches
        merging into one intermediary collection address before a VASP deposit.
        """
        edges = trace_result.get("edges", [])
        if len(edges) < 2:
            return None

        # Track distinct source addresses sending to each destination address
        in_sources: Dict[str, set] = {}
        for e in edges:
            from_addr = (e.get("from") or "").strip().lower()
            to_addr = (e.get("to") or "").strip().lower()
            if from_addr and to_addr and from_addr != to_addr:
                in_sources.setdefault(to_addr, set()).add(from_addr)

        # Check for convergence: any destination receiving funds from >= 2 distinct sources
        convergent = {to_a: srcs for to_a, srcs in in_sources.items() if len(srcs) >= 2}
        if convergent:
            conv_addr, sources = next(iter(convergent.items()))
            return PatternFinding(
                finding_id=f"FIND-CONV-{case_id[-8:] if len(case_id) >= 8 else case_id}",
                case_id=case_id,
                typology_name="CONSOLIDATION_FUNNEL",
                confidence="HIGH" if len(sources) >= 3 else "MEDIUM",
                evidence_json={
                    "convergence_address": conv_addr,
                    "inbound_branch_count": len(sources),
                    "source_addresses": list(sources)[:10],
                },
                uncertainty_notes=(
                    f"Consolidation funnel detected: {len(sources)} independent incoming branches "
                    f"merge into collection address {conv_addr[:10]}... prior to onward movement."
                ),
                data_completeness_pct=trace_result.get("data_completeness_pct", 90.0),
                india_specific=False,
            )
        return None


consolidation_funnel_rule = ConsolidationFunnelRule()
