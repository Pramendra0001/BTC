# BTC-SHIELD Frontend — Tactical Command Center & Forensic UI

The frontend for **BTC-SHIELD** is an enterprise-grade Single Page Application (SPA) designed for rapid tactical situational awareness, interactive graph link analysis, and explainable forensic case reporting.

---

## Architecture & Technology Stack
- **Framework:** React 19 with TypeScript 5
- **Build Tool:** Vite 8 (`@vitejs/plugin-react`)
- **Styling:** Tailwind CSS v4
- **Icons:** Lucide React
- **Data Visualization:** Recharts 3 (Anomaly distribution histograms and KPI sparklines)
- **Link Analysis Graph:** Cytoscape.js 3 (`cytoscape-dagre`, `cytoscape-concentric`)
- **Server State & Caching:** TanStack React Query v5 (progressive data streaming, non-blocking rendering)
- **Routing & Code-Splitting:** React Router v7 with route-level `React.lazy` code splitting

---

## Performance Optimizations
- **Aggressive Code-Splitting:** All secondary routes (`/graph`, `/heuristics`, `/wallets`, `/timeline`, `/evidence`, `/cases`, `/datasets`, etc.) are lazily loaded.
- **Entry Bundle Size:** Reduced from $1.5\text{ MB}$ to **$24.25\text{ kB}$** ($7.62\text{ kB}$ gzipped).
- **Time to Interactive (TTI):** Initial application shell renders in $< 1\text{ second}$.
- **Progressive API Hydration:** Skeletons appear immediately while critical KPIs and leads stream asynchronously without locking the UI.

---

## Automated Verification Suite
Run unit tests with:
```bash
npm test
```

### Verified Test Results
- **Engine:** Node.js native test runner (`node --test tests/**/*.test.ts`)
- **Test Modules:**
  - `tests/auth.test.ts` (4 tests: token storage, invalid login rejection, registration lifecycle, 409 conflict handling)
  - `tests/theme.test.ts` (4 tests: command center dark mode default, light toggle, system preference detection, persistence)
- **Result:** **8 passed, 0 skipped, 0 failed** in $\approx 159\text{ms}$.

---

## Production Build
```bash
npm run build
```
Builds cleanly with zero TypeScript errors in $\approx 800\text{ms}$, ready for deployment to GitHub Pages or offline Docker Nginx static hosting.
