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
import HeuristicsPage from './pages/HeuristicsPage'
import DataQualityPage from './pages/DataQualityPage'
import AuditLogsPage from './pages/AuditLogsPage'
import SettingsPage from './pages/SettingsPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
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
            <Route path="heuristics" element={<HeuristicsPage />} />
            <Route path="data-quality" element={<DataQualityPage />} />
            <Route path="audit-logs" element={<AuditLogsPage />} />
            <Route path="models" element={<ModelsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="system" element={<SystemPage />} />
            <Route path="search" element={<SearchResultsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
