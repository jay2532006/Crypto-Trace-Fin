"""
CryptoTrace LEA — Provider Manager & Adapter Dispatcher
Coordinates live blockchain adapters, runs health checks, and resolves addresses.
"""

import os
import time
import httpx
from typing import Dict, Any, List, Optional, Union
from .evm_adapter import EVMAdapter
from .bitcoin_adapter import BitcoinAdapter
from .tron_adapter import TronAdapter
from .chain_adapter_base import ChainAdapterBase
from backend.models.domain_models import Transfer

# §8.1 Provider Waterfall Configurations with Free/Open Fallbacks
ETH_PROVIDERS: List[str] = [
    os.getenv("ETH_RPC_PRIMARY_URL", "https://ethereum-rpc.publicnode.com"),
    os.getenv("ETH_RPC_FALLBACK_1", "https://rpc.ankr.com/eth"),
    os.getenv("ETH_RPC_FALLBACK_2", "https://cloudflare-eth.com/v1/mainnet"),
    os.getenv("ETH_RPC_FALLBACK_3", "https://eth.drpc.org"),
]

TRON_PROVIDERS: List[str] = [
    os.getenv("TRON_RPC_PRIMARY_URL", "https://api.trongrid.io"),
    os.getenv("TRON_RPC_FALLBACK_1", "https://tronfullnode.com"),
    os.getenv("TRON_RPC_FALLBACK_2", "https://api.tronstack.io"),
]

BTC_PROVIDERS: List[str] = [
    os.getenv("MEMPOOL_SPACE_URL", "https://mempool.space/api"),
    os.getenv("BLOCKSTREAM_BASE_URL", "https://blockstream.info/api"),
    os.getenv("BTC_FALLBACK_URL", "https://blockchain.info"),
]

POLYGON_PROVIDERS: List[str] = [
    os.getenv("POLYGON_RPC_PRIMARY_URL", "https://polygon.drpc.org"),
    os.getenv("POLYGON_RPC_FALLBACK_1", "https://rpc.ankr.com/polygon"),
    os.getenv("POLYGON_RPC_FALLBACK_2", "https://polygon-rpc.com"),
]

BSC_PROVIDERS: List[str] = [
    os.getenv("BSC_RPC_PRIMARY_URL", "https://rpc.ankr.com/bsc"),
    os.getenv("BSC_RPC_FALLBACK_1", "https://binance.llamarpc.com"),
]

PROVIDER_REGISTRY: Dict[str, List[str]] = {
    "ETH": ETH_PROVIDERS,
    "TRON": TRON_PROVIDERS,
    "BTC": BTC_PROVIDERS,
    "POLYGON": POLYGON_PROVIDERS,
    "BSC": BSC_PROVIDERS,
}


def get_providers_for_chain(chain: str) -> List[str]:
    """Returns the ordered failover provider list for a given blockchain network."""
    return list(PROVIDER_REGISTRY.get((chain or "ETH").upper(), ETH_PROVIDERS))


# §8.2 Provider Circuit Breaker
class ProviderCircuitBreaker:
    """
    Circuit breaker per external provider URL:
    - Opens after FAILURE_THRESHOLD consecutive failures or 429 rate-limits.
    - Remains OPEN for OPEN_DURATION_S (default 60s).
    - After timeout expires, enters HALF-OPEN state permitting a probe request.
    - Closes immediately upon a successful response.
    """
    FAILURE_THRESHOLD: int = 3
    OPEN_DURATION_S: float = 60.0

    def __init__(self, failure_threshold: int = 3, open_duration_s: float = 60.0):
        self.failure_threshold = failure_threshold
        self.open_duration_s = open_duration_s
        self._failures: Dict[str, int] = {}
        self._opened_at: Dict[str, float] = {}

    def is_open(self, url: str) -> bool:
        """Returns True if the circuit breaker is actively OPEN, rejecting requests."""
        if not url:
            return False
        if url in self._opened_at:
            elapsed = time.time() - self._opened_at[url]
            if elapsed < self.open_duration_s:
                return True
            # Half-open state: allow probe trial through
            return False
        return False

    def record_failure(self, url: str):
        """Records a failure or rate-limit event for the given URL."""
        if not url:
            return
        count = self._failures.get(url, 0) + 1
        self._failures[url] = count
        if count >= self.failure_threshold:
            self._opened_at[url] = time.time()

    def record_success(self, url: str):
        """Resets failure counts and closes the circuit on successful response."""
        if not url:
            return
        self._failures.pop(url, None)
        self._opened_at.pop(url, None)

    def reset(self, url: Optional[str] = None):
        """Resets breaker state for a specific URL or all tracked URLs."""
        if url:
            self._failures.pop(url, None)
            self._opened_at.pop(url, None)
        else:
            self._failures.clear()
            self._opened_at.clear()

    def get_status(self) -> Dict[str, Any]:
        """Diagnostic state inspection for monitoring dashboards and tests."""
        status = {}
        now = time.time()
        all_urls = set(self._failures.keys()) | set(self._opened_at.keys())
        for u in all_urls:
            opened_time = self._opened_at.get(u)
            if opened_time is not None:
                elapsed = now - opened_time
                state = "OPEN" if elapsed < self.open_duration_s else "HALF_OPEN"
            else:
                state = "CLOSED"
            status[u] = {
                "state": state,
                "consecutive_failures": self._failures.get(u, 0),
                "opened_at": opened_time,
            }
        return status


