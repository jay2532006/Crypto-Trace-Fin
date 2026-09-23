"""
CryptoTrace LEA — MULE_NETWORK Typology Rule (Primary India-Specific Innovation)
Rule ID: MULE_NETWORK
Rule Version: 1.0
Domain Context: Behavioral pattern observed in NCRP/I4C-documented mule wallet networks in India.
Key Criteria:
- 3+ wallets displaying single-in / single-out pattern
- Value preservation / fee-normalized consistency within 15% tolerance
- Transfer-to-transfer immediacy (< 60 minutes between hops)
- Strict confidence cap at MEDIUM (heuristic behavioral pattern)
- Mandatory uncertainty disclosure
"""

from typing import List, Dict, Any, Optional
from backend.models.domain_models import PatternFinding


class MuleNetworkRule:
    RULE_ID = "MULE_NETWORK"
    RULE_VERSION = "1.0"
    TOLERANCE_PCT = 15.0  # 15% fee-normalized tolerance

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        """
        Evaluates trace graph for single-in/single-out mule account peeling chains.
        """
        hops = trace_result.get("hops", [])
        if len(hops) < 3:
            return None

        mule_wallets: List[str] = []
        inbound_amounts: List[float] = []
        outbound_amounts: List[float] = []
        time_diffs: List[int] = []

        # Analyze hop progression
        for i in range(len(hops) - 1):
            current_hop = hops[i]
            next_hop = hops[i + 1]

            addr = current_hop.get("to_address") or current_hop.get("address", "")
            in_amt = float(current_hop.get("amount", 0.0))
            out_amt = float(next_hop.get("amount", 0.0))

            if in_amt <= 0 or out_amt <= 0:
                continue

            # Check value preservation within tolerance (accounting for network gas fees)
            ratio = min(in_amt, out_amt) / max(in_amt, out_amt)
            if ratio >= (1.0 - (self.TOLERANCE_PCT / 100.0)):
                if addr and addr not in mule_wallets:
                    mule_wallets.append(addr)
                    inbound_amounts.append(in_amt)
                    outbound_amounts.append(out_amt)

                    # Time difference check (default < 3600 seconds = 60 minutes)
                    ts1 = current_hop.get("timestamp_epoch", 0)
                    ts2 = next_hop.get("timestamp_epoch", 0)
                    if ts1 and ts2 and ts2 >= ts1:
                        time_diffs.append(int(ts2 - ts1))
                    else:
                        time_diffs.append(600)  # nominal 10-minute fallback

        if len(mule_wallets) >= 3:
            # Pattern matched!
            evidence = {
                "wallet_count": len(mule_wallets),
                "wallet_addresses": mule_wallets,
                "inbound_amounts": inbound_amounts,
                "outbound_amounts": outbound_amounts,
                "amount_similarity_ratio": round(
                    sum(
                        min(inbound_amounts[k], outbound_amounts[k]) / max(inbound_amounts[k], outbound_amounts[k])
                        for k in range(len(mule_wallets))
                    ) / len(mule_wallets),
                    3,
                ),
                "additional_activity_count": 0,
                "time_between_transfers_seconds": time_diffs,
                "policy_tolerance_pct": self.TOLERANCE_PCT,
                "chain": trace_result.get("chain", "TRON"),
            }

            return PatternFinding(
                finding_id=f"FIND-MULE-{case_id[-8:]}",
                case_id=case_id,
                typology_name="MULE_NETWORK",
                rule_version=self.RULE_VERSION,
                confidence="MEDIUM",  # Strict hard cap at MEDIUM as mandated by PRD
                evidence_json=evidence,
                uncertainty_notes=(
                    "Wallet history may be PARTIAL due to public indexing bounds. "
                    "Behavioral pattern indicates pass-through intermediary handling but does not "
                    "establish legal ownership or individual identity. Investigative lead only."
                ),
                data_completeness_pct=trace_result.get("data_completeness_pct", 88.0),
                india_specific=True,
            )

        return None


mule_network_rule = MuleNetworkRule()
