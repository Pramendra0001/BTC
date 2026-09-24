import { useState } from 'react';
import { useAlerts } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Link } from 'react-router-dom';
import { AlertCircle, Filter, ChevronRight, ShieldAlert, Search, ExternalLink, Network } from 'lucide-react';
import { getPriorityColor, getStatusColor, truncateAddress, formatDate } from '../utils/format';

export default function AlertsPage() {
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [page, setPage] = useState<number>(0);
  const pageSize = 25;

  const queryParams = {
    priority: priorityFilter === 'ALL' ? undefined : priorityFilter,
    status: statusFilter === 'ALL' ? undefined : statusFilter,
    skip: page * pageSize,
    limit: pageSize,
  };

  const { data, isLoading, error, refetch } = useAlerts(queryParams);

  const alerts = data?.alerts || [];
  const total = data?.total || 0;

  // Filter client-side for immediate search term match
  const filteredAlerts = alerts.filter((a: any) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      a.entity_id.toLowerCase().includes(term) ||
      a.entity_type.toLowerCase().includes(term) ||
      a.priority.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Alert Prioritizer" 
        description="Ranked investigative leads derived from Isolation Forest anomaly detection and behavioral signals" 
      />

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by entity or ID..."
            className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500/50"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Priority Pills */}
          <div className="flex items-center rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs">
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((p) => (
              <button
                key={p}
                onClick={() => {
                  setPriorityFilter(p);
                  setPage(0);
                }}
                className={`px-2.5 py-1 rounded text-[11px] font-medium transition ${
                  priorityFilter === p
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {p}
              </button>
            ))}
          </div>

          {/* Status Select */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(0);
            }}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="REVIEWING">Reviewing</option>
            <option value="CASE_CREATED">Case Created</option>
            <option value="RESOLVED">Resolved</option>
            <option value="DISMISSED">Dismissed</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Failed to load investigative alerts." onRetry={() => refetch()} />
      ) : filteredAlerts.length === 0 ? (
        <EmptyState
          icon={<AlertCircle size={32} />}
          title="No Alerts Found"
          description={
            total === 0
              ? "No alerts have been generated yet. Please ensure a dataset is ingested and the intelligence pipeline is executed."
              : "No alerts match your current filter criteria."
          }
          action={
            total === 0 ? (
              <Link
                to="/datasets"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition"
              >
                Go to Datasets
              </Link>
            ) : undefined
          }
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase">
                <tr>
                  <th className="py-3 px-4">Priority</th>
                  <th className="py-3 px-4">Entity</th>
                  <th className="py-3 px-4">Identifier</th>
                  <th className="py-3 px-4">Anomaly Score</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Signals</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Generated</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredAlerts.map((alert: any) => {
                  const pColor = getPriorityColor(alert.priority);
                  const sColor = getStatusColor(alert.status);
                  const entityUrl = alert.entity_type === 'WALLET'
                    ? `/wallets/${alert.entity_id}`
                    : alert.entity_type === 'IP'
                    ? `/ips/${alert.entity_id}`
                    : `/transactions/${alert.entity_id}`;
                  const aScore = typeof alert.anomaly_score === 'number'
                    ? alert.anomaly_score
                    : parseFloat(String(alert.anomaly_score || 0)) || 0;

                  return (
                    <tr key={alert.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${pColor.bg} ${pColor.text} border ${pColor.border}`}>
                          {alert.priority}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {alert.entity_type}
                      </td>
                      <td className="py-3 px-4">
                        <Link 
                          to={entityUrl}
                          className="font-mono text-blue-400 hover:underline flex items-center gap-1"
                        >
                          {alert.entity_type === 'WALLET' ? truncateAddress(alert.entity_id) : alert.entity_id}
                          <ExternalLink size={10} className="text-slate-400" />
                        </Link>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${
                                aScore >= 80 ? 'bg-rose-500' : 
                                aScore >= 60 ? 'bg-amber-500' : 'bg-blue-500'
                              }`} 
                              style={{ width: `${Math.min(aScore, 100)}%` }}
                            />
                          </div>
                          <span className="font-mono text-[11px] text-slate-200">
                            {aScore.toFixed(1)}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {Math.round((Number(alert.confidence) || 0) * 100)}%
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 text-[10px] font-mono">
                          {Array.isArray(alert.contributing_signals)
                            ? alert.contributing_signals.length
                            : alert.contributing_signals && typeof alert.contributing_signals === 'object'
                            ? Object.keys(alert.contributing_signals).length
                            : Array.isArray(alert.evidence_ids)
                            ? alert.evidence_ids.length
                            : 0} signals
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${sColor.bg} ${sColor.text} border ${sColor.border}`}>
                          {alert.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                        {formatDate(alert.created_at)}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/graph?entityType=${alert.entity_type || 'WALLET'}&entityId=${encodeURIComponent(alert.entity_id || '')}`}
                            className="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 text-xs font-mono border border-slate-750 transition"
                            title="Investigate in Graph"
                          >
                            <Network size={12} className="text-cyan-400" /> Graph
                          </Link>
                          <Link
                            to={`/alerts/${alert.id}`}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-xs font-medium border border-blue-500/20 transition"
                          >
                            Details <ChevronRight size={12} />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-3 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between text-xs text-slate-400">
            <div>
              Showing {filteredAlerts.length} of {total} alerts
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="px-2.5 py-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 text-slate-200 text-xs"
              >
                Previous
              </button>
              <span className="font-mono text-xs">
                Page {page + 1} of {Math.max(1, Math.ceil(total / pageSize))}
              </span>
              <button
                disabled={(page + 1) * pageSize >= total}
                onClick={() => setPage((p) => p + 1)}
                className="px-2.5 py-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 text-slate-200 text-xs"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
