# BTC-SHIELD 10-Minute Jury Demonstration Script

**Competition:** Smart India Hackathon 2026  
**Problem Statement:** 26146 — AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic  
**Target Organization:** National Technical Research Organisation (NTRO)  
**Demonstration Mode:** Air-Gapped Offline Linux Demonstration / Live Cloud Dual-Stack  

---

## Quick Reference Demonstration Checklist
- [ ] Backend active on `http://localhost:8000` (FastAPI Swagger `/docs`)
- [ ] Frontend active on `http://localhost:5173`
- [ ] Test dataset ready at `data/samples/dataset_1000.csv`
- [ ] Default login credentials: `admin` / `admin123`
- [ ] Network adapter disabled (optional for offline verification proof)

---

## Minute 0:00 - 1:00 | Problem Framing & Technical Mandate
**Screen:** Command Center Dashboard (`http://localhost:5173/`)  
**Talking Points:**
> "Respected Evaluators and Technical Experts from NTRO:  
> Problem Statement 26146 challenges us to monitor and analyze Bitcoin transaction traffic by synthesizing two traditionally siloed domains: on-chain ledger transfers and off-chain peer-to-peer network telemetry.
>
> Many hackathon projects rely on fake synthetic labels, rule-based if-else scripts pretending to be AI, or random node graphs.  
> **BTC-SHIELD is fundamentally different.** It is built on strict evidentiary provenance:  
> `RAW TELEMETRY -> NORMALIZED ENTITIES -> 23 BEHAVIORAL FEATURES -> UNSUPERVISED ML -> VERIFIED EVIDENCE -> FORENSIC CASE DOSSIER`.  
> Every anomaly score, graph edge, and AI explanation displayed today is mathematically derived and traceable back to verified transactions."

---

## Minute 1:00 - 2:00 | Offline Multi-Format Ingestion & Validation
**Screen:** Dataset Management (`/datasets`)  
**Action:**
1. Click **Ingest Dataset** button.
2. Select `data/samples/dataset_1000.csv` (or demonstrate drag-and-drop of JSON/XML).
3. Click **Upload Dataset**.
**Talking Points:**
> "Our ingestion subsystem handles RFC 4180 CSV, JSON, and XML telemetry feeds.  
> As the file ingests, notice that our validator performs field-level syntax verification on Base58Check and Bech32 Bitcoin addresses, IPv4/IPv6 headers, and multi-format timestamps.  
> Notice the **Quality Metrics column**: it displays exactly how many records were valid, rejected, or flagged as cryptographic duplicates via SHA-256 content hashing. Raw records remain immutable in our database for evidentiary integrity."

---

## Minute 2:00 - 3:00 | Automated Intelligence Pipeline & Entity Resolution
**Screen:** Dataset Management (`/datasets`)  
**Action:**
1. Click the **Run ML Pipeline** button on the ingested dataset.
2. Watch the status transition: `PROCESSING_PIPELINE` -> `PIPELINE_COMPLETE`.
**Talking Points:**
> "With a single click, our backend executes the complete six-stage intelligence pipeline:  
> 1. **Entity Resolution:** Maps inputs and outputs across all transactions into unified wallet actors and monitored IP entities.  
> 2. **Feature Extraction:** Computes 23 multi-dimensional behavioral features per entity in under 1 second using bulk in-memory hash indexing.  
> 3. **Unsupervised ML:** Trains Isolation Forest and DBSCAN clustering models.  
> 4. **Graph Persistence:** Constructs the NetworkX directed multigraph and computes PageRank centrality.  
> 5. **Evidence Generation:** Generates discrete evidence records.  
> 6. **Alert Prioritization:** Scores and ranks investigative leads."

---

## Minute 3:00 - 4:00 | Feature Engineering & Model Lab
**Screen:** Model Lab (`/models`)  
**Action:**
1. Point to the **Isolation Forest** and **DBSCAN** registry cards.
2. Review the feature dimensions tag cloud (23 features).
3. Show the evaluation metrics: trained sample count, detected anomalies, anomaly ratio, and silhouette score.
**Talking Points:**
> "Here in the Model Lab, we inspect the trained unsupervised models.  
> Rather than arbitrary thresholds, our Isolation Forest isolates anomalous vectors across 23 dimensions: transaction velocity, fan-out peeling ratios, Shannon entropy across counterparties and ASNs, and inter-arrival burstiness.  
> DBSCAN automatically computes an adaptive epsilon based on the 90th percentile $k$-nearest neighbor distance to partition behavioral noise points. Every model run is serialized to disk and versioned with full parameters."

---

