import { useDashboard } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Link } from 'react-router-dom';
import { 
  ArrowRightLeft, Wallet, Network, AlertCircle, Briefcase, 
  Database, ShieldCheck, TrendingUp, ChevronRight, Activity, Clock
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid 
} from 'recharts';
import { getPriorityColor, getStatusColor, truncateAddress, formatNumber, formatDate } from '../utils/format';
import { useTheme } from '../context/ThemeContext';

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useDashboard();
  const { resolvedTheme } = useTheme();
  const isLight = resolvedTheme === 'light';

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-80 lg:col-span-2 w-full" />
          <Skeleton className="h-80 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState message="Failed to load command center intelligence data." onRetry={() => refetch()} />;
  }

  const hasData = (data?.stats?.totalTx || 0) > 0;

  // Prepare anomaly distribution chart data
  const distData = [
    { range: '0-20', count: data?.anomalyDistribution?.['0-20'] || 0, color: '#3b82f6' },
    { range: '20-40', count: data?.anomalyDistribution?.['20-40'] || 0, color: '#06b6d4' },
    { range: '40-60', count: data?.anomalyDistribution?.['40-60'] || 0, color: '#eab308' },
    { range: '60-80', count: data?.anomalyDistribution?.['60-80'] || 0, color: '#f97316' },
    { range: '80-100', count: data?.anomalyDistribution?.['80-100'] || 0, color: '#ef4444' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Command Center" 
        description="Real-time network telemetry and blockchain transaction intelligence" 
        actions={
          <Link
            to="/datasets"
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition"
          >
            <Database size={14} /> Ingest Dataset
          </Link>
        }
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          icon={<ArrowRightLeft className="text-blue-400" />} 
          label="Total Transactions" 
          value={formatNumber(data?.stats?.totalTx)} 
          subtext={`${formatNumber(data?.stats?.totalObservations)} network events`}
        />
        <StatCard 
          icon={<Wallet className="text-purple-400" />} 
          label="Active Wallets" 
          value={formatNumber(data?.stats?.activeWallets)} 
          subtext="Resolved on-chain actors"
        />
        <StatCard 
          icon={<Network className="text-emerald-400" />} 
          label="Monitored IPs" 
          value={formatNumber(data?.stats?.monitoredIps)} 
          subtext={`${formatNumber(data?.stats?.totalAsns)} distinct ASNs`}
        />
        <StatCard 
          icon={<AlertCircle className="text-rose-400" />} 
          label="Investigative Alerts" 
          value={formatNumber(data?.stats?.activeAlerts)} 
          subtext={`${data?.alerts?.critical || 0} critical priorities`}
        />
      </div>

      {!hasData ? (
        <EmptyState
          icon={<Database size={32} />}
          title="No Intelligence Data Ingested"
          description="Upload bulk Bitcoin transaction and network telemetry metadata (CSV, JSON, or XML) to initiate automated entity resolution, feature computation, and ML anomaly detection."
          action={
            <Link
              to="/datasets"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition"
            >
              <Database size={16} /> Go to Datasets
            </Link>
          }
        />
      ) : (
        <>
          {/* Main Grid: Anomaly Distribution & Priority Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chart: Anomaly Score Distribution */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <TrendingUp size={16} className="text-blue-400" />
                    Anomaly Score Distribution
                  </h3>
                  <span className="text-[11px] font-mono text-slate-400">
                    Model: {data?.modelInfo?.latestModel || 'Isolation Forest v2.0'}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-4">
                  Mathematical distance from baseline behavior normalized to [0 - 100]
                </p>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={distData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} vertical={false} />
                    <XAxis dataKey="range" stroke={isLight ? '#64748b' : '#94a3b8'} fontSize={11} />
                    <YAxis stroke={isLight ? '#64748b' : '#94a3b8'} fontSize={11} allowDecimals={false} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: isLight ? '#ffffff' : '#0f172a', 
                        borderColor: isLight ? '#cbd5e1' : '#334155', 
                        color: isLight ? '#0f172a' : '#f8fafc',
                        borderRadius: '8px', 
                        fontSize: '12px',
                        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
                      }}
                      formatter={(val: any) => [`${val} entities`, 'Entities']}
                    />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {distData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Priority & Status Breakdown */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-1">
                  <AlertCircle size={16} className="text-rose-400" />
                  Prioritized Leads
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  Compound risk assessment for investigator queue
                </p>

                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20">
                    <span className="text-xs font-semibold text-rose-400">CRITICAL</span>
                    <span className="font-mono text-sm font-bold text-white">{data?.alerts?.critical || 0}</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <span className="text-xs font-semibold text-amber-400">HIGH</span>
                    <span className="font-mono text-sm font-bold text-white">{data?.alerts?.high || 0}</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-blue-500/10 border border-blue-500/20">
                    <span className="text-xs font-semibold text-blue-400">MEDIUM</span>
                    <span className="font-mono text-sm font-bold text-white">{data?.alerts?.medium || 0}</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-500/10 border border-slate-500/20">
                    <span className="text-xs font-semibold text-slate-400">LOW</span>
                    <span className="font-mono text-sm font-bold text-white">{data?.alerts?.low || 0}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-800/80 mt-4 flex items-center justify-between text-xs text-slate-400">
                <span>Active Cases: {data?.cases?.active || 0}</span>
                <Link to="/cases" className="text-blue-400 hover:underline flex items-center gap-1">
                  View Cases <ChevronRight size={12} />
                </Link>
              </div>
            </div>
          </div>

          {/* Recent High-Priority Leads Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-white">Recent High-Priority Leads</h3>
                <p className="text-xs text-slate-400">Model-generated signals requiring human investigative review</p>
              </div>
              <Link to="/alerts" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                View all alerts <ChevronRight size={14} />
              </Link>
            </div>

            {data?.recentAlerts && data.recentAlerts.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase">
                    <tr>
                      <th className="py-3 px-4">Priority</th>
                      <th className="py-3 px-4">Entity Type</th>
                      <th className="py-3 px-4">Entity Identifier</th>
                      <th className="py-3 px-4">Anomaly Score</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {data.recentAlerts.map((alert: any) => {
                      const pColor = getPriorityColor(alert.priority);
                      const sColor = getStatusColor(alert.status);
                      return (
                        <tr key={alert.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-4">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${pColor.bg} ${pColor.text} border ${pColor.border}`}>
                              {alert.priority}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-mono text-slate-300">
                            {alert.entity_type}
                          </td>
                          <td className="py-3 px-4 font-mono text-slate-200">
                            {alert.entity_type === 'WALLET' ? truncateAddress(alert.entity_id) : alert.entity_id}
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-20 bg-slate-800 h-2 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-gradient-to-r from-blue-500 via-amber-500 to-rose-500" 
                                  style={{ width: `${Math.min(alert.anomaly_score, 100)}%` }}
                                />
                              </div>
                              <span className="font-mono text-[11px] text-slate-300">
                                {alert.anomaly_score.toFixed(1)}
                              </span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${sColor.bg} ${sColor.text} border ${sColor.border}`}>
                              {alert.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Link
                              to={`/alerts/${alert.id}`}
                              className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                            >
                              Investigate <ChevronRight size={14} />
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-400">
                No alerts generated yet. Run the ML pipeline from the Datasets view.
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
