# backend/attribution/attribution_resolver.py
"""
CryptoTrace LEA - Attribution Resolver
§1.1 FIX: Walk hops in traversal order (by hop_number) and return the FIRST
(nearest/earliest) VASP match — not the terminal node.

Once a VASP hot-wallet is matched, any further hops sourced from that address are
internal exchange movement (out of scope) and should NOT override this finding.

Handles:
- Single unambiguous match → VERIFIED, exact=True
- Multi-VASP ambiguous match → INFERRED, is_ambiguous=True
- No match → UNRESOLVED
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
    # §1.1 new: hop number at which VASP was first encountered
    hop_number: Optional[int] = None


class AttributionResolver:
    def __init__(self, registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.registry = registry or VASP_REGISTRY

    def _match_vasp(self, addr: str) -> Optional[Dict[str, Any]]:
        """
        Check a single address against all VASP hot_wallet_patterns.
        Returns dict with vasp_key, exact, candidates on match; None otherwise.
        """
        addr = addr.lower()
        if not addr:
            return None

        matched: Set[str] = set()
        exact = False

        for vasp_key, vasp_data in self.registry.items():
            patterns = [p.lower() for p in vasp_data.get("hot_wallet_patterns", [])]
            for p in patterns:
                if p.endswith("..."):
                    prefix = p[:-3]
                    if addr.startswith(prefix):
                        matched.add(vasp_key)
                elif addr == p:
                    matched.add(vasp_key)
                    exact = True

        if not matched:
            return None

        candidates = sorted(list(matched))
        return {"vasp_key": candidates[0], "exact": exact, "candidates": candidates}

    def resolve(self, trace_result: Dict[str, Any]) -> ResolvedAttribution:
        """
        §1.1 NEAREST-VASP RESOLUTION:
        Walk hops sorted by hop_number (traversal order) and return the FIRST
        address that matches a VASP registry entry. This correctly identifies the
        nearest exchange, not the terminal (deepest) node.
        """
        hops = trace_result.get("hops", [])

        # Sort hops by hop_number to ensure traversal order
        hops_sorted = sorted(hops, key=lambda h: h.get("hop_number", 0))

        for hop in hops_sorted:
            addr = (hop.get("to_address") or "").lower()
            match = self._match_vasp(addr)
            if match:
                candidates = match["candidates"]
                is_ambiguous = len(candidates) > 1
                # When multiple VASPs share an address, label is INFERRED regardless of
                # whether the individual pattern match is exact — ambiguity caps the certainty.
                label_type = "INFERRED" if is_ambiguous else ("VERIFIED" if match["exact"] else "INFERRED")
                return ResolvedAttribution(
                    vasp_key=match["vasp_key"],
                    label_type=label_type,
                    exact=match["exact"],
                    candidates=candidates,
                    is_ambiguous=is_ambiguous,
                    confidence_cap="MEDIUM" if is_ambiguous else None,
                    matched_address=addr,
                    hop_number=hop.get("hop_number"),
                )

        # No VASP matched across any hop
        return ResolvedAttribution(
            vasp_key=None,
            label_type="UNRESOLVED",
            exact=False,
            candidates=[],
            is_ambiguous=False,
            confidence_cap=None,
            matched_address=None,
            hop_number=None,
        )


attribution_resolver = AttributionResolver()
