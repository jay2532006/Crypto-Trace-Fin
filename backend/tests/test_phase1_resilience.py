"""
CryptoTrace LEA — Phase 1 Resilience & Caching Tests (§11.2)
Per-item unit tests (positive and negative) for every Phase 1 change:

Items covered:
  §8.1 — Cascading provider failover (fetch_with_failover waterfall, never synthesize)
  §8.2 — Circuit breaker per provider (ProviderCircuitBreaker 3-failure open, 60s half-open)
  §8.3 — In-process TTL cache (cachetools 5 tiers, cold vs warm byte-identical trace, /api/v1/system/cache-stats)
  §8.4 — Persistent dedup fix (seed processed_bulletin_hashes from SQLite on __init__)
  §1.8 — Retry queue with backoff (_fetch_hop_with_retry, max 3 retries, exponential backoff)
"""

import os
import sys
import time
import json
import asyncio
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from backend.adapters.provider_manager import (
    ProviderCircuitBreaker,
    fetch_with_failover,
    fetch_with_failover_sync,
    get_providers_for_chain,
    provider_circuit_breaker,
)
from backend.cache.cache_manager import (
    cache_manager,
    HOT_ADDR_CACHE,
    VASP_LABEL_CACHE,
    TRACE_CACHE,
    PRICE_CACHE,
    HEALTH_CACHE,
)
from backend.db.database import canonical_db
from backend.adapters.sahyog_adapter import SAHYOGAdapter
from backend.tracing.trace_engine import BoundedTracer, TraceConstraints, MAX_HOP_RETRIES


# ===========================================================================
# §8.1 — Cascading Provider Failover Tests
# ===========================================================================
class TestCascadingProviderFailover(unittest.TestCase):
    """
    §8.1: fetch_with_failover waterfall:
    Primary -> Fallback 1 -> Fallback 2 -> Circuit-break to empty / raise (never synthesize).
    """

    def setUp(self):
        self.breaker = ProviderCircuitBreaker(failure_threshold=3, open_duration_s=60.0)

    def test_primary_fails_fallback_succeeds_async(self):
        """Positive test: Primary provider returns 500; fallback succeeds with expected data."""
        providers = ["https://rpc-primary.dummy", "https://rpc-fallback.dummy"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "1", "result": [{"hash": "0x123"}]}

        async def run_test():
            with patch("httpx.AsyncClient.get") as mock_get:
                # Primary fails with 500 error, Fallback succeeds with 200
                err_resp = MagicMock()
                err_resp.status_code = 500
                err_resp.raise_for_status.side_effect = Exception("HTTP 500 Server Error")

                mock_get.side_effect = [err_resp, mock_response]

                data = await fetch_with_failover(
                    providers, path="/txs", timeout=2, circuit_breaker=self.breaker
                )
                self.assertEqual(data["status"], "1")
                self.assertEqual(data["result"][0]["hash"], "0x123")
                self.assertEqual(mock_get.call_count, 2)

        asyncio.run(run_test())

    def test_rate_limit_429_skips_to_next_fallback(self):
        """Positive test: 429 on primary triggers failover to fallback without crashing."""
        providers = ["https://rpc-primary.dummy", "https://rpc-fallback.dummy"]
        mock_429 = MagicMock()
        mock_429.status_code = 429

        mock_ok = MagicMock()
        mock_ok.status_code = 200
        mock_ok.json.return_value = {"recovered": True}

        async def run_test():
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_get.side_effect = [mock_429, mock_ok]
                data = await fetch_with_failover(
                    providers, path="/txs", timeout=2, circuit_breaker=self.breaker
                )
                self.assertTrue(data.get("recovered"))
                # Primary URL recorded a failure
                self.assertEqual(self.breaker._failures.get("https://rpc-primary.dummy"), 1)

        asyncio.run(run_test())

    def test_exhaustion_raises_exception_never_synthesizes_fake_data(self):
        """Negative test: When all providers fail, raises Exception — NEVER fabricates fake hops."""
        providers = ["https://rpc-1.dummy", "https://rpc-2.dummy"]

        async def run_test():
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_get.side_effect = Exception("Connection Refused")
                with self.assertRaises(Exception):
                    await fetch_with_failover(
                        providers, path="/txs", timeout=2, circuit_breaker=self.breaker
                    )

        asyncio.run(run_test())

    def test_sync_failover_matches_async_behavior(self):
        """Verify synchronous fetch_with_failover_sync works seamlessly."""
        providers = ["https://rpc-primary.dummy", "https://rpc-fallback.dummy"]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"sync_ok": True}

        with patch("httpx.Client.get") as mock_get:
            mock_get.side_effect = [Exception("Timeout"), mock_resp]
            data = fetch_with_failover_sync(
                providers, path="/txs", timeout=2, circuit_breaker=self.breaker
            )
            self.assertTrue(data.get("sync_ok"))


