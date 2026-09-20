import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorState = ({ message = "An error occurred while loading data.", onRetry }: ErrorStateProps) => {
  return (
    <div className="p-8 bg-slate-900 rounded border border-slate-800 flex flex-col items-center justify-center text-center">
      <div className="p-2 rounded bg-rose-500/10 text-rose-500 mb-3 border border-rose-500/20">
        <AlertCircle size={20} />
      </div>
      <h3 className="text-sm font-semibold text-slate-200 mb-1">Data Retrieval Error</h3>
      <p className="text-xs text-slate-400 max-w-md mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-850 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200 rounded transition cursor-pointer"
        >
          <RefreshCw size={13} /> Retry Query
        </button>
      )}
    </div>
  );
};
