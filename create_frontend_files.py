import os
import json
import textwrap

BASE_DIR = r"c:\Users\PRAMENDRA KUSHWAHA\Desktop\CODING\SIH 2026\BTC\frontend"

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    ensure_dir(full_path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).strip() + "\n")
    print(f"Created {rel_path}")

# 1. frontend/tailwind.config.js
write_file("tailwind.config.js", """
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
""")

# 2. frontend/vite.config.ts
write_file("vite.config.ts", """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
""")

# 3. frontend/src/main.tsx
write_file("src/main.tsx", """
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
""")

# 4. frontend/src/App.tsx
write_file("src/App.tsx", """
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AppLayout from './layouts/AppLayout'
import DashboardPage from './pages/DashboardPage'
import AlertsPage from './pages/AlertsPage'
import AlertDetailPage from './pages/AlertDetailPage'
import WalletsPage from './pages/WalletsPage'
import WalletDetailPage from './pages/WalletDetailPage'
import TransactionsPage from './pages/TransactionsPage'
import TransactionDetailPage from './pages/TransactionDetailPage'
import IPDetailPage from './pages/IPDetailPage'
import ASNDetailPage from './pages/ASNDetailPage'
import GraphPage from './pages/GraphPage'
import TimelinePage from './pages/TimelinePage'
import EvidencePage from './pages/EvidencePage'
import CasesPage from './pages/CasesPage'
import CaseDetailPage from './pages/CaseDetailPage'
import DatasetsPage from './pages/DatasetsPage'
import ModelsPage from './pages/ModelsPage'
import SystemPage from './pages/SystemPage'
import SearchResultsPage from './pages/SearchResultsPage'
import LoginPage from './pages/LoginPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="alerts/:id" element={<AlertDetailPage />} />
            <Route path="wallets" element={<WalletsPage />} />
            <Route path="wallets/:address" element={<WalletDetailPage />} />
            <Route path="transactions" element={<TransactionsPage />} />
            <Route path="transactions/:txid" element={<TransactionDetailPage />} />
            <Route path="ips/:ip" element={<IPDetailPage />} />
            <Route path="asns/:asn" element={<ASNDetailPage />} />
            <Route path="graph" element={<GraphPage />} />
            <Route path="timeline" element={<TimelinePage />} />
            <Route path="evidence" element={<EvidencePage />} />
            <Route path="cases" element={<CasesPage />} />
            <Route path="cases/:id" element={<CaseDetailPage />} />
            <Route path="datasets" element={<DatasetsPage />} />
            <Route path="models" element={<ModelsPage />} />
            <Route path="system" element={<SystemPage />} />
            <Route path="search" element={<SearchResultsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
""")

# 5. frontend/src/index.css
write_file("src/index.css", """
@import 'tailwindcss';

@theme {
  --color-slate-950: #020617;
  --color-slate-900: #0f172a;
  --color-slate-800: #1e293b;
  --color-slate-100: #f1f5f9;
  --color-slate-300: #cbd5e1;
  --color-emerald-500: #10b981;
  --color-amber-500: #f59e0b;
  --color-rose-500: #f43f5e;
  --color-blue-500: #3b82f6;
  --color-violet-500: #8b5cf6;
}

body {
  @apply bg-slate-950 text-slate-100 antialiased;
}
""")

# 6. frontend/src/api/client.ts
write_file("src/api/client.ts", """
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
""")

