import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTransaction } from '../api/hooks';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { 
  ArrowRightLeft, ArrowRight, Network, Clock, ExternalLink, 
  Copy, Check, ShieldAlert, Cpu 
} from 'lucide-react';
import { truncateAddress, formatSatoshis, formatDate } from '../utils/format';

export default function TransactionDetailPage() {
  const { txid } = useParams<{ txid: string }>();
  const [copied, setCopied] = useState(false);

  const { data: tx, isLoading, error, refetch } = useTransaction(txid || '');

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

  if (error || !tx) {
    return <ErrorState message="Failed to load transaction details." onRetry={() => refetch()} />;
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(tx.txid);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const inputs = tx.inputs || [];
  const outputs = tx.outputs || [];

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
        <Link to="/transactions" className="hover:text-slate-300">TRANSACTIONS</Link>
        <span>/</span>
        <span className="text-slate-200 truncate max-w-sm">{tx.txid}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold text-white font-mono flex items-center gap-2">
              <ArrowRightLeft className="text-blue-400" size={20} />
              {truncateAddress(tx.txid, 12, 10)}
            </h1>
            <button
              onClick={handleCopy}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
              title="Copy TXID"
            >
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
            </button>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 uppercase">
              {tx.script_type || 'p2pkh'}
            </span>
          </div>
          <div className="text-xs text-slate-400 font-mono break-all select-all">
            {tx.txid}
          </div>
          <div className="text-xs text-slate-400 font-mono text-[11px] pt-1">
            Confirmed at: <strong className="text-slate-200">{formatDate(tx.timestamp)}</strong>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <Link
            to={`/graph?entityType=TRANSACTION&entityId=${encodeURIComponent(tx.txid)}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-xs font-medium rounded-lg border border-blue-500/30 transition"
          >
            <Network size={14} /> Open in Graph
          </Link>
          <Link
            to={`/timeline?entityType=TRANSACTION&entityId=${encodeURIComponent(tx.txid)}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
          >
            <Clock size={14} /> View Timeline
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Total Input Amount</div>
          <div className="text-lg font-bold font-mono text-white mt-1">
            {formatSatoshis(tx.total_input)}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">{inputs.length} input addresses</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Total Output Amount</div>
          <div className="text-lg font-bold font-mono text-white mt-1">
            {formatSatoshis(tx.total_output)}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">{outputs.length} output addresses</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Miner Transaction Fee</div>
          <div className="text-lg font-bold font-mono text-amber-400 mt-1">
            {formatSatoshis(tx.fee)}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Fee Rate: {tx.total_input > 0 ? ((tx.fee / tx.total_input) * 100).toFixed(4) : 0}%
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Fan-In / Fan-Out Pattern</div>
          <div className="text-lg font-bold font-mono text-purple-400 mt-1">
            {inputs.length} In &rarr; {outputs.length} Out
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            {outputs.length > 5 ? 'Peeling Chain / Tumbling' : inputs.length > 5 ? 'Consolidation' : 'Standard P2P'}
          </div>
        </div>
      </div>

      {/* Inputs and Outputs Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inputs */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
            <h2 className="text-xs font-mono font-bold text-slate-300 uppercase">
              Inputs ({inputs.length})
            </h2>
            <span className="text-xs font-mono text-slate-400">
              Sum: {formatSatoshis(tx.total_input)}
            </span>
          </div>

          <div className="divide-y divide-slate-800/60 max-h-96 overflow-y-auto font-mono text-xs">
            {inputs.length > 0 ? (
              inputs.map((inp: any, idx: number) => (
                <div key={idx} className="p-3.5 flex items-center justify-between hover:bg-slate-800/30">
                  <div className="truncate pr-4">
                    <div className="text-[10px] text-slate-400">INPUT #{inp.position}</div>
                    <Link
                      to={`/wallets/${inp.wallet_address}`}
                      className="text-blue-400 hover:underline flex items-center gap-1 mt-0.5 truncate"
                    >
                      {inp.wallet_address}
                      <ExternalLink size={10} className="shrink-0" />
                    </Link>
                  </div>
                  <div className="text-right font-bold text-white shrink-0">
                    {formatSatoshis(inp.amount)}
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-slate-400">No input details recorded.</div>
            )}
          </div>
        </div>

        {/* Outputs */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
            <h2 className="text-xs font-mono font-bold text-slate-300 uppercase">
              Outputs ({outputs.length})
            </h2>
            <span className="text-xs font-mono text-slate-400">
              Sum: {formatSatoshis(tx.total_output)}
            </span>
          </div>

          <div className="divide-y divide-slate-800/60 max-h-96 overflow-y-auto font-mono text-xs">
            {outputs.length > 0 ? (
              outputs.map((out: any, idx: number) => (
                <div key={idx} className="p-3.5 flex items-center justify-between hover:bg-slate-800/30">
                  <div className="truncate pr-4">
                    <div className="text-[10px] text-slate-400">OUTPUT #{out.position}</div>
                    <Link
                      to={`/wallets/${out.wallet_address}`}
                      className="text-purple-400 hover:underline flex items-center gap-1 mt-0.5 truncate"
                    >
                      {out.wallet_address}
                      <ExternalLink size={10} className="shrink-0" />
                    </Link>
                  </div>
                  <div className="text-right font-bold text-white shrink-0">
                    {formatSatoshis(out.amount)}
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-slate-400">No output details recorded.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
