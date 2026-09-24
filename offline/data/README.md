# BTC-SHIELD — Offline Local Data Storage

This directory serves as local persistent storage for temporary ingestion uploads, quarantined malformed records, and local data buffers when operating in air-gapped Linux environments.

## Directory Structure
- `offline/data/uploads/` — Temporary landing folder for uploaded multi-format datasets.
- `offline/data/quarantine/` — Isolated storage for malformed or unparseable input records for forensic inspection.