# 7. frontend/src/api/hooks.ts
write_file("src/api/hooks.ts", """
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from './client'

export const useDashboard = () => useQuery({ queryKey: ['dashboard'], queryFn: async () => (await apiClient.get('/api/dashboard')).data })
export const useAlerts = (params?: any) => useQuery({ queryKey: ['alerts', params], queryFn: async () => (await apiClient.get('/api/alerts', { params })).data })
export const useAlert = (id: string) => useQuery({ queryKey: ['alert', id], queryFn: async () => (await apiClient.get(`/api/alerts/${id}`)).data })
export const useWallets = (params?: any) => useQuery({ queryKey: ['wallets', params], queryFn: async () => (await apiClient.get('/api/wallets', { params })).data })
export const useWallet = (address: string) => useQuery({ queryKey: ['wallet', address], queryFn: async () => (await apiClient.get(`/api/wallets/${address}`)).data })
export const useTransactions = (params?: any) => useQuery({ queryKey: ['transactions', params], queryFn: async () => (await apiClient.get('/api/transactions', { params })).data })
export const useTransaction = (txid: string) => useQuery({ queryKey: ['transaction', txid], queryFn: async () => (await apiClient.get(`/api/transactions/${txid}`)).data })
export const useIP = (ip: string) => useQuery({ queryKey: ['ip', ip], queryFn: async () => (await apiClient.get(`/api/ips/${ip}`)).data })
export const useASN = (asn: string) => useQuery({ queryKey: ['asn', asn], queryFn: async () => (await apiClient.get(`/api/asns/${asn}`)).data })
export const useGraph = (entityType: string, entityId: string) => useQuery({ queryKey: ['graph', entityType, entityId], queryFn: async () => (await apiClient.get(`/api/graph`, { params: { entityType, entityId } })).data })
export const useTimeline = (entityType: string, entityId: string) => useQuery({ queryKey: ['timeline', entityType, entityId], queryFn: async () => (await apiClient.get(`/api/timeline`, { params: { entityType, entityId } })).data })
export const useEvidence = (id: string) => useQuery({ queryKey: ['evidence', id], queryFn: async () => (await apiClient.get(`/api/evidence/${id}`)).data })
export const useCases = (params?: any) => useQuery({ queryKey: ['cases', params], queryFn: async () => (await apiClient.get('/api/cases', { params })).data })
export const useCase = (id: string) => useQuery({ queryKey: ['case', id], queryFn: async () => (await apiClient.get(`/api/cases/${id}`)).data })
export const useModels = () => useQuery({ queryKey: ['models'], queryFn: async () => (await apiClient.get('/api/models')).data })
export const useDatasets = () => useQuery({ queryKey: ['datasets'], queryFn: async () => (await apiClient.get('/api/datasets')).data })
export const useSearch = (query: string) => useQuery({ queryKey: ['search', query], queryFn: async () => (await apiClient.get('/api/search', { params: { q: query } })).data })
export const useSystemStatus = () => useQuery({ queryKey: ['system-status'], queryFn: async () => (await apiClient.get('/api/system/status')).data })
export const useAIInterpretation = (entityType: string, entityId: string) => useQuery({ queryKey: ['ai-interpretation', entityType, entityId], queryFn: async () => (await apiClient.get('/api/ai/interpretation', { params: { entityType, entityId } })).data })

export const useUploadDataset = () => useMutation({ mutationFn: async (data: any) => (await apiClient.post('/api/datasets', data)).data })
export const useCreateCase = () => useMutation({ mutationFn: async (data: any) => (await apiClient.post('/api/cases', data)).data })
export const useUpdateCase = () => useMutation({ mutationFn: async ({ id, data }: { id: string; data: any }) => (await apiClient.put(`/api/cases/${id}`, data)).data })
export const useAddNote = () => useMutation({ mutationFn: async ({ id, data }: { id: string; data: any }) => (await apiClient.post(`/api/cases/${id}/notes`, data)).data })
export const useRunPipeline = () => useMutation({ mutationFn: async (id: string) => (await apiClient.post(`/api/datasets/${id}/process`)).data })
""")

# 8. frontend/src/types/index.ts
write_file("src/types/index.ts", """
export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface SystemStatus {
  status: 'OPERATIONAL' | 'DEGRADED' | 'ERROR' | 'UNAVAILABLE';
  services: Record<string, string>;
}
// Add other interfaces based on schemas to avoid empty typing
""")

# 9. frontend/src/utils/format.ts
write_file("src/utils/format.ts", """
export const formatBTC = (satoshis: number) => (satoshis / 100000000).toFixed(8) + ' BTC';
export const formatNumber = (n: number) => new Intl.NumberFormat().format(n);
export const formatDate = (iso: string) => new Date(iso).toLocaleDateString();
export const formatRelativeTime = (iso: string) => {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  return `${mins} mins ago`;
}
export const truncateAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;
export const getPriorityColor = (p: string) => {
  const map: Record<string, string> = { CRITICAL: 'bg-rose-500', HIGH: 'bg-amber-500', MEDIUM: 'bg-blue-500', LOW: 'bg-slate-500' };
  return map[p] || 'bg-slate-500';
}
export const getStatusColor = (s: string) => {
  const map: Record<string, string> = { NEW: 'bg-blue-500', REVIEWING: 'bg-amber-500', RESOLVED: 'bg-emerald-500', DISMISSED: 'bg-slate-500' };
  return map[s] || 'bg-slate-500';
}
export const getEntityTypeIcon = (type: string) => null;
""")

