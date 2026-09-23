# BTC-SHIELD — Complete Project Conversation Context

---

## 1. Project Identity

- **Operational Domain:** Blockchain Forensics & Cryptographic Intelligence (Law Enforcement & National Security Track).
- **Project Purpose & Target Users:** An enterprise-grade blockchain analytics and anti-money laundering (AML) forensic platform built for financial crime investigators, law enforcement analysts, and compliance officers. It automates multi-input heuristic entity resolution, 23-dimension behavioral feature extraction, unsupervised machine learning anomaly detection (Isolation Forest and behavioral cohort clustering), graph relationship mapping, verifiable forensic evidence synthesis (peeling chains, CoinJoin/mixing, rapid fan-in/fan-out, burst velocity), and prioritized investigation lead queues.
- **Current Production Architecture:**
  - **Frontend:** Single Page Application (SPA) built with React 19, TypeScript, Vite, Tailwind CSS, Lucide icons, and `@tanstack/react-query` v5. Hosted on **GitHub Pages**.
  - **Backend:** High-performance RESTful API built with Python 3.13, FastAPI (`0.115.0`), SQLAlchemy 2.0 (synchronous engine for reliability), Pydantic v2, Alembic, NumPy, Scikit-Learn, and Polars. Hosted on **Render** (Linux Web Service container).
  - **Database:** Serverless **Neon PostgreSQL** (SSL, cloud-hosted in AWS us-east-1) in production; SQLite (`btcshield.db`) for local offline testing and CI unit tests.
  - **Cloud Infrastructure Constraints:** Render container runs with a hard **512 MB cgroup memory ceiling** and `WEB_CONCURRENCY=1`. Cloudflare sits as the reverse proxy in front of Render.

---

## 2. Repository and Deployment

- **GitHub Remote Repository:** `https://github.com/Pramendra0001/BTC.git`
- **Frontend Live URL (GitHub Pages):** `https://pramendra0001.github.io/BTC/`
- **Backend Live URL (Render Web Service):** `https://btc-3jme.onrender.com`
- **API Documentation (Swagger UI):** `https://btc-3jme.onrender.com/docs`
- **Active Git Branch:** `main`
- **Latest Known Production Commit:** `4f043819f1fb6c9796c2759c165245ee40b39de7`
  - *Commit Message:* `fix(perf): resolve production API latency and frontend hanging via bounded queries, bulk joins, and query client hardening`
- **Core Technology Stack:**
  - *Backend:* Python 3.13, FastAPI, Uvicorn, SQLAlchemy 2.0, PostgreSQL (psycopg2/asyncpg drivers), Scikit-Learn 1.5, NumPy, Polars, Alembic, Pytest.
  - *Frontend:* React 19, TypeScript 5.x, Vite 6.x, Tailwind CSS, TanStack Query v5, Axios, React Router v6.

---

## 3. Complete Architecture & System Flow

