# System Architecture

## Overview
BTC-SHIELD employs a modular, microservices-oriented architecture suitable for both isolated on-premise deployments and scalable cloud hosting.

## Data Flow Pipeline
1. **Ingestion:** Raw transaction and network telemetry data is parsed and validated against JSON Schemas.
2. **Entity Resolution:** Heuristic clustering is applied to link multiple addresses to unified actor entities.
3. **Feature Engine:** Extracted features (velocity, fan-out ratio, time-window density) are computed.
4. **Machine Learning:** Isolation Forest models score the features for anomalous behavior.
5. **Graph Aggregation:** Nodes (addresses/entities) and edges (transactions) are materialized for UI consumption.

## Component Descriptions
- **Backend API:** FastAPI application providing RESTful interfaces.
- **Database:** PostgreSQL handling relational mapping of entities, cases, and audit logs.
- **Frontend UI:** React SPA with complex graph visualizations using tools like Cytoscape.js or React Flow.
- **ML Pipeline:** Asynchronous workers that periodically re-train on new baselines and score new transactions.

## Security Architecture
All endpoints are secured via JWT. Sensitive operations require elevated RBAC roles.
Database credentials and secrets are managed via `.env` files (not committed to version control).
