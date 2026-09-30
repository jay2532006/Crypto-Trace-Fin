"""
TraceX Provider Health Monitor
Pings all external data providers in parallel and returns live latency + status.
"""

import time
import os
import requests
import concurrent.futures
from typing import Dict, Any

TIMEOUT = 5  # seconds per probe


def _probe_etherscan() -> Dict[str, Any]:
    t0 = time.time()
    key = os.getenv("ETHERSCAN_API_KEY", "")
    url = f"https://api.etherscan.io/v2/api?chainid=1&module=stats&action=ethsupply&apikey={key}"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        latency = round((time.time() - t0) * 1000)
        ok = r.status_code == 200 and r.json().get("status") == "1"
        return {
            "provider": "Etherscan",
            "chain": "ETH",
            "status": "ONLINE" if ok else "DEGRADED",
            "latency_ms": latency,
            "key_configured": bool(key),
        }
    except Exception as e:
        return {
            "provider": "Etherscan",
            "chain": "ETH",
            "status": "OFFLINE",
            "latency_ms": None,
            "error": str(e)[:80],
        }


def _probe_blockstream() -> Dict[str, Any]:
    t0 = time.time()
    try:
        r = requests.get("https://blockstream.info/api/blocks/tip/height", timeout=TIMEOUT)
        latency = round((time.time() - t0) * 1000)
        return {
            "provider": "Blockstream",
            "chain": "BTC",
            "status": "ONLINE" if r.status_code == 200 else "DEGRADED",
            "latency_ms": latency,
            "block_height": r.text.strip() if r.status_code == 200 else None,
        }
    except Exception as e:
        return {
            "provider": "Blockstream",
            "chain": "BTC",
            "status": "OFFLINE",
            "latency_ms": None,
            "error": str(e)[:80],
        }


def _probe_trongrid() -> Dict[str, Any]:
    t0 = time.time()
    key = os.getenv("TRONGRID_API_KEY", "")
    headers = {"TRON-PRO-API-KEY": key} if key else {}
    try:
        r = requests.get(
            "https://api.trongrid.io/v1/accounts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
            headers=headers,
            timeout=TIMEOUT,
        )
        latency = round((time.time() - t0) * 1000)
        return {
            "provider": "TronGrid",
            "chain": "TRON",
            "status": "ONLINE" if r.status_code == 200 else "DEGRADED",
            "latency_ms": latency,
            "key_configured": bool(key),
        }
    except Exception as e:
        return {
            "provider": "TronGrid",
            "chain": "TRON",
            "status": "OFFLINE",
            "latency_ms": None,
            "error": str(e)[:80],
        }


def _probe_coingecko() -> Dict[str, Any]:
    t0 = time.time()
    try:
        r = requests.get("https://api.coingecko.com/api/v3/ping", timeout=TIMEOUT)
        latency = round((time.time() - t0) * 1000)
        return {
            "provider": "CoinGecko",
            "type": "Price Feed",
            "status": "ONLINE" if r.status_code == 200 else "DEGRADED",
            "latency_ms": latency,
        }
    except Exception as e:
        return {
            "provider": "CoinGecko",
            "type": "Price Feed",
            "status": "OFFLINE",
            "latency_ms": None,
            "error": str(e)[:80],
        }


def _probe_chainabuse() -> Dict[str, Any]:
    t0 = time.time()
    key = os.getenv("CHAINABUSE_API_KEY", "")
    try:
        r = requests.get(
            "https://api.chainabuse.com/v0/reports?address=0x0&limit=1",
            timeout=TIMEOUT,
            auth=(key, "") if key else None,
        )
        latency = round((time.time() - t0) * 1000)
        return {
            "provider": "Chainabuse",
            "type": "Fraud Reports",
            "status": "ONLINE" if r.status_code in (200, 404) else "DEGRADED",
            "latency_ms": latency,
            "key_configured": bool(key),
        }
    except Exception as e:
        return {
            "provider": "Chainabuse",
            "type": "Fraud Reports",
            "status": "OFFLINE",
            "latency_ms": None,
            "error": str(e)[:80],
        }


def _probe_ofac() -> Dict[str, Any]:
    try:
        import engine.ofac_sanctions as ofac_mod
        registry = getattr(ofac_mod, "OFAC_SDN_REGISTRY", {})
        last_refresh = getattr(ofac_mod, "_OFAC_LAST_REFRESH", None)
        return {
            "provider": "OFAC SDN",
            "type": "Sanctions",
            "status": "ACTIVE",
            "latency_ms": 0,
            "last_refresh": last_refresh or "static_seed",
            "address_count": len(registry),
        }
    except Exception as e:
        return {
            "provider": "OFAC SDN",
            "type": "Sanctions",
            "status": "DEGRADED",
            "error": str(e)[:80],
        }


def check_all_providers() -> Dict[str, Any]:
    """Run all provider health probes in parallel."""
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            "etherscan": pool.submit(_probe_etherscan),
            "blockstream": pool.submit(_probe_blockstream),
            "trongrid": pool.submit(_probe_trongrid),
            "coingecko": pool.submit(_probe_coingecko),
            "chainabuse": pool.submit(_probe_chainabuse),
            "ofac": pool.submit(_probe_ofac),
        }
        results = {}
        for name, fut in futures.items():
            try:
                results[name] = fut.result(timeout=TIMEOUT + 2)
            except Exception as e:
                results[name] = {"provider": name, "status": "TIMEOUT", "error": str(e)[:60]}

    all_statuses = [r.get("status") for r in results.values()]
    overall = (
        "OPERATIONAL"
        if all(s in ("ONLINE", "ACTIVE") for s in all_statuses)
        else ("DEGRADED" if any(s == "ONLINE" for s in all_statuses) else "OFFLINE")
    )

    return {
        "overall": overall,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "probe_duration_ms": round((time.time() - t0) * 1000),
        "providers": results,
    }