```text
[ Browser / GitHub Pages ]
       │
       ▼ (HTTPS / Bearer JWT)
[ Cloudflare Reverse Proxy ]
       │
       ▼
[ Render Web Service (FastAPI / Uvicorn) ] (512 MB cgroup memory ceiling)
       │
       ▼
1. INGESTION SERVICE (ingestion_service.py)
   - Supports CSV, JSON, XML, and ZIP_RELATIONAL formats.
   - Polyglot parser normalizes raw inputs, outputs, amounts, timestamps, and fees.
   - Inserts raw records and normalized transactions in bounded streaming chunks (1,000 rows/batch).
       │
       ▼
2. ENTITY RESOLUTION (entity_service.py)
   - Applies common-input-ownership heuristic: inputs spending together in a single transaction belong to the same entity.
   - Creates or links canonical `Wallet` records and tracks cluster associations.
       │
       ▼
3. BEHAVIORAL FEATURE ENGINEERING (feature_service.py)
   - Computes 23 behavioral forensic dimensions per wallet:
     tx_count, total_sent, total_received, net_balance, sent_received_ratio,
     avg_tx_value, max_tx_value, std_tx_value, avg_fee_paid, max_fee_paid,
     velocity_tx_per_day, burst_ratio_24h, fan_in_count, fan_out_count,
     unique_counterparties, peeling_chain_occurrences, mixing_pattern_matches,
     dormancy_days_before_burst, counterparty_entropy, high_risk_edge_ratio,
     darknet_exposure_score, exchange_exposure_score, avg_time_between_tx.
   - Operates with zero ORM deserialization: queries via SQL aggregations and writes `BehavioralFeature` records in chunks of 1,000.
       │
       ▼
4. MACHINE LEARNING PIPELINE (ml_service.py)
   - Streams feature records in chunks of 2,000 via `yield_per(2000)`.
   - Pre-allocates a compact single-precision `float32` matrix $(N \times 23)$.
   - In-place scaling via `StandardScaler(copy=False)`.
   - Fits **Isolation Forest** ($\psi=256$, 50 trees, `n_jobs=1`), computing outlier decision scores normalized to $[0, 100]$.
   - Fits **MiniBatchKMeans** ($K=12$, `batch_size=2048`, `n_init=3`), partitioning entities and computing centroid distances.
   - Points with centroid distance $d_i > 97\text{th percentile}$ are flagged as behavioral outliers (`cluster_id = -1`).
   - Persists `AnomalyResult` in bulk batches of 2,000 records.
       │
       ▼
5. EVIDENCE GENERATION (evidence_service.py)
   - Evaluates high-anomaly wallets (`anomaly_score >= 80` or `cluster_id == -1`).
   - Verifies forensic heuristic rules:
     - Peeling chain patterns ($\ge 5$ consecutive change hops).
     - CoinJoin / equal-denomination mixing patterns.
     - Sudden velocity burst after extended dormancy ($\ge 5\times$ baseline velocity).
     - Extreme fan-in consolidation ($\ge 20$ inputs consolidated into 1 wallet).
   - Generates structured, immutable `Evidence` records with rule types and confidence scores.
       │
       ▼
6. ALERT SYNTHESIS & PRIORITIZATION (alert_service.py)
   - Synthesizes multi-rule evidence into actionable `Alert` records.
   - Computes composite risk score:
     $$\text{Score} = 0.5 \times \text{ML\_Anomaly\_Score} + 0.3 \times \text{Max\_Evidence\_Confidence} + 0.2 \times \text{Heuristic\_Hits}$$
   - Assigns priority:
     - $\ge 80 \implies \text{CRITICAL}$
     - $60 - 79 \implies \text{HIGH}$
     - $40 - 59 \implies \text{MEDIUM}$
     - $< 40 \implies \text{LOW}$
   - Inserts alerts with status `NEW`.
       │
       ▼
7. COMMAND CENTER & DASHBOARD (dashboard_service.py)
   - Collapses summary statistics into 7 single-pass SQL statements.
   - Evaluates top-ranked alerts to feed the **Prioritized Leads** investigation queue.
```

---

## 4. Dataset History and Current Production Dataset

### A. History of Evaluated Datasets
1. **Old Test Fixtures:**
   - `dataset_250.xml` (250 txs), `dataset_500.json` (500 txs), `dataset_1000.csv` (1,000 txs). Retained strictly for legacy parser tests.
2. **Canonical 1K & 10K Synthetic Datasets:**
   - `data/samples/btc_shield_synthetic_transactions.csv` (1,000 records, 742 wallets). Formed the baseline dataset during initial platform buildout.
   - `data/samples/btc_shield_synthetic_transactions_10000.csv` (10,000 records). Used for initial multi-tier memory benchmarks.
3. **Elliptic & External Public Datasets:**
   - Evaluated during architecture planning. The Elliptic dataset contains Kaggle-format illicit/licit labels on subgraphs but lacks raw input/output transaction scripts and fees required for heuristic peeling/mixing analysis.
   - Decision was made to use synthetic relational datasets structured specifically for enterprise forensic requirements (providing full txid, inputs, outputs, amounts, fees, timestamps, and network observations).
