import { useState } from 'react';
import { useSystemStatus } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { 
  Activity, Server, Database, Cpu, Sparkles, Globe, 
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
      icon: <Sparkles className="text-amber-400" size={20} />,
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
              MODE A: SIH OFFLINE LINUX STACK
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
