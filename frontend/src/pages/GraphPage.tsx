import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useGraph, useDashboard, useSearch } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { GraphVisualization } from '../features/graph/GraphVisualization';
import { Network, Search, Filter, Layers, Database } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function GraphPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlEntityType = searchParams.get('entityType') || 'WALLET';
  const urlEntityId = searchParams.get('entityId') || '';

  const [entityType, setEntityType] = useState<string>(urlEntityType);
  const [entityId, setEntityId] = useState<string>(urlEntityId);
  const [hops, setHops] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const { data: dashboardData } = useDashboard();
  const { data: searchResults } = useSearch(searchQuery);

  // If no entity is specified in URL, pick the top recent alert entity
  useEffect(() => {
    if (!entityId && dashboardData?.recentAlerts && dashboardData.recentAlerts.length > 0) {
      const topAlert = dashboardData.recentAlerts[0];
      setEntityType(topAlert.entity_type);
      setEntityId(topAlert.entity_id);
      setSearchParams({ entityType: topAlert.entity_type, entityId: topAlert.entity_id });
    }
  }, [dashboardData, entityId, setSearchParams]);

  const { data: graphData, isLoading, error, refetch } = useGraph(entityType, entityId, hops);

  const handleSelectSearchResult = (type: string, id: string) => {
    setEntityType(type);
    setEntityId(id);
    setSearchQuery('');
    setSearchParams({ entityType: type, entityId: id });
  };

  return (
    <div className="space-y-4 h-[calc(100vh-100px)] flex flex-col">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
        <div>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <Network className="text-blue-400" size={20} />
            Investigation Link Analysis Graph
          </h1>
          <p className="text-xs text-slate-400">
            Multi-hop relational graph connecting Bitcoin wallets, transactions, IPs, ASNs, and countries
          </p>
        </div>

        {/* Entity Selector & Hop Controls */}
        <div className="flex items-center gap-2">
          {/* Quick Entity Search */}
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Center on wallet / IP / TX..."
              className="w-56 pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />

            {/* Dropdown matches */}
            {searchQuery.length >= 2 && searchResults?.results && searchResults.results.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-800 rounded-lg shadow-2xl z-30 max-h-60 overflow-y-auto divide-y divide-slate-800/60">
                {searchResults.results.map((r: any, idx: number) => (
                  <button
                    key={idx}
                    onClick={() => handleSelectSearchResult(r.type, r.id)}
                    className="w-full px-3 py-2 text-left hover:bg-slate-800 text-xs flex items-center justify-between"
                  >
                    <span className="font-mono text-slate-200 truncate">{r.label}</span>
                    <span className="text-[10px] font-mono text-blue-400 bg-slate-800 px-1.5 py-0.5 rounded">
                      {r.type}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Hop Selector */}
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            <span className="px-2 text-slate-400 text-[11px] font-mono">HOPS:</span>
            {[1, 2, 3].map((h) => (
              <button
                key={h}
                onClick={() => setHops(h)}
                className={`px-2.5 py-0.5 rounded text-xs font-mono font-medium transition ${
                  hops === h ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {h}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Graph Status Info Bar */}
      <div className="bg-slate-900/60 border border-slate-800/80 px-4 py-2 rounded-lg flex items-center justify-between text-xs shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-slate-400">
            Center Node: <span className="font-mono text-white font-bold">{entityId || 'None'}</span>
          </span>
          <span className="text-slate-400">
            Type: <span className="font-mono text-blue-400">{entityType}</span>
          </span>
        </div>
        <div className="flex items-center gap-4 text-slate-400 font-mono text-[11px]">
          <span>Nodes: <strong className="text-white">{graphData?.stats?.node_count || graphData?.nodes?.length || 0}</strong></span>
          <span>Edges: <strong className="text-white">{graphData?.stats?.edge_count || graphData?.edges?.length || 0}</strong></span>
        </div>
      </div>

      {/* Main Canvas */}
      <div className="flex-1 relative min-h-0">
        {isLoading ? (
          <div className="w-full h-full bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-center">
            <div className="text-center space-y-2">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <div className="text-xs text-slate-400">Computing graph topology and centrality metrics...</div>
            </div>
          </div>
        ) : error ? (
          <ErrorState message="Failed to load graph topology." onRetry={() => refetch()} />
        ) : !entityId || !graphData?.nodes || graphData.nodes.length === 0 ? (
          <EmptyState
            icon={<Network size={32} />}
            title="No Graph Nodes Available"
            description="Select an entity or ensure a dataset has been ingested and the intelligence pipeline executed."
            action={
              <Link
                to="/datasets"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition"
              >
                <Database size={14} className="inline mr-1" /> Go to Datasets
              </Link>
            }
          />
        ) : (
          <GraphVisualization
            elements={graphData}
            centerEntityId={entityId}
          />
        )}
      </div>
    </div>
  );
}
