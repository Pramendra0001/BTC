import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useHeuristicsSummary, usePeelingChains, useMixingPatterns, useTransactionHeuristics } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { GitMerge, Shuffle, Search, ArrowRight, ShieldAlert, CheckCircle2, ChevronRight, Layers, ArrowUpRight } from 'lucide-react';
import { formatBTC, formatNumber } from '../utils/format';

export default function HeuristicsPage() {
  const [activeTab, setActiveTab] = useState<'peeling' | 'mixing' | 'analyzer'>('peeling');
  const [searchTxid, setSearchTxid] = useState('');
  const [queryTxid, setQueryTxid] = useState('');
  const [expandedChain, setExpandedChain] = useState<string | null>(null);

  const { data: summary, isLoading: summaryLoading, error: summaryError } = useHeuristicsSummary();
  const { data: peelingChains, isLoading: peelingLoading, error: peelingError } = usePeelingChains({ min_hops: 2, limit: 50 });
  const { data: mixingPatterns, isLoading: mixingLoading, error: mixingError } = useMixingPatterns({ limit: 50 });
  const { data: txAnalysis, isLoading: txLoading } = useTransactionHeuristics(queryTxid);

  const handleSearchTx = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTxid.trim()) {
      setQueryTxid(searchTxid.trim());
      setActiveTab('analyzer');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <PageHeader
          title="Structural Heuristics & Pattern Analysis"
          description="Algorithmic identification of peeling chains, CoinJoin equal-denomination rounds, and tumbler topologies"
        />

        <form onSubmit={handleSearchTx} className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
            <input
              type="text"
              placeholder="Inspect TXID structure..."
              value={searchTxid}
              onChange={(e) => setSearchTxid(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 w-64 md:w-80 font-mono"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition-colors"
          >
            Analyze
          </button>
        </form>
      </div>

      {/* KPI Cards */}
      {summaryLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-7 w-16" />
            </div>
          ))}
        </div>
      ) : summaryError ? (
        <ErrorState message="Failed to load heuristics summary" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Peeling Chains</span>
              <GitMerge size={16} className="text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-white">
              {formatNumber(summary?.peeling_chains_detected || 0)}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Max depth: <span className="text-amber-400 font-mono">{summary?.max_chain_hops || 0} hops</span>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Peeled Volume</span>
              <span className="text-amber-400 font-mono text-xs">BTC</span>
            </div>
            <div className="text-2xl font-bold text-amber-400 font-mono">
              {formatBTC(summary?.total_peeled_volume_btc || 0)}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Cumulative structuring volume
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Mixing Transactions</span>
              <Shuffle size={16} className="text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-white">
              {formatNumber(summary?.mixing_transactions_detected || 0)}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              CoinJoin rounds: <span className="text-blue-400 font-mono">{summary?.coinjoin_rounds_count || 0}</span>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Mixing Volume</span>
              <span className="text-blue-400 font-mono text-xs">BTC</span>
            </div>
            <div className="text-2xl font-bold text-blue-400 font-mono">
              {formatBTC(summary?.total_mixing_volume_btc || 0)}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Volume through high-entropy rounds
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-slate-800 flex items-center gap-6">
        <button
          onClick={() => setActiveTab('peeling')}
          className={`pb-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'peeling'
              ? 'text-amber-400 border-amber-400'
              : 'text-slate-400 border-transparent hover:text-slate-200'
          }`}
        >
          <GitMerge size={14} />
          Peeling Chains ({peelingChains?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('mixing')}
          className={`pb-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'mixing'
              ? 'text-blue-400 border-blue-400'
              : 'text-slate-400 border-transparent hover:text-slate-200'
          }`}
        >
          <Shuffle size={14} />
          Mixing & CoinJoin Patterns ({mixingPatterns?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('analyzer')}
          className={`pb-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'analyzer'
              ? 'text-purple-400 border-purple-400'
              : 'text-slate-400 border-transparent hover:text-slate-200'
          }`}
        >
          <Layers size={14} />
          Single TX Inspector {queryTxid ? `(${queryTxid.slice(0, 8)}...)` : ''}
        </button>
      </div>

      {/* TAB 1: PEELING CHAINS */}
      {activeTab === 'peeling' && (
        <div className="space-y-4">
          {peelingLoading ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : peelingError ? (
            <ErrorState message="Failed to load peeling chains" />
          ) : !peelingChains || peelingChains.length === 0 ? (
            <EmptyState
              icon={<GitMerge className="text-slate-600" size={40} />}
              title="No Peeling Chains Detected"
              description="No multi-hop peeling chains with $\ge 2$ sequential outputs and value asymmetry were detected in the active transaction pool."
            />
          ) : (
            <div className="space-y-3">
              {peelingChains.map((chain: any) => {
                const isExpanded = expandedChain === chain.chain_id;
                return (
                  <div
                    key={chain.chain_id}
                    className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden transition-colors hover:border-slate-700"
                  >
                    <div
                      onClick={() => setExpandedChain(isExpanded ? null : chain.chain_id)}
                      className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer select-none"
                    >
                      <div className="flex items-start md:items-center gap-3">
                        <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
                          <GitMerge size={18} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-bold text-white">
                              Chain {chain.chain_id}
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-400">
                              {chain.hop_count} Hops
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                              Confidence {chain.confidence_score}%
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-2">
                            <span>Origin: <span className="font-mono text-slate-300">{chain.start_txid.slice(0, 16)}...</span></span>
                            <span>•</span>
                            <span>Terminal: <span className="font-mono text-slate-300">{chain.terminal_txid.slice(0, 16)}...</span></span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-6 justify-between md:justify-end">
                        <div className="text-right">
                          <div className="text-xs font-bold font-mono text-amber-400">
                            {formatBTC(chain.total_peeled_btc)} BTC
                          </div>
                          <div className="text-[10px] text-slate-500">
                            Remaining Change: {formatBTC(chain.final_change_btc)} BTC
                          </div>
                        </div>
                        <ChevronRight
                          size={18}
                          className={`text-slate-400 transition-transform ${isExpanded ? 'rotate-90 text-amber-400' : ''}`}
                        />
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="border-t border-slate-800 p-4 bg-slate-950/60 space-y-3">
                        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                          Sequential Peeling Hops ({chain.hops.length})
                        </h4>
                        <div className="space-y-2">
                          {chain.hops.map((hop: any) => (
                            <div
                              key={hop.hop}
                              className="bg-slate-900 border border-slate-800/80 rounded-lg p-3 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
                            >
                              <div className="flex items-center gap-3">
                                <span className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center font-bold text-[11px] text-amber-400">
                                  {hop.hop}
                                </span>
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="text-slate-400 text-[11px]">TX:</span>
                                    <Link
                                      to={`/transactions/${hop.txid}`}
                                      className="font-mono text-blue-400 hover:underline flex items-center gap-1"
                                    >
                                      {hop.txid.slice(0, 16)}...
                                      <ArrowUpRight size={12} />
                                    </Link>
                                  </div>
                                  <div className="text-[11px] text-slate-500 mt-0.5">
                                    {hop.timestamp || 'Timestamp recorded'}
                                  </div>
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-4 text-right">
                                <div>
                                  <div className="text-[10px] text-slate-400">Peeled Out</div>
                                  <div className="font-mono text-rose-400 font-bold">
                                    {formatBTC(hop.peeled_amount)} BTC
                                  </div>
                                  <div className="text-[10px] font-mono text-slate-500 truncate max-w-[140px]">
                                    {hop.peeled_address}
                                  </div>
                                </div>
                                <div>
                                  <div className="text-[10px] text-slate-400">Change Retained</div>
                                  <div className="font-mono text-emerald-400 font-bold">
                                    {formatBTC(hop.change_amount)} BTC
                                  </div>
                                  <div className="text-[10px] font-mono text-slate-500 truncate max-w-[140px]">
                                    {hop.change_address}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: MIXING / COINJOIN PATTERNS */}
      {activeTab === 'mixing' && (
        <div className="space-y-4">
          {mixingLoading ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : mixingError ? (
            <ErrorState message="Failed to load mixing patterns" />
          ) : !mixingPatterns || mixingPatterns.length === 0 ? (
            <EmptyState
              icon={<Shuffle className="text-slate-600" size={40} />}
              title="No Mixing Patterns Detected"
              description="No transactions matching CoinJoin equal-denomination output fingerprints or high-entropy tumbler structures were found."
            />
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider bg-slate-950/40">
                      <th className="p-3">Pattern Type</th>
                      <th className="p-3">Transaction ID</th>
                      <th className="p-3">Topology</th>
                      <th className="p-3">Equal Outputs</th>
                      <th className="p-3">Entropy</th>
                      <th className="p-3">Total Volume</th>
                      <th className="p-3">Confidence</th>
                      <th className="p-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {mixingPatterns.map((mix: any) => (
                      <tr key={mix.txid} className="hover:bg-slate-800/40 transition-colors">
                        <td className="p-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                              mix.pattern_type === 'EQUAL_DENOMINATION_COINJOIN'
                                ? 'bg-purple-500/20 text-purple-400'
                                : mix.pattern_type === 'MANY_TO_MANY_TUMBLER'
                                ? 'bg-blue-500/20 text-blue-400'
                                : 'bg-amber-500/20 text-amber-400'
                            }`}
                          >
                            {mix.pattern_type}
                          </span>
                        </td>
                        <td className="p-3 font-mono">
                          <Link
                            to={`/transactions/${mix.txid}`}
                            className="text-blue-400 hover:underline flex items-center gap-1"
                          >
                            {mix.txid.slice(0, 16)}...
                          </Link>
                        </td>
                        <td className="p-3 font-mono">
                          {mix.input_count} in → {mix.output_count} out
                        </td>
                        <td className="p-3 font-mono text-purple-400 font-bold">
                          {mix.max_equal_outputs} identical
                        </td>
                        <td className="p-3 font-mono text-slate-400">
                          {mix.entropy_bits} bits
                        </td>
                        <td className="p-3 font-mono text-white font-bold">
                          {formatBTC(mix.total_volume_btc)} BTC
                        </td>
                        <td className="p-3">
                          <span className="font-mono text-xs font-semibold text-emerald-400">
                            {mix.confidence_score}%
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <Link
                            to={`/transactions/${mix.txid}`}
                            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] font-semibold transition-colors"
                          >
                            Inspect
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: SINGLE TX INSPECTOR */}
      {activeTab === 'analyzer' && (
        <div className="space-y-4">
          {!queryTxid ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center space-y-3">
              <Layers className="mx-auto text-slate-600" size={40} />
              <h3 className="text-sm font-bold text-white">Enter a Transaction ID to Analyze</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Evaluate any transaction for peeling chain steps, CoinJoin equal outputs, fan-in/fan-out asymmetry, and Shannon entropy.
              </p>
            </div>
          ) : txLoading ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-20 w-full" />
            </div>
          ) : !txAnalysis || !txAnalysis.found ? (
            <ErrorState message={`Transaction ${queryTxid} not found in database.`} />
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div>
                  <div className="text-[11px] text-slate-400 uppercase tracking-wider">Transaction ID</div>
                  <div className="font-mono text-sm font-bold text-white break-all">{txAnalysis.txid}</div>
                  <div className="text-xs text-slate-400 mt-1">{txAnalysis.timestamp}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${
                      txAnalysis.structural_risk_level === 'HIGH'
                        ? 'bg-rose-500/20 text-rose-400'
                        : 'bg-emerald-500/20 text-emerald-400'
                    }`}
                  >
                    Risk Level: {txAnalysis.structural_risk_level}
                  </span>
                  <Link
                    to={`/transactions/${txAnalysis.txid}`}
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition-colors"
                  >
                    View Full TX
                  </Link>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase">Topology</div>
                  <div className="text-base font-bold text-white font-mono mt-0.5">
                    {txAnalysis.input_count} In → {txAnalysis.output_count} Out
                  </div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase">Total Output Volume</div>
                  <div className="text-base font-bold text-white font-mono mt-0.5">
                    {formatBTC(txAnalysis.total_volume_btc)} BTC
                  </div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase">Output Entropy</div>
                  <div className="text-base font-bold text-purple-400 font-mono mt-0.5">
                    {txAnalysis.entropy_bits} bits
                  </div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase">Equal Outputs</div>
                  <div className="text-base font-bold text-amber-400 font-mono mt-0.5">
                    {txAnalysis.max_equal_outputs} matching
                  </div>
                </div>
              </div>

              {/* Detected Structural Patterns */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Detected Structural Fingerprints
                </h4>
                <div className="flex flex-wrap gap-2">
                  {txAnalysis.detected_patterns.map((pat: string) => (
                    <span
                      key={pat}
                      className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-200 text-xs font-mono"
                    >
                      {pat}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
