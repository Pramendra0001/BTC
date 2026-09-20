# BTC-SHIELD System Architecture

**Platform:** Bitcoin Transaction & Network Intelligence Platform  
**Target Competition:** Smart India Hackathon 2026 (Problem Statement 26146)  
**Organization:** National Technical Research Organisation (NTRO)  
**Category:** Software | Blockchain & Cybersecurity  

---

## 1. Executive Architectural Summary

BTC-SHIELD is an explainable Bitcoin transaction and network intelligence platform engineered specifically for national security and law enforcement investigations. It bridges the critical divide between **on-chain Bitcoin ledger movements** (UTXOs, inputs, outputs, scripts, fees) and **fragmented peer-to-peer network layer observations** (source/destination IP addresses, BGP Autonomous System Numbers [ASNs], TCP ports, and geographic jurisdictions).

The fundamental architectural principle of BTC-SHIELD is strict evidentiary traceability:
```
RAW TELEMETRY -> NORMALIZED ENTITIES -> BEHAVIORAL FEATURES -> UNSUPERVISED ML -> VERIFIED EVIDENCE -> PRIORITIZED LEADS -> FORENSIC CASE DOSSIER
```
Every output displayed to an investigator—from anomaly scores and cluster labels to natural language explanations—originates directly from observable telemetry and traceable mathematical computations. Synthetic labels are strictly partitioned and never used to manufacture fake confidence or synthetic guilt.

---

## 2. High-Level Architecture Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                        DATA INGESTION LAYER                                       |
|  +-------------------+  +-------------------+  +-------------------+  +------------------------+  |
|  | CSV Parser        |  | JSON Parser       |  | XML Parser        |  | Hash Duplicate Filter  |  |
|  +-------------------+  +-------------------+  +-------------------+  +------------------------+  |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                   ENTITY RESOLUTION & STORAGE                                     |
|  +---------------------+  +---------------------+  +--------------------+  +-------------------+  |
|  | Wallets (Actors)    |  | Transactions        |  | IPs & Observations |  | ASNs & Geolocation|  |
|  +---------------------+  +---------------------+  +--------------------+  +-------------------+  |
|  Storage Engine: PostgreSQL 16 (Relational ACID) / SQLite (Embedded Offline Standalone)            |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 FEATURE ENGINEERING PIPELINE (v2.0)                               |
|  * 23-Dimensional Entity Feature Vectors:                                                          |
|    - Volume & Value: Sent, Received, Net Flow, Mean, Median, Variance, Min, Max                   |
|    - Structural: Fan-in, Fan-out, Fan Ratio, Mining Fee Ratio                                     |
|    - Temporal: Velocity, Inter-arrival Mean/Std, Burstiness (CV), Hour Entropy, Peak Hour        |
|    - Counterparty: Unique Counterparties, In/Out Count, Interaction Entropy                       |
|    - Network Telemetry: Unique IPs, ASNs, Countries, ASN Entropy                                  |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 UNSUPERVISED MACHINE LEARNING CORE                                |
|  +--------------------------------------------+  +---------------------------------------------+  |
|  | Isolation Forest (Partitioning Ensembles)  |  | DBSCAN (Density-Based Spatial Clustering)   |  |
|  | - 100 Isolation Trees                      |  | - Adaptive Epsilon (90th percentile k-NN)   |  |
|  | - Scaler: Robust StandardScaler            |  | - Min Samples: 3                            |  |
|  | - Scores: Calibrated [0.0 - 100.0]         |  | - Outlier Noise Partitioning (Cluster ID -1)|  |
|  +--------------------------------------------+  +---------------------------------------------+  |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                RELATIONAL LINK ANALYSIS GRAPH & EVIDENCE                          |
|  +--------------------------------------------+  +---------------------------------------------+  |
|  | NetworkX Directed Multigraph               |  | Multi-Category Evidence Generation Engine   |  |
|  | - Nodes: WALLET, TX, IP, ASN, COUNTRY      |  | - 8 Evidence Categories with Signal Weights |  |
|  | - Edges: INPUT_OF, OUTPUT_OF, OBSERVED_FROM|  | - Compound Risk & Sufficiency Confidence    |  |
|  | - K-Hop Expansion & Centrality Indices      |  | - Zero-Hallucination Explainability Assis.  |  |
|  +--------------------------------------------+  +---------------------------------------------+  |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                        APPLICATION INTERFACES                                     |
|  +---------------------------------------------+  +--------------------------------------------+  |
|  | FastAPI REST Service (Port 8000)            |  | React 19 / Vite Dark Investigation SPA     |  |
|  | - 38 Modular OpenAPI Endpoints              |  | - Cytoscape.js Interactive Multigraph      |  |
|  | - JWT RBAC Security Middleware              |  | - Recharts Dynamic Distribution Analytics  |  |
|  | - Sub-second Query Optimization             |  | - Investigative Dossier & Report Export    |  |
|  +---------------------------------------------+  +--------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Core Subsystems

