"""
CryptoTrace LEA — MIXER_BOUNDARY Typology Rule
Rule ID: MIXER_BOUNDARY
Enforces exact PRD parameters:
- Same mixer pool search window: +14,400 seconds (4 hours)
- Payout ratio: 0.90 to 0.995
- Immutable confidence: 0.25 (LEAD band)
- Explicit heuristic uncertainty: "Possible Exit — Heuristic Only"
"""

from typing import Dict, Any, Optional
from backend.models.domain_models import PatternFinding

from backend.typologies.mixer_registry import KNOWN_MIXERS, get_mixer_info


class MixerBoundaryRule:
    RULE_ID = "MIXER_BOUNDARY"
    RULE_VERSION = "1.0"
    WINDOW_SECONDS = 14400  # 4 hours
    MIN_PAYOUT_RATIO = 0.90
    MAX_PAYOUT_RATIO = 0.995

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        hops = trace_result.get("hops", [])
        for hop in hops:
            to_addr = (hop.get("to_address") or "").lower()
            if to_addr in KNOWN_MIXERS:
                mixer_name = KNOWN_MIXERS[to_addr]
                evidence = {
                    "mixer_name": mixer_name,
                    "mixer_address": to_addr,
                    "deposit_amount": hop.get("amount", 0.0),
                    "search_window_seconds": self.WINDOW_SECONDS,
                    "payout_ratio_band": f"{self.MIN_PAYOUT_RATIO} - {self.MAX_PAYOUT_RATIO}",
                    "confidence_score": 0.25,
                    "confidence_band": "LEAD",
                    "relationship_label": "Possible Exit — Heuristic Only",
                }

                return PatternFinding(
                    finding_id=f"FIND-MIXER-{case_id[-8:]}",
                    case_id=case_id,
                    typology_name="MIXER_BOUNDARY",
                    rule_version=self.RULE_VERSION,
                    confidence="LOW",  # 0.25 Lead Band mapped to LOW
                    evidence_json=evidence,
                    uncertainty_notes=(
                        "CRITICAL UNCERTAINTY: Cryptographic de-anonymization of mixer pools is mathematically impossible. "
                        "Correlation is based solely on time/value heuristic window (+14,400s). "
                        "Must NOT be treated as confirmed ownership or definitive fund exit."
                    ),
                    data_completeness_pct=trace_result.get("data_completeness_pct", 75.0),
                    india_specific=False,
                )
        return None


mixer_boundary_rule = MixerBoundaryRule()
