# BTC-SHIELD — Security Architecture & Threat Model

**Platform:** BTC-SHIELD (Bitcoin Transaction & Network Intelligence Platform)  
**Target:** Enterprise Forensic & Intelligence Software Specification  
**Classification:** Forensics & Intelligence Software Architecture  

---

## 1. Executive Security Summary

BTC-SHIELD is engineered for deployment within sensitive national security, law enforcement, and intelligence environments. The platform enforces defense-in-depth principles across data ingestion, API transport, authentication, identity authorization, and database persistence.

Core security guarantees:
1. **Zero Data Fabrication**: All behavioral signals, anomaly scores, and evidence items are mathematically traceable to raw data.
2. **Deterministic Provenance**: Ingested payloads remain immutable in the `raw_records` repository.
3. **Air-Gapped Egress Isolation**: Fully functional in 100% offline Linux environments without external cloud API dependencies.
4. **Forensic Chain-of-Custody**: All investigator actions, case exports, and logins are immutably recorded in the `audit_logs` table.

---

## 2. Threat Model & Mitigation Matrix

| Threat Category | Potential Attack Vector | BTC-SHIELD Mitigation |
| :--- | :--- | :--- |
| **Data Ingestion (XXE)** | XML entity expansion ("Billion Laughs"), external entity injection in XML datasets. | Hardened with `defusedxml.ElementTree` with disabled entity expansion and external DTD resolution. |
| **Data Ingestion (Malformed / DoS)** | Gigabyte-sized malformed CSV/JSON rows crashing in-memory buffers. | Streaming ingestion with row-by-row quarantine; bad rows written to `raw_records(is_valid=False)` without aborting batch. |
| **SQL Injection** | Malicious address or TXID strings containing SQL escape sequences. | 100% parameterized queries via SQLAlchemy 2.0 ORM; zero raw string interpolation. |
| **Credential Compromise** | Rainbow table attacks against stored user credentials. | Direct `bcrypt` password hashing with auto-generated 12-round salt. |
| **Session Hijacking** | Token replay or forged authorization claims. | Cryptographically signed HMAC-SHA256 JWT tokens with 30-minute expiration windows. |
| **Unauthorized Elevation** | Viewer attempting case editing or dataset uploads. | Mandatory FastAPI `require_role` dependency middleware enforcing strict RBAC. |
| **Chain-of-Custody Tampering** | Retrospective modification of evidence or investigator notes. | Append-only note structure and immutable audit logging storing user ID, timestamp, and client IP. |

---

## 3. Role-Based Access Control (RBAC) Matrix

BTC-SHIELD distinguishes four role tiers:

| Resource / Action | ADMINISTRATOR | INVESTIGATOR | ANALYST | VIEWER |
| :--- | :---: | :---: | :---: | :---: |
| **View Dashboard & System KPIs** | Yes | Yes | Yes | Yes |
| **Inspect Wallets, TXs, IPs, ASNs** | Yes | Yes | Yes | Yes |
| **Query Investigation Graph (Cytoscape)** | Yes | Yes | Yes | Yes |
| **Inspect Heuristics & Peeling Chains** | Yes | Yes | Yes | Yes |
| **Upload Datasets (CSV, JSON, XML)** | Yes | Yes | Yes | No |
| **Trigger Pipeline / Retrain ML** | Yes | No | Yes | No |
| **Triage & Update Alert Review States** | Yes | Yes | No | No |
| **Create & Update Cases** | Yes | Yes | No | No |
| **Add Case Notes & Attach Evidence** | Yes | Yes | No | No |
| **Export Forensic Case Reports** | Yes | Yes | No | No |
| **Inspect System Audit Logs** | Yes | Yes | No | No |
| **Manage Users & Assign Roles** | Yes | No | No | No |

---

## 4. Authentication & Token Architecture

### 4.1 JWT Structure
Tokens are generated using HMAC-SHA256 (`HS256`):
```json
{
  "sub": "user_id",
  "exp": 1758369600,
  "iat": 1758367800
}
```
- Expiration default: 30 minutes.
- Secret key stored via `JWT_SECRET` environment variable (never checked into version control).

### 4.2 Password Hashing
Direct bcrypt implementation (`backend/app/core/security.py`):
```python
import bcrypt

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

---

## 5. Input Sanitization & Data Protection

### 5.1 Safe Multi-Format Parsing
- **XML:** Built with `defusedxml` to disallow entity expansion, external parameter entities, and DTD retrieval.
- **CSV:** Parsed using Python's robust `csv.DictReader` with isolated string stripping and type coercion.
- **JSON:** Strict Pydantic v2 validation enforcing schema integrity.

### 5.2 Network Egress Restriction (Air-Gapped Mode)
- In Mode A (Air-Gapped Linux):
  - Local SQLite database `btcshield.db`.
  - Built-in `MockAIProvider` for deterministic, offline evidence explanation.
  - Zero outgoing connections to third-party endpoints.
