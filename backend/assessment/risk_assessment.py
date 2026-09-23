"""
CryptoTrace LEA — Risk Assessor
Computes an independent AML/CFT risk score (0 to 100) and category (CRITICAL, HIGH, MEDIUM, LOW).
Risk and attribution are separate dimensions and must never be collapsed.
"""

from typing import Dict, Any, List
from backend.models.domain_models import RiskAssessment
from backend.models.confidence_types import RiskCategory


class RiskAssessor:
    def assess_risk(self, case_id: str, trace_result: Dict[str, Any]) -> RiskAssessment:
        """Calculates composite risk score based on typologies, mixers, and sanctions."""
        hops = trace_result.get("hops", [])
        typologies = trace_result.get("typologies", [])
        ofac_hit = trace_result.get("ofac_sanction_hit", False)

        components: Dict[str, int] = {
            "ofac_sanctions": 45 if ofac_hit else 0,
            "mixer_interaction": 30 if any(t == "MIXER_BOUNDARY" for t in typologies) else 0,
            "mule_network": 20 if any(t == "MULE_NETWORK" for t in typologies) else 0,
            "peel_chain": 15 if any(t == "PEEL_CHAIN" for t in typologies) else 0,
            "hop_velocity": 10 if len(hops) >= 4 else 5,
        }

        total_risk = min(100, sum(components.values()))

        if total_risk >= 75:
            cat: RiskCategory = "CRITICAL"
        elif total_risk >= 50:
            cat = "HIGH"
        elif total_risk >= 25:
            cat = "MEDIUM"
        else:
            cat = "LOW"

        return RiskAssessment(
            case_id=case_id,
            risk_score=total_risk,
            risk_category=cat,
            component_scores=components,
        )


risk_assessor = RiskAssessor()
