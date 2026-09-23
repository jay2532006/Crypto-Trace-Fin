# 🛡️ TRACEX // MASTER ARCHITECTURE & TECHNICAL REFERENCE MANUAL
### **Autonomous Blockchain Intelligence & Forensic VASP Attribution Engine**
**Problem Statement ID**: 26182 (Smart India Hackathon)  
**Theme**: Blockchain & Cybersecurity — Ministry of Home Affairs (MHA) / Indian Cyber Crime Coordination Centre (I4C)  
**System Version**: TraceX v2.0-PRO (Cyber-Forensics Edition)  
**Author / Prototype**: SIH26182 Research Team  

---

## 📑 TABLE OF CONTENTS
1. [Executive Summary & Problem Statement](#1-executive-summary--problem-statement)
2. [Complete REST API Endpoints Specification](#2-complete-rest-api-endpoints-specification)
3. [External API Gateways & Connectivity Links](#3-external-api-gateways--connectivity-links)
4. [Backend Architecture & Data Flow](#4-backend-architecture--data-flow)
5. [Frontend Cyber Command Center (Architecture & UI)](#5-frontend-cyber-command-center-architecture--ui)
6. [Granular Codebase Walkthrough (Functionality of Modules)](#6-granular-codebase-walkthrough-functionality-of-modules)
7. [Environment Variables & Configuration (`.env`)](#7-environment-variables--configuration-env)
8. [Deployment & Verification Guide](#8-deployment--verification-guide)

---

## 1. Executive Summary & Problem Statement

### The Problem (MHA / I4C PS26182)
When cybercriminals commit cryptocurrency-related financial fraud (ransomware, pig-butchering, fake investment scams, extortion), they rapidly launder stolen funds across multiple hops, peel chains, and decentralized cross-chain bridges. Investigating Officers (IOs) in law enforcement agencies (LEAs) struggle because:
1. **Attribution Latency**: Tracing funds manually across multiple blockchains takes hours or days.
2. **Identification of Off-Ramps**: Discovering which Virtual Asset Service Provider (VASP / Exchange) holds the criminal off-ramp wallet requires specialized clustering heuristics.
3. **Legal Timelines**: Section 91 CrPC / Section 91 Bharatiya Nagarik Suraksha Sanhita (BNSS 2023) legal notices must be drafted and dispatched to the VASP before funds are liquidated into fiat currency.

### TraceX Solution
TraceX is a full-stack cyber-forensics intelligence engine that:
- **Validates & Detects Chain Formats**: Instant cryptographic classification of EVM, Bitcoin, TRON, and Solana wallet addresses.
- **Traces Multi-Hop Fund Flows**: Utilizes `NetworkX` directed graph analysis and live on-chain explorer APIs (Etherscan, TronGrid, Blockstream) to track transactions up to 5 hops deep.
- **Attributes Destination VASPs**: Matches hot/deposit wallets against a curated database of 15+ Indian and international exchanges (WazirX, CoinDCX, Binance, OKX, KuCoin, etc.) with clustering confidence scoring.
- **Flags AML Typologies & OFAC Sanctions**: Detects peel chains, rapid fund dispersion, mixers (Tornado Cash, Blender), and checks against the US Treasury OFAC SDN sanctions list.
- **Generates Section 91 BNSS / CrPC Notices**: Automatically creates court-admissible legal requisition notices with auto-filled transaction hashes and VASP nodal officer contact details.
- **Provides Dual-Engine AI Copilot**: Grounded conversational assistant with automatic failover (Google Gemini Flash + Groq Qwen 3.8-27b + offline deterministic rule engine) supporting English, Hindi, and Hinglish.

---

## 2. Complete REST API Endpoints Specification

All backend endpoints are served via FastAPI on `http://localhost:8765`.

| # | HTTP Method | Endpoint Route | Request Body / Query Params | Description & Response Summary |
|---|-------------|----------------|------------------------------|---------------------------------|
| 1 | `GET` | `/api/health` | None | Returns backend status, runtime environment, prototype version, and ISO timestamp. |
| 2 | `GET` | `/api/config` | None | Returns runtime mode, supported chains (`BTC`, `ETH`, `TRON`, `BNB`, `POLYGON`, `SOL`), active data providers, and system disclaimer tags. |
| 3 | `GET` | `/api/prices` | None | Fetches live spot market rates for BTC, ETH, SOL, TRON, and USDT in both USD and INR via CoinGecko. |
| 4 | `GET` | `/api/test/apis` | None | Runs automated Postman-style diagnostic connectivity checks across all 7 connected external APIs (Etherscan, TronGrid, Bitquery, CoinGecko, Esplora, OFAC, Chainabuse) with latency metrics. |
| 5 | `GET` | `/api/test/api/{api_id}` | Path: `api_id` (`etherscan`, `trongrid`, `bitquery`, `coingecko`, `esplora`, `ofac`, `chainabuse`) | Runs a live health ping against a single selected external API gateway. |
| 6 | `POST` | `/api/test/custom` | JSON: `CustomApiTestRequest` (`url`, `method`, `headers`, `body`) | Interactive Postman-style sandbox endpoint allowing analysts to test arbitrary HTTP/HTTPS endpoints from within the UI. |
| 7 | `GET` | `/api/ai/health` | None | Tests connectivity and operational status for Google Gemini, Groq LPU, and Hugging Face providers. |
| 8 | `POST` | `/api/ai/copilot/chat` | JSON: `AIChatRequest` (`question`: str, `trace_data`: dict) | Grounded AI forensic chat assistant. Analyzes trace evidence without hallucinations. Supports queries in English, Hindi, and Hinglish. |
| 9 | `POST` | `/api/ai/copilot/summary` | JSON: `AISummaryRequest` (`trace_data`: dict) | Generates an executive fund flow summary, hop breakdown, and VASP attribution verdict. |
| 10 | `POST` | `/api/ai/copilot/report` | JSON: `AIReportRequest` (`trace_data`: dict, `io_name`: str, `case_id`: str) | Generates a structured formal investigation report formatted for Section 91 BNSS/CrPC judicial submissions. |
| 11 | `GET` | `/api/chains` | None | Returns metadata, explorers, and API configurations for all supported blockchain networks. |
| 12 | `GET` | `/api/vasps` | None | Returns all 15+ registered VASP profiles, clustering heuristics, hot wallet regexes, nodal officer emails, and LEA portal links. |
| 13 | `GET` | `/api/cases/demo` | None | Returns the list of pre-configured high-impact cyber crime benchmark cases (e.g., WazirX hack, Pig Butchering USDT scam, Ransomware). |
| 14 | `GET` | `/api/live/{address}` | Path: `address`, Query: `chain` (optional) | Live on-chain data lookup for a single wallet address directly from public explorers. Performs format validation first. |
| 15 | `GET` | `/api/cases/history` | None | Fetches the 50 most recent investigations stored in the local SQLite database (`sahyog.db`). |
| 16 | `GET` | `/api/cases/{trace_id}/result`| Path: `trace_id` (int) | Retrieves the complete stored JSON trace output from SQLite for a specific historical case. |
| 17 | `POST` | `/api/trace` | JSON: `TraceRequest` (`address`, `chain`, `crime_category`, `case_id`, `investigating_officer`, `mode`) | **Core Attribution Engine**. Validates address, traverses transaction graph up to 5 hops, attributes nearest VASP, detects AML typologies, scores risk, saves to SQLite, and syncs with Neo4j. |
| 18 | `POST` | `/api/notice/generate` | JSON: `NoticeRequest` (`case_id`, `trace_id`, `investigating_officer`, `unit`, `state`, `fir_number`, `complainant`) | Generates a legally compliant Section 91 BNSS 2023 / CrPC requisition notice addressed to the identified VASP's nodal officer and saves to disk. |
| 19 | `POST` | `/api/demo/trace/{case_index}`| Path: `case_index` (int), Query: `investigating_officer` | Runs the full tracing engine using one of the pre-loaded synthetic benchmark cases. |
| 20 | `GET` | `/api/neo4j/status` | None | Checks Neo4j Aura Cloud graph connectivity and retrieves total node and relationship counts. |
| 21 | `POST` | `/api/neo4j/query` | JSON: `CypherRequest` (`query`: str, `params`: dict) | Executes an arbitrary Cypher query against the Neo4j Aura database. |
| 22 | `POST` | `/api/neo4j/sync` | JSON: `trace_data` (dict) | Manually syncs an existing trace result graph into Neo4j nodes (`:Wallet`, `:VASP`) and relationships (`:TRANSFERRED_TO`). |
| 23 | `GET` | `/` | None | Serves the main cyber command center dashboard UI (`dashboard.html`). |
| 24 | `GET` | `/v1` | None | Serves the legacy Golden Master dashboard (`v1/index.html`). |
| 25 | `GET` | `/robo` & `/old` | None | Serves the interactive companion interface (`robo/index.html`). |
| 26 | `GET` | `/download/{filename}` | Path: `filename` (restricted whitelist) | Securely downloads PDF/Markdown documentation (e.g., `SAHYOG_QA_QUICK_GUIDE_EN.pdf`, `TraceX_System_Workflow_Manual.pdf`). |

---

## 3. External API Gateways & Connectivity Links

TraceX integrates with 7 on-chain and intelligence APIs plus 2 AI inference providers:

| Gateway Name | Provider URL & Official Docs | Required Env Key | Key Cost / Tier | Role in TraceX |
| :--- | :--- | :--- | :--- | :--- |
| **Blockstream Esplora** | [https://blockstream.info/api](https://blockstream.info/api) | *None (Public)* | Free (No key) | Live Bitcoin address summaries, confirmed UTXOs, and transaction histories. |
| **Etherscan V2 API** | [https://etherscan.io/apis](https://etherscan.io/apis) | `ETHERSCAN_API_KEY` | Free Tier (5 calls/sec) | Ethereum (ETH) and ERC-20 token transfer histories, wallet balances, and contract events. |
| **TronGrid API** | [https://www.trongrid.io/](https://www.trongrid.io/) | `TRONGRID_API_KEY` | Free Tier (100k calls/day) | TRON network transactions, TRC-20 USDT token transfers, and account resource states. |
| **CoinGecko API** | [https://www.coingecko.com/en/api](https://www.coingecko.com/en/api) | `COINGECKO_DEMO_API_KEY` | Free Demo Tier | Real-time spot prices for BTC, ETH, SOL, TRX, USDT converted into USD and Indian Rupees (INR). |
| **Bitquery V2 API** | [https://bitquery.io/](https://bitquery.io/) | `BITQUERY_ACCESS_TOKEN` | Free Developer Tier | GraphQL cross-chain blockchain indexing, DEX trades, and smart contract telemetry. |
| **OFAC SDN Sanctions**| [https://sanctionssearch.ofac.treas.gov/](https://sanctionssearch.ofac.treas.gov/) | *None (Built-in + Live)* | Free / Public | US Treasury Office of Foreign Assets Control sanctions screening (Tornado Cash, Lazarus Group, Garantex). |
| **Chainabuse API** | [https://www.chainabuse.com/](https://www.chainabuse.com/) | `CHAINABUSE_API_KEY` | Free Community Tier | Crowdsourced malicious wallet addresses and fraud reporting database. |
| **Google Gemini API** | [https://aistudio.google.com/](https://aistudio.google.com/) | `GEMINI_API_KEY` | Free Tier available | Primary AI Investigator reasoning engine (`gemini-2.5-flash` / `gemini-1.5-flash`). |
| **Groq LPU Cloud** | [https://console.groq.com/](https://console.groq.com/) | `GROQ_API_KEY` | Free Tier available | Ultra-low-latency secondary failover LLM (`qwen/qwen3.8-27b`). |
| **Neo4j Aura Cloud** | [https://neo4j.com/cloud/platform/aura-graph-database/](https://neo4j.com/cloud/platform/aura-graph-database/) | `NEO4J_URI`, `NEO4J_PASSWORD` | Free AuraDB Tier | Cloud graph database for persistent multi-hop network visualization and Cypher querying. |

---

## 4. Backend Architecture & Data Flow

### Architecture Diagram
```
                     +---------------------------------------+
                     |    Web Browser (Cyber LEA Dashboard)  |
                     +---------------------------------------+
                                         |
                                         | HTTP REST (JSON / SSE)
                                         v
                     +---------------------------------------+
                     |      FastAPI Server (app.py : 8765)   |
                     +---------------------------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         v                               v                               v
+------------------+           +-------------------+           +-------------------+
| engine/          |           | engine/           |           | engine/           |
| address_validator|           | graph_tracer.py   |           | ai_copilot.py     |
| (Multi-chain)    |           | (NetworkX 5-Hops) |           | (Dual-LLM Engine) |
+------------------+           +-------------------+           +-------------------+
                                         |                               |
                   +---------------------+---------------------+         |
                   |                     |                     |         |
                   v                     v                     v         v
         +-------------------+ +-------------------+ +-------------------+
         | engine/real_api   | | engine/           | | Google Gemini     |
         | (Etherscan, TRON, | | vasp_cluster.py   | | Groq Qwen         |
         |  Esplora, Price)  | | (Attribution)     | | Rule Fallback     |
         +-------------------+ +-------------------+ +-------------------+
                   |                     |
                   +----------+----------+
                              |
                              v
                +----------------------------+
                |      Persistence Layer     |
                |  - SQLite3 (sahyog.db)     |
                |  - Neo4j Aura Cloud Graph  |
                +----------------------------+
```

### Trace Execution Pipeline (`POST /api/trace`)
1. **Input Sanitization**: Extracts address, target chain (if provided), case ID, and crime category.
2. **Cryptographic Validation** (`address_validator.py`):
   - Confirms length, checksum, prefix, and base encoding.
   - Automatically detects the native chain if omitted by user (`BTC`, `ETH/EVM`, `TRON`, `SOL`).
3. **Graph Traversal & Hop Propagation** (`graph_tracer.py`):
   - In **Live Mode**: Queries `real_api.py` for genuine on-chain transfers.
   - In **Demo/Simulated Mode**: Constructs a reproducible multi-hop laundering pattern from benchmark models (`demo_cases.py`).
   - Uses `NetworkX` directed multi-graphs (`MultiDiGraph`) to compute shortest paths and intermediary hops.
4. **VASP Clustering & Attribution** (`vasp_cluster.py`):
   - Cross-references terminal addresses against known hot wallets, deposit sweeps, and cluster heuristics for 15+ major exchanges.
   - Computes an attribution confidence percentage based on hop distance, clustering size, and transaction cadence.
5. **AML Risk Scoring & Typology Flagging** (`typology.py`, `ofac_sanctions.py`):
   - Screens addresses against OFAC sanctions lists.
   - Evaluates FATF red flags: Peel Chaining, Structuring/Smurfing, Rapid Dispersion, High-Risk Mixer interactions.
   - Assigns a composite risk score (0 to 100) and category (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
6. **Persistence & Graph Sync**:
   - Saves case record, parameters, risk score, and full JSON trace payload into SQLite (`data/sahyog.db`).
   - Syncs nodes and edges to Neo4j Aura Cloud (if configured).

---

## 5. Frontend Cyber Command Center (Architecture & UI)

The frontend is a zero-dependency, self-contained single-page application ([dashboard.html](file:///d:/CRYPTO-TRACE/tracex-sahyog-main/tracex-sahyog-main/dashboard.html)) styled with a specialized dark cyber-forensics theme.

### Key Visual & Functional Modules
1. **Top Command Bar**:
   - Live ticker ribbon streaming spot crypto prices in USD & INR via CoinGecko.
   - Operational mode indicator (`LIVE ON-CHAIN` vs `DEMO BENCHMARK`).
   - Quick navigation links to API Workbench, Neo4j console, and PDF manual downloads.
2. **Investigation Control Console (Left Panel)**:
   - Wallet input field with instant cryptographic badge detection.
   - Pre-loaded benchmark scenario selector (WazirX Security Breach, Pig Butchering USDT Scheme, Darknet Drug Cartel, Ransomware Extortion).
   - Mode switcher (`Live On-Chain` / `Synthetic Benchmark`).
   - One-click "Execute Attribution Trace" button.
3. **Interactive Forensic Graph Canvas (Center Stage)**:
   - Dynamic node-link graph visualization powered by `vis-network`.
   - Distinct node glyphs and colors:
     - 🔴 **Red**: Suspect wallet / Sanctioned entity / Mixer.
     - 🟡 **Yellow / Amber**: Intermediary laundering hops & peel wallets.
     - 🔵 **Cyan / Blue**: Regulated Indian exchange hot wallet.
     - 🟢 **Green**: International exchange deposit wallet.
   - Edge labels displaying transaction amount, token symbol, and relative timestamp.
4. **Attribution Verdict & Action Card (Right Panel)**:
   - Nearest VASP banner with official brand emblem.
   - Nodal Officer legal communication email.
   - LEA Law Enforcement Portal direct link.
   - Attribution confidence meter (0% to 100%).
   - Freezing urgency countdown timer.
5. **AML Forensic Breakdown**:
   - Gauge meter for composite risk score (0-100).
   - Visual badges for detected typologies (Peel Chain, High-Speed Layering, OFAC Hit).
6. **Section 91 BNSS / CrPC Notice Generator Modal**:
   - Pre-fills FIR number, police station, IO name, suspect wallet, and specific transaction hashes.
   - One-click copy, print, or text file export.
7. **AI Investigator Copilot Interface**:
   - Interactive chat drawer grounded strictly on the verified trace evidence.
   - Speech-to-text (Web Speech Recognition API) for hands-free voice questioning.
   - Text-to-speech voice playback for audio briefings.
   - Multilingual reasoning: responds natively in English, Hindi, or Hinglish.
8. **Built-in Postman-Style API Tester Modal**:
   - Allows investigators to test upstream APIs directly from the browser with custom headers, query params, and latency reporting.

---

## 6. Granular Codebase Walkthrough (Functionality of Modules)

### 1. `app.py` (FastAPI Core Dispatcher)
- **Lines 1–60**: Initializes FastAPI application instance, configures CORS middleware for localhost and authorized origins, defines project metadata (Problem Statement ID 26182), and loads `.env`.
- **Lines 62–93 (`init_db`)**: Creates SQLite database (`data/sahyog.db`) and initializes `investigations` table if it does not exist. Calls `init_neo4j_schema()` for cloud indexing.
- **Lines 94–131**: Defines Pydantic validation models: `TraceRequest`, `NoticeRequest`, `CustomApiTestRequest`, `AIChatRequest`, `AISummaryRequest`, `AIReportRequest`, and `CypherRequest`.
- **Lines 133–175**: Health, telemetry, and live crypto pricing endpoints (`/api/health`, `/api/config`, `/api/prices`).
- **Lines 176–243**: API diagnostic testing endpoints (`/api/test/apis`, `/api/test/api/{api_id}`, `/api/test/custom`).
- **Lines 244–277**: AI Investigator Copilot endpoints (`/api/ai/health`, `/api/copilot/chat`, `/api/copilot/summary`, `/api/copilot/report`).
- **Lines 278–343**: Metadata, demo cases, live address lookup, and investigation history endpoints.
- **Lines 344–420 (`run_trace`)**: Validates address format, triggers multi-hop attribution trace, records case in SQLite, and asynchronously pushes graph structure to Neo4j.
- **Lines 421–450 (`create_notice`)**: Compiles formal Section 91 BNSS / CrPC requisition notice and saves plain-text notice report in `reports/`.
- **Lines 451–492**: Demo case execution and Neo4j telemetry / Cypher execution endpoints.
- **Lines 493–553**: Static file and dashboard HTML routes (`/`, `/v1`, `/robo`, `/download/{filename}`).

### 2. `engine/address_validator.py` (Cryptographic Address Validator)
- **`validate_btc_address(address)`**: Validates Bitcoin addresses across Legacy P2PKH (starts with `1`), Script P2SH (starts with `3`), and Native SegWit / Taproot Bech32 (`bc1q...`, `bc1p...`) using Base58Check and Bech32 decoding.
- **`validate_evm_address(address)`**: Validates Ethereum / BNB / Polygon addresses (42 hex characters with `0x` prefix) and checks EIP-55 mixed-case checksum validity.
- **`validate_tron_address(address)`**: Validates TRON Base58Check addresses (34 characters, starts with `T`, decodes with byte prefix `0x41`).
- **`validate_solana_address(address)`**: Validates Solana public keys (32–44 alphanumeric characters in Base58 format).
- **`validate_and_classify_address(address, expected_chain)`**: Universal classification orchestrator. Automatically identifies blockchain network when unspecified and rejects malformed inputs with descriptive errors.

### 3. `engine/graph_tracer.py` (Multi-Hop Tracing & NetworkX Traversal)
- **`trace_wallet(address, chain, max_hops=5, crime_category, mode)`**: Core execution engine.
- **`_build_live_trace(address, chain, max_hops)`**: Iteratively queries public blockchain explorers via `real_api.py`, extracts outgoing transfers, and follows fund paths up to 5 levels deep.
- **`_build_benchmark_trace(address, chain, max_hops, crime_category)`**: Generates realistic forensic test topologies based on standard crime typologies (ransomware peel chains, exchange deposits).
- **`_calculate_risk_score(...)`**: Evaluates hop distance to known VASPs, presence of mixers, structuring patterns, and transaction velocities to assign an AML risk score from 0 to 100.
- **`_detect_typologies(...)`**: Flags specific FATF criminal typologies (Rapid Layering, Smurfing, Peel Chain).

### 4. `engine/vasp_cluster.py` (VASP Attribution & Registry)
- **`VASP_REGISTRY`**: Curated dictionary containing 15+ cryptocurrency exchanges (Binance, WazirX, CoinDCX, ZebPay, KuCoin, OKX, Bybit, Huobi, Kraken, Bitfinex, Coinbase, Mudrex, etc.).
- **Data per VASP**: FIU-IND registration status, cluster hot wallet prefixes/regexes, compliance nodal officer emails (e.g., `nodal@wazirx.com`, `compliance@coindcx.com`), physical jurisdiction, and LEA emergency portal URLs.
- **`attribute_address_to_vasp(address, chain)`**: Matches a target wallet address against known VASP clusters and hot wallet patterns.
- **`get_all_vasps()`**: Returns complete registry list for frontend reference.

### 5. `engine/real_api.py` (Live Blockchain Data Harvester)
- **`get_btc_data(address)`**: Fetches live Bitcoin balance, transaction count, and recent inputs/outputs from Blockstream Esplora.
- **`get_eth_data(address)`**: Queries Etherscan V2 API for ETH balance, ERC-20 token transfers (USDT, USDC), and internal transactions.
- **`get_tron_data(address)`**: Queries TronGrid API for TRX balance and TRC-20 USDT transfer events.
- **`fetch_real_data(address, chain)`**: Unified wrapper routing address queries to the appropriate chain-specific harvester with rate-limit and timeout safeguards.

### 6. `engine/ai_copilot.py` (Dual-LLM Investigator Copilot)
- **`_call_gemini(prompt)`**: Executes completion requests against Google Gemini (`gemini-2.5-flash` / `gemini-1.5-flash`) via the Google Generative Language API.
- **`_call_groq(prompt)`**: Executes completion requests against Groq Cloud (`qwen/qwen3.8-27b`) with sub-second latency.
- **`execute_ai_completion(prompt)`**: Implements intelligent automatic failover: Primary Provider (Gemini or Groq) $\rightarrow$ Secondary Provider $\rightarrow$ Deterministic Rule-Based Forensics Engine.
- **`chat_copilot(question, trace_data)`**: Grounds user queries strictly upon verified JSON trace evidence. Prohibits hallucinated transactions. Supports Hindi, Hinglish, and English questions.
- **`summarize_case(trace_data)`**: Produces an executive fund flow summary and VASP identification briefing.
- **`generate_investigation_report(trace_data, officer_info)`**: Formats an official Section 91 BNSS forensic report.
- **`_generate_rule_based_briefing(prompt)`**: Zero-external-dependency rule engine that parses case variables using regular expressions and generates complete forensic summaries when offline or without API keys.

### 7. `engine/notice_generator.py` (BNSS / CrPC Legal Requisition Generator)
- **`generate_notice(...)`**: Compiles an official legal notice under **Section 91 of Bharatiya Nagarik Suraksha Sanhita (BNSS 2023)** / **Section 91 CrPC**.
- Formats formal demand for:
  1. Immediate freezing of the destination deposit account / hot wallet.
  2. Disclosure of KYC documents (Aadhaar, PAN, Passport, Driving License).
  3. Disclosure of login IP logs, device fingerprints, and linked bank accounts.
  4. Preservation of records under Section 67C of the Information Technology Act.

### 8. `engine/ofac_sanctions.py` (Sanctions Screening Engine)
- Contains an indexed registry of known sanctioned cryptocurrency addresses (Tornado Cash router/pools, Blender.io, Lazarus Group, Garantex, Hydra Market).
- **`screen_ofac_sanctions(address)`**: Checks whether any wallet in the multi-hop trace matches sanctioned entities, returning the designation program, SDN entry name, and legal restriction details.

### 9. `engine/neo4j_engine.py` (Graph Database Sync & Cypher Engine)
- **`check_neo4j_status()`**: Tests driver connectivity to Neo4j Aura Cloud and queries active node/relationship counts.
- **`init_neo4j_schema()`**: Creates unique constraints and indexes on `:Wallet(address)` and `:VASP(name)`.
- **`sync_trace_to_neo4j(trace_data)`**: Automatically ingests multi-hop trace paths into Neo4j:
  - Creates `(:Wallet)` nodes with attributes (`address`, `chain`, `risk_score`).
  - Creates `(:VASP)` nodes for identified exchanges.
  - Creates `[:TRANSFERRED_TO]` edges with transaction hash, value, and timestamp.
  - Creates `[:DEPOSITED_AT]` edges linking intermediary wallets to VASPs.
- **`execute_cypher(query, params)`**: Runs arbitrary Cypher graph queries and returns structured record arrays.

### 10. `engine/price_feed.py` (Live Spot Exchange Rates)
- **`get_live_prices()`**: Fetches real-time market prices for BTC, ETH, SOL, TRX, and USDT in USD and INR from CoinGecko. Implements in-memory caching to respect rate limits.
- **`convert_crypto_value(amount, symbol, currency)`**: Converts token amounts into fiat equivalent values (USD or INR).

### 11. `engine/api_tester.py` (Automated API Health Diagnostics)
- Implements dedicated test functions (`test_etherscan`, `test_trongrid`, `test_bitquery`, `test_coingecko`, `test_blockstream`, `test_ofac`, `test_chainabuse`).
- **`run_all_api_tests()`**: Runs all 7 tests sequentially, records response status and latency in milliseconds, and returns a complete diagnostic dossier.

### 12. `engine/key_manager.py` (Runtime API Key Management)
- **`get_all_configured_keys()`**: Reads API keys from environment and `.env`, returning preview masked values (e.g., `eth_a3...9f2b`).
- **`update_api_key(key_name, key_value)`**: Saves or updates an API key in both `os.environ` and `.env` without requiring a server restart.
- **`validate_key(key_name, key_value)`**: Performs a live test call against the respective provider API to verify key validity before saving.

### 13. `engine/demo_cases.py` (Benchmark Forensic Scenarios)
- Defines pre-configured benchmark cases for presentations, testing, and offline demonstrations:
  - **Case 0**: WazirX Security Incident (EVM multi-hop laundering).
  - **Case 1**: Pig Butchering Scam (TRC-20 USDT multi-hop structuring).
  - **Case 2**: Darknet Narcotics Marketplace (Bitcoin peel chain laundering).
  - **Case 3**: Ransomware Extortion Campaign (Multi-hop mixer evasion).
  - **Case 4**: Decentralized Flash Loan Exploit (Complex smart contract routing).

---

## 7. Environment Variables & Configuration (`.env`)

Configuration settings are stored in `.env` in the project root:

```env
# ─── System & Server Configuration ───
APP_ENV=development
APP_MODE=demo                      # Options: 'demo' (offline/simulated) or 'live' (on-chain)
PORT=8765
HOST=0.0.0.0
ALLOWED_ORIGINS=http://localhost:8765,http://127.0.0.1:8765

# ─── Blockchain Gateways ───
ETHERSCAN_API_KEY=your_etherscan_api_key_here
ETHERSCAN_BASE_URL=https://api.etherscan.io/v2/api
BLOCKSTREAM_BASE_URL=https://blockstream.info/api
TRONGRID_API_KEY=your_trongrid_api_key_here
TRONGRID_BASE_URL=https://api.trongrid.io
BITQUERY_ACCESS_TOKEN=your_bitquery_token_here
BITQUERY_GRAPHQL_URL=https://streaming.bitquery.io/graphql
COINGECKO_DEMO_API_KEY=your_coingecko_demo_key_here
CHAINABUSE_API_KEY=your_chainabuse_api_key_here

# ─── AI Copilot Dual-Engine ───
GEMINI_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_access_token_here

# ─── Copilot Routing Config ───
AI_PRIMARY_PROVIDER=gemini          # Options: 'gemini' or 'groq'
AI_FALLBACK_PROVIDER=groq
GEMINI_MODEL=gemini-2.5-flash
GROQ_MODEL=qwen/qwen3.8-27b

# ─── Neo4j Aura Cloud (Optional) ───
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
NEO4J_DATABASE=neo4j
```

---

## 8. Deployment & Verification Guide

### Quick Launch (Windows)
1. Open PowerShell or Command Prompt in this folder:
   ```cmd
   cd d:\CRYPTO-TRACE\tracex-sahyog-main\tracex-sahyog-main
   ```
2. Double-click `start.bat` or run:
   ```cmd
   python -m uvicorn app:app --host 0.0.0.0 --port 8765 --reload
   ```
3. Open your browser and navigate to: **`http://localhost:8765`**

### Quick Launch (Linux / macOS)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app:app --host 0.0.0.0 --port 8765 --reload
```

### Verification Checklist
- [x] **Backend Health**: Visit `http://localhost:8765/api/health` — should return `status: "running"`.
- [x] **API Connectivity**: Visit `http://localhost:8765/api/test/apis` — executes live diagnostics across all 7 APIs.
- [x] **AI Copilot Health**: Visit `http://localhost:8765/api/ai/health` — checks LLM provider availability.
- [x] **Demo Trace**: In the UI, click any benchmark case (e.g., "Pig Butchering USDT") and click **"Execute Attribution Trace"** to view interactive graph visualization and VASP identification.
- [x] **Section 91 Notice**: Click **"Generate Section 91 Notice"** to inspect the legally drafted requisition notice.
