# scripts/update_ofac_and_briefing.py
doc_path = "docs/ARCHITECTURE_AND_CORE_LOGIC.md"
with open(doc_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace briefing terminal phrase
old_phrase = "On-chain clustering and hot wallet fingerprinting attribute the terminal fund destination to **{vasp}**:"
new_phrase = "On-chain clustering and hot wallet fingerprinting attribute the nearest identified VASP counterparty to **{vasp}**:"
content = content.replace(old_phrase, new_phrase)

# Add fuzzy entity screening to Section 12
old_ofac_steps = """4. **Integration with Trace Engine:**  
   During BFS traversal, all traversed addresses (`start_address`, `nodes`, `hops`) are passed through `screen_ofac_sanctions()`. If any address is sanctioned, `ofac_sanction_hit = True` is set on the trace result, triggering $+45$ in the risk assessment."""

new_ofac_steps = """4. **Integration with Trace Engine:**  
   During BFS traversal, all traversed addresses (`start_address`, `nodes`, `hops`) are passed through `screen_ofac_sanctions()`. If any address is sanctioned, `ofac_sanction_hit = True` is set on the trace result, triggering $+45$ in the risk assessment.
5. **Fuzzy Entity-Name Screening (§Phase5):**  
   `fuzzy_screen_ofac_entity(entity_name, threshold=0.85)` uses Python's `difflib.SequenceMatcher` to fuzzy-match suspected organization and person names against OFAC SDN aliases. Batch workflows utilize `bulk_fuzzy_screen_entities(entities, threshold=0.85)` to screen entire victim complaint sheets simultaneously."""

assert old_ofac_steps in content, "Could not find old_ofac_steps"
content = content.replace(old_ofac_steps, new_ofac_steps)

with open(doc_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: OFAC and briefing updated!")
