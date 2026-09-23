#!/bin/bash
# BTC-SHIELD Offline & Air-Gapped Environment Validation Script (Linux/macOS)
# Validates platform configuration, offline datasets, local GeoIP resolution, and compliance tests.

set -e

echo "=========================================================="
echo "       BTC-SHIELD OFFLINE & AIR-GAPPED VALIDATION         "
echo "=========================================================="

PASS_COUNT=0
FAIL_COUNT=0

test_step() {
    local step_name="$1"
    local cmd="$2"
    printf "[CHECK] %-50s ... " "$step_name"
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "\033[0;32mPASS\033[0m"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "\033[0;31mFAIL\033[0m"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# Determine Python runtime
PYTHON_CMD="python3"
if [ -f "backend/.venv/bin/python" ]; then
    PYTHON_CMD="backend/.venv/bin/python"
elif [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

PYTEST_CMD="pytest"
if [ -f "backend/.venv/bin/pytest" ]; then
    PYTEST_CMD="backend/.venv/bin/pytest"
elif [ -f ".venv/bin/pytest" ]; then
    PYTEST_CMD=".venv/bin/pytest"
fi

# 1. Python Runtime
test_step "Python Runtime Available" "$PYTHON_CMD --version"

# 2. Database Engine & ORM Models
test_step "Database Engine & ORM Models Initialization" "$PYTHON_CMD -c \"import sys; sys.path.insert(0, 'backend'); from app.core.database import engine, Base; from app.models.models import User, Transaction, Wallet, BehavioralFeature, Alert, Case; Base.metadata.create_all(bind=engine)\""

# 3. Offline GeoIP Subsystem
test_step "Offline GeoIP Resolution Engine" "$PYTHON_CMD -c \"import sys; sys.path.insert(0, 'backend'); from app.services.geoip_service import geoip_service; res = geoip_service.lookup('192.0.2.1'); assert res.get('country') is not None; assert res.get('status') == 'RESOLVED'; assert geoip_service.is_operational() is True\""

# 4. Canonical Datasets & Manifests
test_step "Canonical Forensic Datasets & Manifests" "test -f data/samples/btc_shield_100000_manifest.json"

# 5. Core Machine Learning & Algorithmic Modules
test_step "Scikit-Learn & NetworkX Algorithmic Runtime" "$PYTHON_CMD -c \"import sklearn; import networkx as nx; import numpy as np; G = nx.DiGraph(); G.add_edge('A', 'B', weight=1.0); assert nx.is_directed(G)\""

# 6. Platform Compliance Test Suite
test_step "Platform Compliance Test Suite (10 Core Requirements)" "$PYTEST_CMD tests/test_platform_compliance.py -W ignore --quiet"

echo "=========================================================="
if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "\033[0;32mValidation Summary: $PASS_COUNT Passed, $FAIL_COUNT Failed\033[0m"
    echo -e "\033[0;32mSTATUS: AIR-GAPPED & OFFLINE READY\033[0m"
    exit 0
else
    echo -e "\033[0;31mValidation Summary: $PASS_COUNT Passed, $FAIL_COUNT Failed\033[0m"
    exit 1
fi
