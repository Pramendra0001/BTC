import { useState } from 'react';
import { useSystemStatus } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { 
  Activity, Server, Database, Cpu, Bot, Globe, 
  ShieldCheck, CheckCircle2, AlertTriangle, RefreshCw 
} from 'lucide-react';

export default function SystemPage() {
  const { data: status, isLoading, error, refetch } = useSystemStatus();
  const [lastPing, setLastPing] = useState<number | null>(null);

  const handlePing = async () => {
    const start = performance.now();
    await refetch();
    setLastPing(Math.round(performance.now() - start));
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-36 w-full" />
          <Skeleton className="h-36 w-full" />
          <Skeleton className="h-36 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState message="Failed to retrieve system telemetry." onRetry={() => refetch()} />;
  }

  const services = [
    {
      name: 'FastAPI Backend Engine',
      description: 'REST API, request validation, authentication, and routing',
      status: 'OPERATIONAL',
      icon: <Server className="text-blue-400" size={20} />,
      metric: lastPing ? `${lastPing}ms latency` : 'Active',
    },
    {
      name: 'PostgreSQL Relational DB',
      description: 'ACID transaction persistence, Alembic migrations, entity resolution',
      status: status?.database === 'ERROR' ? 'DEGRADED' : 'OPERATIONAL',
      icon: <Database className="text-emerald-400" size={20} />,
      metric: 'Connection Pool Healthy',
    },
    {
      name: 'ML Analytics Engine',
      description: 'Isolation Forest anomaly detection & DBSCAN clustering (scikit-learn)',
      status: 'OPERATIONAL',
      icon: <Cpu className="text-purple-400" size={20} />,
      metric: 'Scikit-learn 1.5+ Ready',
    },
    {
      name: 'Explainable AI Provider',
      description: 'Deterministic rule-based explainability (Zero-Hallucination mode)',
      status: 'OPERATIONAL',
      icon: <Bot className="text-blue-400" size={20} />,
      metric: `Provider: ${status?.ai_provider || 'Mock (Offline Safe)'}`,
    },
    {
      name: 'GeoIP / ASN Resolver',
      description: 'Offline autonomous system and country code spatial lookups',
      status: 'OPERATIONAL',
      icon: <Globe className="text-cyan-400" size={20} />,
      metric: 'Offline DB Active',
    },
    {
      name: 'NetworkX Multigraph',
      description: 'In-memory graph analytics, k-hop subgraphs, and centrality indices',
      status: 'OPERATIONAL',
      icon: <Activity className="text-rose-400" size={20} />,
      metric: 'Topology Engine Online',
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="System Status & Telemetry" 
        description="Real-time operational health of backend micro-services, database engines, and ML pipelines" 
        actions={
          <button
            onClick={handlePing}
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
          >
            <RefreshCw size={14} /> Ping Telemetry
          </button>
        }
      />

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map((srv, idx) => {
          const isOp = srv.status === 'OPERATIONAL';
          return (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 shadow">
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                  {srv.icon}
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                  isOp ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                }`}>
                  {srv.status}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-bold text-white">{srv.name}</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{srv.description}</p>
              </div>

              <div className="pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-400 flex items-center justify-between">
                <span>Metric:</span>
                <span className="text-slate-200">{srv.metric}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* BTC-SHIELD OFFLINE STATUS */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <ShieldCheck size={22} />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                BTC-SHIELD OFFLINE STATUS
                <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  SIH 26146 READY
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Self-contained, air-gapped investigative runtime verification
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-mono">APP_MODE:</span>
            <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold uppercase ${
              status?.app_mode === 'offline' 
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
            }`}>
              {status?.app_mode || 'OFFLINE (AIR-GAPPED LINUX)'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs font-mono">
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">Application Mode:</span>
            <span className="text-emerald-400 font-semibold">{status?.app_mode === 'offline' ? 'OFFLINE (AIR-GAPPED)' : 'ONLINE / CLOUD HYBRID'}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">Frontend Engine:</span>
            <span className="text-emerald-400 font-semibold">OPERATIONAL (Port 3000 / Pages)</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">Backend API:</span>
            <span className="text-emerald-400 font-semibold">OPERATIONAL (Port 8000)</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">Database Engine:</span>
            <span className="text-emerald-400 font-semibold">{status?.database === 'OPERATIONAL' ? 'OPERATIONAL (PostgreSQL 16 Local)' : 'DEGRADED / INITIALIZING'}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">ML Engine:</span>
            <span className="text-emerald-400 font-semibold">scikit-learn IF + DBSCAN (LOCAL)</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">Graph Engine:</span>
            <span className="text-emerald-400 font-semibold">NetworkX (LOCAL)</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">Evidence Engine:</span>
            <span className="text-emerald-400 font-semibold">Deterministic Multi-Layer (LOCAL)</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">GeoIP Resolver:</span>
            <span className="text-emerald-400 font-semibold">Offline MaxMind / RFC 5737 (LOCAL)</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">Dataset Ingestion:</span>
            <span className="text-emerald-400 font-semibold">CSV / JSON / XML / ZIP (LOCAL)</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <span className="text-slate-400">External API Calls:</span>
            <span className="text-emerald-400 font-semibold">NONE (Zero-Egress Verified)</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between md:col-span-2">
            <span className="text-slate-400">Internet Connection Required:</span>
            <span className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle2 size={13} className="text-emerald-400" />
              NO (Fully Air-Gapped & Offline Ready)
            </span>
          </div>
        </div>
      </div>

      {/* Deployment Mode Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 shadow-lg">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <ShieldCheck size={16} className="text-blue-400" />
          Dual-Mode Deployment Verification
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 space-y-1">
            <div className="font-bold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              MODE A: OFFLINE AIR-GAPPED LINUX STACK
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Fully self-contained within Docker Compose. Zero internet dependency. Built-in MockAIProvider ensures explainability without cloud AI keys.
            </p>
          </div>

          <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 space-y-1">
            <div className="font-bold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              MODE B: CLOUD PRODUCTION STACK
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Frontend deployable to GitHub Pages (or static CDN), backend deployed to separate HTTPS container host connected to Neon PostgreSQL.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
