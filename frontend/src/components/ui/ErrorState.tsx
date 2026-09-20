export const ErrorState = ({ message, onRetry }: { message: string, onRetry?: () => void }) => {
  return (
    <div className="p-4 bg-slate-900 rounded-lg border border-rose-900/50 flex flex-col items-center justify-center text-center">
      <div className="text-rose-500 mb-2 text-lg font-semibold">Error Loading Data</div>
      <div className="text-slate-400 mb-4">{message}</div>
      {onRetry && (
        <button onClick={onRetry} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded transition">
          Retry
        </button>
      )}
    </div>
  );
}
