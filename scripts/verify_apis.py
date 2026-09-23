"""
CryptoTrace LEA — Comprehensive API Setup & Verification Suite
Verifies both:
1. Internal Backend FastAPI Endpoints (Auth, Cases, Traces, Notices, Evidence, Audit)
2. External Live Blockchain & Explorer Gateways (ETH, Polygon, Bitcoin, TRON, CoinGecko)
"""

import sys
import os
import json
import time
import requests

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app import app

# Initialize FastAPI TestClient for in-process internal API testing
client = TestClient(app)

print("=" * 70)
print("  CRYPTOTRACE LEA — API SUITE VERIFICATION REPORT")
print("  SIH Problem Statement 26183 | Law Enforcement Intelligence System")
print("=" * 70)

results = []

def record(category: str, name: str, status: str, latency_ms: float, details: str = ""):
    results.append({
        "category": category,
        "name": name,
        "status": status,
        "latency_ms": latency_ms,
        "details": details,
    })
    icon = "[OK]" if status == "PASSED" else "[OPTIONAL/INFO]" if status == "INFO" else "[FAIL]"
    print(f" {icon:<16} | {name:<35} | {latency_ms:>6.1f}ms | {details}")

# ============================================================================
# PART 1: INTERNAL FASTAPI BACKEND ENDPOINTS
# ============================================================================
print("\n--- 1. Testing Internal Backend REST APIs ---")

# 1.1 Auth Login
t0 = time.time()
resp = client.post("/api/v1/auth/login", json={"username": "investigator1", "password": "Password@123"})
ms = (time.time() - t0) * 1000
if resp.status_code == 200 and "access_token" in resp.json():
    auth_token = resp.json()["access_token"]
    record("INTERNAL", "POST /api/v1/auth/login", "PASSED", ms, f"Role: {resp.json().get('role')}")
else:
    auth_token = ""
    record("INTERNAL", "POST /api/v1/auth/login", "FAILED", ms, f"HTTP {resp.status_code}")

headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

# 1.2 Auth Me
t0 = time.time()
resp = client.get("/api/v1/auth/me", headers=headers)
ms = (time.time() - t0) * 1000
if resp.status_code == 200 and resp.json().get("username") == "investigator1":
    record("INTERNAL", "GET /api/v1/me", "PASSED", ms, f"Unit: {resp.json().get('unit')}")
else:
    record("INTERNAL", "GET /api/v1/me", "FAILED", ms, f"HTTP {resp.status_code}")

# 1.3 Case Intake (POST /api/v1/cases)
t0 = time.time()
case_payload = {
    "case_id": f"CR-TEST-{int(time.time())}",
    "source": "NCRP_PORTAL",
    "chain": "ETH",
    "wallet": "0x0cbe050f75bc8f8c2d6c0d249eff12d71a28169b",
    "reported_amount": 150000.0,
    "complaint_text": "Victim reported funds siphoned to suspect address.",
    "complainant_name": "Test Complainant",
    "fir_number": "FIR-2026-TEST",
}
resp = client.post("/api/v1/cases", json=case_payload, headers=headers)
ms = (time.time() - t0) * 1000
if resp.status_code in (200, 201) and resp.json().get("case_id") == case_payload["case_id"]:
    record("INTERNAL", "POST /api/v1/cases", "PASSED", ms, f"Indexed: {case_payload['case_id']}")
else:
    record("INTERNAL", "POST /api/v1/cases", "FAILED", ms, f"HTTP {resp.status_code}")

# 1.4 Case Listing (GET /api/v1/cases)
t0 = time.time()
resp = client.get("/api/v1/cases", headers=headers)
ms = (time.time() - t0) * 1000
if resp.status_code == 200 and isinstance(resp.json(), list):
    record("INTERNAL", "GET /api/v1/cases", "PASSED", ms, f"Total Cases: {len(resp.json())}")
else:
    record("INTERNAL", "GET /api/v1/cases", "FAILED", ms, f"HTTP {resp.status_code}")

# 1.5 Benchmarks / Fixtures (GET /api/v1/fixtures)
t0 = time.time()
resp = client.get("/api/v1/fixtures", headers=headers)
ms = (time.time() - t0) * 1000
if resp.status_code == 200 and len(resp.json()) >= 3:
    record("INTERNAL", "GET /api/v1/fixtures", "PASSED", ms, f"Loaded {len(resp.json())} benchmarks")
else:
    record("INTERNAL", "GET /api/v1/fixtures", "FAILED", ms, f"HTTP {resp.status_code}")

