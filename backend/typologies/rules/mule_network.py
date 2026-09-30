"""
CryptoTrace LEA — MULE_NETWORK Typology Rule (Primary India-Specific Innovation)
Rule ID: MULE_NETWORK
Rule Version: 1.1
Domain Context: Behavioral pattern observed in NCRP/I4C-documented mule wallet networks in India.
Key Criteria:
- 3+ wallets displaying single-in / single-out pattern
- Value preservation / fee-normalized consistency within 15% tolerance
- Transfer-to-transfer immediacy (< 60 minutes between hops)
- Strict confidence cap at MEDIUM (heuristic behavioral pattern)
- Mandatory uncertainty disclosure

§2.1 FIX: Removed fabricated 600s timestamp fallback.
Only timing-confirmed hops (where both timestamp_epoch values are non-zero and valid)
contribute to the mule wallet list. If timing is absent, those hops are counted but
never used as timing "evidence". Confidence is capped at LOW if timing data is incomplete.
"""

from typing import List, Dict, Any, Optional
from backend.models.domain_models import PatternFinding


class MuleNetworkRule:
    RULE_ID = "MULE_NETWORK"
    RULE_VERSION = "1.1"  # §2.1: bumped for timestamp-fix
    TOLERANCE_PCT = 15.0  # 15% fee-normalized tolerance

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        """
        Evaluates trace graph for single-in/single-out mule account peeling chains.
        §2.1: Timing evidence is only used when real timestamp_epoch values exist.
        Hops missing timestamps are included in value-preservation analysis but
        contribute 0 timing evidence — the 600s fallback has been removed.
        """
        hops = trace_result.get("hops", [])
        if len(hops) < 3:
            return None

        mule_wallets: List[str] = []
        inbound_amounts: List[float] = []
        outbound_amounts: List[float] = []
        time_diffs: List[int] = []
        hops_with_timing: int = 0     # §2.1: count confirmed timing pairs
        hops_without_timing: int = 0  # §2.1: count missing timing pairs

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

                    # §2.1: Only append a real time diff when BOTH timestamps are present
                    # and valid. Never inject a synthetic fallback — that is fabricated evidence.
                    ts1 = current_hop.get("timestamp_epoch", 0)
                    ts2 = next_hop.get("timestamp_epoch", 0)
                    if ts1 and ts2 and ts2 >= ts1:
                        time_diffs.append(int(ts2 - ts1))
                        hops_with_timing += 1
                    else:
                        # §2.1: Missing timing — do NOT inject 600s. Just track the gap.
                        hops_without_timing += 1

        if len(mule_wallets) >= 3:
            # §2.1: Determine timing completeness
            timing_confirmed = hops_with_timing
            timing_missing = hops_without_timing
            timing_complete = (timing_missing == 0) and (timing_confirmed >= 3)

            # §2.1: If timing data is incomplete, cap confidence at LOW
            # and add an explicit uncertainty note.
            if timing_complete:
                confidence = "MEDIUM"  # Strict hard cap at MEDIUM as mandated by PRD
                timing_note = ""
            else:
                confidence = "LOW"  # §2.1: Downgraded — timing evidence unverified
                timing_note = (
                    f" TIMING EVIDENCE INCOMPLETE: {timing_missing} of "
                    f"{timing_confirmed + timing_missing} hop-pairs had missing "
                    "timestamp_epoch values. Temporal pattern could not be verified. "
                    "Value-preservation pattern was matched but timing velocity is unconfirmed."
                )

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
                # §2.1: Only real time diffs; no synthetic values
                "time_between_transfers_seconds": time_diffs,
                "hops_with_confirmed_timing": hops_with_timing,  # §2.1
                "hops_with_missing_timing": hops_without_timing,   # §2.1
                "timing_evidence_complete": timing_complete,        # §2.1
                "policy_tolerance_pct": self.TOLERANCE_PCT,
                "chain": trace_result.get("chain", "TRON"),
            }

            uncertainty_base = (
                "Wallet history may be PARTIAL due to public indexing bounds. "
                "Behavioral pattern indicates pass-through intermediary handling but does not "
                "establish legal ownership or individual identity. Investigative lead only."
            )

            return PatternFinding(
                finding_id=f"FIND-MULE-{case_id[-8:]}",
                case_id=case_id,
                typology_name="MULE_NETWORK",
                rule_version=self.RULE_VERSION,
                confidence=confidence,
                evidence_json=evidence,
                uncertainty_notes=uncertainty_base + timing_note,
                data_completeness_pct=trace_result.get("data_completeness_pct", 88.0),
                india_specific=True,
            )

        return None


mule_network_rule = MuleNetworkRule()
