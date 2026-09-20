import { useModels } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Cpu, CheckCircle2, ShieldAlert, GitBranch, Layers } from 'lucide-react';
import { formatDate } from '../utils/format';

export default function ModelsPage() {
  const { data: models, isLoading, error, refetch } = useModels();

  const modelList = Array.isArray(models) ? models : [];

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Model Lab" 
        description="Machine learning model runs, hyperparameter registries, evaluation metrics, and feature schemas" 
      />

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-2">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
              <Cpu size={18} />
            </span>
            <h2 className="text-sm font-bold text-white">Isolation Forest (Unsupervised Anomaly Detector)</h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Constructs randomized partitioning ensembles over 23 multi-dimensional behavioral features. Shorter tree path lengths indicate anomalies that isolate easily from normal peer traffic.
          </p>
          <div className="text-[11px] font-mono text-slate-400 flex flex-wrap gap-3 pt-2">
            <span>Estimators: 100</span>
            <span>Contamination: Adaptive (1-10%)</span>
            <span>Scaler: StandardScaler</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-2">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
              <Layers size={18} />
            </span>
            <h2 className="text-sm font-bold text-white">DBSCAN (Density-Based Behavioral Clustering)</h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Discovers non-linear density clusters of entity behavior. Points marked with Cluster ID -1 represent behavioral outliers that do not conform to any established cluster.
          </p>
          <div className="text-[11px] font-mono text-slate-400 flex flex-wrap gap-3 pt-2">
            <span>Distance Metric: Euclidean</span>
            <span>Epsilon: Adaptive 90th percentile</span>
          </div>
        </div>
      </div>

      {/* Model Runs Table */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Failed to load model registry." onRetry={() => refetch()} />
      ) : modelList.length === 0 ? (
        <EmptyState
          icon={<Cpu size={32} />}
          title="No Models Trained Yet"
          description="Model training is executed automatically when running the intelligence pipeline from the Dataset Management view."
        />
      ) : (
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-white font-mono">Trained Model Registry ({modelList.length})</h2>
          <div className="grid grid-cols-1 gap-4">
            {modelList.map((m: any) => {
              const metrics = m.evaluation_metrics || {};
              const params = m.parameters || {};

              return (
                <div key={m.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 shadow-lg">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
                        {m.model_type}
                      </span>
                      <span className="text-sm font-bold text-white font-mono">
                        Version: {m.model_version}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 font-mono">
                      Trained: <strong className="text-slate-200">{formatDate(m.created_at)}</strong>
                    </div>
                  </div>

                  {/* Metrics and Params Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                      <div className="text-slate-400 text-[10px]">TRAINED SAMPLES</div>
                      <div className="text-base font-bold text-white mt-0.5">
                        {metrics.n_samples !== undefined ? metrics.n_samples : 'N/A'}
                      </div>
                    </div>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                      <div className="text-slate-400 text-[10px]">DETECTED ANOMALIES</div>
                      <div className="text-base font-bold text-rose-400 mt-0.5">
                        {metrics.n_anomalies_detected !== undefined 
                          ? metrics.n_anomalies_detected 
                          : metrics.n_noise_points !== undefined 
                          ? metrics.n_noise_points 
                          : 'N/A'}
                      </div>
                    </div>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                      <div className="text-slate-400 text-[10px]">ANOMALY RATIO</div>
                      <div className="text-base font-bold text-amber-400 mt-0.5">
                        {metrics.anomaly_ratio !== undefined 
                          ? `${(metrics.anomaly_ratio * 100).toFixed(1)}%` 
                          : metrics.noise_ratio !== undefined 
                          ? `${(metrics.noise_ratio * 100).toFixed(1)}%` 
                          : 'N/A'}
                      </div>
                    </div>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                      <div className="text-slate-400 text-[10px]">
                        {m.model_type === 'DBSCAN' ? 'SILHOUETTE SCORE' : 'MEAN ANOMALY SCORE'}
                      </div>
                      <div className="text-base font-bold text-emerald-400 mt-0.5">
                        {metrics.silhouette_score !== undefined && metrics.silhouette_score !== null
                          ? metrics.silhouette_score.toFixed(3)
                          : metrics.score_mean !== undefined 
                          ? metrics.score_mean.toFixed(1) 
                          : 'N/A'}
                      </div>
                    </div>
                  </div>

                  {/* Feature Columns Tag Cloud */}
                  {params.feature_columns && (
                    <div className="space-y-1.5 pt-2 border-t border-slate-800">
                      <div className="text-[11px] font-mono text-slate-400">
                        FEATURE DIMENSIONS ({params.feature_columns.length}):
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {params.feature_columns.map((fc: string, idx: number) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-300"
                          >
                            {fc}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
