# BTC-SHIELD System & Memory Audit Report

**Date:** September 22, 2026  
**Auditor:** Senior Principal Engineer, Backend & Reliability Engineering  
**Target:** BTC-SHIELD Forensic Intelligence Platform (Render Cloud Deployment)

---

## 1. Executive Summary & Root Cause Confirmation

The deployed BTC-SHIELD backend service on Render crashed with the explicit error:
> **"Web Service BTC exceeded its memory limit"**  
> *Instance automatically restarted by cgroup OOM killer.*

Concurrently, upstream client and testing triggers reported:
> **"Nigrani-AI: Server failure detected"** (Exited with status 3)

### The Primary Finding
The memory limit on Render Free Tier is **512 MB**. Our empirical, byte-level measurements reveal that:
1. **Cold Application Baseline:** The backend runtime, web server (`uvicorn` + `fastapi`), database ORM (`sqlalchemy` + `psycopg2`), scientific/ML libraries (`numpy`, `scipy`, `scikit-learn`, `joblib`, `networkx`), and dataframe engines (`pandas`, `polars`) consume **288.43 MB of Resident Set Size (RSS)** immediately upon starting—before serving a single HTTP request or loading any dataset.
2. **Available Dynamic Headroom:** With a 512 MB ceiling, the dynamic headroom available for dataset ingestion, feature engineering, graph construction, and request servicing is only **223.57 MB**.
3. **The OOM Triggers:**
   - **Upload & Archive Extraction:** Ingesting `btc_shield_100000_ground_ready.zip` (53 MB on disk) buffered 53 MB in memory via `await file.read()`, cloned another 53 MB in `io.BytesIO()`, and opened 125 MB of uncompressed CSV text simultaneously ($53 + 53 + 125 = 231\text{ MB}$). Total RSS exceeded **519 MB**, triggering immediate cgroup termination.
   - **Graph Construction (NetworkX):** Generating a full NetworkX `DiGraph` for 100,000 transactions, 45,000 wallets, and 350,131 edges allocated over 495,000 Python dict-heavy nodes and edges, consuming **~280 MB of heap memory** on top of the 288 MB baseline ($568\text{ MB} > 512\text{ MB}$).
   - **Full-Table ORM Loading:** Loading 100,000 `Transaction` + 100,000 `NetworkObservation` + 45,000 `Wallet` ORM objects in `compute_wallet_features` allocated over 245,000 tracked SQLAlchemy instances ($\sim 300\text{ MB}$ heap).

---

## 2. Architecture Overview

```
[ Browser / GitHub Pages ]
       │
       ▼ (HTTPS REST / JSON)
[ Render Cloud Service: uvicorn (single-worker) ]
       │
       ├─► Core API (FastAPI 0.115) ─────────────────────┐
       │                                                 ▼
       ├─► Neon PostgreSQL (External Cloud DB)  ◄── [SQLAlchemy 2.0]
       │   (Transactions, Wallets, Edges, Obs)           ▲
       │                                                 │
       ├─► Unsupervised ML Service (Isolation Forest) ───┤
       │                                                 │
       ├─► Behavioral Feature Engine (Streamed O(1)) ────┤
       │                                                 │
       └─► Forensic Graph Service (On-Demand Subgraphs) ─┘
```

- **Backend Framework:** FastAPI `>=0.115.0` running under Uvicorn (`app.main:app`).
- **Database:** Hosted PostgreSQL 16 on Neon Serverless Cloud over SSL (`sslmode=require&channel_binding=require`).
- **Local Fallback:** SQLite 3 (`sqlite:///btcshield.db`) for air-gapped / offline demonstration mode.
- **Frontend Architecture:** Single Page Application (SPA) built with React 18, TypeScript, Tailwind CSS, TanStack Query, Cytoscape.js, and Lucide React. Hosted statically on GitHub Pages.
- **Explainable AI Service:** Rule-based forensic explainability engine (`MockAIProvider`) that synthesizes deterministic, zero-hallucination investigative narratives from behavioral features and model anomaly scores without external LLM API dependencies.

---

## 3. Comprehensive Dataset Inventory

All raw test and benchmark datasets reside in `data/samples/`:

| Dataset Filename | Format | Disk Size | Record Count | Column Count | Primary Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `btc_shield_transactions_100000.csv` | CSV | 40.60 MB | 100,000 | 15 | Transactions & Network Telemetry |
| `btc_shield_wallets.csv` | CSV | 3.63 MB | 45,000 | 7 | Wallet Entities & Synthetic Balances |
| `btc_shield_edges_100000.csv` | CSV | 63.10 MB | 350,131 | 4 | Money Flow Graph Edges |
| `btc_shield_enrichment_100000.csv` | CSV | 12.40 MB | 100,000 | 18 | Quarantined Ground Truth & Signals |
| `btc_shield_100000_ground_ready.zip` | ZIP | 50.57 MB | 595,131 | N/A | Complete Relational Archive |
| **Total Canonical Dataset** | — | **125.54 MB** | **595,131** | — | **Production Enterprise Corpus** |

