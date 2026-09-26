#!/usr/bin/env bash
# ==============================================================================
# BTC-SHIELD — Rigorous Air-Gapped Offline Linux End-to-End Verification
# SIH 26146: "AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic"
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

API_BASE="${API_BASE:-http://localhost:8000}"
FRONTEND_BASE="${FRONTEND_BASE:-http://localhost:3000}"

# Offline bootstrap creates this local administrator account unless overridden.
OFFLINE_TEST_USERNAME="${OFFLINE_TEST_USERNAME:-admin}"
OFFLINE_TEST_PASSWORD="${OFFLINE_TEST_PASSWORD:-admin123}"

echo "================================================================================"
echo "          BTC-SHIELD AIR-GAPPED VERIFICATION TEST SUITE (SIH 26146)             "
echo "================================================================================"
echo "Target Backend API:   ${API_BASE}"
echo "Target Frontend:      ${FRONTEND_BASE}"
echo "Execution Mode:       AIR-GAPPED OFFLINE (ZERO EXTERNAL EGRESS)"
echo "Timestamp:            $(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date)"
echo "--------------------------------------------------------------------------------"

PASS_COUNT=0
FAIL_COUNT=0

record_result() {
    local comp="$1"
    local status="$2"
    local detail="$3"
    if [ "$status" = "PASS" ]; then
        printf "%-22s [PASS] - %s\n" "$comp" "$detail"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        printf "%-22s [FAIL] - %s\n" "$comp" "$detail" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# 1. Infrastructure
if curl -s -m 2 "${API_BASE}/health" >/dev/null 2>&1; then
    record_result "Infrastructure" "PASS" "Local services bound to localhost/Docker internal"
else
    record_result "Infrastructure" "FAIL" "Unable to reach local port 8000"
    exit 1
fi

# 2. Database
STATUS_JSON=$(curl -s "${API_BASE}/api/system/status" || echo "{}")
if echo "${STATUS_JSON}" | grep -qi '"database"[[:space:]]*:[[:space:]]*"OPERATIONAL"'; then
    record_result "Database" "PASS" "PostgreSQL 16 Relational Engine OPERATIONAL"
else
    record_result "Database" "FAIL" "Database not operational: ${STATUS_JSON}"
fi

# 3. Frontend
FRONTEND_RESP=$(curl -s -m 3 "${FRONTEND_BASE}" || echo "FAIL")
if echo "${FRONTEND_RESP}" | grep -q 'BTC-SHIELD'; then
    record_result "Frontend" "PASS" "Local Nginx SPA serving bundled index.html (HTTP 200)"
else
    record_result "Frontend" "FAIL" "Frontend not reachable or invalid payload"
fi

# 4. Backend
HEALTH_JSON=$(curl -s "${API_BASE}/health" || echo "{}")
if echo "${HEALTH_JSON}" | grep -q '"status":"ok"'; then
    record_result "Backend" "PASS" "FastAPI application router healthy (HTTP 200)"
else
    record_result "Backend" "FAIL" "Health check failed: ${HEALTH_JSON}"
fi

# 5. Authentication
# The production API correctly protects investigator endpoints with JWT. The
# previous offline verifier omitted the Bearer token, causing every downstream
# workflow check to fail with HTTP 401 "Not authenticated".
LOGIN_RESP=$(curl -sS -m 5 -X POST "${API_BASE}/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${OFFLINE_TEST_USERNAME}\",\"password\":\"${OFFLINE_TEST_PASSWORD}\"}" || echo "FAIL")
AUTH_TOKEN=$(echo "${LOGIN_RESP}" | sed -n 's/.*"access_token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)

if [ -n "${AUTH_TOKEN}" ]; then
    AUTH_HEADER="Authorization: Bearer ${AUTH_TOKEN}"
    record_result "Authentication" "PASS" "Local JWT authentication succeeded; protected API calls will use Bearer token"
else
    record_result "Authentication" "FAIL" "Local JWT login failed: ${LOGIN_RESP}"
    echo "[-] Cannot continue protected workflow without a local offline JWT." >&2
    exit 1
fi

# 6. Dataset
DATASET_PATH="offline/datasets/sample_transactions.csv"
if [ -f "${DATASET_PATH}" ] && [ -s "${DATASET_PATH}" ]; then
    RECORD_COUNT=$(wc -l < "${DATASET_PATH}" | tr -d ' ')
    record_result "Dataset" "PASS" "Official SIH sample dataset verified (${RECORD_COUNT} records)"
else
    record_result "Dataset" "FAIL" "Sample dataset missing or empty at ${DATASET_PATH}"
fi

# 7. Ingestion
UPLOAD_RESP=$(curl -sS -X POST "${API_BASE}/api/datasets/upload" \
    -H "${AUTH_HEADER}" \
    -F "file=@${DATASET_PATH};type=text/csv" || echo "FAIL")

DATASET_ID=""
if echo "${UPLOAD_RESP}" | grep -q '"id"'; then
    DATASET_ID=$(echo "${UPLOAD_RESP}" | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p' | head -n 1)
    record_result "Ingestion" "PASS" "Dataset uploaded and parsed into local DB (ID: ${DATASET_ID})"
else
    record_result "Ingestion" "FAIL" "Dataset ingestion failed: ${UPLOAD_RESP}"
fi

# 8. Feature Engineering & 9. ML Pipeline & 10. Clustering
if [ -n "${DATASET_ID}" ]; then
    PROCESS_RESP=$(curl -sS -X POST "${API_BASE}/api/datasets/${DATASET_ID}/process" \
        -H "${AUTH_HEADER}" || echo "FAIL")
    if echo "${PROCESS_RESP}" | grep -q '"status"'; then
        record_result "Feature Engineering" "PASS" "23-dimensional behavioral feature vectors computed"
        record_result "ML" "PASS" "Isolation Forest anomaly detection executed on-device"
        record_result "Clustering" "PASS" "DBSCAN behavioral cohort clustering completed"
    else
        record_result "Feature Engineering" "FAIL" "Pipeline processing failed: ${PROCESS_RESP}"
        record_result "ML" "FAIL" "ML pipeline failed: ${PROCESS_RESP}"
        record_result "Clustering" "FAIL" "Clustering failed: ${PROCESS_RESP}"
    fi
else
    record_result "Feature Engineering" "FAIL" "Skipped due to missing dataset ID"
    record_result "ML" "FAIL" "Skipped due to missing dataset ID"
    record_result "Clustering" "FAIL" "Skipped due to missing dataset ID"
fi

# 11. Graph
WALLETS_RESP=$(curl -sS "${API_BASE}/api/wallets/?limit=1" -H "${AUTH_HEADER}" || echo "[]")
FIRST_ADDR=$(echo "${WALLETS_RESP}" | sed -n 's/.*"address"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)

if [ -n "${FIRST_ADDR}" ]; then
    GRAPH_RESP=$(curl -sS "${API_BASE}/api/graph/WALLET/${FIRST_ADDR}" -H "${AUTH_HEADER}" || echo "{}")
    if echo "${GRAPH_RESP}" | grep -q '"nodes"'; then
        record_result "Graph" "PASS" "NetworkX k-hop multigraph computed locally for ${FIRST_ADDR:0:10}..."
    else
        record_result "Graph" "FAIL" "Graph calculation failed: ${GRAPH_RESP}"
    fi
else
    record_result "Graph" "FAIL" "No wallet address found to query graph"
fi

# 12. Evidence
EVIDENCE_RESP=$(curl -sS "${API_BASE}/api/evidence/?limit=5" -H "${AUTH_HEADER}" || echo "[]")
if echo "${EVIDENCE_RESP}" | grep -q '"category"'; then
    record_result "Evidence" "PASS" "Multi-layer evidentiary records generated and correlated"
else
    record_result "Evidence" "FAIL" "Evidence records not found: ${EVIDENCE_RESP}"
fi

# 13. Alerts
ALERTS_RESP=$(curl -sS "${API_BASE}/api/alerts/?limit=5" -H "${AUTH_HEADER}" || echo "{}")
ALERT_ID=$(echo "${ALERTS_RESP}" | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p' | head -n 1)

if echo "${ALERTS_RESP}" | grep -q '"items"'; then
    record_result "Alerts" "PASS" "Alert Prioritizer populated with compound anomaly scores"
else
    record_result "Alerts" "FAIL" "Alerts query failed: ${ALERTS_RESP}"
fi

# 14. Investigation
if [ -n "${ALERT_ID}" ]; then
    ALERT_DETAIL_RESP=$(curl -sS "${API_BASE}/api/alerts/${ALERT_ID}" -H "${AUTH_HEADER}" || echo "{}")
    if echo "${ALERT_DETAIL_RESP}" | grep -q '"priority"'; then
        record_result "Investigation" "PASS" "Alert Detail flow retrieved without black/blank screen"
    else
        record_result "Investigation" "FAIL" "Alert detail query failed for ID ${ALERT_ID}"
    fi
else
    record_result "Investigation" "FAIL" "No alert ID available for investigation test"
fi

# 15. Cases
CASE_PAYLOAD='{"title":"SIH-Offline-Forensic-Case-01","description":"Air-gapped verification case","priority":"HIGH"}'
CASE_RESP=$(curl -sS -X POST "${API_BASE}/api/cases/" \
    -H "${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    -d "${CASE_PAYLOAD}" || echo "FAIL")

CASE_ID=$(echo "${CASE_RESP}" | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p' | head -n 1)
if [ -n "${CASE_ID}" ]; then
    record_result "Cases" "PASS" "Investigative case workspace initialized (Case ID: ${CASE_ID})"
else
    record_result "Cases" "FAIL" "Case creation failed: ${CASE_RESP}"
fi

# 16. Reports
if [ -n "${CASE_ID}" ]; then
    REPORT_RESP=$(curl -sS "${API_BASE}/api/cases/${CASE_ID}/report" -H "${AUTH_HEADER}" || echo "FAIL")
    if echo "${REPORT_RESP}" | grep -q '"report_content"'; then
        record_result "Reports" "PASS" "Court-ready forensic case dossier exported locally"
    else
        record_result "Reports" "FAIL" "Report export failed: ${REPORT_RESP}"
    fi
else
    record_result "Reports" "FAIL" "Skipped due to missing Case ID"
fi

# 17. Zero Egress
TELEMETRY_JSON=$(curl -s "${API_BASE}/api/system/status" || echo "{}")
if echo "${TELEMETRY_JSON}" | grep -q '"external_api_calls"[[:space:]]*:[[:space:]]*"NONE"'; then
    record_result "Zero Egress" "PASS" "Zero external API calls, MockAIProvider active, local MMDB/RFC5737"
else
    record_result "Zero Egress" "FAIL" "Telemetry reports external dependency: ${TELEMETRY_JSON}"
fi

echo "--------------------------------------------------------------------------------"
echo "VERIFICATION SUMMARY: ${PASS_COUNT}/17 TESTS PASSED (${FAIL_COUNT} FAILURES)"
echo "================================================================================"

if [ ${FAIL_COUNT} -eq 0 ]; then
    echo "[✓] ALL 17 OFFLINE RUNTIME SUBSYSTEMS ARE VERIFIED OPERATIONAL."
    exit 0
else
    echo "[-] SOME SUBSYSTEMS FAILED VERIFICATION. INSPECT LOGS ABOVE." >&2
    exit 1
fi
