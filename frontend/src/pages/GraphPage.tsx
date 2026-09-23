import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useGraph, useDefaultGraphEntity, useSearch } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { GraphVisualization } from '../features/graph/GraphVisualization';
import { Network, Search, Filter, Layers, Database } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function GraphPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const rawType = (searchParams.get('entityType') || 'WALLET').trim().toUpperCase();
  const urlEntityType = (rawType === 'TX' || rawType === 'TRANSACTIONS') ? 'TRANSACTION' : rawType;
  const urlEntityId = (searchParams.get('entityId') || '').replace(/^(TX|TRANSACTION|WALLET|IP|ASN):/i, '').trim();

  const [entityType, setEntityType] = useState<string>(urlEntityType);
  const [entityId, setEntityId] = useState<string>(urlEntityId);
  const [hops, setHops] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Curated default entity lookup (highest-priority alert or top-degree wallet)
  const shouldFetchFallback = !urlEntityId && !entityId;
  const { data: defaultEntityData } = useDefaultGraphEntity();
  const { data: searchResults } = useSearch(searchQuery);

  // Sync state whenever URL search params change (e.g. from navigation or links)
  useEffect(() => {
    if (urlEntityId && urlEntityId !== entityId) {
      setEntityId(urlEntityId);
    }
    if (urlEntityType && urlEntityType !== entityType) {
      setEntityType(urlEntityType);
    }
  }, [urlEntityId, urlEntityType]);

  // If no entity is specified in URL, pick the curated default entity
  useEffect(() => {
    if (!urlEntityId && !entityId && defaultEntityData?.entity_id) {
      const canonicalType = (defaultEntityData.entity_type === 'TX') ? 'TRANSACTION' : defaultEntityData.entity_type;
      setEntityType(canonicalType);
      setEntityId(defaultEntityData.entity_id);
      setSearchParams({ entityType: canonicalType, entityId: defaultEntityData.entity_id });
    }
  }, [defaultEntityData, entityId, urlEntityId, setSearchParams]);

  const { data: graphData, isLoading, error, refetch } = useGraph(entityType, entityId, hops);

  // Canonical entity detection helper for typed search queries
  const detectEntityType = (query: string): { type: string; id: string } => {
    const clean = query.trim();
    if (!clean) return { type: 'WALLET', id: '' };

    // Explicit prefix matches (e.g. "TX:...", "transaction:...", "wallet:...", "ip:...", "asn:...")
    if (/^tx:/i.test(clean) || /^transaction:/i.test(clean)) {
      return { type: 'TRANSACTION', id: clean.replace(/^(tx|transaction):/i, '').trim() };
    }
    if (/^wallet:/i.test(clean)) {
      return { type: 'WALLET', id: clean.replace(/^wallet:/i, '').trim() };
    }
    if (/^ip:/i.test(clean)) {
      return { type: 'IP', id: clean.replace(/^ip:/i, '').trim() };
    }
    if (/^asn:/i.test(clean)) {
      return { type: 'ASN', id: clean.replace(/^asn:/i, '').trim() };
    }

    // Hex hash 64 chars (standard bitcoin txid) or starts with tx_
    if (/^[a-fA-F0-9]{64}$/.test(clean) || /^tx_[a-zA-Z0-9_-]+$/i.test(clean)) {
      return { type: 'TRANSACTION', id: clean };
    }

    // IP address format (e.g. 192.168.1.1)
    if (/^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/.test(clean)) {
      return { type: 'IP', id: clean };
    }

    // ASN format (e.g. AS15169 or AS1234)
    if (/^AS\d+$/i.test(clean)) {
      return { type: 'ASN', id: clean.toUpperCase() };
    }

    // Bitcoin address formats: 1..., 3..., bc1..., tb1...
    if (/^(1|3|bc1|tb1)[a-zA-HJ-NP-Z0-9]{25,62}$/.test(clean)) {
      return { type: 'WALLET', id: clean };
    }

    // Fallback: check if searchResults has an exact or prefix match
    if (searchResults?.results && searchResults.results.length > 0) {
      const topMatch = searchResults.results[0];
      const topType = (topMatch.type === 'TX' || topMatch.type === 'TRANSACTIONS') ? 'TRANSACTION' : topMatch.type;
      return { type: topType, id: topMatch.id };
    }

    // Default heuristic: if 64 chars or contains hex -> TRANSACTION, else WALLET
    if (clean.length === 64 || /^[a-fA-F0-9]{32,}$/.test(clean)) {
      return { type: 'TRANSACTION', id: clean };
    }

    return { type: 'WALLET', id: clean };
  };

  const handleSelectSearchResult = (type: string, id: string) => {
    const canonicalType = (type.toUpperCase() === 'TX' || type.toUpperCase() === 'TRANSACTIONS') ? 'TRANSACTION' : type.toUpperCase();
    const cleanId = id.replace(/^(TX|TRANSACTION|WALLET|IP|ASN):/i, '').trim();
    setEntityType(canonicalType);
    setEntityId(cleanId);
    setSearchQuery('');
    setSearchParams({ entityType: canonicalType, entityId: cleanId });
  };

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;

    // Check if dropdown results contain an exact or strong match
    if (searchResults?.results && searchResults.results.length > 0) {
      const exactMatch = searchResults.results.find(
        (r: any) => r.id.toLowerCase() === query.toLowerCase() ||
                    r.label.toLowerCase() === query.toLowerCase()
      );
      if (exactMatch) {
        handleSelectSearchResult(exactMatch.type, exactMatch.id);
        return;
      }
      const firstResult = searchResults.results[0];
      if (firstResult.id.toLowerCase().startsWith(query.toLowerCase()) || query.length >= 4) {
        handleSelectSearchResult(firstResult.type, firstResult.id);
        return;
      }
    }

    // Auto-detect entity type
    const detected = detectEntityType(query);
    handleSelectSearchResult(detected.type, detected.id);
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
          {/* Quick Entity Search Form */}
          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleSearchSubmit();
                }
              }}
              placeholder="Center on wallet / IP / TX..."
              className="w-56 pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />

            {/* Dropdown matches */}
            {searchQuery.length >= 2 && searchResults?.results && searchResults.results.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-800 rounded-lg shadow-2xl z-30 max-h-60 overflow-y-auto divide-y divide-slate-800/60">
                {searchResults.results.map((r: any, idx: number) => (
                  <button
                    key={idx}
                    type="button"
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
          </form>

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
        <div className="flex items-center gap-4 flex-wrap">
          <span className="text-slate-400">
            Center Node: <span className="font-mono text-white font-bold">{entityId || 'None'}</span>
          </span>
          <span className="text-slate-400">
            Type: <span className="font-mono text-blue-400">{entityType}</span>
          </span>
          {graphData?.stats?.is_isolated && (
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Isolated entity (no counterparty edges observed within {hops} hop{hops > 1 ? 's' : ''})
            </span>
          )}
        </div>
        <div className="flex items-center gap-4 text-slate-400 font-mono text-[11px]">
          <span>Nodes: <strong className="text-white">{graphData?.stats?.node_count || graphData?.nodes?.length || 0}</strong></span>
          <span>Edges: <strong className="text-white">{graphData?.stats?.edge_count || graphData?.edges?.length || 0}</strong></span>
        </div>
      </div>

      {/* Main Canvas */}
      <div className="flex-1 relative min-h-0">
        {isLoading ? (
          <div className="w-full h-full bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-center p-6">
            <div className="text-center space-y-3 max-w-sm">
              <div className="w-9 h-9 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <div className="text-xs font-medium text-slate-200">
                Computing graph topology and centrality metrics...
              </div>
              <div className="text-[11px] font-mono text-slate-400">
                Resolving multi-hop relational edges for {entityType}: {entityId ? entityId.slice(0, 16) + '...' : ''}
              </div>
            </div>
          </div>
        ) : error ? (
          <ErrorState message="Failed to load graph topology." onRetry={() => refetch()} />
        ) : !entityId || !graphData?.nodes || graphData.nodes.length === 0 ? (
          <EmptyState
            icon={<Network size={32} />}
            title="No Graph Nodes Available"
            description={
              entityId
                ? `No link analysis connections found for ${entityType} ${entityId}.`
                : "Select an entity or ensure a dataset has been ingested and the intelligence pipeline executed."
            }
            action={
              <Link
                to="/wallets"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition"
              >
                <Network size={14} className="inline mr-1" /> Browse Wallets
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
