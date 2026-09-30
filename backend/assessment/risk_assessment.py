"""
CryptoTrace LEA — Risk Assessor
Computes an independent AML/CFT risk score (0 to 100) and category (CRITICAL, HIGH, MEDIUM, LOW).
Risk and attribution are separate dimensions and must never be collapsed.
"""

from typing import Dict, Any, List
from backend.models.domain_models import RiskAssessment
from backend.models.confidence_types import RiskCategory


class RiskAssessor:
    @staticmethod
    def amount_component(amount_usd: float) -> int:
        """§3.1: Fraud amount risk component based on INR tiers."""
        if amount_usd >= 1_200_000:  # > ₹10 crore
            return 35
        if amount_usd >= 120_000:    # > ₹1 crore
            return 25
        if amount_usd >= 12_000:     # > ₹10 lakh
            return 15
        return 0

    def assess_risk(self, case_id: str, trace_result: Dict[str, Any]) -> RiskAssessment:
        """
        Calculates composite risk score based on:
        - §3.1: Fraud amount component
        - §3.2: Cross-chain layering penalty
        - §3.3: Offshore/unregistered VASP jurisdiction penalty
        - §3.4: Cross-rule compounding bonuses and category overrides
        - Typologies, mixers, and OFAC sanctions
        """
        hops = trace_result.get("hops", [])
        typologies = trace_result.get("typologies", [])
        ofac_hit = trace_result.get("ofac_sanction_hit", False)

        # §3.1: Fraud amount component
        amount_usd = float(hops[0].get("amount", 0.0) if hops else trace_result.get("reported_amount", 0.0) or 0.0)
        fraud_amt = self.amount_component(amount_usd)

        # §3.2: Cross-chain layering penalty
        cross_chain_links = trace_result.get("cross_chain_links", [])
        n_bridges = len(cross_chain_links)
        cross_chain_score = 20 if n_bridges >= 2 else (10 if n_bridges == 1 else 0)
        if n_bridges > 0 and any(t == "MIXER_BOUNDARY" for t in typologies):
            cross_chain_score += 10  # bridge + mixer compound

        # §3.3: Offshore/unregistered VASP jurisdiction penalty
        attribution = trace_result.get("attribution", {}) or {}
        fiu_status = attribution.get("fiu_status")
        jurisdiction = (attribution.get("jurisdiction") or "").upper()
        offshore_penalty = 15 if (fiu_status == "UNREGISTERED" and jurisdiction != "INDIA") else 0

        # §3.4: Cross-rule compounding bonuses
        has_mule = any(t == "MULE_NETWORK" for t in typologies)
        has_rapid = any(t == "RAPID_HOP" for t in typologies)
        has_mixer = any(t == "MIXER_BOUNDARY" for t in typologies)
        compound_mule_rapid = 15 if (has_mule and has_rapid) else 0
        compound_mule_mixer = 10 if (has_mule and has_mixer) else 0

        components: Dict[str, int] = {
            "ofac_sanctions": 45 if ofac_hit else 0,
            "mixer_interaction": 30 if has_mixer else 0,
            "mule_network": 20 if has_mule else 0,
            "peel_chain": 15 if any(t == "PEEL_CHAIN" for t in typologies) else 0,
            "consolidation_funnel": 15 if any(t == "CONSOLIDATION_FUNNEL" for t in typologies) else 0,
            "hop_velocity": 10 if len(hops) >= 4 else 5,
            "fraud_amount": fraud_amt,
            "cross_chain_layering": cross_chain_score,
            "offshore_vasp_penalty": offshore_penalty,
            "compound_mule_rapid": compound_mule_rapid,
            "compound_mule_mixer": compound_mule_mixer,
        }

        total_risk = min(100, sum(components.values()))

        # §3.4: Category Override Rules
        if ofac_hit and len(typologies) > 0:
            cat: RiskCategory = "CRITICAL"
            total_risk = max(total_risk, 85)
        elif has_mule and has_mixer:
            cat = "CRITICAL"
            total_risk = max(total_risk, 75)
        elif total_risk >= 75:
            cat = "CRITICAL"
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
