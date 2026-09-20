# BTC-SHIELD REST API Reference Manual

**Base URL:** `http://localhost:8000/api`  
**API Specification:** OpenAPI 3.1.0  
**Interactive Documentation:** `http://localhost:8000/docs` (Swagger UI) / `http://localhost:8000/redoc` (ReDoc)  

---

## 1. Authentication & Security

### `POST /api/auth/login`
Authenticates an investigator and returns an RFC 7519 JSON Web Token (JWT). Supports both standard JSON payloads and OAuth2 Form-data.
- **Request Body (JSON):**
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

### `GET /api/auth/me`
Returns current authenticated investigator profile.
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):**
  ```json
  {
    "id": 1,
    "username": "admin",
    "email": "admin@btcshield.gov",
    "role": "ADMINISTRATOR",
    "is_active": true,
    "created_at": "2026-09-20T10:00:00Z"
  }
  ```

---

## 2. Command Center & Telemetry

### `GET /api/dashboard/`
Aggregates platform KPIs, priority lead summaries, score histograms, and recent alerts.
- **Response (200 OK):**
  ```json
  {
    "stats": {
      "totalTx": 1000,
      "activeWallets": 6275,
      "monitoredIps": 1000,
      "activeAlerts": 775,
      "totalAsns": 8,
      "totalObservations": 2000,
      "openCases": 0,
      "totalEvidence": 2063,
      "totalDatasets": 1
    },
    "alerts": {
      "critical": 701,
      "high": 0,
      "medium": 0,
      "low": 74,
      "new": 775,
      "reviewing": 0,
      "resolved": 0
    },
    "cases": {
      "open": 0,
      "active": 0,
      "closed": 0
    },
    "anomalyDistribution": {
      "0-20": 10859,
      "20-40": 556,
      "40-60": 128,
      "60-80": 223,
      "80-100": 784
    },
    "recentAlerts": [ ... ],
    "processingStatus": { ... },
    "modelInfo": {
      "totalRuns": 2,
      "latestModel": "Isolation Forest (v2.0)",
      "latestTrainedAt": "2026-09-20T11:56:33Z"
    }
  }
  ```

### `GET /api/system/status`
Real-time microservice operational status.
- **Response (200 OK):**
  ```json
  {
    "database": "OPERATIONAL",
    "ml_service": "ok",
    "ai_provider": "mock",
    "uptime_seconds": 3600
  }
  ```

---

## 3. Dataset Ingestion & Pipeline

### `POST /api/datasets/upload`
Uploads raw transaction/telemetry file (CSV, JSON, XML), validates records, and detects duplicates.
- **Request:** `multipart/form-data` with `file` binary.
- **Response (200 OK):**
  ```json
  {
    "message": "Dataset uploaded and processed",
    "dataset": {
      "id": 1,
      "name": "btc_shield_synthetic_transactions.csv",
      "format": "csv",
      "status": "COMPLETED",
      "total_records": 1000,
      "valid_records": 1000,
      "invalid_records": 0,
      "duplicate_records": 0
    }
  }
  ```

### `POST /api/datasets/{id}/process` (or `POST /api/processing/run-pipeline?dataset_id={id}`)
Executes the full intelligence pipeline: Entity Resolution -> Feature Engineering -> ML -> Graph -> Evidence -> Alerts.
- **Response (200 OK):**
  ```json
  {
    "message": "Processing complete for dataset 1",
    "dataset_id": 1,
    "status": "PIPELINE_COMPLETE",
    "evidence_count": 2063,
    "alert_count": 775,
    "ml_result": { ... }
  }
  ```

---

## 4. Alert Prioritization

### `GET /api/alerts/`
Retrieves ranked alert leads with filtering and pagination.
- **Query Parameters:**
  - `priority` (optional): `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
  - `status` (optional): `NEW`, `REVIEWING`, `RESOLVED`, `DISMISSED`
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response (200 OK):**
  ```json
  {
    "alerts": [
      {
        "id": 1,
        "entity_type": "WALLET",
        "entity_id": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
        "anomaly_score": 98.4,
        "confidence": 0.85,
        "priority": "CRITICAL",
        "model_version": "IF-2.0",
        "contributing_signals": [ ... ],
        "status": "NEW",
        "created_at": "2026-09-20T11:56:33Z"
      }
    ],
    "total": 775
  }
  ```

### `GET /api/alerts/{id}`
Returns granular alert details and attached evidence signal IDs.

---

## 5. Investigation Link Analysis Graph

### `GET /api/graph/{entity_type}/{entity_id}?hops=1`
Extracts a $k$-hop subgraph centered on the target entity formatted for Cytoscape.js.
- **Query Parameters:** `hops` (Integer: 1, 2, or 3)
- **Response (200 OK):**
  ```json
  {
    "nodes": [
      {
        "data": {
          "id": "WALLET:1BvBMSEY...",
          "label": "1BvBMSEY...",
          "type": "WALLET",
          "anomaly_score": 98.4,
          "is_center": true,
          "centrality": {
            "degree": 14,
            "pagerank": 0.042
          }
        }
      }
    ],
    "edges": [
      {
        "data": {
          "id": "WALLET:1BvBMSEY...->TX:tx001",
          "source": "WALLET:1BvBMSEY...",
          "target": "TX:tx001",
          "type": "INPUT_OF",
          "amount": 50000
        }
      }
    ],
    "stats": {
      "node_count": 12,
      "edge_count": 16,
      "center_node": "WALLET:1BvBMSEY...",
      "hops": 1
    }
  }
  ```

---

## 6. Wallets, Transactions, and Network

- `GET /api/wallets/` - List resolved wallets with financial stats and transaction counts.
- `GET /api/wallets/{address}` - Full wallet intelligence (transactions, counterparties, observations, evidence).
- `GET /api/transactions/` - List transactions with amounts, fees, and script types.
- `GET /api/transactions/{txid}` - Transaction detail with inputs, outputs, and network observations.
- `GET /api/ips` & `GET /api/ips/{ip}` - Monitored IP telemetry and correlated wallet actors.
- `GET /api/asns` & `GET /api/asns/{asn}` - Autonomous system jurisdiction mapping.
- `GET /api/timeline/{entity_type}/{entity_id}` - Chronological vertical event sequence.
- `GET /api/ai/interpret/{entity_type}/{entity_id}` - Zero-hallucination explainability narrative.

---

## 7. Case Management & Dossiers

- `GET /api/cases/` - List active investigation cases.
- `POST /api/cases/` - Create a case dossier (optional `alert_id` auto-pins entities and evidence).
- `GET /api/cases/{id}` - Case detail with pinned entities, evidence, and notes.
- `PATCH /api/cases/{id}` - Update case title, description, priority, or status.
- `POST /api/cases/{id}/notes` - Log an investigator timestamped note.
- `GET /api/cases/{id}/report` - Generate automated forensic intelligence dossier.
