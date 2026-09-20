import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './client'

// Dashboard & System
export const useDashboard = () => 
  useQuery({ 
    queryKey: ['dashboard'], 
    queryFn: async () => (await apiClient.get('/api/dashboard/')).data 
  })

export const useSystemStatus = () => 
  useQuery({ 
    queryKey: ['system-status'], 
    queryFn: async () => (await apiClient.get('/api/system/status')).data 
  })

// Alerts
export const useAlerts = (params?: { priority?: string; status?: string; skip?: number; limit?: number }) => 
  useQuery({ 
    queryKey: ['alerts', params], 
    queryFn: async () => (await apiClient.get('/api/alerts/', { params })).data 
  })

export const useAlert = (id: string | number) => 
  useQuery({ 
    queryKey: ['alert', id], 
    queryFn: async () => (await apiClient.get(`/api/alerts/${id}`)).data,
    enabled: !!id
  })

export const useAlertExplain = (id: string | number) =>
  useQuery({
    queryKey: ['alert-explain', id],
    queryFn: async () => (await apiClient.get(`/api/alerts/${id}/explain`)).data,
    enabled: !!id
  })

// Wallets
export const useWallets = (params?: { skip?: number; limit?: number }) => 
  useQuery({ 
    queryKey: ['wallets', params], 
    queryFn: async () => (await apiClient.get('/api/wallets/', { params })).data 
  })

export const useWallet = (address: string) => 
  useQuery({ 
    queryKey: ['wallet', address], 
    queryFn: async () => (await apiClient.get(`/api/wallets/${address}`)).data,
    enabled: !!address
  })

// Transactions
export const useTransactions = (params?: { skip?: number; limit?: number }) => 
  useQuery({ 
    queryKey: ['transactions', params], 
    queryFn: async () => (await apiClient.get('/api/transactions/', { params })).data 
  })

export const useTransaction = (txid: string) => 
  useQuery({ 
    queryKey: ['transaction', txid], 
    queryFn: async () => (await apiClient.get(`/api/transactions/${txid}`)).data,
    enabled: !!txid
  })

// Network (IP & ASN)
export const useIPs = (params?: { skip?: number; limit?: number }) =>
  useQuery({
    queryKey: ['ips', params],
    queryFn: async () => (await apiClient.get('/api/ips', { params })).data
  })

export const useIP = (ip: string) => 
  useQuery({ 
    queryKey: ['ip', ip], 
    queryFn: async () => (await apiClient.get(`/api/ips/${ip}`)).data,
    enabled: !!ip
  })

export const useASNs = (params?: { skip?: number; limit?: number }) =>
  useQuery({
    queryKey: ['asns', params],
    queryFn: async () => (await apiClient.get('/api/asns', { params })).data
  })

export const useASN = (asn: string) => 
  useQuery({ 
    queryKey: ['asn', asn], 
    queryFn: async () => (await apiClient.get(`/api/asns/${asn}`)).data,
    enabled: !!asn
  })

// Graph & Timeline
export const useGraph = (entityType: string, entityId: string, hops: number = 1) => 
  useQuery({ 
    queryKey: ['graph', entityType, entityId, hops], 
    queryFn: async () => (await apiClient.get(`/api/graph/${entityType}/${entityId}`, { params: { hops } })).data,
    enabled: !!entityType && !!entityId
  })

export const useTimeline = (entityType: string, entityId: string) => 
  useQuery({ 
    queryKey: ['timeline', entityType, entityId], 
    queryFn: async () => (await apiClient.get(`/api/timeline/${entityType}/${entityId}`)).data,
    enabled: !!entityType && !!entityId
  })

// Evidence
export const useEvidenceList = (params?: { entity_type?: string; entity_id?: string; category?: string }) => 
  useQuery({ 
    queryKey: ['evidence-list', params], 
    queryFn: async () => (await apiClient.get('/api/evidence/', { params })).data 
  });

export const useEvidence = (id: string | number) => 
  useQuery({ 
    queryKey: ['evidence', id], 
    queryFn: async () => (await apiClient.get(`/api/evidence/${id}`)).data,
    enabled: !!id
  })

// Cases
export const useCases = (params?: { status?: string; skip?: number; limit?: number }) => 
  useQuery({ 
    queryKey: ['cases', params], 
    queryFn: async () => (await apiClient.get('/api/cases/', { params })).data 
  })

export const useCase = (id: string | number) => 
  useQuery({ 
    queryKey: ['case', id], 
    queryFn: async () => (await apiClient.get(`/api/cases/${id}`)).data,
    enabled: !!id
  })

export const useCaseReport = (id: string | number) =>
  useQuery({
    queryKey: ['case-report', id],
    queryFn: async () => (await apiClient.get(`/api/cases/${id}/report`)).data,
    enabled: !!id
  })

// Models & Datasets
export const useModels = () => 
  useQuery({ 
    queryKey: ['models'], 
    queryFn: async () => (await apiClient.get('/api/models/')).data 
  })

