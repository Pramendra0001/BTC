import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertOctagon, RotateCcw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('BTC-SHIELD Render Exception Caught by Boundary:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[360px] p-6 max-w-2xl mx-auto flex flex-col items-center justify-center text-center my-8">
          <div className="p-3 rounded-full bg-rose-500/10 text-rose-500 mb-4 border border-rose-500/20 shadow-lg shadow-rose-950/20">
            <AlertOctagon size={28} />
          </div>
          <h2 className="text-base font-mono font-bold text-slate-100 uppercase tracking-wider mb-2">
            Intelligence View Recovery
          </h2>
          <p className="text-xs text-slate-400 max-w-md leading-relaxed mb-4">
            An unexpected error occurred while rendering this interface. Core telemetry and intelligence background services remain active.
          </p>

          {this.state.error?.message && (
            <div className="w-full max-w-lg mb-6 p-3 bg-slate-950/80 rounded border border-slate-800 text-left font-mono text-[11px] text-rose-400/90 break-all overflow-auto max-h-32">
              {this.state.error.message}
            </div>
          )}

          <div className="flex items-center gap-3">
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono rounded border border-slate-700 transition cursor-pointer"
            >
              <RotateCcw size={13} /> Reload View
            </button>
            <a
              href="/"
              className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono font-medium rounded transition shadow-xs"
            >
              <Home size={13} /> Return to Command Center
            </a>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