# ===========================================================================
# §8.2 — Circuit Breaker Tests
# ===========================================================================
class TestProviderCircuitBreaker(unittest.TestCase):
    """
    §8.2: ProviderCircuitBreaker opens after 3 failures, half-opens after 60s.
    """

    def setUp(self):
        self.breaker = ProviderCircuitBreaker(failure_threshold=3, open_duration_s=0.2)

    def test_breaker_opens_after_three_failures(self):
        """Breaker is closed for 1 and 2 failures, opens on 3rd failure."""
        url = "https://flaky-rpc.dummy"
        self.assertFalse(self.breaker.is_open(url))

        self.breaker.record_failure(url)
        self.assertFalse(self.breaker.is_open(url))

        self.breaker.record_failure(url)
        self.assertFalse(self.breaker.is_open(url))

        self.breaker.record_failure(url)
        self.assertTrue(self.breaker.is_open(url), "Breaker must open after 3 consecutive failures")

    def test_breaker_half_open_after_duration_and_closes_on_success(self):
        """Breaker half-opens after open_duration_s and closes immediately on success."""
        url = "https://recovering-rpc.dummy"
        for _ in range(3):
            self.breaker.record_failure(url)
        self.assertTrue(self.breaker.is_open(url))

        # Wait for timeout to expire -> half-open
        time.sleep(0.25)
        self.assertFalse(self.breaker.is_open(url), "Breaker must half-open after open duration expires")

        # Trial probe succeeds -> circuit closes
        self.breaker.record_success(url)
        self.assertFalse(self.breaker.is_open(url))
        self.assertEqual(self.breaker._failures.get(url, 0), 0)

    def test_failover_skips_open_breaker_without_request(self):
        """Negative test: failover skips a provider whose breaker is open without querying it."""
        url_bad = "https://broken-rpc.dummy"
        url_good = "https://working-rpc.dummy"
        for _ in range(3):
            self.breaker.record_failure(url_bad)

        self.assertTrue(self.breaker.is_open(url_bad))

        mock_ok = MagicMock()
        mock_ok.status_code = 200
        mock_ok.json.return_value = {"ok": 1}

        with patch("httpx.Client.get") as mock_get:
            mock_get.return_value = mock_ok
            res = fetch_with_failover_sync([url_bad, url_good], "/test", circuit_breaker=self.breaker)
            self.assertEqual(res["ok"], 1)
            # Only url_good should have been called, bad skipped
            self.assertEqual(mock_get.call_count, 1)


