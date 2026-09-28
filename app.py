"""
SAHYOG Blockchain Intelligence & VASP Attribution Engine
FastAPI Backend — Main Application

DATA SOURCE LEGEND (shown in every API response):
  🟢 LIVE      = Real-time data from public blockchain explorer APIs
  🟡 SIMULATED = Algorithmically generated fallback (when API unavailable)
  🔴 HARDCODED = Static data we manually curated (VASP DB, legal templates, mixer list)
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Any, Dict
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "sahyog.db")

# Load environment variables safely
def load_env():
    env_file = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()

load_env()
APP_MODE = os.getenv("APP_MODE", "demo")
APP_ENV = os.getenv("APP_ENV", "development")

from engine.address_validator import validate_and_classify_address
from engine.graph_tracer import trace_wallet, detect_chain
from engine.notice_generator import generate_notice
from engine.vasp_cluster import get_all_vasps, CHAIN_EXPLORERS
from engine.demo_cases import get_demo_cases, get_case_by_id
from engine.real_api import fetch_real_data
from engine.neo4j_engine import check_neo4j_status, sync_trace_to_neo4j, execute_cypher, init_neo4j_schema

from backend.api import case_router, trace_router, notice_router, evidence_router, auth_router, intake_router, copilot_router
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from backend.fixtures.demo_cases_v2 import get_crypto_trace_fixtures
from backend.legal.notice_generator import notice_generator

# Startup Security Guard (Phase 8.1 Win Plan)
_app_env = os.getenv("APP_ENV", "development").lower()
_secret_key = os.getenv("SECRET_KEY", "cryptotrace-lea-insecure-dev-secret-key-32charsmin")
if _app_env == "production" and _secret_key == "cryptotrace-lea-insecure-dev-secret-key-32charsmin":
    raise RuntimeError(
        "FATAL: Insecure default SECRET_KEY detected in production environment. "
        "Server startup aborted per Phase 8.1 security requirements."
    )

app = FastAPI(
    title="CryptoTrace LEA — SIH 26183 Investigation Platform",
    description="Real-Time Crypto Fraud Attribution System for Indian Law Enforcement (MHA / I4C).",
    version="2.0.0-SIH26183",
)

allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Canonical CryptoTrace LEA API Routers
app.include_router(case_router)
app.include_router(trace_router)
app.include_router(notice_router)
app.include_router(evidence_router)
app.include_router(auth_router)
app.include_router(intake_router)
app.include_router(copilot_router)


# ─── Database Setup ──────────────────────────────────────────────────────────

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            suspect_address TEXT,
            chain TEXT,
            crime_category TEXT,
            nearest_vasp TEXT,
            risk_score INTEGER,
            risk_category TEXT,
            confidence INTEGER,
            investigating_officer TEXT,
            created_at TEXT,
            result_json TEXT
        )
    """)
    conn.commit()
    conn.close()
    try:
        init_neo4j_schema()
    except Exception:
        pass

init_db()


# ─── Request Models ──────────────────────────────────────────────────────────

class TraceRequest(BaseModel):
    address: str
    chain: Optional[str] = None
    crime_category: str = "Synthetic Benchmark"
    case_id: Optional[str] = None
    investigating_officer: Optional[str] = "Analyst / Demo"
    mode: Optional[str] = None

class NoticeRequest(BaseModel):
    case_id: str
    trace_id: int
    investigating_officer: str = "Inspector / IO"
    unit: str = "Cyber Crime Police Station"
    state: str = "Maharashtra"
    fir_number: Optional[str] = None
    complainant: Optional[str] = None

class CustomApiTestRequest(BaseModel):
    url: str
    method: Optional[str] = "GET"
    headers: Optional[dict] = None
    body: Optional[Any] = None

class AIChatRequest(BaseModel):
    question: str
    trace_data: Optional[Dict[str, Any]] = None

class AISummaryRequest(BaseModel):
    trace_data: Dict[str, Any]

class AIReportRequest(BaseModel):
    trace_data: Dict[str, Any]
    io_name: Optional[str] = "Investigating Officer"
    case_id: Optional[str] = "CR-2026-UNSPECIFIED"


