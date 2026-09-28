# scripts/mock_ncrp_gateway.py
"""
CryptoTrace LEA - Mock Government NCRP & SAHYOG Sandbox Gateway
Simulates outbound government dispatch of cybercrime complaints (from NCRP portal)
and inter-agency intelligence bulletins (from MHA/I4C SAHYOG).
Dispatches payloads directly to the CryptoTrace LEA intake API.
"""

import time
import requests
import sys
from datetime import datetime, timezone

from backend.auth.jwt_handler import create_access_token

DEFAULT_TARGET = "http://localhost:8765/api/v1/intake"

def get_service_token():
    return create_access_token({
        "username": "mock_ncrp_gateway_service",
        "role": "INTEGRATION_SERVICE",
        "unit": "MHA / I4C National Gateway Gateway Sandbox",
    })

def emit_mock_ncrp_complaint(target_url: str = DEFAULT_TARGET):
    token = get_service_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    ack = f"NCRP-SANDBOX-{int(time.time())}"
    payload = {
        "ncrp_ack_number": ack,
        "chain": "TRON",
        "suspect_wallet": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
        "reported_amount": 54200.0,
        "complainant_name": "R. K. Verma",
        "complaint_text": "Victim reported loss of 54,200 USDT to Telegram fake investment task scam.",
        "fir_number": f"FIR-2026/CYBER/{int(time.time()) % 1000}",
    }
    
    print(f"[*] Emitting NCRP complaint {ack} to {target_url}/ncrp/complaint...")
    try:
        resp = requests.post(f"{target_url}/ncrp/complaint", json=payload, headers=headers, timeout=5)
        print(f"[+] Response ({resp.status_code}):", resp.json())
        return resp.json()
    except Exception as e:
        print(f"[-] Emission failed (is backend running?): {e}")
        return None

def emit_mock_sahyog_bulletin(target_url: str = DEFAULT_TARGET):
    token = get_service_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    b_id = f"SAHYOG-I4C-BULLETIN-{int(time.time())}"
    payload = {
        "bulletin_id": b_id,
        "title": "Operation RedPeel - Syndicate Laundering Alert",
        "agency": "I4C_DELHI_CENTRAL",
        "crime_type": "SYNDICATE_MULE_NETWORK",
        "description": "Cross-border mule network detected funneling funds through TRON and Ethereum corridors.",
        "wallets": [
            "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
            "0x28c6c06298d514db089934071355e5743bf21d60"
        ]
    }
    
    print(f"[*] Emitting SAHYOG bulletin {b_id} to {target_url}/sahyog/bulletin...")
    try:
        resp = requests.post(f"{target_url}/sahyog/bulletin", json=payload, headers=headers, timeout=5)
        print(f"[+] Response ({resp.status_code}):", resp.json())
        return resp.json()
    except Exception as e:
        print(f"[-] Emission failed: {e}")
        return None

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET
    print("=== CryptoTrace LEA - Mock Government Gateway Dispatcher ===")
    emit_mock_ncrp_complaint(url)
    time.sleep(1)
    emit_mock_sahyog_bulletin(url)
