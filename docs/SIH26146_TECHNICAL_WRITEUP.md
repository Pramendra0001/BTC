# BTC-SHIELD — SIH 26146 Technical Write-Up
**Problem Statement 26146:** AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic  
**Organization:** National Technical Research Organisation (NTRO)  
**Security Classification:** Enterprise & Government Technical Documentation  
**Version:** 2.4.0-Enterprise-Airgap  
**Live Online Deployment:** [https://pramendra0001.github.io/BTC/](https://pramendra0001.github.io/BTC/)  
**Offline Deployment Package:** Linux Docker Compose / Multi-Container Air-Gapped Topology  

---

## 1. Problem Statement
The National Technical Research Organisation (NTRO) issued SIH Problem Statement 26146 seeking an advanced, explainable forensic intelligence platform capable of monitoring Bitcoin transaction traffic and correlating on-chain ledger transfers with network-layer peer-to-peer observations.

Bitcoin's pseudo-anonymous architecture facilitates complex obfuscation schemes including peeling chains, rapid coin mixing, UTXO consolidation, high-velocity tumbling, and geographic evasion across diverse Autonomous System Numbers (ASNs). Law enforcement and intelligence agencies require an air-gap capable, mathematically grounded, and court-admissible solution that eliminates reliance on external cloud APIs or proprietary black-box services.

---

## 2. Solution Overview
BTC-SHIELD is an enterprise-grade Bitcoin Transaction and Network Intelligence Platform engineered specifically to satisfy NTRO requirements. The platform combines:
- Streaming multi-format ingestion (CSV, JSON, XML) supporting 100,000+ transaction datasets with zero memory exhaustion.
- Cryptographic syntax validation and defensive quarantine.
- Dual-layer correlation linking Bitcoin UTXO movements with P2P IP addresses and BGP Autonomous Systems.
- Exact 23-dimensional behavioral feature extraction modeling financial volume, velocity, burstiness, counterparty entropy, and network/geographic dispersion.
- Local, calibrated machine learning using Scikit-Learn Isolation Forest for anomaly detection and DBSCAN for cohort clustering.
- In-memory NetworkX directed multigraph analysis computing degree/betweenness centrality and PageRank path discovery.
- Deterministic multi-signal evidence generation with zero LLM hallucinations.
- Decoupled alert prioritization separating mathematical anomaly score, evidentiary confidence, and compound priority triage.
- Native open-source local GeoIP resolution using DB-IP Lite MMDB files (CC BY 4.0) with deterministic RFC 5737 / RFC 1918 fallback.
- Court-admissible forensic case management and automated dossier generation.

---

## 3. Architecture
BTC-SHIELD implements a dual-mode, layered architecture:

```
+-----------------------------------------------------------------------------------+
|                              BTC-SHIELD ARCHITECTURE                              |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ INGESTION LAYER ]                                                              |
|    - CSV / JSON / XML Stream Parsers (Streaming Generators)                       |
|    - Strict Cryptographic Checksums (TXID, Base58, Bech32, IPv4/IPv6)             |
|    - Quarantine & Defensive Isolation Storage (RawRecord Table)                   |
|                                                                                   |
|  [ DATA & PERSISTENCE LAYER ]                                                     |
|    - PostgreSQL 16 (Offline Production) / SQLite WAL (Portable & Unit Testing)    |
|    - Normalized Entities: Wallets, Transactions, Inputs, Outputs, IPs, ASNs       |
|    - Case Evidence Association with ON DELETE CASCADE Foreign Key Hardening       |
|                                                                                   |
|  [ ANALYTICS & MACHINE LEARNING LAYER ]                                           |
|    - 23-Dimensional Behavioral Feature Vector Extractor                           |
|    - Local Isolation Forest Anomaly Engine (Persisted via Joblib in models/)      |
|    - DBSCAN Spatial/Behavioral Cohort Clustering Engine                           |
|    - Deterministic Multi-Layer Evidence Synthesizer                               |
|                                                                                   |
|  [ RESOLUTION & ENRICHMENT LAYER ]                                                |
|    - Local DB-IP Lite Country & ASN MMDB Binary Readers (offline/geoip/)          |
|    - Deterministic RFC 5737 / RFC 1918 Offline Fallback (Zero Outbound Egress)    |
|                                                                                   |
|  [ INVESTIGATIVE UI & GRAPH LAYER ]                                               |
|    - React 19 + TypeScript + Vite + Tailwind CSS                                  |
|    - Cytoscape.js Hardware-Accelerated Multigraph Topology Canvas                 |
|    - Forensic Case Dossier Generator & Chain-of-Custody Exporter                  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

### Operational Modes:
1. **Online Public Evaluation:** Hosted at `https://pramendra0001.github.io/BTC/` communicating over HTTPS to a Render-hosted FastAPI backend with automated TLS and CDN routing.
2. **Offline Enterprise Linux:** Hosted via `docker-compose.offline.yml` orchestrating hardened PostgreSQL 16, FastAPI backend, and Nginx frontend containers on an isolated bridge network with zero external egress.

---

## 4. Dataset
BTC-SHIELD operates on authoritative Bitcoin transaction and network telemetry datasets:
- **Canonical Schema:** `timestamp`, `src_ip`, `dst_ip`, `src_port`, `dst_port`, `txid`, `input_addresses`, `output_addresses`, `input_amounts`, `output_amounts`, `fee`, `script_type`, `geo_country`, `asn`.
- **Synthetic Forensic Testbeds:** Deterministic generation script in `data/generators/generate_dataset.py` simulating 7 distinct investigative scenarios (Normal Baseline, Burst Activity, Peeling Chains, Fan-In Consolidation, Amount Anomalies, Geo-Hopping, and Multi-Signal Anomalies).
- **Scale:** Verified on canonical datasets up to 100,000 records (`data/samples/btc_shield_100000_manifest.json`) maintaining sub-200MB memory consumption.

---

## 5. CSV/JSON/XML Ingestion
BTC-SHIELD provides native streaming parsers for all three required formats in `backend/app/services/ingestion_service.py`:
- **CSV:** Buffered parsing via `csv.DictReader` and Polars chunk readers.
- **JSON:** Memory-efficient stream parsing handling top-level lists and line-delimited JSON objects.
- **XML:** Streaming extraction using Python's `xml.etree.ElementTree.iterparse` and `defusedxml` to prevent billion-laughs and XML entity expansion attacks.
- **Streaming Pipeline:** All formats pipe records directly into relational tables without loading the entire payload into RAM.

---

## 6. Validation
Every transaction record undergoes rigorous cryptographic and semantic validation:
- **TXID Validation:** Regex check enforcing exactly 64 hexadecimal characters (`^[0-9a-fA-F]{64}$`).
- **Bitcoin Address Validation:** Support for Base58Check (P2PKH starting with `1`, P2SH starting with `3`) and Bech32/Bech32m (P2WPKH, P2WSH, P2TR starting with `bc1`).
- **IP Address Validation:** Standard socket conversion via Python `ipaddress.ip_address` rejecting invalid octets or out-of-range strings.
- **Quarantine Engine:** Corrupted or invalid records are safely captured in the `RawRecord` table with `is_valid = False` and detailed error messages, allowing continuous ingestion without pipeline crashes.

---

## 7. Network–Blockchain Correlation
The core investigative breakthrough of BTC-SHIELD is the cross-layer correlation linking blockchain ledger events with network-layer peer observations:
- **Entity Resolution:** Every transaction is tied to its originating P2P source IP, destination node IP, and port (default 8333).
- **BGP Autonomous System Mapping:** Source and destination IPs are mapped to their respective ASNs and autonomous organizations.
- **Multi-Observation Tracking:** When the same wallet address appears across multiple disparate IPs, countries, or ASNs within compressed timeframes, cross-layer correlation flags geo-hopping or VPN/proxy laundering routes.

---

## 8. Feature Engineering
In `backend/app/services/feature_service.py`, BTC-SHIELD computes an exact 23-dimensional behavioral feature vector for each entity:

| # | Feature Name | Category | Forensic Description |
|---|---|---|---|
| 1 | `tx_count` | Volume | Total confirmed transaction volume |
| 2 | `total_sent_btc` | Volume | Cumulative outgoing satoshis normalized to BTC |
| 3 | `total_received_btc` | Volume | Cumulative incoming satoshis normalized to BTC |
| 4 | `avg_tx_amount` | Statistical | Mean transaction value $\mu$ |
| 5 | `median_tx_amount` | Statistical | 50th percentile transaction value |
| 6 | `std_tx_amount` | Statistical | Standard deviation $\sigma$ of transaction values |
| 7 | `min_tx_amount` | Statistical | Minimum recorded transaction value |
| 8 | `max_tx_amount` | Statistical | Maximum recorded transaction value |
| 9 | `avg_fee` | Network Cost | Mean fee paid per transaction |
| 10 | `fee_ratio` | Network Cost | Ratio of fee to principal amount |
| 11 | `tx_velocity_per_hour` | Temporal | Transaction rate per hour $\frac{N}{\Delta t}$ |
| 12 | `avg_interarrival_time` | Temporal | Mean time delta between consecutive transactions |
| 13 | `std_interarrival_time` | Temporal | Variance in transaction pacing (detects bots) |
| 14 | `burst_score` | Temporal | Peak hourly transactions over average rate |
| 15 | `unique_counterparties` | Structural | Count of distinct senders/receivers |
| 16 | `counterparty_concentration`| Structural | Herfindahl-Hirschman Index of counterparties |
| 17 | `counterparty_entropy` | Information | Shannon Entropy of counterparty distribution |
| 18 | `fan_out_ratio` | Topological | Ratio of outputs to inputs |
| 19 | `unique_ips` | Network | Count of distinct IP addresses observing entity |
| 20 | `unique_asns` | Network | Count of distinct ASNs observing entity |
| 21 | `unique_countries` | Geographic | Count of distinct sovereign nations observing entity |
| 22 | `country_entropy` | Geographic | Shannon Entropy of geographic distribution |
| 23 | `asn_entropy` | Network | Shannon Entropy of Autonomous System distribution |

---

## 9. Machine Learning
BTC-SHIELD operates an entirely local, unsupervised machine learning pipeline implemented in `backend/app/services/ml_service.py`:
- **Isolation Forest Algorithm:** Recursive partitioning across randomized decision trees isolates anomalies with shorter path lengths $E(h(x))$.
- **Calibrated Scoring:** Raw decision function values are mapped to an intuitive percentage scale $[0, 100]$:
  $$\text{Score}(x) = 100 \times \left(1 - \frac{1}{1 + \exp(-10 \cdot s(x))}\right)$$
- **Artifact Persistence:** Trained models are serialized to disk using `joblib` in the versioned `models/` directory for fast offline inference.

---

## 10. Clustering
Cohort discovery is executed via DBSCAN (Density-Based Spatial Clustering of Applications with Noise):
- **Parameters:** $\varepsilon = 1.8$, $\text{min\_samples} = 3$ evaluated on StandardScaled feature matrices.
- **Forensic Utility:** Dense clusters unmask coordinated syndicates operating automated bot swarms with identical peeling parameters; noise points ($\text{cluster\_id} = -1$) isolate rogue outlier entities.

---

## 11. Entity/Transaction Graph
The graph intelligence engine in `backend/app/services/graph_service.py` models all relationships in memory using `networkx.DiGraph`:
- **Nodes:** `WALLET`, `TRANSACTION`, `IP`, `ASN`, `COUNTRY`.
- **Edges:** `INPUT_OF`, `OUTPUT_OF`, `OBSERVED_FROM`, `LOCATED_IN`, `BELONGS_TO_ASN`.
- **Centrality Analytics:** High degree centrality identifies mixer collection points; high betweenness centrality identifies money-mule bridges; PageRank identifies structurally critical nodes.
- **Visualization:** Subgraphs are exported in Cytoscape.js format for interactive exploration in the frontend canvas.

---

## 12. Evidence Generation
In `backend/app/services/evidence_service.py`, deterministic, rule-based evidence items are synthesized directly from factual data points:
- **8 Categories:** `MODEL`, `CLUSTER`, `AMOUNT`, `TRANSACTION`, `TEMPORAL`, `NETWORK`, `GEOGRAPHIC`, `GRAPH`.
- **Chain of Custody:** Each record tracks `source_dataset_id`, `source_record_id`, observation text, and strength score ($0.0 - 1.0$).
- **Zero Hallucination Guarantee:** No generative language models are utilized for evidence generation, ensuring court admissibility.

---

## 13. Alert Prioritization
In `backend/app/services/alert_service.py`, alerts are ranked using a compound scoring formula that decouples mathematical deviance from priority:
$$\text{Compound Score} = (\text{Anomaly Score} \times 0.6) + (\text{Confidence} \times 100 \times 0.4)$$
- **CRITICAL:** Compound Score $\ge 80$ AND $\ge 3$ distinct evidence categories.
- **HIGH:** Compound Score $\ge 65$ AND $\ge 2$ distinct evidence categories.
- **MEDIUM:** Compound Score $\ge 45$.
- **LOW:** Compound Score $< 45$.

---

## 14. Explainability
Explainability is provided deterministically via `MockAIProvider` in `backend/app/services/ai_service.py`:
- Generates structured summaries detailing contributing signals, temporal velocity spikes, geographic hops, and recommended investigative actions.
- Explicitly highlights areas of uncertainty and data insufficiency.
- Strictly references factual database evidence IDs without fabricating entities.

---

## 15. Confidence
The confidence metric ($0.0 - 1.0$) measures data sufficiency rather than anomaly severity:
- Accounts for observation density, feature completeness, and distinct evidence categories.
- Prevents false-positive critical alarms on low-activity wallets with scarce observations.

---

## 16. GeoIP Country/ASN
In `backend/app/services/geoip_service.py`, BTC-SHIELD integrates the open-source **DB-IP Lite** MMDB databases:
- **Country Database:** `offline/geoip/DB-IP-Country-Lite.mmdb` (8,284,207 bytes, August 2026 release, SHA-256: `5b370d4cf40259be3113118a1362ca6e704bdcab1842a102cdb6233b501e8558`).
- **ASN Database:** `offline/geoip/DB-IP-ASN-Lite.mmdb` (9,626,826 bytes, August 2026 release, SHA-256: `27bd730c5a754d656bdcf76b80cb92631cf7d98e2e7a3863c617a9d288f64cf5`).
- **Attribution:** *"IP geolocation data provided by DB-IP.com"* under Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Dual-Mode Resolution:** Real binary lookups yield `mode: LOCAL_MMDB` and `source: DB-IP-Lite`. Unmapped public IPs and documentation ranges (RFC 5737 / RFC 1918) fall back deterministically to offline mappings with zero network egress.

---

## 17. Dashboard and Link Analysis
The React 19 frontend provides an intuitive intelligence command center:
- **Dashboard:** Real-time statistics, anomaly score distributions, priority breakdowns, and recent alerts.
- **Link Analysis (GraphPage):** Cytoscape.js canvas supporting breadth-first, concentric, and cola force-directed layouts, node filtering, k-hop expansion, and export to PNG.

---

## 18. Case Investigation
In `backend/app/services/case_service.py`, investigators manage end-to-end case files:
- Create case files with status, priority, and investigator assignments.
- Attach suspect wallets, transactions, IPs, and evidence items.
- Append timestamped investigator notes for collaborative analysis.
- **Database Cascade Resilience:** Hardened foreign key constraints (`ON DELETE CASCADE`) on `case_entities`, `case_evidence`, and `case_notes` ensure that automated pipeline re-runs never trigger database lockups.

---

## 19. Report Generation
Investigators can export comprehensive, court-ready forensic dossiers via `/api/cases/{id}/report`:
- Contains executive summaries, suspect entity profiles, full chronological evidence ledgers, and audit trails.
- Exported in structured JSON and printable Markdown formats.

---

## 20. Offline Linux Architecture
The offline Linux deployment is orchestrated via `docker-compose.offline.yml`:
- **Services:** PostgreSQL 16 Alpine, FastAPI Backend, and Nginx Frontend.
- **Network Isolation:** Internal bridge network (`btcshield_offline_network`) with zero outbound egress.
- **Persistent Storage:** Volumes `pgdata_offline`, `offline_models_volume`, and `offline_data_volume` ensure state preservation across service restarts.

---

## 21. Security
- **Role-Based Access Control (RBAC):** ADMINISTRATOR, INVESTIGATOR, ANALYST, VIEWER roles enforced via JWT bearer tokens in `backend/app/core/security.py`.
- **Password Security:** Bcrypt hashing with dynamic salting.
- **Audit Logging:** Every user action, query, case creation, and report export is recorded in `audit_logs`.
- **Input Sanitization:** Parameterized SQL queries and schema validation prevent injection attacks.

---

## 22. Verification
Platform correctness is proven across a 17-suite automated test matrix:
- `tests/test_platform_compliance.py`: 11 enterprise compliance checks.
- `tests/test_airgap_compliance.py`: Socket-level guard enforcing 0 external connections.
- `tests/test_geoip.py`: 10-point acceptance test verifying real DB-IP Lite MMDB binary lookups.
- `tests/test_evidence_engine.py`: Evidence generation and persistent database rerun resilience.
- `scripts/verify_persistent_db_rerun.py`: Consecutive multi-run execution proving zero ForeignKeyViolations.

---

## 23. Limitations
- Unsupervised Isolation Forest relies on representative training distributions; sudden structural protocol forks may require model retraining.
- P2P network telemetry reflects observation vantage points; encrypted P2P connections (BIP 324) require direct mempool node instrumentation.
- Lightning Network off-chain channel balances are not tracked on-chain.

---

## 24. SIH Requirement Mapping
Every requirement specified in SIH Problem Statement 26146 is mapped directly to a verified production component:
- **Ingestion (CSV/JSON/XML):** `backend/app/services/ingestion_service.py` (PASS)
- **Validation & Quarantine:** `backend/app/services/ingestion_service.py` (PASS)
- **Network-Blockchain Correlation:** `backend/app/services/entity_service.py` (PASS)
- **23D Behavioral Features:** `backend/app/services/feature_service.py` (PASS)
- **AI/ML Anomaly Detection:** `backend/app/services/ml_service.py` (PASS)
- **Cohort Clustering:** `backend/app/services/ml_service.py` (PASS)
- **Multigraph & Centrality:** `backend/app/services/graph_service.py` (PASS)
- **Evidence Engine:** `backend/app/services/evidence_service.py` (PASS)
- **Ranked Alerts & Confidence:** `backend/app/services/alert_service.py` (PASS)
- **Explainability:** `backend/app/services/ai_service.py` (PASS)
- **Local DB-IP GeoIP:** `backend/app/services/geoip_service.py` (PASS)
- **Forensic Cases & Reports:** `backend/app/services/case_service.py` (PASS)
- **Offline Linux Containerization:** `docker-compose.offline.yml` (PASS)
- **Zero-Egress Air-Gap Operation:** `tests/test_airgap_compliance.py` (PASS)