# ─── API Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "running",
        "prototype": "TraceX v2.0 (SIH26182 Research Prototype)",
        "theme": "Ministry of Home Affairs / I4C CIS Division",
        "problem_statement_id": "26182",
        "app_mode": os.getenv("APP_MODE", "demo"),
        "environment": os.getenv("APP_ENV", "development"),
        "time": datetime.now().isoformat()
    }


@app.get("/api/config")
def get_config():
    return {
        "app_mode": os.getenv("APP_MODE", "demo"),
        "supported_chains": ["BTC", "ETH", "TRON", "BNB", "POLYGON", "SOL"],
        "providers": {
            "btc": "Blockstream Esplora (Public / Open)",
            "eth": "Etherscan V2 API (ChainID 1 - Active Key)",
            "tron": "TronGrid API (TRON-PRO-API-KEY Active)",
            "multi_chain": "Bitquery V2 GraphQL (Bearer Token Active)",
            "prices": "CoinGecko API (Demo Key Active - USD/INR)",
            "sanctions": "OFAC Sanctions List Service (US Treasury SDN)",
            "fraud": "Chainabuse API (Public Intelligence)"
        },
        "claims": {
            "sahyog_integration": "MOCK / DRAFT SPECIFICATION",
            "status": "SIH26182 Research Prototype",
            "legal_notice": "Draft only — Requires IO Authorization under BNSS 2023 / CrPC 91"
        }
    }


@app.get("/api/prices")
def get_crypto_prices():
    """Return live CoinGecko spot rates for BTC, ETH, SOL, TRON, USDT."""
    from engine.price_feed import get_live_prices
    return get_live_prices()


@app.get("/api/test/apis")
def test_all_connected_apis():
    """Live Postman-style diagnostic test across all 7 connected blockchain & AML APIs."""
    from engine.api_tester import run_all_api_tests
    return run_all_api_tests()


@app.get("/api/test/api/{api_id}")
def test_individual_api(api_id: str):
    """Execute live Postman-style ping on a specific API provider."""
    from engine.api_tester import API_TESTERS
    fn = API_TESTERS.get(api_id.lower())
    if not fn:
        raise HTTPException(
            status_code=404,
            detail=f"API '{api_id}' not found. Valid APIs: {list(API_TESTERS.keys())}"
        )
    return fn()


@app.post("/api/test/custom")
def test_custom_api(req: CustomApiTestRequest):
    """
    Arbitrary outbound HTTP tester is disabled in production per PRD Section 19.3
    to protect LEA infrastructure against Server-Side Request Forgery (SSRF).
    """
    raise HTTPException(
        status_code=403,
        detail="Security Policy Restriction: Arbitrary outbound HTTP requests are disabled per CryptoTrace LEA PRD Section 19.3."
    )


# ─── AI Investigator Copilot Endpoints ─────────────────────────────────────

@app.get("/api/ai/health")
def get_ai_health():
    """Diagnostic health check for Gemini (Primary), Groq (Fallback), and Hugging Face."""
    from engine.ai_copilot import test_ai_health
    return test_ai_health()


@app.post("/api/ai/copilot/chat")
def copilot_chat(req: AIChatRequest):
    """Interactive AI Copilot Q&A grounded strictly upon verified cryptographic case trace."""
    from engine.ai_copilot import chat_copilot
    return chat_copilot(req.question, req.trace_data or {})


@app.post("/api/ai/copilot/summary")
def copilot_summary(req: AISummaryRequest):
    """Generate concise fund flow summary and VASP identification briefing."""
    from engine.ai_copilot import summarize_case
    return summarize_case(req.trace_data)


@app.post("/api/ai/copilot/report")
def copilot_report(req: AIReportRequest):
    """Generate formal Section 91 BNSS Investigation Report drafted for human/legal review."""
    from engine.ai_copilot import generate_investigation_report
    officer_info = {
        "officer": req.io_name or "Investigating Officer",
        "case_id": req.case_id or "CR-2026-UNSPECIFIED"
    }
    return generate_investigation_report(req.trace_data, officer_info)


@app.get("/api/chains")
def get_chains():
    return CHAIN_EXPLORERS


@app.get("/api/vasps")
def get_vasps():
    return get_all_vasps()


