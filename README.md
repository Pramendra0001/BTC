# BTC-SHIELD

## AI-Powered Bitcoin Transaction Intelligence, Anomaly Detection & Risk Decision-Support Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-0284c7?style=flat-square&logo=github)](https://pramendra0001.github.io/BTC/)
[![Backend API](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Render-10b981?style=flat-square&logo=fastapi)](https://btc-3jme.onrender.com)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger%20UI-38bdf8?style=flat-square&logo=swagger)](https://btc-3jme.onrender.com/docs)
[![API Health](https://img.shields.io/badge/API%20Health-Live-22c55e?style=flat-square&logo=fastapi)](https://btc-3jme.onrender.com/health)
[![CI Pipeline](https://github.com/Pramendra0001/BTC/actions/workflows/ci.yml/badge.svg)](https://github.com/Pramendra0001/BTC/actions/workflows/ci.yml)
[![Deploy Frontend](https://github.com/Pramendra0001/BTC/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/Pramendra0001/BTC/actions/workflows/deploy-frontend.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![Vite 8](https://img.shields.io/badge/Vite-8-646CFF.svg)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

BTC-SHIELD is an AI-powered Bitcoin intelligence and decision-support platform for transaction risk analysis, anomaly detection, forensic graph investigation, structural heuristic analysis, and explainable blockchain intelligence.

The platform combines on-chain transaction behavior with P2P network telemetry, machine-learning anomaly detection, graph analytics, deterministic structural heuristics, evidence generation, and case-management workflows. It is designed to help investigators and analysts move from raw blockchain data to prioritized, explainable leads without treating algorithmic risk indicators as legal conclusions.

> **Decision-Support Disclaimer:**  
> BTC-SHIELD is an investigatory intelligence and decision-support system. It computes behavioral anomaly scores, surfaces structural heuristics, correlates network telemetry, and generates structured evidentiary records. Algorithmic outputs and risk classifications are analytical indicators, not definitive legal proof or determinations of guilt. Every surfaced lead requires human review, corroborating evidence, and applicable legal due process.

---

## 🌐 Live Project & Access

| Service | Access |
|---|---|
| 🚀 Live Application | [Open BTC-SHIELD](https://pramendra0001.github.io/BTC/) |
| 💻 BTC-SHIELD Project Repository | [View Project on GitHub](https://github.com/Pramendra0001/BTC) |
| ⚙️ Backend API | [FastAPI on Render](https://btc-3jme.onrender.com) |
| 📚 API Documentation | [Interactive Swagger / OpenAPI Docs](https://btc-3jme.onrender.com/docs) |
| ❤️ API Health Check | [Check API Status](https://btc-3jme.onrender.com/health) |
| 🔄 Frontend Deployment | [GitHub Actions Deployment](https://github.com/Pramendra0001/BTC/actions/workflows/deploy-frontend.yml) |
| 🧪 CI & Verification | [GitHub Actions CI](https://github.com/Pramendra0001/BTC/actions/workflows/ci.yml) |

---

## 📖 Project Documentation

Use the sections below as the primary navigation map for the BTC-SHIELD documentation.

- 📌 [Project Overview](#1-executive-summary--problem-addressed)
- 🎯 [Problem Addressed](#1-executive-summary--problem-addressed)
- 🧠 [Core Capabilities](#2-core-platform-capabilities)
- 🏗️ [System Architecture](#3-end-to-end-system-architecture)
- ⚙️ [Core Intelligence Engines](#4-core-intelligence--analytical-engines)
- 🔬 [Risk Scoring Methodology](#5-multi-signal-risk-scoring-methodology)
- 🔄 [End-to-End Workflow](#6-investigation-workflow-ingestion-to-case-dossier)
- 🧩 [Key Modules & User Workflows](#7-key-application-modules--user-workflows)
- 📥 [Data Ingestion & Data Quality](#9-data-quality-framework--integrity-controls)
- 🧾 [Data Sources & Provenance](#8-data-provenance--canonical-datasets)
- 🗂️ [Official vs. Derived vs. Demo / Synthetic Data](#8-data-provenance--canonical-datasets)
- 📊 [Data-Dependent Capabilities](#10-data-dependent-system-capabilities-matrix)
- 💻 [Technology Stack](#11-technology-stack)
- 🛠️ [Installation & Setup](#13-installation--local-development-guide)
- 🔐 [Environment Configuration](#14-environment-configuration)
- ▶️ [Running the Application](#13-installation--local-development-guide)
- 🧪 [Testing & Verification](#15-verification--test-suite-summary)
- 🚀 [Deployment](#16-production-deployment--cloud-architecture)
- 🛡️ [Security & Data Handling Limitations](#17-security-architecture--threat-model)
- 🔭 [Future Integration Possibilities](#20-future-integration-possibilities)

---

## 1. Project Overview

BTC-SHIELD is an AI-powered Bitcoin intelligence and decision-support platform for transaction risk analysis, anomaly detection, forensic graph investigation, structural heuristic analysis, and explainable blockchain intelligence.

The platform combines on-chain transaction behavior with P2P network telemetry, machine-learning anomaly detection, graph analytics, deterministic structural heuristics, evidence generation, and case-management workflows. It is designed to help investigators and analysts move from raw blockchain data to prioritized, explainable leads without treating algorithmic risk indicators as legal conclusions.

## 2. Problem Addressed

Bitcoin's public ledger provides transparent and immutable transaction records, but its pseudo-anonymous structure creates significant challenges for forensic analysis and financial-risk investigation:

1. **Transaction Obfuscation:** Recursive peeling chains, mixing activity, rapid fan-out/fan-in flows, and multi-hop transfers can make suspicious movement difficult to trace.
2. **Network/Ledger Disconnection:** On-chain analysis can lack complementary P2P network context such as source IPs, ASNs, and geographic routing metadata.
3. **Scaling Constraints:** Naive graph and clustering approaches can create excessive memory requirements as transaction and entity cohorts grow.
4. **Evidentiary Opacity:** Black-box risk scores can be difficult to audit, reproduce, and explain to investigators or compliance reviewers.
5. **Investigation Workflow Fragmentation:** Analysts need connected workflows that move from ingestion and data-quality checks through detection, evidence review, alert prioritization, and case documentation.

BTC-SHIELD addresses these challenges through streaming ingestion, behavioral feature engineering, unsupervised anomaly detection, memory-bounded clustering, graph intelligence, deterministic structural heuristics, explainable evidence generation, and structured investigation workflows.

## 3. Core Platform Capabilities

- **Streaming Multi-Format Ingestion:** High-throughput streaming parser for CSV, JSON, and XML ledger/telemetry files with defensive Pydantic validation, schema isolation of malformed records, and duplicate transaction handling.
- **23-Dimensional Behavioral Feature Engineering:** Continuous mathematical profiling covering transaction velocity, burstiness, inter-arrival intervals, value concentration, Shannon entropy of counterparty addresses, and network ASN distribution.
- **Calibrated Unsupervised Anomaly Detection:** Ensemble Isolation Forest (`n_estimators=50`, $\psi=256$) calibrated to normalized $[0, 100]$ risk scores with dynamic contamination bounds ($0.01$ to $0.10$).
- **Dual-Scale Behavioral Cohort Clustering:** Memory-safe clustering engine running exact DBSCAN on small cohorts ($\le 1,000$ entities) and MiniBatch cohort clustering ($k=12$, batch size 2,048) with 97th percentile centroid distance outlier detection on large cohorts ($> 1,000$ entities), strictly capping peak memory at $O(N \cdot K)$.
- **Structural Heuristic Engines:** Rule-based detectors identifying recursive peeling cascades ($\ge 3$ consecutive hops with asymmetric change splits) and high-entropy mixing transactions (equal-denomination outputs with Shannon entropy $H \ge 2.5$).
- **Multi-Entity Directed Graph Intelligence:** Interactive NetworkX and Cytoscape.js multigraph visualization supporting $k$-hop neighborhood expansion, degree/betweenness centrality computation, and shortest-path taint tracking across wallets, transactions, IPs, and ASNs.
- **Rule-Based Deterministic AI Explanations:** Zero-hallucination forensic summary engine generating plain-language analytical rationales derived directly from mathematical feature thresholds and structural heuristics.
- **Court-Ready Case Management & Dossier Export:** Comprehensive investigation workflow supporting entity tagging, evidence attachment, chronological investigator notes, and JSON forensic report export with mandatory legal decision-support disclaimers.
- **Four-Tier Role-Based Access Control (RBAC):** Granular authorization securing administrative, investigative, analytical, and view-only operational boundaries.

---

## 4. End-to-End System Architecture

```text
===================================================================================================
                                      BTC-SHIELD ARCHITECTURE
===================================================================================================

 [ INGESTION & DATA SOURCES ]
      |
      +---> CSV / JSON / XML Ledger & P2P Telemetry Files
      |
      v
 [ INGESTION & VALIDATION ENGINE (app/services/ingestion_service.py) ]
      |
      +---> Defused XML & Streaming Chunk Parser (yield_per 1000)
      +---> Pydantic v2 Schema Normalization & Malformed Record Isolation
      +---> 8-Point Data Quality Rules Enforcement (DQ Score 0-100%)
      |
      v
 [ STORAGE & PERSISTENCE LAYER (app/core/database.py) ]
      |
      +---> Neon PostgreSQL (Production Cloud) / SQLite (Offline / Air-Gapped)
      +---> Relational Schema: Users, Datasets, Transactions, Wallets, IPs, ASNs,
      |     BehavioralFeatures, ModelRuns, AnomalyResults, Evidence, Alerts, Cases
      |
      v
 [ ANALYTICAL & INTELLIGENCE ENGINES ]
      |
      +---> Feature Engineering Engine (app/services/feature_service.py)
      |     * 23 continuous behavioral dimensions (velocity, burstiness, entropy)
      |
      +---> Unsupervised Anomaly Engine (app/services/ml_service.py)
      |     * Isolation Forest (n_estimators=50, max_samples=min(256, N))
      |     * Raw score inversion & [0, 100] normalization
      |
      +---> Dual-Scale Cohort Clustering Engine (app/services/ml_service.py)
      |     * <= 1k entities: Exact DBSCAN (adaptive eps, min_samples=3-10)
      |     * > 1k entities: MiniBatchKMeans (k=12) + Centroid Distance Outlier Thresholding
      |
      +---> Structural Heuristics Engine (app/services/heuristics_service.py)
      |     * Peeling chain cascade detection (>= 3 hops)
      |     * CoinJoin / mixing detection (equal-denomination outputs, entropy >= 2.5)
      |
      +---> Graph & Centrality Engine (app/services/graph_service.py)
      |     * NetworkX DiGraph: Degree, Betweenness, Centrality, Shortest Path
      |
      +---> Alert Prioritization & Evidence Engine (app/services/alert_service.py)
      |     * Dynamic priority rules (CRITICAL, HIGH, MEDIUM, LOW)
      |     * Deterministic evidence record generation & Explainable AI summaries
      |
      v
 [ REST API INTERFACE (FastAPI 0.115+ / Uvicorn) ]
      |
      +---> 20 Domain Routers: /auth, /dashboard, /alerts, /wallets, /transactions,
      |     /network, /graph, /timeline, /evidence, /cases, /models, /heuristics, ...
      |
      v
 [ PRESENTATION LAYER (React 19 / Vite 8 / Tailwind CSS v4) ]
      |
      +---> 24 Code-Split Dynamic Pages (Dashboard, Graph, Alerts, Cases, Heuristics...)
      +---> Cytoscape.js Interactive Network Canvas & Recharts Analytics
      +---> Dual Theme Support (Dark Command Center Default & Light Mode)
===================================================================================================
```

---

## 5. Core Intelligence & Analytical Engines

| # | Intelligence Engine | Implementation Module | Core Algorithm / Methodology | Primary Output / Artifact |
|---|---|---|---|---|
| **1** | **Feature Engineering Engine** | `app/services/feature_service.py` | 23 continuous dimensions: volume, net flow, velocity, burstiness, fan-in/fan-out, counterparty entropy, ASN diversity | `BehavioralFeature` records with JSON feature vector |
| **2** | **Unsupervised Anomaly Detector** | `app/services/ml_service.py` | Calibrated `IsolationForest(n_estimators=50, max_samples=min(256, N), random_state=42)` | Scaled anomaly score ($0-100$) and persisted `joblib` model artifact |
| **3** | **Dual-Scale Cohort Clustering** | `app/services/ml_service.py` | Exact `DBSCAN` for $N \le 1,000$; `MiniBatchKMeans(k=12)` with 97th-percentile centroid distance outlier marking for $N > 1,000$ | Behavioral cohort `cluster_id` and noise label (`-1`) |
| **4** | **Structural Heuristics Engine** | `app/services/heuristics_service.py` | Deterministic graph traversal: recursive peeling chains ($\ge 3$ hops) and Shannon entropy ($H \ge 2.5$) for equal-denomination mixing | `HeuristicPatternResponse` with matched hops and addresses |
| **5** | **Evidence & Alert Prioritizer** | `app/services/alert_service.py` | Multi-signal weighting matrix mapping anomaly scores, heuristic detections, and network diversity to priority tiers | Prioritized `Alert` records and structured `Evidence` cards |

---

## 6. Multi-Signal Risk Scoring Methodology

BTC-SHIELD computes composite risk through a deterministic, explainable multi-signal fusion pipeline:

```text
+---------------------------------------------------------------------------------------+
|                             MULTI-SIGNAL FUSION PIPELINE                              |
+---------------------------------------------------------------------------------------+
|  1. Behavioral Anomaly Score (0 - 100)                                                |
|     S_IF = (( -raw_score - min_score ) / ( max_score - min_score )) * 100            |
|                                                                                       |
|  2. Structural Heuristics Multiplier                                                  |
|     +25 pts: Active participation in recursive peeling cascade (>= 3 hops)             |
|     +30 pts: Involvement in high-entropy CoinJoin / mixing transaction (H >= 2.5)     |
|                                                                                       |
|  3. Network Telemetry Indicators                                                      |
|     +15 pts: Rapid geographic hopping across >= 3 distinct countries in 24 hours      |
|     +10 pts: High ASN diversity / high routing entropy                                |
|                                                                                       |
|  4. Composite Priority Classification                                                 |
|     * CRITICAL (Score >= 80 OR Anomaly + Active Mixing / Peeling)                     |
|     * HIGH     (Score 60 - 79 OR High Behavioral Anomaly)                             |
|     * MEDIUM   (Score 40 - 59 OR Multi-Country Telemetry Discrepancy)                 |
|     * LOW      (Score < 40: Normal Baseline Activity)                                 |
+---------------------------------------------------------------------------------------+
```

Every score modification is accompanied by a discrete `Evidence` record detailing the observed feature values, mathematical thresholds, and contributing signals to maintain strict evidentiary chain-of-custody.

---

## 7. Investigation Workflow: Ingestion to Case Dossier

```text
  [ Step 1: Ingestion ]       User uploads raw CSV, JSON, or XML transaction and telemetry files.
            |
            v
  [ Step 2: Quality Audit ]   System validates schema, computes 8-point data quality metrics, and isolates errors.
            |
            v
  [ Step 3: Entity Profiling] Entity resolution maps unique Wallets, Transactions, IPs, and ASNs.
            |
            v
  [ Step 4: ML & Analytics ]  Feature extraction computes 23 continuous features; Isolation Forest & clustering execute.
            |
            v
  [ Step 5: Heuristics Scan ] Graph algorithms detect peeling chains, mixing transactions, and rapid consolidation.
            |
            v
  [ Step 6: Alert Triage ]    Alert Prioritizer generates prioritized alerts with explainable AI reasoning.
            |
            v
  [ Step 7: Graph Tracking ]  Investigator visualizes $k$-hop subgraphs, expands neighbors, and traces taint flows.
            |
            v
  [ Step 8: Case Dossier ]    Entities & evidence attached to Case; investigator exports courtroom-ready report.
```

---

## 8. Key Application Modules & User Workflows

### 7.1 Command Center Dashboard (`/`)
- Real-time aggregate statistics: Total Monitored Wallets, Ingested Transactions, Active Alerts, System Risk State, and Data Quality Index.
- High-priority alert queue with one-click navigation to underlying entity details.
- Temporal transaction volume distribution and geographical observation breakdown.

### 7.2 Alert Management & Triage (`/alerts`, `/alerts/:id`)
- Paginated, filterable alert registry supporting filtering by priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), review status (`NEW`, `IN_REVIEW`, `RESOLVED`, `FALSE_POSITIVE`), and entity type.
- Alert detail view displaying contributing behavioral signals, anomaly score distribution, linked evidence records, and rule-based AI analytical explanations.

### 7.3 Interactive Graph Intelligence (`/graph`)
- High-performance Cytoscape.js canvas rendering directed multigraph topologies of wallets, transactions, IPs, and ASNs.
- Capabilities: $k$-hop radius expansion, node degree/betweenness centrality styling, shortest-path calculation between suspect addresses, and layout toggling (CoSE, Breadthfirst, Concentric).

### 7.4 Structural Heuristics Explorer (`/heuristics`)
- Dedicated forensic detection interface for:
  - **Peeling Chain Cascade Detector:** Tracing structured fund dissipation across peeling chains with configurable hop thresholds.
  - **CoinJoin / Mixing Detector:** Identifying anonymizing mixing pools via equal-denomination output matching and Shannon entropy calculation.

### 7.5 Case Management & Forensic Dossier Export (`/cases`, `/cases/:id`)
- End-to-end case lifecycle tracking (`OPEN`, `INVESTIGATING`, `CLOSED`, `ARCHIVED`).
- Case workspaces allowing investigators to attach suspect wallets, transactions, evidence items, and timestamped investigator notes.
- One-click **Export Forensic Report** generating a structured JSON dossier complete with entity metadata, chronological audit logs, and mandatory decision-support disclaimers.

### 7.6 Data Quality & Governance Engine (`/data-quality`)
- Real-time audit dashboard reporting adherence across 8 data quality dimensions.
- Tabular breakdown of total ingested records, valid rows, isolated malformed rows, duplicate transactions, and overall Data Quality Index ($0-100\%$).

---

## 9. Data Sources & Provenance

BTC-SHIELD maintains strict separation between synthetic evaluation data, external reference academic benchmarks, and demonstration fixtures:

| Dataset Category | Dataset Name / Source | Size / Dimensions | Provenance & Usage Characterization |
|---|---|---|---|
| **Synthetic Evaluation Benchmark** | **Dataset 6 (BTC-SHIELD Ground-Ready)** | 100,000 transactions<br>45,000 wallets<br>350,131 edges (42.5 MB CSV) | **Synthetic Data.** Generated algorithmically to simulate high-volume transaction flow, peeling chains, mixing patterns, and P2P routing telemetry. Used for empirical load and memory testing. |
| **Public Academic Reference** | **Elliptic Graph Benchmark** | 203,769 transactions<br>234,355 directed edges | **Public Reference Benchmark (External).** Academic Bitcoin transaction graph evaluated during architectural research as a topological baseline for degree distributions. Not bundled in repository due to absence of UTXO fees and raw script structures in Kaggle releases. |
| **Pre-Seeded Demonstration Fixtures** | **Forensic Demonstration Scenarios** | 3 cases<br>4 demo accounts | **Deterministic Demo Fixtures.** Pre-configured case dossiers (`Alpha-Peel Cascade`, `CoinJoin Syndicate`, `Darknet Gateway`) used for offline product demonstrations and evaluation walks. |

> [!NOTE]
> All bundled transaction sets located in `data/samples/` (`btc_shield_synthetic_transactions.*` and `btc_shield_100000_*`) are synthetic research scenarios engineered to model specific financial crime topologies (peeling cascades, CoinJoin mixing, high fan-out disbursements) and evaluate system throughput. They do not contain live surveillance or classified records.


### Official vs. Derived vs. Demo / Synthetic Data

BTC-SHIELD distinguishes between source records, platform-derived intelligence, and demonstration or synthetic benchmark data:

| Data Classification | Meaning |
|---|---|
| 🏛️ **Official / Source Data** | Records or metadata obtained from documented source datasets and public blockchain/network references where available. |
| 🧮 **Derived Data** | Metrics calculated by BTC-SHIELD, including behavioral features, anomaly scores, cluster assignments, graph measures, heuristic matches, and evidence attributes. |
| 🧪 **Demo Data** | Bundled records used to demonstrate application workflows and UI behavior without requiring a live external feed. |
| 🧬 **Synthetic Benchmark Data** | Generated evaluation data used for scale, resilience, anomaly-detection, clustering, and ingestion testing; it is not presented as live network telemetry. |

All data-dependent capabilities should be interpreted according to the source tier and operating mode shown by the application.

---

## 10. Data Ingestion & Data Quality Framework

All ingested data is evaluated against an 8-point automated integrity verification matrix:

| Rule ID | Data Quality Dimension | Verification Rule | Severity | Handling on Violation |
|---|---|---|:---:|---|
| **DQ-01** | **Cryptographic Hash Integrity** | `txid` must be valid 64-character hexadecimal string | Critical | Row rejected; isolated in `RawRecord` error table |
| **DQ-02** | **Address Syntax Validation** | Input/output addresses must match Base58Check (P2PKH/P2SH) or Bech32 (P2WPKH/P2WSH) | Critical | Row rejected; isolated with parse error |
| **DQ-03** | **Non-Negative Value Range** | Value amounts must be positive numbers; fee $\ge 0$ | High | Value clamped or rejected; warning flagged |
| **DQ-04** | **Temporal Sequence Coherence** | Timestamp must be valid UTC ISO-8601 or UNIX epoch within $[2009\text{-}01\text{-}03, \text{now}]$ | High | Normalized to standard UTC or rejected if unparseable |
| **DQ-05** | **IP Address Validity** | Network IPs must conform to valid IPv4/IPv6 syntax | Medium | Validated via Python `ipaddress` module; invalid IPs logged |
| **DQ-06** | **Deduplication Check** | Ingested `txid` must not collide with existing committed records | High | Deduplicated; logged in dataset duplicate counter |
| **DQ-07** | **Fee Conservation Law** | Total input amount must equal total output amount plus transaction fee ($\sum \text{In} = \sum \text{Out} + \text{Fee}$) | Medium | Flagged as balance anomaly; recorded in evidence table |
| **DQ-08** | **XML / Payload Defense** | XML files must not contain DTD entity expansion (Billion Laughs defense) | Critical | Defused via `defusedxml`; parsing aborted on entity expansion |

---

## 11. Data-Dependent Capabilities

| System Capability | Baseline / Offline Fixtures | Synthetic 100k Benchmark | Real-World Network Feeds (Future) |
|---|:---:|:---:|:---:|
| **Authentication & RBAC Enforcement** | Available | Available | Available |
| **Static Heuristic Detection (Peeling/Mixing)** | Available | Available | Available |
| **Interactive Cytoscape Graph Visualization** | Available | Available | Available |
| **Isolation Forest Anomaly Scoring** | Available (Fixture features) | Available (23-dim continuous features) | Requires live feature computation |
| **Dual-Scale Cohort Clustering** | Exact DBSCAN ($\le 1\text{k}$) | MiniBatch KMeans ($> 1\text{k}$) | Scalable MiniBatch KMeans |
| **Court-Ready JSON Report Export** | Available | Available | Available |
| **Real-Time P2P Network Telemetry** | Simulated IP/ASN | Simulated TEST-NET | Requires live node daemon connection |

---

## 12. Technology Stack

### Frontend Architecture
- **Framework:** React 19 (`19.2.8`)
- **Language:** TypeScript (`~6.0.2`)
- **Build Tool:** Vite 8 (`8.3.0`)
- **Styling:** Tailwind CSS v4 (`4.3.3`)
- **Graph Visualization:** Cytoscape.js (`3.34.3`)
- **Analytics & Charting:** Recharts (`3.10.1`)
- **State Management & Caching:** TanStack React Query (`5.103.1`)
- **Icons:** Lucide React (`1.47.0`)
- **Routing:** React Router DOM (`^7.18.4`)

### Backend Architecture
- **Framework:** FastAPI (`>=0.115.0`)
- **ASGI Server:** Uvicorn (`>=0.30.0`)
- **Language:** Python 3.13+
- **Database ORM:** SQLAlchemy 2.0 (`>=2.0.30`) with SQLite (local) and PostgreSQL / Neon (cloud)
- **Data Validation:** Pydantic v2 (`>=2.7.0`) & Pydantic Settings (`>=2.3.0`)
- **Authentication & Cryptography:** Python-Jose (`>=3.3.0`), Passlib with Bcrypt (`>=1.7.4`)
- **XML Parsing Defense:** DefusedXML (`>=0.7.1`)

### Scientific, Graph & Machine Learning
- **Machine Learning:** Scikit-Learn (`>=1.5.0`) — Isolation Forest, DBSCAN, MiniBatchKMeans, StandardScaler, Silhouette Score
- **Data Manipulation:** NumPy (`>=1.26.0`), Polars (`>=1.0.0`), Pandas (`>=2.2.0`)
- **Graph Mathematics:** NetworkX (`>=3.3`) — Centrality metrics, Dijkstra pathfinding, $k$-hop neighborhood expansion
- **Model Serialization:** Joblib (`>=1.4.0`)

---

## 13. Repository Structure

```text
BTC/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/       # 20 distinct API router modules
│   │   │   │   ├── alerts.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── cases.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── data_quality.py
│   │   │   │   ├── graph.py
│   │   │   │   ├── heuristics.py
│   │   │   │   └── ...
│   │   │   └── router.py        # Central API router combining all modules
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic BaseSettings & production security validators
│   │   │   ├── database.py      # SQLAlchemy engine, session maker, base model
│   │   │   └── security.py      # JWT authentication, bcrypt hashing, RBAC decorators
│   │   ├── models/
│   │   │   └── models.py        # SQLAlchemy relational database models
│   │   ├── schemas/
│   │   │   └── schemas.py       # Pydantic v2 request/response schemas
│   │   ├── services/
│   │   │   ├── alert_service.py # Alert generation & prioritization
│   │   │   ├── case_service.py  # Case management & report generation
│   │   │   ├── feature_service.py # 23-dimensional feature computation
│   │   │   ├── graph_service.py # NetworkX graph algorithms & centrality
│   │   │   ├── heuristics_service.py # Peeling & CoinJoin detectors
│   │   │   ├── ingestion_service.py  # Streaming file ingestion & DQ audit
│   │   │   └── ml_service.py    # Isolation Forest & dual-scale clustering
│   │   └── main.py              # Application lifespan, CORS, and startup bootstrap
│   ├── ml_models/               # Persisted joblib model artifacts
│   ├── requirements.txt         # Pinned backend Python dependencies
│   └── Dockerfile               # Backend container configuration
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios HTTP client & API query functions
│   │   ├── components/          # Reusable UI widgets, modals, charts, and tables
│   │   ├── context/             # ThemeContext (dark command center default)
│   │   ├── layouts/             # AppLayout, sidebar navigation, top command bar
│   │   ├── pages/               # 24 lazy-loaded React page views
│   │   └── App.tsx              # React Router setup & QueryClient configuration
│   ├── tests/                   # Frontend unit test suites (auth, theme)
│   ├── package.json             # NPM dependencies & build scripts
│   └── vite.config.ts           # Vite configuration & chunk-splitting rules
├── data/
│   ├── generators/              # Synthetic dataset generation scripts
│   ├── samples/                 # Canonical 100k synthetic dataset & manifests
│   └── schemas/                 # JSON schema contracts
├── deployment/
│   ├── docker/                  # Dockerfiles and Nginx configurations
│   └── github-actions/          # CI/CD deployment definitions
├── docs/                        # Architectural specifications & guides
├── tests/                       # Pytest test suite (57 backend test modules)
├── docker-compose.yml           # Multi-container local orchestration
└── README.md                    # Canonical project documentation
```

---

## 14. Installation, Setup & Running the Application

### Prerequisites
- Python 3.13+
- Node.js 20+ and npm 10+
- Git

### 13.1 Backend Setup
```bash
# Navigate to repository root
cd BTC

# Create and activate Python virtual environment
python -m venv backend/.venv

# Windows activation:
backend\.venv\Scripts\activate

# Linux/macOS activation:
source backend/.venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
pip install pytest httpx

# Start local backend server (SQLite development mode)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.

### 13.2 Frontend Setup
```bash
# Open a new terminal and navigate to frontend directory
cd BTC/frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
The frontend is now accessible at `http://localhost:5173`.

### 13.3 Pre-Seeded Demonstration Accounts

| Role | Username | Email | Default Password | Permissions |
|---|---|---|---|---|
| **ADMINISTRATOR** | `admin` | `admin@btcshield.gov` | `admin123` *(dev)* | Full platform administration, system settings, model retraining |
| **INVESTIGATOR** | `lead_investigator` | `investigator@btcshield.gov` | `Investigator@2026!` | Case management, dossier editing, note attachment, report export |
| **ANALYST** | `aml_analyst` | `analyst@btcshield.gov` | `Analyst@2026!` | Alert triage, heuristic execution, graph exploration, data auditing |
| **VIEWER** | `compliance_viewer` | `viewer@btcshield.gov` | `Viewer@2026!` | Read-only access to dashboards, graph views, and summary statistics |

---

## 15. Environment Configuration

All settings are managed via environment variables and validated at runtime using Pydantic Settings (`backend/app/core/config.py`):

| Variable | Default Value (Development) | Production Requirement | Description |
|---|---|---|---|
| `ENVIRONMENT` | `development` | Set to `production` | Enables production security guardrails and validation |
| `DATABASE_URL` | `sqlite:///btcshield.db` | PostgreSQL URL required | Database connection string (SQLite rejected in production) |
| `JWT_SECRET` | `dev-insecure-secret-key-32-chars-long-min` | Cryptographically random string ($\ge 32$ chars) | Secret key for signing HS256 JWT access tokens |
| `JWT_ALGORITHM` | `HS256` | `HS256` | Cryptographic signature algorithm for access tokens |
| `JWT_EXPIRATION_MINUTES` | `1440` (24 hours) | `480` (8 hours recommended) | Token validity duration |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Exact production URLs | Allowed origins (wildcard `*` rejected in production) |
| `ADMIN_USERNAME` | `admin` | Custom admin handle | Username for initial root administrator account |
| `ADMIN_PASSWORD` | `""` *(falls back to dev default)* | Complex string ($\ge 12$ chars) | Initial administrator password |
| `ADMIN_EMAIL` | `admin@btcshield.gov` | Valid enterprise email | Administrator contact email |
| `AI_PROVIDER` | `mock` | `mock` / `gemini` / `openai` | Analytical narrative provider |
| `LOG_LEVEL` | `INFO` | `INFO` or `WARNING` | Logging verbosity |
| `MAX_UPLOAD_SIZE_MB` | `250` | `250` | Maximum allowed payload size for dataset upload |
| `INGESTION_BATCH_SIZE` | `1000` | `1000` | Batch chunk size for database inserts |
| `GEOIP_DB_PATH` | `data/geoip/GeoLite2-City.mmdb` | Absolute path to local MMDB | Local MaxMind City database (optional; falls back to static RFC 5737 tables when missing) |
| `GEOIP_ASN_DB_PATH` | `data/geoip/GeoLite2-ASN.mmdb` | Absolute path to local MMDB | Local MaxMind ASN database (optional; falls back to static ASN mapping when missing) |

---

## 16. Verification & Test Suite Summary

The repository enforces end-to-end verification through automated tests covering backend API contracts, heuristics, graph math, machine learning pipelines, and frontend client states:

```text
===================================================================================================
                                AUTOMATED TEST VERIFICATION SUMMARY
===================================================================================================
Platform: Windows & Linux (Python 3.13, Node.js v24)
Test Suites:
  - Backend (pytest 9.1.1):           72 passed, 0 skipped, 0 failed in 113.24s (100% pass rate)
  - Frontend (node --test):            8 passed, 0 skipped, 0 failed in 143ms   (100% pass rate)
  - Combined Repository Tests:        80 passed, 0 skipped, 0 failed (100% pass rate)
  - Frontend Production Build:        tsc -b && vite build clean (2,601 modules transformed)
===================================================================================================
```

### Verified Test Suites

#### Backend Test Suites (`pytest tests/ -v`)
- `tests/test_platform_compliance.py`: Comprehensive validation across 12 platform compliance checks (syntax integrity, multi-format ingestion, 23-dim feature vectors, unsupervised Isolation Forest & clustering, peeling cascade heuristics, multigraph centrality, compound alerts, case dossiers, offline deterministic fallback GeoIP, real MMDB reader integration path, RBAC authorization, and air-gapped zero external network call guarantee).
- `tests/test_canonical_files.py`: Full ingestion and entity creation across canonical 1,000-record CSV, JSON, and XML datasets.
- `tests/test_api.py`: Full API endpoint contracts, authentication flows, and privilege escalation prevention.
- `tests/test_graph.py`: Directed graph construction, centrality scoring, and shortest path execution.
- `tests/test_heuristics.py`: Recursive peeling cascade detection and CoinJoin Shannon entropy calculation.
- `tests/test_final_release.py`: Prefix normalization, alert schemas, and case seeding integrity.
- `tests/test_ml_pipeline.py`: Model training, parameter recording, and anomaly score scaling.
- `tests/test_alert_prioritizer.py`: Dynamic priority rule assignment and evidence attachment.
- `tests/test_evidence_engine.py`: Deterministic evidence card generation and threshold recording.
- `tests/test_100k_dataset.py`: Large-dataset streaming ingestion and memory boundary verification.
- `tests/test_feature_engineering.py`: 23-dimensional continuous feature calculation.
- `tests/test_ingestion.py`: CSV/JSON/XML parsing and malformed record isolation.

#### Frontend Test Suites (`frontend/tests/`)
- `frontend/tests/auth.test.ts`: Client authentication state, token persistence, duplicate registration handling, and 409 conflict notifications.
- `frontend/tests/theme.test.ts`: Command center theme state, dark/light persistence, and system media query resolution.

---

## 17. Production Deployment & Cloud Architecture

### Frontend Deployment (GitHub Pages)
- Deployed as a static Single-Page Application (SPA) using GitHub Actions (`.github/workflows/deploy-frontend.yml`).
- Configured with `404.html` SPA redirect fallback to support client-side routing on GitHub Pages.
- Production URL: `https://pramendra0001.github.io/BTC/`

### Backend Deployment (Render Cloud)
- Deployed as a containerized web service running Python 3.13 and Uvicorn.
- Connects to managed cloud PostgreSQL (Neon).
- Production API Base URL: `https://btc-3jme.onrender.com`

### Docker Multi-Container Topology
The repository includes a ready-to-run `docker-compose.yml` for fully air-gapped or on-premises deployment:
```bash
# Launch entire stack locally (Postgres 16, FastAPI Backend, Nginx Frontend)
docker-compose up -d --build
```

---

## 18. Security Architecture & Data Handling Limitations

| Threat / Risk Vector | Mitigating Architectural Control | Enforcement Mechanism |
|---|---|---|
| **Privilege Escalation** | 4-tier Role-Based Access Control (`ADMINISTRATOR`, `INVESTIGATOR`, `ANALYST`, `VIEWER`) | FastAPI dependency injection (`require_role(...)`) on all sensitive routes |
| **Insecure Production Secret** | Startup validation rejects default secrets and strings $< 32$ characters | `model_validator` in `backend/app/core/config.py` raises fatal error |
| **CORS Wildcard Abuse** | Wildcard `*` disallowed when `allow_credentials=True` | Production configuration check enforces explicit domain allowlists |
| **Bcrypt DoS via Long Passwords** | Byte truncation to 72 bytes prior to hashing | `backend/app/core/security.py` truncates UTF-8 bytes to prevent CPU exhaustion |
| **XML Entity Attacks (Billion Laughs)** | Prohibit DTD entity expansions in XML uploads | Parsed via `defusedxml` package; execution aborts upon entity detection |
| **SQL Injection** | Parameterized relational queries across all operations | SQLAlchemy 2.0 ORM query builder; zero string-concatenated SQL queries |
| **Memory Exhaustion (DoS via Large Data)** | Streaming chunk parsing (`yield_per 1000`) and MiniBatch clustering | Zero-ORM raw tuple extraction with bounded $O(N \cdot K)$ memory complexity |
| **Audit Non-Repudiation** | Immutable audit logs recorded for every status change and data export | `AuditLog` database table tracking user ID, IP address, action, and timestamp |

---

## 19. Known Limitations & Edge Cases

1. **Synthetic Telemetry Boundaries:** The 100k evaluation dataset utilizes documentation-only IP ranges (`TEST-NET`) and simulated ASN identifiers. Network telemetry reflects synthetic benchmark scenarios rather than live operational ISP logs.
2. **Cold-Start Latency on Render Free Tier:** The live demonstration backend on Render enters sleep mode after periods of inactivity; initial API requests may experience a 30-50 second cold-start delay while the container spins up.
3. **Sub-Sampled Silhouette Scoring:** Silhouette score evaluation on large cohorts ($> 1,000$ entities) is evaluated on a random representative subsample ($\le 300$ entities) to prevent quadratic computation delays during live ingestion.
4. **Air-Gapped Offline Mode:** When deployed in completely air-gapped environments without external internet connectivity, GeoIP city-level resolution falls back to country/ASN metadata provided in the ingestion stream.

---

## 20. Frequently Asked Questions (FAQ)

#### Q1: Does BTC-SHIELD determine legal guilt or illicit culpability?
**No.** BTC-SHIELD is an investigatory decision-support system. It computes behavioral anomaly scores, surfaces structural heuristics, and identifies statistical outliers. All outputs represent analytical risk indicators that require human investigator validation.

#### Q2: How does BTC-SHIELD avoid crashing on large 100,000-record datasets?
BTC-SHIELD implements a dual-scale clustering architecture: cohorts exceeding 1,000 entities transition from standard DBSCAN (which requires a memory-prohibitive $O(N^2)$ pairwise distance matrix) to `MiniBatchKMeans` with Euclidean centroid distance outlier thresholding, maintaining a compact $O(N \cdot K)$ memory profile.

#### Q3: Can the platform run without an internet connection?
**Yes.** The system natively supports an offline/air-gapped deployment mode utilizing local SQLite persistence and local asset bundles with zero external cloud dependencies.

#### Q4: What makes the AI summaries explainable and courtroom-ready?
The analytical summary assistant uses deterministic rule-based synthesis derived directly from computed feature thresholds, heuristic hop sequences, and evidence records, eliminating generative model hallucinations.

---

## 21. Future Integration Possibilities

- **Live Bitcoin Core Node Integration:** Direct RPC / ZeroMQ connection to Bitcoin Core full nodes for block-by-block streaming ingestion of live mempool and confirmed transactions.
- **Hardware-Security-Module (HSM) Signing:** Cryptographic signing of exported forensic dossiers using PKCS#11 hardware security modules for tamper-evident chain of custody.
- **Graph Neural Network (GNN) Embeddings:** Integration of inductive Graph Convolutional Networks (GCN) or Graph Attention Networks (GAT) for semi-supervised entity role classification.
- **Decentralized VASP Directory Synchronization:** Automated synchronization with OpenVASP / TRISA directory protocols for verified Virtual Asset Service Provider address attribution.

---

### License & Governance
BTC-SHIELD is released under the **MIT License**. See [LICENSE](LICENSE) for details. All investigative workflows must adhere to applicable financial compliance frameworks, data protection regulations, and legal due process standards.
