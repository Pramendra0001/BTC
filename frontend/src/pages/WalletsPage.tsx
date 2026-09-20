import { useState } from 'react';
import { useWallets } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Link } from 'react-router-dom';
import { Wallet, Search, ChevronRight, ExternalLink, Network, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { truncateAddress, formatSatoshis, formatDate, formatNumber } from '../utils/format';

export default function WalletsPage() {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [page, setPage] = useState<number>(0);
  const pageSize = 25;

  const { data, isLoading, error, refetch } = useWallets({
    skip: page * pageSize,
    limit: pageSize,
  });

  const wallets = data?.wallets || [];
  const total = data?.total || 0;

  const filtered = wallets.filter((w: any) => {
    if (!searchTerm) return true;
    return w.address.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Wallet Intelligence" 
        description="Resolved on-chain wallet actors, behavioral summaries, and transaction flows" 
      />

      {/* Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by Bitcoin address..."
            className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500/50"
          />
        </div>
        <div className="text-xs text-slate-400 font-mono">
          Total Wallets: <strong className="text-white">{formatNumber(total)}</strong>
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
        <ErrorState message="Failed to load wallet intelligence." onRetry={() => refetch()} />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<Wallet size={32} />}
          title="No Wallets Found"
          description={
            total === 0
              ? "No wallets have been resolved yet. Please ingest a dataset to populate the database."
              : "No wallets match your search filter."
          }
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase">
                <tr>
                  <th className="py-3 px-4">Wallet Address</th>
                  <th className="py-3 px-4">Tx Count</th>
                  <th className="py-3 px-4">Total Sent</th>
                  <th className="py-3 px-4">Total Received</th>
                  <th className="py-3 px-4">First Seen</th>
                  <th className="py-3 px-4">Last Seen</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filtered.map((w: any) => (
                  <tr key={w.address} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4">
                      <Link
                        to={`/wallets/${w.address}`}
                        className="text-blue-400 hover:underline flex items-center gap-1 font-bold"
                      >
                        {truncateAddress(w.address, 10, 8)}
                        <ExternalLink size={10} className="text-slate-400" />
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-slate-200">
                      {w.tx_count}
                    </td>
                    <td className="py-3 px-4 text-rose-400">
                      <span className="flex items-center gap-1">
                        <ArrowUpRight size={12} /> {formatSatoshis(w.total_sent)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-emerald-400">
                      <span className="flex items-center gap-1">
                        <ArrowDownLeft size={12} /> {formatSatoshis(w.total_received)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">
                      {formatDate(w.first_seen)}
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">
                      {formatDate(w.last_seen)}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <Link
                        to={`/graph?entityType=WALLET&entityId=${encodeURIComponent(w.address)}`}
                        title="View in Graph"
                        className="inline-flex items-center p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-blue-400"
                      >
                        <Network size={14} />
                      </Link>
                      <Link
                        to={`/wallets/${w.address}`}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-[11px] font-sans border border-blue-500/20"
                      >
                        Inspect <ChevronRight size={12} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-3 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between text-xs text-slate-400">
            <div>Showing {filtered.length} of {total} wallets</div>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="px-2.5 py-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 text-slate-200 text-xs"
              >
                Previous
              </button>
              <span className="font-mono text-xs">
                Page {page + 1} of {Math.max(1, Math.ceil(total / pageSize))}
              </span>
              <button
                disabled={(page + 1) * pageSize >= total}
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
