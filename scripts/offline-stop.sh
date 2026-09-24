#!/usr/bin/env bash
# ==============================================================================
# BTC-SHIELD — Air-Gapped Offline Linux Shutdown Script
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

echo "[+] Gracefully stopping BTC-SHIELD offline containers (preserving persistent data)..."
${DOCKER_COMPOSE_CMD} -f docker-compose.offline.yml stop

echo "[✓] All offline services stopped successfully."
echo "    Persistent volumes remain intact."
echo "    To restart: ./scripts/offline-start.sh"
