# BTC-SHIELD
**Bitcoin Transaction & Network Intelligence Platform**

BTC-SHIELD is a comprehensive intelligence platform designed to detect, analyze, and visualize anomalous and illicit activities within the Bitcoin network. Developed for SIH 2026.

## Architecture Overview

```text
[Frontend (React/Vite)] <---> [Backend API (FastAPI)]
                                      |
                              [Data Processing]
                                      |
                              [Machine Learning]
                                      |
                             [PostgreSQL Database]
```

## Key Features
- **Deterministic Synthetic Data Generator:** Simulate realistic network topologies and anomalies.
- **Advanced Graph Visualization:** Trace transaction flows, consolidation, and peeling chains.
- **Machine Learning Integration:** Automated anomaly detection scoring via Isolation Forests & DBSCAN.
- **Role-Based Access Control (RBAC):** Granular permissions for admins, investigators, and viewers.
- **Offline Capable:** Full Docker Compose stack for secure, isolated deployments.

## Quick Start (Docker Compose)
1. Ensure Docker and Docker Compose are installed.
2. Run `docker-compose up -d`
3. Access the frontend at `http://localhost:3000`

## Development Setup
For manual setup, run the appropriate setup script for your OS:
- Windows: `.\scripts\setup-dev.ps1`
- Linux/Mac: `./scripts/setup-dev.sh`

## Tech Stack
| Component | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS, TanStack Query |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL 16 |
| Machine Learning | Scikit-Learn, NetworkX |
| Deployment | Docker, GitHub Actions |

## Testing
- Backend: Run `pytest` inside the `backend/` directory.
- Frontend: Run `npm run test` inside the `frontend/` directory.

## License
MIT License
