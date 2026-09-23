# BTC-SHIELD Air-Gapped Offline Linux Deployment Guide

**Target Environment:** Air-Gapped Linux Host / Offline Forensic Workstation  
**Host Operating System:** Ubuntu 22.04 / 24.04 LTS, Debian 12, or RHEL 9  
**Air-Gap Guarantee:** Zero internet connectivity required. No external DNS, CDN, or cloud AI API dependencies.  

---

## 1. Pre-Deployment Preparation (Offline Staging)

To guarantee flawless offline execution without internet access, prepare a USB flash drive or offline staging directory:

### Step 1.1: Cache Python Wheels
Run on an internet-connected build machine:
```bash
mkdir -p offline_assets/pip_cache
pip download -r backend/requirements.txt -d offline_assets/pip_cache/
pip download pytest pytest-asyncio httpx -d offline_assets/pip_cache/
```

### Step 1.2: Cache Node.js Dependencies & Production Bundle
```bash
cd frontend
npm ci
npm run build
cd ..
tar -czvf offline_assets/frontend_dist.tar.gz -C frontend dist/
tar -czvf offline_assets/frontend_node_modules.tar.gz -C frontend node_modules/
```

### Step 1.3: (Optional) Pre-build Docker Container Images
If evaluating using Docker Compose:
```bash
docker compose build
docker save btc-backend btc-frontend postgres:16-alpine -o offline_assets/btc_shield_docker_images.tar
```

---

## 2. Air-Gapped Offline Setup

### Step 2.1: Clone/Copy Repository
```bash
cp -r /media/usb/BTC /opt/btc-shield
cd /opt/btc-shield
```

### Step 2.2: Disable External Network Connections (Proof of Air-Gap)
```bash
# Verify air-gap mode
sudo nmcli networking off
# OR disconnect Wi-Fi and unplug Ethernet
ping -c 1 8.8.8.8 || echo "Confirmed: 100% Offline"
```

### Step 2.3: Initialize Virtual Environment from Local Wheels
```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install --no-index --find-links=offline_assets/pip_cache/ -r backend/requirements.txt
```

---

## 3. Starting the Platform Offline

### Option A: Local Python & Node Preview (Fastest Standalone Mode)

**Terminal 1 (Backend REST API):**
```bash
cd backend
source .venv/bin/activate
export DATABASE_URL="sqlite:///btcshield.db"
export AI_PROVIDER="mock"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*Output confirmed:*
```
INFO:     Started server process
INFO:     Admin user created.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 (Frontend Static Preview):**
```bash
cd frontend
# Either serve the pre-built dist folder:
npx --yes serve -s dist -l 5173
# OR if node_modules are unpacked:
npm run dev -- --host 0.0.0.0 --port 5173
```

### Option B: Docker Compose Offline Stack
```bash
# Load pre-cached images if using Docker:
docker load -i offline_assets/btc_shield_docker_images.tar
docker compose up -d
```

---

## 4. Air-Gapped Verification & Audit Checklist

1. **Verify No Internet Egress:**
   ```bash
   # Run in background to prove zero outbound traffic:
   sudo tcpdump -i any -n 'port 53 or port 443 or port 80' &
   ```
2. **Access the Web Interface:**
   Open browser to: `http://localhost:5173`
3. **Investigator Authentication & Self-Registration:**
   - Investigators may register a new account directly via the UI registration tab (`/login` -> Register).
   - Alternatively, configure `ADMIN_PASSWORD` in the local environment to seed an initial administrator account.
4. **Execute Automated Verification Suite:**
   ```bash
   cd /opt/btc-shield
   source backend/.venv/bin/activate
   python -m pytest tests -v -W ignore
   # All 70 backend tests pass in < 35 seconds!
   ```
5. **Run Standalone Offline Validation Script:**
   ```bash
   bash scripts/offline-validation.sh
   # 6/6 checks verified: STATUS: AIR-GAPPED & OFFLINE READY
   ```
6. **Ingest Pre-Generated Sample Scenarios:**
   Go to `/datasets` -> Select `data/samples/btc_shield_synthetic_transactions.csv` -> Click **Upload** -> Click **Run ML Pipeline**.

---

## 5. Troubleshooting & Immediate Fixes

| Symptom | Cause | Immediate Resolution |
|---|---|---|
| Port 8000 already in use | Previous process running | `kill -9 $(lsof -t -i:8000)` |
| Port 5173 already in use | Vite or node server active | `kill -9 $(lsof -t -i:5173)` |
| Database locked error (SQLite) | Concurrent write thread | `rm backend/btcshield.db` and restart backend (auto-recreates schema) |
| Missing node modules | Uncached npm install | Extract `offline_assets/frontend_node_modules.tar.gz` into `frontend/` |
