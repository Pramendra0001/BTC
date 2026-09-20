export type Priority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type AlertStatus = 'NEW' | 'REVIEWING' | 'RESOLVED' | 'DISMISSED' | 'CASE_CREATED';
export type CaseStatus = 'OPEN' | 'ACTIVE' | 'CLOSED';
export type EntityType = 'WALLET' | 'TRANSACTION' | 'IP' | 'ASN' | 'COUNTRY';

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'ADMINISTRATOR' | 'INVESTIGATOR' | 'ANALYST' | 'VIEWER';
  is_active: boolean;
  created_at: string;
}

export interface DashboardData {
  stats: {
    totalTx: number;
    activeWallets: number;
    monitoredIps: number;
    activeAlerts: number;
    totalAsns: number;
    totalObservations: number;
    openCases: number;
    totalEvidence: number;
    totalDatasets: number;
  };
  alerts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    new: number;
    reviewing: number;
    resolved: number;
  };
  cases: {
    open: number;
    active: number;
    closed: number;
  };
  anomalyDistribution: Record<string, number>;
  recentAlerts: Array<{
    id: number;
    entity_type: string;
    entity_id: string;
    priority: Priority;
    anomaly_score: number;
    status: AlertStatus;
    created_at: string;
  }>;
  processingStatus: {
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  };
  modelInfo: {
    totalRuns: number;
    latestModel?: string;
    latestTrainedAt?: string;
  };
}

export interface AlertItem {
  id: number;
  entity_type: string;
  entity_id: string;
  priority: Priority;
  anomaly_score: number;
  confidence: number;
  model_version?: string;
  contributing_signals?: Array<{
    category: string;
    observation: string;
    strength: number;
    evidence_id?: number;
  }>;
  evidence_ids?: number[];
  status: AlertStatus;
  review_state: string;
  created_at: string;
  updated_at?: string;
}

export interface WalletItem {
  address: string;
  tx_count: number;
  total_sent: number;
  total_received: number;
  first_seen?: string;
  last_seen?: string;
}

export interface WalletDetail extends WalletItem {
  net_flow: number;
  transactions: Array<{
    txid: string;
    timestamp: string;
    direction: 'SENT' | 'RECEIVED';
    total_input: number;
    total_output: number;
    fee: number;
    script_type: string;
  }>;
  network_observations: Array<{
    src_ip: string;
    dst_ip: string;
    asn: string;
    country: string;
    timestamp: string;
  }>;
  counterparties: string[];
  counterparty_count: number;
  alerts: AlertItem[];
  evidence: EvidenceItem[];
  features?: Record<string, any>;
  anomaly_score?: number;
  cluster_id?: number;
}

export interface TransactionItem {
  id: number;
  txid: string;
  timestamp: string;
  fee: number;
  script_type: string;
  total_input: number;
  total_output: number;
}

export interface TransactionDetail extends TransactionItem {
  inputs: Array<{
    wallet_address: string;
    amount: number;
    position: number;
  }>;
  outputs: Array<{
    wallet_address: string;
    amount: number;
    position: number;
  }>;
}

export interface IPEntityItem {
  ip_address: string;
  first_seen?: string;
  last_seen?: string;
  observation_count: number;
  asn?: string;
  country?: string;
  recent_observations?: Array<{
    transaction_id: string;
    dst_ip: string;
    timestamp: string;
    asn: string;
    geo_country: string;
  }>;
  related_txids?: string[];
  related_wallets?: string[];
}

export interface ASNEntityItem {
  asn_number: string;
  name: string;
  country_count: number;
  ip_count: number;
  associated_ips?: string[];
  associated_countries?: string[];
}

export interface EvidenceItem {
  id: number;
  entity_type: string;
  entity_id: string;
  category: string;
  observation: string;
  details?: Record<string, any>;
  source_dataset_id?: number;
  source_record_id?: number;
  strength: number;
  created_at?: string;
}

export interface CaseItem {
  id: number;
  title: string;
  description?: string;
  status: CaseStatus;
  priority: Priority;
  investigator?: string;
  investigator_id?: number;
  created_at: string;
  updated_at?: string;
  entity_count?: number;
  evidence_count?: number;
  note_count?: number;
}

