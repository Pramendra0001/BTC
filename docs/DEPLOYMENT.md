# BTC-SHIELD — Deployment & Operational Guide

**Platform:** BTC-SHIELD (Bitcoin Transaction & Network Intelligence Platform)  
**Target:** Smart India Hackathon 2026 — Problem Statement 26146 (NTRO)  
**Supported Environments:** Air-Gapped Linux (Mode A) & Cloud Production (Mode B)  

---

## 1. Deployment Architectures

BTC-SHIELD supports dual-mode operation out of the box:

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 BTC-SHIELD DEPLOYMENT                   │
                  └────────────────────────────┬────────────────────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       │                                               │
                       ▼                                               ▼
          ┌───────────────────────────┐                   ┌───────────────────────────┐
          │   MODE A: AIR-GAPPED      │                   │   MODE B: CLOUD PROD      │
          │   (SIH Competition)       │                   │   (Enterprise / SaaS)     │
          ├───────────────────────────┤                   ├───────────────────────────┤
          │ • Offline Linux / Docker  │                   │ • GitHub Pages Frontend   │
          │ • SQLite Engine (Local)   │                   │ • HTTPS FastAPI Backend   │
          │ • Local Mock AI Engine    │                   │ • Neon PostgreSQL DB      │
          │ • 0 Network Egress Req.   │                   │ • Live CI/CD Automation   │
          └───────────────────────────┘                   └───────────────────────────┘
```

---

## 2. Mode A: Air-Gapped Linux (SIH Competition Evaluation)

Mode A is optimized for evaluations where the evaluation machine has no internet connectivity.

### Option 1: Docker Compose (One-Command Stack)
```bash
# Clone or transfer repository onto evaluation Linux host
cd BTC

# Launch complete offline stack (Backend on :8000, Frontend on :5173)
docker compose up -d

# Verify containers are running
docker compose ps
```

### Option 2: Native Linux Host Execution
#### Backend Setup:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start backend with pre-seeded SQLite database
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup:
```bash
cd frontend
npm install
npm run build
npm run preview -- --port 5173 --host
```

Access the application in your browser at `http://localhost:5173`. Default administrator credentials:
- **Username:** `admin`
- **Password:** `admin123`

---

## 3. Mode B: Cloud Production Deployment

### 3.1 Frontend on GitHub Pages
BTC-SHIELD includes an automated GitHub Actions deployment workflow (`.github/workflows/deploy-frontend.yml`).

1. **Repository Settings:**
   - Go to `Settings` -> `Pages` in the GitHub repository.
   - Set source to `GitHub Actions`.
2. **Build Configuration:**
   - Vite is configured with relative base paths (`./`) and copies `index.html` to `404.html` so client-side SPA routing works on all subpaths (`/alerts`, `/graph`, `/heuristics`).
3. Every push to `main` automatically builds and publishes the latest production UI.

### 3.2 Backend on Cloud Host (Render / Railway / AWS EC2)
Configure environment variables on your cloud provider:
```bash
DATABASE_URL=postgresql://neondb_owner:password@ep-xyz.us-east-2.aws.neon.tech/btcshield?sslmode=require
JWT_SECRET=super-secure-production-random-secret-key-min-32-chars
CORS_ORIGINS=["https://pramendra0001.github.io","http://localhost:5173"]
AI_PROVIDER=mock
LOG_LEVEL=INFO
```

---

## 4. Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `BTC-SHIELD` | Application title and API header identity |
| `API_V1_STR` | `/api` | Base API route prefix |
| `DATABASE_URL` | `sqlite:///btcshield.db` | SQLAlchemy connection string (SQLite or PostgreSQL) |
| `JWT_SECRET` | `change-this-secret-in-production` | Secret key for signing JWT authorization tokens |
| `JWT_ALGORITHM` | `HS256` | Cryptographic algorithm for JWT |
| `JWT_EXPIRATION_MINUTES`| `30` | Access token lifespan |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins for browser security |
| `AI_PROVIDER` | `mock` | AI explainability provider (`mock` or `gemini`) |
| `LOG_LEVEL` | `INFO` | Application log verbosity (`DEBUG`, `INFO`, `WARNING`) |

---

## 5. Nginx Reverse Proxy Configuration (Production)

For bare-metal Linux servers running behind Nginx:
```nginx
server {
    listen 80;
    server_name btcshield.domain.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name btcshield.domain.org;

    ssl_certificate /etc/letsencrypt/live/btcshield.domain.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/btcshield.domain.org/privkey.pem;

    # Static Frontend
    location / {
        root /var/www/btcshield/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API Reverse Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
