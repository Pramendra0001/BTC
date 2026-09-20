import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useWallet } from '../api/hooks';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { 
  Wallet, Network, ArrowRightLeft, Clock, AlertTriangle, 
  ExternalLink, Copy, Check, ArrowUpRight, ArrowDownLeft, ShieldAlert
} from 'lucide-react';
import { 
  truncateAddress, formatSatoshis, formatDate, formatNumber, getPriorityColor 
} from '../utils/format';

export default function WalletDetailPage() {
  const { address } = useParams<{ address: string }>();
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'transactions' | 'network' | 'counterparties' | 'evidence'>('transactions');

  const { data: wallet, isLoading, error, refetch } = useWallet(address || '');

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-96" />
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <Skeleton className="h-80 w-full" />
      </div>
    );
  }

  if (error || !wallet) {
    return <ErrorState message="Failed to load wallet intelligence." onRetry={() => refetch()} />;
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(wallet.address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isAnomalous = (wallet.anomaly_score || 0) > 60;

  return (
    <div className="space-y-6">
      {/* Breadcrumb & Navigation */}
      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
        <Link to="/wallets" className="hover:text-slate-300">WALLETS</Link>
        <span>/</span>
        <span className="text-slate-200 truncate max-w-sm">{wallet.address}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold text-white font-mono flex items-center gap-2">
              <Wallet className="text-blue-400" size={20} />
              {truncateAddress(wallet.address, 12, 10)}
            </h1>
            <button
              onClick={handleCopy}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
              title="Copy Full Address"
            >
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
            </button>
            {isAnomalous && (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1">
                <ShieldAlert size={11} /> ANOMALOUS ({wallet.anomaly_score?.toFixed(1)})
              </span>
            )}
          </div>
          <div className="text-xs text-slate-400 font-mono break-all select-all">
            {wallet.address}
          </div>
          <div className="text-xs text-slate-400 flex items-center gap-4 pt-1 font-mono text-[11px]">
            <span>First seen: <strong className="text-slate-200">{formatDate(wallet.first_seen)}</strong></span>
            <span>Last seen: <strong className="text-slate-200">{formatDate(wallet.last_seen)}</strong></span>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          <Link
            to={`/graph?entityType=WALLET&entityId=${encodeURIComponent(wallet.address)}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-xs font-medium rounded-lg border border-blue-500/30 transition"
          >
            <Network size={14} /> Open in Graph
          </Link>
          <Link
            to={`/timeline?entityType=WALLET&entityId=${encodeURIComponent(wallet.address)}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
          >
            <Clock size={14} /> View Timeline
          </Link>
        </div>
      </div>

      {/* Financial Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Total Outbound (Sent)</div>
          <div className="text-lg font-bold font-mono text-rose-400 mt-1 flex items-center gap-1">
            <ArrowUpRight size={16} /> {formatSatoshis(wallet.total_sent)}
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Total Inbound (Received)</div>
          <div className="text-lg font-bold font-mono text-emerald-400 mt-1 flex items-center gap-1">
            <ArrowDownLeft size={16} /> {formatSatoshis(wallet.total_received)}
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Transaction Volume</div>
          <div className="text-lg font-bold font-mono text-white mt-1">
            {wallet.tx_count} txs
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Counterparties</div>
          <div className="text-lg font-bold font-mono text-purple-400 mt-1">
            {wallet.counterparty_count || wallet.counterparties?.length || 0} unique
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="flex border-b border-slate-800 px-4 bg-slate-950/40">
          {[
            { id: 'transactions', label: `Transactions (${wallet.transactions?.length || 0})` },
            { id: 'network', label: `Network Observations (${wallet.network_observations?.length || 0})` },
            { id: 'counterparties', label: `Counterparties (${wallet.counterparties?.length || 0})` },
            { id: 'evidence', label: `Evidence & Signals (${wallet.evidence?.length || 0})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-3 px-4 text-xs font-medium border-b-2 transition ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-4">
          {/* Tab 1: Transactions */}
          {activeTab === 'transactions' && (
            <div className="overflow-x-auto">
              {wallet.transactions && wallet.transactions.length > 0 ? (
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase">
                    <tr>
                      <th className="py-2.5 px-3">Direction</th>
                      <th className="py-2.5 px-3">TXID</th>
                      <th className="py-2.5 px-3">Amount</th>
                      <th className="py-2.5 px-3">Fee</th>
                      <th className="py-2.5 px-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 font-mono">
                    {wallet.transactions.map((tx: any) => (
                      <tr key={tx.txid} className="hover:bg-slate-800/30">
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            tx.direction === 'SENT' ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'
                          }`}>
                            {tx.direction}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <Link to={`/transactions/${tx.txid}`} className="text-blue-400 hover:underline">
                            {truncateAddress(tx.txid, 10, 8)}
                          </Link>
                        </td>
                        <td className="py-2.5 px-3 text-slate-200">
                          {formatSatoshis(tx.total_input)}
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">
                          {formatSatoshis(tx.fee)}
                        </td>
                        <td className="py-2.5 px-3 text-slate-400 text-[11px]">
                          {formatDate(tx.timestamp)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">No transactions recorded for this wallet.</div>
              )}
            </div>
          )}

          {/* Tab 2: Network Observations */}
          {activeTab === 'network' && (
            <div className="overflow-x-auto">
              {wallet.network_observations && wallet.network_observations.length > 0 ? (
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase">
                    <tr>
                      <th className="py-2.5 px-3">Source IP</th>
                      <th className="py-2.5 px-3">Destination IP</th>
                      <th className="py-2.5 px-3">ASN</th>
                      <th className="py-2.5 px-3">Country</th>
                      <th className="py-2.5 px-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 font-mono">
                    {wallet.network_observations.map((obs: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="py-2.5 px-3 text-blue-400">
                          <Link to={`/ips/${obs.src_ip}`} className="hover:underline">{obs.src_ip}</Link>
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">{obs.dst_ip}</td>
                        <td className="py-2.5 px-3 text-amber-400">
                          <Link to={`/asns/${obs.asn}`} className="hover:underline">{obs.asn}</Link>
                        </td>
                        <td className="py-2.5 px-3 text-slate-300">{obs.country || 'Unknown'}</td>
                        <td className="py-2.5 px-3 text-slate-400 text-[11px]">{formatDate(obs.timestamp)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">No network layer observations correlated with this wallet.</div>
              )}
            </div>
          )}

          {/* Tab 3: Counterparties */}
          {activeTab === 'counterparties' && (
            <div className="space-y-2">
              {wallet.counterparties && wallet.counterparties.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                  {wallet.counterparties.map((cp: string, idx: number) => (
                    <Link
                      key={idx}
                      to={`/wallets/${cp}`}
                      className="p-2.5 bg-slate-950 border border-slate-800 rounded-lg hover:border-blue-500/50 flex items-center justify-between text-xs font-mono text-slate-300 hover:text-white transition"
                    >
                      <span className="truncate pr-2">{cp}</span>
                      <ExternalLink size={12} className="text-slate-400 shrink-0" />
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">No direct counterparties identified.</div>
              )}
            </div>
          )}

          {/* Tab 4: Evidence */}
          {activeTab === 'evidence' && (
            <div className="space-y-3">
              {wallet.evidence && wallet.evidence.length > 0 ? (
                wallet.evidence.map((ev: any) => (
                  <div key={ev.id} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-blue-400">
                        {ev.category}
                      </span>
                      <span className="text-xs font-mono text-slate-400">
                        Strength: <strong className="text-white">{Math.round(ev.strength * 100)}%</strong>
                      </span>
                    </div>
                    <p className="text-xs text-slate-300">{ev.observation}</p>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">No behavioral evidence items logged for this wallet.</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