### 3.1 Data Ingestion Subsystem
- **Supported Formats:** RFC 4180 CSV, JSON array/object schemas, hierarchical XML feeds.
- **Validation:** Strict field-level checks on Bitcoin addresses (Base58Check and Bech32 regex), IPv4/IPv6 syntax, numeric amounts, and timestamp formats (ISO-8601, RFC 2822, UNIX epoch).
- **Duplicate Prevention:** Cryptographic SHA-256 content hashing of critical transaction and network fields. Duplicate records are tagged, counted in quality metrics, and quarantined from contaminating models.
- **Immutable Raw Storage:** All ingested raw records are preserved unaltered in `raw_records` with line-level auditability.

### 3.2 Feature Engineering Subsystem
- Computes **23 dimensional behavioral features** structured under Schema Version 2.0.
- Implements mathematical Shannon entropy across counterparty interactions and ASN distributions.
- Calculates coefficient of variation ($CV = \sigma / \mu$) to capture burstiness and peeling behavior.
- Optimized with bulk in-memory hash mappings, avoiding $O(N^2)$ relational lookups and processing 1,000+ entities in under 1 second.

### 3.3 Machine Learning Pipeline
- **Isolation Forest:** Completely unsupervised tree ensemble that isolates anomalous data points by randomly selecting features and split values. Anomaly scores are normalized to a uniform $[0.0, 100.0]$ scale where $100.0$ represents extreme mathematical divergence from baseline.
- **DBSCAN:** Discovers non-linear density clusters. Outliers falling in low-density regions are identified as noise (Cluster ID -1).
- **Model Versioning:** Models and scalers are versioned with unique UUIDs and serialized via `joblib` into `ml_models/`. Full evaluation metrics (contamination ratio, silhouette score, sample counts, feature column schemas) are persisted in `model_runs`.

### 3.4 Relational Link Analysis Graph
- **Graph Model:** Directed multigraph implemented via NetworkX.
- **Node Classification:**
  - `WALLET`: On-chain Bitcoin addresses with transaction counts and anomaly scores.
  - `TRANSACTION`: Bitcoin transaction hashes with fees and amounts.
  - `IP`: Source and relay IP addresses observed during transaction propagation.
  - `ASN`: Autonomous System Numbers providing network hosting context.
  - `COUNTRY`: Geographic jurisdictions.
- **Subgraphs:** Subgraph extraction with breadth-first search (BFS) $k$-hop expansion ($k \in [1, 3]$) formatted in Cytoscape.js JSON format.
- **Centrality Metrics:** Degree centrality and PageRank calculated to identify central laundering hubs and peel-chain conduits.

### 3.5 Evidence & Alert Prioritizer
- **Evidence Engine:** Generates discrete evidence signals categorized under `MODEL`, `CLUSTER`, `AMOUNT`, `TRANSACTION`, `TEMPORAL`, `NETWORK`, `GEOGRAPHIC`, and `GRAPH`.
- **Alert Prioritization:** Eliminates arbitrary thresholds by computing:
  $$\text{Priority} = f(\text{Anomaly Score}, \text{Evidence Strength}, \text{Signal Diversity})$$
  Categories: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- **Confidence Rating:** Separately scores data sufficiency based on observation count and temporal duration, ensuring investigators can differentiate between high-risk confirmed actors and noisy sparse records.

### 3.6 Explainable AI Provider
- **Deterministic Explainability:** Implements `MockAIProvider` with rule-based narrative generation that analyzes structured evidence cards.
- **Zero-Hallucination Mandate:** Never synthesizes unverified criminal accusations, fictitious counterparties, or fake confidence percentages. Outputs structured findings, uncertainties, and investigative review checklists.

---

## 4. Dual-Mode Deployment Topology

BTC-SHIELD is architecturally designed to support two distinct operating environments without requiring code modifications:

### Mode A: Smart India Hackathon (SIH) Offline Linux Mode
- Deployed on a single air-gapped Linux machine (Ubuntu 22.04 / 24.04 LTS or Debian 12).
- Zero external internet connectivity required.
- SQLite or local Docker PostgreSQL instance.
- Offline MaxMind GeoLite2 ASN/Country database.
- Deterministic synthetic generator generates full investigative scenarios locally.

### Mode B: Cloud Production Stack
- Frontend: Single Page Application (SPA) deployed to GitHub Pages or static CDN with client-side 404 routing.
- Backend: Containerized FastAPI service on an HTTPS host (Google Cloud Run, AWS ECS, or Azure Container Apps).
- Database: Managed PostgreSQL (Neon, Cloud SQL, Supabase).
- CI/CD: Automated GitHub Actions pipelines for type-checking, automated pytest execution, and deployment.
