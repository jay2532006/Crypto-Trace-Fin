# CryptoTrace LEA — Deployment Guide

## 1. Prerequisites
- **Python**: 3.10+ (Tested on Python 3.13)
- **Node/Browser**: Modern Evergreen Browser (Chrome, Edge, Firefox)
- **Database**: PostgreSQL 14+ (Production) or SQLite 3 (Local / Demonstration)
- **Cache/Queue**: Redis 6+ (Optional for local dev, mandatory for clustered multi-node live ingestion)

---

## 2. Environment Configuration
Create a `.env` file from `.env.example`:

```bash
# Core Environment
ENVIRONMENT=production
DEBUG=false
APP_MODE=live
SECRET_KEY=generate-a-cryptographically-secure-random-key-here

# Database Configuration (PostgreSQL Authoritative)
DATABASE_URL=postgresql://cryptotrace_user:secure_password@localhost:5432/cryptotrace_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis Cache & Deduplication
REDIS_URL=redis://localhost:6379/0

# Live Blockchain Provider Backbone
ETH_RPC_PRIMARY_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
POLYGON_RPC_PRIMARY_URL=https://polygon-mainnet.infura.io/v3/YOUR_INFURA_KEY
TRON_RPC_PRIMARY_URL=https://api.trongrid.io
TRON_GRID_API_KEY=YOUR_TRONGRID_KEY
MEMPOOL_SPACE_URL=https://mempool.space/api

# Secondary Historical Enrichment
ETHERSCAN_API_KEY=YOUR_ETHERSCAN_KEY
POLYGONSCAN_API_KEY=YOUR_POLYGONSCAN_KEY

# Law Enforcement Agency Configuration
LEA_AGENCY_NAME="Cyber Crime Police Station"
LEA_STATE="Maharashtra"
```

---

## 3. Database Migration
Apply the canonical schema to PostgreSQL:

```bash
psql -U cryptotrace_user -d cryptotrace_db -f backend/db/migrations/001_initial_schema.sql
```

For local development or portable demonstration, SQLite initializes automatically under `data/sahyog.db`.

---

## 4. Running the Application

### Starting the FastAPI Backend
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Accessing the Investigator Workstation
Open your web browser and navigate to:
```text
http://localhost:8000/
```
or serve `dashboard.html` directly via your secure reverse proxy (Nginx / Caddy).

---

## 5. Reverse Proxy Configuration (Nginx Example)
```nginx
server {
    listen 443 ssl http2;
    server_name cryptotrace.police.gov.in;

    ssl_certificate /etc/ssl/certs/cryptotrace.crt;
    ssl_certificate_key /etc/ssl/private/cryptotrace.key;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        root /var/www/cryptotrace;
        index dashboard.html;
        try_files $uri $uri/ /dashboard.html;
    }
}
```
