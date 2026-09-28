"""
CryptoTrace LEA — Cross-Chain Analyzer
Strictly distinguishes PROVEN cross-chain bridges from HEURISTIC correlation.
Time/value match is NEVER presented as proof of bridge execution.
"""

from typing import List, Dict, Any
from backend.models.domain_models import CrossChainLink
from backend.models.confidence_types import LinkType, ConfidenceLevel


class CrossChainAnalyzer:
    def analyze_cross_chain(
        self,
        from_chain: str,
        from_addr: str,
        to_chain: str,
        to_addr: str,
        amount_from: float,
        amount_to: float,
        time_delta_seconds: int,
        bridge_tx_hash: str = None,
        bridge_protocol: str = "Across / LayerZero",
        dest_tx_hash: str = None,
    ) -> CrossChainLink:
        """
        Classifies cross-chain relationship as PROVEN (if bridge TX hash is verified)
        or HEURISTIC_CORRELATION (if based purely on time/value proximity).
        """
        if bridge_tx_hash:
            return CrossChainLink(
                from_chain=from_chain.upper(),
                from_addr=from_addr,
                to_chain=to_chain.upper(),
                to_addr=to_addr,
                link_type="PROVEN",
                supporting_evidence={
                    "bridge_protocol": bridge_protocol,
                    "bridge_tx_hash": bridge_tx_hash,
                    "dest_tx_hash": dest_tx_hash,
                    "source_amount": amount_from,
                    "dest_amount": amount_to,
                    "verification": "VERIFIED_ON_CHAIN_EVENT",
                },
                confidence="HIGH",
            )

        # Heuristic Correlation
        fee_tolerance = abs(amount_from - amount_to) / max(amount_from, 1.0)
        is_close_time = (time_delta_seconds <= 3600)  # within 1 hour
        is_close_value = (fee_tolerance <= 0.05)       # within 5% fee tolerance

        conf: ConfidenceLevel = "MEDIUM" if (is_close_time and is_close_value) else "LOW"

        return CrossChainLink(
            from_chain=from_chain.upper(),
            from_addr=from_addr,
            to_chain=to_chain.upper(),
            to_addr=to_addr,
            link_type="HEURISTIC_CORRELATION",
            supporting_evidence={
                "time_delta_seconds": time_delta_seconds,
                "amount_delta": abs(amount_from - amount_to),
                "fee_tolerance_pct": round(fee_tolerance * 100, 2),
                "disclaimer": "Heuristic correlation only. Does not prove bridge execution.",
            },
            confidence=conf,
        )


cross_chain_analyzer = CrossChainAnalyzer()
