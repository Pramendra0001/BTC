import { useState } from 'react';
import { useTransactions } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Link } from 'react-router-dom';
import { ArrowRightLeft, Search, ChevronRight, ExternalLink, Network } from 'lucide-react';
import { truncateAddress, formatSatoshis, formatDate } from '../utils/format';

export default function TransactionsPage() {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [page, setPage] = useState<number>(0);
  const pageSize = 25;

  const { data: transactions, isLoading, error, refetch } = useTransactions({
    skip: page * pageSize,
    limit: pageSize,
  });

  const txList = Array.isArray(transactions) ? transactions : [];

  const filtered = txList.filter((tx: any) => {
    if (!searchTerm) return true;
    return tx.txid.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Transactions" 
        description="Bitcoin on-chain transactions ingested and correlated with network layer telemetry" 
      />

      {/* Search */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by TXID hash..."
            className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500/50"
          />
        </div>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Failed to load transaction data." onRetry={() => refetch()} />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<ArrowRightLeft size={32} />}
          title="No Transactions Found"
          description="No transactions match your query or have been processed."
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase">
                <tr>
                  <th className="py-3 px-4">TXID</th>
                  <th className="py-3 px-4">Total Input</th>
                  <th className="py-3 px-4">Total Output</th>
                  <th className="py-3 px-4">Mining Fee</th>
                  <th className="py-3 px-4">Script Type</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filtered.map((tx: any) => (
                  <tr key={tx.txid} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4">
                      <Link
                        to={`/transactions/${tx.txid}`}
                        className="text-blue-400 hover:underline flex items-center gap-1 font-bold"
                      >
                        {truncateAddress(tx.txid, 12, 10)}
                        <ExternalLink size={10} className="text-slate-400" />
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-slate-200">
                      {formatSatoshis(tx.total_input)}
                    </td>
                    <td className="py-3 px-4 text-slate-200">
                      {formatSatoshis(tx.total_output)}
                    </td>
                    <td className="py-3 px-4 text-amber-400">
                      {formatSatoshis(tx.fee)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 uppercase">
                        {tx.script_type || 'p2pkh'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">
                      {formatDate(tx.timestamp)}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <Link
                        to={`/graph?entityType=TRANSACTION&entityId=${encodeURIComponent(tx.txid)}`}
                        title="View in Graph"
                        className="inline-flex items-center p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-blue-400"
                      >
                        <Network size={14} />
                      </Link>
                      <Link
                        to={`/transactions/${tx.txid}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-xs font-sans border border-blue-500/20"
                      >
                        Details <ChevronRight size={12} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-3 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between text-xs text-slate-400">
            <div>Showing {filtered.length} transactions</div>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="px-2.5 py-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 text-slate-200 text-xs"
              >
                Previous
              </button>
              <span className="font-mono text-xs">Page {page + 1}</span>
              <button
                disabled={filtered.length < pageSize}
                onClick={() => setPage((p) => p + 1)}
                className="px-2.5 py-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 text-slate-200 text-xs"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