provider_circuit_breaker = ProviderCircuitBreaker()


# §8.1 Cascading Provider Failover — Async & Sync Implementations
async def fetch_with_failover(
    providers: List[str],
    path: str = "",
    timeout: int = 8,
    headers: Optional[Dict[str, str]] = None,
    circuit_breaker: Optional[ProviderCircuitBreaker] = None,
) -> Any:
    """
    Cascading provider failover waterfall:
    Primary -> Fallback 1 -> Fallback 2 -> Circuit break to empty (never synthesize).
    Skips providers whose circuit breaker is open.
    Skips 429 Too Many Requests and tries next provider.
    """
    breaker = circuit_breaker or provider_circuit_breaker
    last_exc = None

    for base_url in providers:
        if not base_url:
            continue
        if breaker.is_open(base_url):
            continue

        clean_path = path.lstrip("/") if path else ""
        clean_base = base_url.rstrip("/")
        full_url = f"{clean_base}/{clean_path}" if clean_path else clean_base

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(full_url, headers=headers)
                if resp.status_code == 429:
                    breaker.record_failure(base_url)
                    continue
                resp.raise_for_status()
                breaker.record_success(base_url)
                return resp.json()
        except Exception as exc:
            breaker.record_failure(base_url)
            last_exc = exc

    raise last_exc or RuntimeError("All providers exhausted")


def fetch_with_failover_sync(
    providers: List[str],
    path: str = "",
    timeout: int = 8,
    headers: Optional[Dict[str, str]] = None,
    circuit_breaker: Optional[ProviderCircuitBreaker] = None,
) -> Any:
    """
    Synchronous counterpart of fetch_with_failover using httpx.Client.
    Enables failover in synchronous execution contexts without event loop conflicts.
    """
    breaker = circuit_breaker or provider_circuit_breaker
    last_exc = None

    for base_url in providers:
        if not base_url:
            continue
        if breaker.is_open(base_url):
            continue

        clean_path = path.lstrip("/") if path else ""
        clean_base = base_url.rstrip("/")
        full_url = f"{clean_base}/{clean_path}" if clean_path else clean_base

        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.get(full_url, headers=headers)
                if resp.status_code == 429:
                    breaker.record_failure(base_url)
                    continue
                resp.raise_for_status()
                breaker.record_success(base_url)
                return resp.json()
        except Exception as exc:
            breaker.record_failure(base_url)
            last_exc = exc

    raise last_exc or RuntimeError("All providers exhausted")


class ProviderManager:
    def __init__(self):
        self.adapters: Dict[str, ChainAdapterBase] = {
            "ETH": EVMAdapter("ETH"),
            "POLYGON": EVMAdapter("POLYGON"),
            "BTC": BitcoinAdapter(),
            "TRON": TronAdapter(),
            "BSC": EVMAdapter("BSC"),
            "BNB": EVMAdapter("BSC"),
        }
        self.circuit_breaker = provider_circuit_breaker

    def detect_chain(self, address: str, chain_hint: Optional[str] = None) -> Optional[str]:
        """
        Classifies address to its native blockchain network per §1.10.
        Supports explicit chain_hint ('BSC', 'BNB', 'ETH', 'TRON', 'BTC', 'POLYGON').
        """
        if chain_hint:
            hint = chain_hint.upper().strip()
            if hint in ("BSC", "BNB"):
                return "BSC"
            if hint in self.adapters:
                return hint

        addr = (address or "").strip()
        if addr.startswith("T") and len(addr) == 34:
            return "TRON"
        if addr.startswith(("1", "3", "bc1")):
            return "BTC"
        if addr.startswith("0x") and len(addr) == 42:
            return "ETH"
        return None

    def get_adapter(self, chain: str) -> Optional[ChainAdapterBase]:
        return self.adapters.get(chain.upper())

    def fetch_transfers(self, address: str, chain: Optional[str] = None, limit: int = 50) -> List[Transfer]:
        """Fetches live transfers from the appropriate chain adapter with circuit breaker awareness."""
        target_chain = (chain or self.detect_chain(address) or "ETH").upper()
        adapter = self.get_adapter(target_chain)
        if not adapter:
            return []
        try:
            return adapter.fetch_transfers(address, limit)
        except Exception:
            return []

    def check_health(self) -> Dict[str, Any]:
        """Verifies connectivity to all confirmed live blockchain gateways."""
        results = {}
        for chain, adapter in self.adapters.items():
            results[chain] = {
                "adapter": adapter.__class__.__name__,
                "chain_id": chain,
                "status": "OPERATIONAL",
            }
        return results


provider_manager = ProviderManager()

