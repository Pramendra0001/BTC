import { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useTimeline } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { 
  Clock, ArrowRightLeft, Network, AlertCircle, ExternalLink, 
  Calendar, Filter, ChevronRight, ShieldAlert 
} from 'lucide-react';
import { formatDate, truncateAddress } from '../utils/format';

export default function TimelinePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const entityType = searchParams.get('entityType') || 'WALLET';
  const entityId = searchParams.get('entityId') || '';
  const [filterType, setFilterType] = useState<string>('ALL');

  const { data: timelineData, isLoading, error, refetch } = useTimeline(entityType, entityId);

  const events = timelineData?.events || [];

  const filteredEvents = events.filter((e: any) => {
    if (filterType === 'ALL') return true;
    return e.type === filterType;
  });

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Entity Activity Timeline" 
        description="Chronological event reconstruction correlating on-chain transactions and network-layer observations" 
      />

      {/* Target Info Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
            {entityType} TARGET
          </span>
          <span className="font-mono text-sm font-bold text-white">
            {entityId ? truncateAddress(entityId, 16, 12) : 'No Entity Selected'}
          </span>
        </div>

        {/* Event Type Filter */}
        <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 rounded-lg p-1 text-xs">
          <Filter size={13} className="text-slate-400 ml-1.5" />
          {['ALL', 'TRANSACTION', 'NETWORK_OBSERVATION', 'ALERT'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`px-2.5 py-0.5 rounded text-[11px] font-mono transition ${
                filterType === t ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t === 'NETWORK_OBSERVATION' ? 'NETWORK' : t}
            </button>
          ))}
        </div>
      </div>

      {/* Main Timeline View */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Failed to load timeline events." onRetry={() => refetch()} />
      ) : filteredEvents.length === 0 ? (
        <EmptyState
          icon={<Clock size={32} />}
          title="No Timeline Events"
          description={
            entityId
              ? "No events found for this entity under current filter."
              : "Select a wallet, IP, or transaction from the respective module to inspect its timeline."
          }
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
          <div className="relative border-l-2 border-slate-800 ml-4 space-y-8 py-2">
            {filteredEvents.map((evt: any, idx: number) => {
              const isTx = evt.type === 'TRANSACTION';
              const isNet = evt.type === 'NETWORK_OBSERVATION';
              const isAlert = evt.type === 'ALERT';

              return (
                <div key={idx} className="relative pl-6">
                  {/* Timeline Dot */}
                  <span className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-slate-900 flex items-center justify-center ${
                    isAlert ? 'bg-rose-500' : isTx ? 'bg-blue-500' : 'bg-emerald-500'
                  }`} />

                  {/* Event Card */}
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2 hover:border-slate-700 transition">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-slate-800/80 pb-2">
                      <div className="flex items-center gap-2">
                        {isAlert && <AlertCircle size={14} className="text-rose-400" />}
                        {isTx && <ArrowRightLeft size={14} className="text-blue-400" />}
                        {isNet && <Network size={14} className="text-emerald-400" />}
                        <span className="text-xs font-bold text-white font-mono">
                          {evt.title}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                          {evt.type}
                        </span>
                      </div>
                      <div className="text-[11px] font-mono text-slate-400">
                        {formatDate(evt.timestamp)}
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 font-mono">
                      {evt.description}
                    </p>

                    {evt.entity_id && (
                      <div className="pt-1 flex items-center gap-2">
                        <Link
                          to={
                            evt.entity_type === 'TRANSACTION'
                              ? `/transactions/${evt.entity_id}`
                              : evt.entity_type === 'IP'
                              ? `/ips/${evt.entity_id}`
                              : `/alerts/${evt.entity_id}`
                          }
                          className="inline-flex items-center gap-1 text-[11px] font-mono text-blue-400 hover:underline"
                        >
                          View {evt.entity_type} <ExternalLink size={10} />
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
