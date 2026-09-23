# BTC-SHIELD Offline & Air-Gapped Environment Validation Script
# Validates platform configuration, offline datasets, local GeoIP resolution, and compliance tests.

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       BTC-SHIELD OFFLINE & AIR-GAPPED VALIDATION         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$passCount = 0
$failCount = 0

function Test-Step($stepName, $scriptBlock) {
    Write-Host -NoNewline "[CHECK] $stepName ... "
    try {
        & $scriptBlock
        Write-Host "PASS" -ForegroundColor Green
        $global:passCount++
    }
    catch {
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host "       Error: $_" -ForegroundColor Yellow
        $global:failCount++
    }
}

# Determine Python command
$pythonCmd = "python"
if (Test-Path "backend\.venv\Scripts\python.exe") {
    $pythonCmd = "backend\.venv\Scripts\python.exe"
} elseif (Test-Path ".venv\Scripts\python.exe") {
    $pythonCmd = ".venv\Scripts\python.exe"
}

$pytestCmd = "pytest"
if (Test-Path "backend\.venv\Scripts\pytest.exe") {
    $pytestCmd = "backend\.venv\Scripts\pytest.exe"
} elseif (Test-Path ".venv\Scripts\pytest.exe") {
    $pytestCmd = ".venv\Scripts\pytest.exe"
}

# 1. Python Runtime
Test-Step "Python Runtime Available" {
    $ver = & $pythonCmd --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Python not found" }
}

# 2. Local Database & Models
Test-Step "Database Engine & ORM Models Initialization" {
    $code = @"
import sys; sys.path.insert(0, 'backend')
from app.core.database import engine, Base
from app.models.models import User, Transaction, Wallet, BehavioralFeature, Alert, Case
Base.metadata.create_all(bind=engine)
"@
    & $pythonCmd -c $code
    if ($LASTEXITCODE -ne 0) { throw "Database or Model initialization failed" }
}

# 3. Offline GeoIP Subsystem
Test-Step "Offline GeoIP Resolution Engine" {
    $code = @"
import sys; sys.path.insert(0, 'backend')
from app.services.geoip_service import geoip_service
res = geoip_service.lookup('192.0.2.1')
assert res.get('status') == 'RESOLVED', 'Expected RESOLVED status'
assert res.get('country') is not None, 'Missing country fallback'
assert geoip_service.is_operational() is True, 'GeoIP service reported not operational'
"@
    & $pythonCmd -c $code
    if ($LASTEXITCODE -ne 0) { throw "Offline GeoIP validation failed" }
}

# 4. Canonical Datasets & Manifests
Test-Step "Canonical Forensic Datasets & Manifests" {
    if (-not (Test-Path "data\samples\btc_shield_100000_manifest.json")) {
        throw "Missing 100,000 transaction manifest file"
    }
}

# 5. Core Machine Learning & Algorithmic Modules
Test-Step "Scikit-Learn & NetworkX Algorithmic Runtime" {
    $code = @"
import sklearn
import networkx as nx
import numpy as np
G = nx.DiGraph()
G.add_edge('A', 'B', weight=1.0)
assert nx.is_directed(G)
"@
    & $pythonCmd -c $code
    if ($LASTEXITCODE -ne 0) { throw "ML/Graph library check failed" }
}

# 6. Platform Compliance Test Suite
Test-Step "Platform Compliance Test Suite (12 Core Requirements)" {
    $out = & $pytestCmd tests/test_platform_compliance.py -W ignore --quiet 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "One or more platform compliance tests failed: `n$out"
    }
}

$summaryColor = "Green"
if ($failCount -gt 0) {
    $summaryColor = "Red"
}
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Validation Summary: $passCount Passed, $failCount Failed" -ForegroundColor $summaryColor
Write-Host "==========================================================" -ForegroundColor Cyan

if ($failCount -gt 0) {
    exit 1
} else {
    Write-Host "STATUS: AIR-GAPPED & OFFLINE READY" -ForegroundColor Green
    exit 0
}