export const useDatasets = () => 
  useQuery({ 
    queryKey: ['datasets'], 
    queryFn: async () => (await apiClient.get('/api/datasets/')).data 
  })

export const useDataset = (id: string | number) =>
  useQuery({
    queryKey: ['dataset', id],
    queryFn: async () => (await apiClient.get(`/api/datasets/${id}`)).data,
    enabled: !!id
  })

// Search
export const useSearch = (query: string) => 
  useQuery({ 
    queryKey: ['search', query], 
    queryFn: async () => (await apiClient.get('/api/search/', { params: { q: query } })).data,
    enabled: query.length >= 2
  })

// AI Interpretation
export const useAIInterpretation = (entityType: string, entityId: string) => 
  useQuery({ 
    queryKey: ['ai-interpretation', entityType, entityId], 
    queryFn: async () => (await apiClient.get(`/api/ai/interpret/${entityType}/${entityId}`)).data,
    enabled: !!entityType && !!entityId
  })

// Mutations
export const useUploadDataset = () => {
  const queryClient = useQueryClient()
  return useMutation({ 
    mutationFn: async (formData: FormData) => {
      return (await apiClient.post('/api/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })).data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    }
  })
}

export const useCreateCase = () => {
  const queryClient = useQueryClient()
  return useMutation({ 
    mutationFn: async (data: { title: string; description?: string; priority?: string; alert_id?: number }) => 
      (await apiClient.post('/api/cases/', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] })
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    }
  })
}

export const useUpdateCase = () => {
  const queryClient = useQueryClient()
  return useMutation({ 
    mutationFn: async ({ id, data }: { id: string | number; data: any }) => 
      (await apiClient.patch(`/api/cases/${id}`, data)).data,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['case', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['cases'] })
    }
  })
}

export const useAddNote = () => {
  const queryClient = useQueryClient()
  return useMutation({ 
    mutationFn: async ({ id, content }: { id: string | number; content: string }) => 
      (await apiClient.post(`/api/cases/${id}/notes`, { content })).data,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['case', variables.id] })
    }
  })
}

export const useRunPipeline = () => {
  const queryClient = useQueryClient()
  return useMutation({ 
    mutationFn: async (id: string | number) => 
      (await apiClient.post(`/api/datasets/${id}/process`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['wallets'] })
      queryClient.invalidateQueries({ queryKey: ['models'] })
    }
  })
}

// Heuristics & Structural Patterns
export const useHeuristicsSummary = () =>
  useQuery({
    queryKey: ['heuristics-summary'],
    queryFn: async () => (await apiClient.get('/api/heuristics/summary')).data
  })

export const usePeelingChains = (params?: { min_hops?: number; limit?: number }) =>
  useQuery({
    queryKey: ['peeling-chains', params],
    queryFn: async () => (await apiClient.get('/api/heuristics/peeling-chains', { params })).data
  })

export const useMixingPatterns = (params?: { limit?: number }) =>
  useQuery({
    queryKey: ['mixing-patterns', params],
    queryFn: async () => (await apiClient.get('/api/heuristics/mixing-patterns', { params })).data
  })

export const useTransactionHeuristics = (txid: string) =>
  useQuery({
    queryKey: ['transaction-heuristics', txid],
    queryFn: async () => (await apiClient.get(`/api/heuristics/transaction/${txid}`)).data,
    enabled: !!txid
  })

// Data Quality Subsystem
export const useDataQualitySummary = () =>
  useQuery({
    queryKey: ['data-quality-summary'],
    queryFn: async () => (await apiClient.get('/api/data-quality/summary')).data
  })

export const useRejectedRecords = (params?: { dataset_id?: number; limit?: number; offset?: number }) =>
  useQuery({
    queryKey: ['rejected-records', params],
    queryFn: async () => (await apiClient.get('/api/data-quality/rejected-records', { params })).data
  })

// Audit Trail
export const useAuditLogs = (params?: { action?: string; user_id?: number; entity_type?: string; limit?: number; offset?: number }) =>
  useQuery({
    queryKey: ['audit-logs', params],
    queryFn: async () => (await apiClient.get('/api/audit-logs', { params })).data
  })

// Users & RBAC
export const useUsers = () =>
  useQuery({
    queryKey: ['users'],
    queryFn: async () => (await apiClient.get('/api/users')).data
  })

export const useUpdateUser = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ userId, data }: { userId: number; data: { role?: string; is_active?: boolean } }) =>
      (await apiClient.patch(`/api/users/${userId}`, data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })
}

// Jobs / Asynchronous Pipeline Tasks
export const useJobs = (params?: { limit?: number }) =>
  useQuery({
    queryKey: ['jobs', params],
    queryFn: async () => (await apiClient.get('/api/jobs', { params })).data,
    refetchInterval: 5000 // Poll active jobs every 5 seconds
  })

export const useJob = (jobId: string) =>
  useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => (await apiClient.get(`/api/jobs/${jobId}`)).data,
    enabled: !!jobId
  })