## Minute 4:00 - 5:00 | Alert Prioritizer & Explainable AI Assistant
**Screen:** Alert Prioritizer (`/alerts`) -> Alert Detail (`/alerts/:id`)  
**Action:**
1. Filter alerts by `CRITICAL` priority.
2. Click **Details** on the top lead.
3. Show the **Anomaly Score Heat Bar**, **Data Confidence Meter**, and the **Explainable AI Assistant** box.
**Talking Points:**
> "In the Alert Prioritizer, alerts are ranked by compound risk: anomaly score multiplied by evidence strength and signal diversity.  
> Notice that we strictly separate **Anomaly Score** (how mathematically unusual the entity is) from **Data Confidence** (how much empirical observation data we actually have).  
> In the Alert Detail view, our **Zero-Hallucination Explainability Assistant** synthesizes the evidence into natural language findings, recommended investigator review actions, and explicit uncertainty assessments. It never hallucinates unverified criminal accusations."

---

## Minute 5:00 - 6:00 | Cytoscape.js Link Analysis Multigraph
**Screen:** Investigation Graph (`/graph`)  
**Action:**
1. Switch layouts: Click **Concentric Layout** -> **Breadth-First Hierarchy**.
2. Select 1, 2, or 3 Hops.
3. Click on a node to show the **Node Detail Drawer** with Degree, PageRank, and Anomaly Score.
4. Click **Export PNG** to show forensic image generation.
**Talking Points:**
> "Our Link Analysis Graph is a fully interactive Cytoscape.js directed multigraph.  
> It visualizes five distinct entity types: Wallets (blue), Transactions (purple), IPs (emerald), ASNs (amber), and Countries (cyan).  
> Anomalous entities are visually highlighted with red pulsing borders.  
> Investigators can switch layout algorithms, expand 1 to 3 hops, inspect centrality metrics, and export high-resolution forensic diagrams for courtroom or intelligence briefings."

---

## Minute 6:00 - 7:00 | Chronological Activity Timeline
**Screen:** Activity Timeline (`/timeline?entityType=WALLET&entityId=...`)  
**Action:**
1. Filter events by `TRANSACTION`, `NETWORK`, or `ALERT`.
2. Scroll through the chronological vertical trail.
**Talking Points:**
> "Investigative leads require precise temporal reconstruction.  
> The Timeline module unifies on-chain block confirmations with network-layer IP observations in strict chronological order.  
> Investigators can pinpoint when an entity initiated a peel chain, when its IP address hopped across autonomous systems, and the exact moment our models triggered an anomaly lead."

---

## Minute 7:00 - 8:00 | Case Dossiers, Notes Logging & Forensic Report Export
**Screen:** Cases & Reports (`/cases`) -> Case Detail (`/cases/:id`)  
**Action:**
1. Click **Promote to Case** or open an active case.
2. Review **Pinned Entities** and **Attached Evidence**.
3. Type an investigator note: `'High-priority laundering hub identified via PageRank centrality.'` and click **Log Note**.
4. Open the **Forensic Report** tab and click **Download JSON** or **Print Preview**.
**Talking Points:**
> "From an alert, an investigator promotes the lead to an active Case Dossier with one click.  
> The dossier pins target entities, attaches immutable evidence signals, and maintains an investigator audit log.  
> In the Forensic Report tab, the platform auto-generates a standardized intelligence dossier with legal disclaimers, timestamps, and evidence chains, exportable as JSON or formatted printable output."

---

## Minute 8:00 - 9:00 | Dual-Mode Architecture & Automated Testing
**Screen:** System Status (`/system`) & Terminal  
**Action:**
1. Show the System Status telemetry: FastAPI, Database, ML Engine, GeoIP, and NetworkX.
2. In terminal, show test results: `pytest tests -v` (16 passed tests).
**Talking Points:**
> "BTC-SHIELD operates in two production topologies:  
> - **Mode A:** Fully air-gapped offline Linux demonstration inside Docker Compose with zero network egress.  
> - **Mode B:** Cloud deployment with GitHub Actions CI/CD, GitHub Pages frontend, and Neon PostgreSQL.  
> Our automated test suite features 16 comprehensive unit and integration tests covering ingestion, features, models, graph topology, evidence logic, and REST endpoints."

---

## Minute 9:00 - 10:00 | Questions & Technical Defense
**Key Answers for Jury Questions:**
1. **How do you prevent false positives?**  
   *Answer:* "We combine Isolation Forest anomaly scores with multi-category evidence confirmation and a distinct Data Sufficiency Confidence rating. Single isolated spikes do not trigger critical alerts without corroborating temporal or structural signals."
2. **Does this system require an internet connection?**  
   *Answer:* "No. BTC-SHIELD runs 100% offline on any standard Linux distribution using embedded SQLite or local Docker PostgreSQL, with offline GeoIP databases and deterministic synthetic scenario generation."
3. **How does the AI assistant avoid hallucinations?**  
   *Answer:* "Our MockAIProvider generates explanations strictly from validated evidence categories and mathematical metrics present in the database. It is hardcoded never to extrapolate unobserved facts."