@app.get("/api/cases/demo")
def demo_cases():
    fixtures = get_crypto_trace_fixtures()
    return [
        {
            "case_id": f["case_id"],
            "title": f["title"],
            "suspect_address": f["suspect_wallet"],
            "chain": f["chain"],
            "crime_category": f["crime_category"],
            "reported_amount": f"{f['reported_amount']:,.0f} {f['reported_asset']}",
            "summary": f["documented_pattern"],
            "demo_data": True,
            "source_origin": f["source_origin"],
        }
        for f in fixtures
    ]


@app.get("/api/live/{address}")
def get_live_data(address: str, chain: Optional[str] = None):
    """
    🟢 LIVE endpoint — Fetch real blockchain data from public APIs.
    Calls Etherscan (ETH), Blockstream/Blockchair (BTC), TronScan (TRON).
    Strictly validates address format before making upstream queries.
    """
    addr = (address or "").strip()
    val = validate_and_classify_address(addr, expected_chain=chain)
    if not val["is_valid"]:
        raise HTTPException(
            status_code=422,
            detail={
                "error_code": "INVALID_WALLET_ADDRESS",
                "message": val["error"],
                "input_address": addr
            }
        )
    return fetch_real_data(addr, val["detected_chain"])


@app.get("/api/cases/history")
def investigation_history():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, case_id, suspect_address, chain, crime_category,
               nearest_vasp, risk_score, risk_category, confidence,
               investigating_officer, created_at
        FROM investigations ORDER BY id DESC LIMIT 50
    """)
    rows = cur.fetchall()
    conn.close()
    cols = ["id", "case_id", "suspect_address", "chain", "crime_category",
            "nearest_vasp", "risk_score", "risk_category", "confidence",
            "investigating_officer", "created_at"]
    return [dict(zip(cols, row)) for row in rows]


@app.get("/api/cases/{trace_id}/result")
def get_trace_result(trace_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT result_json FROM investigations WHERE id=?", (trace_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Trace not found")
    return json.loads(row[0])


@app.post("/api/trace")
def run_trace(req: TraceRequest):
    """Main endpoint: Validate wallet address and execute VASP attribution trace."""
    address = (req.address or "").strip()
    if not address:
        raise HTTPException(
            status_code=422,
            detail={"error_code": "EMPTY_ADDRESS", "message": "Wallet address is required"}
        )

    # 1. Cryptographic Address Validation
    val = validate_and_classify_address(address, expected_chain=req.chain)
    if not val["is_valid"]:
        raise HTTPException(
            status_code=422,
            detail={
                "error_code": "INVALID_WALLET_ADDRESS",
                "message": val["error"],
                "input_address": address,
                "supported_formats": "Bitcoin (1..., 3..., bc1...), EVM (ETH/BNB/Polygon 0x...), TRON (T...), Solana (Base58)"
            }
        )

    resolved_chain = val["detected_chain"]
    mode = req.mode or os.getenv("APP_MODE", "demo")
    case_id = req.case_id or f"CR-2026-AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Execute Bounded Trace with AdaptiveVASPScorer, MULE_NETWORK, Risk & Recovery
    result = bounded_tracer.trace(
        start_address=address,
        chain=resolved_chain,
        constraints=TraceConstraints(max_hops=5),
        case_id=case_id,
        mode=mode.upper(),
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=422, detail=result)

    # Backward compatibility mapping for legacy UI widgets
    attr = result.get("attribution", {})
    raw_conf = attr.get("score", 0)
    conf_pct = int(round(raw_conf * 100)) if raw_conf <= 1.0 else int(raw_conf)
    result["nearest_vasp"] = {
        "name": attr.get("vasp_name", "Unknown"),
        "confidence": conf_pct,
        "score": raw_conf,
        "label_type": attr.get("label_type", "UNRESOLVED"),
        "confidence_band": attr.get("confidence_band", "LOW"),
        "policy_version": attr.get("policy_version", "policy_v1_india_kyc"),
        "nodal_officer_email": attr.get("nodal_officer_email", "nodal@exchange.com"),
        "fiu_status": attr.get("fiu_status", "UNREGISTERED"),
        "scoring_steps": attr.get("scoring_steps", []),
    }
    result["risk_score"] = result.get("risk", {}).get("risk_score", 0)
    result["risk_category"] = result.get("risk", {}).get("risk_category", "UNKNOWN")

    # Save to SQLite history
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO investigations
        (case_id, suspect_address, chain, crime_category, nearest_vasp,
         risk_score, risk_category, confidence, investigating_officer, created_at, result_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        case_id,
        address,
        resolved_chain,
        req.crime_category,
        result["nearest_vasp"]["name"],
        result["risk_score"],
        result["risk_category"],
        result["nearest_vasp"]["confidence"],
        req.investigating_officer or "Inspector R. Sharma",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        json.dumps(result),
    ))
    trace_id = cur.lastrowid
    conn.commit()
    conn.close()

    result["trace_id"] = trace_id
    result["case_id"] = case_id
    result["mode"] = mode.upper()

    return result


@app.post("/api/notice/generate")
def create_notice(req: NoticeRequest):
    """Generate a lawful disclosure and freezing notice for the identified VASP."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT result_json FROM investigations WHERE id=?", (req.trace_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Trace result not found. Run /api/trace first.")

    trace_result = json.loads(row[0])
    notice = generate_notice(
        trace_result=trace_result,
        case_id=req.case_id,
        investigating_officer=req.investigating_officer,
        unit=req.unit,
        state=req.state,
        fir_number=req.fir_number,
        complainant=req.complainant,
    )

    # Save notice to file
    notice_file = os.path.join(BASE_DIR, "reports", f"notice_{req.case_id}_{req.trace_id}.txt")
    with open(notice_file, "w") as f:
        f.write(notice["notice_text"])

    return notice


@app.post("/api/demo/trace/{case_index}")
def run_demo_trace(case_index: int, investigating_officer: str = "Inspector Demo"):
    """Run a trace using one of the pre-loaded demo cases."""
    cases = get_demo_cases()
    if case_index < 0 or case_index >= len(cases):
        raise HTTPException(status_code=404, detail=f"Demo case index {case_index} not found")

    case = cases[case_index]
    req = TraceRequest(
        address=case["suspect_address"],
        chain=case["chain"],
        crime_category=case["crime_category"],
        case_id=case["case_id"],
        investigating_officer=investigating_officer,
    )
    return run_trace(req)


class CypherRequest(BaseModel):
    query: str
    params: Optional[Dict[str, Any]] = None


@app.get("/api/neo4j/status")
def get_neo4j_telemetry():
    """Fetch live Neo4j Aura Cloud graph status, telemetry, and node/relationship counts."""
    return check_neo4j_status()


@app.post("/api/neo4j/query")
def run_neo4j_cypher(req: CypherRequest):
    """
    Arbitrary Cypher query execution is disabled in production per PRD Section 18.2.
    Graph store is a rebuildable projection only; all queries must use controlled APIs.
    """
    raise HTTPException(
        status_code=403,
        detail="Security Policy Restriction: Arbitrary Cypher execution is prohibited per CryptoTrace LEA PRD Section 18.2."
    )


@app.post("/api/neo4j/sync")
def sync_neo4j_trace(trace_data: Dict[str, Any]):
    """Manually trigger trace graph synchronization to Neo4j Aura."""
    return sync_trace_to_neo4j(trace_data)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/")
def api_root():
    """TraceX Sahyog API health check. Frontend is served on port 3000 (Next.js)."""
    return {
        "service": "TraceX Sahyog Blockchain Intelligence API",
        "version": "2.0.0",
        "status": "operational",
        "frontend": "http://localhost:3000",
        "docs": "/docs",
    }


@app.get("/download/{filename}")
def download_file(filename: str):
    """Directly download forensic guides, manuals, and reports."""
    allowed = {
        "SAHYOG_QA_QUICK_GUIDE_EN.pdf",
        "SAHYOG_QA_QUICK_GUIDE.pdf",
        "TraceX_System_Workflow_Manual.pdf",
        "SAHYOG_QA_QUICK_GUIDE_EN.md",
        "SAHYOG_QA_QUICK_GUIDE.md",
        "WORKFLOW_MANUAL.md",
    }
    if filename in allowed:
        file_path = os.path.join(BASE_DIR, filename)
        if os.path.exists(file_path):
            media_type = "application/pdf" if filename.endswith(".pdf") else "text/markdown"
            return FileResponse(
                file_path,
                filename=filename,
                media_type=media_type,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8765, reload=True)