4. **Current Production 100K Dataset (Dataset ID: 6):**
   - **Filename:** `btc_shield_100000_ground_ready.zip` [VERIFIED]
   - **Format:** `ZIP_RELATIONAL` containing 4 relational CSV tables:
     1. `btc_shield_transactions_100000.csv` (100,000 txs)
     2. `btc_shield_wallets.csv` (45,000 resolved entities)
     3. `btc_shield_edges_100000.csv` (350,131 graph edges)
     4. `btc_shield_enrichment_100000.csv` (IP, ASN, geolocation metadata)
   - **Status in Neon PostgreSQL:** `PIPELINE_COMPLETE` [VERIFIED]
   - **Verified Record Counts:**
     - Transactions: `100,000` [VERIFIED]
     - Wallets: `45,000` [VERIFIED]
     - Graph Edges: `350,131` [VERIFIED]
     - Behavioral Features: `45,000` [VERIFIED]
     - Anomaly Results: `45,000` [VERIFIED]
     - Evidence Records: `10,034` [VERIFIED]
     - Alerts Generated: `3,233` [VERIFIED]
     - Transaction Inputs: Estimated ~180,000 [ESTIMATED]
     - Transaction Outputs: Estimated ~210,000 [ESTIMATED]

---

## 5. ML Pipeline & Render 512 MB OOM Investigation

### A. The Incident
On September 22, 2026, Render reported:
`"Web Service BTC exceeded its memory limit. Ran out of memory (used over 512MB) while running your code. Exited with status 3."`
Logs confirmed the crash occurred immediately after:
`INFO:app.services.ml_service:Starting ML pipeline for dataset 6`

### B. Root Cause Breakdown
1. **DBSCAN Quadratic Memory Explosion ($O(N^2)$):**
   - Scikit-Learn's `DBSCAN(eps=0.5, min_samples=5)` was called on 45,000 23-dimensional vectors.
   - Because tree-based spatial partitioning fails in 23 dimensions, Scikit-Learn computed an uncompressed pairwise Euclidean distance matrix:
     $$45,000 \times 45,000 \times 8\text{ bytes} \approx \mathbf{16.2\text{ GB}}$$
     This instantly exceeded Render's 512 MB container ceiling.
2. **Double ORM Deserialization:**
   - Calling `db.query(BehavioralFeature).all()` instantiated 45,000 heavy Python objects with internal dict caches, consuming ~180 MB.
3. **Session Identity Map Retention:**
   - Committing thousands of rows without calling `db.expunge_all()` left all instances bound to the SQLAlchemy session, leaking heap memory.

### C. Architectural Remediation (Commit `8c60901`)
1. **Replacement with Bounded `MiniBatchKMeans`:**
   - Implemented `MiniBatchKMeans(n_clusters=12, batch_size=2048, n_init=3, max_iter=100)`.
   - **CRITICAL DISTINCTION:** `MiniBatchKMeans` is **NOT** claimed to be mathematically or semantically identical to `DBSCAN`. Instead, it was chosen because it achieves $O(N \cdot K)$ memory complexity (allocating only ~6.38 MB vs >15 GB) while **preserving the downstream outlier contract**:
     - It partitions wallets into $K=12$ behavioral clusters.
     - Computes the Euclidean distance $d_i = \|x_i - \mu_{c_i}\|$ to the centroid.
     - Wallets in the top 3% furthest distances ($d_i > 97\text{th percentile}$) are tagged with `cluster_id = -1`.
     - Downstream services (`evidence_service.py` checking `cluster_id == -1`) receive identical behavioral outlier indicators without quadratic memory allocation.
2. **Isolation Forest Subsampling ($\psi=256$):**
   - Configured subsample size $\psi=256$ with 50 trees (`n_jobs=1`), capping estimator memory at **1.32 MB** while maximizing anomaly detection sensitivity (Liu et al., 2008).
3. **Chunked Streaming & Float32 Pre-allocation:**
   - Streamed rows via `yield_per(2000)` into a pre-allocated single-precision `float32` matrix $(45000 \times 23)$, scaled in-place via `StandardScaler(copy=False)`.
4. **Proactive Session Expunging & GC:**
   - Injected `db.expunge_all()` and `gc.collect()` at every stage boundary.