# 10. frontend/src/components/ui/Badge.tsx
write_file("src/components/ui/Badge.tsx", """
import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const Badge = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return (
    <span className={cn("px-2 py-1 rounded text-xs font-medium text-white", className)}>
      {children}
    </span>
  );
}
""")

# 11. frontend/src/components/ui/StatCard.tsx
write_file("src/components/ui/StatCard.tsx", """
import React from 'react';

export const StatCard = ({ icon, label, value, trend }: any) => {
  return (
    <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
      <div className="flex items-center space-x-2 text-slate-400 mb-2">
        {icon}
        <span className="text-sm">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
      {trend && <div className="text-xs text-emerald-500 mt-1">{trend}</div>}
    </div>
  );
}
""")

# 12. frontend/src/components/ui/Skeleton.tsx
write_file("src/components/ui/Skeleton.tsx", """
export const Skeleton = ({ className }: { className?: string }) => {
  return <div className={`animate-pulse bg-slate-800 rounded ${className}`} />;
}
""")

# 13. frontend/src/components/ui/ErrorState.tsx
write_file("src/components/ui/ErrorState.tsx", """
export const ErrorState = ({ message, onRetry }: { message: string, onRetry?: () => void }) => {
  return (
    <div className="p-4 bg-slate-900 rounded-lg border border-rose-900/50 flex flex-col items-center justify-center text-center">
      <div className="text-rose-500 mb-2 text-lg font-semibold">Error Loading Data</div>
      <div className="text-slate-400 mb-4">{message}</div>
      {onRetry && (
        <button onClick={onRetry} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded transition">
          Retry
        </button>
      )}
    </div>
  );
}
""")

# 14. frontend/src/components/ui/EmptyState.tsx
write_file("src/components/ui/EmptyState.tsx", """
export const EmptyState = ({ icon, message, action }: any) => {
  return (
    <div className="p-8 flex flex-col items-center justify-center text-center text-slate-400 border border-dashed border-slate-800 rounded-lg">
      <div className="mb-4 opacity-50">{icon}</div>
      <div className="mb-4">{message}</div>
      {action}
    </div>
  );
}
""")

# 15. frontend/src/components/ui/DataTable.tsx
write_file("src/components/ui/DataTable.tsx", """
export const DataTable = ({ columns, data }: { columns: any[], data: any[] }) => {
  return (
    <div className="overflow-x-auto w-full border border-slate-800 rounded-lg">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-900 text-slate-400">
          <tr>
            {columns.map((c, i) => (
              <th key={i} className="px-4 py-3 border-b border-slate-800">{c.header}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-900/50">
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-slate-800 transition">
              {columns.map((c, j) => (
                <td key={j} className="px-4 py-3">{c.cell ? c.cell(row) : row[c.accessorKey]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
""")

# 16. frontend/src/components/ui/Modal.tsx
write_file("src/components/ui/Modal.tsx", """
export const Modal = ({ isOpen, onClose, title, children }: any) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg shadow-xl w-full max-w-lg">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">{title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">&times;</button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
}
""")

# 17. frontend/src/components/ui/PageHeader.tsx
write_file("src/components/ui/PageHeader.tsx", """
export const PageHeader = ({ title, description, actions }: any) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        {description && <p className="text-slate-400 text-sm mt-1">{description}</p>}
      </div>
      {actions && <div className="mt-4 sm:mt-0 flex gap-2">{actions}</div>}
    </div>
  );
}
""")

# 18. frontend/src/layouts/AppLayout.tsx
write_file("src/layouts/AppLayout.tsx", """
import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, AlertCircle, Wallet, ArrowRightLeft, Network, Activity, Briefcase, Database, Cpu, Settings, Globe } from 'lucide-react';
import { cn } from '../components/ui/Badge';

const navItems = [
  { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={18} /> },
  { name: 'Alerts', path: '/alerts', icon: <AlertCircle size={18} /> },
  { name: 'Wallets', path: '/wallets', icon: <Wallet size={18} /> },
  { name: 'Transactions', path: '/transactions', icon: <ArrowRightLeft size={18} /> },
  { name: 'Graph', path: '/graph', icon: <Network size={18} /> },
  { name: 'Cases', path: '/cases', icon: <Briefcase size={18} /> },
  { name: 'Datasets', path: '/datasets', icon: <Database size={18} /> },
  { name: 'Models', path: '/models', icon: <Cpu size={18} /> },
  { name: 'System', path: '/system', icon: <Activity size={18} /> },
];

export default function AppLayout() {
  const location = useLocation();
  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col hidden md:flex">
        <div className="p-4 border-b border-slate-800">
          <div className="text-xl font-bold text-white flex items-center gap-2">
            <Globe className="text-blue-500" /> BTC-SHIELD
          </div>
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          {navItems.map((item) => (
            <Link key={item.path} to={item.path} className={cn("flex items-center gap-3 px-3 py-2 rounded-md transition", location.pathname === item.path ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white hover:bg-slate-800/50")}>
              {item.icon}
              {item.name}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">
          <div className="text-slate-400">Global Search...</div>
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 bg-slate-700 rounded-full"></div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-6 relative">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
""")

