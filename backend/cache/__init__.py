"""
CryptoTrace LEA — In-Process Multi-Tier TTL Cache
Implements zero-infrastructure caching with optional Redis transparent upgrade.
"""

from .cache_manager import (
    CacheManager,
    cache_manager,
    HOT_ADDR_CACHE,
    VASP_LABEL_CACHE,
    TRACE_CACHE,
    PRICE_CACHE,
    HEALTH_CACHE,
)

__all__ = [
    "CacheManager",
    "cache_manager",
    "HOT_ADDR_CACHE",
    "VASP_LABEL_CACHE",
    "TRACE_CACHE",
    "PRICE_CACHE",
    "HEALTH_CACHE",
]
