"""
CryptoTrace LEA — RecoveryProbabilityScore / Heuristic Recovery Estimate (Primary Victim-Impact Innovation)
Translates forensic tracing results into actionable victim-impact language.
Primary UI Label: 'Heuristic Recovery Estimate' (Never presented as a mathematical probability).

Boundary Eligibility Conditions:
1. Traced value >= threshold (INR 10,000 / $120 USD)
2. Data completeness >= 70%
3. Attribution confidence >= MEDIUM
If conditions are not met, surfaces explicit 'ineligible' state with reasons.
"""

from typing import Dict, Any, Optional
from backend.models.domain_models import RecoveryAssessment
from backend.models.confidence_types import DisplayTier


class RecoveryEstimator:
    MIN_VALUE_USD = 120.0  # Approx ₹10,000 INR threshold
    MIN_COMPLETENESS_PCT = 70.0

    def estimate_recovery(
        self,
        case_id: str,
        traced_amount_usd: float,
        data_completeness_pct: float,
        attribution_confidence: str,  # LOW, MEDIUM, HIGH
        is_fiu_registered_vasp: bool,
        hop_count: int,
        elapsed_hours: float = 12.0,
        mixer_detected: bool = False,
    ) -> RecoveryAssessment:
        """
        Calculates the Heuristic Recovery Estimate score (0-100) and operational action window.
        """
        # ── Step 1: Check PRD FR-016 Eligibility Boundary Conditions ──
        ineligibility_reasons = []
        if hop_count <= 0:
            ineligibility_reasons.append(
                "Zero-hop trace is invalid for recovery scoring per PRD FR-016."
            )
        if traced_amount_usd <= 0:
            ineligibility_reasons.append(
                "Missing or zero fraud amount resulted in insufficient-data state per PRD FR-016."
            )
        elif traced_amount_usd < self.MIN_VALUE_USD:
            ineligibility_reasons.append(
                f"Traced value (${traced_amount_usd:,.2f}) is below minimum actionable threshold (${self.MIN_VALUE_USD:.0f})."
            )
        if data_completeness_pct < self.MIN_COMPLETENESS_PCT:
            ineligibility_reasons.append(
                f"Data completeness ({data_completeness_pct:.1f}%) is below reliable threshold ({self.MIN_COMPLETENESS_PCT}%)."
            )
        if attribution_confidence.upper() in ["LEAD", "NONE", "LOW"] or mixer_detected:
            ineligibility_reasons.append(
                f"Attribution candidate with '{attribution_confidence}' confidence or mixer interaction is invalid for recovery scoring per PRD FR-016."
            )

        if ineligibility_reasons:
            return RecoveryAssessment(
                case_id=case_id,
                recovery_score=0,
                action_window_hours=0,
                display_tier="ineligible",
                calculation_basis="; ".join(ineligibility_reasons),
                disclaimer=(
                    "Heuristic Recovery Estimate is INELIGIBLE for this case due to incomplete data, "
                    "low attribution confidence, or mixer boundary obstruction."
                ),
            )

        # ── Step 2: Compute Heuristic Urgency Score (Eligible Cases) ──
        # Factors:
        # a) Exchange Cooperation: FIU-registered Indian exchange = +35, Global registered = +20, Offshore = +5
        cooperation_score = 35 if is_fiu_registered_vasp else 20

        # b) Elapsed Time Decay: < 24h = +30, 24-48h = +15, > 48h = +5
        if elapsed_hours <= 24:
            time_score = 30
            action_window = max(6, int(36 - elapsed_hours))
        elif elapsed_hours <= 48:
            time_score = 15
            action_window = max(4, int(48 - elapsed_hours))
        else:
            time_score = 5
            action_window = 12

        # c) Path Simplicity: 1 hop = +25, 2-3 hops = +15, 4+ hops = +5
        if hop_count <= 1:
            path_score = 25
        elif hop_count <= 3:
            path_score = 15
        else:
            path_score = 5

        # d) Attribution Band: HIGH = +10, MEDIUM = +5
        attr_score = 10 if attribution_confidence.upper() == "HIGH" else 5

        total_score = min(95, cooperation_score + time_score + path_score + attr_score)

        basis = (
            f"Eligible Case: Traced ${traced_amount_usd:,.2f} USD ({hop_count} hops). "
            f"VASP Cooperation Factor: {cooperation_score}/35. "
            f"Time Urgency Factor: {time_score}/30 ({elapsed_hours:.1f}h elapsed). "
            f"Path Simplicity: {path_score}/25."
        )

        return RecoveryAssessment(
            case_id=case_id,
            recovery_score=total_score,
            action_window_hours=action_window,
            display_tier="eligible",
            calculation_basis=basis,
            disclaimer=(
                "Heuristic Recovery Estimate is an operational urgency indicator based on path complexity, "
                "elapsed time, and exchange cooperation. It is not a statistical probability or legal guarantee."
            ),
        )


recovery_estimator = RecoveryEstimator()
