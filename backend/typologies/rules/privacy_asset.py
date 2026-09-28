# backend/typologies/rules/privacy_asset.py
"""
CryptoTrace LEA - Privacy Asset / No-KYC Swap Exposure Rule
Flags fund exposure to Monero (XMR), Zcash (ZEC) swap services, privacy bridges,
or no-KYC swap gateways. Treats these endpoints as forensic boundary horizons
with full disclaimer that off-chain zero-knowledge ledgers cannot be unmasked.
"""

from typing import Dict, Any, Optional
from backend.models.domain_models import PatternFinding
from backend.typologies.mixer_registry import MIXER_REGISTRY

PRIVACY_ASSETS = {"XMR", "ZEC", "SCRT", "DASH"}

class PrivacyAssetRule:
    RULE_ID = "PRIVACY_ASSET_EXPOSURE"
    RULE_VERSION = "1.0"

    def evaluate(self, trace_result: Dict[str, Any], case_id: str) -> Optional[PatternFinding]:
        hops = trace_result.get("hops", [])
        for hop in hops:
            asset = (hop.get("asset") or "").upper()
            to_addr = (hop.get("to_address") or "").lower()

            is_privacy_coin = asset in PRIVACY_ASSETS
            mixer_entry = MIXER_REGISTRY.get(to_addr)
            is_swap_or_privacy = mixer_entry and mixer_entry.get("category") in {"PRIVACY_POOL", "NO_KYC_SWAP"}

            if is_privacy_coin or is_swap_or_privacy:
                target_name = mixer_entry["name"] if mixer_entry else f"Privacy Asset Corridor ({asset})"
                return PatternFinding(
                    finding_id=f"FIND-PRIVACY-{case_id[-8:]}",
                    case_id=case_id,
                    typology_name="PRIVACY_ASSET_EXPOSURE",
                    rule_version=self.RULE_VERSION,
                    confidence="LOW",
                    evidence_json={
                        "target_name": target_name,
                        "address": to_addr,
                        "asset": asset,
                        "category": mixer_entry.get("category", "PRIVACY_COIN") if mixer_entry else "PRIVACY_COIN",
                        "deposit_amount": hop.get("amount", 0.0),
                        "hop_number": hop.get("hop_number", 1),
                        "relationship_label": "Privacy Horizon ? Non-Attributable",
                    },
                    uncertainty_notes=(
                        "FORENSIC LIMITATION: Fund flow entered a privacy-preserving protocol or asset "
                        "(e.g., Monero/Zcash/FixedFloat). Mathematical zero-knowledge or stealth address "
                        "properties prevent onward ledger attribution without off-chain server seizure."
                    ),
                    data_completeness_pct=trace_result.get("data_completeness_pct", 70.0),
                    india_specific=False,
                )
        return None

privacy_asset_rule = PrivacyAssetRule()
