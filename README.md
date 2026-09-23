# BTC-SHIELD: Bitcoin Transaction & Network Intelligence Platform

> **"Transforming fragmented on-chain Bitcoin ledger movements and off-chain P2P network telemetry into explainable, court-ready forensic intelligence."**

[![CI Pipeline](https://github.com/Pramendra0001/BTC/actions/workflows/ci.yml/badge.svg)](https://github.com/Pramendra0001/BTC/actions/workflows/ci.yml)
[![Deploy Frontend](https://github.com/Pramendra0001/BTC/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/Pramendra0001/BTC/actions/workflows/deploy-frontend.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![Vite 8](https://img.shields.io/badge/Vite-8-646CFF.svg)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-65%20Passed%20%7C%203%20Skipped-success.svg)](#19-testing--verification)

**Target Competition:** Smart India Hackathon 2026 Grand Finale  
**Problem Statement ID:** 26146 — AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic  
**Sponsoring Organization:** National Technical Research Organisation (NTRO)  
**Category:** Software | Blockchain Intelligence & Cybersecurity  
**Deployment Topologies:** Mode A (Air-Gapped Offline Linux Demonstration) & Mode B (Production Cloud Architecture)

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Problem Addressed](#2-problem-addressed)
3. [SIH 26146 Alignment](#3-sih-26146-alignment)
4. [Core Capabilities](#4-core-capabilities)
5. [System Architecture](#5-system-architecture)
6. [Intelligence & Analytical Engines](#6-intelligence--analytical-engines)
7. [End-to-End Forensic Workflow](#7-end-to-end-forensic-workflow)
8. [Platform Modules](#8-platform-modules)
9. [Data Ingestion & Data Quality](#9-data-ingestion--data-quality)
10. [Data Provenance](#10-data-provenance)
11. [Official vs. Derived vs. Synthetic / Demo Data](#11-official-vs-derived-vs-synthetic--demo-data)
12. [Machine Learning Methodology](#12-machine-learning-methodology)
13. [Explainability & Evidence Generation](#13-explainability--evidence-generation)
14. [Security Architecture & Role-Based Access Control](#14-security-architecture--role-based-access-control)
15. [Technology Stack](#15-technology-stack)
16. [Quickstart Guide](#16-quickstart-guide)
17. [Offline & Air-Gapped Deployment](#17-offline--air-gapped-deployment)
18. [Cloud Deployment Architecture](#18-cloud-deployment-architecture)
19. [Testing & Verification](#19-testing--verification)
20. [Performance & Memory Engineering](#20-performance--memory-engineering)
21. [System Limitations](#21-system-limitations)
22. [Future Integrations & Roadmap](#22-future-integrations--roadmap)
23. [Presentation & Demonstration Flow](#23-presentation--demonstration-flow)
24. [Compliance & Forensic Disclaimer](#24-compliance--forensic-disclaimer)

---

## 1. Executive Summary

**BTC-SHIELD** is an enterprise-grade forensic intelligence and link-analysis system architected specifically for the **National Technical Research Organisation (NTRO)**. It bridges the fundamental investigative gap between pseudonymous, on-chain Bitcoin UTXO ledger activity and off-chain peer-to-peer network propagation telemetry.

By fusing on-chain transaction mechanics (inputs, outputs, scripts, fees, locktimes) with off-chain network telemetry (relay node IP addresses, Autonomous System Numbers [ASNs], TCP ports, geographic jurisdictions, and broadcast timestamps), BTC-SHIELD surfaces illicit financial obfuscation techniques—including high-frequency peeling chains, CoinJoin mixers, nested tumblers, burst velocity routing, and rapid cross-border geo-hopping.

### Foundational Principles
- **Strict Evidentiary Provenance:** Zero synthetic hallucinations. Every risk score, network edge, and natural language summary traces directly back to immutable raw database records.
- **Dual-Scale Algorithmic Truth:** Unsupervised anomaly scoring via ensemble Isolation Forest combined with a dual-scale clustering architecture (exact DBSCAN for small investigative cohorts $\le 1,000$ entities; memory-efficient MiniBatchKMeans centroid-distance outlier thresholding for large cohorts $> 1,000$ entities).
- **Dual-Mode Operational Readiness:** Fully functional in 100% air-gapped, zero-egress offline Linux environments (Mode A for SIH jury evaluation) and high-availability cloud configurations (Mode B on Render and Neon PostgreSQL).
- **Court-Admissible Dossier Export:** Structured Case Management module with cryptographic SHA-256 chain-of-custody signatures and printable forensic PDF/JSON dossiers.

---

## 2. Problem Addressed

Investigating suspicious financial activity on the Bitcoin network presents severe operational challenges for intelligence and law enforcement agencies:

1. **Pseudonymity & UTXO Fragmentation:** Bitcoin transactions do not record real-world identities. Wallets rotate addresses per transaction, fragmenting funds across hundreds of ephemeral unspent transaction outputs (UTXOs).
2. **Advanced Obfuscation Topology:** Malicious actors utilize automated tumbling cascades (peeling chains where micro-payments are peeled off into merchant services while change cycles indefinitely) and collaborative CoinJoin transactions (equal-denomination outputs with maximum Shannon entropy) to confound traditional heuristic analysis.
3. **Decoupled Network Observation:** On-chain ledger explorers lack awareness of where or how a transaction was introduced to the P2P broadcast swarm. Conversely, network surveillance appliances observe IP packets but lack UTXO transaction context.
4. **Volume & Alert Fatigue:** High-throughput Bitcoin traffic generates thousands of statistical anomalies. Without compound risk scoring, data sufficiency confidence weighting, and deterministic natural-language reasoning, forensic investigators drown in false-positive noise.

**BTC-SHIELD resolves these challenges** by establishing a unified bipartite graph correlating ledger events with network telemetry, extracting 23 behavioral features, executing calibrated anomaly models, and generating evidence-grounded investigative dossiers.

---

## 3. SIH 26146 Alignment

BTC-SHIELD fulfills **100% of the functional, technical, algorithmic, and operational mandates** specified in NTRO Problem Statement 26146:

| Requirement | Implementation | API / Module | Verification Test | Current Status |
|---|---|---|---|---|
| **1. Multi-Format Ingestion** | Streaming parser supporting CSV, JSON (arrays & object envelopes), and XML (`<records><record>...`). | `POST /api/datasets/upload`<br>`backend/app/services/ingestion_service.py` | `tests/test_ingestion.py::<br>test_csv_ingestion`<br>`test_json_ingestion`<br>`test_xml_ingestion` | **PASS (Verified)** |
| **2. Syntax & Integrity Validation** | Deterministic syntax validators for Base58/Bech32 addresses, IPv4/IPv6, SHA-256 txid hashes, and satoshi range limits. | `POST /api/datasets/validate`<br>`backend/app/services/ingestion_service.py` | `tests/test_ingestion.py::<br>test_record_validation` | **PASS (Verified)** |
| **3. Data Quality & Quarantine** | Non-blocking quarantine subsystem isolating malformed or duplicate records with line numbers and error diagnostics. | `GET /api/data-quality/quarantine`<br>`GET /api/data-quality/summary` | `tests/test_ingestion.py::<br>test_malformed_record_quarantine` | **PASS (Verified)** |
| **4. On-Chain & Off-Chain Correlation** | Bipartite join engine linking UTXO transactions to peer relay IP, ASN, port, and geo-jurisdiction within temporal coincidence windows. | `GET /api/wallets/{addr}/network`<br>`GET /api/transactions/{txid}/peers` | `tests/test_evidence_engine.py::<br>test_network_correlation` | **PASS (Verified)** |
| **5. 23-Dimensional Feature Engine** | Mathematical vectorizer extracting volume, structural, temporal, and network dynamics per entity. | `POST /api/models/features/extract`<br>`backend/app/services/feature_service.py` | `tests/test_feature_engineering.py::<br>test_23_dimensional_feature_vector` | **PASS (Verified)** |
| **6. Unsupervised Anomaly Detection** | Isolation Forest ensemble scoring entities on non-parametric tree path lengths, calibrated to $[0, 100]$. | `POST /api/models/train`<br>`backend/app/services/ml_service.py` | `tests/test_ml_pipeline.py::<br>test_isolation_forest_scoring` | **PASS (Verified)** |
| **7. Cohort Behavioral Clustering** | Dual-scale clustering: exact DBSCAN for cohorts $\le 1,000$; MiniBatchKMeans + 97th percentile centroid distance for cohorts $> 1,000$. | `POST /api/models/cluster`<br>`backend/app/services/ml_service.py` | `tests/test_ml_pipeline.py::<br>test_dbscan_clustering` | **PASS (Verified)** |
| **8. Peeling Chain Detection** | Recursive change-address tracker identifying asymmetric splits (high-value change vs micro-split) over $\ge 3$ consecutive hops. | `GET /api/heuristics/peeling-chains`<br>`backend/app/services/heuristic_service.py` | `tests/test_heuristics.py::<br>test_peeling_chain_detection` | **PASS (Verified)** |
| **9. CoinJoin & Mixer Fingerprinting** | Equal-denomination output matching with Shannon entropy thresholding ($H \ge 2.5$) detecting privacy tumblers. | `GET /api/heuristics/mixing`<br>`backend/app/services/heuristic_service.py` | `tests/test_heuristics.py::<br>test_mixing_pattern_detection` | **PASS (Verified)** |
| **10. Multigraph Link Analysis** | Interactive Cytoscape.js canvas rendering Wallets, TXs, IPs, and ASNs with $1 - 3$ hop neighborhood traversal. | `GET /api/graph/subgraph`<br>`GET /api/graph/default-entity`<br>`frontend/src/pages/GraphPage.tsx` | `tests/test_graph.py::<br>test_subgraph_generation` | **PASS (Verified)** |
| **11. Graph Centrality Metrics** | Network topology analyzer computing Degree Centrality, In/Out degree ratios, and PageRank ($\alpha=0.85$). | `GET /api/graph/metrics`<br>`backend/app/services/graph_service.py` | `tests/test_graph.py::<br>test_centrality_metrics` | **PASS (Verified)** |
| **12. Compound Alert Prioritizer** | Multi-signal triage queue weighting ML anomaly scores ($45\%$), heuristic triggers ($35\%$), and network indicators ($20\%$). | `GET /api/alerts`<br>`GET /api/alerts/{id}`<br>`backend/app/services/alert_service.py` | `tests/test_alert_prioritizer.py::<br>test_compound_risk_calculation` | **PASS (Verified)** |
| **13. Data Sufficiency Confidence** | Multi-source observation density metric quantifying observable telemetry depth ($0 - 100\%$). | `GET /api/alerts/{id}/confidence`<br>`backend/app/services/alert_service.py` | `tests/test_alert_prioritizer.py::<br>test_confidence_scoring` | **PASS (Verified)** |
| **14. Explainable AI Assistant** | Grounded deterministic reasoning assistant producing narrative findings, signal breakdowns, and actions without LLM hallucinations. | `POST /api/alerts/{id}/explain`<br>`backend/app/services/ai_service.py` | `tests/test_api.py::<br>test_alert_explainability` | **PASS (Verified)** |
| **15. Activity Chronology Timeline** | Normalized microsecond timeline sequencing on-chain transaction events and off-chain network observations chronologically. | `GET /api/timeline/events`<br>`backend/app/api/endpoints/timeline.py` | `tests/test_api.py::<br>test_timeline_events` | **PASS (Verified)** |
| **16. Evidence Lineage & Provenance** | 5-stage data lineage linking final intelligence claims back to immutable raw database records across 8 signal categories. | `GET /api/evidence`<br>`GET /api/evidence/{id}`<br>`backend/app/services/evidence_service.py` | `tests/test_evidence_engine.py::<br>test_evidence_chain_integrity` | **PASS (Verified)** |
| **17. Case Management & Dossiers** | Dedicated investigation workspace with entity pinning, immutable notes, and printable forensic intelligence dossiers. | `POST /api/cases`<br>`GET /api/cases/{id}/report`<br>`backend/app/services/case_service.py` | `tests/test_final_release.py::<br>test_case_seeding_and_reporting` | **PASS (Verified)** |
| **18. Model Lab & Registry** | Versioned registry tracking hyperparameters, training timestamps, feature schemas, and clustering metrics. | `GET /api/models/registry`<br>`GET /api/models/active` | `tests/test_api.py::<br>test_model_registry` | **PASS (Verified)** |
| **19. Tactical Command Center** | Real-time executive dashboard summarizing operational KPIs, Recharts anomaly histograms, and prioritized leads queue. | `GET /api/dashboard/stats`<br>`GET /api/dashboard/distribution` | `tests/test_api.py::<br>test_dashboard_stats` | **PASS (Verified)** |
| **20. Adaptive High-Contrast UI** | Professional command center styling with light/dark/system themes, zero initial render flash, and full accessibility. | Client-side persistent state<br>`frontend/src/context/ThemeContext.tsx` | `frontend/tests/theme.test.ts::<br>test_theme_lifecycle` | **PASS (Verified)** |
| **21. Air-Gapped Offline Execution** | 100% self-contained offline capability in Docker Compose or native Python/Node with zero outbound network calls. | Local SQLite engine<br>`AI_PROVIDER=mock`<br>`docs/OFFLINE_LINUX_GUIDE.md` | `tests/test_api.py`<br>`docs/OFFLINE_LINUX_GUIDE.md` | **PASS (Verified)** |
| **22. RBAC & Security Hardening** | 4-tier Role-Based Access Control (`ADMINISTRATOR`, `INVESTIGATOR`, `ANALYST`, `VIEWER`), bcrypt hashing, and JWT tokens. | `POST /api/auth/login`<br>`backend/app/core/security.py` | `tests/test_final_release.py::<br>test_rbac_user_seeding` | **PASS (Verified)** |

---

## 4. Core Capabilities

1. **Multi-Format Ingestion with Automated Quarantine:**  
   Ingests structured Bitcoin transaction records and network telemetry from CSV, JSON, and XML streams. Syntax errors, duplicate transactions, and malformed inputs are quarantined with detailed line-level diagnostics without interrupting batch execution.
2. **23-Dimensional Mathematical Feature Extraction:**  
   Calculates high-order behavioral statistics spanning financial volume (amounts, fees, fee rates), transaction topology (fan-in, fan-out, script entropy), temporal dynamics (inter-arrival burstiness $CV$, propagation delays), and network dispersion (relay node count, ASN diversity, geo-hopping velocity).
3. **Dual-Scale Unsupervised Anomaly Radar:**  
   Employs an Isolation Forest ensemble for multidimensional anomaly scoring, paired with a scalable cohort clustering engine (exact DBSCAN for test and focused cohorts $\le 1,000$ entities; memory-bounded MiniBatchKMeans centroid-distance thresholding for large 45,000+ entity populations).
4. **Heuristic Obfuscation Detectors:**  
   Identifies change-address peeling cascades through recursive graph searches and flags privacy mixers (Wasabi, Whirlpool, CoinJoin) through equal-denomination output matching and Shannon entropy ($H \ge 2.5$).
5. **Interactive Directed Multigraph (Cytoscape.js):**  
   Visualizes multi-hop entity interactions across Wallets, Transactions, IP addresses, and ASNs. Features concentric, breadth-first, and force-directed layouts, PageRank centrality calculation, entity key normalization, and one-click PNG intelligence export.
6. **Compound Risk Prioritization Queue:**  
   Eliminates alert fatigue by computing composite risk ratings ($0 - 100$) combining ML outlier scores, heuristic flags, and network signals, augmented by an explicit Data Sufficiency Confidence rating ($0 - 100\%$).
7. **Explainable AI Investigation Assistant:**  
   Synthesizes deterministic, evidence-grounded natural language intelligence summaries without relying on external hallucinating LLMs. Provides clear findings, contributing evidentiary signals, concrete next steps, and explicit uncertainty assessments.
8. **Formal Case Management & Forensic Reports:**  
   Enables investigators to pin entities, attach immutable evidence records, log timestamped investigative hypotheses, and generate court-ready forensic intelligence reports complete with investigator attribution and cryptographic verification lines.

---

## 5. System Architecture

```
                                  +---------------------------------------+
                                  |         RAW TELEMETRY INGESTION       |
                                  |   CSV / JSON / XML Multi-Format Feeds |
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
                                  | Dual-Scale Cohort Clustering          |
                                  | (DBSCAN <=1k / MiniBatchKMeans >1k)   |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   EVIDENCE & ALERT PRIORITIZATION     |
                                  | 8 Signal Categories, Compound Risk    |
                                  | Data Sufficiency Confidence (0-100%)  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
+-----------------------------------------------------+-----------------------------------------------------+
|                                              INVESTIGATIVE WORKSPACE                              |
|  - Tactical Command Center (Recharts)               - Cytoscape.js Link Analysis Multigraph               |
|  - Explainable AI Investigation Assistant           - Chronological Vertical Timeline                     |
|  - Case Dossier Workspace & Notes Logger            - Forensic Report Generator (Print & JSON)           |
+-----------------------------------------------------------------------------------------------------------+
```

### Data Layer Topologies
- **Mode A (Offline Air-Gapped):** Local SQLite (`btcshield.db`) synchronized with thread-safe connection pooling, zero egress.
- **Mode B (Cloud Production):** Serverless Neon PostgreSQL with SSL connection pooling, indexed foreign keys, and migration tracking.

---

## 6. Intelligence & Analytical Engines

BTC-SHIELD partitions its analytical workload across nine dedicated engines:

1. **Ingestion & Validation Engine (`ingestion_service.py`):**  
   Streams records from raw uploads, verifies cryptographic format validity, deduplicates records via SHA-256 content hashes, and quarantines anomalies into `raw_records`.
2. **Entity Resolution Engine (`graph_service.py`):**  
   Extracts unique wallets, transaction hashes, IP addresses, and ASNs. Normalizes prefixed entity keys (`wallet:...`, `tx:...`, `ip:...`, `asn:...`) to ensure seamless graph traversal.
3. **23-Dimensional Feature Engine (`feature_service.py`):**  
   Executes sliding-window and graph-wide feature aggregation over UTXO and network tables, computing standardized feature matrices.
4. **Machine Learning Anomaly Engine (`ml_service.py`):**  
   Trains and evaluates Isolation Forest ensembles and scalable behavioral cohort clusterers, generating calibrated anomaly scores ($0 - 100$) and noise classification flags (`cluster_id = -1`).
5. **Structural Heuristics Engine (`heuristic_service.py`):**  
   Applies domain-specific blockchain analysis algorithms to identify peeling chains, change-address reuse, and CoinJoin mixer structures.
6. **Evidence Generation Engine (`evidence_service.py`):**  
   Translates raw mathematical anomalies and heuristic triggers into immutable, categorized evidence records across 8 standardized signal categories.
7. **Alert Prioritization Engine (`alert_service.py`):**  
   Computes composite compound risk scores and observational data sufficiency ratings, ranking alerts into an actionable triage queue (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
8. **Explainable AI Assistant Engine (`ai_service.py`):**  
   Executes deterministic, rule-based natural language synthesis to construct juror-comprehensible investigative briefs without external API dependencies.
9. **Forensic Case & Reporting Engine (`case_service.py`):**  
   Manages the investigative case lifecycle (`OPEN`, `INVESTIGATING`, `CLOSED`), associates pinned entities and evidence, and compiles formal forensic reports.

---

## 7. End-to-End Forensic Workflow

```
[Raw Telemetry Feed]
       │
       ▼
[1. Ingest & Quarantine] ──(Invalid / Duplicate)──► [Quarantine Table & Audit Log]
       │
       ▼ (Valid Records)
[2. Entity Resolution] ──► [Wallets, TXs, Network Observations]
       │
       ▼
[3. Feature Extraction] ──► [23-Dimensional Vector Matrix]
       │
       ▼
[4. ML Anomaly Radar] ──► [Isolation Forest Score + Cohort Cluster Outliers]
       │
       ▼
[5. Heuristic Correlation] ──► [Peeling Chain & CoinJoin Fingerprints]
       │
       ▼
[6. Evidence Generation] ──► [Immutable Evidence Records across 8 Categories]
       │
       ▼
[7. Alert Prioritization] ──► [Triage Queue: Compound Risk + Data Sufficiency]
       │
       ▼
[8. Link Analysis] ──► [Cytoscape Multigraph 1-3 Hop Traversal]
       │
       ▼
[9. Case Promotion] ──► [Case Dossier, Investigator Notes, Forensic Report Export]
```

---

## 8. Platform Modules

| Module | Route | Primary Purpose |
|---|---|---|
| **Command Center** | `/` | Executive situational awareness, real-time KPIs, anomaly score distribution, urgent leads queue. |
| **Alert Prioritizer** | `/alerts` | Ranked alert triage feed with priority/status filtering, compound risk scores, and data sufficiency meters. |
| **Alert Detail** | `/alerts/:id` | Deep-dive alert analysis, Explainable AI Assistant narrative, evidence signal breakdown, promote-to-case modal. |
| **Investigation Graph** | `/graph` | Interactive Cytoscape.js multigraph, 1-3 hop neighborhood expansion, PageRank centrality, PNG export. |
| **Structural Heuristics** | `/heuristics` | Automated detection of asymmetric peeling chains, CoinJoin mixers, and single-tx structural analyzer. |
| **Wallet Intelligence** | `/wallets` & `/:addr` | Wallet financial profile, balance, net flow, transaction history, and correlated network peers. |
| **Transaction Analysis** | `/transactions` & `/:txid`| Granular UTXO breakdown, inputs, outputs, fee rates, script types, and fan-out classifications. |
| **Network Entities** | `/ips/:ip` & `/asns/:asn` | Peer relay history, geographic jurisdictions, hosting ASNs, and correlated on-chain actors. |
| **Activity Timeline** | `/timeline` | Unified chronological vertical timeline merging on-chain ledger events and network telemetry. |
| **Evidence Explorer** | `/evidence` | Complete 5-stage evidentiary lineage table across 8 behavioral signal categories. |
| **Cases & Dossiers** | `/cases` & `/:id` | Investigator case workspaces, pinned entities, attached evidence, notes logger, and report generator. |
| **Dataset Management** | `/datasets` | Multi-format upload (CSV, JSON, XML), data quality metrics, one-click ML intelligence pipeline execution. |
| **Data Quality & Quarantine** | `/data-quality` | Ingestion integrity audit, quarantined record inspection with syntax error diagnostics. |
| **Model Lab** | `/models` | Unsupervised model registry, hyperparameter configurations, feature importance, and silhouette metrics. |
| **Forensic Audit Trail** | `/audit-logs` | Immutable audit log of all logins, uploads, case creations, and report exports with IP attribution. |
| **Settings & RBAC** | `/settings` | Role-Based Access Control matrix, background job monitoring, and air-gapped system toggles. |
| **System Telemetry** | `/system` | Live operational health check across REST API, database, ML engine, and NetworkX multigraph. |

---

## 9. Data Ingestion & Data Quality

BTC-SHIELD handles heterogeneous data feeds while guaranteeing that malformed inputs cannot crash the processing pipeline:

### 1. Ingestion Formats
- **CSV:** Tabular records parsed with robust row-by-row streaming.
- **JSON:** Accepts both raw arrays of transaction objects and wrapped metadata envelopes (`{"records": [...]}`).
- **XML:** Hardened streaming with `defusedxml` targeting `<records><record>...</record></records>` structures, mitigating XML External Entity (XXE) and Billion Laughs expansion vulnerabilities.

### 2. Syntactic & Integrity Validation
Every record must satisfy strict deterministic format checks:
- **Bitcoin Addresses:** Must match standard Base58Check (`1...`, `3...`) or Bech32 SegWit (`bc1q...`, `bc1p...`) regular expressions.
- **Transaction Hashes:** Must be exactly 64-character lowercase hexadecimal strings (`^[0-9a-fA-F]{64}$`).
- **IP Addresses:** Validated via standard IPv4/IPv6 socket conversion; invalid octets are rejected.
- **Financial Balances:** Satoshi amounts must be non-negative integers; transaction inputs must strictly equal outputs plus fees ($\sum In = \sum Out + Fee$).

### 3. Quarantine & Data Quality Assurance
Records failing validation or identified as duplicate entries via SHA-256 payload hashing are isolated in `raw_records` with `is_valid = False` and an explicit `error_message`. The pipeline logs the exact line number and failure category, allowing investigators to audit ingestion quality without corrupting downstream feature vectors.

---

## 10. Data Provenance

To maintain absolute credibility for law enforcement and intelligence juries, BTC-SHIELD strictly defines the origin, boundary, and classification of all data within the platform:

```
                                  DATA PROVENANCE ARCHITECTURE
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │ 1. OFFICIAL / PUBLIC SOURCE DATA                                                      │
  │    - Elliptic Graph Benchmark (203k transactions, 4,696 illicit classes)              │
  │    - Bitcoin Protocol Specifications (BIP 141 SegWit, BIP 173 Bech32, UTXO mechanics) │
  └────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │ 2. DERIVED ANALYTICAL DATA                                                             │
  │    - 23-Dimensional Mathematical Feature Vectors                                      │
  │    - NetworkX Directed Bipartite Multigraph Edges                                      │
  │    - Isolation Forest Anomaly Scores & Centroid Distance Outlier Flags                │
  │    - 8 Standardized Evidence Signal Records                                           │
  └────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │ 3. SYNTHETIC EVALUATION DATASET (Dataset 6)                                            │
  │    - 100,000 Relational Transactions | 45,000 Wallets | 350,131 Edges                 │
  │    - Purpose: High-volume stress testing and SIH 26146 jury benchmarking              │
  │    - NOTE: Explicitly synthetic evaluation data; NOT real-world surveillance traffic   │
  └────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │ 4. DEMO & PRESENTATION DATA                                                            │
  │    - 3 Pre-Seeded Presentation Cases (Alpha-Peel, CoinJoin Syndicate, Darknet Gateway)│
  │    - 4 Pre-Seeded RBAC Demo Accounts (Administrator, Investigator, Analyst, Viewer)   │
  └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Official vs. Derived vs. Synthetic / Demo Data

| Dimension | 1. Official / Public Source Data | 2. Derived Analytical Data | 3. Synthetic Benchmark Data (Dataset 6) | 4. Demo & Presentation Data |
|---|---|---|---|---|
| **Origin** | Public academic benchmarks (Elliptic) & Bitcoin Core protocol specifications. | Generated dynamically by BTC-SHIELD feature and ML services. | Programmatically generated via deterministic Bitcoin graph synthesizer (`generate_dataset.py`). | Pre-seeded during platform initialization (`main.py` & `case_service.py`). |
| **Purpose** | Algorithmic baseline validation and protocol conformity. | Mathematical anomaly quantification and graph link analysis. | High-throughput stress-testing ($100\text{k}$ txs, $45\text{k}$ wallets) and SIH demonstration. | Immediate walkthrough ready for evaluators and jury inspection. |
| **Storage Tables** | External reference schemas / documentation. | `features`, `graph_edges`, `evidence`, `alerts`, `model_runs`. | `raw_records`, `transactions`, `wallets`, `network_observations`. | `cases`, `case_notes`, `case_entities`, `case_evidence`, `users`. |
| **Realism Nature** | Historical real-world Bitcoin transactions. | Strictly deterministic derived metrics; zero hallucination. | Heavy-tailed realistic amounts, UTXO fee balance, documentation IPs. | Realistic operational scenarios; clearly marked as demonstration leads. |
| **Forensic Claim** | Public academic reference. | Verified mathematical output. | **Synthetic evaluation benchmark.** | **Demonstration fixture.** |

---

## 12. Machine Learning Methodology

BTC-SHIELD employs an unsupervised machine learning architecture engineered specifically for high-dimensional financial graphs:

### 12.1 23-Dimensional Behavioral Feature Vector
The feature extraction engine computes 23 continuous features across four domains:

$$\vec{x} = \Big[ \underbrace{v_1, \dots, v_6}_{\text{Volume}}, \; \underbrace{s_1, \dots, s_7}_{\text{Structural}}, \; \underbrace{t_1, \dots, t_5}_{\text{Temporal}}, \; \underbrace{n_1, \dots, n_5}_{\text{Network}} \Big]^T$$

1. **Volume Features (6):** `total_input_sats`, `total_output_sats`, `fee_sats`, `fee_rate_sat_vb`, `output_value_mean`, `output_value_std`.
2. **Structural Features (7):** `num_inputs`, `num_outputs`, `fan_out_ratio`, `script_type_entropy`, `is_rbf_enabled`, `has_op_return`, `locktime_type`.
3. **Temporal Dynamics (5):** `block_interarrival_time`, `burstiness_cv` (Coefficient of Variation: $\sigma / \mu$), `propagation_delay_sec`, `hour_of_day_utc`, `day_of_week`.
4. **Network Telemetry Correlation (5):** `relay_node_count`, `unique_asn_count`, `cross_border_hop_count`, `tor_or_proxy_risk_score`, `coincident_node_dispersion`.

### 12.2 Isolation Forest Anomaly Detection
- **Mathematical Principle:** Anomalous data points require fewer random axis-aligned splits to be isolated in binary search trees.
- **Formulation:** Path length $h(x)$ across $T$ trees is normalized against average path length $c(n)$:
  $$c(n) = 2 \ln(n - 1) + 0.5772156649 - \frac{2(n - 1)}{n}, \quad s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}$$
- **Hyperparameters:** `n_estimators = 50`, `max_samples = min(256, n_samples)`, single-threaded execution (`n_jobs = 1`), `contamination = "auto"`.
- **Score Calibration:** Raw scores are linearly calibrated to an intuitive scale $[0.0, 100.0]$. Scores exceeding $75.0$ are flagged as anomalous.

### 12.3 Dual-Scale Cohort Behavioral Clustering (Algorithmic Truth)
To prevent quadratic memory explosion ($O(N^2)$) on production datasets while preserving downstream outlier classification contracts, BTC-SHIELD implements a **dual-scale clustering architecture**:

```
                              INPUT COHORT SIZE (N)
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
             N <= 1,000 Entities                     N > 1,000 Entities
         (Tests / Focused Cohorts)              (Production 45k+ Datasets)
                    │                                       │
                    ▼                                       ▼
              Exact DBSCAN                          MiniBatchKMeans
         - k-NN Distance Elbow                  - n_clusters = 12
         - Adaptive Epsilon (80th pct)          - batch_size = 2048
         - min_samples = 3 to 10                - Distance-to-Centroid Analysis
         - Memory: O(N^2) (Safe for N<=1k)      - Top 3% Furthest (97th pct)
                    │                             assigned Cluster ID = -1
                    │                           - Memory: O(N * K) (Safe for 512MB)
                    │                                       │
                    └───────────────────┬───────────────────┘
                                        ▼
                         UNIFIED OUTLIER CONTRACT
                       cluster_id = -1 (Noise/Outlier)
```

- **Small Cohorts ($N \le 1,000$):** Executes exact standard `DBSCAN(eps=eps, min_samples=min_samples_val, n_jobs=1)` with adaptive epsilon computed from the 80th percentile of $k$-NN distances.
- **Large Cohorts ($N > 1,000$, e.g. 45,000-entity populations):** Executes `MiniBatchKMeans(n_clusters=12, batch_size=2048, random_state=42)`. Following cluster assignment, the Euclidean distance from each feature vector to its assigned cluster centroid is computed. Entities residing in the top 3% distance tail (97th percentile) are assigned `cluster_id = -1` (un-clusterable behavioral noise).
- **Algorithmic Reality:** MiniBatchKMeans is **not** mathematically identical to DBSCAN; it is an engineered operational substitute that guarantees $O(N \cdot K)$ memory complexity (allocating ~6.4 MB vs >15 GB) while strictly satisfying downstream evidence and alert pipeline requirements.

---

## 13. Explainability & Evidence Generation

BTC-SHIELD guarantees zero black-box hallucinations by grounding all forensic assessments in deterministic rule engines:

### 13.1 Standardized Evidence Categories (8 Signal Types)
1. `HIGH_ANOMALY_SCORE`: Multi-dimensional feature vector deviation confirmed by Isolation Forest ($Score \ge 75.0$).
2. `PEELING_CHAIN_CHANGE`: Asymmetric peeling cascade tracking repeated high-value change and micro-expenditure splits.
3. `COINJOIN_MIXER`: Equal-denomination output matching with high Shannon entropy ($H \ge 2.5$).
4. `BURST_VELOCITY`: Temporal transaction clustering indicating rapid automated automated dispersion ($CV \ge 2.0$).
5. `GEO_HOPPING`: Relay node broadcast originating from geographically dispersed jurisdictions within tight temporal windows.
6. `HIGH_FAN_OUT`: Single-input to high-volume multi-output fan-out patterns indicative of distribution syndicates.
7. `HIGH_FEE_ANOMALY`: Extreme transaction fee rates paid to guarantee immediate block inclusion.
8. `HIGH_VALUE_TRANSFER`: Significant satoshi volume transfers exceeding normal historical baseline distributions.

### 13.2 Compound Alert Prioritization & Data Sufficiency
Alerts are scored on two complementary orthogonal axes:
- **Compound Risk Score ($0 - 100$):**
  $$\text{Risk} = 0.45 \cdot S_{\text{ML}} + 0.35 \cdot \sum W_{\text{heuristics}} + 0.20 \cdot C_{\text{network}}$$
  Categorized into `CRITICAL` ($\ge 85$), `HIGH` ($70 - 84$), `MEDIUM` ($50 - 69$), and `LOW` ($< 50$).
- **Data Sufficiency Confidence ($0 - 100\%$):**
  Quantifies observational depth ($N_{\text{observations}}$, $N_{\text{transactions}}$, temporal span $T_{\text{span}}$) so investigators can immediately distinguish high-certainty leads from sparse observations.

### 13.3 Explainable AI Assistant (Zero Hallucination)
The built-in assistant synthesizes findings into a four-part juror-ready narrative:
1. **Primary Finding:** Plain-language synthesis of primary anomaly and heuristic drivers.
2. **Contributing Signals:** Itemized breakdown of active evidence categories with individual strength weights.
3. **Recommended Investigative Steps:** Actionable directives (e.g., "Inspect change output address `bc1q...` in Graph Analysis", "Query hosting ASN 13335 for relay infrastructure").
4. **Uncertainty & Forensic Caveats:** Explicit acknowledgment of data limits and alternative legitimate explanations (e.g., exchange batching or mining pool payouts).

---

## 14. Security Architecture & Role-Based Access Control

BTC-SHIELD is architected for deployment in sensitive intelligence and law enforcement environments:

### 14.1 Zero Hardcoded Secrets
- All credentials (`DATABASE_URL`, `JWT_SECRET`, `ADMIN_PASSWORD`) are loaded strictly from environment variables.
- Production startup checks reject insecure defaults (e.g., short JWT secrets $< 32$ characters or SQLite in production mode).

### 14.2 Role-Based Access Control (RBAC) Enforcement
Access is gated at the FastAPI middleware layer across four distinct operational roles:

| Capability / Resource | ADMINISTRATOR | INVESTIGATOR | ANALYST | VIEWER |
|---|:---:|:---:|:---:|:---:|
| **View Tactical Command Center & KPIs** | Yes | Yes | Yes | Yes |
| **Inspect Wallets, Transactions, IPs, ASNs** | Yes | Yes | Yes | Yes |
| **Interactive Graph Traversal (Cytoscape)** | Yes | Yes | Yes | Yes |
| **Inspect Heuristics & Peeling Chains** | Yes | Yes | Yes | Yes |
| **Upload Datasets (CSV, JSON, XML)** | Yes | Yes | Yes | No |
| **Trigger Feature Extraction & Train ML** | Yes | No | Yes | No |
| **Triage & Update Alert Review Status** | Yes | Yes | No | No |
| **Create Cases & Attach Evidence** | Yes | Yes | No | No |
| **Log Timestamped Case Notes** | Yes | Yes | No | No |
| **Generate & Export Forensic Reports** | Yes | Yes | No | No |
| **Inspect System Audit Logs** | Yes | Yes | No | No |
| **User Administration & Role Management** | Yes | No | No | No |

*Public self-registration via `/login` strictly assigns the `VIEWER` role by default, preventing unauthorized privilege escalation.*

### 14.3 Pre-Seeded Demonstration Accounts
For rapid SIH evaluation and jury testing, the following accounts are pre-seeded:
- `admin` / `Admin@123` (`ADMINISTRATOR`)
- `lead_investigator` / `Investigator@123` (`INVESTIGATOR`)
- `aml_analyst` / `Analyst@123` (`ANALYST`)
- `compliance_viewer` / `Viewer@123` (`VIEWER`)

---

## 15. Technology Stack

### Backend
- **Language & Runtime:** Python 3.13+
- **API Framework:** FastAPI 0.115+ with Uvicorn ASGI server
- **Database & ORM:** SQLAlchemy 2.0 (Sync sessions with PostgreSQL / SQLite compatibility)
- **Scientific & ML Libraries:** Scikit-Learn 1.5, NumPy, Polars, NetworkX, Joblib
- **Security & Crypto:** Bcrypt password hashing, PyJWT, DefusedXML
- **Validation:** Pydantic v2 Settings & Schemas

### Frontend
- **Framework & Build:** React 19, TypeScript 5, Vite 8
- **UI Components & Styling:** Tailwind CSS v4, Lucide React icons
- **Data Visualization:** Recharts 3 (Anomaly histograms & KPI cards)
- **Network Graph Canvas:** Cytoscape.js 3 with `cytoscape-dagre` & `cytoscape-concentric` layouts
- **State & Caching:** TanStack React Query v5 (stale-while-revalidate, zero-render blocking)

---

## 16. Quickstart Guide

### Prerequisites
- Python 3.13+ (or 3.11/3.12)
- Node.js 20+ and npm

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/Pramendra0001/BTC.git
cd BTC

# 2. Configure and activate Python virtual environment
python -m venv backend/.venv
# Windows:
backend\.venv\Scripts\activate
# Linux / macOS:
source backend/.venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt
pip install pytest httpx

# 4. Generate local synthetic test dataset
python data/generators/generate_dataset.py --size 1000 --format csv --output data/samples

# 5. Launch FastAPI backend (Port 8000)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In a separate terminal window:
```bash
# 6. Install frontend dependencies and launch development server (Port 5173)
cd frontend
npm install
npm run dev
```

Open your browser to `http://localhost:5173` and authenticate using `admin` / `Admin@123`.

---

## 17. Offline & Air-Gapped Deployment

BTC-SHIELD is certified for 100% air-gapped, zero-egress execution for **SIH Grand Finale Jury Evaluation (Mode A)**:

```bash
# Execute single-command containerized stack:
docker compose up -d --build
```
- **Frontend SPA:** `http://localhost:3000` (or `http://localhost:5173`)
- **Backend OpenAPI Documentation:** `http://localhost:8000/docs`
- **Zero Internet Requirement:** The platform bundles all JavaScript assets, CSS stylesheets, Python wheels, and scikit-learn model definitions locally. External DNS lookups and remote cloud APIs are completely disabled (`AI_PROVIDER=mock`).

*For step-by-step air-gapped Linux setup on fresh Ubuntu/Debian machines, see [docs/OFFLINE_LINUX_GUIDE.md](docs/OFFLINE_LINUX_GUIDE.md).*

---

## 18. Cloud Deployment Architecture

BTC-SHIELD operates an active, continuous production deployment topology (**Mode B**):

- **Production Frontend:** [https://pramendra0001.github.io/BTC/](https://pramendra0001.github.io/BTC/)  
  Hosted via GitHub Pages, compiled with Vite 8, featuring automated code-splitting and client-side routing.
- **Production Backend API:** [https://btc-3jme.onrender.com](https://btc-3jme.onrender.com)  
  Containerized FastAPI microservice running on Render with automatic HTTPS and CORS authorization.
- **Interactive OpenAPI Documentation:** [https://btc-3jme.onrender.com/docs](https://btc-3jme.onrender.com/docs)
- **Database Engine:** Managed Neon Serverless PostgreSQL with SSL encryption and automated Alembic schema migrations.

---

## 19. Testing & Verification

Every functional module and algorithmic subsystem is backed by rigorous automated test suites.

### Canonical Test Execution Matrix

```text
====================================================================================
                        BTC-SHIELD CANONICAL TEST SUITE AUDIT
====================================================================================
Backend Pytest Suite:     57 passed, 3 skipped, 0 failed  (19.46s execution)
Frontend Node/Unit Suite:  8 passed, 0 skipped, 0 failed  (159ms execution)
Combined Repo Total:      65 passed, 3 skipped, 0 failed  (100% Pass Rate)
Overall Status:           PASS
====================================================================================
```

### Backend Test Coverage Breakdown (`pytest tests/ -v`)
- `tests/test_api.py` (19 tests): Authentication lifecycle, dashboard stats, timeline queries, cases, notes, reports, and heuristic API contracts.
- `tests/test_graph.py` (5 tests): Directed multigraph construction, multi-hop traversal, PageRank and Degree centrality metrics.
- `tests/test_heuristics.py` (4 tests): Peeling-chain cascade tracking and equal-denomination CoinJoin mixer detection.
- `tests/test_final_release.py` (4 tests): Entity key normalization (`wallet:...`), alert schema compatibility, pre-seeded presentation cases, and RBAC user provisioning.
- `tests/test_ml_pipeline.py` (4 tests): Isolation Forest scoring, dual-scale cohort clustering, score calibration, and artifact serialization.
- `tests/test_alert_prioritizer.py` (4 tests): Compound risk calculation, data sufficiency confidence scoring, and priority classification.
- `tests/test_evidence_engine.py` (4 tests): Evidence signal generation across 8 categories and cryptographic hash chain verification.
- `tests/test_feature_engineering.py` (4 tests): 23-dimensional feature vector extraction and mathematical correctness.
- `tests/test_ingestion.py` (6 tests): CSV, JSON, and XML streaming parsers, Base58/Bech32 address validators, and malformed record quarantine.
- `tests/test_config.py` (2 tests): Security settings, CORS parser, and environment variable enforcement.
- `tests/test_100k_dataset.py` (1 test): High-volume relational schema validation.
- *(3 skipped tests: Optional live PostgreSQL connection tests when running in SQLite mode).*

### Frontend Test Coverage Breakdown (`npm test`)
- `frontend/tests/auth.test.ts` (4 tests): JWT token persistence, invalid credential rejection, user registration, and 409 conflict handling.
- `frontend/tests/theme.test.ts` (4 tests): Dark/light/system theme resolution, localStorage persistence, and canvas re-rendering.

---

## 20. Performance & Memory Engineering

Performance claims in BTC-SHIELD are strictly categorized by verification level:

### 1. [LOCAL BENCHMARK]
- **Ingestion Throughput:** Ingests $10,000$ records in $1.42\text{ s}$ using streaming dictionary parsers on modern multi-core hardware.
- **23-Dimensional Feature Extraction:** Extracts complete feature vectors for $45,000$ entities in $3.84\text{ s}$.
- **Graph Visualization:** Renders 200 nodes and 350 directed edges on Cytoscape.js in $< 85\text{ ms}$.

### 2. [PRODUCTION OBSERVATION]
- **512 MB Container Memory Bound:** Resolved previous container OOM termination through zero-copy `float32` matrices, session expunging (`db.expunge_all()`), and replacing $O(N^2)$ DBSCAN with $O(N \cdot K)$ MiniBatchKMeans. Baseline production memory footprint is $\approx 140\text{ MB}$; peak ML execution footprint is $\approx 285\text{ MB}$ (comfortably within the 512 MB limit).
- **Frontend Bundle Size:** Reduced entry JavaScript bundle from $1.5\text{ MB}$ to **$24.25\text{ kB}$** via aggressive route-level code-splitting (`React.lazy`). The initial application shell becomes interactive in $< 1\text{ second}$.

### 3. [EXPECTED / ESTIMATED]
- **Projected Throughput:** Architected to handle $1,000,000$ transactions in batches of $50,000$ using Polars out-of-core streaming on 4 GB RAM instances.

---

## 21. System Limitations

In adherence to scientific integrity, BTC-SHIELD explicitly documents its technical boundaries:
1. **Free-Tier Cloud Constraints:** Production cloud deployment on free-tier containers restricts concurrent heavy ML training jobs to single-worker sequential queues.
2. **Probabilistic Heuristics:** On-chain clustering heuristics (e.g., change-address identification) rely on standard Bitcoin wallet behaviors and can be partially degraded by non-standard scripting or coin-control techniques.
3. **P2P Relay Ambiguity:** Off-chain relay observations reflect the first peer node broadcasting a transaction to the listening probe network. Relay telemetry may point to VPNs, Tor exit nodes, or relay gateways rather than the originating physical device.
4. **Unsupervised Scope:** Machine learning models detect statistical anomalies and behavioral deviations; they do not generate definitive legal determinations of guilt or criminal intent.

---

## 22. Future Integrations & Roadmap

- **Live Bitcoin P2P Daemon Tap:** Direct ZeroMQ / RPC integration with Bitcoin Core nodes to capture live mempool broadcast telemetry in real time.
- **Lightning Network (L2) Intelligence:** Routing node topology analysis, channel exhaustion detection, and HTLC fee anomaly monitoring.
- **Graph Neural Networks (GNNs):** Semi-supervised node classification using PyTorch Geometric (RGCN / GraphSAGE) trained on academic benchmark sets.
- **Commercial Attribution Feeds:** API connectors for verified VASP (Virtual Asset Service Provider) exchange wallet tags and sanctions lists.

---

## 23. Presentation & Demonstration Flow

### 10-Minute Master Jury Demonstration Script

| Time | Phase | Target Screen | Core Narrative & Evaluator Talking Points |
|---|---|---|---|
| **0:00 - 1:30** | **Executive Overview** | `/` (Command Center) | Introduce Problem Statement 26146 (NTRO). Highlight real-time KPIs, anomaly score distribution, and the ranked triage queue. |
| **1:30 - 3:00** | **Alert Triage & Explainability** | `/alerts` & `/alerts/:id` | Open a `CRITICAL` lead. Demonstrate the Explainable AI Assistant narrative, multi-signal evidence cards, and Data Sufficiency rating. |
| **3:00 - 5:00** | **Interactive Link Analysis** | `/graph` | Explore the directed multigraph. Demonstrate 1-3 hop neighborhood expansion, PageRank centrality inspection, and PNG dossier export. |
| **5:00 - 6:30** | **Structural Heuristics** | `/heuristics` | Inspect the peeling-chain cascade visualizer and CoinJoin mixer entropy analyzer ($H \ge 2.5$). |
| **6:30 - 8:00** | **Case Dossier & Export** | `/cases` & `/cases/:id` | Open an active case dossier. Review pinned entities, immutable evidence records, investigator notes, and export the official forensic intelligence report. |
| **8:00 - 9:00** | **Data Ingestion & Integrity** | `/datasets` & `/data-quality` | Review multi-format upload capability (CSV/JSON/XML) and show the malformed record quarantine table. |
| **9:00 - 10:00** | **Verification & Technical Defense** | Terminal & `/system` | Display live system telemetry and run the automated test suite (**65 passed, 3 skipped**). Address jury questions on air-gapped readiness and ML memory bounds. |

---

## 24. Compliance & Forensic Disclaimer

> **IMPORTANT FORENSIC NOTICE:**  
> BTC-SHIELD operates on synthetic benchmark datasets, academic graph evaluations, and simulated network telemetry for competitive, research, and evaluation purposes. All analytical outputs—including anomaly scores, clustering labels, heuristic classifications, and natural language briefs—represent **probabilistic investigative leads and statistical risk indicators requiring independent corroboration by qualified human investigators**. They do not constitute definitive legal conclusions of criminality, fraud, or illicit conduct.

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for full legal text.
