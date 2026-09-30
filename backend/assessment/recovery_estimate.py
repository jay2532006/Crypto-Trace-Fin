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


# §4.2: Fraud-type recovery difficulty calibration
FRAUD_TYPE_MODIFIERS: Dict[str, int] = {
    "INVESTMENT_SCAM": 0,
    "TASK_BASED_FRAUD": 5,      # Faster off-ramp observed
    "RANSOMWARE": -10,          # Negotiation delays recovery
    "SEXTORTION": -15,          # Victim reporting delay reduces window
    "DARKNET": -30,             # Near-zero recovery baseline
    "PHISHING": 0,
    "ORGANIZED_CRIME": -10,     # Multi-layered syndicate dissipation
}


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
        elapsed_hours: Optional[float] = None,
        mixer_detected: bool = False,
        fraud_type: Optional[str] = None,
    ) -> RecoveryAssessment:
        """
        Calculates the Heuristic Recovery Estimate score (0-100) and operational action window.
        §4.1: If elapsed_hours is None (no verified case date or hop timestamps),
        returns display_tier='insufficient_data' rather than fabricating urgency.
        """
        # ── Step 0: Check Temporal Verification (§4.1) ──
        if elapsed_hours is None:
            return RecoveryAssessment(
                case_id=case_id,
                recovery_score=0,
                action_window_hours=0,
                display_tier="insufficient_data",
                calculation_basis="Temporal evidence missing: case creation date and hop timestamps unavailable to evaluate action window.",
                disclaimer="Recovery estimate requires verified elapsed time to compute operational action window. Insufficient timing data.",
            )

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

        # e) §4.2 Fraud Type Modifier
        fraud_mod = 0
        if fraud_type:
            cleaned_ft = fraud_type.strip().upper().replace(" ", "_").replace("-", "_")
            fraud_mod = FRAUD_TYPE_MODIFIERS.get(cleaned_ft, 0)

        total_score = max(5, min(95, cooperation_score + time_score + path_score + attr_score + fraud_mod))

        basis = (
            f"Eligible Case: Traced ${traced_amount_usd:,.2f} USD ({hop_count} hops). "
            f"VASP Cooperation Factor: {cooperation_score}/35. "
            f"Time Urgency Factor: {time_score}/30 ({elapsed_hours:.1f}h elapsed). "
            f"Path Simplicity: {path_score}/25."
        )
        if fraud_type:
            basis += f" Fraud Type Modifier: {fraud_type} ({fraud_mod:+d} pts)."

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