5. **Measured Benchmark Results:**
   - 1,000 records: 0.59s, 204.2 MB peak RSS.
   - 10,000 records: 2.73s, 223.1 MB peak RSS.
   - 45,000 records (Dataset 6): **116.33 seconds** total cloud E2E pipeline execution on Render, peak memory ~310 MB (**>200 MB headroom under 512 MB limit**). 0 worker restarts.

---

## 6. Production Performance Audit & Latency Fixes

Prior to commit `4f04381`, production API requests caused severe latency:

1. **Structural Heuristics Bottleneck (`/api/heuristics/summary`):**
   - *Baseline Latency:* **29.40 seconds** [MEASURED]
   - *Cause:* Executed `db.query(Transaction).all()`, `db.query(TransactionInput).all()`, and `db.query(TransactionOutput).all()` twice per request.
   - *Fix:* Bounded candidate discovery to the top 2,000 recent transactions (`order_by(Transaction.timestamp.desc().nullslast()).limit(2000)`) with bulk `in_(candidate_tx_ids)` joins.
   - *Hardened Latency:* **0.28 seconds (>99% reduction)** [MEASURED]
2. **N+1 Counterparty Traversal (`/api/wallets/{address}`):**
   - *Baseline Latency:* **0.85 seconds** [MEASURED]
   - *Cause:* Executed individual queries inside loops for every input and output (50–100 sequential round trips).
   - *Fix:* Converted to 2 bulk SQL `in_()` queries across inputs and outputs.
   - *Hardened Latency:* **0.14 seconds** [MEASURED]
3. **N+1 Graph Queries (`/api/graph/`):**
   - *Baseline Latency:* **0.43 seconds** [MEASURED]
   - *Fix:* Pre-fetched candidate transactions in bulk via `needed_tx_ids`.
   - *Hardened Latency:* **0.15 seconds** [MEASURED]
4. **Dashboard Single-Pass Aggregations (`/api/dashboard/`):**
   - *Baseline Latency:* **0.22 seconds** [MEASURED]
   - *Fix:* Collapsed 22 sequential queries into 7 single-pass SQL statements using `func.count(case(...))` and direct scalar counts.
   - *Hardened Latency:* **0.08 seconds** [MEASURED]
5. **Database Indexing:** Added migration `a1b2c3d4e5f6_add_performance_indexes.py` for B-tree indexes on `graph_edges`, `transactions.timestamp DESC`, `wallets.tx_count`, `alerts`, and `audit_logs`.
6. **Frontend Query Client Hardening:** Configured Axios timeout of **25 seconds** (`timeout: 25000`), `staleTime: 30s`, `gcTime: 5m`, `refetchOnWindowFocus: false`, and capped retries to 1 for network errors.

---

## 7. Prioritized Leads Investigation & Forensic Status

### A. The Symptom
The Command Center dashboard on GitHub Pages appeared to show an empty or perpetually loading Prioritized Leads queue.

### B. Endpoints & Data Contracts Involved
- **Endpoint 1:** `GET /api/dashboard/` returns `recent_alerts` (top 10 alerts ordered by `score DESC`).
- **Endpoint 2:** `GET /api/alerts/?limit=10&priority=CRITICAL` returns alerts filtered by `priority == 'CRITICAL'`.

### C. Hypothesized Root Causes (Pending Production Verification)
1. **Schema Shape Mismatch (`data.items` vs. Raw Array):**
   - `GET /api/alerts/` returns a raw JSON array: `[ {...}, {...} ]`.
   - In `DashboardPage.tsx`, the code attempts to read `alertsData?.items`. Because `alertsData` is already an Array, `alertsData?.items` evaluates to `undefined`, resolving to an empty array `[]`.
2. **Case Sensitivity in PostgreSQL String Comparison:**
   - PostgreSQL string equality is strictly case-sensitive. `Alert.priority` is stored as `'CRITICAL'`. If the frontend hook passes `priority: 'critical'` or `priority: 'Critical'`, PostgreSQL returns 0 matches.
3. **Score Field Name Mismatch:**
   - In `models.py`, `Alert.score` is the column name. In `AnomalyResult`, the field is `anomaly_score`. If the frontend expects `anomaly_score`, the value renders as `NaN` or `undefined`.
