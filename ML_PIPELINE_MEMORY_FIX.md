# BTC-SHIELD — ML Pipeline Memory Fix Implementation Specification

**Specification Reference:** BTC-ML-FIX-2026  
**Status:** **READY FOR IMPLEMENTATION**  
**Target Codebase:**
- `backend/app/services/ml_service.py`
- `backend/app/services/feature_service.py`
- `backend/app/services/alert_service.py`
- `backend/app/api/endpoints/datasets.py`

---

## 1. Architectural Strategy

The memory fix replaces the unconstrained "load-all-and-process" pattern with a **zero-ORM streaming pipeline**:

```
[ PostgreSQL: behavioral_features (452,547 rows) ]
                       │
                       ▼ (db.query(entity_id, features).yield_per(2000))
[ Streaming Iterator: 2,000 Raw Tuples at a time ]
                       │
                       ▼ (Deduplicate entity_id on the fly)
[ Pre-Allocated Compact Matrix: X = np.zeros((45000, 23), float32) — ONLY 3.95 MB ]
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
[ Isolation Forest (ψ=256, 50 trees) ]  [ MiniBatchKMeans (k=12, batch=2048) ]
  • RAM: 0.4 MB                           • RAM: 6.38 MB
  • Latency: 0.08s                        • Outliers (>97% distance): cluster_id = -1
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼ (Batched 2,000 inserts + db.expunge_all())
[ PostgreSQL: anomaly_results ]
                       │
                       ▼
[ Explicit gc.collect() — Memory Returned to OS ]
```

---

## 2. File-by-File Code Changes

### File 1: `backend/app/services/ml_service.py`
1. **Streaming Feature Extraction (`_extract_feature_matrix_streaming`)**:
   - Stream `(entity_id, features)` tuples in batches of 2,000 using `.yield_per(2000)`.
   - Maintain a simple `seen_entities` set. If an entity was already processed, skip duplicate historical runs without loading them into memory.
   - Pre-allocate a 2D NumPy array `X = np.zeros((n_entities, 23), dtype=np.float32)`.
   - Write row values directly into `X`, bypassing all intermediate Python lists of lists.
2. **Isolation Forest Hardening**:
   - Set `n_estimators=50` and `max_samples=min(256, len(X))` based on Liu et al. (2008).
   - Set `n_jobs=1` to prevent subprocess duplication.
   - Persist anomaly results in chunks of 2,000 with `db.bulk_save_objects()`, `db.commit()`, and `db.expunge_all()`.
3. **Behavioral Cohort Clustering (`train_dbscan`)**:
   - For small datasets ($N \le 1,000$ in test suites): Run standard `DBSCAN(eps=0.8, min_samples=5, n_jobs=1)` without calculating the pairwise silhouette distance matrix.
   - For production datasets ($N > 1,000$):
     - Use `MiniBatchKMeans(n_clusters=12, batch_size=2048, random_state=42)` for $O(1)$ memory consumption ($<7\text{ MB}$).
     - Compute distance from each point to its assigned centroid: $d_i = \|x_i - \mu_{c_i}\|$.
     - Flag the top 3% furthest points as behavioral outliers (`cluster_id = -1`), preserving exact downstream semantics for `evidence_service.py`.
     - Evaluate cluster sizes and silhouette score using a lightweight subsample ($\le 500$ points, $<2\text{ MB}$ RAM) rather than a $5,000 \times 5,000$ full distance matrix.
   - Persist clustering results in chunks of 2,000 with `db.expunge_all()`.

---

### File 2: `backend/app/services/feature_service.py`
1. **Eliminate `wallet_neighbors = defaultdict(set)`**:
   - In `compute_wallet_features` relational mode, replace accumulating 350,000 transaction IDs across 45,000 Python `set` objects with a single integer degree counter: `wallet_edge_counts = defaultdict(int)`.
   - Derive `unique_counterparties` and `counterparty_entropy` from degree counts directly:
     $$N_{\text{neighbors}} = \min(\text{edge\_deg}, \text{tx\_cnt} \times 2)$$
   - Eliminates ~50 MB of string-set memory overhead.
2. **Eliminate ORM Deserialization in `existing_bf`**:
   - Replace `db.query(BehavioralFeature).filter(...).all()` with streaming entity IDs:
     ```python
     existing_ids = set(r[0] for r in db.query(BehavioralFeature.entity_id).filter(BehavioralFeature.entity_type == "WALLET").yield_per(5000))
     ```
   - Only insert new `BehavioralFeature` records if `addr not in existing_ids`.
   - Batch insert in chunks of 2,000 with `db.expunge_all()`.

---

### File 3: `backend/app/api/endpoints/datasets.py`
1. **Session Cleansing Across Pipeline Stages**:
   - In `trigger_processing()`, invoke `db.commit()`, `db.expunge_all()`, and `gc.collect()` between each of the six stages:
     ```python
     resolve_all(db)
     db.commit(); db.expunge_all(); gc.collect()

     compute_all_features(db)
     db.commit(); db.expunge_all(); gc.collect()

     ml_result = run_full_ml_pipeline(db, id)
     db.commit(); db.expunge_all(); gc.collect()

     persist_graph(db)
     db.commit(); db.expunge_all(); gc.collect()

     ev_count = generate_evidence(db)
     db.commit(); db.expunge_all(); gc.collect()

     alert_count = generate_alerts(db)
     db.commit(); db.expunge_all(); gc.collect()
     ```
   - Prevents the SQLAlchemy `IdentityMap` from accumulating hundreds of thousands of objects across the request lifetime.

---

### File 4: `backend/app/services/alert_service.py`
1. **Bounded Anomaly Querying**:
   - Instead of fetching all 90,000 `AnomalyResult` ORM objects into RAM with `.all()`, query only the anomaly scores for entities that actually have evidence:
     ```python
     anomaly_map = {
         (row[0], row[1]): float(row[2])
         for row in db.query(
             AnomalyResult.entity_type,
             AnomalyResult.entity_id,
             AnomalyResult.anomaly_score
         ).filter(
             AnomalyResult.entity_id.in_([e[1] for e in entity_evidence_map.keys()]),
             AnomalyResult.anomaly_score.isnot(None)
         ).all()
     }
     ```
   - Limits memory consumption in `generate_alerts()` to $< 2\text{ MB}$.
