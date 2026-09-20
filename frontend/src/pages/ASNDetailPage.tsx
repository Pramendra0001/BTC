import { useParams, Link } from 'react-router-dom';
import { useASN } from '../api/hooks';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { Server, Globe, Network, ExternalLink } from 'lucide-react';

export default function ASNDetailPage() {
  const { asn } = useParams<{ asn: string }>();
  const { data: asnData, isLoading, error, refetch } = useASN(asn || '');

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <Skeleton className="h-80 w-full" />
      </div>
    );
  }

  if (error || !asnData) {
    return <ErrorState message="Failed to load ASN intelligence details." onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
        <Link to="/graph" className="hover:text-slate-300">NETWORK ENTITIES</Link>
        <span>/</span>
        <span className="text-slate-200">{asnData.asn_number}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold text-white font-mono flex items-center gap-2">
              <Server className="text-amber-400" size={20} />
              {asnData.asn_number}
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
              AUTONOMOUS SYSTEM
            </span>
          </div>
          <div className="text-xs text-slate-400 font-mono">
            {asnData.name || `Autonomous System ${asnData.asn_number}`}
          </div>
        </div>

        <Link
          to={`/graph?entityType=ASN&entityId=${encodeURIComponent(asnData.asn_number)}`}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-xs font-medium rounded-lg border border-blue-500/30 transition"
        >
          <Network size={14} /> View in Graph
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Associated IPs</div>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
            {asnData.associated_ips?.length || asnData.ip_count || 0} IPs
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Geographic Jurisdictions</div>
          <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
            {asnData.associated_countries?.length || asnData.country_count || 0} Countries
          </div>
        </div>
      </div>

      {/* Associated IPs and Countries */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* IPs */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-950/40">
            <h2 className="text-xs font-mono font-bold text-slate-300 uppercase flex items-center gap-2">
              <Network size={14} className="text-emerald-400" />
              Observed IP Addresses ({asnData.associated_ips?.length || 0})
            </h2>
          </div>
          <div className="divide-y divide-slate-800/60 max-h-80 overflow-y-auto p-2">
            {asnData.associated_ips && asnData.associated_ips.length > 0 ? (
              asnData.associated_ips.map((ip: string, idx: number) => (
                <Link
                  key={idx}
                  to={`/ips/${ip}`}
                  className="p-2.5 rounded-lg hover:bg-slate-800/50 flex items-center justify-between text-xs font-mono text-blue-400 hover:text-blue-300 transition"
                >
                  <span>{ip}</span>
                  <ExternalLink size={12} className="text-slate-400" />
                </Link>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-400">No observed IPs for this ASN.</div>
            )}
          </div>
        </div>

        {/* Countries */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-950/40">
            <h2 className="text-xs font-mono font-bold text-slate-300 uppercase flex items-center gap-2">
              <Globe size={14} className="text-cyan-400" />
              Jurisdictions / Countries ({asnData.associated_countries?.length || 0})
            </h2>
          </div>
          <div className="p-4 flex flex-wrap gap-2">
            {asnData.associated_countries && asnData.associated_countries.length > 0 ? (
              asnData.associated_countries.map((c: string, idx: number) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200"
                >
                  {c}
                </span>
              ))
            ) : (
              <div className="text-xs text-slate-400">No country affiliations recorded.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
