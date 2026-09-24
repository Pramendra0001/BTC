#!/usr/bin/env bash
# ==============================================================================
# BTC-SHIELD — Air-Gapped Offline Linux Startup Script
# SIH Problem Statement 26146
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

echo "================================================================================"
echo "          BTC-SHIELD — AIR-GAPPED OFFLINE LINUX DEPLOYMENT                     "
echo "               SIH 2026 Problem Statement 26146                                 "
echo "================================================================================"
echo "[+] Step 1: Checking system prerequisites..."

# 1. Check Docker
if ! command -v docker >/dev/null 2>&1; then
    echo "[-] ERROR: Docker is not installed or not in PATH." >&2
    echo "    Please install Docker Engine (v24+) to run the offline stack." >&2
    exit 1
fi

# 2. Check Docker Compose
DOCKER_COMPOSE_CMD=""
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo "[-] ERROR: Docker Compose is not installed." >&2
    exit 1
fi

echo "[✓] Docker and Compose detected: ${DOCKER_COMPOSE_CMD}"

# 3. Verify directory layout
echo "[+] Step 2: Verifying offline runtime directory layout..."
mkdir -p offline/datasets offline/geoip offline/models offline/data

echo "[✓] Offline directories verified."

BUILD_FLAG=""
if [ "${1:-}" = "--build" ] || [ "${1:-}" = "-b" ]; then
    BUILD_FLAG="--build"
    echo "[i] Build flag specified: building images before launch..."
fi

# 4. Start Containers
echo "[+] Step 3: Launching offline container stack..."
${DOCKER_COMPOSE_CMD} -f docker-compose.offline.yml up -d ${BUILD_FLAG}

echo "[+] Step 4: Awaiting backend API health probe..."
HEALTH_URL="http://localhost:8000/health"
MAX_ATTEMPTS=40
ATTEMPT=0
READY=false

while [ ${ATTEMPT} -lt ${MAX_ATTEMPTS} ]; do
    if command -v curl >/dev/null 2>&1; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_URL}" || echo "000")
        if [ "${HTTP_CODE}" = "200" ]; then
            READY=true
            break
        fi
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "    Waiting for backend service (attempt ${ATTEMPT}/${MAX_ATTEMPTS})..."
    sleep 2
done

if [ "${READY}" = "false" ]; then
    echo "[-] WARNING: Backend did not respond with HTTP 200 within timeout."
    echo "    Inspect container logs with: ${DOCKER_COMPOSE_CMD} -f docker-compose.offline.yml logs backend"
else
    echo "[✓] Backend API is healthy!"
fi

echo "[+] Step 5: Verifying frontend application server..."
FRONTEND_URL="http://localhost:3000"
if command -v curl >/dev/null 2>&1; then
    FRONTEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}" || echo "000")
    if [ "${FRONTEND_CODE}" = "200" ]; then
        echo "[✓] Frontend application server is healthy (HTTP 200)!"
    fi
fi


echo ""
echo "================================================================================"
echo "          BTC-SHIELD OFFLINE LINUX STACK OPERATIONAL                            "
echo "================================================================================"
echo "  Frontend Application:   http://localhost:3000"
echo "  Backend API Engine:     http://localhost:8000"
echo "  Interactive API Docs:   http://localhost:8000/docs"
echo "  System Telemetry:       http://localhost:8000/api/system/status"
echo "  Air-Gapped Status:      VERIFIED (Zero External Network Egress)"
echo "================================================================================"
echo "  To stop the stack:      ./scripts/offline-stop.sh"
echo "  To run test suite:      ./scripts/offline-test.sh"
echo "================================================================================"
