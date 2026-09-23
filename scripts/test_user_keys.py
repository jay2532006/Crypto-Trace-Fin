"""
CryptoTrace LEA — Dedicated User API Key Validation Script
Tests each configured key individually and reports exact operational status.
"""

import os
import sys
import json
import time
import requests

# Load .env
env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

print("=" * 70)
print("  CRYPTOTRACE LEA — API KEY FUNCTIONALITY VALIDATION")
print("=" * 70)

# -------------------------------------------------------------
# 1. ETHERSCAN API KEY
# -------------------------------------------------------------
print("\n[1/6] Testing ETHERSCAN_API_KEY...")
etherscan_key = os.getenv("ETHERSCAN_API_KEY", "")
if not etherscan_key:
    print("  -> ETHERSCAN_API_KEY is missing in .env")
else:
    # Test with a known high-profile address (Vitalik's address)
    url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=balance&address=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&tag=latest&apikey={etherscan_key}"
    try:
        t0 = time.time()
        r = requests.get(url, timeout=10)
        ms = (time.time() - t0) * 1000
        data = r.json()
        status = data.get("status")
        message = data.get("message")
        result = data.get("result")
        if status == "1":
            eth_bal = int(result) / 10**18
            print(f"  [SUCCESS] Etherscan API Key is VALID! Latency: {ms:.1f}ms")
            print(f"    Queried Address: 0xd8dA...6045")
            print(f"    Observed Balance: {eth_bal:,.4f} ETH")
        else:
            print(f"  [WARNING] Etherscan response: message={message}, result={result}")
    except Exception as e:
        print(f"  [ERROR] Etherscan test failed: {e}")

# -------------------------------------------------------------
# 2. TRON GRID API KEY
# -------------------------------------------------------------
print("\n[2/6] Testing TRON_GRID_API_KEY...")
trongrid_key = os.getenv("TRON_GRID_API_KEY", "")
if not trongrid_key:
    print("  -> TRON_GRID_API_KEY is missing in .env")
else:
    url = "https://api.trongrid.io/v1/accounts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t" # USDT contract address
    headers = {"TRON-PRO-API-KEY": trongrid_key, "User-Agent": "CryptoTrace-LEA/2.0"}
    try:
        t0 = time.time()
        r = requests.get(url, headers=headers, timeout=10)
        ms = (time.time() - t0) * 1000
        if r.status_code == 200:
            d = r.json().get("data", [])
            print(f"  [SUCCESS] TronGrid API Key is VALID! Latency: {ms:.1f}ms")
            print(f"    Contract TR7NHq... account query returned {len(d)} entity records.")
        else:
            print(f"  [WARNING] TronGrid returned HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  [ERROR] TronGrid test failed: {e}")

# -------------------------------------------------------------
# 3. COINGECKO DEMO API KEY
# -------------------------------------------------------------
print("\n[3/6] Testing COINGECKO_DEMO_API_KEY...")
cg_key = os.getenv("COINGECKO_DEMO_API_KEY", "")
if not cg_key:
    print("  -> COINGECKO_DEMO_API_KEY is missing in .env")
else:
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether&vs_currencies=usd,inr"
    headers = {"x-cg-demo-api-key": cg_key, "User-Agent": "CryptoTrace-LEA/2.0"}
    try:
        t0 = time.time()
        r = requests.get(url, headers=headers, timeout=10)
        ms = (time.time() - t0) * 1000
        if r.status_code == 200:
            prices = r.json()
            btc_usd = prices.get("bitcoin", {}).get("usd")
            btc_inr = prices.get("bitcoin", {}).get("inr")
            eth_usd = prices.get("ethereum", {}).get("usd")
            print(f"  [SUCCESS] CoinGecko Demo Key is VALID! Latency: {ms:.1f}ms")
            print(f"    BTC/USD: ${btc_usd:,.2f} | BTC/INR: Rs. {btc_inr:,.0f}")
            print(f"    ETH/USD: ${eth_usd:,.2f}")
        else:
            print(f"  [WARNING] CoinGecko returned HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  [ERROR] CoinGecko test failed: {e}")