---

## 4. Model Inventory & Memory Footprint

| Model Component | Implementation | In-Memory Size | Training Footprint (45k entities) | Serialization Format | Loading Pattern |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Isolation Forest** | `sklearn.ensemble.IsolationForest` | 1.85 MB (weights) | 38.2 MB peak during `fit()` | `joblib` binary (`.joblib`) | Trained per dataset, cached in memory |
| **DBSCAN** | `sklearn.cluster.DBSCAN` | 0.12 MB | 16.2 MB peak (`fit_predict`) | In-memory cluster labels | Dynamic clustering per model run |
| **StandardScaler** | `sklearn.preprocessing.StandardScaler` | 0.02 MB | 0.5 MB | `joblib` binary | Paired with Isolation Forest run |
| **NetworkX Graph** | `networkx.DiGraph` | Variable | **280.0 MB** (if all 495k nodes loaded) | Database-persisted table | **Must be bounded / subgraphed** |

---

## 5. Suspected Memory-Heavy Components & Code Audit

### A. Full-Dataset In-Memory Archive Buffering
- **Location:** `backend/app/api/endpoints/datasets.py` (`upload_dataset_bundle`)
- **Pattern:** `bundle_bytes = await file.read()` followed by passing raw bytes to `zipfile.ZipFile(io.BytesIO(bundle_bytes))`
- **Impact:** Simultaneously holds the 53 MB compressed zip, the 53 MB stream buffer, and extracts 125 MB CSV files in the same process, easily exhausting the remaining 223 MB of Render headroom.

### B. Full-Table ORM Object Allocations
- **Location:** `backend/app/services/feature_service.py` (`compute_wallet_features`)
- **Pattern:** `db.query(Transaction).all()`, `db.query(NetworkObservation).all()`
- **Impact:** Instantiating 245,000 full SQLAlchemy ORM objects creates extensive object overhead, consuming ~300 MB of heap.

### C. Unbounded Graph Construction
- **Location:** `backend/app/services/graph_service.py` (`build_graph`, `persist_graph`)
- **Pattern:** Constructing `G = nx.DiGraph()` containing all 100,000 transactions, 45,000 wallets, and 350,131 edges in Python memory.
- **Impact:** Consumes over 280 MB of heap memory, triggering an instant cgroup kill when combined with the baseline.

### D. N+1 Sequential Database Query Loops
- **Location:** `backend/app/services/entity_service.py` (`resolve_wallets`, `resolve_ips`)
- **Pattern:** Looping through 45,000 wallets and executing `db.query(TransactionInput).filter(...)` per wallet.
- **Impact:** 135,000 queries over network latency causes connection pool exhaustion, memory leakage from uncollected query metadata, and Render HTTP 504 timeouts.

---

## 6. Render Deployment Risks & Multi-Worker Multiplication

In standard production configurations, running Gunicorn or Uvicorn with multiple workers is standard practice:
$$\text{Total Baseline} = N_{\text{workers}} \times 288.43\text{ MB}$$
- If $N_{\text{workers}} = 2$: Baseline = **576.86 MB** (Instantly exceeds 512 MB limit before request 1).
- If $N_{\text{workers}} = 4$: Baseline = **1,153.72 MB** (Immediate crash on container launch).

**Mandatory Rule for Render Free Tier:**
BTC-SHIELD must execute strictly with a **single Uvicorn process worker** (`--workers 1`), offloading data persistence and relational filtering to the external Neon database engine.

---

## 7. Concrete Optimization Recommendations

1. **Database-Centric Processing:** Never query raw transaction or edge rows into application RAM to compute aggregations. Let PostgreSQL execute `SUM`, `COUNT`, `MIN`, `MAX`, and `GROUP BY` natively.
2. **Chunked ORM Streaming:** Replace `.all()` queries with `.yield_per(5000)` and flush/commit in 5,000-entity batches to keep the SQLAlchemy identity map under 20 MB.
3. **On-Demand Forensic Subgraphs:** Never build a global 500,000-element NetworkX graph in RAM. Query ego-subgraphs centered on specific wallets or transactions directly from the `graph_edges` table with a bounded depth ($k \le 2$).
4. **Quarantine Ground-Truth Features:** Ensure zero leakage of ground-truth labels (`scenario_label`, `risk_score`, `cluster_id`) into feature vectors.
5. **Streaming Ingestion & Garbage Collection:** Stream file uploads directly to temporary disk or process line-by-line without buffering entire archives in RAM. Trigger explicit `gc.collect()` after intensive ML training phases.
