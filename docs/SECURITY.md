# Security Guide

## Authentication
JSON Web Tokens (JWT) are used for all authentication.
Tokens expire every 30 minutes, requiring a refresh token flow.

## Authorization (RBAC)
- **Admin:** Manage users, configure system settings, trigger full pipeline resets.
- **Investigator:** Manage cases, edit alerts, assign tasks.
- **Analyst:** View alerts, add notes, view graphs.
- **Viewer:** Read-only access to dashboards.

## Audit Logging
Every write operation (POST, PUT, PATCH, DELETE) is logged in the `audit_logs` table containing:
- `user_id`
- `action`
- `resource_id`
- `timestamp`

## File Upload Security
Data ingestion files (CSV/JSON/XML) are validated strictly against their respective schemas.
Payloads exceeding 10MB are rejected by default unless chunked.