# -------------------------------------------------------------
# 4. GROQ API KEY
# -------------------------------------------------------------
print("\n[4/6] Testing GROQ_API_KEY...")
groq_key = os.getenv("GROQ_API_KEY", "")
if not groq_key:
    print("  -> GROQ_API_KEY is missing in .env")
else:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "qwen/qwen3.8-27b",
        "messages": [
            {"role": "system", "content": "You are a cybercrime forensic investigator."},
            {"role": "user", "content": "State in 5 words why Section 91 CrPC notice is critical for crypto preservation."},
        ],
        "max_tokens": 30,
    }
    try:
        t0 = time.time()
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        ms = (time.time() - t0) * 1000
        if r.status_code == 200:
            ans = r.json()["choices"][0]["message"]["content"].strip()
            print(f"  [SUCCESS] Groq API Key is VALID! Latency: {ms:.1f}ms")
            print(f"    Model: qwen/qwen3.8-27b")
            print(f"    Response: \"{ans}\"")
        else:
            print(f"  [WARNING] Groq returned HTTP {r.status_code}: {r.text[:120]}")
    except Exception as e:
        print(f"  [ERROR] Groq test failed: {e}")

# -------------------------------------------------------------
# 5. GEMINI API KEY
# -------------------------------------------------------------
print("\n[5/6] Testing GEMINI_API_KEY...")
gemini_key = os.getenv("GEMINI_API_KEY", "")
if not gemini_key:
    print("  -> GEMINI_API_KEY is missing in .env")
else:
    # Try calling Google Gemini generateContent endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    payload = {
        "contents": [{
            "parts": [{"text": "Explain in one sentence the purpose of FIU-IND registered VASP off-ramps."}]
        }]
    }
    try:
        t0 = time.time()
        r = requests.post(url, json=payload, timeout=10)
        ms = (time.time() - t0) * 1000
        if r.status_code == 200:
            ans = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"  [SUCCESS] Gemini API Key is VALID! Latency: {ms:.1f}ms")
            print(f"    Response: \"{ans[:90]}...\"")
        else:
            print(f"  [INFO] Gemini API returned HTTP {r.status_code}: {r.text[:120]}")
            print("    (Note: If this key is for Vertex AI / Cloud Project 515650279416, Groq is set as primary provider)")
    except Exception as e:
        print(f"  [ERROR] Gemini test failed: {e}")

# -------------------------------------------------------------
# 6. NEO4J CLOUD DATABASE
# -------------------------------------------------------------
print("\n[6/6] Testing NEO4J Connection...")
neo4j_uri = os.getenv("NEO4J_URI", "")
neo4j_user = os.getenv("NEO4J_USERNAME", "")
neo4j_pass = os.getenv("NEO4J_PASSWORD", "")
if not neo4j_uri or not neo4j_pass:
    print("  -> Neo4j credentials incomplete in .env")
else:
    try:
        from neo4j import GraphDatabase
        t0 = time.time()
        db_name = os.getenv("NEO4J_DATABASE", "2f55ecc7")
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
        with driver.session(database=db_name) as session:
            result = session.run("RETURN 1 as test")
            val = result.single()["test"]
        driver.close()
        ms = (time.time() - t0) * 1000
        print(f"  [SUCCESS] Neo4j AuraDB Connection is VALID! Latency: {ms:.1f}ms")
        print(f"    Target Database: '{db_name}' | Query 'RETURN 1' evaluated to {val}")
    except ImportError:
        print("  [INFO] 'neo4j' Python driver not installed in current environment; install via 'pip install neo4j' if needed.")
    except Exception as e:
        print(f"  [INFO] Neo4j connection attempt to {neo4j_uri}: {str(e)[:100]}")

print("\n" + "=" * 70)
print("  VALIDATION COMPLETE")
print("=" * 70)
