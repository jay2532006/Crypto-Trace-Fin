# backend/legal/mixer_recommendation.py
"""
CryptoTrace LEA - Partial Investigative Recommendation Generator
Produces actionable law enforcement guidance when a trace hits a cryptographic
mixer or privacy pool boundary (e.g. Tornado Cash).
Emphasizes pre-mixer preservation, deposit evidence collection, off-chain subpoenas,
and strict labeling of heuristic exit leads.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class CandidateExit(BaseModel):
    tx_hash: str
    recipient: str
    amount: float
    asset: str
    time_delta_seconds: int
    relationship_label: str = "Possible Exit ? Heuristic Only"
    confidence: float = 0.25
    disclaimer: str = (
        "HEURISTIC LEAD ONLY: Output correlations from privacy pools share pool liquidity "
        "and cannot definitively be attributed to the subject depositor."
    )

class PartialRecommendation(BaseModel):
    boundary_type: str
    mixer_name: str
    mixer_address: str
    deposit_tx_hash: Optional[str] = None
    deposit_amount: float
    asset: str
    pre_mixer_freeze_targets: List[str]
    evidentiary_summary: str
    payout_candidates: List[CandidateExit] = []
    off_chain_actions: List[str]
    disclaimer: str

class MixerRecommendationEngine:
    def generate(
        self,
        trace_result: Dict[str, Any],
        boundary_event: Dict[str, Any],
    ) -> PartialRecommendation:
        hops = trace_result.get("hops", [])
        mixer_addr = boundary_event.get("address", "").lower()
        mixer_name = boundary_event.get("name", "Unknown Privacy Mixer")
        deposit_amt = boundary_event.get("deposit_amount", 0.0)
        asset = boundary_event.get("asset", "ETH")

        # 1. Identify pre-mixer addresses (hops leading up to the mixer)
        pre_mixer_addrs = set()
        dep_tx = None
        for h in hops:
            if (h.get("to_address") or "").lower() == mixer_addr:
                pre_mixer_addrs.add(h.get("from_address"))
                dep_tx = h.get("tx_hash")
            else:
                pre_mixer_addrs.add(h.get("from_address"))
                pre_mixer_addrs.add(h.get("to_address"))
        # Exclude the mixer itself from freeze targets
        pre_mixer_targets = [a for a in pre_mixer_addrs if a and a.lower() != mixer_addr]

        # 2. Simulated/heuristic exit candidates within +14,400s window (0.90 - 0.995 ratio)
        candidates: List[CandidateExit] = []
        if deposit_amt > 0:
            est_payout = round(deposit_amt * 0.98, 4)
            candidates.append(
                CandidateExit(
                    tx_hash="0xheuristic_exit_candidate_tx_lead_only",
                    recipient="0xpossible_exit_lead_unverified",
                    amount=est_payout,
                    asset=asset,
                    time_delta_seconds=3600,
                    relationship_label="Possible Exit ? Heuristic Only",
                    confidence=0.25,
                )
            )

        # 3. Formulate off-chain actionable investigative leads
        off_chain_leads = [
            f"Issue BNSS Section 91 notice to upstream funding VASP / RPC provider for IP, User-Agent, and session telemetry on deposit tx {dep_tx or 'N/A'}.",
            f"Lodge urgent freeze orders on verified pre-mixer intermediate wallets ({', '.join(pre_mixer_targets[:3]) if pre_mixer_targets else 'originating address'}).",
            "Subpoena relayer transaction gas sponsors / fee-paying wallets for KYC identity matches.",
            "Index recipient exchange off-ramps against victim communications and known extortion syndicate chat logs."
        ]

        summary = (
            f"Onward tracing halted at {mixer_name} ({mixer_addr}) due to cryptographic zero-knowledge pool obfuscation. "
            f"Investigative focus shifts from unprovable onward tracing to urgent pre-mixer fund freezing and "
            f"deposit-corridor off-chain telemetry preservation."
        )

        disclaimer = (
            "LEGAL ADMISSIBILITY NOTICE: Post-mixer linkages are mathematically non-attributable on public ledgers. "
            "Any exit candidates listed herein are preliminary leads for intelligence gathering and must not be submitted "
            "in judicial proceedings as conclusive proof of ownership."
        )

        return PartialRecommendation(
            boundary_type=boundary_event.get("kind", "MIXER"),
            mixer_name=mixer_name,
            mixer_address=mixer_addr,
            deposit_tx_hash=dep_tx,
            deposit_amount=deposit_amt,
            asset=asset,
            pre_mixer_freeze_targets=pre_mixer_targets,
            evidentiary_summary=summary,
            payout_candidates=candidates,
            off_chain_actions=off_chain_leads,
            disclaimer=disclaimer,
        )

mixer_recommendation_engine = MixerRecommendationEngine()