# ===========================================================================
# §8.3 — In-Process TTL Cache Tests
# ===========================================================================
class TestInProcessTTLCache(unittest.TestCase):
    """
    §8.3: cachetools.TTLCache 5 tiers, transparent read-through, /api/v1/system/cache-stats.
    """

    def setUp(self):
        cache_manager.clear_all()
        self.client = TestClient(app)

    def tearDown(self):
        cache_manager.clear_all()

    def test_five_cache_tiers_configuration(self):
        """Verify all 5 cache tiers exist with exact PRD maxsize and TTL specifications."""
        stats = cache_manager.get_stats()["caches"]

        # 1. HOT_ADDR_CACHE: maxsize=2000, ttl=300 (5 min)
        self.assertEqual(stats["hot_addr_cache"]["maxsize"], 2000)
        self.assertEqual(stats["hot_addr_cache"]["ttl_seconds"], 300)

        # 2. VASP_LABEL_CACHE: maxsize=500, ttl=3600 (1 hour)
        self.assertEqual(stats["vasp_label_cache"]["maxsize"], 500)
        self.assertEqual(stats["vasp_label_cache"]["ttl_seconds"], 3600)

        # 3. TRACE_CACHE: maxsize=200, ttl=1800 (30 min)
        self.assertEqual(stats["trace_cache"]["maxsize"], 200)
        self.assertEqual(stats["trace_cache"]["ttl_seconds"], 1800)

        # 4. PRICE_CACHE: maxsize=50, ttl=60 (1 min)
        self.assertEqual(stats["price_cache"]["maxsize"], 50)
        self.assertEqual(stats["price_cache"]["ttl_seconds"], 60)

        # 5. HEALTH_CACHE: maxsize=20, ttl=30 (30 sec)
        self.assertEqual(stats["health_cache"]["maxsize"], 20)
        self.assertEqual(stats["health_cache"]["ttl_seconds"], 30)

    def test_trace_cache_cold_vs_warm_byte_identical(self):
        """
        §11.3 Mandate: Cache must be transparent and read-through.
        Cold trace vs warm trace result JSON must be byte-identical.
        """
        tracer = BoundedTracer()
        start_addr = "0x71c8fb9284285741829e05e55099e0344d9f1091"
        case_id = "CR-2026-CACHE-TEST"

        # Cold trace (first execution)
        cold_res = tracer.trace(
            start_address=start_addr,
            chain="ETH",
            constraints=TraceConstraints(max_hops=3),
            case_id=case_id,
            mode="DEMO",
        )

        # Warm trace (cached execution)
        warm_res = tracer.trace(
            start_address=start_addr,
            chain="ETH",
            constraints=TraceConstraints(max_hops=3),
            case_id=case_id,
            mode="DEMO",
        )

        cold_json = json.dumps(cold_res, sort_keys=True)
        warm_json = json.dumps(warm_res, sort_keys=True)

        self.assertEqual(
            cold_json,
            warm_json,
            "§11.3: Cold and warm trace results must be byte-identical",
        )
        # Trace cache hit recorded
        self.assertGreaterEqual(cache_manager.stats["trace"]["hits"], 1)

    def test_cache_stats_api_endpoint(self):
        """GET /api/v1/system/cache-stats returns 200 with complete cache telemetry."""
        resp = self.client.get("/api/v1/system/cache-stats")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get("status"), "ok")
        data = body.get("data", {})
        self.assertIn("backend", data)
        self.assertIn("caches", data)
        self.assertIn("hot_addr_cache", data["caches"])
        self.assertIn("vasp_label_cache", data["caches"])
        self.assertIn("trace_cache", data["caches"])


