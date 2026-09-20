import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Link } from 'react-router-dom';
import { 
  FileText, Filter, Search, ExternalLink, ArrowRight, 
  Layers, ShieldAlert, CheckCircle2 
} from 'lucide-react';
import { truncateAddress } from '../utils/format';

export default function EvidencePage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const { data: evidenceList, isLoading, error, refetch } = useQuery({
    queryKey: ['evidence-list'],
    queryFn: async () => (await apiClient.get('/api/evidence/')).data,
  });

  const list: any[] = Array.isArray(evidenceList) ? evidenceList : [];

  const categories = ['ALL', 'MODEL', 'TRANSACTION', 'TEMPORAL', 'AMOUNT', 'NETWORK', 'GEOGRAPHIC', 'CLUSTER', 'GRAPH'];

  const filtered = list.filter((ev) => {
    const matchesCat = selectedCategory === 'ALL' || ev.category === selectedCategory;
    const matchesSearch = !searchTerm || ev.entity_id.toLowerCase().includes(searchTerm.toLowerCase()) || ev.observation.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Evidence Explorer & Data Lineage" 
        description="Traceable audit trail from raw blockchain/network telemetry to algorithmic signals and prioritized leads" 
      />

      {/* 5-Stage Lineage Architecture Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 overflow-x-auto shadow">
        <div className="text-[11px] font-mono text-slate-400 mb-2 uppercase">BTC-SHIELD EVIDENCE PIPELINE:</div>
        <div className="flex items-center gap-2 text-xs font-mono min-w-[700px]">
          <div className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
            1. RAW OBSERVATION
          </div>
          <ArrowRight size={14} className="text-slate-400 shrink-0" />
          <div className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-blue-400">
            2. NORMALIZED ENTITY
          </div>
          <ArrowRight size={14} className="text-slate-400 shrink-0" />
          <div className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-purple-400">
            3. BEHAVIORAL FEATURE
          </div>
          <ArrowRight size={14} className="text-slate-400 shrink-0" />
          <div className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-rose-400">
            4. ML ANOMALY SIGNAL
          </div>
          <ArrowRight size={14} className="text-slate-400 shrink-0" />
          <div className="px-3 py-1.5 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-300 font-bold">
            5. VERIFIED EVIDENCE
          </div>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search evidence observation or target..."
            className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500/50"
          />
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setSelectedCategory(c)}
              className={`px-2.5 py-1 rounded text-[11px] font-mono transition ${
                selectedCategory === c
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Evidence Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Failed to load evidence records." onRetry={() => refetch()} />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<FileText size={32} />}
          title="No Evidence Generated"
          description="Run the full intelligence pipeline on an ingested dataset to produce multi-signal evidence items."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((ev: any) => {
            const url = ev.entity_type === 'WALLET' ? `/wallets/${ev.entity_id}` : `/ips/${ev.entity_id}`;
            return (
              <div key={ev.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 shadow hover:border-slate-700 transition">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
                      {ev.category}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 uppercase">
                      ID #{ev.id}
                    </span>
                  </div>
                  <div className="text-xs font-mono text-slate-300">
                    Strength: <strong className="text-white">{Math.round((ev.strength || 0) * 100)}%</strong>
                  </div>
                </div>

                <p className="text-xs text-slate-200 leading-relaxed">
                  {ev.observation}
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[11px] font-mono">
                  <span className="text-slate-400">
                    Target: <strong className="text-slate-200">{truncateAddress(ev.entity_id, 10, 8)}</strong>
                  </span>
                  <Link to={url} className="text-blue-400 hover:underline flex items-center gap-1">
                    Inspect Entity <ExternalLink size={10} />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
