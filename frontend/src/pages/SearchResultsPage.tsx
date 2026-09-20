import { useSearchParams, Link } from 'react-router-dom';
import { useSearch } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Search, ChevronRight, ExternalLink, Wallet, ArrowRightLeft, Network, Briefcase } from 'lucide-react';
import { truncateAddress } from '../utils/format';

export default function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  const { data: searchData, isLoading, error, refetch } = useSearch(query);

  const results = searchData?.results || [];

  return (
    <div className="space-y-6">
      <PageHeader 
        title={`Search Results for "${query}"`} 
        description={`Categorized intelligence entities matching query criteria (${results.length} found)`} 
      />

      {isLoading ? (
        <div className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Search execution failed." onRetry={() => refetch()} />
      ) : results.length === 0 ? (
        <EmptyState
          icon={<Search size={32} />}
          title="No Entities Found"
          description={`No wallets, transactions, IPs, ASNs, or cases matched "${query}".`}
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl divide-y divide-slate-800/80 overflow-hidden shadow">
          {results.map((r: any, idx: number) => {
            const isWallet = r.type === 'WALLET';
            const isTx = r.type === 'TRANSACTION';
            const isIp = r.type === 'IP';
            const isCase = r.type === 'CASE';

            return (
              <Link
                key={idx}
                to={r.url}
                className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition block"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400">
                    {isWallet && <Wallet size={16} className="text-blue-400" />}
                    {isTx && <ArrowRightLeft size={16} className="text-purple-400" />}
                    {isIp && <Network size={16} className="text-emerald-400" />}
                    {isCase && <Briefcase size={16} className="text-amber-400" />}
                    {!isWallet && !isTx && !isIp && !isCase && <Search size={16} />}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {r.type}
                      </span>
                      <span className="text-sm font-semibold text-white font-mono">
                        {isWallet ? truncateAddress(r.label, 12, 10) : r.label}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1 font-mono">
                      {r.subtitle}
                    </div>
                  </div>
                </div>

                <ChevronRight size={16} className="text-slate-400" />
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
