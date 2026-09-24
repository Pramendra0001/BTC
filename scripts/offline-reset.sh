#!/usr/bin/env bash
# ==============================================================================
# BTC-SHIELD — Air-Gapped Offline Linux Environment Reset Script
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

DOCKER_COMPOSE_CMD=""
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo "[-] ERROR: Docker Compose not found." >&2
    exit 1
fi

PURGE_DATA=false
if [ "${1:-}" = "--purge" ] || [ "${1:-}" = "-p" ]; then
    PURGE_DATA=true
fi

echo "================================================================================"
echo "          BTC-SHIELD — OFFLINE ENVIRONMENT RESET                               "
echo "================================================================================"

if [ "${PURGE_DATA}" = "true" ]; then
    echo "[!] WARNING: Full purge requested. All local database records and trained models will be deleted."
    ${DOCKER_COMPOSE_CMD} -f docker-compose.offline.yml down -v --remove-orphans
    echo "[✓] Containers and persistent volumes purged."
else
    echo "[+] Resetting containers without purging database volumes..."
    ${DOCKER_COMPOSE_CMD} -f docker-compose.offline.yml down --remove-orphans
    echo "[✓] Containers stopped and removed. Persistent volumes preserved."
    echo "    (To purge all data volumes, re-run with: ./scripts/offline-reset.sh --purge)"
fi

echo "[+] Done."
