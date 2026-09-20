# Deployment Guide

## Offline / SIH Deployment (Docker Compose)
For strictly offline environments, use Docker Compose. This packages the database, frontend, and backend together without external dependencies.
1. `docker-compose build`
2. `docker-compose up -d`
3. Check logs: `docker-compose logs -f`

## Cloud Deployment
- **Frontend:** GitHub Pages via GitHub Actions (`deploy-frontend.yml`).
- **Backend:** Can be deployed to AWS EC2, Heroku, or DigitalOcean. Ensure CORS is configured properly.
- **Database:** Managed PostgreSQL (e.g., Neon.tech, AWS RDS).

## Database Migrations
Migrations are handled by Alembic (Backend).
Run: `alembic upgrade head` inside the backend container to apply schemas.

## Environment Variables
- `DATABASE_URL`: Connection string for Postgres.
- `SECRET_KEY`: JWT signing key.
- `CORS_ORIGINS`: Comma-separated list of allowed origins.
