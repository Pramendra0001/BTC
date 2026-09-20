import { useParams, Link } from 'react-router-dom';
import { useIP } from '../api/hooks';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { 
  Network, Globe, Server, Clock, ExternalLink, ArrowRightLeft, Wallet 
} from 'lucide-react';
import { truncateAddress, formatDate } from '../utils/format';

export default function IPDetailPage() {
  const { ip } = useParams<{ ip: string }>();
  const { data: ipData, isLoading, error, refetch } = useIP(ip || '');

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <Skeleton className="h-80 w-full" />
      </div>
    );
  }

  if (error || !ipData) {
    return <ErrorState message="Failed to load IP intelligence details." onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
        <Link to="/graph" className="hover:text-slate-300">NETWORK ENTITIES</Link>
        <span>/</span>
        <span className="text-slate-200">{ipData.ip_address}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold text-white font-mono flex items-center gap-2">
              <Network className="text-emerald-400" size={20} />
              {ipData.ip_address}
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              IPv4 OBSERVATION
            </span>
          </div>
          <div className="text-xs text-slate-400 font-mono flex items-center gap-4 pt-1">
            <span>First Observed: <strong className="text-slate-200">{formatDate(ipData.first_seen)}</strong></span>
            <span>Last Observed: <strong className="text-slate-200">{formatDate(ipData.last_seen)}</strong></span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Link
            to={`/graph?entityType=IP&entityId=${encodeURIComponent(ipData.ip_address)}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-xs font-medium rounded-lg border border-blue-500/30 transition"
          >
            <Network size={14} /> View in Graph
          </Link>
          <Link
            to={`/timeline?entityType=IP&entityId=${encodeURIComponent(ipData.ip_address)}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
          >
            <Clock size={14} /> View Timeline
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Autonomous System (ASN)</div>
          <div className="text-base font-bold font-mono text-amber-400 mt-1 flex items-center gap-1.5">
            <Server size={16} />
            {ipData.asn ? (
              <Link to={`/asns/${ipData.asn}`} className="hover:underline">
                {ipData.asn}
              </Link>
            ) : (
              'Unresolved'
            )}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Geographic Country</div>
          <div className="text-base font-bold font-mono text-cyan-400 mt-1 flex items-center gap-1.5">
            <Globe size={16} />
            {ipData.country || 'Unknown'}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Total Observations</div>
          <div className="text-lg font-bold font-mono text-white mt-1">
            {ipData.observation_count} events
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Correlated Wallets</div>
          <div className="text-lg font-bold font-mono text-purple-400 mt-1">
            {ipData.related_wallets?.length || 0} actors
          </div>
        </div>
      </div>

      {/* Related Wallets & Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Correlated Wallets */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-950/40">
            <h2 className="text-xs font-mono font-bold text-slate-300 uppercase flex items-center gap-2">
              <Wallet size={14} className="text-blue-400" />
              Correlated Wallet Actors ({ipData.related_wallets?.length || 0})
            </h2>
          </div>
          <div className="divide-y divide-slate-800/60 max-h-80 overflow-y-auto p-2">
            {ipData.related_wallets && ipData.related_wallets.length > 0 ? (
              ipData.related_wallets.map((w: string, idx: number) => (
                <Link
                  key={idx}
                  to={`/wallets/${w}`}
                  className="p-2.5 rounded-lg hover:bg-slate-800/50 flex items-center justify-between text-xs font-mono text-blue-400 hover:text-blue-300 transition"
                >
                  <span>{truncateAddress(w, 14, 12)}</span>
                  <ExternalLink size={12} className="text-slate-400" />
                </Link>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-400">No correlated wallet actors.</div>
            )}
          </div>
        </div>

        {/* Recent Network Observations */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-950/40">
            <h2 className="text-xs font-mono font-bold text-slate-300 uppercase flex items-center gap-2">
              <ArrowRightLeft size={14} className="text-emerald-400" />
              Recent Observations ({ipData.recent_observations?.length || 0})
            </h2>
          </div>
          <div className="divide-y divide-slate-800/60 max-h-80 overflow-y-auto p-2 text-xs font-mono">
            {ipData.recent_observations && ipData.recent_observations.length > 0 ? (
              ipData.recent_observations.map((obs: any, idx: number) => (
                <div key={idx} className="p-2.5 rounded-lg hover:bg-slate-800/30 flex items-center justify-between">
                  <div>
                    <div className="text-slate-300 flex items-center gap-1">
                      <span>TX:</span>
                      <Link to={`/transactions/${obs.transaction_id}`} className="text-blue-400 hover:underline">
                        {truncateAddress(obs.transaction_id, 8, 6)}
                      </Link>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">Dest: {obs.dst_ip}</div>
                  </div>
                  <div className="text-right text-[11px] text-slate-400">
                    {formatDate(obs.timestamp)}
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-400">No recent observation events.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