# 19. frontend/src/pages/DashboardPage.tsx
write_file("src/pages/DashboardPage.tsx", """
import { useDashboard } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { AlertCircle, Wallet, ArrowRightLeft, Network, Activity } from 'lucide-react';

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();
  
  if (isLoading) return <div className="space-y-4"><Skeleton className="h-10 w-48" /><div className="grid grid-cols-4 gap-4"><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /></div></div>;
  if (error) return <ErrorState message="Failed to load dashboard data." />;

  return (
    <div className="space-y-6">
      <PageHeader title="Command Center" description="Overview of network intelligence" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={<ArrowRightLeft />} label="Total Transactions" value={data?.stats?.totalTx || 0} />
        <StatCard icon={<Wallet />} label="Active Wallets" value={data?.stats?.activeWallets || 0} />
        <StatCard icon={<Network />} label="Monitored IPs" value={data?.stats?.monitoredIps || 0} />
        <StatCard icon={<AlertCircle />} label="Active Alerts" value={data?.stats?.activeAlerts || 0} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
           <h3 className="text-lg font-medium mb-4">Anomaly Distribution</h3>
           <div className="h-64 flex items-center justify-center text-slate-500">Chart rendering...</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
           <h3 className="text-lg font-medium mb-4">System Health</h3>
           <div className="h-64 flex items-center justify-center text-slate-500">Health indicators...</div>
        </div>
      </div>
    </div>
  );
}
""")

# Generically create pages 20-37
pages = [
    "AlertsPage", "AlertDetailPage", "WalletsPage", "WalletDetailPage",
    "TransactionsPage", "TransactionDetailPage", "IPDetailPage", "ASNDetailPage",
    "GraphPage", "TimelinePage", "EvidencePage", "CasesPage", "CaseDetailPage",
    "DatasetsPage", "ModelsPage", "SystemPage", "SearchResultsPage", "LoginPage"
]

for page in pages:
    content = f"""
import React from 'react';
import {{ PageHeader }} from '../components/ui/PageHeader';

export default function {page}() {{
  return (
    <div className="space-y-6">
      <PageHeader title="{page.replace('Page', '')}" />
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
        <p className="text-slate-400">Content for {page} will be displayed here.</p>
      </div>
    </div>
  );
}}
"""
    write_file(f"src/pages/{page}.tsx", content)

# 38. frontend/src/features/graph/GraphVisualization.tsx
write_file("src/features/graph/GraphVisualization.tsx", """
import React from 'react';
import CytoscapeComponent from 'react-cytoscapejs';

export const GraphVisualization = ({ elements }: { elements: any }) => {
  return (
    <div className="h-full w-full bg-slate-900 rounded-lg border border-slate-800">
       <CytoscapeComponent elements={elements} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
""")

# 39. frontend/src/features/timeline/TimelineView.tsx
write_file("src/features/timeline/TimelineView.tsx", """
import React from 'react';

export const TimelineView = ({ events }: { events: any[] }) => {
  return (
    <div className="space-y-4">
      {events?.map((e, i) => (
         <div key={i} className="flex gap-4">
            <div className="w-1 bg-slate-700 h-full relative" />
            <div className="bg-slate-900 p-4 rounded border border-slate-800 flex-1">{e.title}</div>
         </div>
      ))}
    </div>
  );
}
""")

# 40. frontend/src/features/evidence/EvidenceCard.tsx
write_file("src/features/evidence/EvidenceCard.tsx", """
import React from 'react';

export const EvidenceCard = ({ evidence }: { evidence: any }) => {
  return (
    <div className="bg-slate-900 p-4 rounded border border-slate-800">
      <h4 className="font-semibold">{evidence?.title || "Evidence"}</h4>
      <p className="text-sm text-slate-400">{evidence?.description || "Description"}</p>
    </div>
  );
}
""")