# 1.6 Bounded Forensic Trace (POST /api/v1/trace)
t0 = time.time()
trace_req = {
    "address": "0x0cbe050f75bc8f8c2d6c0d249eff12d71a28169b",
    "chain": "ETH",
    "max_hops": 4,
    "mode": "DEMO",
}
resp = client.post("/api/v1/trace", json=trace_req, headers=headers)
ms = (time.time() - t0) * 1000
trace_data = resp.json() if resp.status_code == 200 else {}
if resp.status_code == 200 and "attribution" in trace_data and "hops" in trace_data:
    vasp = trace_data.get("attribution", {}).get("vasp_name", "Unknown")
    score = trace_data.get("attribution", {}).get("score", 0)
    record("INTERNAL", "POST /api/v1/trace", "PASSED", ms, f"VASP: {vasp} | Score: {score}")
else:
    record("INTERNAL", "POST /api/v1/trace", "FAILED", ms, f"HTTP {resp.status_code}")

# 1.7 Section 91 Notice Drafting (POST /api/v1/notices/draft)
t0 = time.time()
notice_req = {
    "case_id": case_payload["case_id"],
    "trace_data": trace_data or {"attribution": {"vasp_name": "WazirX"}},
    "investigating_officer": "Inspector R. Sharma",
    "unit": "Cyber Crime PS",
    "state": "Maharashtra",
    "fir_number": "FIR-2026/89",
    "complainant": "Victim S.",
}
resp = client.post("/api/v1/notices/draft", json=notice_req, headers=headers)
ms = (time.time() - t0) * 1000
draft_id = resp.json().get("draft_id") if resp.status_code == 200 else ""
if resp.status_code == 200 and draft_id and resp.json().get("status") == "DRAFT":
    record("INTERNAL", "POST /api/v1/notices/draft", "PASSED", ms, f"Draft: {draft_id}")
else:
    record("INTERNAL", "POST /api/v1/notices/draft", "FAILED", ms, f"HTTP {resp.status_code}")

# 1.8 Notice Submit for Approval (POST /api/v1/notices/{id}/submit)
if draft_id:
    t0 = time.time()
    resp = client.post(f"/api/v1/notices/{draft_id}/submit", headers=headers)
    ms = (time.time() - t0) * 1000
    if resp.status_code == 200 and resp.json().get("draft", {}).get("status") == "PENDING_APPROVAL":
        record("INTERNAL", "POST /notices/{id}/submit", "PASSED", ms, "Status: PENDING_APPROVAL")
    else:
        record("INTERNAL", "POST /notices/{id}/submit", "FAILED", ms, f"HTTP {resp.status_code}")

    # 1.9 Supervisor Approval Gate (POST /api/v1/notices/{id}/approve)
    # Obtain supervisor token
    s_resp = client.post("/api/v1/auth/login", json={"username": "supervisor1", "password": "Password@123"})
    sup_token = s_resp.json().get("access_token", "")
    sup_headers = {"Authorization": f"Bearer {sup_token}"}

    t0 = time.time()
    resp = client.post(
        f"/api/v1/notices/{draft_id}/approve",
        json={"supervisor_notes": "Formal Section 91 order authorized for dispatch."},
        headers=sup_headers,
    )
    ms = (time.time() - t0) * 1000
    if resp.status_code == 200 and resp.json().get("draft", {}).get("status") == "APPROVED":
        record("INTERNAL", "POST /notices/{id}/approve", "PASSED", ms, "Status: APPROVED by Supervisor")
    else:
        record("INTERNAL", "POST /notices/{id}/approve", "FAILED", ms, f"HTTP {resp.status_code}")

# 1.10 Cryptographic Audit Chain Verification (GET /api/v1/audit/verify-chain)
t0 = time.time()
resp = client.get("/api/v1/audit/verify-chain", headers=headers)
ms = (time.time() - t0) * 1000
if resp.status_code == 200 and resp.json().get("is_valid", resp.json().get("valid")) is True:
    total_evts = resp.json().get("total_events", 0)
    record("INTERNAL", "GET /api/v1/audit/verify-chain", "PASSED", ms, f"Chain Valid: {total_evts} events")
else:
    record("INTERNAL", "GET /api/v1/audit/verify-chain", "FAILED", ms, f"HTTP {resp.status_code}")


# ============================================================================
# PART 2: EXTERNAL LIVE BLOCKCHAIN & EXPLORER GATEWAYS
# ============================================================================
print("\n--- 2. Testing External Live Blockchain Gateways ---")

HTTP_HEADERS = {"User-Agent": "CryptoTrace-LEA/2.0"}

# 2.1 Ethereum Primary RPC (PublicNode / Merkle)
try:
    t0 = time.time()
    r = requests.post(
        "https://ethereum-rpc.publicnode.com",
        json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
        headers=HTTP_HEADERS,
        timeout=6,
    )
    ms = (time.time() - t0) * 1000
    if r.status_code == 200 and "result" in r.json():
        blk = int(r.json()["result"], 16)
        record("EXTERNAL", "Ethereum PublicNode RPC", "PASSED", ms, f"Current Block: #{blk:,}")
    else:
        record("EXTERNAL", "Ethereum PublicNode RPC", "FAILED", ms, f"HTTP {r.status_code}")
except Exception as e:
    record("EXTERNAL", "Ethereum PublicNode RPC", "FAILED", 0, str(e)[:40])

