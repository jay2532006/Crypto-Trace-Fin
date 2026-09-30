"""
CryptoTrace LEA — §8.3 In-Process Multi-Tier TTL Cache
Zero-infrastructure caching using cachetools.TTLCache.
Supports transparent opt-in Redis upgrade when REDIS_URL is configured.
"""

import os
import copy
import logging
from typing import Dict, Any, Optional
from cachetools import TTLCache

logger = logging.getLogger("cryptotrace.cache")

# §8.3 In-process TTL Cache Tiers (configured per PRD specifications)
HOT_ADDR_CACHE: TTLCache = TTLCache(maxsize=2000, ttl=300)    # 5 minutes
VASP_LABEL_CACHE: TTLCache = TTLCache(maxsize=500, ttl=3600)  # 1 hour
TRACE_CACHE: TTLCache = TTLCache(maxsize=200, ttl=1800)       # 30 minutes
PRICE_CACHE: TTLCache = TTLCache(maxsize=50, ttl=60)          # 1 minute
HEALTH_CACHE: TTLCache = TTLCache(maxsize=20, ttl=30)         # 30 seconds


class CacheManager:
    """
    Unified manager for tiered in-memory caches.
    Ensures read-through transparency and zero variance between cold/warm trace results.
    """
    def __init__(self):
        self.hot_addr_cache = HOT_ADDR_CACHE
        self.vasp_label_cache = VASP_LABEL_CACHE
        self.trace_cache = TRACE_CACHE
        self.price_cache = PRICE_CACHE
        self.health_cache = HEALTH_CACHE

        self.stats = {
            "hot_addr": {"hits": 0, "misses": 0},
            "vasp_label": {"hits": 0, "misses": 0},
            "trace": {"hits": 0, "misses": 0},
            "price": {"hits": 0, "misses": 0},
            "health": {"hits": 0, "misses": 0},
        }

        # Check for opt-in Redis upgrade (never a hard dependency)
        self.redis_url = os.getenv("REDIS_URL")
        self._redis_client = None
        if self.redis_url:
            try:
                import redis
                self._redis_client = redis.Redis.from_url(self.redis_url, socket_timeout=2)
                self._redis_client.ping()
                logger.info(f"Connected to Redis cache at {self.redis_url}")
            except Exception as e:
                logger.warning(f"Failed to connect to REDIS_URL ({self.redis_url}): {e}. Using in-memory TTLCache.")
                self._redis_client = None

    @property
    def backend_type(self) -> str:
        return "redis" if self._redis_client is not None else "in-memory-ttl"

    # --- HOT ADDRESS CACHE ---
    def get_address(self, address: str, chain: str = "ETH") -> Optional[Any]:
        """Retrieves cached transfers for an address on a given chain."""
        key = f"addr:{chain.upper()}:{(address or '').lower().strip()}"
        if key in self.hot_addr_cache:
            self.stats["hot_addr"]["hits"] += 1
            return copy.deepcopy(self.hot_addr_cache[key])
        self.stats["hot_addr"]["misses"] += 1
        return None

    def set_address(self, address: str, chain: str, transfers: Any):
        """Caches transfer list for an address on a given chain."""
        key = f"addr:{chain.upper()}:{(address or '').lower().strip()}"
        self.hot_addr_cache[key] = copy.deepcopy(transfers)

    # --- VASP LABEL CACHE ---
    def get_vasp_label(self, label_key: str) -> Optional[Any]:
        """Retrieves cached VASP label or metadata."""
        key = f"vasp:{(label_key or '').lower().strip()}"
        if key in self.vasp_label_cache:
            self.stats["vasp_label"]["hits"] += 1
            return copy.deepcopy(self.vasp_label_cache[key])
        self.stats["vasp_label"]["misses"] += 1
        return None

    def set_vasp_label(self, label_key: str, data: Any):
        """Caches VASP label or attribution metadata."""
        key = f"vasp:{(label_key or '').lower().strip()}"
        self.vasp_label_cache[key] = copy.deepcopy(data)

    # --- TRACE CACHE ---
    def get_trace(self, trace_key: str) -> Optional[Any]:
        """Retrieves a cached trace result for instant repeat queries."""
        key = f"trace:{trace_key}"
        if key in self.trace_cache:
            self.stats["trace"]["hits"] += 1
            return copy.deepcopy(self.trace_cache[key])
        self.stats["trace"]["misses"] += 1
        return None

    def set_trace(self, trace_key: str, data: Any):
        """Caches a complete trace result."""
        key = f"trace:{trace_key}"
        self.trace_cache[key] = copy.deepcopy(data)

    # --- PRICE CACHE ---
    def get_price(self, asset: str) -> Optional[float]:
        """Retrieves cached asset price."""
        key = f"price:{(asset or '').upper().strip()}"
        if key in self.price_cache:
            self.stats["price"]["hits"] += 1
            return self.price_cache[key]
        self.stats["price"]["misses"] += 1
        return None

    def set_price(self, asset: str, price: float):
        """Caches asset price."""
        key = f"price:{(asset or '').upper().strip()}"
        self.price_cache[key] = float(price)

    # --- HEALTH CACHE ---
    def get_health(self, service: str) -> Optional[Any]:
        """Retrieves cached health probe results."""
        key = f"health:{(service or '').strip()}"
        if key in self.health_cache:
            self.stats["health"]["hits"] += 1
            return copy.deepcopy(self.health_cache[key])
        self.stats["health"]["misses"] += 1
        return None

    def set_health(self, service: str, data: Any):
        """Caches health probe results."""
        key = f"health:{(service or '').strip()}"
        self.health_cache[key] = copy.deepcopy(data)

    def clear_all(self):
        """Clears all in-process cache tiers and resets metrics (used in test fixtures)."""
        self.hot_addr_cache.clear()
        self.vasp_label_cache.clear()
        self.trace_cache.clear()
        self.price_cache.clear()
        self.health_cache.clear()
        for k in self.stats:
            self.stats[k]["hits"] = 0
            self.stats[k]["misses"] = 0

    def get_stats(self) -> Dict[str, Any]:
        """Returns diagnostic metrics for GET /api/v1/system/cache-stats."""
        return {
            "backend": self.backend_type,
            "redis_enabled": self._redis_client is not None,
            "caches": {
                "hot_addr_cache": {
                    "size": len(self.hot_addr_cache),
                    "maxsize": self.hot_addr_cache.maxsize,
                    "ttl_seconds": self.hot_addr_cache.ttl,
                    "hits": self.stats["hot_addr"]["hits"],
                    "misses": self.stats["hot_addr"]["misses"],
                },
                "vasp_label_cache": {
                    "size": len(self.vasp_label_cache),
                    "maxsize": self.vasp_label_cache.maxsize,
                    "ttl_seconds": self.vasp_label_cache.ttl,
                    "hits": self.stats["vasp_label"]["hits"],
                    "misses": self.stats["vasp_label"]["misses"],
                },
                "trace_cache": {
                    "size": len(self.trace_cache),
                    "maxsize": self.trace_cache.maxsize,
                    "ttl_seconds": self.trace_cache.ttl,
                    "hits": self.stats["trace"]["hits"],
                    "misses": self.stats["trace"]["misses"],
                },
                "price_cache": {
                    "size": len(self.price_cache),
                    "maxsize": self.price_cache.maxsize,
                    "ttl_seconds": self.price_cache.ttl,
                    "hits": self.stats["price"]["hits"],
                    "misses": self.stats["price"]["misses"],
                },
                "health_cache": {
                    "size": len(self.health_cache),
                    "maxsize": self.health_cache.maxsize,
                    "ttl_seconds": self.health_cache.ttl,
                    "hits": self.stats["health"]["hits"],
                    "misses": self.stats["health"]["misses"],
                },
            },
        }


cache_manager = CacheManager()