4. **Absence of Clean Empty State:**
   - If zero items match the strict `CRITICAL` filter, the component previously remained in a skeleton state rather than rendering an explicit "No critical leads pending triage" card.
5. **IMPORTANT NOTE:** These 4 points remain **HYPOTHESES** until verified against actual live HTTP responses and exact component code. Under no circumstances should an unverified hypothesis be declared as fact.

### D. Lead Provenance Chain
For any verified alert, the provenance is 100% database-backed:
$$\text{Prioritized Lead} \longrightarrow \text{Alert} \longrightarrow \text{Wallet / Entity} \longrightarrow \text{Anomaly Result} \longrightarrow \text{Evidence} \longrightarrow \text{Source Transactions}$$
No fake rows exist or should ever be created.

---

## 8. Frontend Performance & Startup Waterfall Investigation

### A. Current Behavior
When opening `https://pramendra0001.github.io/BTC/`, users experience a perceived loading delay before the application shell becomes interactive.

### B. Root Causes
1. **Monolithic Initial Bundle (Zero Route Splitting):**
   In `frontend/src/App.tsx`, all 10 page components are imported statically at the top of the file. The browser must download and parse the entire bundle (including Recharts, Lucide icons, and graph visualization libraries) before rendering the sidebar or header.
2. **Coarse Loading Skeletons:**
   `DashboardPage.tsx` previously wrapped entire views in a single loading conditional, delaying KPI card display until secondary data finished loading.
3. **Critical Distinction Regarding Timing:**
   - **Static Asset Load (CDN):** 0.15s – 0.30s.
   - **Frontend App Shell Render:** < 0.40s.
   - **Warm Backend API Latency:** 0.05s – 0.28s (verified on live Neon DB).
   - **Render Cold Start:** **30 – 45 seconds** if the free-tier container has been inactive for >15 minutes.
   - **CRITICAL RULE:** Frontend code splitting **cannot** and **must not** be claimed to eliminate Render cold-start latency. Cold-start delays must always be measured and reported separately from client render times.

---

## 9. Antigravity Tool-Runner Problem & Technical Context

### A. The Exact Error
During tool invocation (`run_command`, `write_to_file`, `view_file`), the platform failed with:
```text
JSON hook "jsonhook__googlecloudtools.datacloud_telemetry_PreToolUse_0_0" failed: command failed: exit status 1, stderr: node:internal/modules/cjs/loader:1422
  throw err;
  ^
Error: Cannot find module 'C:\Users\PRAMENDRA KUSHWAHA\.gemini\config\plugins\googlecloudtools.datacloud_telemetry\"C:\Users\PRAMENDRA'
```

### B. Root Cause
The plugin `googlecloudtools.datacloud_telemetry` registered a `PreToolUse` hook. On Windows, because the user path contains a space (`PRAMENDRA KUSHWAHA`), the command line invoking Node.js constructed an argument ending with a trailing backslash inside double quotes (`...telemetry\"`), which escaped the double quote in Windows argv parsing and mangled the path.

### C. Attempted Remediation & Key Finding
- The user first renamed the folder to `googlecloudtools.datacloud_telemetry.bak`.
- However, the Antigravity plugin loader dynamically scans **all subdirectories** inside `C:\Users\PRAMENDRA KUSHWAHA\.gemini\config\plugins\`. Consequently, it detected the `.bak` folder and continued attempting to load the broken hook.
- **Required Remediation:** The `.bak` folder must be **moved completely outside** the `plugins\` directory (e.g., moved to the Desktop) or deleted entirely.

---

## 10. Current Required Next Steps for Next AI Agent

1. **Verify Tool Runner:** Ensure `run_command` executes cleanly without hook errors.
2. **Inspect Production API Responses:** Query `GET https://btc-3jme.onrender.com/api/alerts/?limit=10&priority=CRITICAL` and `GET https://btc-3jme.onrender.com/api/dashboard/` with authentication to record the exact JSON shapes.
3. **Trace Prioritized Leads:** Inspect `DashboardPage.tsx`, `hooks.ts`, and `client.ts` to verify whether array vs. `data.items`, score naming, or case sensitivity is causing empty lead displays.
4. **Fix Data Mapping & Empty State:** Update `DashboardPage.tsx` to handle array normalization and display an explicit "No critical leads pending triage" card when 0 critical alerts exist.
5. **Implement Measured Frontend Code Splitting:**
   - Convert `App.tsx` routes to `React.lazy()` with `<Suspense fallback={<PageSkeleton />}>`.
   - Configure Vite `manualChunks` in `vite.config.ts` to isolate `recharts` and graph modules.
   - Decouple Dashboard into independent async sections (KPI cards, Leads, Charts).
