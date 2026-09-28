# backend/attribution/attribution_resolver.py
"""
CryptoTrace LEA - Attribution Resolver
Resolves terminal/deposit nodes against VASP_REGISTRY hot_wallet_patterns dynamically.
Handles single match, zero matches (UNRESOLVED, never default to WAZIRX),
and ambiguous multi-matches (e.g. 0x28c6c062... shared across WAZIRX/BINANCE).
"""

from typing import Dict, Any, List, Optional, Set
from pydantic import BaseModel
from .vasp_registry import VASP_REGISTRY

class ResolvedAttribution(BaseModel):
    vasp_key: Optional[str] = None
    label_type: str = "UNRESOLVED"
    exact: bool = False
    candidates: List[str] = []
    is_ambiguous: bool = False
    confidence_cap: Optional[str] = None
    matched_address: Optional[str] = None

class AttributionResolver:
    def __init__(self, registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.registry = registry or VASP_REGISTRY

    def resolve(self, trace_result: Dict[str, Any]) -> ResolvedAttribution:
        hops = trace_result.get("hops", [])
        nodes = trace_result.get("nodes", [])

        # Identify terminal destination addresses (to_address that is not a from_address)
        from_addrs = {h.get("from_address", "").lower() for h in hops}
        to_addrs = [h.get("to_address", "").lower() for h in hops if h.get("to_address")]

        terminal_addrs = [addr for addr in to_addrs if addr not in from_addrs]
        candidate_addrs = terminal_addrs if terminal_addrs else to_addrs

        if not candidate_addrs and nodes:
            # Fall back to leaf nodes (depth > 0)
            candidate_addrs = [n.get("id", "").lower() for n in nodes if n.get("depth", 0) > 0]

        matched_vasps: Set[str] = set()
        matched_addr: Optional[str] = None

        for addr in candidate_addrs:
            if not addr:
                continue
            for vasp_key, vasp_data in self.registry.items():
                patterns = [p.lower() for p in vasp_data.get("hot_wallet_patterns", [])]
                for p in patterns:
                    if p.endswith("..."):
                        prefix = p[:-3]
                        if addr.startswith(prefix):
                            matched_vasps.add(vasp_key)
                            matched_addr = addr
                    elif addr == p:
                        matched_vasps.add(vasp_key)
                        matched_addr = addr

        if not matched_vasps:
            return ResolvedAttribution(
                vasp_key=None,
                label_type="UNRESOLVED",
                exact=False,
                candidates=[],
                is_ambiguous=False,
                confidence_cap=None,
                matched_address=None
            )

        candidates = sorted(list(matched_vasps))
        if len(candidates) == 1:
            return ResolvedAttribution(
                vasp_key=candidates[0],
                label_type="VERIFIED",
                exact=True,
                candidates=candidates,
                is_ambiguous=False,
                confidence_cap=None,
                matched_address=matched_addr
            )
        else:
            # Ambiguous match (e.g. D9: 0x28c6c062... in both WAZIRX and BINANCE)
            return ResolvedAttribution(
                vasp_key=candidates[0],
                label_type="INFERRED",
                exact=True,
                candidates=candidates,
                is_ambiguous=True,
                confidence_cap="MEDIUM",
                matched_address=matched_addr
            )

attribution_resolver = AttributionResolver()
