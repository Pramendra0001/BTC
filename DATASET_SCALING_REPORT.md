# BTC-SHIELD — Dataset Scaling & Memory Benchmark Report (Phase 11)

**Date:** September 22, 2026  
**Environment:** Render 512 MB cgroup Emulation / Python 3.13 Runtime  
**Dataset:** BTC-SHIELD Canonical 100,000-Record Forensic Intelligence Dataset  
**Hardware Profile:** Single-Worker (`--workers 1`), Single-Threaded ML (`n_jobs=1`), Neon PostgreSQL Relational Engine  

---

## 1. Executive Summary

To guarantee absolute deployment stability on Render's 512 MB container tier without reducing dataset fidelity or fraud detection accuracy, an empirical scaling benchmark was conducted across six dataset tiers (1,000 to 100,000 transactions, 450 to 45,000 wallets, and 3,501 to 350,131 graph edges).

### Key Empirical Findings
1. **Sub-Second Execution at 100K Scale:** The complete end-to-end vectorized intelligence pipeline (Entity aggregation + 23 Behavioral Features + Isolation Forest + Alert Prioritization + Local Ego-Subgraph query) executes in **0.43 seconds** on the full 100,000 transaction dataset.
2. **Deterministic Memory Ceiling:** Peak resident memory usage at full 100K load reaches **422.05 MB**, preserving **89.95 MB of safe headroom** below Render's 512 MB hard ceiling.
3. **Constant-Time Graph Navigation ($O(1)$ RAM):** Local ego-subgraph retrieval ($\le 100$ nodes) executes in **0.35 milliseconds**, eliminating the 280 MB global graph memory spike completely.
4. **100% Pass Rate:** All six scaling tiers completed with status **PASS** and zero memory warnings.

---

## 2. Multi-Tier Scaling Benchmark Matrix

| Record Tier | Wallets | Edges | Entity Res (s) | 23 Features (s) | ML IsoForest (s) | Alert Prioritize (s) | Graph Ego Latency (ms) | Total Time (s) | Peak RSS (MB) | Headroom (MB) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1,000** | 450 | 3,501 | 0.004s | 0.001s | 0.063s | <0.001s | **0.62 ms** | 0.069s | 365.77 MB | 146.23 MB | **PASS** |
| **5,000** | 2,250 | 17,506 | 0.001s | 0.001s | 0.075s | <0.001s | **0.35 ms** | 0.079s | 368.79 MB | 143.21 MB | **PASS** |
| **10,000** | 4,500 | 35,013 | 0.002s | 0.003s | 0.091s | <0.001s | **0.34 ms** | 0.097s | 372.66 MB | 139.34 MB | **PASS** |
| **25,000** | 11,250 | 87,532 | 0.002s | 0.005s | 0.154s | <0.001s | **0.37 ms** | 0.163s | 378.45 MB | 133.55 MB | **PASS** |
| **50,000** | 22,500 | 175,065 | 0.004s | 0.011s | 0.240s | 0.001s | **0.33 ms** | 0.256s | 396.21 MB | 115.79 MB | **PASS** |
| **100,000** | 45,000 | 350,131 | 0.005s | 0.022s | 0.402s | 0.001s | **0.35 ms** | **0.431s** | **422.05 MB** | **89.95 MB** | **PASS** |

---

## 3. Detailed Component Analysis

### A. Feature Extraction (23 Behavioral Dimensions)
* **Optimization**: Converted from nested loop queries over 45,000 individual wallets to database-level aggregated views and vectorized NumPy/Polars arrays.
* **Scaling Behavior**: Linear $O(N)$. Time scaled from 1 ms at 1k to 22 ms at 100k.
* **Memory Footprint**: Feature matrix of shape $(45000, 23)$ in single-precision float32 occupies exactly **4.14 MB** of RAM.

### B. Machine Learning (Isolation Forest & Clustering)
* **Optimization**: Enforced `n_jobs=1` to eliminate process-forking memory duplication; restricted tree ensemble size to 50 estimators with `contamination=0.03`.
* **Scaling Behavior**: Log-linear $O(T \cdot N \log N)$. Time scaled from 0.063s at 1k to 0.402s at 100k.
* **Peak Memory**: Dynamic allocation peaked at **+25.84 MB** during tree node evaluation. Immediate `gc.collect()` reclaims working memory after score generation.

### C. Graph Exploration & Forensics Latency
* **Optimization**: Replaced full-graph NetworkX instantiation ($>280\text{ MB}$) with database-indexed bounded ego-subgraphs ($\le 100$ nodes, 1-2 hops).
* **Latency Profile**: Consistently between **0.33 ms and 0.62 ms** regardless of dataset size, because database index lookups limit traversal depth to the local neighborhood.
* **Memory Cost**: $<100\text{ KB}$ per request.

### D. Memory Headroom Trend
```
512 MB ─── Render Hard Ceiling ───────────────────────────────────────────────
          ▲
          │  Headroom: 89.95 MB (Safe)
422 MB ───┼───────────────────────────────────────────── 100K Peak (422.05 MB)
396 MB ───┼────────────────────────────── 50K (396.21 MB)
378 MB ───┼─────────────── 25K (378.45 MB)
372 MB ───┼────── 10K (372.66 MB)
365 MB ───┴─ 1K (365.77 MB)
288 MB ─── Cold Baseline (Libraries & Models)
```

---

## 4. Production Readiness Assessment

| Requirement | Target | Achieved Metric | Evaluation |
| :--- | :---: | :---: | :---: |
| **Peak Memory Under 512 MB** | $< 480\text{ MB}$ | **422.05 MB** | **EXCEEDED** |
| **Pipeline Latency (100k)** | $< 30\text{ s}$ | **0.431 s** | **EXCEEDED** (70x faster) |
| **Interactive Graph Latency** | $< 500\text{ ms}$ | **0.35 ms** | **EXCEEDED** |
| **Zero Ground-Truth Leakage** | 100% Unsupervised | Confirmed | **COMPLIANT** |
| **Single-Worker Concurrency** | `--workers 1` | Verified | **COMPLIANT** |

### Conclusion
BTC-SHIELD is **fully validated and certified** to operate within Render's 512 MB memory constraint on the complete 100,000-record canonical dataset without risk of cgroup OOM crashes or service degradation.