6. **Execute Verification Suite:** Run `pytest tests/ -v` and `npm run build`.
7. **Measure & Report:** Record exact before/after bundle sizes and load timings. Document findings in `FINAL_PRODUCTION_VALIDATION_REPORT.md`.
8. **Git Operations:** Commit and push only after verification has completed.

---

## 11. Important Engineering Rules

1. **No Fake Alerts:** Do not insert fabricated rows into `alerts` or hardcode leads in the frontend.
2. **No Fabricated Provenance:** Every displayed lead must link to authentic underlying database entities and transactions.
3. **No Unverified Claims:** Mark all measurements as [VERIFIED], [MEASURED], [ESTIMATED], or [NOT VERIFIED].
4. **No Unnecessary New Datasets:** Do not generate or upload new datasets when Dataset 6 is already populated with 100,000 transactions and 3,233 alerts.
5. **No Threshold Dilution:** Do not lower AML or heuristic alert thresholds merely to force items into the dashboard.
6. **No Secret Exposure:** Never include JWT secrets, passwords, or database connection strings in markdown or chat.
7. **No Claims of Algorithmic Equivalence:** Never claim MiniBatchKMeans is mathematically identical to DBSCAN; state clearly that it is an operational substitute preserving outlier contracts.
8. **No Guarantees on Uncontrollable Latency:** Never claim the entire website will load in 1 second during a Render container cold start.

---

## 12. Chronological Conversation & Decision Log

- **Phase 1 (Dataset Hardening):** Evaluated legacy fixtures (`dataset_250.xml`, `dataset_500.json`, `dataset_1000.csv`). Hardened `ingestion_service.py` to support native lists, JSON-stringified arrays, and semicolon-separated strings.
- **Phase 2 (100K Dataset Introduction):** Received relational 100K dataset (`btc_shield_transactions_100000.csv`, `wallets`, `edges`, `enrichment`). Designed ingestion for relational archives.
- **Phase 3 (Render 512 MB OOM Crisis):** Production Render container crashed with status 3 during ML execution on Dataset 6. Investigated root cause: DBSCAN $O(N^2)$ memory explosion (16.2 GB) and ORM heap accumulation.
- **Phase 4 (ML Zero-ORM Refactor - Commit `8c60901`):** Replaced DBSCAN with `MiniBatchKMeans(n_clusters=12, batch_size=2048)`, implemented Isolation Forest with $\psi=256$, pre-allocated single-precision `float32` matrices, and added `db.expunge_all()`.
- **Phase 5 (Production Performance Audit - Commit `4f04381`):** Identified 29.40s bottleneck in `/api/heuristics/summary` and N+1 query loops in wallet/graph endpoints. Bounded candidate discovery to 2,000 txs (<0.28s) and added B-tree database indexes via Alembic.
- **Phase 6 (Production E2E Validation):** Executed full 100K pipeline on Render backend live: **completed in 116.33 seconds**, generating 10,034 evidence items and 3,233 alerts. Confirmed zero OOM crashes.
- **Phase 7 (Prioritized Leads & Frontend Speed Request):** User identified that Prioritized Leads appeared empty on the dashboard and frontend navigation felt sluggish. Diagnosed potential schema mismatch (`data.items` vs array) and lack of route code splitting.
- **Phase 8 (Plugin Hook Interruption):** The IDE's `googlecloudtools.datacloud_telemetry` hook began failing with `MODULE_NOT_FOUND` due to unescaped spaces in the Windows user path, halting automated tool operations.

---

## 13. Files and Code Areas

