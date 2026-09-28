"""
CryptoTrace LEA — Base Configuration Module
Strict environment-based configuration management.
Secrets are never hardcoded and never logged.
"""

import os
from typing import List
from pydantic import BaseModel

class AppConfig(BaseModel):
    # System & Environment
    APP_NAME: str = "CryptoTrace LEA"
    APP_VERSION: str = "2.0.0-SIH26183"
    APP_ENV: str = os.getenv("APP_ENV", "development")  # development, staging, production
    APP_MODE: str = os.getenv("APP_MODE", "demo")        # demo, live
    PORT: int = int(os.getenv("PORT", "8765"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cryptotrace-lea-insecure-dev-secret-key-32charsmin")
    ALLOWED_ORIGINS: List[str] = [
        o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8765,http://127.0.0.1:8765").split(",") if o.strip()
    ]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/sahyog.db")
    POSTGRES_AUTHORITATIVE: bool = os.getenv("POSTGRES_AUTHORITATIVE", "false").lower() == "true"

    # Redis (Cache / Deduplication / Coordination only)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Primary Live Blockchain Gateways (Confirmed SIH Backbone)
    ETH_RPC_PRIMARY_URL: str = os.getenv("ETH_RPC_PRIMARY_URL", "https://ethereum-rpc.publicnode.com")
    POLYGON_RPC_PRIMARY_URL: str = os.getenv("POLYGON_RPC_PRIMARY_URL", "https://polygon.drpc.org")
    TRON_RPC_PRIMARY_URL: str = os.getenv("TRON_RPC_PRIMARY_URL", "https://api.trongrid.io")
    TRON_GRID_API_KEY: str = os.getenv("TRON_GRID_API_KEY", "")
    MEMPOOL_SPACE_URL: str = os.getenv("MEMPOOL_SPACE_URL", "https://mempool.space/api")
    
    # Auxiliary Providers (Enrichment / Fallbacks only)
    ETHERSCAN_API_KEY: str = os.getenv("ETHERSCAN_API_KEY", "")
    BLOCKSTREAM_BASE_URL: str = os.getenv("BLOCKSTREAM_BASE_URL", "https://blockstream.info/api")
    COINGECKO_DEMO_API_KEY: str = os.getenv("COINGECKO_DEMO_API_KEY", "")

    # Graph Projection
    NEO4J_URI: str = os.getenv("NEO4J_URI", "")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # AI Reasoning Engine (Optional Auxiliary)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    AI_PRIMARY_PROVIDER: str = os.getenv("AI_PRIMARY_PROVIDER", "gemini")

    # Feature Flags (Win Plan)
    TRACE_OFAC_SANCTIONS: bool = os.getenv("TRACE_OFAC_SANCTIONS", "true").lower() == "true"
    TRACE_STOP_AT_MIXER: bool = os.getenv("TRACE_STOP_AT_MIXER", "true").lower() == "true"
    TRACE_CROSS_CHAIN: bool = os.getenv("TRACE_CROSS_CHAIN", "true").lower() == "true"
    INTAKE_ENABLED: bool = os.getenv("INTAKE_ENABLED", "true").lower() == "true"
    INTAKE_AUTOTRACE: bool = os.getenv("INTAKE_AUTOTRACE", "false").lower() == "true"
    DEMO_SEED_ON_START: bool = os.getenv("DEMO_SEED_ON_START", "false").lower() == "true"

    # Security & Audit
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 8
    AUDIT_LOG_DIR: str = "./data/audit"
    RAW_STORAGE_DIR: str = "./data/raw"

def get_config() -> AppConfig:
    return AppConfig()
