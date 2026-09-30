"""
CryptoTrace LEA — System Diagnostic & Status Routes
Endpoints:
- GET /api/v1/system/cache-stats (Surfaces multi-tier cache telemetry per §8.3)
"""

from typing import Dict, Any
from fastapi import APIRouter
from backend.cache.cache_manager import cache_manager

router = APIRouter(prefix="/api/v1/system", tags=["System"])


@router.get("/cache-stats")
def get_cache_stats() -> Dict[str, Any]:
    """
    §8.3 Cache Telemetry Endpoint:
    Returns utilization, hit/miss rates, and active backend type for all 5 in-process cache tiers:
    - HOT_ADDR_CACHE (5 min TTL)
    - VASP_LABEL_CACHE (1 hr TTL)
    - TRACE_CACHE (30 min TTL)
    - PRICE_CACHE (1 min TTL)
    - HEALTH_CACHE (30 sec TTL)
    """
    return {
        "status": "ok",
        "data": cache_manager.get_stats(),
    }
