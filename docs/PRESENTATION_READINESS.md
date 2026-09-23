# BTC-SHIELD — Presentation Readiness & Pre-SIH Final Verification Dossier

**Smart India Hackathon 2026 — Problem Statement ID: 26146**  
**Track:** National Technical Research Organisation (NTRO)  
**System Version:** Release Candidate v1.0.0 (Production Hardened)  
**Target Environment:** Air-gapped forensic deployment ready • Cloud validated  
**Production URLs:**
- **Frontend Dashboard:** [https://pramendra0001.github.io/BTC/](https://pramendra0001.github.io/BTC/)
- **Backend API Engine:** `https://btc-3jme.onrender.com`
- **Interactive OpenAPI Specification:** `https://btc-3jme.onrender.com/docs`

---

## 1. Executive Summary & Forensic Alignment

BTC-SHIELD is an end-to-end Bitcoin transaction intelligence and forensic link analysis platform engineered specifically for law enforcement, intelligence analysts (NTRO), and AML investigators.

### Key Capabilities Aligned with SIH 26146:
1. **Multi-Signal Anomaly Detection:** Ensemble unsupervised ML engine combining Isolation Forest, Local Outlier Factor (LOF), and DBSCAN with heuristic rules (velocity bursts, structural fan-in/fan-out, geo-hopping, fee anomalies).
2. **Prioritized Leads Queue:** Automatic triaging and risk-scoring of on-chain anomalies, routing critical alerts (scores $\ge 80$) to senior investigators with full explainability.
3. **Investigation Link Analysis Graph:** Multi-hop relational graph engine linking Bitcoin wallets, transactions, counterparties, network IP addresses, autonomous systems (ASNs), and sovereign countries.
4. **Structural Heuristics Engine:** Algorithmic identification of peeling chains, CoinJoin equal-denomination rounds, and tumbler topologies across arbitrary dataset formats.
5. **Forensic Case & Dossier Management:** Investigative lifecycle from alert escalation to evidence correlation, investigator notes, and tamper-evident PDF/JSON forensic reports with legal disclaimers.
6. **Role-Based Access Control (RBAC):** Strict four-tier permission model (`ADMINISTRATOR`, `INVESTIGATOR`, `ANALYST`, `VIEWER`) enforced via signed JWTs with bcrypt password hashing.

---

## 2. Proven Production Bug Fixes & Root Cause Audits

| Module | Observed Bug | Proven Root Cause | Implemented Resolution | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Investigation Graph** | `Nodes: 1, Edges: 0` (1-dot bug) | 1. Double prefixing (`WALLET:WALLET:addr`).<br>2. Dataset 6 stored wallets in `GraphEdge.properties` rather than `source_id`.<br>3. Relational transactions were not connected to wallet nodes. | Added `normalize_entity_key` to strip redundant prefixes. Implemented dual-schema resolution querying direct edges, relational `properties`, and raw audit logs. Default entity query selects top-degree wallet. | **VERIFIED** (7 nodes, 6 edges on default entity, multi-hop cascades active) |
| **Structural Heuristics** | All metric cards displayed `0` | `detect_peeling_chains` and `detect_mixing_patterns` queried `TransactionInput`/`Output` tables, which are empty in relational 100k mode. | Implemented `get_tx_io_map` abstraction that seamlessly parses `RawRecord.raw_data` inputs/outputs when dedicated tables are unpopulated. | **VERIFIED** (100 peeling chains, 75 mixing transactions detected in <50ms) |
| **Alert Detail View** | `500 Internal Server Error` on click | `contributing_signals` was stored as `list[dict]`, but Pydantic `AlertDetailResponse` declared `Dict[str, Any]` (type mismatch). | Updated schema to `Optional[Union[Dict[str, Any], List[Any]]] = None` with default fallbacks for optional timestamps. | **VERIFIED** (200 OK, full alert detail and evidence cards render) |
| **Cases & Dossiers** | Empty state / 0 cases | Case service existed but had no presentation seeding routine. | Added idempotent `seed_presentation_cases()` generating 3 evidence-backed cases linked to top database alerts and wallets. | **VERIFIED** (3 cases seeded: Behavioral Anomaly, Peeling Chain, Geo-Hopping) |
| **Settings & RBAC** | Only 1 user account visible | Only admin user was bootstrapped on startup. | Added `bootstrap_system_users()` to seed all 4 roles (`admin`, `lead_investigator`, `aml_analyst`, `compliance_viewer`). | **VERIFIED** (All 4 roles active and visible in Settings table) |
| **Frontend Speed** | Sluggish initial page load (multiple seconds) | Monolithic synchronous bundling of all 25 page components and heavy libraries (Recharts, Cytoscape) into a single 1.5MB JS bundle. | Configured `React.lazy()` dynamic imports with `<Suspense>` skeletons and Vite Rollup `manualChunks` code splitting. | **VERIFIED** (Entry bundle reduced to 24 kB; built in 799ms) |

---

## 3. Production Architecture & Performance Verification

### Bundle Size Optimization (Measured via Vite):
- **Core Entry Bundle:** `24.25 kB` (gzip: `6.87 kB`) — *Application shell renders in ~1 second*
- **React Vendor Chunk:** `265.20 kB` (gzip: `84.87 kB`)
- **Query & HTTP Vendor Chunk:** `49.95 kB` (gzip: `18.75 kB`)
- **Recharts Chunk:** `368.11 kB` (gzip: `106.81 kB`) — *Only loaded when viewing charts*
- **Cytoscape Graph Chunk:** `434.85 kB` (gzip: `137.78 kB`) — *Only loaded on `/graph`*
- **Page-specific Chunks:** `2.3 kB – 16.7 kB` each

### Backend Memory & Concurrency Guardrails:
- Single synchronous worker (`WEB_CONCURRENCY=1`) to prevent Render 512 MB memory exhaustion.
- Bounded database queries (`limit`, `yield_per`, SQL-level scalar aggregations) with zero full-dataset in-memory graph instantiations.
- Database index coverage on `(source_id, target_id)`, `(entity_type, entity_id)`, and `(anomaly_score DESC)`.

---

## 4. Live Demonstration Script for Judges & Evaluators

### Flow 1: Command Center & Prioritized Leads (2 minutes)
1. Open [https://pramendra0001.github.io/BTC/](https://pramendra0001.github.io/BTC/).
2. Point out instant rendering of the operational shell, KPI metrics (Total Transactions, Active Wallets, Monitored IPs, Investigative Alerts).
3. Scroll to **Recent High-Priority Leads**: Highlight that alerts are ranked by anomaly score descending ($\ge 90$).
4. Click **Investigate** on the top lead to navigate directly to `/alerts/{id}`.

### Flow 2: Alert Detail & Explainable Forensic Evidence (1.5 minutes)
1. In Alert Detail, show the **Anomaly Score Gauge** (e.g. 98.4 / 100) and **Risk Classification** (`CRITICAL`).
2. Point to the **Model Signals & Contributing Factors**: explain why the ML model flagged the entity (e.g. `VELOCITY_BURST`, `FAN_OUT_RATIO`, `GEO_HOPPING`).
3. Point to the **Correlated Forensic Evidence Records** with cryptographic audit trail.
4. Click **Open in Link Graph** or **Create Case**.

### Flow 3: Investigation Link Analysis Graph (2.5 minutes)
1. Navigate to `/graph`. Notice the automatic selection of the top anomalous entity.
2. Observe the Cytoscape graph canvas rendering the central Wallet connected to:
   - Transaction nodes (`INPUT_OF` and `OUTPUT_OF`)
   - Counterparty wallets
   - IP observations (`OBSERVED_FROM`)
   - Autonomous Systems (`BELONGS_TO_ASN`)
3. Switch **HOPS** from `1` to `2` to `3`: explain bounded expansion preventing browser lag.
4. Use the search box to center on any specific wallet or IP address.

### Flow 4: Structural Heuristics & Mixing Detection (2 minutes)
1. Navigate to `/heuristics`.
2. Review the KPI banner: **100 Peeling Chains Detected**, **75 Mixing Transactions Detected**, cumulative structuring volumes.
3. Switch between **Peeling Chains** and **CoinJoin / Mixing** tabs.
4. Expand a peeling chain: show the sequential hops, peeled amount vs. change amount, and confidence scores.
5. In the Transaction Inspector, search any transaction ID to see immediate entropy and structural pattern detection (`COINJOIN_EQUAL_OUTPUTS`, `MANY_TO_MANY_TUMBLER`, `PEELING_CHAIN_STEP`).

### Flow 5: Cases & Formal Forensic Reports (1.5 minutes)
1. Navigate to `/cases`. Show the 3 active presentation cases.
2. Open **High-Velocity Multi-Signal Behavioral Anomaly**.
3. Point out attached entities, attached evidence records, and dated investigator notes.
4. Click **Export Forensic Report**: show the complete structured dossier with legal disclaimer.

### Flow 6: Role-Based Access Control & System Settings (1 minute)
1. Navigate to `/settings`.
2. Highlight the 4 active roles: `ADMINISTRATOR`, `INVESTIGATOR`, `ANALYST`, and `VIEWER`.
3. Demonstrate air-gapped forensic mode indicator and dual SQLite/PostgreSQL compatibility.

---

## 5. Automated Test Verification Summary

```text
============================== Test Execution Summary ==============================
Platform: Windows (Python 3.13.14, Node.js v24.13.3)
Test Suites:
  - Backend (pytest): 57 passed, 3 skipped, 0 failed (100% pass rate)
  - Frontend (node test): 8 passed, 0 failed (100% pass rate)
  - Build Validation: npm run build completed cleanly in 799ms
====================================================================================
```

### Verified Passing Suites:
- `tests/test_api.py` (Full API endpoint and auth contracts)
- `tests/test_graph.py` (Graph construction, centrality, and persistence)
- `tests/test_heuristics.py` (Peeling and mixing detection)
- `tests/test_final_release.py` (Prefix normalization, alert schemas, case seeding)
- `tests/test_ml_pipeline.py` (ML model training and anomaly scoring)
- `tests/test_alert_prioritizer.py` (Priority rule assignment)
- `tests/test_evidence_engine.py` (Deterministic evidence generation)
- `frontend/tests/auth.test.ts` (Client authentication and token persistence)
- `frontend/tests/theme.test.ts` (Command center theme state management)
