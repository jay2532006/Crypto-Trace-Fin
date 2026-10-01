# scripts/update_resolver_snippet.py
doc_path = "docs/ARCHITECTURE_AND_CORE_LOGIC.md"
with open(doc_path, "r", encoding="utf-8") as f:
    content = f.read()

old_resolver_code = """```python
# backend/attribution/attribution_resolver.py
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
```

#### Edge cases & failure modes:
- **Mixer Traversal False Positives:** When a mixer is traversed, `mixer_detected` is `True`. In Step 4, `match_strength` is forcibly lowered to `0.10`, the `mixer_weight` is set to `-0.30`, and `label_type` can never be `VERIFIED`.
- **Unknown Destination Address:** If the terminal node does not match any pattern in `VASP_REGISTRY`, `resolve()` returns `vasp_key = None` and `label_type = "UNRESOLVED"`. The engine does not guess or default to WazirX.
- **Ambiguous Multi-VASP Match:** Addresses associated with both Binance and WazirX (due to joint custody/infrastructure) trigger `is_ambiguous = True`, capping confidence at `MEDIUM`."""

new_resolver_code = """```python
# backend/attribution/attribution_resolver.py
class AttributionResolver:
    def __init__(self, registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.registry = registry or VASP_REGISTRY

    def _match_vasp(self, addr: str) -> Optional[Dict[str, Any]]:
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
        \"\"\"
        §1.1 NEAREST-VASP RESOLUTION:
        Walk hops sorted by hop_number (traversal order) and return the FIRST
        address that matches a VASP registry entry. This correctly identifies the
        nearest exchange, not the terminal (deepest) node.
        \"\"\"
        hops = trace_result.get("hops", [])
        hops_sorted = sorted(hops, key=lambda h: h.get("hop_number", 0))

        for hop in hops_sorted:
            addr = (hop.get("to_address") or "").lower()
            match = self._match_vasp(addr)
            if match:
                candidates = match["candidates"]
                is_ambiguous = len(candidates) > 1
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
```

#### Edge cases & failure modes:
- **Nearest-VASP-First Resolution (§1.1):** Walks hops in traversal order (`hops_sorted = sorted(hops, key=lambda h: h.get('hop_number', 0))`) and returns the earliest match. Any subsequent hops from that address represent internal exchange movement and are ignored.
- **Mixer Traversal False Positives:** When a mixer is traversed, `mixer_detected` is `True`. In Step 4, `match_strength` is forcibly lowered to `0.10`, the `mixer_weight` is set to `-0.30`, and `label_type` can never be `VERIFIED`.
- **Unknown Destination Address:** If no traversed address matches any pattern in `VASP_REGISTRY`, `resolve()` returns `vasp_key = None` and `label_type = "UNRESOLVED"`. The engine does not guess or default to WazirX.
- **Ambiguous Multi-VASP Match:** Addresses associated with multiple VASPs (due to shared/co-custody infrastructure) trigger `is_ambiguous = True`, capping confidence at `MEDIUM`, and `score_all_candidates()` produces a ranked candidate list descending."""

assert old_resolver_code in content, "Could not find old_resolver_code"
content = content.replace(old_resolver_code, new_resolver_code)

with open(doc_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: AttributionResolver snippet in Part 3 updated to Nearest-VASP!")