### Backend
- `backend/app/api/endpoints/alerts.py`: Alert queries, status updates, priority filtering.
- `backend/app/api/endpoints/dashboard.py`: Consolidated dashboard statistics and recent alerts.
- `backend/app/api/endpoints/datasets.py`: Upload and trigger `/process` endpoint.
- `backend/app/api/endpoints/graph.py`: Subgraph extraction and bounded ego expansion.
- `backend/app/api/endpoints/wallets.py`: Entity details and bulk counterparty queries.
- `backend/app/api/endpoints/heuristics.py`: Bounded peeling chain and mixing pattern summary.
- `backend/app/services/ml_service.py`: Zero-ORM streaming, Isolation Forest, MiniBatchKMeans.
- `backend/app/services/alert_service.py`: Composite risk score calculation and alert synthesis.
- `backend/app/services/evidence_service.py`: Heuristic rule validation and evidence persistence.
- `backend/app/services/dashboard_service.py`: Single-pass SQL aggregation service.
- `backend/app/models/models.py`: Declarative SQLAlchemy models with B-tree indexes.

### Frontend
- `frontend/src/App.tsx`: Route configuration, query client settings, and lazy-loading boundaries.
- `frontend/src/api/client.ts`: Axios instance, 25s timeout, error interceptors.
- `frontend/src/api/hooks.ts`: React Query custom hooks (`useDashboard`, `useAlerts`, etc.).
- `frontend/src/pages/DashboardPage.tsx`: Command Center view, KPI cards, Prioritized Leads queue.
- `frontend/src/pages/AlertsPage.tsx`: Full alert management table with filtering.
- `frontend/src/pages/GraphPage.tsx`: Interactive transaction graph canvas.
- `frontend/src/pages/TransactionsPage.tsx`: Paginated transaction ledger.
- `frontend/src/pages/WalletsPage.tsx`: Searchable entity registry.
- `frontend/src/pages/WalletDetailPage.tsx`: Detailed wallet profile and counterparty breakdown.
- `frontend/vite.config.ts`: Build bundling configuration and vendor manual chunking.

---

## 14. Verification History

- **Backend Pytest Suite:** `53 passed, 3 skipped, 0 failed` in 18.96s [VERIFIED].
- **Frontend Production Build:** `tsc -b && vite build` completed cleanly in 1.07s [VERIFIED].
- **Production Health Probe:** `GET /health` returned `200 OK` in 0.05s with header `x-process-time: 0.003s` [VERIFIED].
- **Production Pipeline Execution:** `POST /api/datasets/6/process` returned `200 OK` in 116.33s on live Render container [VERIFIED].
- **Active Production Commit:** `4f043819f1fb6c9796c2759c165245ee40b39de7` deployed on Render and GitHub Pages [VERIFIED].

---

## 15. FINAL HANDOFF TO NEXT AI AGENT

When resuming work on this repository:
1. **First Check:** Run `python -c "print('HOOK TEST SUCCESS')"` via `run_command` to verify that the telemetry plugin folder has been moved completely out of `plugins\` and tool execution is functional.
2. **Prioritized Leads Investigation:**
   - Do NOT assume the frontend or backend is broken without probing first.
   - Authenticate with `POST https://btc-3jme.onrender.com/api/auth/login` and probe `GET /api/alerts/?limit=10&priority=CRITICAL` and `GET /api/dashboard/`.
   - Inspect the actual returned JSON shape and compare with `DashboardPage.tsx`. Check specifically for `data.items` vs direct array access and `priority === 'CRITICAL'`.
   - Add a verified empty state ("No critical leads pending triage") when 0 items match.
3. **Frontend Speed Hardening:**
   - Implement `React.lazy()` for all route components in `App.tsx` and wrap in `<Suspense fallback={<PageSkeleton />}>`.
   - Configure manual chunks in `vite.config.ts` to isolate `recharts` and graph modules from the initial entry chunk.
   - Implement progressive loading in `DashboardPage.tsx` so KPI stats cards render immediately.
4. **Verification:**
   - Run `pytest tests/ -v` and `npm run build` in `frontend/`.
   - Record actual measured bundle sizes before and after code splitting.
   - Do not commit or push until production behavior is verified.