# ===========================================================================
# §8.4 — Persistent Deduplication Tests
# ===========================================================================
class TestPersistentDeduplication(unittest.TestCase):
    """
    §8.4: Seed processed_bulletin_hashes from SQLite on __init__ to prevent data loss on restart.
    """

    def test_adapter_seeds_from_sqlite_on_init(self):
        """Positive test: existing SQLite hashes are seeded into processed_bulletin_hashes."""
        test_hash = f"test_hash_{int(time.time() * 1000)}"
        canonical_db.record_intake_dedupe(test_hash, "SAHYOG", "BULLETIN-SEED-TEST")

        # Create fresh adapter instance — simulating server restart
        fresh_adapter = SAHYOGAdapter()
        self.assertIn(
            test_hash,
            fresh_adapter.processed_bulletin_hashes,
            "§8.4: Fresh adapter instance must seed hashes from SQLite on __init__",
        )

    def test_duplicate_bulletin_rejected_across_process_restart(self):
        """Negative test: Bulletin ingested once is rejected by fresh adapter instance on reboot."""
        b_id = f"SAHYOG-REBOOT-{int(time.time() * 1000)}"
        bulletin = {
            "bulletin_id": b_id,
            "title": "Reboot Resilience Test",
            "agency": "CBI_CYBER_CRIME",
            "crime_type": "INVESTMENT_FRAUD",
            "wallets": ["0x28c6c06298d514db089934071355e5743bf21d60"],
        }

        # 1. Ingest with first adapter instance
        adapter_pre = SAHYOGAdapter()
        res1 = adapter_pre.ingest_bulletin(bulletin)
        self.assertEqual(res1["status"], "INGESTED")

        # 2. Simulate process restart by instantiating adapter_post
        adapter_post = SAHYOGAdapter()
        res2 = adapter_post.ingest_bulletin(bulletin)
        self.assertEqual(
            res2["status"],
            "ALREADY_EXISTS",
            "§8.4: Fresh instance must reject already ingested bulletin without data loss",
        )


# ===========================================================================
# §1.8 — Retry Queue with Exponential Backoff Tests
# ===========================================================================
class TestRetryQueueWithBackoff(unittest.TestCase):
    """
    §1.8: _fetch_hop_with_retry: max 3 retries, exponential backoff (2^attempt), never synthesize.
    """

    def test_retry_succeeds_on_second_attempt_async(self):
        """Positive test: fails on attempt 0, succeeds on attempt 1 with exponential backoff."""
        tracer = BoundedTracer()

        async def run_test():
            with patch("backend.tracing.trace_engine.fetch_with_failover") as mock_fetch:
                mock_fetch.side_effect = [
                    Exception("Transient 503"),
                    [{"tx_hash": "0xabc", "value": 1.5}],
                ]
                with patch("asyncio.sleep") as mock_sleep:
                    res = await tracer._fetch_hop_with_retry("0xaddress", "ETH")
                    self.assertEqual(len(res), 1)
                    self.assertEqual(res[0]["tx_hash"], "0xabc")
                    self.assertEqual(mock_fetch.call_count, 2)
                    mock_sleep.assert_called_once_with(1)  # 2^0 = 1s

        asyncio.run(run_test())

    def test_retry_exhaustion_returns_empty_never_synthesizes_fake_hops(self):
        """Negative test: all 3 attempts fail; returns [] (marked incomplete), never fake hops."""
        tracer = BoundedTracer()

        async def run_test():
            with patch("backend.tracing.trace_engine.fetch_with_failover") as mock_fetch:
                mock_fetch.side_effect = Exception("Persistent Outage")
                with patch("asyncio.sleep") as mock_sleep:
                    res = await tracer._fetch_hop_with_retry("0xdead_address", "ETH")
                    self.assertEqual(res, [], "Must return empty list upon exhaustion, never synthesize")
                    self.assertEqual(mock_fetch.call_count, MAX_HOP_RETRIES)
                    self.assertEqual(mock_sleep.call_count, MAX_HOP_RETRIES - 1)

        asyncio.run(run_test())

    def test_sync_retry_exhaustion_returns_empty(self):
        """Negative test (sync): _fetch_hop_with_retry_sync exhausts 3 attempts and returns []."""
        tracer = BoundedTracer()

        with patch("backend.tracing.trace_engine.fetch_with_failover_sync") as mock_fetch:
            mock_fetch.side_effect = Exception("Network Down")
            with patch("time.sleep") as mock_sleep:
                res = tracer._fetch_hop_with_retry_sync("0xdead_sync", "ETH")
                self.assertEqual(res, [])
                self.assertEqual(mock_fetch.call_count, MAX_HOP_RETRIES)
                self.assertEqual(mock_sleep.call_count, MAX_HOP_RETRIES - 1)


if __name__ == "__main__":
    unittest.main()
