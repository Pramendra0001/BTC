import { useDashboard } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Link } from 'react-router-dom';
import { 
  ArrowRightLeft, Wallet, Network, AlertCircle, 
  Database, TrendingUp, ChevronRight
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid 
} from 'recharts';
import { getPriorityColor, getStatusColor, truncateAddress, formatNumber } from '../utils/format';
import { useTheme } from '../context/ThemeContext';

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useDashboard();
  const { resolvedTheme } = useTheme();
  const isLight = resolvedTheme === 'light';

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-7 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-72 lg:col-span-2 w-full" />
          <Skeleton className="h-72 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState message="Failed to load command center intelligence data." onRetry={() => refetch()} />;
  }

  const hasData = (data?.stats?.totalTx || 0) > 0;

  // Analytical color palette for score distribution
  const distData = [
    { range: '0-20', count: data?.anomalyDistribution?.['0-20'] || 0, color: '#2B73E8' },
    { range: '20-40', count: data?.anomalyDistribution?.['20-40'] || 0, color: '#0284C7' },
    { range: '40-60', count: data?.anomalyDistribution?.['40-60'] || 0, color: '#D97706' },
    { range: '60-80', count: data?.anomalyDistribution?.['60-80'] || 0, color: '#EA580C' },
    { range: '80-100', count: data?.anomalyDistribution?.['80-100'] || 0, color: '#DC2626' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Command Center" 
        description="Operational overview: Network telemetry and blockchain transaction intelligence" 
        actions={
          <Link
            to="/datasets"
            className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded transition shadow-xs"
          >
            <Database size={13} /> Ingest Dataset
          </Link>
        }
      />

      {/* Top Analytical KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          icon={<ArrowRightLeft size={16} className="text-slate-400" />} 
          label="Total Transactions" 
          value={formatNumber(data?.stats?.totalTx)} 
          subtext={`${formatNumber(data?.stats?.totalObservations)} network events correlated`}
        />
        <StatCard 
          icon={<Wallet size={16} className="text-slate-400" />} 
          label="Active Wallets" 
          value={formatNumber(data?.stats?.activeWallets)} 
          subtext="Resolved on-chain cluster entities"
        />
        <StatCard 
          icon={<Network size={16} className="text-slate-400" />} 
          label="Monitored IPs" 
          value={formatNumber(data?.stats?.monitoredIps)} 
          subtext={`${formatNumber(data?.stats?.totalAsns)} routing ASNs mapped`}
        />
        <StatCard 
          icon={<AlertCircle size={16} className="text-rose-500" />} 
          label="Investigative Alerts" 
          value={formatNumber(data?.stats?.activeAlerts)} 
          subtext={`${data?.alerts?.critical || 0} critical priorities queued`}
        />
      </div>

      {!hasData ? (
        <EmptyState
          icon={<Database size={28} />}
          title="No Ingested Intelligence Data"
          description="Upload bulk Bitcoin transaction and network telemetry metadata (CSV, JSON, or XML) to initiate automated entity resolution, feature computation, and ML anomaly detection."
          action={
            <Link
              to="/datasets"
              className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded transition"
            >
              <Database size={14} /> Navigate to Datasets
            </Link>
          }
        />
      ) : (
        <>
          {/* Main Grid: Analytical Distribution & Priority Leads */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Chart: Anomaly Score Distribution */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                    <TrendingUp size={15} className="text-blue-500" />
                    Anomaly Score Distribution
                  </h3>
                  <span className="text-[10px] font-mono text-slate-500">
                    Model: {data?.modelInfo?.latestModel || 'Isolation Forest v2.0'}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mb-3">
                  Statistical dispersion from baseline behavioral vector [0 - 100]
                </p>
              </div>

              <div className="h-60 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={distData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" stroke={isLight ? '#D9D7D1' : '#262B30'} vertical={false} />
                    <XAxis dataKey="range" stroke={isLight ? '#7A7F84' : '#737A82'} fontSize={10} fontStyle="normal" />
                    <YAxis stroke={isLight ? '#7A7F84' : '#737A82'} fontSize={10} allowDecimals={false} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: isLight ? '#FFFFFF' : '#15191D', 
                        borderColor: isLight ? '#D9D7D1' : '#262B30', 
                        color: isLight ? '#181A1C' : '#F1F3F5',
                        borderRadius: '4px', 
                        fontSize: '11px',
                        fontFamily: 'monospace'
                      }}
                      formatter={(val: any) => [`${val} entities`, 'Count']}
                    />
                    <Bar dataKey="count" radius={[2, 2, 0, 0]}>
                      {distData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Prioritized Leads Queue */}
            <div className="bg-slate-900 border border-slate-800 rounded p-4 flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-200 flex items-center gap-2 mb-1">
                  <AlertCircle size={15} className="text-rose-500" />
                  Prioritized Leads Queue
                </h3>
                <p className="text-[11px] text-slate-400 mb-3">
                  Compound risk assessment for investigator triage
                </p>

                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 rounded bg-slate-850 border border-slate-800">
                    <span className="text-[11px] font-mono font-semibold text-rose-500">CRITICAL</span>
                    <span className="font-mono text-xs font-bold text-white">{data?.alerts?.critical || 0}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded bg-slate-850 border border-slate-800">
                    <span className="text-[11px] font-mono font-semibold text-amber-500">HIGH</span>
                    <span className="font-mono text-xs font-bold text-white">{data?.alerts?.high || 0}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded bg-slate-850 border border-slate-800">
                    <span className="text-[11px] font-mono font-semibold text-blue-400">MEDIUM</span>
                    <span className="font-mono text-xs font-bold text-white">{data?.alerts?.medium || 0}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded bg-slate-850 border border-slate-800">
                    <span className="text-[11px] font-mono font-semibold text-slate-400">LOW</span>
                    <span className="font-mono text-xs font-bold text-white">{data?.alerts?.low || 0}</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 mt-3 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>Active Cases: {data?.cases?.active || 0}</span>
                <Link to="/cases" className="text-blue-500 hover:text-blue-400 flex items-center gap-1 transition-colors">
                  Dossiers <ChevronRight size={12} />
                </Link>
              </div>
            </div>
          </div>

          {/* Recent High-Priority Leads Table */}
          <div className="bg-slate-900 border border-slate-800 rounded overflow-hidden">
            <div className="p-3.5 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-200">
                  Recent High-Priority Leads
                </h3>
                <p className="text-[11px] text-slate-400 mt-0.5">Model-generated signals requiring investigative review</p>
              </div>
              <Link to="/alerts" className="text-xs font-mono text-blue-500 hover:text-blue-400 flex items-center gap-1 transition-colors">
                All alerts <ChevronRight size={13} />
              </Link>
            </div>

            {data?.recentAlerts && data.recentAlerts.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-850 text-slate-400 border-b border-slate-800 font-mono text-[10px] uppercase tracking-wider">
                    <tr>
                      <th className="py-2.5 px-3.5">Priority</th>
                      <th className="py-2.5 px-3.5">Entity Type</th>
                      <th className="py-2.5 px-3.5">Entity Identifier</th>
                      <th className="py-2.5 px-3.5">Anomaly Score</th>
                      <th className="py-2.5 px-3.5">Status</th>
                      <th className="py-2.5 px-3.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {(data.recentAlerts || []).map((alert: any) => {
                      const pColor = getPriorityColor(alert.priority);
                      const sColor = getStatusColor(alert.status);
                      const aScore = typeof alert.anomaly_score === 'number' 
                        ? alert.anomaly_score 
                        : parseFloat(String(alert.anomaly_score || 0)) || 0;
                      const scoreBarColor = 
                        aScore >= 75 ? 'bg-rose-500' :
                        aScore >= 50 ? 'bg-amber-500' : 'bg-blue-500';

                      return (
                        <tr key={alert.id} className="hover:bg-slate-850/50 transition-colors">
                          <td className="py-2.5 px-3.5">
                            <span className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold ${pColor.bg} ${pColor.text} border ${pColor.border}`}>
                              {alert.priority}
                            </span>
                          </td>
                          <td className="py-2.5 px-3.5 font-mono text-[11px] text-slate-400">
                            {alert.entity_type}
                          </td>
                          <td className="py-2.5 px-3.5 font-mono text-[11px] text-slate-200">
                            {alert.entity_type === 'WALLET' ? truncateAddress(alert.entity_id) : alert.entity_id}
                          </td>
                          <td className="py-2.5 px-3.5">
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-slate-800 h-1.5 rounded overflow-hidden">
                                <div 
                                  className={`h-full ${scoreBarColor}`} 
                                  style={{ width: `${Math.min(aScore, 100)}%` }}
                                />
                              </div>
                              <span className="font-mono text-[11px] text-slate-300">
                                {aScore.toFixed(1)}
                              </span>
                            </div>
                          </td>
                          <td className="py-2.5 px-3.5">
                            <span className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-mono ${sColor.bg} ${sColor.text} border ${sColor.border}`}>
                              {alert.status}
                            </span>
                          </td>
                          <td className="py-2.5 px-3.5 text-right">
                            <div className="flex items-center justify-end gap-2.5">
                              <Link
                                to={`/graph?entityType=${alert.entity_type || 'WALLET'}&entityId=${encodeURIComponent(alert.entity_id || '')}`}
                                className="inline-flex items-center gap-1 text-[11px] font-mono text-cyan-400 hover:text-cyan-300 transition-colors"
                                title="Investigate in Graph"
                              >
                                <Network size={12} /> Investigate
                              </Link>
                              <Link
                                to={`/alerts/${alert.id}`}
                                className="inline-flex items-center gap-1 text-[11px] font-mono text-slate-400 hover:text-slate-200 transition-colors"
                                title="View Alert Details"
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
            ) : (
              <div className="p-8 text-center text-xs text-slate-500 font-mono">
                No alerts queued. Ingest telemetry data to run feature computation.
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
