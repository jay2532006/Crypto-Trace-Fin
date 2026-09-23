"""
CryptoTrace LEA — Core Typology Rules (Peel Chain, Fan In, Fan Out, Rapid Hop, Bridge)
"""

from typing import Dict, Any, Optional
from backend.models.domain_models import PatternFinding


class PeelChainRule:
    RULE_ID = "PEEL_CHAIN"
    RULE_VERSION = "1.0"

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        hops = trace_result.get("hops", [])
        if len(hops) >= 3:
            # Check for decreasing amounts across successive hops
            amounts = [float(h.get("amount", 0)) for h in hops if float(h.get("amount", 0)) > 0]
            if len(amounts) >= 3 and all(amounts[i] >= amounts[i+1] * 0.85 for i in range(len(amounts)-1)):
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
                    },
                    uncertainty_notes="Successive fractional deductions observed; consistent with automated peel wallet laundering.",
                    data_completeness_pct=trace_result.get("data_completeness_pct", 90.0),
                    india_specific=False,
                )
        return None


class RapidHopRule:
    RULE_ID = "RAPID_HOP"
    RULE_VERSION = "1.0"

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        hops = trace_result.get("hops", [])
        if len(hops) >= 3:
            # Check rapid time succession (all hops within 3 hours)
            timestamps = [h.get("timestamp_epoch", 0) for h in hops if h.get("timestamp_epoch", 0) > 0]
            if len(timestamps) >= 3:
                time_span = max(timestamps) - min(timestamps)
                if time_span > 0 and time_span <= 10800:  # <= 3 hours
                    return PatternFinding(
                        finding_id=f"FIND-RAPID-{case_id[-8:]}",
                        case_id=case_id,
                        typology_name="RAPID_HOP",
                        rule_version=self.RULE_VERSION,
                        confidence="MEDIUM",
                        evidence_json={
                            "total_time_span_seconds": time_span,
                            "hop_velocity": round(len(hops) / (time_span / 3600), 2),
                            "hops_in_window": len(hops),
                        },
                        uncertainty_notes="High-velocity fund dispersion through intermediary addresses within compressed time window.",
                        data_completeness_pct=trace_result.get("data_completeness_pct", 85.0),
                        india_specific=False,
                    )
        return None


peel_chain_rule = PeelChainRule()
rapid_hop_rule = RapidHopRule()
