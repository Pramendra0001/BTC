# Data Model

## Core Tables

### users
- `id` (UUID, PK)
- `email` (VARCHAR, Unique)
- `hashed_password` (VARCHAR)
- `role` (ENUM: admin, investigator, analyst, viewer)

### transactions
- `txid` (VARCHAR(64), PK)
- `timestamp` (TIMESTAMP)
- `fee` (BIGINT)
- `src_ip` (VARCHAR)
- `dst_ip` (VARCHAR)
- `geo_country` (VARCHAR(2))

### addresses
- `address` (VARCHAR, PK)
- `script_type` (VARCHAR)

### tx_inputs
- `id` (UUID, PK)
- `txid` (FK -> transactions.txid)
- `address` (FK -> addresses.address)
- `amount` (BIGINT)

### tx_outputs
- `id` (UUID, PK)
- `txid` (FK -> transactions.txid)
- `address` (FK -> addresses.address)
- `amount` (BIGINT)

### alerts
- `id` (UUID, PK)
- `txid` (FK -> transactions.txid)
- `anomaly_score` (FLOAT)
- `scenario_type` (VARCHAR)
- `status` (VARCHAR)

## Index Strategy
- B-Tree indexes on `transactions.timestamp` for time-series filtering.
- B-Tree indexes on `tx_inputs.address` and `tx_outputs.address` for fast graph traversal.