export interface CaseDetail extends CaseItem {
  entities: Array<{
    type: string;
    id: string;
    label?: string;
    added_at?: string;
    tx_count?: number;
    country?: string;
  }>;
  evidence: Array<{
    id: number;
    category: string;
    observation: string;
    strength: number;
    entity_type: string;
    entity_id: string;
  }>;
  notes: Array<{
    id: number;
    content: string;
    author: string;
    created_at: string;
  }>;
}

export interface DatasetItem {
  id: number;
  name: string;
  filename: string;
  format?: string;
  status: string;
  total_records: number;
  valid_records: number;
  invalid_records: number;
  duplicate_records: number;
  created_at: string;
  updated_at?: string;
}

export interface ModelRunItem {
  id: number;
  model_type: string;
  model_version: string;
  status: string;
  parameters?: Record<string, any>;
  evaluation_metrics?: Record<string, any>;
  created_at: string;
}

export interface AIInterpretation {
  entity_type: string;
  entity_id: string;
  summary: string;
  observations: string[];
  contributing_signals: Array<{
    category: string;
    strength: number;
    evidence_id?: number;
  }>;
  recommended_review_actions: string[];
  uncertainty: string;
  insufficient_information: string[];
  confidence: number;
  evidence_count?: number;
  categories_analyzed?: string[];
}

export interface TimelineEvent {
  type: string;
  timestamp?: string;
  title: string;
  description: string;
  entity_type?: string;
  entity_id?: string;
  details?: Record<string, any>;
}

export interface GraphData {
  nodes: Array<{
    data: {
      id: string;
      label: string;
      type: string;
      full_id?: string;
      anomaly_score?: number;
      tx_count?: number;
      country?: string;
      asn?: string;
      is_center?: boolean;
      centrality?: Record<string, number>;
    };
  }>;
  edges: Array<{
    data: {
      id: string;
      source: string;
      target: string;
      type: string;
      amount?: number;
      tx_count?: number;
      provenance?: string;
    };
  }>;
  stats?: {
    node_count: number;
    edge_count: number;
    center_node: string;
    hops: number;
  };
}

export interface SearchResult {
  type: string;
  id: string;
  label: string;
  subtitle: string;
  url: string;
}

export interface HeuristicsSummary {
  peeling_chains_detected: number;
  total_peeled_volume_btc: number;
  max_chain_hops: number;
  mixing_transactions_detected: number;
  total_mixing_volume_btc: number;
  coinjoin_rounds_count: number;
  tumbler_transactions_count: number;
  fan_out_dispersion_count: number;
}

export interface PeelingHop {
  hop: number;
  txid: string;
  timestamp?: string;
  peeled_amount: number;
  peeled_address: string;
  change_amount: number;
  change_address: string;
  fee: number;
}

export interface PeelingChain {
  chain_id: string;
  start_txid: string;
  terminal_txid: string;
  hop_count: number;
  total_peeled_btc: number;
  initial_amount_btc: number;
  final_change_btc: number;
  unique_addresses_count: number;
  confidence_score: number;
  hops: PeelingHop[];
}

export interface MixingPattern {
  txid: string;
  timestamp?: string;
  pattern_type: string;
  confidence_score: number;
  input_count: number;
  output_count: number;
  max_equal_outputs: number;
  equal_denominations: Array<{ amount_btc: number; count: number }>;
  entropy_bits: number;
  total_volume_btc: number;
  fee_btc: number;
}

export interface DataQualitySummary {
  total_datasets: number;
  total_records: number;
  valid_records: number;
  invalid_records: number;
  duplicate_records: number;
  overall_health_score: number;
  format_breakdown: Record<string, number>;
  enrichment_coverage: {
    network_observations_total: number;
    geoip_resolution_pct: number;
    asn_resolution_pct: number;
    tx_network_correlation_pct: number;
  };
  datasets: Array<{
    id: number;
    name: string;
    format: string;
    status: string;
    total_records: number;
    valid_records: number;
    invalid_records: number;
    duplicate_records: number;
    health_score: number;
    created_at?: string;
  }>;
}

export interface RejectedRecord {
  id: number;
  dataset_id: number;
  line_number: number;
  error_message: string;
  raw_data: Record<string, any>;
  created_at?: string;
}

export interface AuditLogItem {
  id: number;
  user_id?: number;
  username: string;
  action: string;
  entity_type?: string;
  entity_id?: string;
  details: Record<string, any>;
  ip_address?: string;
  timestamp: string;
}

export interface JobItem {
  job_id: string;
  job_type: string;
  description: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  progress_pct: number;
  message: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  result?: Record<string, any>;
}
