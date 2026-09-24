# BTC-SHIELD — Air-Gapped Offline Linux Architecture

## Overview
BTC-SHIELD provides a first-class, fully air-gapped, zero-egress offline runtime designed for Linux workstations and secure investigative environments.

This deployment model is specifically tailored for **SIH Problem Statement 26146 ("AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic")** and guarantees that all Bitcoin transaction correlation, network telemetry analysis, graph intelligence, machine learning anomaly detection, alert generation, and case dossier generation execute 100% locally without an active internet connection.

---

## Directory Layout
```text
offline/
├── datasets/          # SIH-compliant raw metadata files (CSV, JSON, XML)
├── geoip/             # MaxMind binary database location (City & ASN mmdb)
├── models/            # Persisted local ML models (Isolation Forest, DBSCAN, Scaler)
├── data/              # Local storage for raw file processing & sqlite backup
└── README.md          # Architectural and operational specification
```

---

## Key Offline Capabilities

1. **Zero External Network Egress:**
   - No external APIs, no OpenAI or remote LLM connections, no cloud storage, no blockchain explorers.
   - Built-in `MockAIProvider` provides deterministic, mathematical investigative reasoning without cloud API tokens.

2. **Self-Contained Local Database:**
   - Runs on local PostgreSQL container (persisted to Docker volume `pgdata_offline`) or local SQLite engine.
   - Automated schema migrations via Alembic.

3. **Local Machine Learning Analytics:**
   - Unsupervised Isolation Forest anomaly scoring scaled to `[0, 100]`.
   - Density-based DBSCAN clustering for behavioral anomaly grouping.
   - Feature engineering running locally via NumPy and Pandas.

4. **Multi-Format Ingestion:**
   - SIH-compliant CSV, JSON, XML, and ZIP bundle parsers.
   - Strict validation and quarantine for malformed syntax, invalid Bitcoin addresses, or irregular timestamps.

5. **Local Dual-Mode GeoIP Resolution:**
   - Uses local `GeoLite2-City.mmdb` and `GeoLite2-ASN.mmdb` if present.
   - Deterministic offline RFC 5737/1918 fallback if MMDB files are absent, clearly indicating fallback state in telemetry.

---

## Operational Scripts
All operational management scripts are located in `scripts/`:
- `scripts/offline-start.sh`: Validates prerequisites, starts the Docker stack, awaits health checks, and reports readiness.
- `scripts/offline-stop.sh`: Gracefully shuts down the containers while preserving all data volumes.
- `scripts/offline-reset.sh`: Interactively resets containers or purges local persistent databases.
- `scripts/offline-test.sh`: Runs the full automated verification test suite against the offline deployment.
