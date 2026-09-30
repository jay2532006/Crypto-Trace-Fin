"""
CryptoTrace LEA — Typology Engine
Orchestrates detection of explainable forensic typologies across all registered rules.
"""

from typing import List, Dict, Any
from backend.models.domain_models import PatternFinding
from .rules.mule_network import mule_network_rule
from .rules.mixer_boundary import mixer_boundary_rule
from .rules.other_rules import peel_chain_rule, rapid_hop_rule, consolidation_funnel_rule
from .rules.privacy_asset import privacy_asset_rule


class TypologyEngine:
    def __init__(self):
        self.rules = [
            mule_network_rule,
            mixer_boundary_rule,
            peel_chain_rule,
            rapid_hop_rule,
            consolidation_funnel_rule,
            privacy_asset_rule,
        ]

    def detect_typologies(self, trace_result: Dict[str, Any], case_id: str) -> List[PatternFinding]:
        """Runs all versioned typology rules and returns validated pattern findings."""
        findings: List[PatternFinding] = []
        for rule in self.rules:
            try:
                finding = rule.evaluate(trace_result, case_id)
                if finding:
                    findings.append(finding)
            except Exception:
                continue
        return findings


typology_engine = TypologyEngine()
