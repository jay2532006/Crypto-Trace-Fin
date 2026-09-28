# backend/api/copilot_routes.py
"""
CryptoTrace LEA - AI Investigator Copilot API Router (Phase 6.1)
Exposes grounded forensic reasoning with multi-provider failover (Gemini / Groq / Rule-based)
and strict anti-hallucination guardrail stripping unverified addresses.
"""

import re
import hashlib
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.auth.decorators import get_current_user
from backend.db.database import db_manager
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from engine.ai_copilot import recommend_actions, summarize_case, chat_copilot, test_ai_health

router = APIRouter(prefix="/api/v1/copilot", tags=["AI Copilot"])

# In-memory cache by (case_id, trace_hash)
COPILOT_CACHE: Dict[str, Any] = {}

class CopilotQueryRequest(BaseModel):
    query: str
    trace_data: Optional[Dict[str, Any]] = None

def enforce_grounding_guardrail(copilot_text: str, trace_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asserts every crypto address (0x... or T...) cited in output exists in the verified trace.
    Strips hallucinated addresses per SIH 26183 evidentiary integrity mandates.
    """
    hops = trace_data.get("hops", [])
    nodes = trace_data.get("nodes", [])
    valid_addrs = set()
    for h in hops:
        if h.get("from_address"): valid_addrs.add(h["from_address"].lower())
        if h.get("to_address"): valid_addrs.add(h["to_address"].lower())
    for n in nodes:
        if n.get("id"): valid_addrs.add(n["id"].lower())
    suspect = trace_data.get("suspect_address")
    if suspect: valid_addrs.add(suspect.lower())

    hallucinations = []
    addr_pattern = re.compile(r"\b(0x[a-fA-F0-9]{40}|T[A-Za-z1-9]{33})\b")

    def _replace_hallucination(match):
        found = match.group(1)
        if found.lower() not in valid_addrs:
            hallucinations.append(found)
            return f"[UNVERIFIED ADDRESS {found[:6]}... STRIPPED BY CO-PILOT SAFEGUARD]"
        return found

    sanitized = addr_pattern.sub(_replace_hallucination, copilot_text)
    return {
        "text": sanitized,
        "guardrail_triggered": len(hallucinations) > 0,
        "stripped_hallucinations": hallucinations,
        "is_grounded": len(hallucinations) == 0,
    }

@router.get("/health")
def get_copilot_health():
    """Returns health and provider status (Gemini, Groq, Fallback)."""
    return test_ai_health()

@router.post("/{case_id}/recommend")
def get_copilot_recommendations(
    case_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Generates grounded investigative action recommendations for a case."""
    case = db_manager.get_case(case_id)
    wallet = case["wallet"] if case else "0x0cbe050f75bc8f8c2d6c0d249eff12d71a28169b"
    chain = case.get("chain", "ETH") if case else "ETH"

    # Fetch or run trace
    trace_data = bounded_tracer.trace(
        start_address=wallet,
        chain=chain,
        constraints=TraceConstraints(max_hops=4),
        case_id=case_id,
        mode="DEMO"
    )

    trace_hash = hashlib.sha256(json.dumps(trace_data.get("hops", []), sort_keys=True).encode()).hexdigest()
    cache_key = f"{case_id}:{trace_hash}:recommend"

    if cache_key in COPILOT_CACHE:
        return COPILOT_CACHE[cache_key]

    raw_response = recommend_actions(trace_data)
    action_text = raw_response.get("recommendations") or raw_response.get("summary") or str(raw_response)
    
    guardrail_res = enforce_grounding_guardrail(action_text, trace_data)

    result = {
        "case_id": case_id,
        "provider": raw_response.get("provider", "Rule-Based Deterministic Fallback"),
        "model": raw_response.get("model", "Deterministic Forensic Engine"),
        "recommendations": guardrail_res["text"],
        "guardrail": {
            "is_grounded": guardrail_res["is_grounded"],
            "guardrail_triggered": guardrail_res["guardrail_triggered"],
            "stripped_hallucinations": guardrail_res["stripped_hallucinations"],
        },
        "cached": False,
    }
    COPILOT_CACHE[cache_key] = result
    return result

@router.post("/{case_id}/chat")
def post_copilot_chat(
    case_id: str,
    req: CopilotQueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Interactive case Q&A grounded exclusively in verified forensic trace evidence."""
    case = db_manager.get_case(case_id)
    wallet = case["wallet"] if case else "0x0cbe050f75bc8f8c2d6c0d249eff12d71a28169b"
    chain = case.get("chain", "ETH") if case else "ETH"

    trace_data = req.trace_data or bounded_tracer.trace(
        start_address=wallet, chain=chain, constraints=TraceConstraints(max_hops=4), case_id=case_id, mode="DEMO"
    )

    raw_ans = chat_copilot(query=req.query, trace_data=trace_data)
    ans_text = raw_ans.get("response") or raw_ans.get("answer") or str(raw_ans)
    guardrail_res = enforce_grounding_guardrail(ans_text, trace_data)

    return {
        "case_id": case_id,
        "query": req.query,
        "response": guardrail_res["text"],
        "provider": raw_ans.get("provider", "Rule-based Fallback"),
        "guardrail": guardrail_res,
    }
