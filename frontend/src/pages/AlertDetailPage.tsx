import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAlert, useAIInterpretation, useCreateCase } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { 
  AlertCircle, ShieldCheck, Briefcase, Network, Clock, 
  ExternalLink, Sparkles, CheckCircle2, AlertTriangle, HelpCircle, FileText
} from 'lucide-react';
import { getPriorityColor, getStatusColor, truncateAddress, formatDate } from '../utils/format';

export default function AlertDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [caseModalOpen, setCaseModalOpen] = useState(false);
  const [caseTitle, setCaseTitle] = useState('');
  const [caseDescription, setCaseDescription] = useState('');

  const { data: alert, isLoading, error, refetch } = useAlert(id || '');
  const { data: aiData, isLoading: isAiLoading } = useAIInterpretation(
    alert?.entity_type || '', 
    alert?.entity_id || ''
  );
  const createCaseMutation = useCreateCase();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-64 lg:col-span-2 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error || !alert) {
    return <ErrorState message="Failed to load alert details." onRetry={() => refetch()} />;
  }

  const pColor = getPriorityColor(alert.priority);
  const sColor = getStatusColor(alert.status);

  const entityUrl = alert.entity_type === 'WALLET'
    ? `/wallets/${alert.entity_id}`
    : alert.entity_type === 'IP'
    ? `/ips/${alert.entity_id}`
    : `/transactions/${alert.entity_id}`;

  const handleCreateCase = async () => {
    if (!caseTitle) return;
    try {
      const res = await createCaseMutation.mutateAsync({
        title: caseTitle,
        description: caseDescription || `Investigation promoted from Alert #${alert.id} (${alert.priority} priority on ${alert.entity_type} ${alert.entity_id})`,
        priority: alert.priority,
        alert_id: alert.id,
      });
      setCaseModalOpen(false);
      navigate(`/cases/${res.id}`);
    } catch (err) {
      console.error('Failed to create case:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Breadcrumb & Header */}
      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
        <Link to="/alerts" className="hover:text-slate-300">ALERTS</Link>
        <span>/</span>
        <span className="text-slate-200">ALERT #{alert.id}</span>
      </div>

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-white font-mono">
              Alert #{alert.id}: {alert.entity_type} {alert.entity_type === 'WALLET' ? truncateAddress(alert.entity_id) : alert.entity_id}
            </h1>
            <span className={`px-2.5 py-0.5 rounded text-xs font-bold font-mono ${pColor.bg} ${pColor.text} border ${pColor.border}`}>
              {alert.priority}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs font-mono ${sColor.bg} ${sColor.text} border ${sColor.border}`}>
              {alert.status}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Generated {formatDate(alert.created_at)} by Model Version <span className="font-mono text-slate-300">{alert.model_version || 'IF-2.0'}</span>
          </p>
        </div>

        {/* Quick Action Buttons */}
        <div className="flex items-center gap-2">
          <Link
            to={`/graph?entityType=${alert.entity_type}&entityId=${encodeURIComponent(alert.entity_id)}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition"
          >
            <Network size={14} className="text-blue-400" /> Explore in Graph
          </Link>
          <button
            onClick={() => {
              setCaseTitle(`Investigate ${alert.entity_type} ${truncateAddress(alert.entity_id)}`);
              setCaseModalOpen(true);
            }}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition shadow"
          >
            <Briefcase size={14} /> Promote to Case
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Anomaly Score (Isolation Forest)</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-white">
              {alert.anomaly_score.toFixed(1)}
            </span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden mt-3">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 via-amber-500 to-rose-500" 
              style={{ width: `${Math.min(alert.anomaly_score, 100)}%` }}
            />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Data Confidence (Sufficiency)</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-white">
              {Math.round((alert.confidence || 0) * 100)}%
            </span>
            <span className="text-xs text-emerald-400 font-mono">
              {alert.confidence > 0.7 ? 'High Sufficiency' : 'Moderate'}
            </span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden mt-3">
            <div 
              className="h-full bg-emerald-500" 
              style={{ width: `${Math.min((alert.confidence || 0) * 100, 100)}%` }}
            />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Entity Details</div>
          <div className="mt-1">
            <Link to={entityUrl} className="text-sm font-mono text-blue-400 hover:underline flex items-center gap-1">
              {alert.entity_id}
              <ExternalLink size={12} />
            </Link>
            <div className="text-xs text-slate-400 mt-1">
              Type: <span className="font-mono text-slate-300">{alert.entity_type}</span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Interpretation Assistant */}
      <div className="bg-slate-900 border border-blue-500/30 rounded-xl p-5 shadow-lg relative overflow-hidden">
        <div className="flex items-center gap-2 mb-3">
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
            <Sparkles size={16} />
          </div>
          <h2 className="text-sm font-semibold text-white">
            Explainable AI Interpretation
          </h2>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 ml-auto">
            Zero-Hallucination Engine
          </span>
        </div>

        {isAiLoading ? (
          <div className="space-y-2 py-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        ) : (
          <div className="space-y-4 text-xs">
            <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80 leading-relaxed text-slate-200">
              {aiData?.summary || "Behavioral anomaly evaluation in progress."}
            </div>

            {/* Recommended Review Actions */}
            {aiData?.recommended_review_actions && aiData.recommended_review_actions.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                  <CheckCircle2 size={13} className="text-emerald-400" /> Recommended Investigator Review Actions:
                </h3>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {aiData.recommended_review_actions.map((act: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2 bg-slate-950/40 p-2 rounded border border-slate-800/60 text-slate-300">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1 shrink-0" />
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Uncertainty & Limitations */}
            <div className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-800 flex items-start gap-2 text-slate-400">
              <HelpCircle size={14} className="text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-slate-300">Uncertainty Assessment: </span>
                {aiData?.uncertainty || "Standard statistical confidence."}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Contributing Evidence Signals */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <AlertTriangle size={16} className="text-amber-400" />
          Contributing Evidence Signals ({alert.contributing_signals?.length || 0})
        </h2>

        {alert.contributing_signals && alert.contributing_signals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {alert.contributing_signals.map((sig: any, idx: number) => (
              <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-blue-400 border border-slate-700">
                    {sig.category} SIGNAL
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    Strength: <span className="text-white font-bold">{Math.round(sig.strength * 100)}%</span>
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {sig.observation}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-slate-400 text-center py-6">
            No discrete evidence signals attached to this alert.
          </div>
        )}
      </div>

      {/* Promote to Case Modal */}
      {caseModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Briefcase size={18} className="text-blue-400" />
              Create Investigation Case
            </h3>
            <p className="text-xs text-slate-400">
              Promote this alert to an active investigative case. All associated entities, network observations, and evidence will be automatically pinned.
            </p>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Case Title</label>
                <input
                  type="text"
                  value={caseTitle}
                  onChange={(e) => setCaseTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description / Investigative Hypothesis</label>
                <textarea
                  rows={3}
                  value={caseDescription}
                  onChange={(e) => setCaseDescription(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setCaseModalOpen(false)}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateCase}
                disabled={createCaseMutation.isPending || !caseTitle}
                className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition"
              >
                {createCaseMutation.isPending ? 'Creating...' : 'Open Case'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
