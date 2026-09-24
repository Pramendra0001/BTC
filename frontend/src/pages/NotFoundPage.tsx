import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, LayoutDashboard, AlertCircle, Network, Wallet, ArrowRightLeft } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <div className="min-h-[480px] p-6 max-w-xl mx-auto flex flex-col items-center justify-center text-center my-6">
      <div className="p-3.5 rounded-full bg-amber-500/10 text-amber-400 mb-4 border border-amber-500/20 shadow-lg shadow-amber-950/20">
        <ShieldAlert size={32} />
      </div>

      <h1 className="text-xl font-mono font-bold text-white tracking-wide mb-2">
        404 — Route Not Located
      </h1>
      <p className="text-xs text-slate-400 max-w-sm leading-relaxed mb-6">
        The requested path does not match an active intelligence route or entity identifier in BTC-SHIELD.
      </p>

      <div className="w-full bg-slate-900 border border-slate-800 rounded-lg p-4 mb-6">
        <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-3 text-left">
          Available Intelligence Views
        </div>
        <div className="grid grid-cols-2 gap-2 text-left text-xs font-mono">
          <Link
            to="/"
            className="flex items-center gap-2 p-2 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors"
          >
            <LayoutDashboard size={14} className="text-blue-400" /> Command Center
          </Link>
          <Link
            to="/alerts"
            className="flex items-center gap-2 p-2 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors"
          >
            <AlertCircle size={14} className="text-amber-400" /> Alert Queue
          </Link>
          <Link
            to="/graph"
            className="flex items-center gap-2 p-2 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors"
          >
            <Network size={14} className="text-cyan-400" /> Graph Traversal
          </Link>
          <Link
            to="/wallets"
            className="flex items-center gap-2 p-2 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors"
          >
            <Wallet size={14} className="text-emerald-400" /> Wallets
          </Link>
          <Link
            to="/transactions"
            className="flex items-center gap-2 p-2 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors"
          >
            <ArrowRightLeft size={14} className="text-purple-400" /> Transactions
          </Link>
          <Link
            to="/cases"
            className="flex items-center gap-2 p-2 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors"
          >
            <ArrowLeft size={14} className="text-indigo-400" /> Cases & Reports
          </Link>
        </div>
      </div>

      <Link
        to="/"
        className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono font-medium rounded transition shadow-xs"
      >
        <ArrowLeft size={13} /> Return to Command Center
      </Link>
    </div>
  );
}
