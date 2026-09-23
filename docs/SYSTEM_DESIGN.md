# BTC-SHIELD System Design & Data Model Specification

**Platform:** BTC-SHIELD — Bitcoin Transaction & Network Intelligence Platform  
**Target:** Enterprise Forensic & Cryptographic Intelligence Specification  

---

## 1. Architectural Principles

1. **Evidentiary Integrity:** All intelligence derived by the platform must trace back to immutable raw records.
2. **Offline Self-Sufficiency:** The system must install, run, train models, and generate forensic reports without external internet access.
3. **Decoupled Relational Schema:** Clear separation between on-chain blockchain entities (Wallets, Transactions, UTXOs) and network layer telemetry (IPs, ASNs, Observations).
4. **Sub-second Responsiveness:** Critical UI endpoints must respond within 100ms through pre-aggregated lookups, database indexes, and in-memory multigraph representations.

---

## 2. Entity-Relationship & Relational Schema

The relational schema is managed through SQLAlchemy 2.0 and Alembic:

### 2.1 Core Ingestion & Telemetry Tables

```sql
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    format VARCHAR(32) NOT NULL, -- 'csv', 'json', 'xml'
    status VARCHAR(64) DEFAULT 'PENDING',
    total_records INTEGER DEFAULT 0,
    valid_records INTEGER DEFAULT 0,
    invalid_records INTEGER DEFAULT 0,
    duplicate_records INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw_records (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    raw_data JSONB NOT NULL,
    is_valid BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 Normalized On-Chain & Network Tables

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    txid VARCHAR(64) UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    fee FLOAT DEFAULT 0.0,
    script_type VARCHAR(32),
    total_input FLOAT DEFAULT 0.0,
    total_output FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tx_txid ON transactions(txid);

CREATE TABLE transaction_inputs (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    wallet_address VARCHAR(128) NOT NULL,
    amount FLOAT DEFAULT 0.0,
    position INTEGER DEFAULT 0
);
CREATE INDEX idx_inputs_wallet ON transaction_inputs(wallet_address);

CREATE TABLE transaction_outputs (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    wallet_address VARCHAR(128) NOT NULL,
    amount FLOAT DEFAULT 0.0,
    position INTEGER DEFAULT 0
);
CREATE INDEX idx_outputs_wallet ON transaction_outputs(wallet_address);

CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    address VARCHAR(128) UNIQUE NOT NULL,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    total_sent FLOAT DEFAULT 0.0,
    total_received FLOAT DEFAULT 0.0,
    tx_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_wallets_address ON wallets(address);

CREATE TABLE network_observations (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    transaction_id VARCHAR(64),
    src_ip VARCHAR(64) NOT NULL,
    dst_ip VARCHAR(64),
    src_port INTEGER,
    dst_port INTEGER,
    timestamp TIMESTAMP,
    geo_country VARCHAR(8),
    asn VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_net_src_ip ON network_observations(src_ip);
CREATE INDEX idx_net_txid ON network_observations(transaction_id);

CREATE TABLE ip_entities (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(64) UNIQUE NOT NULL,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    observation_count INTEGER DEFAULT 0,
    asn VARCHAR(64),
    country VARCHAR(8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE asn_entities (
    id SERIAL PRIMARY KEY,
    asn_number VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255),
    country_count INTEGER DEFAULT 0,
    ip_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 Analytics, Evidence, and Alerts Tables

```sql
CREATE TABLE behavioral_features (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(32) NOT NULL, -- 'WALLET', 'IP'
    entity_id VARCHAR(128) NOT NULL,
    feature_schema_version VARCHAR(16) NOT NULL,
    features JSONB NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_feat_entity ON behavioral_features(entity_type, entity_id);

CREATE TABLE model_runs (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    model_type VARCHAR(64) NOT NULL, -- 'ISOLATION_FOREST', 'DBSCAN'
    model_version VARCHAR(64) NOT NULL,
    parameters JSONB NOT NULL,
    evaluation_metrics JSONB,
    artifact_path VARCHAR(255),
    status VARCHAR(32) DEFAULT 'COMPLETED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE anomaly_results (
    id SERIAL PRIMARY KEY,
    model_run_id INTEGER REFERENCES model_runs(id),
    entity_type VARCHAR(32) NOT NULL,
    entity_id VARCHAR(128) NOT NULL,
    anomaly_score FLOAT, -- Calibrated [0.0 - 100.0]
    cluster_id INTEGER,  -- DBSCAN cluster ID (-1 for noise)
    is_anomaly BOOLEAN DEFAULT FALSE,
    features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(32) NOT NULL,
    entity_id VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL, -- 'MODEL', 'CLUSTER', 'AMOUNT', 'TRANSACTION', 'TEMPORAL', 'NETWORK', 'GEOGRAPHIC', 'GRAPH'
    observation TEXT NOT NULL,
    details JSONB,
    source_dataset_id INTEGER REFERENCES datasets(id),
    source_record_id INTEGER,
    strength FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(32) NOT NULL,
    entity_id VARCHAR(128) NOT NULL,
    anomaly_score FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    priority VARCHAR(32) NOT NULL, -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    model_version VARCHAR(64),
    contributing_signals JSONB,
    evidence_ids JSONB,
    status VARCHAR(32) DEFAULT 'NEW',
    review_state VARCHAR(32) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.4 Case Management & Audit Dossier Tables

```sql
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(32) DEFAULT 'OPEN', -- 'OPEN', 'ACTIVE', 'CLOSED'
    priority VARCHAR(32) DEFAULT 'MEDIUM',
    investigator_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE case_entities (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id) ON DELETE CASCADE,
    entity_type VARCHAR(32) NOT NULL,
    entity_id VARCHAR(128) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE case_evidence (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id) ON DELETE CASCADE,
    evidence_id INTEGER REFERENCES evidence(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE case_notes (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(128) NOT NULL,
    resource_type VARCHAR(64) NOT NULL,
    resource_id VARCHAR(128),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
