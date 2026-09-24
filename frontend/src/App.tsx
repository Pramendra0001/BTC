import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AppLayout from './layouts/AppLayout'
import { ThemeProvider } from './context/ThemeContext'

// Code-split dynamic page imports for progressive fast loading
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const AlertsPage = lazy(() => import('./pages/AlertsPage'))
const AlertDetailPage = lazy(() => import('./pages/AlertDetailPage'))
const WalletsPage = lazy(() => import('./pages/WalletsPage'))
const WalletDetailPage = lazy(() => import('./pages/WalletDetailPage'))
const TransactionsPage = lazy(() => import('./pages/TransactionsPage'))
const TransactionDetailPage = lazy(() => import('./pages/TransactionDetailPage'))
const IPDetailPage = lazy(() => import('./pages/IPDetailPage'))
const ASNDetailPage = lazy(() => import('./pages/ASNDetailPage'))
const GraphPage = lazy(() => import('./pages/GraphPage'))
const TimelinePage = lazy(() => import('./pages/TimelinePage'))
const EvidencePage = lazy(() => import('./pages/EvidencePage'))
const CasesPage = lazy(() => import('./pages/CasesPage'))
const CaseDetailPage = lazy(() => import('./pages/CaseDetailPage'))
const DatasetsPage = lazy(() => import('./pages/DatasetsPage'))
const ModelsPage = lazy(() => import('./pages/ModelsPage'))
const SystemPage = lazy(() => import('./pages/SystemPage'))
const SearchResultsPage = lazy(() => import('./pages/SearchResultsPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const HeuristicsPage = lazy(() => import('./pages/HeuristicsPage'))
const DataQualityPage = lazy(() => import('./pages/DataQualityPage'))
const AuditLogsPage = lazy(() => import('./pages/AuditLogsPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const TermsPage = lazy(() => import('./pages/TermsPage'))
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // Prevent avalanche of refetches on tab focus
      staleTime: 30 * 1000,        // 30 seconds fresh cache to avoid repeated requests
      gcTime: 5 * 60 * 1000,       // 5 minutes garbage collection
      retry: (failureCount, error: any) => {
        // Do not retry 4xx client errors (401, 403, 404, 422)
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false
        }
        // At most 1 retry for transient network issues to avoid hanging
        return failureCount < 1
      },
    },
  },
})

function App() {
  return (
    <ThemeProvider>
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
              <Route path="investigate" element={<Navigate to="/graph" replace />} />
              <Route path="investigations" element={<Navigate to="/cases" replace />} />
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
              <Route path="terms" element={<TermsPage />} />
              <Route path="privacy" element={<PrivacyPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  )
}

export default App
