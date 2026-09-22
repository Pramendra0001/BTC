# BTC-SHIELD — Render Deployment Runbook & Memory Sizing Guide

## 1. Architecture & Resource Allocation

BTC-SHIELD is a high-performance Bitcoin transaction forensics and network intelligence platform. On Render's standard container tier (512 MB RAM ceiling), memory efficiency is paramount.

### Container Tier Specifications
* **Target Environment**: Render Web Service (Docker / Python 3.13 Runtime)
* **cgroup Memory Limit**: `512 MB` (Free / Starter Tier)
* **vCPU Allocation**: Shared / 1-2 vCPU burstable
* **Persistent Disk**: Ephemeral container filesystem; persistent state hosted on **Neon PostgreSQL**

---

## 2. Mandatory Runtime Configuration

### Uvicorn Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
```

> [!CAUTION]
> **Strict Concurrency Rule**: Render's default or automatic worker detection may attempt to launch `WEB_CONCURRENCY=2` or `4` based on host core count. Because the cold BTC-SHIELD scientific application image (FastAPI + SQLAlchemy + Scikit-Learn + Polars + NetworkX) occupies **288.43 MB** of resident RAM:
> * 1 worker: ~288 MB cold, ~350 MB active peak (**SAFE**, 162 MB headroom)
> * 2 workers: $2 \times 288\text{ MB} = 576.86\text{ MB}$ (**IMMEDIATE CGROUP OOM TERMINATION**)
>
> Therefore, `--workers 1` or `WEB_CONCURRENCY=1` is **strictly required**.

---

## 3. Recommended Environment Variables

Configure the following environment variables in the Render Dashboard (**Dashboard -> Web Service -> Environment**):

| Variable | Recommended Value | Purpose / Impact |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Enables production security, disables reloaders and debug logging |
| `WEB_CONCURRENCY` | `1` | Forces single-process worker mode to respect 512 MB ceiling |
| `PYTHONUNBUFFERED` | `1` | Ensures immediate stdout/stderr logging for forensic tracking |
| `MALLOC_ARENA_MAX` | `2` | Limits glibc memory arena fragmentation in multi-threaded Linux containers |
| `DATABASE_URL` | `postgresql://...neon.tech/neondb?sslmode=require` | Connection string to Neon serverless PostgreSQL |
| `JWT_SECRET` | *(64-hex random string)* | Production HMAC-SHA256 signature key |
| `AI_PROVIDER` | `mock` / `deepseek` / `openai` | Reasoning explanation provider |
| `LOG_LEVEL` | `INFO` | Low-overhead structured logging |

---

## 4. Subgraph & Forensics Memory Safety

To protect the 512 MB memory boundary, the following core engineering invariants are active in BTC-SHIELD:

1. **Bounded Ego-Subgraphs**:
   * API endpoints (`/api/graph/{type}/{id}/subgraph`) query PostgreSQL directly using indexed foreign keys (`source_id`, `target_id`) with strict degree limits ($\le 100$ edges).
   * NetworkX graphs are constructed **only for the localized 100-node ego subgraphs** ($<100\text{ KB}$ RAM) rather than loading 500,000 entities into global process memory.
2. **Deterministic Single-Threaded ML Inference**:
   * Scikit-Learn algorithms (`IsolationForest`, `DBSCAN`) run with `n_jobs=1`.
   * Multi-processing forks (`n_jobs=-1` or `joblib.Parallel`) are prohibited to prevent duplicating the 288 MB process memory footprint across subprocesses.
3. **Streamed Dataset Ingestion**:
   * Large relational bundles (e.g. 50 MB `.zip` archives containing 100,000 transactions, 45,000 wallets, and 350,000 edges) are streamed directly to disk via `shutil.copyfileobj` rather than being buffered in memory.
   * SQLAlchemy batches commits in 5,000 to 10,000 row chunks with `db.expire_on_commit=False` and explicit `gc.collect()`.

---

## 5. Health Check & Monitoring

### Health Check Endpoint
* **URL**: `/health` (or `/api/health`)
* **Expected Response**: `{"status": "healthy", "service": "btc-shield-backend"}`
* **Interval**: Configure Render health check to poll `/health` every 15–30 seconds.

### Memory Monitoring Verification
1. Access the **Render Dashboard -> BTC Service -> Metrics -> Memory**.
2. Normal operating profile:
   * **Cold Start Baseline**: ~288 MB - 305 MB
   * **Active Query / Forensics Investigation**: ~320 MB - 355 MB
   * **Headroom Remaining**: ~157 MB - 192 MB (Safe)
3. If memory usage exceeds 450 MB, Render triggers an early memory warning.

---

## 6. OOM Troubleshooting Procedure

If Render reports:
```text
Web Service BTC exceeded its memory limit
Instance restarted
```

Follow this diagnostic checklist:
1. **Check Worker Count**: Confirm that `WEB_CONCURRENCY=1` is set in environment variables and that `uvicorn` is not running with `--workers > 1`.
2. **Inspect Upload Payload**: Verify that uploaded datasets did not attempt to load raw multi-gigabyte files into RAM unbatched.
3. **Verify Graph Query Range**: Confirm that graph analysis queries use ego subgraphs with `depth <= 2` and `limit <= 100`.
4. **Trigger Database Reset (If Corrupted)**: Use `POST /api/datasets/admin/reset-application-data` with admin bearer token to purge orphan memory-consuming test artifacts.
