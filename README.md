# BTC-SHIELD: Bitcoin Transaction & Network Intelligence Platform

> **"From fragmented Bitcoin traffic to explainable investigative intelligence."**

[![CI Pipeline](https://github.com/Pramendra0001/BTC/actions/workflows/ci.yml/badge.svg)](https://github.com/Pramendra0001/BTC/actions/workflows/ci.yml)
[![Deploy Frontend](https://github.com/Pramendra0001/BTC/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/Pramendra0001/BTC/actions/workflows/deploy-frontend.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![Vite 8](https://img.shields.io/badge/Vite-8-646CFF.svg)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Live Demo](https://img.shields.io/badge/Demo-GitHub%20Pages-success.svg)](https://pramendra0001.github.io/BTC/)

**Target Competition:** Smart India Hackathon 2026  
**Problem Statement:** 26146 — AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic  
**Organization:** National Technical Research Organisation (NTRO)  
**Category:** Software | Blockchain & Cybersecurity  

---

## 1. Executive Summary

BTC-SHIELD is an advanced intelligence and link analysis platform developed for the **National Technical Research Organisation (NTRO)**. It solves the critical investigative challenge of correlating on-chain Bitcoin ledger movements (UTXOs, inputs, outputs, script types, fees) with off-chain peer-to-peer network telemetry (relay IP addresses, BGP Autonomous System Numbers [ASNs], TCP ports, and geographic jurisdictions).

### Core Pillars
1. **Strict Evidentiary Provenance:** Zero hallucination. Every risk score, link, and natural language summary traces directly back to raw, immutable database records:
   $$\text{Raw Telemetry} \rightarrow \text{Normalized Entities} \rightarrow \text{23 Behavioral Features} \rightarrow \text{Unsupervised ML} \rightarrow \text{Evidence} \rightarrow \text{Case Dossier}$$
2. **Dual-Mode Deployment:**
   - **Mode A (SIH Finals Mode):** 100% self-contained, air-gapped offline Linux execution (Docker Compose or local Python/Node preview). Zero outbound internet or external API dependencies.
   - **Mode B (Cloud Production Mode):** Single Page Application deployed to GitHub Pages, backed by containerized FastAPI microservices and Neon PostgreSQL.
3. **Multi-Hop Link Analysis:** Interactive Cytoscape.js directed multigraph supporting 1 to 3 hops, hierarchical layouts, PageRank centrality, and forensic image export.
4. **Explainable AI Assistant:** Deterministic, evidence-grounded explainability assistant providing natural language findings, recommended investigative actions, and explicit uncertainty assessments.

---

## 2. System Architecture

```
                                  +---------------------------------------+
                                  |         RAW TELEMETRY INGESTION       |
                                  | CSV / JSON / XML Multi-format Feeds   |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |     ENTITY RESOLUTION & STORAGE       |
                                  | Wallets, Transactions, IPs, ASNs, Geo |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   23-DIMENSIONAL FEATURE EXTRACTION   |
                                  | Volume, Structural, Temporal, Network |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |    UNSUPERVISED ML & ANOMALY RADAR    |
                                  | Isolation Forest (Calibrated 0-100)   |
                                  | DBSCAN Clustering (Adaptive Epsilon)  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   EVIDENCE & ALERT PRIORITIZATION     |
                                  | 8 Signal Categories, Compound Risk    |
                                  +-------------------+-------------------+
                                                      |
                                                      v
+-----------------------------------------------------+-----------------------------------------------------+
|                                              INVESTIGATIVE WORKSPACE                              |
|  - Tactical Command Center (Recharts)               - Cytoscape.js Link Analysis Multigraph               |
|  - Explainable AI Investigation Assistant           - Chronological Vertical Timeline                     |
|  - Case Dossier Workspace & Notes Logger            - Forensic Report Generator (JSON & Print)           |
+-----------------------------------------------------------------------------------------------------------+
```

---

## 3. Platform Modules

| Module | Route | Key Capabilities |
|---|---|---|
| **Command Center** | `/` | Real-time KPIs, Recharts anomaly score distribution histogram, prioritized investigative leads table, model telemetry. |
| **Alert Prioritizer** | `/alerts` | Ranked triage queue filtered by Priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and Status, anomaly heat meters, and confidence sufficiency ratings. |
| **Alert Detail** | `/alerts/:id` | Explainable AI Assistant narrative, contributing evidence signals breakdown, and one-click Promote-to-Case action. |
| **Investigation Graph** | `/graph` | Directed multigraph with concentric/hierarchical layouts, 1-3 hop expansion, node centrality metrics (Degree, PageRank), and PNG export. |
| **Structural Heuristics** | `/heuristics` | Peeling-chain cascade detector, CoinJoin equal-denomination fingerprinting, high-entropy tumbler topology analysis, and single-tx structural analyzer. |
| **Wallet Intelligence** | `/wallets` & `/wallets/:addr` | Financial balances, net flow, recent transactions, correlated network observations, and counterparty interactions. |
| **Transactions** | `/transactions` & `/:txid` | Granular UTXO input/output breakdown, satoshi values, fee rates, script types, and fan-in/fan-out structural classification. |
| **Network Entities** | `/ips/:ip` & `/asns/:asn` | Peer IP observation history, geographic jurisdictions, hosting ASNs, and correlated on-chain actors. |
| **Activity Timeline** | `/timeline` | Vertical chronological event sequencing unifying on-chain transactions and network telemetry events. |
| **Evidence Explorer** | `/evidence` | 5-stage data lineage audit trail from raw observation to verified evidence cards across 8 behavioral categories. |
| **Cases & Reports** | `/cases` & `/cases/:id` | Formal case dossier workspace, entity pinning, immutable evidence links, timestamped investigator notes, and exportable forensic intelligence reports. |
| **Dataset Management** | `/datasets` | Multi-format upload (CSV, JSON, XML), data quality metrics (valid, duplicate, rejected), and one-click ML intelligence pipeline execution. |
| **Data Quality & Quarantine** | `/data-quality` | Ingestion integrity audit, malformed record quarantine viewer, GeoIP/ASN enrichment coverage meters. |
| **Model Lab** | `/models` | Unsupervised model registry, hyperparameter tracking, 23-dimensional feature schema, sample counts, and silhouette scores. |
| **Forensic Audit Trail** | `/audit-logs` | Immutable chain-of-custody logging all investigator logins, dataset uploads, case creations, and forensic report exports with IP and user attribution. |
| **Settings & RBAC** | `/settings` | Role-Based Access Control matrix (ADMINISTRATOR, INVESTIGATOR, ANALYST, VIEWER), asynchronous background pipeline job monitors. |
| **System Telemetry** | `/system` | Live operational health check across REST API, database, scikit-learn ML engine, and NetworkX multigraph. |

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.13+ (or Python 3.11/3.12)
- Node.js 20+ & npm

### Method 1: Local Development (Instant SQLite Mode)

```bash
# 1. Clone the repository
git clone https://github.com/Pramendra0001/BTC.git
cd BTC

# 2. Setup and activate backend virtual environment
python -m venv backend/.venv
# Windows:
backend\.venv\Scripts\activate
# Linux/macOS:
source backend/.venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt
pip install pytest httpx

# 4. Generate synthetic test datasets
python data/generators/generate_dataset.py --size 1000 --format csv --output data/samples

# 5. Start Backend REST API (Port 8000)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In a new terminal:
```bash
# 6. Install frontend dependencies and launch SPA (Port 5173)
cd frontend
npm install
npm run dev
```

Open browser to `http://localhost:5173`  
**Default Credentials:** `admin` / `admin123`

---

### Method 2: Docker Compose (Self-Contained Stack)

```bash
docker compose up -d --build
```
- Frontend: `http://localhost:3000` (or `http://localhost:5173`)
- Backend API Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

---

## 5. Automated Verification & Testing

BTC-SHIELD features a comprehensive automated test suite verifying all architectural layers:

```bash
# Run test suite from repository root:
pytest tests -v
```

### Verified Test Matrix:
- `tests/test_ingestion.py`: CSV, JSON, XML multi-format parsing, address/IP syntax validators, SHA-256 duplicate quarantine.
- `tests/test_feature_engineering.py`: 23 behavioral features, Shannon entropy calculations, inter-arrival burstiness ($CV$).
- `tests/test_ml_pipeline.py`: Isolation Forest anomaly scoring, DBSCAN adaptive epsilon, score normalization ($[0 - 100]$).
- `tests/test_graph.py`: NetworkX directed multigraph, edge typing, Degree/PageRank centrality, Cytoscape JSON output.
- `tests/test_evidence_engine.py`: Evidence signal generation across 8 categories, strength scoring.
- `tests/test_alert_prioritizer.py`: Compound risk calculation, data sufficiency confidence, priority tier classification.
- `tests/test_api.py`: FastAPI REST client endpoints (health, auth, dashboard, cases, heuristics, data quality, audit logs, users, jobs).

**Result: 20 passed in ~16 seconds.**

---

## 6. Technical Documentation Index

Detailed engineering documentation is available in the `docs/` directory:
- [System Architecture](docs/ARCHITECTURE.md) — Comprehensive architectural specification and data flow.
- [System Design & Schemas](docs/SYSTEM_DESIGN.md) — Full SQL schemas, foreign keys, and indexes.
- [REST API Reference](docs/API_REFERENCE.md) — Exhaustive 49-endpoint API contract.
- [Security Architecture & Threat Model](docs/SECURITY.md) — RBAC matrix, JWT, safe XML parsing, and input sanitization.
- [Deployment & Operational Guide](docs/DEPLOYMENT.md) — Mode A (Air-gapped Linux) & Mode B (Cloud Production).
- [Machine Learning Pipeline](docs/ML_PIPELINE.md) — Mathematical formulation and 23 feature dimensions.
- [Graph Schema](docs/GRAPH_SCHEMA.md) — Heterogeneous multigraph ontology and centrality metrics.
- [Air-Gapped Offline Guide](docs/OFFLINE_LINUX_GUIDE.md) — Offline demonstration setup for SIH evaluators.
- [Algorithmic Evaluation Report](docs/EVALUATION_REPORT.md) — Benchmarks, contamination experiments, and latency metrics.
- [10-Minute Jury Demonstration Script](docs/DEMO_SCRIPT.md) — Minute-by-minute evaluation walkthrough for SIH PS 26146.

---

## 7. Compliance & Forensic Disclaimer

> **IMPORTANT NOTICE:** BTC-SHIELD operates strictly on synthetic, simulated, or public on-chain telemetry for academic and competitive evaluation purposes. Outputs generated by machine learning models represent **statistical behavioral anomalies and investigative leads**, not definitive legal determinations of guilt or criminality. All intelligence products require human investigator corroboration.

---

## 8. License

Distributed under the MIT License. See `LICENSE` for details.