# 2.2 Polygon PoS Primary RPC (1RPC)
try:
    t0 = time.time()
    r = requests.post(
        "https://1rpc.io/matic",
        json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
        headers=HTTP_HEADERS,
        timeout=6,
    )
    ms = (time.time() - t0) * 1000
    if r.status_code == 200 and "result" in r.json():
        blk = int(r.json()["result"], 16)
        record("EXTERNAL", "Polygon 1RPC Gateway", "PASSED", ms, f"Current Block: #{blk:,}")
    else:
        record("EXTERNAL", "Polygon 1RPC Gateway", "FAILED", ms, f"HTTP {r.status_code}")
except Exception as e:
    record("EXTERNAL", "Polygon 1RPC Gateway", "FAILED", 0, str(e)[:40])

# 2.3 Bitcoin Mempool.space
try:
    t0 = time.time()
    r = requests.get("https://mempool.space/api/blocks/tip/height", headers=HTTP_HEADERS, timeout=6)
    ms = (time.time() - t0) * 1000
    if r.status_code == 200 and r.text.strip().isdigit():
        record("EXTERNAL", "Bitcoin Mempool.space", "PASSED", ms, f"Tip Height: #{int(r.text.strip()):,}")
    else:
        record("EXTERNAL", "Bitcoin Mempool.space", "FAILED", ms, f"HTTP {r.status_code}")
except Exception as e:
    record("EXTERNAL", "Bitcoin Mempool.space", "FAILED", 0, str(e)[:40])

# 2.4 Bitcoin Blockstream Esplora (Fallback)
try:
    t0 = time.time()
    r = requests.get("https://blockstream.info/api/blocks/tip/height", headers=HTTP_HEADERS, timeout=6)
    ms = (time.time() - t0) * 1000
    if r.status_code == 200 and r.text.strip().isdigit():
        record("EXTERNAL", "Bitcoin Blockstream Esplora", "PASSED", ms, f"Tip Height: #{int(r.text.strip()):,}")
    else:
        record("EXTERNAL", "Bitcoin Blockstream Esplora", "FAILED", ms, f"HTTP {r.status_code}")
except Exception as e:
    record("EXTERNAL", "Bitcoin Blockstream Esplora", "FAILED", 0, str(e)[:40])

# 2.5 TRON TronGrid Gateway
try:
    t0 = time.time()
    r = requests.post("https://api.trongrid.io/wallet/getnowblock", headers=HTTP_HEADERS, timeout=6)
    ms = (time.time() - t0) * 1000
    if r.status_code == 200 and "block_header" in r.json():
        b_num = r.json()["block_header"]["raw_data"]["number"]
        record("EXTERNAL", "TRON TronGrid Gateway", "PASSED", ms, f"Latest Block: #{b_num:,}")
    else:
        record("EXTERNAL", "TRON TronGrid Gateway", "FAILED", ms, f"HTTP {r.status_code}")
except Exception as e:
    record("EXTERNAL", "TRON TronGrid Gateway", "FAILED", 0, str(e)[:40])

# 2.6 CoinGecko Live Price Feed
try:
    t0 = time.time()
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether,solana&vs_currencies=usd,inr",
        headers=HTTP_HEADERS,
        timeout=6,
    )
    ms = (time.time() - t0) * 1000
    if r.status_code == 200 and "bitcoin" in r.json():
        btc_usd = r.json()["bitcoin"]["usd"]
        eth_usd = r.json()["ethereum"]["usd"]
        record("EXTERNAL", "CoinGecko Market Feed", "PASSED", ms, f"BTC: ${btc_usd:,} | ETH: ${eth_usd:,}")
    else:
        record("EXTERNAL", "CoinGecko Market Feed", "FAILED", ms, f"HTTP {r.status_code}")
except Exception as e:
    record("EXTERNAL", "CoinGecko Market Feed", "FAILED", 0, str(e)[:40])

# 2.7 Etherscan API V2
try:
    t0 = time.time()
    r = requests.get(
        "https://api.etherscan.io/v2/api?chainid=1&module=proxy&action=eth_blockNumber",
        headers=HTTP_HEADERS,
        timeout=6,
    )
    ms = (time.time() - t0) * 1000
    if r.status_code == 200:
        record("EXTERNAL", "Etherscan V2 Gateway", "PASSED", ms, "Endpoint responsive")
    else:
        record("EXTERNAL", "Etherscan V2 Gateway", "INFO", ms, f"HTTP {r.status_code} (Requires API Key for higher rate limit)")
except Exception as e:
    record("EXTERNAL", "Etherscan V2 Gateway", "INFO", 0, "Public rate limit or key needed")


print("\n" + "=" * 70)
total_tested = len(results)
passed = sum(1 for r in results if r["status"] == "PASSED")
print(f"  VERIFICATION COMPLETE: {passed}/{total_tested} APIs Verified and Operational.")
print("=" * 70)
